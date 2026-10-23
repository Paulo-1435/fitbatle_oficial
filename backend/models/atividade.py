from database import db
from models.base import ModeloBase
from utils import agora, iso_utc


class Atividade(ModeloBase):
    __tablename__ = "atividade"

    id_atividade = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario", ondelete="CASCADE"),
        nullable=False,
    )
    tipo = db.Column(db.String(60), nullable=False)
    titulo = db.Column(db.String(120))
    descricao = db.Column(db.String(500))
    tempo_min = db.Column(db.Integer)
    distancia_km = db.Column(db.Numeric(6, 2))
    carga_kg = db.Column(db.Numeric(6, 2))
    repeticoes = db.Column(db.Integer)
    pontuacao = db.Column(db.Integer, nullable=False, default=0)
    data_registro = db.Column(db.DateTime, nullable=False, default=agora)

    def to_dict(self):
        return {
            "id": self.id_atividade,
            "id_usuario": self.id_usuario,
            "tipo": self.tipo,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "tempo_min": self.tempo_min,
            "distancia_km": float(self.distancia_km) if self.distancia_km is not None else None,
            "carga_kg": float(self.carga_kg) if self.carga_kg is not None else None,
            "repeticoes": self.repeticoes,
            "pontuacao": self.pontuacao,
            "data_registro": iso_utc(self.data_registro),
        }
