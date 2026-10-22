import os
import re
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PASTA_FRONTEND = os.path.join(RAIZ, "frontend")
PASTA_MOCKUPS = os.path.join(PASTA_FRONTEND, "mockups")
ARQUIVO_ICONES = os.path.join(PASTA_FRONTEND, "icones.js")


def _arquivos_do_frontend():
    for raiz, pastas, nomes in os.walk(PASTA_FRONTEND):
        if raiz.startswith(PASTA_MOCKUPS):
            pastas[:] = []
            continue
        for nome in nomes:
            if nome.endswith((".js", ".html")):
                yield os.path.join(raiz, nome)


def _texto(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return arquivo.read()


def _nomes_usados_nas_telas():
    usados = set()
    for caminho in _arquivos_do_frontend():
        conteudo = _texto(caminho)
        usados.update(re.findall(r"criarIcone\(\s*['\"](\w+)['\"]", conteudo))
        usados.update(re.findall(r"montarComIcone\(\s*['\"](\w+)['\"]", conteudo))
        usados.update(re.findall(r"data-icone=\"(\w+)\"", conteudo))
    return usados


class TestIcones(unittest.TestCase):

    def test_todo_nome_usado_existe_no_conjunto(self):
        codigo = _texto(ARQUIVO_ICONES)
        existentes = set(re.findall(r"^  (\w+): \[", codigo, re.M))
        mapa = re.search(r"const ICONE_POR_TIPO = \{(.*?)\};", codigo, re.S).group(1)
        usados = _nomes_usados_nas_telas() | set(re.findall(r"'(\w+)'", mapa))
        faltando = sorted(usados - existentes)
        self.assertEqual(faltando, [], f"Ícones usados sem definição em icones.js: {faltando}")

    def test_criacao_de_icones_nao_usa_innerhtml(self):
        self.assertNotIn("innerHTML", _texto(ARQUIVO_ICONES))


if __name__ == "__main__":
    unittest.main()
