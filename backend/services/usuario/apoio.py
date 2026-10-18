import os

from repositories.repository import UsuarioRepository
from services.comum import ErroValidacao
from utils import calcular_idade

IDADE_MAIORIDADE = 18


def buscar_usuario(id_usuario):
    usuario = UsuarioRepository.buscar_por_id(id_usuario)
    if not usuario:
        raise ErroValidacao("Usuário não encontrado.", status=404)
    return usuario


def e_maior_de_idade(usuario):
    idade = calcular_idade(usuario.data_nascimento, usuario.idade)
    return idade is None or idade >= IDADE_MAIORIDADE


def buscar_usuario_visivel(id_usuario, id_solicitante):
    usuario = buscar_usuario(id_usuario)
    if usuario.id_usuario != id_solicitante:
        if not usuario.perfil_publico or not e_maior_de_idade(usuario):
            raise ErroValidacao("Usuário não encontrado.", status=404)
    return usuario


def usuario_eh_admin(usuario):
    admins = {
        email.strip().lower()
        for email in os.environ.get("ADMIN_EMAILS", "").split(",")
        if email.strip()
    }
    return usuario.email.lower() in admins


def exigir_admin(id_usuario):
    usuario = buscar_usuario(id_usuario)
    if not usuario_eh_admin(usuario):
        raise ErroValidacao("Apenas a administração pode fazer isso.", status=403)
    return usuario
