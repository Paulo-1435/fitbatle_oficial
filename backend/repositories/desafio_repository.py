from database import db
from models.desafio import Desafio


class DesafioRepository:

    @staticmethod
    def criar(dados):
        desafio = Desafio(**dados)
        db.session.add(desafio)
        db.session.commit()
        return desafio

    @staticmethod
    def buscar_por_id(id_desafio):
        return db.session.get(Desafio, id_desafio)

    @staticmethod
    def listar_ativos(hoje):
        return (
            Desafio.query.filter(Desafio.data_fim >= hoje)
            .order_by(Desafio.data_inicio.asc())
            .all()
        )

    @staticmethod
    def salvar(desafio):
        db.session.add(desafio)
        db.session.commit()
        return desafio
