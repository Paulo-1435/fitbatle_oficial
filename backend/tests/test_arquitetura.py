import ast
import os
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PENDENTES = [
    "atividade/legado.py",
    "usuario/legado.py",
]

ARQUIVOS_ISENTOS_DA_REGRA_DE_CASO_DE_USO = {"__init__.py", "apoio.py", "limitador_login.py"}


def _nomes_importados(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        arvore = ast.parse(arquivo.read(), filename=caminho)
    nomes = []
    for nodo in ast.walk(arvore):
        if isinstance(nodo, ast.Import):
            nomes.extend(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            nomes.append(nodo.module)
    return nomes


def _arquivos_py(pasta):
    caminho_pasta = os.path.join(RAIZ, pasta)
    arquivos = []
    for raiz, pastas, nomes in os.walk(caminho_pasta):
        pastas[:] = [p for p in pastas if p != "__pycache__"]
        for nome in nomes:
            if nome.endswith(".py"):
                arquivos.append(os.path.join(raiz, nome))
    return sorted(arquivos)


def _comeca_com(nome, prefixos):
    return any(nome == prefixo or nome.startswith(prefixo + ".") for prefixo in prefixos)


def _pastas_de_area(caminho_services):
    return sorted(
        nome
        for nome in os.listdir(caminho_services)
        if nome != "__pycache__" and os.path.isdir(os.path.join(caminho_services, nome))
    )


def _areas_com_pacote(caminho_services):
    return {
        nome
        for nome in _pastas_de_area(caminho_services)
        if os.path.isfile(os.path.join(caminho_services, nome, "__init__.py"))
    }


def _caminho_relativo_a_services(caminho, caminho_services):
    return os.path.relpath(caminho, caminho_services).replace(os.sep, "/")


def _classe_e_metodo_do_caso_de_uso(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        arvore = ast.parse(arquivo.read(), filename=caminho)

    classes = [
        nodo for nodo in arvore.body
        if isinstance(nodo, ast.ClassDef) and not nodo.name.startswith("_")
    ]
    if len(classes) != 1:
        return f"{caminho} deve ter exatamente uma classe pública, tem {len(classes)}"

    classe = classes[0]
    if not classe.name.endswith("Service"):
        return f"{caminho}: classe '{classe.name}' deveria terminar com 'Service'"

    metodos_publicos = [
        nodo for nodo in classe.body
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)) and not nodo.name.startswith("_")
    ]
    if len(metodos_publicos) != 1:
        return (
            f"{caminho}: classe '{classe.name}' deve ter exatamente um método público, "
            f"tem {len(metodos_publicos)}"
        )

    metodo = metodos_publicos[0]
    if metodo.name != "executar":
        return f"{caminho}: método público deveria se chamar 'executar', é '{metodo.name}'"

    decoradores = {d.id for d in metodo.decorator_list if isinstance(d, ast.Name)}
    if "staticmethod" not in decoradores:
        return f"{caminho}: 'executar' deveria ser @staticmethod"

    return None


class TestArquiteturaEmCamadas(unittest.TestCase):

    def test_services_nao_importam_database_models_ou_sqlalchemy(self):
        proibidos = ("database", "models", "sqlalchemy")
        for caminho in _arquivos_py("services"):
            for nome in _nomes_importados(caminho):
                self.assertFalse(
                    _comeca_com(nome, proibidos),
                    f"{caminho} importa '{nome}', proibido para a camada de services",
                )

    def test_controllers_nao_importam_repositories_ou_models(self):
        proibidos = ("repositories", "models")
        for caminho in _arquivos_py("controllers"):
            for nome in _nomes_importados(caminho):
                self.assertFalse(
                    _comeca_com(nome, proibidos),
                    f"{caminho} importa '{nome}', proibido para a camada de controllers",
                )

    def test_repositories_nao_importam_services_ou_controllers(self):
        proibidos = ("services", "controllers")
        for caminho in _arquivos_py("repositories"):
            for nome in _nomes_importados(caminho):
                self.assertFalse(
                    _comeca_com(nome, proibidos),
                    f"{caminho} importa '{nome}', proibido para a camada de repositories",
                )


class TestServicesPorCasoDeUso(unittest.TestCase):

    def test_arquivos_de_caso_de_uso_tem_uma_classe_service_com_um_metodo_executar(self):
        caminho_services = os.path.join(RAIZ, "services")
        pendentes = set(PENDENTES)
        for nome_area in _pastas_de_area(caminho_services):
            caminho_area = os.path.join(caminho_services, nome_area)
            for nome_arquivo in sorted(os.listdir(caminho_area)):
                if not nome_arquivo.endswith(".py"):
                    continue
                if nome_arquivo in ARQUIVOS_ISENTOS_DA_REGRA_DE_CASO_DE_USO:
                    continue
                caminho = os.path.join(caminho_area, nome_arquivo)
                if _caminho_relativo_a_services(caminho, caminho_services) in pendentes:
                    continue
                erro = _classe_e_metodo_do_caso_de_uso(caminho)
                self.assertIsNone(erro, erro)

    def test_verificacao_de_caso_de_uso_reprova_duas_classes_publicas(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "exemplo_invalido.py")
            with open(caminho, "w", encoding="utf-8") as arquivo:
                arquivo.write(
                    "class UmService:\n"
                    "    @staticmethod\n"
                    "    def executar():\n"
                    "        pass\n"
                    "\n"
                    "class DoisService:\n"
                    "    @staticmethod\n"
                    "    def executar():\n"
                    "        pass\n"
                )
            self.assertIsNotNone(_classe_e_metodo_do_caso_de_uso(caminho))

    def test_verificacao_de_caso_de_uso_reprova_dois_metodos_publicos(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "exemplo_invalido.py")
            with open(caminho, "w", encoding="utf-8") as arquivo:
                arquivo.write(
                    "class ExemploService:\n"
                    "    @staticmethod\n"
                    "    def executar():\n"
                    "        pass\n"
                    "\n"
                    "    @staticmethod\n"
                    "    def outro():\n"
                    "        pass\n"
                )
            self.assertIsNotNone(_classe_e_metodo_do_caso_de_uso(caminho))

    def test_services_nao_importam_pacote_de_area_direto(self):
        caminho_services = os.path.join(RAIZ, "services")
        areas = _areas_com_pacote(caminho_services)
        pendentes = set(PENDENTES)
        caminho_init_raiz = os.path.normpath(os.path.join(caminho_services, "__init__.py"))
        for caminho in _arquivos_py("services"):
            if os.path.normpath(caminho) == caminho_init_raiz:
                continue
            if _caminho_relativo_a_services(caminho, caminho_services) in pendentes:
                continue
            for nome in _nomes_importados(caminho):
                partes = nome.split(".")
                if len(partes) == 2 and partes[0] == "services" and partes[1] in areas:
                    self.fail(
                        f"{caminho} importa '{nome}' (pacote de área); "
                        "importe o módulo completo, ex.: services.<area>.apoio"
                    )

    def test_arquivos_pendentes_de_migracao_sao_so_os_declarados(self):
        caminho_services = os.path.join(RAIZ, "services")
        pendentes_raiz = {p for p in PENDENTES if "/" not in p}
        pendentes_aninhados = {p for p in PENDENTES if "/" in p}

        planos = {
            nome
            for nome in os.listdir(caminho_services)
            if nome.endswith(".py")
            and nome not in ("__init__.py", "comum.py")
            and os.path.isfile(os.path.join(caminho_services, nome))
        }
        self.assertEqual(planos, pendentes_raiz)

        for pendente in pendentes_aninhados:
            caminho = os.path.join(caminho_services, *pendente.split("/"))
            self.assertTrue(os.path.isfile(caminho), f"{pendente} não existe mais")
            erro = _classe_e_metodo_do_caso_de_uso(caminho)
            self.assertIsNotNone(
                erro, f"{pendente} já segue a regra de caso de uso, remova de PENDENTES"
            )


if __name__ == "__main__":
    unittest.main()
