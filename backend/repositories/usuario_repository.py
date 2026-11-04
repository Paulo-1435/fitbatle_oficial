from database import db
from models.consentimento import Consentimento
from models.usuario import Usuario
from repositories.apoio import escapar_like


class UsuarioRepository:

    @staticmethod
    def listar(filtro_nome=None):
        query = Usuario.query
        if filtro_nome:
            query = query.filter(Usuario.nome.like(f"%{filtro_nome}%"))
        return query.order_by(Usuario.nome).all()

    @staticmethod
    def buscar_publicos(termo, id_excluido):
        padrao = "%" + escapar_like(termo) + "%"
        return (
            Usuario.query.join(
                Consentimento,
                db.and_(
                    Consentimento.id_usuario == Usuario.id_usuario,
                    Consentimento.chave == "busca_perfil",
                    Consentimento.aceito.is_(True),
                ),
            )
            .filter(
                Usuario.perfil_publico.is_(True),
                Usuario.id_usuario != id_excluido,
                db.or_(
                    Usuario.nome.like(padrao, escape="\\"),
                    Usuario.cidade.like(padrao, escape="\\"),
                ),
            )
            .order_by(Usuario.nome)
            .all()
        )

    @staticmethod
    def buscar_por_email(email):
        return Usuario.query.filter_by(email=email).first()
