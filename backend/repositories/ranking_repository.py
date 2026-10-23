from sqlalchemy import text
from database import db
from repositories.apoio import COLUNAS_RANKING, linha_ranking


class RankingRepository:

    @staticmethod
    def global_(limite):
        sql = text(
            f"SELECT {COLUNAS_RANKING} FROM vw_ranking_global "
            "ORDER BY posicao LIMIT :lim"
        )
        linhas = db.session.execute(sql, {"lim": limite}).mappings()
        return [linha_ranking(linha) for linha in linhas]

    @staticmethod
    def regional_todos():
        sql = text(f"SELECT {COLUNAS_RANKING} FROM vw_ranking_regional")
        linhas = db.session.execute(sql).mappings()
        return [linha_ranking(linha) for linha in linhas]

    @staticmethod
    def por_exercicio(titulo, cidade, limite):
        sql = text(
            "SELECT id_usuario, nome, cidade, estado, titulo, carga_maxima, posicao "
            "FROM vw_ranking_exercicio "
            "WHERE titulo_normalizado = :titulo "
            + ("AND cidade = :cidade " if cidade else "")
            + "ORDER BY posicao LIMIT :lim"
        )
        parametros = {"titulo": titulo.strip().lower(), "lim": limite}
        if cidade:
            parametros["cidade"] = cidade
        linhas = db.session.execute(sql, parametros).mappings()
        return [linha_ranking(linha) for linha in linhas]

    @staticmethod
    def minha_posicao_global(id_usuario):
        sql = text(
            "SELECT posicao, pontuacao_total FROM vw_ranking_global "
            "WHERE id_usuario = :id"
        )
        return linha_ranking(db.session.execute(sql, {"id": id_usuario}).mappings().first())

    @staticmethod
    def minha_posicao_regional(id_usuario):
        sql = text(
            "SELECT posicao, pontuacao_total, cidade FROM vw_ranking_regional "
            "WHERE id_usuario = :id"
        )
        return linha_ranking(db.session.execute(sql, {"id": id_usuario}).mappings().first())

    @staticmethod
    def grupo(id_grupo, limite):
        sql = text(
            "SELECT id_usuario, nome, pontuacao_total, posicao FROM vw_ranking_grupo "
            "WHERE id_grupo = :id_grupo ORDER BY posicao LIMIT :lim"
        )
        linhas = db.session.execute(sql, {"id_grupo": id_grupo, "lim": limite}).mappings()
        return [linha_ranking(linha) for linha in linhas]
