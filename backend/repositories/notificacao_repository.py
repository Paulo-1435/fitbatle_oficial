from models.base import efetivar
from models.notificacao import Notificacao


class NotificacaoRepository:

    @staticmethod
    def existe(id_usuario, tipo, mensagem):
        return Notificacao.query.filter_by(id_usuario=id_usuario, tipo=tipo, mensagem=mensagem).first() is not None

    @staticmethod
    def listar_do_usuario(id_usuario, limite=50):
        return (
            Notificacao.query.filter_by(id_usuario=id_usuario)
            .order_by(Notificacao.data_envio.desc())
            .limit(limite)
            .all()
        )

    @staticmethod
    def contar_nao_lidas(id_usuario):
        return Notificacao.query.filter_by(id_usuario=id_usuario, lida=False).count()

    @staticmethod
    def marcar_todas_lidas(id_usuario):
        Notificacao.query.filter_by(id_usuario=id_usuario, lida=False).update({"lida": True})
        efetivar()
