from werkzeug.security import check_password_hash

from repositories.repository import UsuarioRepository
from services.comum import ErroValidacao, senha_do_cliente, texto_do_cliente
from services.usuario.limitador_login import _LimitadorLogin


class AutenticarUsuarioService:

    @staticmethod
    def executar(email, senha):
        email = texto_do_cliente(email, "e-mail")
        senha = senha_do_cliente(senha) if senha is not None else ""
        chave = email.lower()
        _LimitadorLogin.verificar(chave)

        usuario = UsuarioRepository.buscar_por_email(email)
        if not usuario or not check_password_hash(usuario.senha, senha):
            _LimitadorLogin.registrar_falha(chave)
            raise ErroValidacao("E-mail ou senha incorretos.", status=401)

        _LimitadorLogin.registrar_sucesso(chave)
        return usuario
