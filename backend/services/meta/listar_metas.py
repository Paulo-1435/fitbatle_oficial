from repositories.repository import MetaRepository
from services.meta.apoio import meta_com_progresso


class ListarMetasService:

    @staticmethod
    def executar(id_usuario):
        metas = MetaRepository.listar_do_usuario(id_usuario)
        return [meta_com_progresso(m) for m in metas]
