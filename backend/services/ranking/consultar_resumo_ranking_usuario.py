from repositories.repository import RankingRepository
from services.usuario.apoio import buscar_usuario_visivel


class ConsultarResumoRankingUsuarioService:

    @staticmethod
    def executar(id_usuario, id_solicitante):
        buscar_usuario_visivel(id_usuario, id_solicitante)
        return {
            "global": RankingRepository.minha_posicao_global(id_usuario),
            "regional": RankingRepository.minha_posicao_regional(id_usuario),
        }
