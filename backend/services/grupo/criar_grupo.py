from repositories.repository import GrupoRepository
from services.comum import ErroValidacao
from services.grupo.apoio import gerar_codigo_convite


class CriarGrupoService:

    NOME_MAX = 50
    DESCRICAO_MAX = 300

    @staticmethod
    def executar(id_usuario, dados):
        dados = dados or {}
        nome = (dados.get("nome") or "").strip()
        descricao = (dados.get("descricao") or "").strip() or None

        if not nome:
            raise ErroValidacao("Informe o nome do grupo.")
        if len(nome) > CriarGrupoService.NOME_MAX:
            raise ErroValidacao(f"O nome do grupo pode ter no máximo {CriarGrupoService.NOME_MAX} caracteres.")
        if descricao and len(descricao) > CriarGrupoService.DESCRICAO_MAX:
            raise ErroValidacao(f"A descrição pode ter no máximo {CriarGrupoService.DESCRICAO_MAX} caracteres.")

        codigo = gerar_codigo_convite()
        grupo = GrupoRepository.criar(nome, descricao, id_usuario, codigo)
        GrupoRepository.adicionar_membro(grupo.id_grupo, id_usuario, "admin")
        return grupo
