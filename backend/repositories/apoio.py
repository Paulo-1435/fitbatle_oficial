from datetime import date
from database import db
from utils import IDADE_MAIORIDADE, limite_nascimento_maioridade
from models.usuario import Usuario


COLUNAS_RANKING = "id_usuario, nome, cidade, estado, pontuacao_total, posicao"


def clausula_maior_de_idade_ou_proprio(id_solicitante):
    limite = limite_nascimento_maioridade(date.today())
    maior = db.or_(
        Usuario.data_nascimento <= limite,
        db.and_(
            Usuario.data_nascimento.is_(None),
            db.or_(Usuario.idade.is_(None), Usuario.idade >= IDADE_MAIORIDADE),
        ),
    )
    if id_solicitante is None:
        return maior
    return db.or_(Usuario.id_usuario == id_solicitante, maior)


def escapar_like(termo):
    return termo.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


CAMPOS_EDITAVEIS = (
    "nome", "email", "data_nascimento", "peso", "altura",
    "cidade", "estado", "descricao",
)


def linha_ranking(linha):
    if linha is None:
        return None
    d = dict(linha)
    if "pontuacao_total" in d:
        d["pontuacao_total"] = int(d["pontuacao_total"] or 0)
    if "carga_maxima" in d and d["carga_maxima"] is not None:
        d["carga_maxima"] = float(d["carga_maxima"])
    if "posicao" in d and d["posicao"] is not None:
        d["posicao"] = int(d["posicao"])
    return d
