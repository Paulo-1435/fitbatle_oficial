from repositories.repository import GrupoRepository
from services.grupo.apoio import exigir_admin_grupo, gerar_codigo_convite


class RegenerarCodigoConviteService:

    @staticmethod
    def executar(id_grupo, id_usuario):
        grupo = exigir_admin_grupo(id_grupo, id_usuario)
        grupo.codigo_convite = gerar_codigo_convite()
        GrupoRepository.salvar(grupo)
        return {"codigo": grupo.codigo_convite}
