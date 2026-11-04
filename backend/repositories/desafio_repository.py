from models.desafio import Desafio


class DesafioRepository:

    @staticmethod
    def listar_ativos(hoje):
        return (
            Desafio.query.filter(Desafio.data_fim >= hoje)
            .order_by(Desafio.data_inicio.asc())
            .all()
        )
