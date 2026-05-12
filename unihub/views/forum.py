from flask import Blueprint, request

from unihub.ext.db import db
from unihub.models import ForumResposta, ForumTopico, Usuario
from unihub.utils.auth import (
    usuario_atual_pode_moderar,
    resposta_proibida,
    obter_usuario_atual_id,
    exigir_login,
    exigir_moderador,
)
from unihub.utils.responses import resposta_erro, resposta_sucesso


bp = Blueprint("forum", __name__, url_prefix="/forum")


def _payload():
    data = request.get_json(silent=True)
    if not data:
        return None, resposta_erro("JSON vazio ou invalido", 400)
    return data, None


def _missing_fields(data, fields):
    return [field for field in fields if data.get(field) in [None, ""]]


def _get_autor_id(data):
    return obter_usuario_atual_id()


def _get_topico_or_404(topico_id):
    topico = db.session.get(ForumTopico, topico_id)
    if not topico:
        return None, resposta_erro("Topico nao encontrado", 404)
    return topico, None


@bp.get("/topicos")
def listar_topicos():
    query = ForumTopico.query

    status = request.args.get("status")
    if status:
        query = query.filter(ForumTopico.status == status)
    else:
        query = query.filter(ForumTopico.status != "desativado")

    for campo in ["curso", "disciplina", "categoria", "tipo"]:
        valor = request.args.get(campo)
        if valor:
            query = query.filter(getattr(ForumTopico, campo).ilike(f"%{valor}%"))

    busca = request.args.get("busca")
    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            db.or_(
                ForumTopico.titulo.ilike(termo),
                ForumTopico.descricao.ilike(termo),
                ForumTopico.disciplina.ilike(termo),
                ForumTopico.categoria.ilike(termo),
            )
        )

    topicos = query.order_by(ForumTopico.atualizado_em.desc()).all()
    return resposta_sucesso(dados=[topico.to_dict() for topico in topicos])


@bp.get("/topicos/<int:topico_id>")
def detalhar_topico(topico_id):
    topico, response = _get_topico_or_404(topico_id)
    if response:
        return response

    topico.visualizacoes += 1
    db.session.commit()
    return resposta_sucesso(dados=topico.to_dict(include_respostas=True))


@bp.post("/topicos")
@exigir_login
def criar_topico():
    data, response = _payload()
    if response:
        return response

    obrigatorios = ["titulo", "descricao", "curso", "disciplina", "categoria"]
    faltando = _missing_fields(data, obrigatorios)
    if faltando:
        return resposta_erro("Campos obrigatorios ausentes", 400, {"campos": faltando})

    autor_id = _get_autor_id(data)
    if not db.session.get(Usuario, autor_id):
        return resposta_erro("Autor nao encontrado", 404)

    tipo = data.get("tipo", "topico")
    if tipo == "aviso" and not usuario_atual_pode_moderar():
        return resposta_proibida("Somente moderadores podem criar avisos oficiais")

    topico = ForumTopico(
        titulo=data["titulo"],
        descricao=data["descricao"],
        curso=data["curso"],
        disciplina=data["disciplina"],
        categoria=data["categoria"],
        status="aberto",
        tipo=tipo,
        aviso_oficial=True if tipo == "aviso" else bool(data.get("aviso_oficial", False)),
        autor_id=autor_id,
    )

    db.session.add(topico)
    db.session.commit()
    return resposta_sucesso("Topico criado com sucesso", dados=topico.to_dict(), codigo_status=201)


@bp.put("/topicos/<int:topico_id>")
@exigir_login
def editar_topico(topico_id):
    topico, response = _get_topico_or_404(topico_id)
    if response:
        return response

    if topico.autor_id != obter_usuario_atual_id() and not usuario_atual_pode_moderar():
        return resposta_proibida("Somente o autor ou um moderador pode editar este topico")

    data, response = _payload()
    if response:
        return response

    for campo in ["titulo", "descricao", "curso", "disciplina", "categoria", "status", "tipo"]:
        if campo in data:
            setattr(topico, campo, data[campo])

    if "aviso_oficial" in data:
        topico.aviso_oficial = bool(data["aviso_oficial"])
    if topico.tipo == "aviso":
        topico.aviso_oficial = True

    db.session.commit()
    return resposta_sucesso("Topico atualizado com sucesso", dados=topico.to_dict())


def _alterar_status_topico(topico_id, status, mensagem):
    topico, response = _get_topico_or_404(topico_id)
    if response:
        return response

    topico.status = status
    db.session.commit()
    return resposta_sucesso(mensagem, dados=topico.to_dict())


