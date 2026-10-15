from repositories.repository import CurtidaRepository
from services.comum import ErroValidacao
from services.feed import FeedService
from services.usuario import UsuarioService


class CurtidaService:

    @staticmethod
    def alternar(id_usuario, tipo_alvo, id_alvo):
        if id_usuario is None:
            raise ErroValidacao("Informe o usuário.", status=401)
        UsuarioService.buscar(id_usuario)
        FeedService.buscar_alvo(tipo_alvo, id_alvo)

        existente = CurtidaRepository.buscar(id_usuario, tipo_alvo, id_alvo)
        if existente:
            CurtidaRepository.descurtir(existente)
            curti = False
        else:
            CurtidaRepository.curtir(id_usuario, tipo_alvo, id_alvo)
            curti = True

        return {"curti": curti, "curtidas": CurtidaRepository.contar(tipo_alvo, id_alvo)}
