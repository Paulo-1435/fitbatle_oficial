from repositories.repository import ConsentimentoRepository, NotificacaoRepository
from services.email.enviar_email import EnviarEmailService


def gerar_notificacao(id_usuario, tipo, mensagem, tipo_alvo=None, id_alvo=None):
    consentimento = ConsentimentoRepository.buscar(id_usuario, "notificacoes")
    if not consentimento or not consentimento.aceito:
        return None
    notificacao = NotificacaoRepository.criar(id_usuario, tipo, mensagem, tipo_alvo, id_alvo)
    EnviarEmailService.executar(id_usuario, mensagem)
    return notificacao
