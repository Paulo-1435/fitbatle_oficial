from database import db
from models.base import ModeloBase
from utils import agora, iso_utc


class Comentario(ModeloBase):
    __tablename__ = "comentario"

    id_comentario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario", ondelete="CASCADE"),
        nullable=False,
    )
    tipo_alvo = db.Column(db.String(20), nullable=False)
    id_alvo = db.Column(db.Integer, nullable=False)
    texto = db.Column(db.String(500), nullable=False)
    data_registro = db.Column(db.DateTime, nullable=False, default=agora)

    def to_dict(self):
        return {
            "id": self.id_comentario,
            "id_usuario": self.id_usuario,
            "texto": self.texto,
            "data_registro": iso_utc(self.data_registro),
        }
