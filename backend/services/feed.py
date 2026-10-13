from repositories.repository import (
    AtividadeRepository,
    ComentarioRepository,
    CurtidaRepository,
    PostagemRepository,
    UsuarioRepository,
)
from services.comum import ErroValidacao, salvar_imagem
from services.usuario import UsuarioService

TIPOS_ALVO_FEED = {"atividade", "postagem"}


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


class FeedService:

    LIMITE_PADRAO = 30
    LIMITE_MAXIMO = 100

    @staticmethod
    def listar(id_usuario_atual, limite=LIMITE_PADRAO):
        limite = FeedService._limite(limite)

        atividades = AtividadeRepository.listar_publicas(limite)
        postagens = PostagemRepository.listar_publicas(limite)

        itens = []
        for a in atividades:
            itens.append({
                "tipo": "atividade", "id": a.id_atividade, "id_usuario": a.id_usuario,
                "data_registro": a.data_registro, "objeto": a,
            })
        for p in postagens:
            itens.append({
                "tipo": "postagem", "id": p.id_postagem, "id_usuario": p.id_usuario,
                "data_registro": p.data_registro, "objeto": p,
            })

        itens.sort(key=lambda i: i["data_registro"], reverse=True)
        itens = itens[:limite]

        ids_atividade = [i["id"] for i in itens if i["tipo"] == "atividade"]
        ids_postagem = [i["id"] for i in itens if i["tipo"] == "postagem"]

        curtidas_atividade = CurtidaRepository.contar_em_lote("atividade", ids_atividade)
        curtidas_postagem = CurtidaRepository.contar_em_lote("postagem", ids_postagem)
        comentarios_atividade = ComentarioRepository.contar_em_lote("atividade", ids_atividade)
        comentarios_postagem = ComentarioRepository.contar_em_lote("postagem", ids_postagem)

        curti_atividade = set()
        curti_postagem = set()
        if id_usuario_atual:
            curti_atividade = CurtidaRepository.curtidos_pelo_usuario(
                id_usuario_atual, "atividade", ids_atividade
            )
            curti_postagem = CurtidaRepository.curtidos_pelo_usuario(
                id_usuario_atual, "postagem", ids_postagem
            )

        ids_donos = {i["id_usuario"] for i in itens}
        donos = {
            uid: UsuarioRepository.buscar_por_id(uid)
            for uid in ids_donos
        }

        resultado = []
        for i in itens:
            dono = donos.get(i["id_usuario"])
            base = i["objeto"].to_dict()
            base["tipo_conteudo"] = i["tipo"]
            base["usuario"] = {
                "id": dono.id_usuario if dono else None,
                "nome": dono.nome if dono else "Usuário removido",
                "foto": dono.foto if dono else None,
            }
            if i["tipo"] == "atividade":
                base["curtidas"] = curtidas_atividade.get(i["id"], 0)
                base["comentarios"] = comentarios_atividade.get(i["id"], 0)
                base["curti"] = i["id"] in curti_atividade
            else:
                base["curtidas"] = curtidas_postagem.get(i["id"], 0)
                base["comentarios"] = comentarios_postagem.get(i["id"], 0)
                base["curti"] = i["id"] in curti_postagem
            resultado.append(base)

        return resultado

    @staticmethod
    def _limite(valor):
        try:
            numero = int(valor)
        except (TypeError, ValueError):
            return FeedService.LIMITE_PADRAO
        return max(1, min(numero, FeedService.LIMITE_MAXIMO))

    @staticmethod
    def buscar_alvo(tipo_alvo, id_alvo):
        if tipo_alvo not in TIPOS_ALVO_FEED:
            raise ErroValidacao("Tipo de conteúdo inválido.")
        if tipo_alvo == "atividade":
            alvo = AtividadeRepository.buscar_por_id(id_alvo)
        else:
            alvo = PostagemRepository.buscar_por_id(id_alvo)
        if not alvo:
            raise ErroValidacao("Conteúdo não encontrado.", status=404)
        return alvo


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
