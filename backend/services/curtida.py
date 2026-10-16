from repositories.repository import CurtidaRepository
from services.comum import ErroValidacao
from services.feed import FeedService
from services.notificacao import NotificacaoService
from services.usuario import UsuarioService


class CurtidaService:

    @staticmethod
    def alternar(id_usuario, tipo_alvo, id_alvo):
        if id_usuario is None:
            raise ErroValidacao("Informe o usuário.", status=401)
        quem_curtiu = UsuarioService.buscar(id_usuario)
        alvo = FeedService.buscar_alvo(tipo_alvo, id_alvo)

        existente = CurtidaRepository.buscar(id_usuario, tipo_alvo, id_alvo)
        if existente:
            CurtidaRepository.descurtir(existente)
            curti = False
        else:
            CurtidaRepository.curtir(id_usuario, tipo_alvo, id_alvo)
            curti = True
            if alvo.id_usuario != id_usuario:
                rotulo = "treino" if tipo_alvo == "atividade" else "postagem"
                NotificacaoService.gerar(
                    alvo.id_usuario,
                    "curtida",
                    f"{quem_curtiu.nome} curtiu seu {rotulo}.",
                    tipo_alvo=tipo_alvo,
                    id_alvo=id_alvo,
                )

        return {"curti": curti, "curtidas": CurtidaRepository.contar(tipo_alvo, id_alvo)}
