from database import db
from models.compartilhamento import Compartilhamento


class CompartilhamentoRepository:

    @staticmethod
    def criar(id_usuario, tipo_conteudo, id_atividade, id_meta, rede_social, chave_medalha=None):
        registro = Compartilhamento(
            id_usuario=id_usuario,
            tipo_conteudo=tipo_conteudo,
            id_atividade=id_atividade,
            id_meta=id_meta,
            chave_medalha=chave_medalha,
            rede_social=rede_social,
        )
        db.session.add(registro)
        db.session.commit()
        return registro
