from datetime import datetime, timedelta

from repositories.repository import (
    AtividadeRepository,
    DesafioRepository,
    DesafioUsuarioRepository,
    UsuarioRepository,
)
from services.comum import ErroValidacao
from services.notificacao import NotificacaoService
from services.usuario import UsuarioService
from utils import agora, iso_utc


class DesafioService:

    TIPOS_METRICA = {"treinos", "carga_maxima"}
    NOME_MAX = 120
    DESCRICAO_MAX = 500

    @staticmethod
    def criar(id_usuario, dados):
        UsuarioService.exigir_admin(id_usuario)
        limpos = DesafioService._validar(dados or {})
        desafio = DesafioRepository.criar(limpos)
        return DesafioService._dict_admin(desafio)

    @staticmethod
    def atualizar(id_usuario, id_desafio, dados):
        UsuarioService.exigir_admin(id_usuario)
        desafio = DesafioService._buscar(id_desafio)
        dados = dados or {}

        if dados.get("nome") is not None:
            desafio.nome = DesafioService._validar_nome(dados["nome"])
        if "descricao" in dados:
            descricao = (dados["descricao"] or "").strip()
            if len(descricao) > DesafioService.DESCRICAO_MAX:
                raise ErroValidacao(f"A descrição pode ter no máximo {DesafioService.DESCRICAO_MAX} caracteres.")
            desafio.descricao = descricao or None
        if "exercicio" in dados:
            desafio.exercicio = DesafioService._normalizar_exercicio(dados["exercicio"])
        if dados.get("data_inicio") is not None:
            desafio.data_inicio = DesafioService._validar_data(dados["data_inicio"], "data de início")
        if dados.get("data_fim") is not None:
            desafio.data_fim = DesafioService._validar_data(dados["data_fim"], "data de fim")
        if dados.get("recompensa_xp") is not None:
            desafio.recompensa_xp = DesafioService._validar_inteiro(dados["recompensa_xp"], "recompensa em XP")
        if dados.get("tipo_metrica") is not None:
            desafio.tipo_metrica = DesafioService._validar_tipo_metrica(dados["tipo_metrica"])
        if dados.get("valor_objetivo") is not None:
            desafio.valor_objetivo = DesafioService._validar_numero(dados["valor_objetivo"], "valor objetivo")

        if desafio.data_fim < desafio.data_inicio:
            raise ErroValidacao("A data de fim não pode ser antes da data de início.")

        DesafioRepository.salvar(desafio)
        return DesafioService._dict_admin(desafio)

    @staticmethod
    def encerrar(id_usuario, id_desafio):
        UsuarioService.exigir_admin(id_usuario)
        desafio = DesafioService._buscar(id_desafio)
        ontem = agora().date() - timedelta(days=1)
        if desafio.data_fim > ontem:
            desafio.data_fim = ontem
            if desafio.data_inicio > desafio.data_fim:
                desafio.data_inicio = desafio.data_fim
            DesafioRepository.salvar(desafio)
        return DesafioService._dict_admin(desafio)

    @staticmethod
    def listar_ativos(id_usuario):
        hoje = agora().date()
        desafios = DesafioRepository.listar_ativos(hoje)
        return [DesafioService._com_progresso(d, id_usuario) for d in desafios]

    @staticmethod
    def detalhe(id_desafio, id_usuario):
        desafio = DesafioService._buscar(id_desafio)
        return DesafioService._com_progresso(desafio, id_usuario)

    @staticmethod
    def participar(id_usuario, id_desafio):
        desafio = DesafioService._buscar(id_desafio)
        hoje = agora().date()
        if desafio.data_fim < hoje:
            raise ErroValidacao("Este desafio já foi encerrado.")

        inscricao = DesafioUsuarioRepository.buscar(id_desafio, id_usuario)
        if inscricao and inscricao.status == "inscrito":
            raise ErroValidacao("Você já está inscrito neste desafio.", status=409)
        if inscricao:
            inscricao.status = "inscrito"
            inscricao.concluido_em = None
            DesafioUsuarioRepository.salvar(inscricao)
        else:
            DesafioUsuarioRepository.inscrever(id_desafio, id_usuario)
        return DesafioService._com_progresso(desafio, id_usuario)

    @staticmethod
    def desistir(id_usuario, id_desafio):
        inscricao = DesafioUsuarioRepository.buscar(id_desafio, id_usuario)
        if not inscricao or inscricao.status != "inscrito":
            raise ErroValidacao("Você não está inscrito neste desafio.", status=404)
        inscricao.status = "desistiu"
        DesafioUsuarioRepository.salvar(inscricao)
        desafio = DesafioService._buscar(id_desafio)
        return DesafioService._com_progresso(desafio, id_usuario)

    @staticmethod
    def avaliar_para_usuario(id_usuario):
        for inscricao in DesafioUsuarioRepository.listar_do_usuario(id_usuario):
            if inscricao.status != "inscrito":
                continue
            desafio = DesafioRepository.buscar_por_id(inscricao.id_desafio)
            if desafio:
                DesafioService._avaliar_conclusao(desafio, inscricao)

    @staticmethod
    def _buscar(id_desafio):
        desafio = DesafioRepository.buscar_por_id(id_desafio)
        if not desafio:
            raise ErroValidacao("Desafio não encontrado.", status=404)
        return desafio

    @staticmethod
    def _titulo_filtro(desafio):
        exercicio = (desafio.exercicio or "livre").strip().lower()
        return None if exercicio == "livre" else exercicio

    @staticmethod
    def _valor_atual(desafio, id_usuario):
        inicio = datetime.combine(desafio.data_inicio, datetime.min.time())
        fim = datetime.combine(desafio.data_fim, datetime.min.time()) + timedelta(days=1)
        titulo = DesafioService._titulo_filtro(desafio)

        if desafio.tipo_metrica == "carga_maxima":
            return AtividadeRepository.maior_carga_no_periodo(id_usuario, inicio, fim, titulo) or 0.0
        return float(AtividadeRepository.contar_no_periodo(id_usuario, inicio, fim, titulo))

    @staticmethod
    def _avaliar_conclusao(desafio, inscricao):
        if inscricao.status != "inscrito":
            return
        atual = DesafioService._valor_atual(desafio, inscricao.id_usuario)
        objetivo = float(desafio.valor_objetivo)
        if objetivo <= 0 or atual < objetivo:
            return

        inscricao.status = "concluido"
        inscricao.concluido_em = agora()
        DesafioUsuarioRepository.salvar(inscricao)

        if desafio.recompensa_xp:
            from services.atividade import nivel_por_xp

            usuario = UsuarioService.buscar(inscricao.id_usuario)
            usuario.xp += desafio.recompensa_xp
            usuario.nivel = nivel_por_xp(usuario.xp)
            UsuarioRepository.salvar(usuario)

        NotificacaoService.gerar(
            inscricao.id_usuario,
            "desafio_concluido",
            f"Você concluiu o desafio \"{desafio.nome}\"!",
            tipo_alvo="desafio",
            id_alvo=desafio.id_desafio,
        )

    @staticmethod
    def _com_progresso(desafio, id_usuario):
        inscricao = DesafioUsuarioRepository.buscar(desafio.id_desafio, id_usuario)
        if inscricao:
            DesafioService._avaliar_conclusao(desafio, inscricao)

        atual = DesafioService._valor_atual(desafio, id_usuario)
        objetivo = float(desafio.valor_objetivo)
        percentual = max(0, min(100, round((atual / objetivo) * 100))) if objetivo > 0 else 0

        return {
            "id": desafio.id_desafio,
            "nome": desafio.nome,
            "descricao": desafio.descricao,
            "exercicio": desafio.exercicio,
            "tipo_metrica": desafio.tipo_metrica,
            "valor_objetivo": objetivo,
            "data_inicio": desafio.data_inicio.isoformat(),
            "data_fim": desafio.data_fim.isoformat(),
            "recompensa_xp": desafio.recompensa_xp,
            "minha_inscricao": {
                "status": inscricao.status if inscricao else None,
                "valor_atual": atual,
                "percentual": percentual,
                "concluido_em": iso_utc(inscricao.concluido_em) if inscricao and inscricao.concluido_em else None,
            },
        }

    @staticmethod
    def _dict_admin(desafio):
        return {
            "id": desafio.id_desafio,
            "nome": desafio.nome,
            "descricao": desafio.descricao,
            "exercicio": desafio.exercicio,
            "tipo_metrica": desafio.tipo_metrica,
            "valor_objetivo": float(desafio.valor_objetivo),
            "data_inicio": desafio.data_inicio.isoformat(),
            "data_fim": desafio.data_fim.isoformat(),
            "recompensa_xp": desafio.recompensa_xp,
        }

    @staticmethod
    def _validar(dados):
        nome = DesafioService._validar_nome(dados.get("nome"))
        descricao = (dados.get("descricao") or "").strip()
        if len(descricao) > DesafioService.DESCRICAO_MAX:
            raise ErroValidacao(f"A descrição pode ter no máximo {DesafioService.DESCRICAO_MAX} caracteres.")

        tipo_metrica = DesafioService._validar_tipo_metrica(dados.get("tipo_metrica"))
        exercicio = DesafioService._normalizar_exercicio(dados.get("exercicio"))
        valor_objetivo = DesafioService._validar_numero(dados.get("valor_objetivo"), "valor objetivo")
        data_inicio = DesafioService._validar_data(dados.get("data_inicio"), "data de início")
        data_fim = DesafioService._validar_data(dados.get("data_fim"), "data de fim")
        if data_fim < data_inicio:
            raise ErroValidacao("A data de fim não pode ser antes da data de início.")

        recompensa_xp = dados.get("recompensa_xp")
        recompensa_xp = DesafioService._validar_inteiro(recompensa_xp, "recompensa em XP") if recompensa_xp not in (None, "") else 0

        return {
            "nome": nome,
            "descricao": descricao or None,
            "exercicio": exercicio,
            "tipo_metrica": tipo_metrica,
            "valor_objetivo": valor_objetivo,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "recompensa_xp": recompensa_xp,
        }

    @staticmethod
    def _validar_nome(nome):
        nome = (nome or "").strip()
        if not nome:
            raise ErroValidacao("Informe o nome do desafio.")
        if len(nome) > DesafioService.NOME_MAX:
            raise ErroValidacao(f"O nome pode ter no máximo {DesafioService.NOME_MAX} caracteres.")
        return nome

    @staticmethod
    def _validar_tipo_metrica(tipo_metrica):
        if tipo_metrica not in DesafioService.TIPOS_METRICA:
            raise ErroValidacao("Tipo de métrica inválido. Use: treinos ou carga_maxima.")
        return tipo_metrica

    @staticmethod
    def _normalizar_exercicio(exercicio):
        exercicio = (exercicio or "").strip()
        return exercicio if exercicio else "livre"

    @staticmethod
    def _validar_numero(valor, nome):
        try:
            numero = float(str(valor).replace(",", "."))
        except (TypeError, ValueError):
            raise ErroValidacao(f"Informe um {nome} válido.")
        if numero <= 0:
            raise ErroValidacao(f"O {nome} deve ser maior que zero.")
        return round(numero, 2)

    @staticmethod
    def _validar_inteiro(valor, nome):
        try:
            numero = int(valor)
        except (TypeError, ValueError):
            raise ErroValidacao(f"Informe um {nome} válido.")
        if numero < 0:
            raise ErroValidacao(f"O {nome} não pode ser negativo.")
        return numero

    @staticmethod
    def _validar_data(valor, nome):
        try:
            return datetime.strptime(valor, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            raise ErroValidacao(f"Informe uma {nome} válida. Use o formato AAAA-MM-DD.")
