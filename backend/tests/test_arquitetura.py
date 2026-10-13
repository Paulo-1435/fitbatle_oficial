import ast
import os
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
    return [
        os.path.join(caminho_pasta, nome)
        for nome in os.listdir(caminho_pasta)
        if nome.endswith(".py")
    ]


def _comeca_com(nome, prefixos):
    return any(nome == prefixo or nome.startswith(prefixo + ".") for prefixo in prefixos)


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


if __name__ == "__main__":
    unittest.main()
