from repositories.repository import UsuarioRepository
from services.atividade.apoio import buscar_atividade
from services.comum import ErroValidacao
from services.usuario.apoio import e_maior_de_idade


class ConsultarAtividadeService:

    @staticmethod
    def executar(id_atividade, id_solicitante):
        atividade = buscar_atividade(id_atividade)
        if atividade.id_usuario != id_solicitante:
            dono = UsuarioRepository.buscar_por_id(atividade.id_usuario)
            if dono is None or not dono.perfil_publico or not e_maior_de_idade(dono):
                raise ErroValidacao("Atividade não encontrada.", status=404)
        return atividade
