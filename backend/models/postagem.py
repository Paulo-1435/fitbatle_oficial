from database import db
from models.base import ModeloBase
from utils import agora, iso_utc


class Postagem(ModeloBase):
    __tablename__ = "postagem"

    id_postagem = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario", ondelete="CASCADE"),
        nullable=False,
    )
    texto = db.Column(db.String(1000), nullable=False)
    foto = db.Column(db.String(255))
    data_registro = db.Column(db.DateTime, nullable=False, default=agora)

    def to_dict(self):
        return {
            "id": self.id_postagem,
            "id_usuario": self.id_usuario,
            "texto": self.texto,
            "foto": self.foto,
            "data_registro": iso_utc(self.data_registro),
        }
