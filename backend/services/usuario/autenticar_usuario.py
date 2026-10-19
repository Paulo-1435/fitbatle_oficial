from werkzeug.security import check_password_hash

from repositories.repository import UsuarioRepository
from services.comum import ErroValidacao
from services.usuario.limitador_login import _LimitadorLogin


class AutenticarUsuarioService:

    @staticmethod
    def executar(email, senha):
        email = (email or "").strip()
        chave = email.lower()
        _LimitadorLogin.verificar(chave)

        usuario = UsuarioRepository.buscar_por_email(email)
        if not usuario or not check_password_hash(usuario.senha, senha or ""):
            _LimitadorLogin.registrar_falha(chave)
            raise ErroValidacao("E-mail ou senha incorretos.", status=401)

        _LimitadorLogin.registrar_sucesso(chave)
        return usuario
