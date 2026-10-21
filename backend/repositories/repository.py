from datetime import date

from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError

from database import db
from models.model import (
    Atividade,
    Comentario,
    Compartilhamento,
    Consentimento,
    Convite,
    Curtida,
    Desafio,
    DesafioUsuario,
    Grupo,
    GrupoMembro,
    Meta,
    Notificacao,
    Postagem,
    Usuario,
)
from utils import IDADE_MAIORIDADE, limite_nascimento_maioridade

_COLUNAS_RANKING = "id_usuario, nome, cidade, estado, pontuacao_total, posicao"


def _clausula_maior_de_idade_ou_proprio(id_solicitante):
    limite = limite_nascimento_maioridade(date.today())
    maior = db.or_(
        Usuario.data_nascimento <= limite,
        db.and_(
            Usuario.data_nascimento.is_(None),
            db.or_(Usuario.idade.is_(None), Usuario.idade >= IDADE_MAIORIDADE),
        ),
    )
    if id_solicitante is None:
        return maior
    return db.or_(Usuario.id_usuario == id_solicitante, maior)


def _escapar_like(termo):
    return termo.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


_CAMPOS_EDITAVEIS = (
    "nome", "email", "data_nascimento", "peso", "altura",
    "cidade", "estado", "descricao",
)


class UsuarioRepository:

    @staticmethod
    def listar(filtro_nome=None):
        query = Usuario.query
        if filtro_nome:
            query = query.filter(Usuario.nome.like(f"%{filtro_nome}%"))
        return query.order_by(Usuario.nome).all()

    @staticmethod
    def buscar_publicos(termo, id_excluido, limite):
        padrao = "%" + _escapar_like(termo) + "%"
        return (
            Usuario.query.join(
                Consentimento,
                db.and_(
                    Consentimento.id_usuario == Usuario.id_usuario,
                    Consentimento.chave == "busca_perfil",
                    Consentimento.aceito.is_(True),
                ),
            )
            .filter(
                Usuario.perfil_publico.is_(True),
                Usuario.id_usuario != id_excluido,
                db.or_(
                    Usuario.nome.like(padrao, escape="\\"),
                    Usuario.cidade.like(padrao, escape="\\"),
                ),
            )
            .order_by(Usuario.nome)
            .limit(limite)
            .all()
        )

    @staticmethod
    def buscar_por_id(id_usuario):
        return db.session.get(Usuario, id_usuario)

    @staticmethod
    def buscar_por_email(email):
        return Usuario.query.filter_by(email=email).first()

    @staticmethod
    def criar(dados):
        usuario = Usuario(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            data_nascimento=dados.get("data_nascimento"),
            cidade=dados.get("cidade"),
            estado=dados.get("estado"),
            descricao=dados.get("descricao"),
            perfil_publico=dados.get("perfil_publico", True),
            responsavel_nome=dados.get("responsavel_nome"),
            responsavel_email=dados.get("responsavel_email"),
            responsavel_autorizado_em=dados.get("responsavel_autorizado_em"),
        )
        db.session.add(usuario)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return usuario

    @staticmethod
    def atualizar(usuario, dados):
        for campo in _CAMPOS_EDITAVEIS:
            if dados.get(campo) is not None:
                setattr(usuario, campo, dados[campo])
        if dados.get("senha"):
            usuario.senha = dados["senha"]
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return usuario

    @staticmethod
    def excluir(usuario):
        db.session.delete(usuario)
        db.session.commit()

    @staticmethod
    def salvar(usuario):
        db.session.add(usuario)
        db.session.commit()
        return usuario


