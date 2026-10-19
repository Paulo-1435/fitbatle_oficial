from services.comum import ErroValidacao
from services.usuario import BuscarPerfisService, UsuarioService, resetar_limitador_login
from services.privacidade import AtualizarConsentimentoService, ListarConsentimentosService
from services.atividade import (
    ConsultarAtividadeService,
    ConsultarHistoricoTreinosService,
    ExcluirAtividadeService,
    RegistrarTreinoService,
)
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
from services.grupo import (
    BuscarUsuariosParaConvidarService,
    ConsultarCodigoConviteService,
    ConsultarGrupoService,
    ConsultarRankingGrupoService,
    ConvidarParaGrupoService,
    CriarGrupoService,
    EntrarGrupoPorCodigoService,
    ListarMembrosGrupoService,
    ListarMeusGruposService,
    RegenerarCodigoConviteService,
)
from services.convite import ListarConvitesRecebidosService, ResponderConviteService
from services.meta import (
    AtualizarMetaService,
    ConsultarMetaService,
    CriarMetaService,
    ExcluirMetaService,
    ListarMetasService,
)
from services.compartilhamento import RegistrarCompartilhamentoService
from services.dashboard import ConsultarDashboardService
from services.notificacao import (
    ContarNotificacoesNaoLidasService,
    ListarNotificacoesService,
    MarcarNotificacaoLidaService,
    MarcarTodasNotificacoesLidasService,
)
from services.desafio import (
    AtualizarDesafioService,
    AvaliarDesafiosDoUsuarioService,
    ConsultarDesafioService,
    CriarDesafioService,
    DesistirDesafioService,
    EncerrarDesafioService,
    ListarDesafiosAtivosService,
    ParticiparDesafioService,
)
