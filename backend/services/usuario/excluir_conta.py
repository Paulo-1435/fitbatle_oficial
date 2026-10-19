import os

from repositories.repository import PostagemRepository, UsuarioRepository
from services.usuario.apoio import buscar_usuario


class ExcluirContaService:

    @staticmethod
    def executar(id_usuario, pasta_uploads=None):
        usuario = buscar_usuario(id_usuario)

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
