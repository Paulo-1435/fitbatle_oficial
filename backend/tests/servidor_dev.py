import os
import sys
from datetime import date, timedelta

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

CAMINHO_BANCO = os.path.join(RAIZ, "dev.db").replace("\\", "/")
os.environ.setdefault("DB_URI", "sqlite:///" + CAMINHO_BANCO)

from app import criar_app
from database import db
from models.model import Atividade, Desafio, DesafioUsuario, Usuario
from services import (
    AlternarCurtidaService,
    CadastrarUsuarioService,
    CriarComentarioService,
    CriarGrupoService,
    CriarMetaService,
    EntrarGrupoPorCodigoService,
)
from services.atividade.apoio import calcular_pontuacao, nivel_por_xp
from tests.apoio import CONSENTIMENTOS_OPCIONAIS_ACEITOS, criar_views_de_ranking
from utils import inicio_utc_do_dia_local

SENHA = "senhaforte123"
PRINCIPAL = "helena@fitbattle.dev"

USUARIOS = [
    ("Helena Duarte", PRINCIPAL, 29, "Belo Horizonte", "MG"),
    ("Lucas Ferreira", "lucas@fitbattle.dev", 26, "Belo Horizonte", "MG"),
    ("Marina Alves", "marina@fitbattle.dev", 24, "Belo Horizonte", "MG"),
    ("Bruno Teixeira", "bruno@fitbattle.dev", 31, "Belo Horizonte", "MG"),
    ("Carolina Pires", "carolina@fitbattle.dev", 27, "Belo Horizonte", "MG"),
    ("Diego Moreira", "diego@fitbattle.dev", 33, "Contagem", "MG"),
    ("Juliana Rocha", "juliana@fitbattle.dev", 35, "Belo Horizonte", "MG"),
    ("Rafael Nunes", "rafael@fitbattle.dev", 30, "Belo Horizonte", "MG"),
    ("Fernanda Lima", "fernanda@fitbattle.dev", 25, "Nova Lima", "MG"),
    ("Thiago Barros", "thiago@fitbattle.dev", 28, "Belo Horizonte", "MG"),
    ("Beatriz Correia", "beatriz@fitbattle.dev", 26, "Belo Horizonte", "MG"),
    ("Gustavo Melo", "gustavo@fitbattle.dev", 40, "Betim", "MG"),
]

DESCRICOES = [
    "Supino reto com pausa de um segundo no peito. Última série até a falha técnica.",
    "Treino de costas focado em remada e puxada. Descanso de 90 segundos entre as séries.",
    "Agachamento livre e leg press. Subi a carga em relação à semana passada.",
    "Corrida leve no parque, ritmo constante e respiração controlada.",
    "Intervalado na bike: um minuto forte e um minuto leve, repetidos.",
    "Ombro e abdômen com execução lenta, sem balanço.",
    "Yoga de recuperação depois do treino pesado. Alongamento de quadril e costas.",
    "Full body com carga moderada. Boa energia do começo ao fim.",
    "Esteira em ritmo de tempo: aquecimento de 10 minutos e bloco forte no meio.",
    "Peito e tríceps mantendo a amplitude completa em todas as repetições.",
    "Remada curvada com halteres. Boa tensão nas costas.",
    "Treino leve para manter a rotina depois da viagem.",
    "Subida de rampa na esteira, inclinação 8 por 25 minutos.",
    "Pernas: afundo e cadeira extensora. Reduzi a carga no último bloco.",
    "Caminhada rápida na hora do almoço, 40 minutos.",
]

MUSCULACAO = ["Costas e bíceps", "Pernas", "Ombros e abdômen", "Full body", "Peito e tríceps"]
CARDIO = ["Corrida no parque", "Bike ergométrica", "Esteira intervalada", "Caminhada rápida"]

HELENA_DIAS_ATRAS = [56, 54, 52, 49, 47, 45, 42, 40, 38, 35, 33, 31, 28, 26, 24, 21, 19, 17, 14, 12, 10, 7, 5, 3, 1, 0]


def treino_principal(i, dias_atras):
    descricao = DESCRICOES[i % len(DESCRICOES)]
    if i % 3 == 1:
        return {
            "tipo": "cardio", "titulo": CARDIO[i % len(CARDIO)], "descricao": descricao,
            "tempo_min": 30 + (i % 4) * 5, "distancia_km": round(3 + (i % 5) * 0.8, 1),
            "dias_atras": dias_atras,
        }
    if i % 3 == 0:
        return {
            "tipo": "musculacao", "titulo": "Supino reto", "descricao": descricao,
            "tempo_min": 45 + (i % 4) * 5, "carga_kg": round(60 + i * 1.5, 1), "repeticoes": 8 - (i % 3),
            "dias_atras": dias_atras,
        }
    return {
        "tipo": "musculacao", "titulo": MUSCULACAO[i % len(MUSCULACAO)], "descricao": descricao,
        "tempo_min": 45 + (i % 4) * 5, "carga_kg": 40 + (i % 5) * 8, "repeticoes": 8 + (i % 3) * 2,
        "dias_atras": dias_atras,
    }


