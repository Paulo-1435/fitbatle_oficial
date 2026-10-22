from repositories.repository import GrupoRepository


class ListarMeusGruposService:

    @staticmethod
    def executar(id_usuario):
        resultado = []
        for grupo, papel in GrupoRepository.listar_do_usuario(id_usuario):
            dado = grupo.to_dict()
            dado["meu_papel"] = papel
            dado["membros"] = GrupoRepository.contar_membros(grupo.id_grupo)
            resultado.append(dado)
        return resultado
