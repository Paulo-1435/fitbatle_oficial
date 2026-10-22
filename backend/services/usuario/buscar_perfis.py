from repositories.repository import UsuarioRepository
from services.comum import ErroValidacao
from services.usuario.apoio import e_maior_de_idade


class BuscarPerfisService:

    BUSCA_MINIMO_CARACTERES = 2
    BUSCA_LIMITE = 20

    @staticmethod
    def executar(termo, id_solicitante):
        termo = (termo or "").strip()
        if len(termo) < BuscarPerfisService.BUSCA_MINIMO_CARACTERES:
            raise ErroValidacao(
                f"Digite ao menos {BuscarPerfisService.BUSCA_MINIMO_CARACTERES} letras para buscar."
            )
        resultados = UsuarioRepository.buscar_publicos(termo, id_solicitante)
        adultos = [u for u in resultados if e_maior_de_idade(u)]
        return adultos[: BuscarPerfisService.BUSCA_LIMITE]
