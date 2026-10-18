from repositories.repository import ComentarioRepository
from services.comum import ErroValidacao


class ExcluirComentarioService:

    @staticmethod
    def executar(id_usuario, id_comentario):
        if id_usuario is None:
            raise ErroValidacao("Informe o usuário.", status=401)
        comentario = ComentarioRepository.buscar_por_id(id_comentario)
        if not comentario:
            raise ErroValidacao("Comentário não encontrado.", status=404)
        if comentario.id_usuario != id_usuario:
            raise ErroValidacao("Você só pode excluir seus próprios comentários.", status=403)
        ComentarioRepository.excluir(comentario)
