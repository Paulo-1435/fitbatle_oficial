from repositories.repository import NotificacaoRepository


class ListarNotificacoesService:

    @staticmethod
    def executar(id_usuario):
        return NotificacaoRepository.listar_do_usuario(id_usuario)
