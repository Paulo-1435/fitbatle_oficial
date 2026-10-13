import os
import re
import threading
import time
from datetime import date, datetime

from werkzeug.security import check_password_hash, generate_password_hash

from repositories.repository import PostagemRepository, UsuarioRepository
from services.comum import ErroValidacao, salvar_imagem
from utils import agora, calcular_idade

EMAIL_REGEX = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"

IDADE_MINIMA_CADASTRO = 13
IDADE_MAIORIDADE = 18
IDADE_MAXIMA_PLAUSIVEL = 120


class _LimitadorLogin:

    MAX_TENTATIVAS = 5
    JANELA_SEGUNDOS = 15 * 60
    BLOQUEIO_SEGUNDOS = 15 * 60

    _tentativas = {}
    _lock = threading.Lock()

    @classmethod
    def verificar(cls, chave):
        with cls._lock:
            registro = cls._tentativas.get(chave)
            if not registro:
                return
            bloqueado_ate = registro.get("bloqueado_ate")
            if bloqueado_ate and bloqueado_ate > time.time():
                restante = int(bloqueado_ate - time.time())
                raise ErroValidacao(
                    f"Muitas tentativas de login. Tente novamente em {restante} segundos.",
                    status=429,
                )

    @classmethod
    def registrar_falha(cls, chave):
        with cls._lock:
            agora = time.time()
            registro = cls._tentativas.setdefault(chave, {"falhas": [], "bloqueado_ate": None})
            registro["falhas"] = [t for t in registro["falhas"] if agora - t < cls.JANELA_SEGUNDOS]
            registro["falhas"].append(agora)
            if len(registro["falhas"]) >= cls.MAX_TENTATIVAS:
                registro["bloqueado_ate"] = agora + cls.BLOQUEIO_SEGUNDOS
                registro["falhas"] = []

    @classmethod
    def registrar_sucesso(cls, chave):
        with cls._lock:
            cls._tentativas.pop(chave, None)

    @classmethod
    def resetar(cls):
        with cls._lock:
            cls._tentativas.clear()


def resetar_limitador_login():
    _LimitadorLogin.resetar()


