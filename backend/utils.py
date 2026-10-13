from datetime import date, datetime, timezone


def agora():
    return datetime.now(timezone.utc)


def iso_utc(valor):
    if valor is None:
        return None
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=timezone.utc)
    return valor.isoformat()


def calcular_idade(data_nascimento, idade_legada=None, hoje=None):
    if data_nascimento is None:
        return idade_legada
    hoje = hoje or date.today()
    idade = hoje.year - data_nascimento.year
    if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
        idade -= 1
    return idade
