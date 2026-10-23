from database import db
from models.postagem import Postagem
from models.usuario import Usuario
from repositories.apoio import clausula_maior_de_idade_ou_proprio


class PostagemRepository:

    @staticmethod
    def buscar_por_id(id_postagem):
        return db.session.get(Postagem, id_postagem)

    @staticmethod
    def criar(id_usuario, texto, foto):
        postagem = Postagem(id_usuario=id_usuario, texto=texto, foto=foto)
        db.session.add(postagem)
        db.session.commit()
        return postagem

    @staticmethod
    def excluir(postagem):
        db.session.delete(postagem)
        db.session.commit()

    @staticmethod
    def listar_publicas(limite, id_solicitante=None):
        return (
            Postagem.query.join(Usuario, Postagem.id_usuario == Usuario.id_usuario)
            .filter(Usuario.perfil_publico.is_(True), clausula_maior_de_idade_ou_proprio(id_solicitante))
            .order_by(Postagem.data_registro.desc())
            .limit(limite)
            .all()
        )

    @staticmethod
    def listar_do_usuario(id_usuario):
        return Postagem.query.filter_by(id_usuario=id_usuario).all()
