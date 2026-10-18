from repositories.repository import RankingRepository
from services.ranking.apoio import LIMITE_PADRAO, normalizar_limite_ranking


class ConsultarRankingGlobalService:

    @staticmethod
    def executar(limite=LIMITE_PADRAO):
        return RankingRepository.global_(normalizar_limite_ranking(limite))
