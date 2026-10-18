from repositories.repository import ConviteRepository, GrupoRepository
from services.comum import ErroValidacao
from services.grupo.apoio import buscar_grupo, exigir_membro
from services.notificacao.apoio import gerar_notificacao
from services.usuario.apoio import buscar_usuario


class ConvidarParaGrupoService:

    @staticmethod
    def executar(id_grupo, id_remetente, id_destinatario):
        exigir_membro(id_grupo, id_remetente)
        destinatario = buscar_usuario(id_destinatario)
        if GrupoRepository.papel_do_membro(id_grupo, destinatario.id_usuario) is not None:
            raise ErroValidacao("Esse usuário já é membro do grupo.", status=409)
        convite = ConviteRepository.criar(id_grupo, id_remetente, destinatario.id_usuario)
        if convite is None:
            raise ErroValidacao("Já existe um convite pendente para esse usuário.", status=409)

        grupo = buscar_grupo(id_grupo)
        gerar_notificacao(
            destinatario.id_usuario,
            "convite_recebido",
            f"Você recebeu um convite para o grupo {grupo.nome}.",
            tipo_alvo="convite",
            id_alvo=convite.id_convite,
        )
        return convite
