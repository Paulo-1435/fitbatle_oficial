from repositories.repository import DesafioUsuarioRepository
from services.comum import ErroValidacao
from services.desafio.apoio import buscar_desafio, desafio_com_progresso


class DesistirDesafioService:

    @staticmethod
    def executar(id_usuario, id_desafio):
        inscricao = DesafioUsuarioRepository.buscar(id_desafio, id_usuario)
        if not inscricao or inscricao.status != "inscrito":
            raise ErroValidacao("Você não está inscrito neste desafio.", status=404)
        inscricao.status = "desistiu"
        DesafioUsuarioRepository.salvar(inscricao)
        desafio = buscar_desafio(id_desafio)
        return desafio_com_progresso(desafio, id_usuario)