class AtividadeRepository:

    @staticmethod
    def listar_do_usuario(id_usuario):
        return (
            Atividade.query.filter_by(id_usuario=id_usuario)
            .order_by(Atividade.data_registro.desc())
            .all()
        )

    @staticmethod
    def buscar_por_id(id_atividade):
        return db.session.get(Atividade, id_atividade)

    @staticmethod
    def criar(id_usuario, dados):
        atividade = Atividade(
            id_usuario=id_usuario,
            tipo=dados["tipo"],
            titulo=dados.get("titulo"),
            descricao=dados.get("descricao"),
            tempo_min=dados.get("tempo_min"),
            distancia_km=dados.get("distancia_km"),
            carga_kg=dados.get("carga_kg"),
            repeticoes=dados.get("repeticoes"),
            pontuacao=dados["pontuacao"],
        )
        db.session.add(atividade)
        db.session.commit()
        return atividade

    @staticmethod
    def excluir(atividade):
        db.session.delete(atividade)
        db.session.commit()

    @staticmethod
    def listar_publicas(limite, id_solicitante=None):
        return (
            Atividade.query.join(Usuario, Atividade.id_usuario == Usuario.id_usuario)
            .filter(Usuario.perfil_publico.is_(True), _clausula_maior_de_idade_ou_proprio(id_solicitante))
            .order_by(Atividade.data_registro.desc())
            .limit(limite)
            .all()
        )

    @staticmethod
    def maior_carga(id_usuario, titulo_normalizado):
        resultado = (
            db.session.query(func.max(Atividade.carga_kg))
            .filter(
                Atividade.id_usuario == id_usuario,
                Atividade.tipo == "musculacao",
                func.lower(Atividade.titulo) == titulo_normalizado,
            )
            .scalar()
        )
        return float(resultado) if resultado is not None else None

    @staticmethod
    def contar_desde(id_usuario, data_inicio):
        return Atividade.query.filter(
            Atividade.id_usuario == id_usuario,
            Atividade.data_registro >= data_inicio,
        ).count()

    @staticmethod
    def contar_no_periodo(id_usuario, inicio, fim, titulo_normalizado=None):
        query = Atividade.query.filter(
            Atividade.id_usuario == id_usuario,
            Atividade.data_registro >= inicio,
            Atividade.data_registro < fim,
        )
        if titulo_normalizado:
            query = query.filter(func.lower(Atividade.titulo) == titulo_normalizado)
        return query.count()

    @staticmethod
    def maior_carga_no_periodo(id_usuario, inicio, fim, titulo_normalizado=None):
        query = db.session.query(func.max(Atividade.carga_kg)).filter(
            Atividade.id_usuario == id_usuario,
            Atividade.tipo == "musculacao",
            Atividade.data_registro >= inicio,
            Atividade.data_registro < fim,
        )
        if titulo_normalizado:
            query = query.filter(func.lower(Atividade.titulo) == titulo_normalizado)
        resultado = query.scalar()
        return float(resultado) if resultado is not None else None

    @staticmethod
    def listar_do_usuario_por_titulo(id_usuario, titulo_normalizado):
        return (
            Atividade.query.filter(
                Atividade.id_usuario == id_usuario,
                Atividade.tipo == "musculacao",
                func.lower(Atividade.titulo) == titulo_normalizado,
            )
            .order_by(Atividade.data_registro.asc())
            .all()
        )

    @staticmethod
    def pontuacao_total_desde(id_usuario, desde_utc):
        total = (
            db.session.query(func.coalesce(func.sum(Atividade.pontuacao), 0))
            .filter(Atividade.id_usuario == id_usuario, Atividade.data_registro >= desde_utc)
            .scalar()
        )
        return int(total)

    @staticmethod
    def pontuacoes_desde(id_usuario, desde_utc):
        return (
            db.session.query(Atividade.data_registro, Atividade.pontuacao)
            .filter(Atividade.id_usuario == id_usuario, Atividade.data_registro >= desde_utc)
            .all()
        )

    @staticmethod
    def distribuicao_por_tipo(id_usuario):
        linhas = (
            db.session.query(Atividade.tipo, func.count(Atividade.id_atividade))
            .filter(Atividade.id_usuario == id_usuario)
            .group_by(Atividade.tipo)
            .all()
        )
        return dict(linhas)

    @staticmethod
    def datas_registro(id_usuario):
        linhas = (
            db.session.query(Atividade.data_registro)
            .filter(Atividade.id_usuario == id_usuario)
            .all()
        )
        return [linha[0] for linha in linhas]

    @staticmethod
    def totais(id_usuario):
        total_treinos, total_tempo = (
            db.session.query(
                func.count(Atividade.id_atividade),
                func.coalesce(func.sum(Atividade.tempo_min), 0),
            )
            .filter(Atividade.id_usuario == id_usuario)
            .first()
        )
        return total_treinos, total_tempo

    @staticmethod
    def titulos_distintos(id_usuario):
        linhas = (
            db.session.query(Atividade.titulo)
            .filter(
                Atividade.id_usuario == id_usuario,
                Atividade.tipo == "musculacao",
                Atividade.carga_kg.isnot(None),
            )
            .distinct()
            .order_by(Atividade.titulo)
            .all()
        )
        return [linha[0] for linha in linhas if linha[0]]


