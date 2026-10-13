from repositories.repository import ConsentimentoRepository, UsuarioRepository
from services.comum import ErroValidacao
from services.usuario import UsuarioService
from utils import agora

CONSENTIMENTOS_OBRIGATORIOS = {
    "conta_autenticacao": "Criar, autenticar e manter a minha conta",
    "registro_atividades": "Registrar e armazenar meus treinos",
    "historico_estatisticas": "Manter meu histórico e minhas estatísticas individuais",
    "dados_saude": "Tratar dados de treino que possam revelar condição de saúde (art. 11 da LGPD)",
    "seguranca_auditoria": "Guardar registros técnicos de segurança e auditoria",
}
CONSENTIMENTOS_OPCIONAIS = {
    "ranking_publico": "Exibir meu perfil e desempenho nos rankings regional e global",
    "localizacao": "Usar minha cidade/região para o ranking regional",
    "chat_publico": "Participar dos chats públicos da plataforma",
    "chat_privado_externo": "Receber mensagens privadas de usuários fora dos meus grupos",
    "busca_perfil": "Permitir que outros usuários me encontrem pela busca",
    "notificacoes": "Receber notificações por push ou e-mail",
    "compartilhamento": "Compartilhar conquistas e recordes em redes sociais externas",
}


class ConsentimentoService:

    @staticmethod
    def registrar_iniciais(id_usuario, escolhas):
        escolhas = escolhas or {}
        registros = []

        for chave, descricao in CONSENTIMENTOS_OBRIGATORIOS.items():
            registros.append({
                "chave": chave, "descricao": descricao,
                "obrigatorio": True, "aceito": True,
            })

        for chave, descricao in CONSENTIMENTOS_OPCIONAIS.items():
            registros.append({
                "chave": chave, "descricao": descricao,
                "obrigatorio": False,
                "aceito": bool(escolhas.get(chave, True)),
            })

        return ConsentimentoRepository.criar_varios(id_usuario, registros)

    @staticmethod
    def listar(id_usuario):
        UsuarioService.buscar(id_usuario)
        return ConsentimentoRepository.listar_do_usuario(id_usuario)

    @staticmethod
    def atualizar(id_usuario, chave, aceito):
        UsuarioService.buscar(id_usuario)

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
