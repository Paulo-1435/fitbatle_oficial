from database import db
from models.notificacao import Notificacao


class NotificacaoRepository:

    @staticmethod
    def criar(id_usuario, tipo, mensagem, tipo_alvo, id_alvo):
        notificacao = Notificacao(
            id_usuario=id_usuario,
            tipo=tipo,
            mensagem=mensagem,
            tipo_alvo=tipo_alvo,
            id_alvo=id_alvo,
        )
        db.session.add(notificacao)
        db.session.commit()
        return notificacao

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
    def buscar_por_id(id_notificacao):
        return db.session.get(Notificacao, id_notificacao)

    @staticmethod
    def marcar_lida(notificacao):
        notificacao.lida = True
        db.session.commit()

    @staticmethod
    def marcar_todas_lidas(id_usuario):
        Notificacao.query.filter_by(id_usuario=id_usuario, lida=False).update({"lida": True})
        db.session.commit()