class PostagemRepository:

    @staticmethod
    def buscar_por_id(id_postagem):
        return db.session.get(Postagem, id_postagem)

    @staticmethod
    def criar(id_usuario, texto, foto):
        postagem = Postagem(id_usuario=id_usuario, texto=texto, foto=foto)
        db.session.add(postagem)
        db.session.commit()
        return postagem

    @staticmethod
    def excluir(postagem):
        db.session.delete(postagem)
        db.session.commit()

    @staticmethod
    def listar_publicas(limite, id_solicitante=None):
        return (
            Postagem.query.join(Usuario, Postagem.id_usuario == Usuario.id_usuario)
            .filter(Usuario.perfil_publico.is_(True), _clausula_maior_de_idade_ou_proprio(id_solicitante))
            .order_by(Postagem.data_registro.desc())
            .limit(limite)
            .all()
        )

    @staticmethod
    def listar_do_usuario(id_usuario):
        return Postagem.query.filter_by(id_usuario=id_usuario).all()


class CurtidaRepository:

    @staticmethod
    def buscar(id_usuario, tipo_alvo, id_alvo):
        return Curtida.query.filter_by(
            id_usuario=id_usuario, tipo_alvo=tipo_alvo, id_alvo=id_alvo
        ).first()

    @staticmethod
    def curtir(id_usuario, tipo_alvo, id_alvo):
        curtida = Curtida(id_usuario=id_usuario, tipo_alvo=tipo_alvo, id_alvo=id_alvo)
        db.session.add(curtida)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return curtida

    @staticmethod
    def descurtir(curtida):
        db.session.delete(curtida)
        db.session.commit()

    @staticmethod
    def contar(tipo_alvo, id_alvo):
        return Curtida.query.filter_by(tipo_alvo=tipo_alvo, id_alvo=id_alvo).count()

    @staticmethod
    def contar_em_lote(tipo_alvo, ids_alvo):
        if not ids_alvo:
            return {}
        linhas = (
            db.session.query(Curtida.id_alvo, func.count(Curtida.id_curtida))
            .filter(Curtida.tipo_alvo == tipo_alvo, Curtida.id_alvo.in_(ids_alvo))
            .group_by(Curtida.id_alvo)
            .all()
        )
        return {id_alvo: total for id_alvo, total in linhas}

    @staticmethod
    def curtidos_pelo_usuario(id_usuario, tipo_alvo, ids_alvo):
        if not ids_alvo:
            return set()
        linhas = (
            db.session.query(Curtida.id_alvo)
            .filter(
                Curtida.id_usuario == id_usuario,
                Curtida.tipo_alvo == tipo_alvo,
                Curtida.id_alvo.in_(ids_alvo),
            )
            .all()
        )
        return {id_alvo for (id_alvo,) in linhas}

    @staticmethod
    def excluir_do_alvo(tipo_alvo, id_alvo):
        Curtida.query.filter_by(tipo_alvo=tipo_alvo, id_alvo=id_alvo).delete()
        db.session.commit()

    @staticmethod
    def excluir_do_usuario(id_usuario):
        Curtida.query.filter_by(id_usuario=id_usuario).delete()
        db.session.commit()


