from services.comum import ErroValidacao
from services.usuario import UsuarioService, resetar_limitador_login
from services.privacidade import ConsentimentoService
from services.atividade import AtividadeService
from services.postagem import CriarPostagemService, ExcluirPostagemService
from services.feed import ListarFeedService
from services.curtida import AlternarCurtidaService
from services.comentario import (
    CriarComentarioService,
    ExcluirComentarioService,
    ListarComentariosService,
)
from services.ranking import (
    ConsultarRankingGlobalService,
    ConsultarRankingPorExercicioService,
    ConsultarRankingRegionalService,
    ConsultarResumoRankingUsuarioService,
)
from services.grupo import GrupoService
from services.convite import ConviteService
from services.meta import MetaService
from services.compartilhamento import RegistrarCompartilhamentoService
from services.dashboard import ConsultarDashboardService
from services.notificacao import (
    ContarNotificacoesNaoLidasService,
    ListarNotificacoesService,
    MarcarNotificacaoLidaService,
    MarcarTodasNotificacoesLidasService,
)
from services.desafio import DesafioService
