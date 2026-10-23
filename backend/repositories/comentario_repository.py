from sqlalchemy import func
from database import db
from models.comentario import Comentario


class ComentarioRepository:

    @staticmethod
    def buscar_por_id(id_comentario):
        return db.session.get(Comentario, id_comentario)

    @staticmethod
    def criar(id_usuario, tipo_alvo, id_alvo, texto):
        comentario = Comentario(
            id_usuario=id_usuario, tipo_alvo=tipo_alvo, id_alvo=id_alvo, texto=texto
        )
        db.session.add(comentario)
        db.session.commit()
        return comentario

    @staticmethod
    def excluir(comentario):
        db.session.delete(comentario)
        db.session.commit()

    @staticmethod
    def listar(tipo_alvo, id_alvo):
        return (
            Comentario.query.filter_by(tipo_alvo=tipo_alvo, id_alvo=id_alvo)
            .order_by(Comentario.data_registro.asc())
            .all()
        )

    @staticmethod
    def contar_em_lote(tipo_alvo, ids_alvo):
        if not ids_alvo:
            return {}
        linhas = (
            db.session.query(Comentario.id_alvo, func.count(Comentario.id_comentario))
            .filter(Comentario.tipo_alvo == tipo_alvo, Comentario.id_alvo.in_(ids_alvo))
            .group_by(Comentario.id_alvo)
            .all()
        )
        return {id_alvo: total for id_alvo, total in linhas}

    @staticmethod
    def excluir_do_alvo(tipo_alvo, id_alvo):
        Comentario.query.filter_by(tipo_alvo=tipo_alvo, id_alvo=id_alvo).delete()
        db.session.commit()

    @staticmethod
    def excluir_do_usuario(id_usuario):
        Comentario.query.filter_by(id_usuario=id_usuario).delete()
        db.session.commit()
