from database import db
from models.desafio_usuario import DesafioUsuario


class DesafioUsuarioRepository:

    @staticmethod
    def buscar(id_desafio, id_usuario):
        return db.session.get(DesafioUsuario, (id_desafio, id_usuario))

    @staticmethod
    def inscrever(id_desafio, id_usuario):
        inscricao = DesafioUsuario(id_desafio=id_desafio, id_usuario=id_usuario, status="inscrito")
        db.session.add(inscricao)
        db.session.commit()
        return inscricao

    @staticmethod
    def salvar(inscricao):
        db.session.add(inscricao)
        db.session.commit()
        return inscricao

    @staticmethod
    def listar_do_usuario(id_usuario):
        return DesafioUsuario.query.filter_by(id_usuario=id_usuario).all()