class ComentarioRepository:

    @staticmethod
    def buscar_por_id(id_comentario):
        return db.session.get(Comentario, id_comentario)

    @staticmethod
    def criar(id_usuario, tipo_alvo, id_alvo, texto):
        comentario = Comentario(
            id_usuario=id_usuario, tipo_alvo=tipo_alvo, id_alvo=id_alvo, texto=texto
        )
        db.session.add(comentario)
        db.session.commit()
        return comentario

    @staticmethod
    def excluir(comentario):
        db.session.delete(comentario)
        db.session.commit()

    @staticmethod
    def listar(tipo_alvo, id_alvo):
        return (
            Comentario.query.filter_by(tipo_alvo=tipo_alvo, id_alvo=id_alvo)
            .order_by(Comentario.data_registro.asc())
            .all()
        )

    @staticmethod
    def contar_em_lote(tipo_alvo, ids_alvo):
        if not ids_alvo:
            return {}
        linhas = (
            db.session.query(Comentario.id_alvo, func.count(Comentario.id_comentario))
            .filter(Comentario.tipo_alvo == tipo_alvo, Comentario.id_alvo.in_(ids_alvo))
            .group_by(Comentario.id_alvo)
            .all()
        )
        return {id_alvo: total for id_alvo, total in linhas}

    @staticmethod
    def excluir_do_alvo(tipo_alvo, id_alvo):
        Comentario.query.filter_by(tipo_alvo=tipo_alvo, id_alvo=id_alvo).delete()
        db.session.commit()

    @staticmethod
    def excluir_do_usuario(id_usuario):
        Comentario.query.filter_by(id_usuario=id_usuario).delete()
        db.session.commit()


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

    @staticmethod
    def criar_varios(id_usuario, registros):
        objetos = [Consentimento(id_usuario=id_usuario, **r) for r in registros]
        db.session.add_all(objetos)
        db.session.commit()
        return objetos

    @staticmethod
    def salvar(consentimento):
        db.session.add(consentimento)
        db.session.commit()
        return consentimento


def _linha_ranking(linha):
    if linha is None:
        return None
    d = dict(linha)
    if "pontuacao_total" in d:
        d["pontuacao_total"] = int(d["pontuacao_total"] or 0)
    if "carga_maxima" in d and d["carga_maxima"] is not None:
        d["carga_maxima"] = float(d["carga_maxima"])
    if "posicao" in d and d["posicao"] is not None:
        d["posicao"] = int(d["posicao"])
    return d


class RankingRepository:

    @staticmethod
    def global_(limite):
        sql = text(
            f"SELECT {_COLUNAS_RANKING} FROM vw_ranking_global "
            "ORDER BY posicao LIMIT :lim"
        )
        linhas = db.session.execute(sql, {"lim": limite}).mappings()
        return [_linha_ranking(linha) for linha in linhas]

    @staticmethod
    def regional(cidade, limite):
        sql = text(
            f"SELECT {_COLUNAS_RANKING} FROM vw_ranking_regional "
            "WHERE cidade = :cidade ORDER BY posicao LIMIT :lim"
        )
        linhas = db.session.execute(sql, {"cidade": cidade, "lim": limite}).mappings()
        return [_linha_ranking(linha) for linha in linhas]

    @staticmethod
    def por_exercicio(titulo, cidade, limite):
        sql = text(
            "SELECT id_usuario, nome, cidade, estado, titulo, carga_maxima, posicao "
            "FROM vw_ranking_exercicio "
            "WHERE titulo_normalizado = :titulo "
            + ("AND cidade = :cidade " if cidade else "")
            + "ORDER BY posicao LIMIT :lim"
        )
        parametros = {"titulo": titulo.strip().lower(), "lim": limite}
        if cidade:
            parametros["cidade"] = cidade
        linhas = db.session.execute(sql, parametros).mappings()
        return [_linha_ranking(linha) for linha in linhas]

    @staticmethod
    def minha_posicao_global(id_usuario):
        sql = text(
            "SELECT posicao, pontuacao_total FROM vw_ranking_global "
            "WHERE id_usuario = :id"
        )
        return _linha_ranking(db.session.execute(sql, {"id": id_usuario}).mappings().first())

    @staticmethod
    def minha_posicao_regional(id_usuario):
        sql = text(
            "SELECT posicao, pontuacao_total, cidade FROM vw_ranking_regional "
            "WHERE id_usuario = :id"
        )
        return _linha_ranking(db.session.execute(sql, {"id": id_usuario}).mappings().first())

    @staticmethod
    def grupo(id_grupo, limite):
        sql = text(
            "SELECT id_usuario, nome, pontuacao_total, posicao FROM vw_ranking_grupo "
            "WHERE id_grupo = :id_grupo ORDER BY posicao LIMIT :lim"
        )
        linhas = db.session.execute(sql, {"id_grupo": id_grupo, "lim": limite}).mappings()
        return [_linha_ranking(linha) for linha in linhas]


