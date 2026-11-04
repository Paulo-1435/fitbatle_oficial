from models.grupo_membro import GrupoMembro
from repositories.repository import GrupoRepository
from services.comum import ErroValidacao, texto_do_cliente


class EntrarGrupoPorCodigoService:

    @staticmethod
    def executar(id_usuario, codigo):
        codigo = texto_do_cliente(codigo, "código").upper()
        if not codigo:
            raise ErroValidacao("Informe o código de convite.")
        grupo = GrupoRepository.buscar_por_codigo(codigo)
        if not grupo:
            raise ErroValidacao("Código de convite inválido.", status=404)
        if GrupoRepository.papel_do_membro(grupo.id_grupo, id_usuario) is not None:
            raise ErroValidacao("Você já participa deste grupo.", status=409)
        GrupoMembro(id_grupo=grupo.id_grupo, id_usuario=id_usuario, papel="membro").salvar()
        return grupo
