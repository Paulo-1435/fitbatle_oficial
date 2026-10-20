import os
import re
from datetime import date, datetime

from repositories.repository import UsuarioRepository
from services.comum import ErroValidacao
from utils import IDADE_MAIORIDADE, agora, calcular_idade

EMAIL_REGEX = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
IDADE_MINIMA_CADASTRO = 13
IDADE_MAXIMA_PLAUSIVEL = 120


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


def validar_data_nascimento(valor):
    if not valor:
        raise ErroValidacao("Informe a data de nascimento.")
    try:
        nascimento = datetime.strptime(valor, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        raise ErroValidacao("Data de nascimento inválida. Use o formato AAAA-MM-DD.")

    hoje = date.today()
    if nascimento > hoje:
        raise ErroValidacao("A data de nascimento não pode ser no futuro.")

    idade = calcular_idade(nascimento, hoje=hoje)
    if idade > IDADE_MAXIMA_PLAUSIVEL:
        raise ErroValidacao("Data de nascimento inválida.")
    return nascimento, idade


def validar_faixa_etaria(idade, dados):
    if idade is None:
        raise ErroValidacao("Informe a idade.")

    if idade < IDADE_MINIMA_CADASTRO:
        raise ErroValidacao(
            "Não é permitido ter menos de 13 anos na plataforma (art. 14 da LGPD)."
        )

    if idade >= IDADE_MAIORIDADE:
        return {}

    responsavel = dados.get("responsavel") or {}
    nome = (responsavel.get("nome") or "").strip()
    email = (responsavel.get("email") or "").strip()

    if not dados.get("autorizacao_responsavel"):
        raise ErroValidacao(
            "Para menores de 18 anos é necessária a autorização do responsável legal."
        )
    if len(nome) < 3:
        raise ErroValidacao("Informe o nome completo do responsável legal.")
    if not re.match(EMAIL_REGEX, email):
        raise ErroValidacao("Informe um e-mail válido do responsável legal.")

    return {
        "responsavel_nome": nome,
        "responsavel_email": email,
        "responsavel_autorizado_em": agora(),
    }
