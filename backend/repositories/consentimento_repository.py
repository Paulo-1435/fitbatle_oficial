from models.consentimento import Consentimento


class ConsentimentoRepository:

    @staticmethod
    def listar_do_usuario(id_usuario):
        return (
            Consentimento.query.filter_by(id_usuario=id_usuario)
            .order_by(Consentimento.obrigatorio.desc(), Consentimento.id_consentimento)
            .all()
        )

    @staticmethod
    def buscar(id_usuario, chave):
        return Consentimento.query.filter_by(id_usuario=id_usuario, chave=chave).first()
