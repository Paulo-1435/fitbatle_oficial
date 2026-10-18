import os
import smtplib
from email.message import EmailMessage

from repositories.repository import ConsentimentoRepository, NotificacaoRepository, UsuarioRepository


def gerar_notificacao(id_usuario, tipo, mensagem, tipo_alvo=None, id_alvo=None):
    consentimento = ConsentimentoRepository.buscar(id_usuario, "notificacoes")
    if not consentimento or not consentimento.aceito:
        return None
    notificacao = NotificacaoRepository.criar(id_usuario, tipo, mensagem, tipo_alvo, id_alvo)
    _enviar_email_se_configurado(id_usuario, mensagem)
    return notificacao


def _enviar_email_se_configurado(id_usuario, mensagem):
    host = os.environ.get("SMTP_HOST")
    if not host:
        return
    usuario = UsuarioRepository.buscar_por_id(id_usuario)
    if not usuario or not usuario.email:
        return
    try:
        porta = int(os.environ.get("SMTP_PORT", "587"))
        usuario_smtp = os.environ.get("SMTP_USER")
        senha_smtp = os.environ.get("SMTP_PASSWORD")
        remetente = os.environ.get("SMTP_FROM") or usuario_smtp or "noreply@fitbattle.local"

        email = EmailMessage()
        email["Subject"] = "FitBattle"
        email["From"] = remetente
        email["To"] = usuario.email
        email.set_content(mensagem)

        with smtplib.SMTP(host, porta, timeout=5) as servidor:
            if usuario_smtp and senha_smtp:
                servidor.starttls()
                servidor.login(usuario_smtp, senha_smtp)
            servidor.send_message(email)
    except Exception:
        pass