class UsuarioService:

    BUSCA_MINIMO_CARACTERES = 2
    BUSCA_LIMITE = 20

    @staticmethod
    def cadastrar(dados):
        from services.privacidade import ConsentimentoService
        dados = dados or {}
        limpos = UsuarioService._validar(dados, senha_obrigatoria=True)

        if not dados.get("aceite_termos"):
            raise ErroValidacao(
                "É necessário ler e aceitar o Termo de Uso e o Termo de Consentimento."
            )

        nascimento, idade = UsuarioService._validar_data_nascimento(dados.get("data_nascimento"))
        limpos["data_nascimento"] = nascimento
        limpos.update(UsuarioService._validar_faixa_etaria(idade, dados))

        if UsuarioRepository.buscar_por_email(limpos["email"]):
            raise ErroValidacao("E-mail já cadastrado.", status=409)

        consentimentos = dados.get("consentimentos") or {}
        limpos["perfil_publico"] = bool(consentimentos.get("ranking_publico", True))

        limpos["senha"] = generate_password_hash(limpos["senha"])
        usuario = UsuarioRepository.criar(limpos)
        if usuario is None:
            raise ErroValidacao("E-mail já cadastrado.", status=409)
        ConsentimentoService.registrar_iniciais(usuario.id_usuario, consentimentos)
        return usuario

    @staticmethod
    def autenticar(email, senha):
        email = (email or "").strip()
        chave = email.lower()
        _LimitadorLogin.verificar(chave)

        usuario = UsuarioRepository.buscar_por_email(email)
        if not usuario or not check_password_hash(usuario.senha, senha or ""):
            _LimitadorLogin.registrar_falha(chave)
            raise ErroValidacao("E-mail ou senha incorretos.", status=401)

        _LimitadorLogin.registrar_sucesso(chave)
        return usuario

    @staticmethod
    def buscar_por_termo(termo, id_solicitante):
        termo = (termo or "").strip()
        if len(termo) < UsuarioService.BUSCA_MINIMO_CARACTERES:
            raise ErroValidacao(
                f"Digite ao menos {UsuarioService.BUSCA_MINIMO_CARACTERES} letras para buscar."
            )
        return UsuarioRepository.buscar_publicos(
            termo, id_solicitante, UsuarioService.BUSCA_LIMITE
        )

    @staticmethod
    def buscar(id_usuario):
        usuario = UsuarioRepository.buscar_por_id(id_usuario)
        if not usuario:
            raise ErroValidacao("Usuário não encontrado.", status=404)
        return usuario

    @staticmethod
    def buscar_visivel(id_usuario, id_solicitante):
        usuario = UsuarioService.buscar(id_usuario)
        if usuario.id_usuario != id_solicitante and not usuario.perfil_publico:
            raise ErroValidacao("Usuário não encontrado.", status=404)
        return usuario

    @staticmethod
    def atualizar(id_usuario, dados):
        usuario = UsuarioService.buscar(id_usuario)
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
            nascimento, idade = UsuarioService._validar_data_nascimento(dados["data_nascimento"])
            dados["data_nascimento"] = nascimento
            dados.update(UsuarioService._validar_faixa_etaria(idade, dados))

        if dados.get("peso") not in (None, ""):
            dados["peso"] = UsuarioService._validar_numero(dados["peso"], "peso", 20, 400)
        if dados.get("altura") not in (None, ""):
            dados["altura"] = UsuarioService._validar_numero(dados["altura"], "altura", 0.5, 2.7)

        return UsuarioRepository.atualizar(usuario, dados)

    @staticmethod
    def salvar_foto(id_usuario, arquivo, pasta_destino):
        usuario = UsuarioService.buscar(id_usuario)

        if arquivo is None or not arquivo.filename:
            raise ErroValidacao("Nenhuma imagem enviada.")

        usuario.foto = salvar_imagem(
            arquivo, pasta_destino, f"usuario_{id_usuario}", apagar_existentes=True
        )
        return UsuarioRepository.salvar(usuario)

    @staticmethod
    def excluir(id_usuario, pasta_uploads=None):
        usuario = UsuarioService.buscar(id_usuario)

        caminhos_foto = []
        if usuario.foto:
            caminhos_foto.append(usuario.foto)
        for postagem in PostagemRepository.listar_do_usuario(id_usuario):
            if postagem.foto:
                caminhos_foto.append(postagem.foto)

        UsuarioRepository.excluir(usuario)

        if pasta_uploads:
            for caminho in caminhos_foto:
                try:
                    os.remove(os.path.join(pasta_uploads, os.path.basename(caminho)))
                except OSError:
                    pass

    @staticmethod
    def estatisticas():
        usuarios = UsuarioRepository.listar()
        total = len(usuarios)
        media_xp = round(sum(u.xp for u in usuarios) / total, 2) if total else 0
        return {"total_usuarios": total, "media_xp": media_xp}

    @staticmethod
    def _validar(dados, senha_obrigatoria):
        if not dados:
            raise ErroValidacao("Corpo da requisição vazio ou JSON inválido.")

        nome = (dados.get("nome") or "").strip()
        email = (dados.get("email") or "").strip()
        senha = dados.get("senha") or ""

        if len(nome) < 3:
            raise ErroValidacao("O nome deve ter no mínimo 3 caracteres.")
        if not re.match(EMAIL_REGEX, email):
            raise ErroValidacao("Informe um e-mail válido.")
        if senha_obrigatoria and len(senha) < 8:
            raise ErroValidacao("A senha deve ter no mínimo 8 caracteres.")

        return {
            "nome": nome,
            "email": email,
            "senha": senha,
            "cidade": (dados.get("cidade") or None),
            "estado": (dados.get("estado") or None),
            "descricao": (dados.get("descricao") or None),
        }

    @staticmethod
    def _validar_data_nascimento(valor):
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

    @staticmethod
    def _validar_numero(valor, nome, minimo, maximo):
        try:
            numero = float(str(valor).replace(",", "."))
        except (TypeError, ValueError):
            raise ErroValidacao(f"Valor de {nome} inválido.")
        if numero < minimo or numero > maximo:
            raise ErroValidacao(f"Valor de {nome} fora do intervalo permitido.")
        return round(numero, 2)

    @staticmethod
    def _validar_faixa_etaria(idade, dados):
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
