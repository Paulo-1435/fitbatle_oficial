from repositories.repository import ConsentimentoRepository, UsuarioRepository
from services.comum import ErroValidacao
from services.privacidade.apoio import CONSENTIMENTOS_OBRIGATORIOS, CONSENTIMENTOS_OPCIONAIS
from services.usuario.apoio import buscar_usuario
from utils import agora


class AtualizarConsentimentoService:

    @staticmethod
    def executar(id_usuario, chave, aceito):
        buscar_usuario(id_usuario)

        if chave in CONSENTIMENTOS_OBRIGATORIOS:
            raise ErroValidacao(
                "Este consentimento é obrigatório para manter a conta e não pode ser alterado.",
                status=409,
            )
        if chave not in CONSENTIMENTOS_OPCIONAIS:
            raise ErroValidacao("Consentimento não encontrado.", status=404)
        if aceito is None:
            raise ErroValidacao("Informe o campo 'aceito' (true ou false).")

        registro = ConsentimentoRepository.buscar(id_usuario, chave)
        if not registro:
            raise ErroValidacao("Consentimento não encontrado.", status=404)

        registro.aceito = bool(aceito)
        registro.data_atualizacao = agora()
        ConsentimentoRepository.salvar(registro)

        if chave == "ranking_publico":
            usuario = UsuarioRepository.buscar_por_id(id_usuario)
            usuario.perfil_publico = registro.aceito
            UsuarioRepository.salvar(usuario)

        return registro
