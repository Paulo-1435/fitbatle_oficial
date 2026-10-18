from repositories.repository import RankingRepository
from services.grupo.apoio import exigir_membro


class ConsultarRankingGrupoService:

    @staticmethod
    def executar(id_grupo, id_usuario, limite=20):
        exigir_membro(id_grupo, id_usuario)
        return RankingRepository.grupo(id_grupo, limite)
