LIMITE_PADRAO = 20
LIMITE_MAXIMO = 100


def normalizar_limite_ranking(valor):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return LIMITE_PADRAO
    return max(1, min(numero, LIMITE_MAXIMO))
