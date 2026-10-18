from repositories.repository import (
    AtividadeRepository,
    ComentarioRepository,
    CurtidaRepository,
    RankingRepository,
    UsuarioRepository,
)
from services.comum import ErroValidacao
from services.desafio import DesafioService
from services.notificacao.apoio import gerar_notificacao
from services.usuario import UsuarioService

FAIXAS_NIVEL = [
    (0, "iniciante"),
    (1000, "intermediario"),
    (3000, "avancado"),
    (7000, "profissional"),
    (15000, "elite"),
]


def nivel_por_xp(xp):
    nivel = FAIXAS_NIVEL[0][1]
    for xp_minimo, nome in FAIXAS_NIVEL:
        if xp >= xp_minimo:
            nivel = nome
    return nivel


class AtividadeService:

    TIPOS_VALIDOS = {"musculacao", "cardio", "yoga", "outro"}

    LIMITES_CAMPOS = {
        "tempo_min": 600,
        "distancia_km": 500,
        "carga_kg": 500,
        "repeticoes": 1000,
    }

    @staticmethod
    def registrar(id_usuario, dados):
        usuario = UsuarioService.buscar(id_usuario)
        limpos = AtividadeService._validar(dados)

        posicao_antes = RankingRepository.minha_posicao_global(id_usuario)

        limpos["pontuacao"] = AtividadeService.calcular_pontuacao(limpos)
        atividade = AtividadeRepository.criar(id_usuario, limpos)

        usuario.xp += atividade.pontuacao
        usuario.nivel = nivel_por_xp(usuario.xp)
        UsuarioRepository.salvar(usuario)

        AtividadeService._notificar_subida_no_ranking(id_usuario, posicao_antes)
        DesafioService.avaliar_para_usuario(id_usuario)

        return atividade, usuario

    @staticmethod
    def _notificar_subida_no_ranking(id_usuario, posicao_antes):
        posicao_depois = RankingRepository.minha_posicao_global(id_usuario)
        if not posicao_antes or not posicao_depois:
            return
        if posicao_depois["posicao"] < posicao_antes["posicao"]:
            gerar_notificacao(
                id_usuario,
                "subida_ranking",
                f"Você subiu para a posição #{posicao_depois['posicao']} no ranking global!",
            )

    @staticmethod
    def historico(id_usuario):
        UsuarioService.buscar(id_usuario)
        return AtividadeRepository.listar_do_usuario(id_usuario)

    @staticmethod
    def buscar(id_atividade):
        atividade = AtividadeRepository.buscar_por_id(id_atividade)
        if not atividade:
            raise ErroValidacao("Atividade não encontrada.", status=404)
        return atividade

    @staticmethod
    def buscar_visivel(id_atividade, id_solicitante):
        atividade = AtividadeService.buscar(id_atividade)
        if atividade.id_usuario != id_solicitante:
            dono = UsuarioRepository.buscar_por_id(atividade.id_usuario)
            if dono is None or not dono.perfil_publico:
                raise ErroValidacao("Atividade não encontrada.", status=404)
        return atividade

    @staticmethod
    def excluir(id_usuario, id_atividade):
        atividade = AtividadeService.buscar(id_atividade)
        if atividade.id_usuario != id_usuario:
            raise ErroValidacao("Você só pode excluir seus próprios treinos.", status=403)
        usuario = UsuarioRepository.buscar_por_id(atividade.id_usuario)
        if usuario:
            usuario.xp = max(0, usuario.xp - atividade.pontuacao)
            usuario.nivel = nivel_por_xp(usuario.xp)
            UsuarioRepository.salvar(usuario)
        CurtidaRepository.excluir_do_alvo("atividade", id_atividade)
        ComentarioRepository.excluir_do_alvo("atividade", id_atividade)
        AtividadeRepository.excluir(atividade)

    @staticmethod
    def calcular_pontuacao(dados):
        tempo = dados.get("tempo_min") or 0
        distancia = dados.get("distancia_km") or 0
        carga = dados.get("carga_kg") or 0
        reps = dados.get("repeticoes") or 0

        pontos = tempo * 1 + distancia * 10 + (carga * reps) / 100

        bonus_tipo = {"musculacao": 20, "cardio": 15, "yoga": 10, "outro": 5}
        pontos += bonus_tipo.get(dados["tipo"], 5)

        return max(10, round(pontos))

    @staticmethod
    def _validar(dados):
        if not dados:
            raise ErroValidacao("Corpo da requisição vazio ou JSON inválido.")

        tipo = (dados.get("tipo") or "").strip().lower()
        if tipo not in AtividadeService.TIPOS_VALIDOS:
            raise ErroValidacao(
                "Tipo inválido. Use: " + ", ".join(sorted(AtividadeService.TIPOS_VALIDOS))
            )

        numericos = {}
        for campo in ("tempo_min", "distancia_km", "carga_kg", "repeticoes"):
            valor = dados.get(campo)
            if valor in (None, ""):
                numericos[campo] = None
                continue
            try:
                valor = float(str(valor).replace(",", "."))
            except (TypeError, ValueError):
                raise ErroValidacao(f"O campo '{campo}' deve ser numérico.")
            if valor < 0:
                raise ErroValidacao(f"O campo '{campo}' não pode ser negativo.")
            limite = AtividadeService.LIMITES_CAMPOS[campo]
            if valor > limite:
                raise ErroValidacao(f"O campo '{campo}' não pode passar de {limite}.")
            numericos[campo] = valor

        if not numericos["tempo_min"] and not numericos["distancia_km"]:
            raise ErroValidacao("Informe ao menos a duração ou a distância do treino.")

        return {
            "tipo": tipo,
            "titulo": (dados.get("titulo") or None),
            "descricao": (dados.get("descricao") or None),
            **numericos,
        }