@bp.patch("/topicos/<int:topico_id>/resolver")
@exigir_moderador
def resolver_topico(topico_id):
    return _alterar_status_topico(topico_id, "resolvido", "Topico marcado como resolvido")


@bp.patch("/topicos/<int:topico_id>/fechar")
@exigir_moderador
def fechar_topico(topico_id):
    return _alterar_status_topico(topico_id, "fechado", "Topico fechado com sucesso")


@bp.patch("/topicos/<int:topico_id>/desativar")
@exigir_moderador
def desativar_topico(topico_id):
    return _alterar_status_topico(topico_id, "desativado", "Topico desativado com sucesso")


@bp.get("/topicos/<int:topico_id>/respostas")
def listar_respostas(topico_id):
    topico, response = _get_topico_or_404(topico_id)
    if response:
        return response

    respostas = (
        ForumResposta.query.filter_by(topico_id=topico.id)
        .filter(ForumResposta.status != "desativado")
        .order_by(ForumResposta.criado_em.asc())
        .all()
    )
    return resposta_sucesso(dados=[resposta.to_dict() for resposta in respostas])


@bp.post("/topicos/<int:topico_id>/respostas")
@exigir_login
def criar_resposta(topico_id):
    topico, response = _get_topico_or_404(topico_id)
    if response:
        return response

    if topico.status != "aberto":
        return resposta_erro("So e possivel responder topicos abertos", 400)

    data, response = _payload()
    if response:
        return response

    if not data.get("conteudo"):
        return resposta_erro("Campo obrigatorio ausente", 400, {"campos": ["conteudo"]})

    autor_id = _get_autor_id(data)
    if not db.session.get(Usuario, autor_id):
        return resposta_erro("Autor nao encontrado", 404)

    resposta = ForumResposta(conteudo=data["conteudo"], topico_id=topico.id, autor_id=autor_id)
    db.session.add(resposta)
    db.session.commit()
    return resposta_sucesso("Resposta criada com sucesso", dados=resposta.to_dict(), codigo_status=201)


@bp.put("/respostas/<int:resposta_id>")
@exigir_login
def editar_resposta(resposta_id):
    resposta = db.session.get(ForumResposta, resposta_id)
    if not resposta:
        return resposta_erro("Resposta nao encontrada", 404)
    if resposta.autor_id != obter_usuario_atual_id() and not usuario_atual_pode_moderar():
        return resposta_proibida("Somente o autor ou um moderador pode editar esta resposta")

    data, response = _payload()
    if response:
        return response
    if not data.get("conteudo"):
        return resposta_erro("Campo obrigatorio ausente", 400, {"campos": ["conteudo"]})

    resposta.conteudo = data["conteudo"]
    resposta.status = "editado"
    db.session.commit()
    return resposta_sucesso("Resposta atualizada com sucesso", dados=resposta.to_dict())


@bp.delete("/respostas/<int:resposta_id>")
@exigir_login
def desativar_resposta(resposta_id):
    resposta = db.session.get(ForumResposta, resposta_id)
    if not resposta:
        return resposta_erro("Resposta nao encontrada", 404)
    if resposta.autor_id != obter_usuario_atual_id() and not usuario_atual_pode_moderar():
        return resposta_proibida("Somente o autor ou um moderador pode desativar esta resposta")

    resposta.status = "desativado"
    db.session.commit()
    return resposta_sucesso("Resposta desativada com sucesso", dados=resposta.to_dict())


@bp.get("/meus-posts")
@exigir_login
def meus_posts():
    usuario_atual_id = obter_usuario_atual_id()
    topicos = ForumTopico.query.filter_by(autor_id=usuario_atual_id).all()
    respostas = ForumResposta.query.filter_by(autor_id=usuario_atual_id).all()
    return resposta_sucesso(
        dados={
            "topicos": [topico.to_dict() for topico in topicos],
            "respostas": [resposta.to_dict() for resposta in respostas],
        }
    )


@bp.get("/avisos")
def listar_avisos():
    avisos = (
        ForumTopico.query.filter(
            db.or_(ForumTopico.tipo == "aviso", ForumTopico.aviso_oficial.is_(True))
        )
        .filter(ForumTopico.status != "desativado")
        .order_by(ForumTopico.atualizado_em.desc())
        .all()
    )
    return resposta_sucesso(dados=[aviso.to_dict() for aviso in avisos])
