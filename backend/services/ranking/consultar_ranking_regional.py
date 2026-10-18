from repositories.repository import RankingRepository
from services.comum import ErroValidacao
from services.ranking.apoio import LIMITE_PADRAO, normalizar_limite_ranking


class ConsultarRankingRegionalService:

    @staticmethod
    def executar(cidade, limite=LIMITE_PADRAO):
        cidade = (cidade or "").strip()
        if not cidade:
            raise ErroValidacao(
                "Informe a cidade para ver o ranking regional."
            )
        return RankingRepository.regional(cidade, normalizar_limite_ranking(limite))
