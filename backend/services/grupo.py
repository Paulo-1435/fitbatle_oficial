import secrets
import string

from repositories.repository import ConviteRepository, GrupoRepository, RankingRepository
from services.comum import ErroValidacao
from services.usuario import UsuarioService
from utils import agora, iso_utc

CODIGO_CONVITE_ALFABETO = string.ascii_uppercase + string.digits


def _gerar_codigo_convite():
    for _ in range(10):
        codigo = "".join(secrets.choice(CODIGO_CONVITE_ALFABETO) for _ in range(10))
        if not GrupoRepository.buscar_por_codigo(codigo):
            return codigo
    raise ErroValidacao("Não foi possível gerar um código de convite. Tente novamente.", status=500)


def _handles(usuarios):
    raizes = {}
    contagem = {}
    for usuario in usuarios:
        raiz = (usuario.email.split("@")[0] or "atleta").lower()
        raizes[usuario.id_usuario] = raiz
        contagem[raiz] = contagem.get(raiz, 0) + 1

    handles = {}
    for usuario in usuarios:
        raiz = raizes[usuario.id_usuario]
        if contagem[raiz] > 1:
            handles[usuario.id_usuario] = f"{raiz}{usuario.id_usuario % 100:02d}"
        else:
            handles[usuario.id_usuario] = raiz
    return handles


class GrupoService:

    NOME_MAX = 50
    DESCRICAO_MAX = 300

    @staticmethod
    def criar(id_usuario, dados):
        dados = dados or {}
        nome = (dados.get("nome") or "").strip()
        descricao = (dados.get("descricao") or "").strip() or None

        if not nome:
            raise ErroValidacao("Informe o nome do grupo.")
        if len(nome) > GrupoService.NOME_MAX:
            raise ErroValidacao(f"O nome do grupo pode ter no máximo {GrupoService.NOME_MAX} caracteres.")
        if descricao and len(descricao) > GrupoService.DESCRICAO_MAX:
            raise ErroValidacao(f"A descrição pode ter no máximo {GrupoService.DESCRICAO_MAX} caracteres.")

        codigo = _gerar_codigo_convite()
        grupo = GrupoRepository.criar(nome, descricao, id_usuario, codigo)
        GrupoRepository.adicionar_membro(grupo.id_grupo, id_usuario, "admin")
        return grupo

    @staticmethod
    def buscar(id_grupo):
        grupo = GrupoRepository.buscar_por_id(id_grupo)
        if not grupo:
            raise ErroValidacao("Grupo não encontrado.", status=404)
        return grupo

    @staticmethod
    def _exigir_membro(id_grupo, id_usuario):
        grupo = GrupoService.buscar(id_grupo)
        papel = GrupoRepository.papel_do_membro(id_grupo, id_usuario)
        if papel is None:
            raise ErroValidacao("Você não participa deste grupo.", status=403)
        return grupo, papel

    @staticmethod
    def _exigir_admin(id_grupo, id_usuario):
        grupo, papel = GrupoService._exigir_membro(id_grupo, id_usuario)
        if papel != "admin":
            raise ErroValidacao("Apenas administradores do grupo podem fazer isso.", status=403)
        return grupo

    @staticmethod
    def listar_meus(id_usuario):
        resultado = []
        for grupo, papel in GrupoRepository.listar_do_usuario(id_usuario):
            dado = grupo.to_dict()
            dado["meu_papel"] = papel
            dado["membros"] = GrupoRepository.contar_membros(grupo.id_grupo)
            resultado.append(dado)
        return resultado

    @staticmethod
    def detalhe(id_grupo, id_usuario):
        grupo, papel = GrupoService._exigir_membro(id_grupo, id_usuario)
        dado = grupo.to_dict()
        dado["meu_papel"] = papel
        dado["membros"] = GrupoRepository.contar_membros(id_grupo)
        return dado

    @staticmethod
    def membros(id_grupo, id_usuario):
        GrupoService._exigir_membro(id_grupo, id_usuario)
        pares = GrupoRepository.listar_membros(id_grupo)
        handles = _handles([usuario for usuario, _ in pares])
        return [
            {
                "id": usuario.id_usuario,
                "nome": usuario.nome,
                "handle": handles[usuario.id_usuario],
                "cidade": usuario.cidade,
                "estado": usuario.estado,
                "foto": usuario.foto,
                "papel": papel,
            }
            for usuario, papel in pares
        ]

    @staticmethod
    def ranking(id_grupo, id_usuario, limite=20):
        GrupoService._exigir_membro(id_grupo, id_usuario)
        return RankingRepository.grupo(id_grupo, limite)

    @staticmethod
    def convite_info(id_grupo, id_usuario):
        grupo = GrupoService._exigir_admin(id_grupo, id_usuario)
        return {"codigo": grupo.codigo_convite}

    @staticmethod
    def regenerar_codigo(id_grupo, id_usuario):
        grupo = GrupoService._exigir_admin(id_grupo, id_usuario)
        grupo.codigo_convite = _gerar_codigo_convite()
        GrupoRepository.salvar(grupo)
        return {"codigo": grupo.codigo_convite}

    @staticmethod
    def entrar_por_codigo(id_usuario, codigo):
        codigo = (codigo or "").strip().upper()
        if not codigo:
            raise ErroValidacao("Informe o código de convite.")
        grupo = GrupoRepository.buscar_por_codigo(codigo)
        if not grupo:
            raise ErroValidacao("Código de convite inválido.", status=404)
        if GrupoRepository.papel_do_membro(grupo.id_grupo, id_usuario) is not None:
            raise ErroValidacao("Você já participa deste grupo.", status=409)
        GrupoRepository.adicionar_membro(grupo.id_grupo, id_usuario, "membro")
        return grupo

    @staticmethod
    def buscar_para_convidar(id_grupo, id_usuario, termo):
        GrupoService._exigir_membro(id_grupo, id_usuario)
        encontrados = UsuarioService.buscar_por_termo(termo, id_usuario)
        ids_membros = GrupoRepository.ids_membros(id_grupo)
        candidatos = [u for u in encontrados if u.id_usuario not in ids_membros]
        handles = _handles(candidatos)

        resultado = []
        for usuario in candidatos:
            resultado.append({
                "id": usuario.id_usuario,
                "nome": usuario.nome,
                "handle": handles[usuario.id_usuario],
                "cidade": usuario.cidade,
                "estado": usuario.estado,
                "foto": usuario.foto,
                "convite_pendente": ConviteRepository.buscar_pendente(id_grupo, usuario.id_usuario) is not None,
            })
        return resultado

    @staticmethod
    def convidar(id_grupo, id_remetente, id_destinatario):
        GrupoService._exigir_membro(id_grupo, id_remetente)
        destinatario = UsuarioService.buscar(id_destinatario)
        if GrupoRepository.papel_do_membro(id_grupo, destinatario.id_usuario) is not None:
            raise ErroValidacao("Esse usuário já é membro do grupo.", status=409)
        convite = ConviteRepository.criar(id_grupo, id_remetente, destinatario.id_usuario)
        if convite is None:
            raise ErroValidacao("Já existe um convite pendente para esse usuário.", status=409)
        return convite


