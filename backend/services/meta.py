from datetime import date, datetime

from repositories.repository import AtividadeRepository, MetaRepository
from services.comum import ErroValidacao
from services.notificacao.apoio import gerar_notificacao
from utils import agora, iso_utc


class MetaService:

    TIPOS_PRAZO = {"curto_prazo", "longo_prazo"}
    TIPOS_METRICA = {"carga_maxima", "frequencia"}
    TITULO_MAX = 300

    @staticmethod
    def criar(id_usuario, dados):
        dados = dados or {}
        titulo = (dados.get("titulo") or "").strip()
        tipo = dados.get("tipo")
        tipo_metrica = dados.get("tipo_metrica")
        exercicio = (dados.get("exercicio") or "").strip() or None
        data_final = dados.get("data_final")

        if not titulo:
            raise ErroValidacao("Informe o título da meta.")
        if len(titulo) > MetaService.TITULO_MAX:
            raise ErroValidacao(f"O título pode ter no máximo {MetaService.TITULO_MAX} caracteres.")
        if tipo not in MetaService.TIPOS_PRAZO:
            raise ErroValidacao("Tipo de prazo inválido. Use: curto_prazo ou longo_prazo.")
        if tipo_metrica not in MetaService.TIPOS_METRICA:
            raise ErroValidacao("Tipo de métrica inválido. Use: carga_maxima ou frequencia.")
        if tipo_metrica == "carga_maxima" and not exercicio:
            raise ErroValidacao("Informe o exercício vinculado a esta meta.")
        if tipo_metrica == "frequencia":
            exercicio = None

        valor_objetivo = MetaService._validar_numero(dados.get("valor_objetivo"), "valor objetivo")

        valor_partida = dados.get("valor_partida")
        if valor_partida not in (None, ""):
            valor_partida = MetaService._validar_numero(valor_partida, "valor de partida")
        elif tipo_metrica == "carga_maxima":
            valor_partida = AtividadeRepository.maior_carga(id_usuario, exercicio.lower()) or 0
        else:
            valor_partida = 0

        data_final_convertida = None
        if data_final:
            data_final_convertida = MetaService._validar_data(data_final)
            if data_final_convertida < date.today():
                raise ErroValidacao("O prazo da meta não pode ser uma data no passado.")

        meta = MetaRepository.criar({
            "id_usuario": id_usuario,
            "descricao": titulo,
            "tipo": tipo,
            "tipo_metrica": tipo_metrica,
            "exercicio": exercicio,
            "valor_objetivo": valor_objetivo,
            "valor_partida": valor_partida,
            "data_inicio": date.today(),
            "data_final": data_final_convertida,
            "status": "em_andamento",
        })
        return MetaService._com_progresso(meta)

    @staticmethod
    def buscar(id_meta):
        meta = MetaRepository.buscar_por_id(id_meta)
        if not meta:
            raise ErroValidacao("Meta não encontrada.", status=404)
        return meta

    @staticmethod
    def _exigir_dono(id_meta, id_usuario):
        meta = MetaService.buscar(id_meta)
        if meta.id_usuario != id_usuario:
            raise ErroValidacao("Você não tem permissão para acessar esta meta.", status=403)
        return meta

    @staticmethod
    def listar_do_usuario(id_usuario):
        metas = MetaRepository.listar_do_usuario(id_usuario)
        return [MetaService._com_progresso(m) for m in metas]

    @staticmethod
    def detalhe(id_meta, id_usuario):
        meta = MetaService._exigir_dono(id_meta, id_usuario)
        dado = MetaService._com_progresso(meta)
        dado["historico"] = MetaService._historico(meta)
        return dado

    @staticmethod
    def atualizar(id_meta, id_usuario, dados):
        meta = MetaService._exigir_dono(id_meta, id_usuario)
        dados = dados or {}

        if dados.get("titulo") is not None:
            titulo = dados["titulo"].strip()
            if not titulo:
                raise ErroValidacao("Informe o título da meta.")
            meta.descricao = titulo
        if dados.get("valor_objetivo") is not None:
            meta.valor_objetivo = MetaService._validar_numero(dados["valor_objetivo"], "valor objetivo")
        if "data_final" in dados:
            meta.data_final = MetaService._validar_data(dados["data_final"]) if dados["data_final"] else None

        MetaRepository.salvar(meta)
        return MetaService._com_progresso(meta)

    @staticmethod
    def excluir(id_meta, id_usuario):
        meta = MetaService._exigir_dono(id_meta, id_usuario)
        MetaRepository.excluir(meta)

    @staticmethod
    def _valor_atual(meta):
        if meta.tipo_metrica == "carga_maxima":
            maior = AtividadeRepository.maior_carga(meta.id_usuario, (meta.exercicio or "").strip().lower())
            if maior is None:
                return float(meta.valor_partida) if meta.valor_partida is not None else 0.0
            return maior
        inicio = datetime.combine(meta.data_inicio, datetime.min.time())
        return float(AtividadeRepository.contar_desde(meta.id_usuario, inicio))

    @staticmethod
    def _com_progresso(meta):
        if meta.valor_objetivo is None:
            return {
                "id": meta.id_meta,
                "titulo": meta.descricao,
                "tipo": meta.tipo,
                "tipo_metrica": None,
                "exercicio": None,
                "valor_objetivo": None,
                "valor_partida": None,
                "valor_atual": None,
                "faltam": None,
                "percentual": None,
                "status": meta.status,
                "data_inicio": meta.data_inicio.isoformat(),
                "data_final": meta.data_final.isoformat() if meta.data_final else None,
                "dias_restantes": (meta.data_final - date.today()).days if meta.data_final else None,
                "concluida_em": meta.concluida_em.isoformat() if meta.concluida_em else None,
            }

        atual = MetaService._valor_atual(meta)
        objetivo = float(meta.valor_objetivo)
        partida = float(meta.valor_partida) if meta.valor_partida is not None else 0.0

        if meta.status == "em_andamento" and objetivo > 0 and atual >= objetivo:
            meta.status = "concluida"
            meta.concluida_em = agora()
            MetaRepository.salvar(meta)
            gerar_notificacao(
                meta.id_usuario,
                "meta_concluida",
                f"Você concluiu a meta \"{meta.descricao}\"!",
                tipo_alvo="meta",
                id_alvo=meta.id_meta,
            )

        percentual = 0
        if objetivo > 0:
            percentual = max(0, min(100, round((atual / objetivo) * 100)))

        dias_restantes = None
        if meta.data_final:
            dias_restantes = (meta.data_final - date.today()).days

        return {
            "id": meta.id_meta,
            "titulo": meta.descricao,
            "tipo": meta.tipo,
            "tipo_metrica": meta.tipo_metrica,
            "exercicio": meta.exercicio,
            "valor_objetivo": objetivo,
            "valor_partida": partida,
            "valor_atual": atual,
            "faltam": max(0, round(objetivo - atual, 2)),
            "percentual": percentual,
            "status": meta.status,
            "data_inicio": meta.data_inicio.isoformat(),
            "data_final": meta.data_final.isoformat() if meta.data_final else None,
            "dias_restantes": dias_restantes,
            "concluida_em": meta.concluida_em.isoformat() if meta.concluida_em else None,
        }

    @staticmethod
    def _historico(meta):
        if meta.tipo_metrica != "carga_maxima" or not meta.exercicio:
            return []

        atividades = AtividadeRepository.listar_do_usuario_por_titulo(
            meta.id_usuario, meta.exercicio.strip().lower()
        )
        historico = []
        anterior = None
        for indice, atividade in enumerate(atividades, start=1):
            carga = float(atividade.carga_kg) if atividade.carga_kg is not None else None
            if anterior is None:
                rotulo = "Registro inicial da meta"
            elif carga == anterior:
                rotulo = "Carga mantida"
            elif carga is not None and anterior is not None and carga > anterior:
                rotulo = f"+{carga - anterior:g} kg em relação ao anterior"
            else:
                rotulo = f"{(carga - anterior):g} kg em relação ao anterior" if carga is not None and anterior is not None else "—"

            historico.append({
                "sessao": indice,
                "carga_kg": carga,
                "repeticoes": atividade.repeticoes,
                "data_registro": iso_utc(atividade.data_registro),
                "rotulo": rotulo,
            })
            anterior = carga
        return historico

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
    def _validar_data(valor):
        try:
            return datetime.strptime(valor, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            raise ErroValidacao("Data inválida. Use o formato AAAA-MM-DD.")