class GrupoRepository:

    @staticmethod
    def criar(nome, descricao, id_criador, codigo_convite):
        grupo = Grupo(
            nome=nome, descricao=descricao, id_criador=id_criador, codigo_convite=codigo_convite,
        )
        db.session.add(grupo)
        db.session.commit()
        return grupo

    @staticmethod
    def buscar_por_id(id_grupo):
        return db.session.get(Grupo, id_grupo)

    @staticmethod
    def buscar_por_codigo(codigo):
        return Grupo.query.filter_by(codigo_convite=codigo).first()

    @staticmethod
    def salvar(grupo):
        db.session.add(grupo)
        db.session.commit()
        return grupo

    @staticmethod
    def listar_do_usuario(id_usuario):
        return (
            db.session.query(Grupo, GrupoMembro.papel)
            .join(GrupoMembro, GrupoMembro.id_grupo == Grupo.id_grupo)
            .filter(GrupoMembro.id_usuario == id_usuario)
            .order_by(Grupo.nome)
            .all()
        )

    @staticmethod
    def contar_membros(id_grupo):
        return GrupoMembro.query.filter_by(id_grupo=id_grupo).count()

    @staticmethod
    def papel_do_membro(id_grupo, id_usuario):
        membro = GrupoMembro.query.filter_by(id_grupo=id_grupo, id_usuario=id_usuario).first()
        return membro.papel if membro else None

    @staticmethod
    def adicionar_membro(id_grupo, id_usuario, papel="membro"):
        membro = GrupoMembro(id_grupo=id_grupo, id_usuario=id_usuario, papel=papel)
        db.session.add(membro)
        db.session.commit()
        return membro

    @staticmethod
    def listar_membros(id_grupo):
        return (
            db.session.query(Usuario, GrupoMembro.papel)
            .join(GrupoMembro, GrupoMembro.id_usuario == Usuario.id_usuario)
            .filter(GrupoMembro.id_grupo == id_grupo)
            .order_by(GrupoMembro.papel, Usuario.nome)
            .all()
        )

    @staticmethod
    def ids_membros(id_grupo):
        linhas = (
            db.session.query(GrupoMembro.id_usuario)
            .filter(GrupoMembro.id_grupo == id_grupo)
            .all()
        )
        return {id_usuario for (id_usuario,) in linhas}


class ConviteRepository:

    @staticmethod
    def criar(id_grupo, id_remetente, id_destinatario):
        convite = Convite(id_grupo=id_grupo, id_remetente=id_remetente, id_destinatario=id_destinatario)
        db.session.add(convite)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return convite

    @staticmethod
    def buscar_por_id(id_convite):
        return db.session.get(Convite, id_convite)

    @staticmethod
    def buscar_pendente(id_grupo, id_destinatario):
        return Convite.query.filter_by(
            id_grupo=id_grupo, id_destinatario=id_destinatario, status="pendente",
        ).first()

    @staticmethod
    def listar_pendentes_recebidos(id_usuario):
        return (
            db.session.query(Convite, Grupo, Usuario)
            .join(Grupo, Grupo.id_grupo == Convite.id_grupo)
            .join(Usuario, Usuario.id_usuario == Convite.id_remetente)
            .filter(Convite.id_destinatario == id_usuario, Convite.status == "pendente")
            .order_by(Convite.data_envio.desc())
            .all()
        )

    @staticmethod
    def contar_enviados_pendentes(id_usuario):
        return Convite.query.filter_by(id_remetente=id_usuario, status="pendente").count()

    @staticmethod
    def salvar(convite):
        db.session.add(convite)
        db.session.commit()
        return convite


