from models.desafio import Desafio
from repositories.repository import DesafioUsuarioRepository
from services.desafio.apoio import avaliar_conclusao


class AvaliarDesafiosDoUsuarioService:

    @staticmethod
    def executar(id_usuario):
        for inscricao in DesafioUsuarioRepository.listar_do_usuario(id_usuario):
            if inscricao.status != "inscrito":
                continue
            desafio = Desafio.buscar_por_id(inscricao.id_desafio)
            if desafio:
                avaliar_conclusao(desafio, inscricao)
