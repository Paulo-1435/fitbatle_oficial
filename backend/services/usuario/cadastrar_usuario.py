import re

from werkzeug.security import generate_password_hash

from repositories.repository import UsuarioRepository
from services.comum import ErroValidacao
from services.privacidade.apoio import registrar_consentimentos_iniciais
from services.usuario.apoio import EMAIL_REGEX, validar_data_nascimento, validar_faixa_etaria


def _validar(dados):
    nome = (dados.get("nome") or "").strip()
    email = (dados.get("email") or "").strip()
    senha = dados.get("senha") or ""

    if len(nome) < 3:
        raise ErroValidacao("O nome deve ter no mínimo 3 caracteres.")
    if not re.match(EMAIL_REGEX, email):
        raise ErroValidacao("Informe um e-mail válido.")
    if len(senha) < 8:
        raise ErroValidacao("A senha deve ter no mínimo 8 caracteres.")

    return {
        "nome": nome,
        "email": email,
        "senha": senha,
        "cidade": (dados.get("cidade") or None),
        "estado": (dados.get("estado") or None),
        "descricao": (dados.get("descricao") or None),
    }


class CadastrarUsuarioService:

    @staticmethod
    def executar(dados):
        dados = dados or {}
        if not dados:
            raise ErroValidacao("Corpo da requisição vazio ou JSON inválido.")
        limpos = _validar(dados)

        if not dados.get("aceite_termos"):
            raise ErroValidacao(
                "É necessário ler e aceitar o Termo de Uso e o Termo de Consentimento."
            )

        nascimento, idade = validar_data_nascimento(dados.get("data_nascimento"))
        limpos["data_nascimento"] = nascimento
        limpos.update(validar_faixa_etaria(idade, dados))

        if UsuarioRepository.buscar_por_email(limpos["email"]):
            raise ErroValidacao("E-mail já cadastrado.", status=409)

        consentimentos = dados.get("consentimentos") or {}
        limpos["perfil_publico"] = bool(consentimentos.get("ranking_publico", True))

        limpos["senha"] = generate_password_hash(limpos["senha"])
        usuario = UsuarioRepository.criar(limpos)
        if usuario is None:
            raise ErroValidacao("E-mail já cadastrado.", status=409)
        registrar_consentimentos_iniciais(usuario.id_usuario, consentimentos)
        return usuario
