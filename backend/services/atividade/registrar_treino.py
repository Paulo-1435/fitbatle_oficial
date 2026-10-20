from repositories.repository import AtividadeRepository, RankingRepository, UsuarioRepository
from services.atividade.apoio import (
    PONTUACAO_MAXIMA_TREINO,
    XP_MAXIMO_DIARIO,
    calcular_pontuacao,
    nivel_por_xp,
)
from services.comum import ErroValidacao, numero_decimal
from services.desafio.avaliar_desafios_do_usuario import AvaliarDesafiosDoUsuarioService
from services.notificacao.apoio import gerar_notificacao
from services.usuario.apoio import buscar_usuario
from utils import agora, data_local, inicio_utc_do_dia_local

TIPOS_VALIDOS = {"musculacao", "cardio", "yoga", "outro"}

LIMITES_CAMPOS = {
    "tempo_min": 600,
    "distancia_km": 500,
    "carga_kg": 500,
    "repeticoes": 1000,
}


def _validar(dados):
    if not dados:
        raise ErroValidacao("Corpo da requisição vazio ou JSON inválido.")

    tipo = (dados.get("tipo") or "").strip().lower()
    if tipo not in TIPOS_VALIDOS:
        raise ErroValidacao(
            "Tipo inválido. Use: " + ", ".join(sorted(TIPOS_VALIDOS))
        )

    numericos = {}
    for campo in ("tempo_min", "distancia_km", "carga_kg", "repeticoes"):
        valor = dados.get(campo)
        if valor in (None, ""):
            numericos[campo] = None
            continue
        valor = numero_decimal(valor, campo, LIMITES_CAMPOS[campo])
        if valor < 0:
            raise ErroValidacao(f"O campo '{campo}' não pode ser negativo.")
        numericos[campo] = valor

    if not numericos["tempo_min"] and not numericos["distancia_km"]:
        raise ErroValidacao("Informe ao menos a duração ou a distância do treino.")

    return {
        "tipo": tipo,
        "titulo": (dados.get("titulo") or None),
        "descricao": (dados.get("descricao") or None),
        **numericos,
    }


def _validar_teto(id_usuario, pontuacao):
    if pontuacao > PONTUACAO_MAXIMA_TREINO:
        raise ErroValidacao(
            f"Este treino vale {pontuacao} XP, acima do máximo de {PONTUACAO_MAXIMA_TREINO} XP por treino. "
            "Confira os valores informados."
        )
    xp_hoje = AtividadeRepository.pontuacao_total_desde(
        id_usuario, inicio_utc_do_dia_local(data_local(agora()))
    )
    if xp_hoje + pontuacao > XP_MAXIMO_DIARIO:
        raise ErroValidacao(
            f"Limite diário de XP atingido: você já somou {xp_hoje} XP hoje e o máximo é "
            f"{XP_MAXIMO_DIARIO} XP por dia. Tente novamente amanhã."
        )


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


class RegistrarTreinoService:

    @staticmethod
    def executar(id_usuario, dados):
        usuario = buscar_usuario(id_usuario)
        limpos = _validar(dados)

        posicao_antes = RankingRepository.minha_posicao_global(id_usuario)

        limpos["pontuacao"] = calcular_pontuacao(limpos)
        _validar_teto(id_usuario, limpos["pontuacao"])
        atividade = AtividadeRepository.criar(id_usuario, limpos)

        usuario.xp += atividade.pontuacao
        usuario.nivel = nivel_por_xp(usuario.xp)
        UsuarioRepository.salvar(usuario)

        _notificar_subida_no_ranking(id_usuario, posicao_antes)
        AvaliarDesafiosDoUsuarioService.executar(id_usuario)

        return atividade, usuario
