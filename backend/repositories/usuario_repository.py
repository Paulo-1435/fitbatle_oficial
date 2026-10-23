from sqlalchemy.exc import IntegrityError
from database import db
from models.consentimento import Consentimento
from models.usuario import Usuario
from repositories.apoio import CAMPOS_EDITAVEIS, escapar_like


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
    def buscar_por_id(id_usuario):
        return db.session.get(Usuario, id_usuario)

    @staticmethod
    def buscar_por_email(email):
        return Usuario.query.filter_by(email=email).first()

    @staticmethod
    def criar(dados):
        usuario = Usuario(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            data_nascimento=dados.get("data_nascimento"),
            cidade=dados.get("cidade"),
            estado=dados.get("estado"),
            descricao=dados.get("descricao"),
            perfil_publico=dados.get("perfil_publico", True),
            responsavel_nome=dados.get("responsavel_nome"),
            responsavel_email=dados.get("responsavel_email"),
            responsavel_autorizado_em=dados.get("responsavel_autorizado_em"),
        )
        db.session.add(usuario)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return usuario

    @staticmethod
    def atualizar(usuario, dados):
        for campo in CAMPOS_EDITAVEIS:
            if dados.get(campo) is not None:
                setattr(usuario, campo, dados[campo])
        if dados.get("senha"):
            usuario.senha = dados["senha"]
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return usuario

    @staticmethod
    def excluir(usuario):
        db.session.delete(usuario)
        db.session.commit()

    @staticmethod
    def salvar(usuario):
        db.session.add(usuario)
        db.session.commit()
        return usuario
