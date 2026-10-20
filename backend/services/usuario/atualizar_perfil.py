import re

from werkzeug.security import generate_password_hash

from repositories.repository import UsuarioRepository
from services.comum import ErroValidacao, numero_decimal
from services.usuario.apoio import (
    EMAIL_REGEX,
    buscar_usuario,
    validar_data_nascimento,
    validar_faixa_etaria,
)


def _validar_numero(valor, nome, minimo, maximo):
    numero = numero_decimal(valor, nome, maximo)
    if numero < minimo:
        raise ErroValidacao(f"Valor de {nome} fora do intervalo permitido.")
    return round(numero, 2)


class AtualizarPerfilService:

    @staticmethod
    def executar(id_usuario, dados):
        usuario = buscar_usuario(id_usuario)
        dados = dict(dados or {})

        if dados.get("nome") is not None and len(dados["nome"].strip()) < 3:
            raise ErroValidacao("O nome deve ter no mínimo 3 caracteres.")

        if dados.get("email"):
            email = dados["email"].strip()
            if not re.match(EMAIL_REGEX, email):
                raise ErroValidacao("Informe um e-mail válido.")
            existente = UsuarioRepository.buscar_por_email(email)
            if existente and existente.id_usuario != usuario.id_usuario:
                raise ErroValidacao("E-mail já cadastrado.", status=409)
            dados["email"] = email

        if dados.get("senha"):
            if len(dados["senha"]) < 8:
                raise ErroValidacao("A senha deve ter no mínimo 8 caracteres.")
            dados["senha"] = generate_password_hash(dados["senha"])

        if dados.get("data_nascimento"):
            nascimento, idade = validar_data_nascimento(dados["data_nascimento"])
            dados["data_nascimento"] = nascimento
            dados.update(validar_faixa_etaria(idade, dados))

        if dados.get("peso") not in (None, ""):
            dados["peso"] = _validar_numero(dados["peso"], "peso", 20, 400)
        if dados.get("altura") not in (None, ""):
            dados["altura"] = _validar_numero(dados["altura"], "altura", 0.5, 2.7)

        return UsuarioRepository.atualizar(usuario, dados)
