from repositories.repository import ConviteRepository, GrupoRepository
from services.comum import ErroValidacao
from services.notificacao.apoio import gerar_notificacao
from services.usuario.apoio import buscar_usuario
from utils import agora


class ResponderConviteService:

    @staticmethod
    def executar(id_convite, id_usuario, aceito):
        convite = ConviteRepository.buscar_por_id(id_convite)
        if not convite:
            raise ErroValidacao("Convite não encontrado.", status=404)
        if convite.id_destinatario != id_usuario:
            raise ErroValidacao("Você não tem permissão para responder este convite.", status=403)
        if convite.status != "pendente":
            raise ErroValidacao("Este convite já foi respondido.", status=409)
        if aceito is None:
            raise ErroValidacao("Informe o campo 'aceito' (true ou false).")

        convite.status = "aceito" if aceito else "recusado"
        convite.data_resposta = agora()
        ConviteRepository.salvar(convite)

        if aceito and GrupoRepository.papel_do_membro(convite.id_grupo, id_usuario) is None:
            GrupoRepository.adicionar_membro(convite.id_grupo, id_usuario, "membro")

        if aceito:
            destinatario = buscar_usuario(id_usuario)
            gerar_notificacao(
                convite.id_remetente,
                "convite_aceito",
                f"{destinatario.nome} aceitou seu convite para o grupo.",
                tipo_alvo="convite",
                id_alvo=convite.id_convite,
            )

        return convite
