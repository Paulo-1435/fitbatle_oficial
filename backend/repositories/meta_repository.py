from models.meta import Meta


class MetaRepository:

    @staticmethod
    def listar_do_usuario(id_usuario):
        return (
            Meta.query.filter_by(id_usuario=id_usuario)
            .order_by(Meta.data_inicio.desc())
            .all()
        )
