import os
from flask import current_app, g, jsonify, request

from auth import gerar_token
from services import (
    AlternarCurtidaService,
    AtualizarConsentimentoService,
    AtualizarDesafioService,
    AtualizarFotoPerfilService,
    AtualizarMetaService,
    AtualizarPerfilService,
    AutenticarUsuarioService,
    BuscarPerfisService,
    BuscarUsuarioService,
    BuscarUsuariosParaConvidarService,
    CadastrarUsuarioService,
    ConsultarAtividadeService,
    ConsultarCodigoConviteService,
    ConsultarDashboardService,
    ConsultarDesafioService,
    ConsultarEstatisticasService,
    ConsultarGrupoService,
    ConsultarHistoricoTreinosService,
    ConsultarMetaService,
    ConsultarPerfilService,
    ConsultarRankingGlobalService,
    ConsultarRankingGrupoService,
    ConsultarRankingPorExercicioService,
    ConsultarRankingRegionalService,
    ConsultarResumoRankingUsuarioService,
    ListarMedalhasService,
    ContarNotificacoesNaoLidasService,
    ConvidarParaGrupoService,
    CriarComentarioService,
    CriarDesafioService,
    CriarGrupoService,
    CriarMetaService,
    CriarPostagemService,
    DesistirDesafioService,
    EncerrarDesafioService,
    EntrarGrupoPorCodigoService,
    ErroValidacao,
    ExcluirAtividadeService,
    ExcluirComentarioService,
    ExcluirContaService,
    ExcluirMetaService,
    ExcluirPostagemService,
    ListarComentariosService,
    ListarConsentimentosService,
    ListarConvitesRecebidosService,
    ListarDesafiosAtivosService,
    ListarFeedService,
    ListarMembrosGrupoService,
    ListarMetasService,
    ListarMeusGruposService,
    ListarNotificacoesService,
    MarcarNotificacaoLidaService,
    MarcarTodasNotificacoesLidasService,
    ParticiparDesafioService,
    RegenerarCodigoConviteService,
    RegistrarCompartilhamentoService,
    RegistrarTreinoService,
    ResponderConviteService,
    VerificarAdminService,
)


def _id_logado():
    return g.usuario_atual.id_usuario


def _ip_do_cliente():
    if os.getenv("TRUST_PROXY") == "1":
        encaminhado = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if encaminhado:
            return encaminhado
    return request.remote_addr or ""


def _corpo_json():
    corpo = request.get_json(silent=True)
    if not isinstance(corpo, dict):
        raise ErroValidacao("Corpo da requisição vazio ou JSON inválido.")
    return corpo


class UsuarioController:

    @staticmethod
    def cadastrar():
        try:
            usuario = CadastrarUsuarioService.executar(_corpo_json())
            return jsonify({
                "mensagem": "Cadastro concluído!",
                "usuario": usuario.to_dict(),
            }), 201
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def login():
        try:
            dados = _corpo_json()
            usuario = AutenticarUsuarioService.executar(dados.get("email"), dados.get("senha"), _ip_do_cliente())
            return jsonify({
                "mensagem": "Login efetuado!",
                "token": gerar_token(usuario.id_usuario, usuario.senha),
                "usuario": usuario.to_dict(),
            })
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def eu():
        dados = g.usuario_atual.to_dict()
        dados["admin"] = VerificarAdminService.executar(g.usuario_atual)
        return jsonify({"usuario": dados})

    @staticmethod
    def busca():
        try:
            usuarios = BuscarPerfisService.executar(
                request.args.get("nome"), _id_logado()
            )
            return jsonify([u.to_publico() for u in usuarios])
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def buscar(id_usuario):
        try:
            usuario = ConsultarPerfilService.executar(id_usuario, _id_logado())
            if usuario.id_usuario == _id_logado():
                return jsonify(usuario.to_dict())
            return jsonify(usuario.to_publico())
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def atualizar(id_usuario):
        try:
            dados = _corpo_json()
            usuario = AtualizarPerfilService.executar(id_usuario, dados)
            resposta = {
                "mensagem": "Usuário atualizado.",
                "usuario": usuario.to_dict(),
            }
            if dados.get("senha"):
                resposta["token"] = gerar_token(usuario.id_usuario, usuario.senha)
            return jsonify(resposta)
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def excluir(id_usuario):
        try:
            ExcluirContaService.executar(id_usuario, current_app.config["UPLOAD_FOLDER"])
            return jsonify({"mensagem": "Usuário excluído.", "id": id_usuario})
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def upload_foto(id_usuario):
        try:
            usuario = AtualizarFotoPerfilService.executar(
                id_usuario,
                request.files.get("foto"),
                current_app.config["UPLOAD_FOLDER"],
            )
            return jsonify({"mensagem": "Foto atualizada.", "usuario": usuario.to_dict()})
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def estatisticas():
        return jsonify(ConsultarEstatisticasService.executar())


