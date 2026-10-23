from sqlalchemy import func
from database import db
from models.atividade import Atividade
from models.usuario import Usuario
from repositories.apoio import clausula_maior_de_idade_ou_proprio


class AtividadeRepository:

    @staticmethod
    def listar_do_usuario(id_usuario):
        return (
            Atividade.query.filter_by(id_usuario=id_usuario)
            .order_by(Atividade.data_registro.desc())
            .all()
        )

    @staticmethod
    def buscar_por_id(id_atividade):
        return db.session.get(Atividade, id_atividade)

    @staticmethod
    def criar(id_usuario, dados):
        atividade = Atividade(
            id_usuario=id_usuario,
            tipo=dados["tipo"],
            titulo=dados.get("titulo"),
            descricao=dados.get("descricao"),
            tempo_min=dados.get("tempo_min"),
            distancia_km=dados.get("distancia_km"),
            carga_kg=dados.get("carga_kg"),
            repeticoes=dados.get("repeticoes"),
            pontuacao=dados["pontuacao"],
        )
        db.session.add(atividade)
        db.session.commit()
        return atividade

    @staticmethod
    def excluir(atividade):
        db.session.delete(atividade)
        db.session.commit()

    @staticmethod
    def listar_publicas(limite, id_solicitante=None):
        return (
            Atividade.query.join(Usuario, Atividade.id_usuario == Usuario.id_usuario)
            .filter(Usuario.perfil_publico.is_(True), clausula_maior_de_idade_ou_proprio(id_solicitante))
            .order_by(Atividade.data_registro.desc())
            .limit(limite)
            .all()
        )

    @staticmethod
    def maior_carga(id_usuario, titulo_normalizado):
        resultado = (
            db.session.query(func.max(Atividade.carga_kg))
            .filter(
                Atividade.id_usuario == id_usuario,
                Atividade.tipo == "musculacao",
                func.lower(Atividade.titulo) == titulo_normalizado,
            )
            .scalar()
        )
        return float(resultado) if resultado is not None else None

    @staticmethod
    def contar_desde(id_usuario, data_inicio):
        return Atividade.query.filter(
            Atividade.id_usuario == id_usuario,
            Atividade.data_registro >= data_inicio,
        ).count()

    @staticmethod
    def contar_no_periodo(id_usuario, inicio, fim, titulo_normalizado=None):
        query = Atividade.query.filter(
            Atividade.id_usuario == id_usuario,
            Atividade.data_registro >= inicio,
            Atividade.data_registro < fim,
        )
        if titulo_normalizado:
            query = query.filter(func.lower(Atividade.titulo) == titulo_normalizado)
        return query.count()

    @staticmethod
    def maior_carga_no_periodo(id_usuario, inicio, fim, titulo_normalizado=None):
        query = db.session.query(func.max(Atividade.carga_kg)).filter(
            Atividade.id_usuario == id_usuario,
            Atividade.tipo == "musculacao",
            Atividade.data_registro >= inicio,
            Atividade.data_registro < fim,
        )
        if titulo_normalizado:
            query = query.filter(func.lower(Atividade.titulo) == titulo_normalizado)
        resultado = query.scalar()
        return float(resultado) if resultado is not None else None

    @staticmethod
    def listar_do_usuario_por_titulo(id_usuario, titulo_normalizado):
        return (
            Atividade.query.filter(
                Atividade.id_usuario == id_usuario,
                Atividade.tipo == "musculacao",
                func.lower(Atividade.titulo) == titulo_normalizado,
            )
            .order_by(Atividade.data_registro.asc())
            .all()
        )

    @staticmethod
    def pontuacao_total_desde(id_usuario, desde_utc):
        total = (
            db.session.query(func.coalesce(func.sum(Atividade.pontuacao), 0))
            .filter(Atividade.id_usuario == id_usuario, Atividade.data_registro >= desde_utc)
            .scalar()
        )
        return int(total)

    @staticmethod
    def pontuacoes_desde(id_usuario, desde_utc):
        return (
            db.session.query(Atividade.data_registro, Atividade.pontuacao)
            .filter(Atividade.id_usuario == id_usuario, Atividade.data_registro >= desde_utc)
            .all()
        )

    @staticmethod
    def distribuicao_por_tipo(id_usuario):
        linhas = (
            db.session.query(Atividade.tipo, func.count(Atividade.id_atividade))
            .filter(Atividade.id_usuario == id_usuario)
            .group_by(Atividade.tipo)
            .all()
        )
        return dict(linhas)

    @staticmethod
    def datas_registro(id_usuario):
        linhas = (
            db.session.query(Atividade.data_registro)
            .filter(Atividade.id_usuario == id_usuario)
            .all()
        )
        return [linha[0] for linha in linhas]

    @staticmethod
    def totais(id_usuario):
        total_treinos, total_tempo = (
            db.session.query(
                func.count(Atividade.id_atividade),
                func.coalesce(func.sum(Atividade.tempo_min), 0),
            )
            .filter(Atividade.id_usuario == id_usuario)
            .first()
        )
        return total_treinos, total_tempo

    @staticmethod
    def titulos_distintos(id_usuario):
        linhas = (
            db.session.query(Atividade.titulo)
            .filter(
                Atividade.id_usuario == id_usuario,
                Atividade.tipo == "musculacao",
                Atividade.carga_kg.isnot(None),
            )
            .distinct()
            .order_by(Atividade.titulo)
            .all()
        )
        return [linha[0] for linha in linhas if linha[0]]
