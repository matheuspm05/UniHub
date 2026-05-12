from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user

from unihub.ext.db import db
from unihub.models import ForumResposta, ForumTopico, Mensagem, Notificacao, Usuario
from unihub.utils.auth import (
    usuario_atual_pode_moderar,
    resposta_proibida,
    obter_usuario_atual_id,
    exigir_login,
    exigir_moderador,
)
from unihub.utils.responses import resposta_erro, resposta_sucesso


bp = Blueprint("forum", __name__, url_prefix="/forum")


def _prefer_html():
    return request.accept_mimetypes.best_match(["text/html", "application/json"]) == "text/html"


def _iniciais(nome):
    partes = [parte for parte in nome.split() if parte]
    if not partes:
        return "U"
    return "".join(parte[0].upper() for parte in partes[:2])


def _base_contexto():
    usuario_id = obter_usuario_atual_id()
    return {
        "iniciais": _iniciais,
        "notificacoes_count": Notificacao.query.filter_by(
            usuario_id=usuario_id,
            lida=False,
        ).count(),
        "mensagens_count": Mensagem.query.filter_by(
            destinatario_id=usuario_id,
            lida=False,
        ).count(),
    }


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


def _opcoes_topicos(campo):
    return [
        valor
        for (valor,) in db.session.query(getattr(ForumTopico, campo))
        .filter(ForumTopico.status != "desativado")
        .distinct()
        .order_by(getattr(ForumTopico, campo).asc())
        .all()
        if valor
    ]


def _query_topicos():
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

    return query.order_by(ForumTopico.atualizado_em.desc())


def _dados_topico_formulario():
    return {
        "titulo": request.form.get("titulo", "").strip(),
        "descricao": request.form.get("descricao", "").strip(),
        "curso": request.form.get("curso", "").strip(),
        "disciplina": request.form.get("disciplina", "").strip(),
        "categoria": request.form.get("categoria", "").strip(),
        "tipo": "topico",
        "aviso_oficial": False,
    }


def _criar_topico_com_dados(data):
    obrigatorios = ["titulo", "descricao", "curso", "disciplina", "categoria"]
    faltando = _missing_fields(data, obrigatorios)
    if faltando:
        return None, resposta_erro("Campos obrigatorios ausentes", 400, {"campos": faltando})

    autor_id = _get_autor_id(data)
    if not db.session.get(Usuario, autor_id):
        return None, resposta_erro("Autor nao encontrado", 404)

    tipo = data.get("tipo", "topico")
    if tipo == "aviso" and not usuario_atual_pode_moderar():
        return None, resposta_proibida("Somente moderadores podem criar avisos oficiais")

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
    return topico, None


@bp.get("")
@exigir_login
def tela_forum():
    return _renderizar_lista_topicos()


def _renderizar_lista_topicos():
    topicos = _query_topicos().all()
    contexto = _base_contexto()
    contexto.update(
        {
            "topicos": topicos,
            "filtros": request.args,
            "cursos": _opcoes_topicos("curso"),
            "disciplinas": _opcoes_topicos("disciplina"),
            "categorias": _opcoes_topicos("categoria"),
        }
    )
    return render_template("forum/index.html", **contexto)


@bp.get("/topicos")
def listar_topicos():
    topicos = _query_topicos().all()
    if _prefer_html():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.tela_login"))
        return _renderizar_lista_topicos()

    return resposta_sucesso(dados=[topico.to_dict() for topico in topicos])


@bp.get("/topicos/<int:topico_id>")
def detalhar_topico(topico_id):
    topico, response = _get_topico_or_404(topico_id)
    if response:
        return response

    topico.visualizacoes += 1
    db.session.commit()
    if _prefer_html():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.tela_login"))

        contexto = _base_contexto()
        respostas = [
            resposta
            for resposta in sorted(topico.respostas, key=lambda item: item.criado_em)
            if resposta.status != "desativado"
        ]
        contexto.update(
            {
                "topico": topico,
                "respostas": respostas,
                "usuario_e_autor": topico.autor_id == obter_usuario_atual_id(),
            }
        )
        return render_template("forum/detalhes.html", **contexto)

    return resposta_sucesso(dados=topico.to_dict(include_respostas=True))


@bp.post("/topicos")
@exigir_login
def criar_topico():
    data, response = _payload()
    if response:
        return response

    topico, response = _criar_topico_com_dados(data)
    if response:
        return response
    return resposta_sucesso("Topico criado com sucesso", dados=topico.to_dict(), codigo_status=201)


@bp.route("/criar", methods=["GET", "POST"])
@exigir_login
def criar_topico_html():
    if request.method == "POST":
        topico, response = _criar_topico_com_dados(_dados_topico_formulario())
        if response:
            return response
        return redirect(url_for("forum.detalhar_topico", topico_id=topico.id))

    contexto = _base_contexto()
    contexto.update(
        {
            "cursos": _opcoes_topicos("curso"),
            "disciplinas": _opcoes_topicos("disciplina"),
            "categorias": _opcoes_topicos("categoria"),
        }
    )
    return render_template("forum/criar.html", **contexto)


@bp.put("/topicos/<int:topico_id>")
@exigir_login
def editar_topico(topico_id):
    topico, response = _get_topico_or_404(topico_id)
    if response:
        return response

    pode_moderar = usuario_atual_pode_moderar()
    if topico.autor_id != obter_usuario_atual_id() and not pode_moderar:
        return resposta_proibida("Somente o autor ou um moderador pode editar este topico")

    data, response = _payload()
    if response:
        return response

    if not pode_moderar:
        campos_restritos = [
            campo for campo in ["status", "tipo", "aviso_oficial"] if campo in data
        ]
        if campos_restritos:
            return resposta_proibida(
                "Somente moderadores podem alterar status, tipo ou aviso_oficial"
            )

    campos_editaveis = ["titulo", "descricao", "curso", "disciplina", "categoria"]
    if pode_moderar:
        campos_editaveis.extend(["status", "tipo"])

    for campo in campos_editaveis:
        if campo in data:
            setattr(topico, campo, data[campo])

    if pode_moderar and "aviso_oficial" in data:
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

    if request.form:
        data = {"conteudo": request.form.get("conteudo", "").strip()}
    else:
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
    if _prefer_html():
        return redirect(url_for("forum.detalhar_topico", topico_id=topico.id))

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
