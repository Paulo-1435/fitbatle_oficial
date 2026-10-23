from database import db
from models.grupo import Grupo
from models.grupo_membro import GrupoMembro
from models.usuario import Usuario


class GrupoRepository:

    @staticmethod
    def criar(nome, descricao, id_criador, codigo_convite):
        grupo = Grupo(
            nome=nome, descricao=descricao, id_criador=id_criador, codigo_convite=codigo_convite,
        )
        db.session.add(grupo)
        db.session.commit()
        return grupo

    @staticmethod
    def buscar_por_id(id_grupo):
        return db.session.get(Grupo, id_grupo)

    @staticmethod
    def buscar_por_codigo(codigo):
        return Grupo.query.filter_by(codigo_convite=codigo).first()

    @staticmethod
    def salvar(grupo):
        db.session.add(grupo)
        db.session.commit()
        return grupo

    @staticmethod
    def listar_do_usuario(id_usuario):
        return (
            db.session.query(Grupo, GrupoMembro.papel)
            .join(GrupoMembro, GrupoMembro.id_grupo == Grupo.id_grupo)
            .filter(GrupoMembro.id_usuario == id_usuario)
            .order_by(Grupo.nome)
            .all()
        )

    @staticmethod
    def contar_membros(id_grupo):
        return GrupoMembro.query.filter_by(id_grupo=id_grupo).count()

    @staticmethod
    def papel_do_membro(id_grupo, id_usuario):
        membro = GrupoMembro.query.filter_by(id_grupo=id_grupo, id_usuario=id_usuario).first()
        return membro.papel if membro else None

    @staticmethod
    def adicionar_membro(id_grupo, id_usuario, papel="membro"):
        membro = GrupoMembro(id_grupo=id_grupo, id_usuario=id_usuario, papel=papel)
        db.session.add(membro)
        db.session.commit()
        return membro

    @staticmethod
    def listar_membros(id_grupo):
        return (
            db.session.query(Usuario, GrupoMembro.papel)
            .join(GrupoMembro, GrupoMembro.id_usuario == Usuario.id_usuario)
            .filter(GrupoMembro.id_grupo == id_grupo)
            .order_by(GrupoMembro.papel, Usuario.nome)
            .all()
        )

    @staticmethod
    def ids_membros(id_grupo):
        linhas = (
            db.session.query(GrupoMembro.id_usuario)
            .filter(GrupoMembro.id_grupo == id_grupo)
            .all()
        )
        return {id_usuario for (id_usuario,) in linhas}
