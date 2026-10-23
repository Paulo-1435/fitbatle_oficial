from sqlalchemy.exc import IntegrityError
from database import db
from models.convite import Convite
from models.grupo import Grupo
from models.usuario import Usuario


class ConviteRepository:

    @staticmethod
    def criar(id_grupo, id_remetente, id_destinatario):
        convite = Convite(id_grupo=id_grupo, id_remetente=id_remetente, id_destinatario=id_destinatario)
        db.session.add(convite)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return convite

    @staticmethod
    def buscar_por_id(id_convite):
        return db.session.get(Convite, id_convite)

    @staticmethod
    def buscar_pendente(id_grupo, id_destinatario):
        return Convite.query.filter_by(
            id_grupo=id_grupo, id_destinatario=id_destinatario, status="pendente",
        ).first()

    @staticmethod
    def listar_pendentes_recebidos(id_usuario):
        return (
            db.session.query(Convite, Grupo, Usuario)
            .join(Grupo, Grupo.id_grupo == Convite.id_grupo)
            .join(Usuario, Usuario.id_usuario == Convite.id_remetente)
            .filter(Convite.id_destinatario == id_usuario, Convite.status == "pendente")
            .order_by(Convite.data_envio.desc())
            .all()
        )

    @staticmethod
    def contar_enviados_pendentes(id_usuario):
        return Convite.query.filter_by(id_remetente=id_usuario, status="pendente").count()

    @staticmethod
    def salvar(convite):
        db.session.add(convite)
        db.session.commit()
        return convite
