from repositories.repository import ConviteRepository, GrupoRepository
from utils import iso_utc


class ListarConvitesRecebidosService:

    @staticmethod
    def executar(id_usuario):
        pendentes = []
        for convite, grupo, remetente in ConviteRepository.listar_pendentes_recebidos(id_usuario):
            pendentes.append({
                "id": convite.id_convite,
                "grupo": {
                    "id": grupo.id_grupo,
                    "nome": grupo.nome,
                    "descricao": grupo.descricao,
                    "membros": GrupoRepository.contar_membros(grupo.id_grupo)["total"],
                },
                "remetente": {"id": remetente.id_usuario, "nome": remetente.nome},
                "data_envio": iso_utc(convite.data_envio),
            })
        return {
            "pendentes": pendentes,
            "meus_grupos": len(GrupoRepository.listar_do_usuario(id_usuario)),
            "convites_enviados_pendentes": ConviteRepository.contar_enviados_pendentes(id_usuario),
        }
