from repositories.repository import ComentarioRepository, UsuarioRepository
from services.comum import ErroValidacao
from services.feed import FeedService
from services.usuario import UsuarioService


class ComentarioService:

    TEXTO_MAX = 500

    @staticmethod
    def listar(tipo_alvo, id_alvo):
        FeedService.buscar_alvo(tipo_alvo, id_alvo)
        comentarios = ComentarioRepository.listar(tipo_alvo, id_alvo)

        resultado = []
        for c in comentarios:
            dado = c.to_dict()
            autor = UsuarioRepository.buscar_por_id(c.id_usuario)
            dado["usuario"] = {
                "id": autor.id_usuario if autor else None,
                "nome": autor.nome if autor else "Usuário removido",
                "foto": autor.foto if autor else None,
            }
            resultado.append(dado)
        return resultado

    @staticmethod
    def criar(id_usuario, tipo_alvo, id_alvo, texto):
        if id_usuario is None:
            raise ErroValidacao("Informe o usuário.", status=401)
        UsuarioService.buscar(id_usuario)
        FeedService.buscar_alvo(tipo_alvo, id_alvo)

        texto = (texto or "").strip()
        if not texto:
            raise ErroValidacao("Escreva um comentário.")
        if len(texto) > ComentarioService.TEXTO_MAX:
            raise ErroValidacao(
                f"O comentário pode ter no máximo {ComentarioService.TEXTO_MAX} caracteres."
            )

        return ComentarioRepository.criar(id_usuario, tipo_alvo, id_alvo, texto)

    @staticmethod
    def excluir(id_usuario, id_comentario):
        if id_usuario is None:
            raise ErroValidacao("Informe o usuário.", status=401)
        comentario = ComentarioRepository.buscar_por_id(id_comentario)
        if not comentario:
            raise ErroValidacao("Comentário não encontrado.", status=404)
        if comentario.id_usuario != id_usuario:
            raise ErroValidacao("Você só pode excluir seus próprios comentários.", status=403)
        ComentarioRepository.excluir(comentario)
