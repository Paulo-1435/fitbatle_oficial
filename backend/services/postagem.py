from repositories.repository import ComentarioRepository, CurtidaRepository, PostagemRepository
from services.comum import ErroValidacao, salvar_imagem
from services.usuario import UsuarioService


class PostagemService:

    TEXTO_MAX = 1000

    @staticmethod
    def criar(id_usuario, texto, arquivo, pasta_destino):
        if id_usuario is None:
            raise ErroValidacao("Informe o usuário.", status=401)
        UsuarioService.buscar(id_usuario)
        texto = (texto or "").strip()

        if not texto and not (arquivo and arquivo.filename):
            raise ErroValidacao("Escreva algo ou envie uma foto para publicar.")
        if len(texto) > PostagemService.TEXTO_MAX:
            raise ErroValidacao(
                f"O texto pode ter no máximo {PostagemService.TEXTO_MAX} caracteres."
            )

        foto = None
        if arquivo and arquivo.filename:
            foto = salvar_imagem(arquivo, pasta_destino, f"postagem_{id_usuario}")

        return PostagemRepository.criar(id_usuario, texto, foto)

    @staticmethod
    def excluir(id_usuario, id_postagem):
        if id_usuario is None:
            raise ErroValidacao("Informe o usuário.", status=401)
        postagem = PostagemRepository.buscar_por_id(id_postagem)
        if not postagem:
            raise ErroValidacao("Postagem não encontrada.", status=404)
        if postagem.id_usuario != id_usuario:
            raise ErroValidacao("Você só pode excluir suas próprias postagens.", status=403)
        CurtidaRepository.excluir_do_alvo("postagem", id_postagem)
        ComentarioRepository.excluir_do_alvo("postagem", id_postagem)
        PostagemRepository.excluir(postagem)
