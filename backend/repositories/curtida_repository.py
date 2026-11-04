from sqlalchemy import func
from database import db
from models.base import efetivar
from models.curtida import Curtida


class CurtidaRepository:

    @staticmethod
    def buscar(id_usuario, tipo_alvo, id_alvo):
        return Curtida.query.filter_by(
            id_usuario=id_usuario, tipo_alvo=tipo_alvo, id_alvo=id_alvo
        ).first()

    @staticmethod
    def contar(tipo_alvo, id_alvo):
        return Curtida.query.filter_by(tipo_alvo=tipo_alvo, id_alvo=id_alvo).count()

    @staticmethod
    def contar_em_lote(tipo_alvo, ids_alvo):
        if not ids_alvo:
            return {}
        linhas = (
            db.session.query(Curtida.id_alvo, func.count(Curtida.id_curtida))
            .filter(Curtida.tipo_alvo == tipo_alvo, Curtida.id_alvo.in_(ids_alvo))
            .group_by(Curtida.id_alvo)
            .all()
        )
        return {id_alvo: total for id_alvo, total in linhas}

    @staticmethod
    def curtidos_pelo_usuario(id_usuario, tipo_alvo, ids_alvo):
        if not ids_alvo:
            return set()
        linhas = (
            db.session.query(Curtida.id_alvo)
            .filter(
                Curtida.id_usuario == id_usuario,
                Curtida.tipo_alvo == tipo_alvo,
                Curtida.id_alvo.in_(ids_alvo),
            )
            .all()
        )
        return {id_alvo for (id_alvo,) in linhas}

    @staticmethod
    def excluir_do_alvo(tipo_alvo, id_alvo):
        Curtida.query.filter_by(tipo_alvo=tipo_alvo, id_alvo=id_alvo).delete()
        efetivar()

    @staticmethod
    def excluir_do_usuario(id_usuario):
        Curtida.query.filter_by(id_usuario=id_usuario).delete()
        efetivar()
