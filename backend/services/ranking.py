from repositories.repository import RankingRepository
from services.comum import ErroValidacao
from services.usuario import UsuarioService


class RankingService:

    LIMITE_PADRAO = 20
    LIMITE_MAXIMO = 100

    @staticmethod
    def global_(limite=LIMITE_PADRAO):
        return RankingRepository.global_(RankingService._limite(limite))

    @staticmethod
    def regional(cidade, limite=LIMITE_PADRAO):
        cidade = (cidade or "").strip()
        if not cidade:
            raise ErroValidacao(
                "Informe a cidade para ver o ranking regional."
            )
        return RankingRepository.regional(cidade, RankingService._limite(limite))

    @staticmethod
    def por_exercicio(titulo, cidade=None, limite=LIMITE_PADRAO):
        titulo = (titulo or "").strip()
        if not titulo:
            raise ErroValidacao("Informe o exercício para ver o ranking.")
        cidade = (cidade or "").strip() or None
        return RankingRepository.por_exercicio(titulo, cidade, RankingService._limite(limite))

    @staticmethod
    def resumo_usuario(id_usuario):
        UsuarioService.buscar(id_usuario)
        return {
            "global": RankingRepository.minha_posicao_global(id_usuario),
            "regional": RankingRepository.minha_posicao_regional(id_usuario),
        }

    @staticmethod
    def _limite(valor):
        try:
            numero = int(valor)
        except (TypeError, ValueError):
            return RankingService.LIMITE_PADRAO
        return max(1, min(numero, RankingService.LIMITE_MAXIMO))
