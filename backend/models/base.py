from database import db


class ModeloBase(db.Model):
    __abstract__ = True

    def salvar(self):
        return self._confirmar(lambda: db.session.add(self))

    def atualizar(self, campos):
        chaves = {coluna.key for coluna in self.__mapper__.primary_key}
        atributos = {coluna.key for coluna in self.__mapper__.column_attrs} - chaves
        for nome, valor in campos.items():
            if nome in atributos:
                setattr(self, nome, valor)
        return self.salvar()

    def deletar(self):
        return self._confirmar(lambda: db.session.delete(self))

    @classmethod
    def listar_todos(cls):
        return db.session.execute(db.select(cls)).scalars().all()

    @classmethod
    def buscar_por_id(cls, chave):
        return db.session.get(cls, chave)

    def _confirmar(self, operacao):
        try:
            operacao()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return self
