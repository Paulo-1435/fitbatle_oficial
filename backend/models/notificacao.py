from database import db
from models.base import ModeloBase
from utils import agora, iso_utc


class Notificacao(ModeloBase):
    __tablename__ = "notificacao"

    id_notif = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario", ondelete="CASCADE"),
        nullable=False,
    )
    tipo = db.Column(db.String(60), nullable=False)
    mensagem = db.Column(db.String(300), nullable=False)
    lida = db.Column(db.Boolean, nullable=False, default=False)
    tipo_alvo = db.Column(db.String(20))
    id_alvo = db.Column(db.Integer)
    data_envio = db.Column(db.DateTime, nullable=False, default=agora)

    def to_dict(self):
        return {
            "id": self.id_notif,
            "tipo": self.tipo,
            "mensagem": self.mensagem,
            "lida": self.lida,
            "tipo_alvo": self.tipo_alvo,
            "id_alvo": self.id_alvo,
            "data_envio": iso_utc(self.data_envio),
        }