def treino_de_outro(i, k):
    descricao = DESCRICOES[(i * 3 + k) % len(DESCRICOES)]
    dias_atras = 2 + k * 4 + (i % 3)
    if k % 2 == 0:
        return {
            "tipo": "musculacao", "titulo": MUSCULACAO[(i + k) % len(MUSCULACAO)], "descricao": descricao,
            "tempo_min": 40 + (k % 3) * 10, "carga_kg": 30 + ((i + k) % 6) * 10, "repeticoes": 8 + (k % 3),
            "dias_atras": dias_atras,
        }
    return {
        "tipo": "cardio", "titulo": CARDIO[(i + k) % len(CARDIO)], "descricao": descricao,
        "tempo_min": 25 + (k % 3) * 10, "distancia_km": round(2.5 + (k % 4) * 0.7, 1),
        "dias_atras": dias_atras,
    }


def planos_de_treino():
    planos = {PRINCIPAL: [treino_principal(i, dias) for i, dias in enumerate(HELENA_DIAS_ATRAS)]}
    for i, (_, email, _, _, _) in enumerate(USUARIOS[1:], start=1):
        planos[email] = [treino_de_outro(i, k) for k in range(3 + i % 3)]
    return planos


def registrar_treinos_historicos(ids, hoje):
    primeira = None
    for email, treinos in planos_de_treino().items():
        uid = ids[email]
        xp = 0
        for treino in treinos:
            dias_atras = treino.pop("dias_atras")
            dados = dict(treino)
            dados["pontuacao"] = calcular_pontuacao(dados)
            atividade = Atividade(id_usuario=uid, **dados).salvar()
            atividade.data_registro = inicio_utc_do_dia_local(hoje - timedelta(days=dias_atras)) + timedelta(hours=18)
            db.session.commit()
            xp += atividade.pontuacao
            primeira = primeira or atividade.id_atividade
        usuario = Usuario.buscar_por_id(uid)
        usuario.xp = xp
        usuario.nivel = nivel_por_xp(xp)
        usuario.salvar()
    return primeira


def data_nascimento_para_idade(idade):
    hoje = date.today()
    try:
        nascimento = hoje.replace(year=hoje.year - idade)
    except ValueError:
        nascimento = hoje.replace(year=hoje.year - idade, month=3, day=1)
    return nascimento.isoformat()


def popular():
    if Usuario.query.count() > 0:
        return
    ids = {}
    for nome, email, idade, cidade, estado in USUARIOS:
        usuario = CadastrarUsuarioService.executar({
            "nome": nome, "email": email,
            "data_nascimento": data_nascimento_para_idade(idade), "senha": SENHA,
            "aceite_termos": True, "consentimentos": CONSENTIMENTOS_OPCIONAIS_ACEITOS,
        })
        usuario.cidade = cidade
        usuario.estado = estado
        db.session.commit()
        ids[email] = usuario.id_usuario

    hoje = date.today()
    primeira = registrar_treinos_historicos(ids, hoje)

    CriarComentarioService.executar(ids["carolina@fitbattle.dev"], "atividade", primeira, "Mandou bem demais!")
    CriarComentarioService.executar(ids["lucas@fitbattle.dev"], "atividade", primeira, "Bora pra cima!")
    AlternarCurtidaService.executar(ids["lucas@fitbattle.dev"], "atividade", primeira)
    AlternarCurtidaService.executar(ids["diego@fitbattle.dev"], "atividade", primeira)

    grupo = CriarGrupoService.executar(ids[PRINCIPAL], {
        "nome": "Turma do Parque", "descricao": "Grupo para treinar junto e acompanhar a evolução.",
    })
    EntrarGrupoPorCodigoService.executar(ids["lucas@fitbattle.dev"], grupo.codigo_convite)
    CriarMetaService.executar(ids[PRINCIPAL], {
        "titulo": "Supino 120 kg", "tipo": "curto_prazo", "tipo_metrica": "carga_maxima",
        "exercicio": "supino reto", "valor_objetivo": 120, "data_final": "2030-12-31",
    })

    desafio = Desafio(**{
        "nome": "Desafio: 5 treinos nesta semana",
        "descricao": "Registre 5 treinos no período para ganhar 100 XP de bônus.",
        "exercicio": "livre",
        "tipo_metrica": "treinos",
        "valor_objetivo": 5,
        "data_inicio": hoje - timedelta(days=3),
        "data_fim": hoje + timedelta(days=11),
        "recompensa_xp": 100,
    }).salvar()
    DesafioUsuario(id_desafio=desafio.id_desafio, id_usuario=ids[PRINCIPAL], status="inscrito").salvar()


def preparar():
    app = criar_app()
    with app.app_context():
        criar_views_de_ranking(db)
        popular()
    return app


if __name__ == "__main__":
    preparar().run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=False,
    )