class AtividadeController:

    @staticmethod
    def registrar(id_usuario):
        try:
            atividade, usuario = RegistrarTreinoService.executar(
                id_usuario, _corpo_json()
            )
            return jsonify({
                "mensagem": "Treino registrado!",
                "pontuacao_ganha": atividade.pontuacao,
                "atividade": atividade.to_dict(),
                "usuario": usuario.to_dict(),
            }), 201
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def historico(id_usuario):
        try:
            atividades = ConsultarHistoricoTreinosService.executar(id_usuario)
            return jsonify([a.to_dict() for a in atividades])
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def buscar(id_atividade):
        try:
            return jsonify(ConsultarAtividadeService.executar(id_atividade, _id_logado()).to_dict())
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def excluir(id_atividade):
        try:
            ExcluirAtividadeService.executar(_id_logado(), id_atividade)
            return jsonify({"mensagem": "Atividade excluída.", "id": id_atividade})
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status


class PostagemController:

    @staticmethod
    def criar():
        try:
            postagem = CriarPostagemService.executar(
                _id_logado(),
                request.form.get("texto"),
                request.files.get("foto"),
                current_app.config["UPLOAD_FOLDER"],
            )
            return jsonify({
                "mensagem": "Postagem publicada!",
                "postagem": postagem.to_dict(),
            }), 201
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def excluir(id_postagem):
        try:
            ExcluirPostagemService.executar(_id_logado(), id_postagem)
            return jsonify({"mensagem": "Postagem excluída.", "id": id_postagem})
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status


class FeedController:

    @staticmethod
    def listar():
        limite = request.args.get("limite", 30)
        return jsonify(ListarFeedService.executar(_id_logado(), limite))


class CurtidaController:

    @staticmethod
    def alternar(tipo_alvo, id_alvo):
        try:
            resultado = AlternarCurtidaService.executar(_id_logado(), tipo_alvo, id_alvo)
            return jsonify(resultado)
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status


class ComentarioController:

    @staticmethod
    def listar(tipo_alvo, id_alvo):
        try:
            comentarios = ListarComentariosService.executar(tipo_alvo, id_alvo, _id_logado())
            return jsonify(comentarios)
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def criar(tipo_alvo, id_alvo):
        try:
            dados = _corpo_json()
            comentario = CriarComentarioService.executar(
                _id_logado(), tipo_alvo, id_alvo, dados.get("texto")
            )
            resultado = comentario.to_dict()
            autor = BuscarUsuarioService.executar(comentario.id_usuario)
            resultado["usuario"] = {
                "id": autor.id_usuario, "nome": autor.nome, "foto": autor.foto,
            }
            return jsonify({"mensagem": "Comentário publicado.", "comentario": resultado}), 201
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def excluir(id_comentario):
        try:
            ExcluirComentarioService.executar(_id_logado(), id_comentario)
            return jsonify({"mensagem": "Comentário excluído.", "id": id_comentario})
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status


class MedalhaController:

    @staticmethod
    def listar(id_usuario):
        try:
            return jsonify(ListarMedalhasService.executar(id_usuario, _id_logado()))
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status


class RankingController:

    @staticmethod
    def ranking_global():
        return jsonify(ConsultarRankingGlobalService.executar(request.args.get("limite", 20)))

    @staticmethod
    def ranking_regional():
        try:
            dados = ConsultarRankingRegionalService.executar(
                request.args.get("cidade"), request.args.get("limite", 20)
            )
            return jsonify(dados)
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def ranking_por_exercicio():
        try:
            dados = ConsultarRankingPorExercicioService.executar(
                request.args.get("titulo"),
                request.args.get("cidade"),
                request.args.get("limite", 20),
            )
            return jsonify(dados)
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def resumo_usuario(id_usuario):
        try:
            return jsonify(ConsultarResumoRankingUsuarioService.executar(id_usuario, _id_logado()))
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status


class ConsentimentoController:

    @staticmethod
    def listar(id_usuario):
        try:
            registros = ListarConsentimentosService.executar(id_usuario)
            return jsonify([c.to_dict() for c in registros])
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def atualizar(id_usuario, chave):
        try:
            dados = _corpo_json()
            registro = AtualizarConsentimentoService.executar(id_usuario, chave, dados.get("aceito"))
            return jsonify({
                "mensagem": "Consentimento atualizado.",
                "consentimento": registro.to_dict(),
            })
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status


