from repositories.repository import ComentarioRepository, UsuarioRepository
from services.comum import ErroValidacao
from services.feed import FeedService
from services.notificacao import NotificacaoService
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
        autor = UsuarioService.buscar(id_usuario)
        alvo = FeedService.buscar_alvo(tipo_alvo, id_alvo)

        texto = (texto or "").strip()
        if not texto:
            raise ErroValidacao("Escreva um comentário.")
        if len(texto) > ComentarioService.TEXTO_MAX:
            raise ErroValidacao(
                f"O comentário pode ter no máximo {ComentarioService.TEXTO_MAX} caracteres."
            )

        comentario = ComentarioRepository.criar(id_usuario, tipo_alvo, id_alvo, texto)

        if alvo.id_usuario != id_usuario:
            rotulo = "treino" if tipo_alvo == "atividade" else "postagem"
            NotificacaoService.gerar(
                alvo.id_usuario,
                "comentario",
                f"{autor.nome} comentou no seu {rotulo}.",
                tipo_alvo=tipo_alvo,
                id_alvo=id_alvo,
            )

        return comentario

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