class ConviteService:

    @staticmethod
    def meus_recebidos(id_usuario):
        pendentes = []
        for convite, grupo, remetente in ConviteRepository.listar_pendentes_recebidos(id_usuario):
            pendentes.append({
                "id": convite.id_convite,
                "grupo": {
                    "id": grupo.id_grupo,
                    "nome": grupo.nome,
                    "descricao": grupo.descricao,
                    "membros": GrupoRepository.contar_membros(grupo.id_grupo),
                },
                "remetente": {"id": remetente.id_usuario, "nome": remetente.nome},
                "data_envio": iso_utc(convite.data_envio),
            })
        return {
            "pendentes": pendentes,
            "meus_grupos": len(GrupoRepository.listar_do_usuario(id_usuario)),
            "convites_enviados_pendentes": ConviteRepository.contar_enviados_pendentes(id_usuario),
        }

    @staticmethod
    def responder(id_convite, id_usuario, aceito):
        convite = ConviteRepository.buscar_por_id(id_convite)
        if not convite:
            raise ErroValidacao("Convite não encontrado.", status=404)
        if convite.id_destinatario != id_usuario:
            raise ErroValidacao("Você não tem permissão para responder este convite.", status=403)
        if convite.status != "pendente":
            raise ErroValidacao("Este convite já foi respondido.", status=409)
        if aceito is None:
            raise ErroValidacao("Informe o campo 'aceito' (true ou false).")

        convite.status = "aceito" if aceito else "recusado"
        convite.data_resposta = agora()
        ConviteRepository.salvar(convite)

        if aceito and GrupoRepository.papel_do_membro(convite.id_grupo, id_usuario) is None:
            GrupoRepository.adicionar_membro(convite.id_grupo, id_usuario, "membro")

        return convite
