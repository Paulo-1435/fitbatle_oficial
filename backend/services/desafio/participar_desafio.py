from repositories.repository import DesafioUsuarioRepository
from services.comum import ErroValidacao
from services.desafio.apoio import buscar_desafio, desafio_com_progresso
from utils import agora


class ParticiparDesafioService:

    @staticmethod
    def executar(id_usuario, id_desafio):
        desafio = buscar_desafio(id_desafio)
        hoje = agora().date()
        if desafio.data_fim < hoje:
            raise ErroValidacao("Este desafio já foi encerrado.")

        inscricao = DesafioUsuarioRepository.buscar(id_desafio, id_usuario)
        if inscricao and inscricao.status == "inscrito":
            raise ErroValidacao("Você já está inscrito neste desafio.", status=409)
        if inscricao:
            inscricao.status = "inscrito"
            inscricao.concluido_em = None
            DesafioUsuarioRepository.salvar(inscricao)
        else:
            DesafioUsuarioRepository.inscrever(id_desafio, id_usuario)
        return desafio_com_progresso(desafio, id_usuario)
