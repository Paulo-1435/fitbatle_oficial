from repositories.repository import AtividadeRepository, MetaRepository
from services.medalha.apoio import calcular_medalhas, metas_com_progresso
from services.usuario.apoio import buscar_usuario_visivel


class ListarMedalhasService:

    @staticmethod
    def executar(id_usuario, id_solicitante):
        usuario = buscar_usuario_visivel(id_usuario, id_solicitante)
        atividades = AtividadeRepository.listar_do_usuario(usuario.id_usuario)
        metas = MetaRepository.listar_do_usuario(usuario.id_usuario)
        medalhas = calcular_medalhas(usuario, atividades, metas_com_progresso(metas))
        if usuario.id_usuario != id_solicitante:
            medalhas = [medalha for medalha in medalhas if medalha["conquistada"]]
        return medalhas
