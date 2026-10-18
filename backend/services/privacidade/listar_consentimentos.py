from repositories.repository import ConsentimentoRepository
from services.usuario.apoio import buscar_usuario


class ListarConsentimentosService:

    @staticmethod
    def executar(id_usuario):
        buscar_usuario(id_usuario)
        return ConsentimentoRepository.listar_do_usuario(id_usuario)
