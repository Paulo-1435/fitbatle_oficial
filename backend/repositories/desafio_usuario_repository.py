from models.desafio_usuario import DesafioUsuario


class DesafioUsuarioRepository:

    @staticmethod
    def listar_do_usuario(id_usuario):
        return DesafioUsuario.query.filter_by(id_usuario=id_usuario).all()