class MetaRepository:

    @staticmethod
    def criar(dados):
        meta = Meta(**dados)
        db.session.add(meta)
        db.session.commit()
        return meta

    @staticmethod
    def buscar_por_id(id_meta):
        return db.session.get(Meta, id_meta)

    @staticmethod
    def listar_do_usuario(id_usuario):
        return (
            Meta.query.filter_by(id_usuario=id_usuario)
            .order_by(Meta.data_inicio.desc())
            .all()
        )

    @staticmethod
    def salvar(meta):
        db.session.add(meta)
        db.session.commit()
        return meta

    @staticmethod
    def excluir(meta):
        db.session.delete(meta)
        db.session.commit()


class DesafioRepository:

    @staticmethod
    def criar(dados):
        desafio = Desafio(**dados)
        db.session.add(desafio)
        db.session.commit()
        return desafio

    @staticmethod
    def buscar_por_id(id_desafio):
        return db.session.get(Desafio, id_desafio)

    @staticmethod
    def listar_ativos(hoje):
        return (
            Desafio.query.filter(Desafio.data_fim >= hoje)
            .order_by(Desafio.data_inicio.asc())
            .all()
        )

    @staticmethod
    def salvar(desafio):
        db.session.add(desafio)
        db.session.commit()
        return desafio


class DesafioUsuarioRepository:

    @staticmethod
    def buscar(id_desafio, id_usuario):
        return db.session.get(DesafioUsuario, (id_desafio, id_usuario))

    @staticmethod
    def inscrever(id_desafio, id_usuario):
        inscricao = DesafioUsuario(id_desafio=id_desafio, id_usuario=id_usuario, status="inscrito")
        db.session.add(inscricao)
        db.session.commit()
        return inscricao

    @staticmethod
    def salvar(inscricao):
        db.session.add(inscricao)
        db.session.commit()
        return inscricao

    @staticmethod
    def listar_do_usuario(id_usuario):
        return DesafioUsuario.query.filter_by(id_usuario=id_usuario).all()


class CompartilhamentoRepository:

    @staticmethod
    def criar(id_usuario, tipo_conteudo, id_atividade, id_meta, rede_social):
        registro = Compartilhamento(
            id_usuario=id_usuario,
            tipo_conteudo=tipo_conteudo,
            id_atividade=id_atividade,
            id_meta=id_meta,
            rede_social=rede_social,
        )
        db.session.add(registro)
        db.session.commit()
        return registro


class NotificacaoRepository:

    @staticmethod
    def criar(id_usuario, tipo, mensagem, tipo_alvo, id_alvo):
        notificacao = Notificacao(
            id_usuario=id_usuario,
            tipo=tipo,
            mensagem=mensagem,
            tipo_alvo=tipo_alvo,
            id_alvo=id_alvo,
        )
        db.session.add(notificacao)
        db.session.commit()
        return notificacao

    @staticmethod
    def listar_do_usuario(id_usuario, limite=50):
        return (
            Notificacao.query.filter_by(id_usuario=id_usuario)
            .order_by(Notificacao.data_envio.desc())
            .limit(limite)
            .all()
        )

    @staticmethod
    def contar_nao_lidas(id_usuario):
        return Notificacao.query.filter_by(id_usuario=id_usuario, lida=False).count()

    @staticmethod
    def buscar_por_id(id_notificacao):
        return db.session.get(Notificacao, id_notificacao)

    @staticmethod
    def marcar_lida(notificacao):
        notificacao.lida = True
        db.session.commit()

    @staticmethod
    def marcar_todas_lidas(id_usuario):
        Notificacao.query.filter_by(id_usuario=id_usuario, lida=False).update({"lida": True})
        db.session.commit()
