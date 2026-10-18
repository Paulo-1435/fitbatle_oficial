from repositories.repository import AtividadeRepository, PostagemRepository
from services.comum import ErroValidacao

TIPOS_ALVO_FEED = {"atividade", "postagem"}


def buscar_alvo(tipo_alvo, id_alvo):
    if tipo_alvo not in TIPOS_ALVO_FEED:
        raise ErroValidacao("Tipo de conteúdo inválido.")
    if tipo_alvo == "atividade":
        alvo = AtividadeRepository.buscar_por_id(id_alvo)
    else:
        alvo = PostagemRepository.buscar_por_id(id_alvo)
    if not alvo:
        raise ErroValidacao("Conteúdo não encontrado.", status=404)
    return alvo
