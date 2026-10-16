import os
import smtplib
from email.message import EmailMessage

from repositories.repository import ConsentimentoRepository, NotificacaoRepository, UsuarioRepository
from services.comum import ErroValidacao


class NotificacaoService:

    @staticmethod
    def gerar(id_usuario, tipo, mensagem, tipo_alvo=None, id_alvo=None):
        consentimento = ConsentimentoRepository.buscar(id_usuario, "notificacoes")
        if not consentimento or not consentimento.aceito:
            return None
        notificacao = NotificacaoRepository.criar(id_usuario, tipo, mensagem, tipo_alvo, id_alvo)
        NotificacaoService._enviar_email_se_configurado(id_usuario, mensagem)
        return notificacao

    @staticmethod
    def listar(id_usuario):
        return NotificacaoRepository.listar_do_usuario(id_usuario)

    @staticmethod
    def contar_nao_lidas(id_usuario):
        return NotificacaoRepository.contar_nao_lidas(id_usuario)

    @staticmethod
    def marcar_lida(id_notificacao, id_usuario):
        notificacao = NotificacaoRepository.buscar_por_id(id_notificacao)
        if not notificacao:
            raise ErroValidacao("Notificação não encontrada.", status=404)
        if notificacao.id_usuario != id_usuario:
            raise ErroValidacao("Você não tem permissão para esta notificação.", status=403)
        NotificacaoRepository.marcar_lida(notificacao)
        return notificacao

    @staticmethod
    def marcar_todas_lidas(id_usuario):
        NotificacaoRepository.marcar_todas_lidas(id_usuario)

    @staticmethod
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