class GrupoController:

    @staticmethod
    def criar():
        try:
            grupo = CriarGrupoService.executar(_id_logado(), _corpo_json())
            return jsonify({"mensagem": "Grupo criado!", "grupo": grupo.to_dict()}), 201
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def listar_meus():
        return jsonify(ListarMeusGruposService.executar(_id_logado()))

    @staticmethod
    def detalhe(id_grupo):
        try:
            return jsonify(ConsultarGrupoService.executar(id_grupo, _id_logado()))
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def membros(id_grupo):
        try:
            return jsonify(ListarMembrosGrupoService.executar(id_grupo, _id_logado()))
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def ranking(id_grupo):
        try:
            return jsonify(ConsultarRankingGrupoService.executar(id_grupo, _id_logado(), request.args.get("limite", 20)))
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def convite_info(id_grupo):
        try:
            return jsonify(ConsultarCodigoConviteService.executar(id_grupo, _id_logado()))
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def regenerar_convite(id_grupo):
        try:
            return jsonify(RegenerarCodigoConviteService.executar(id_grupo, _id_logado()))
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def entrar():
        try:
            dados = _corpo_json()
            grupo = EntrarGrupoPorCodigoService.executar(_id_logado(), dados.get("codigo"))
            return jsonify({"mensagem": "Você entrou no grupo!", "grupo": grupo.to_dict()})
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def buscar_para_convidar(id_grupo):
        try:
            resultado = BuscarUsuariosParaConvidarService.executar(
                id_grupo, _id_logado(), request.args.get("nome")
            )
            return jsonify(resultado)
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def convidar(id_grupo):
        try:
            dados = _corpo_json()
            convite = ConvidarParaGrupoService.executar(id_grupo, _id_logado(), dados.get("id_usuario"))
            return jsonify({"mensagem": "Convite enviado!", "id": convite.id_convite}), 201
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status


class ConviteController:

    @staticmethod
    def meus_recebidos():
        return jsonify(ListarConvitesRecebidosService.executar(_id_logado()))

    @staticmethod
    def responder(id_convite):
        try:
            dados = _corpo_json()
            ResponderConviteService.executar(id_convite, _id_logado(), dados.get("aceito"))
            return jsonify({"mensagem": "Convite respondido.", "id": id_convite})
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status


class NotificacaoController:

    @staticmethod
    def listar():
        return jsonify([n.to_dict() for n in ListarNotificacoesService.executar(_id_logado())])

    @staticmethod
    def contagem():
        return jsonify({"nao_lidas": ContarNotificacoesNaoLidasService.executar(_id_logado())})

    @staticmethod
    def marcar_lida(id_notificacao):
        try:
            MarcarNotificacaoLidaService.executar(id_notificacao, _id_logado())
            return jsonify({"mensagem": "Notificação marcada como lida.", "id": id_notificacao})
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def marcar_todas_lidas():
        MarcarTodasNotificacoesLidasService.executar(_id_logado())
        return jsonify({"mensagem": "Todas as notificações foram marcadas como lidas."})


class DashboardController:

    @staticmethod
    def resumo():
        try:
            dados = ConsultarDashboardService.executar(_id_logado(), request.args.get("exercicio"))
            return jsonify(dados)
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status


class CompartilhamentoController:

    @staticmethod
    def registrar():
        try:
            registro = RegistrarCompartilhamentoService.executar(_id_logado(), _corpo_json())
            return jsonify({
                "mensagem": "Compartilhamento registrado.",
                "compartilhamento": registro.to_dict(),
            }), 201
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status


class MetaController:

    @staticmethod
    def criar():
        try:
            meta = CriarMetaService.executar(_id_logado(), _corpo_json())
            return jsonify({"mensagem": "Meta criada!", "meta": meta}), 201
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def listar():
        return jsonify(ListarMetasService.executar(_id_logado()))

    @staticmethod
    def detalhe(id_meta):
        try:
            return jsonify(ConsultarMetaService.executar(id_meta, _id_logado()))
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def atualizar(id_meta):
        try:
            meta = AtualizarMetaService.executar(id_meta, _id_logado(), _corpo_json())
            return jsonify({"mensagem": "Meta atualizada.", "meta": meta})
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def excluir(id_meta):
        try:
            ExcluirMetaService.executar(id_meta, _id_logado())
            return jsonify({"mensagem": "Meta excluída.", "id": id_meta})
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status


class DesafioController:

    @staticmethod
    def criar():
        try:
            desafio = CriarDesafioService.executar(_id_logado(), _corpo_json())
            return jsonify({"mensagem": "Desafio criado!", "desafio": desafio}), 201
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def listar():
        return jsonify(ListarDesafiosAtivosService.executar(_id_logado()))

    @staticmethod
    def detalhe(id_desafio):
        try:
            return jsonify(ConsultarDesafioService.executar(id_desafio, _id_logado()))
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def atualizar(id_desafio):
        try:
            desafio = AtualizarDesafioService.executar(_id_logado(), id_desafio, _corpo_json())
            return jsonify({"mensagem": "Desafio atualizado.", "desafio": desafio})
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def encerrar(id_desafio):
        try:
            desafio = EncerrarDesafioService.executar(_id_logado(), id_desafio)
            return jsonify({"mensagem": "Desafio encerrado.", "desafio": desafio})
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def participar(id_desafio):
        try:
            desafio = ParticiparDesafioService.executar(_id_logado(), id_desafio)
            return jsonify({"mensagem": "Inscrição confirmada!", "desafio": desafio})
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status

    @staticmethod
    def desistir(id_desafio):
        try:
            desafio = DesistirDesafioService.executar(_id_logado(), id_desafio)
            return jsonify({"mensagem": "Você desistiu do desafio.", "desafio": desafio})
        except ErroValidacao as erro:
            return jsonify({"erro": erro.mensagem}), erro.status
