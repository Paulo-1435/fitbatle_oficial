from repositories.repository import AtividadeRepository
from services.comum import ErroValidacao

FAIXAS_NIVEL = [
    (0, "iniciante"),
    (1000, "intermediario"),
    (3000, "avancado"),
    (7000, "profissional"),
    (15000, "elite"),
]

PONTUACAO_MAXIMA_TREINO = 2000
XP_MAXIMO_DIARIO = 3000


def nivel_por_xp(xp):
    nivel = FAIXAS_NIVEL[0][1]
    for xp_minimo, nome in FAIXAS_NIVEL:
        if xp >= xp_minimo:
            nivel = nome
    return nivel


def calcular_pontuacao(dados):
    tempo = dados.get("tempo_min") or 0
    distancia = dados.get("distancia_km") or 0
    carga = dados.get("carga_kg") or 0
    reps = dados.get("repeticoes") or 0

    pontos = tempo * 1 + distancia * 10 + (carga * reps) / 100

    bonus_tipo = {"musculacao": 20, "cardio": 15, "yoga": 10, "outro": 5}
    pontos += bonus_tipo.get(dados["tipo"], 5)

    return max(10, round(pontos))


def buscar_atividade(id_atividade):
    atividade = AtividadeRepository.buscar_por_id(id_atividade)
    if not atividade:
        raise ErroValidacao("Atividade não encontrada.", status=404)
    return atividade
