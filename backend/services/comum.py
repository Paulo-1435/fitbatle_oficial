import os
import time

EXTENSOES_FOTO = {"png", "jpg", "jpeg", "webp"}


class ErroValidacao(Exception):

    def __init__(self, mensagem, status=400):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status


def validar_extensao_imagem(arquivo):
    ext = arquivo.filename.rsplit(".", 1)[-1].lower() if "." in arquivo.filename else ""
    if ext not in EXTENSOES_FOTO:
        raise ErroValidacao("Formato inválido. Envie uma imagem PNG, JPG ou WEBP.")
    return "jpg" if ext == "jpeg" else ext


def salvar_imagem(arquivo, pasta_destino, prefixo, apagar_existentes=False):
    ext = validar_extensao_imagem(arquivo)
    os.makedirs(pasta_destino, exist_ok=True)

    if apagar_existentes:
        for nome_arquivo in os.listdir(pasta_destino):
            if nome_arquivo.startswith(prefixo + "_") or nome_arquivo.startswith(prefixo + "."):
                try:
                    os.remove(os.path.join(pasta_destino, nome_arquivo))
                except OSError:
                    pass

    nome = f"{prefixo}_{int(time.time())}.{ext}"
    arquivo.save(os.path.join(pasta_destino, nome))
    return "/uploads/" + nome
