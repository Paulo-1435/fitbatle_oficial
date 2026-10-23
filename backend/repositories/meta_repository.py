from database import db
from models.meta import Meta


class MetaRepository:

    @staticmethod
    def criar(dados):
        meta = Meta(**dados)
        db.session.add(meta)
        db.session.commit()
        return meta

    @staticmethod
    def buscar_por_id(id_meta):
        return db.session.get(Meta, id_meta)

    @staticmethod
    def listar_do_usuario(id_usuario):
        return (
            Meta.query.filter_by(id_usuario=id_usuario)
            .order_by(Meta.data_inicio.desc())
            .all()
        )

    @staticmethod
    def salvar(meta):
        db.session.add(meta)
        db.session.commit()
        return meta

    @staticmethod
    def excluir(meta):
        db.session.delete(meta)
        db.session.commit()
