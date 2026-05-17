from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user

from unihub.ext.db import db
from unihub.models import (
    Evento,
    ForumResposta,
    ForumTopico,
    Mensagem,
    Moradia,
    Notificacao,
    Usuario,
)
from unihub.utils.auth import exigir_admin
from unihub.utils.responses import resposta_erro, resposta_sucesso
from unihub.utils.security import safe_redirect_target
from unihub.utils.view_helpers import contexto_dashboard


bp = Blueprint("admin", __name__, url_prefix="/admin")
ROLES_VALIDAS = {"usuario", "moderador", "admin"}


def _prefer_html():
    return request.accept_mimetypes.best_match(["text/html", "application/json"]) == "text/html"


def _eventos_query():
    query = Evento.query

    status = request.args.get("status")
    if status:
        query = query.filter(Evento.status == status)

    for campo in ["categoria", "local"]:
        valor = request.args.get(campo)
        if valor:
            query = query.filter(getattr(Evento, campo).ilike(f"%{valor}%"))

    organizador = request.args.get("organizador")
    if organizador:
        query = query.join(Usuario, Evento.organizador_id == Usuario.id).filter(
            Usuario.nome.ilike(f"%{organizador}%")
        )

    busca = request.args.get("busca")
    if busca:
        termo = f"%{busca}%"
        query = query.join(Usuario, Evento.organizador_id == Usuario.id).filter(
            db.or_(
                Evento.titulo.ilike(termo),
                Evento.descricao.ilike(termo),
                Evento.local.ilike(termo),
                Evento.categoria.ilike(termo),
                Usuario.nome.ilike(termo),
            )
        )

    return query.order_by(Evento.criado_em.desc())


def _topicos_query():
    query = ForumTopico.query

    status = request.args.get("status")
    if status:
        query = query.filter(ForumTopico.status == status)

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
                ForumTopico.curso.ilike(termo),
                ForumTopico.disciplina.ilike(termo),
                ForumTopico.categoria.ilike(termo),
            )
        )

    return query.order_by(ForumTopico.atualizado_em.desc())


def _respostas_query():
    query = ForumResposta.query.join(ForumTopico)

    status = request.args.get("status")
    if status:
        query = query.filter(ForumResposta.status == status)

    busca = request.args.get("busca")
    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            db.or_(
                ForumResposta.conteudo.ilike(termo),
                ForumTopico.titulo.ilike(termo),
            )
        )

    return query.order_by(ForumResposta.criado_em.desc())


def _usuarios_query():
    query = Usuario.query

    busca = request.args.get("busca")
    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            db.or_(
                Usuario.nome.ilike(termo),
                Usuario.email.ilike(termo),
                Usuario.curso.ilike(termo),
                Usuario.cidade.ilike(termo),
            )
        )

    role = request.args.get("role")
    if role in ROLES_VALIDAS:
        query = query.filter(Usuario.role == role)

    ativo = request.args.get("ativo")
    if ativo == "1":
        query = query.filter(Usuario.ativo.is_(True))
    elif ativo == "0":
        query = query.filter(Usuario.ativo.is_(False))

    return query.order_by(Usuario.nome.asc())


def _opcoes_distintas(model, campo):
    return [
        valor
        for (valor,) in db.session.query(getattr(model, campo))
        .distinct()
        .order_by(getattr(model, campo).asc())
        .all()
        if valor
    ]


@bp.get("/forum")
@exigir_admin
def gerenciar_forum():
    return redirect(url_for("admin.listar_todos_topicos"))


@bp.get("/eventos")
@exigir_admin
def gerenciar_eventos():
    eventos = _eventos_query().all()
    if _prefer_html():
        contexto = contexto_dashboard()
        contexto.update(
            {
                "eventos": eventos,
                "total_eventos": len(eventos),
                "filtros": request.args,
                "categorias": _opcoes_distintas(Evento, "categoria"),
                "locais": _opcoes_distintas(Evento, "local"),
                "organizadores": Usuario.query.order_by(Usuario.nome.asc()).all(),
                "imagem_padrao": "imgs/eventos/foto padrao evento.png",
            }
        )
        return render_template("admin/eventos.html", **contexto)

    return resposta_sucesso(dados=[evento.to_dict() for evento in eventos])


@bp.get("/dashboard")
@exigir_admin
def dashboard():
    return resposta_sucesso(
        dados={
            "total_usuarios": Usuario.query.count(),
            "total_topicos": ForumTopico.query.count(),
            "total_respostas": ForumResposta.query.count(),
            "total_eventos": Evento.query.count(),
            "total_moradias": Moradia.query.count(),
            "total_notificacoes": Notificacao.query.count(),
            "total_mensagens": Mensagem.query.count(),
        }
    )


@bp.get("/forum/topicos")
@exigir_admin
def listar_todos_topicos():
    topicos = _topicos_query().all()
    if _prefer_html():
        contexto = contexto_dashboard()
        contexto.update(
            {
                "topicos": topicos,
                "total_topicos": len(topicos),
                "filtros": request.args,
                "cursos": _opcoes_distintas(ForumTopico, "curso"),
                "disciplinas": _opcoes_distintas(ForumTopico, "disciplina"),
                "categorias": _opcoes_distintas(ForumTopico, "categoria"),
            }
        )
        return render_template("admin/forum_topicos.html", **contexto)

    return resposta_sucesso(dados=[topico.to_dict() for topico in topicos])


@bp.get("/forum/respostas")
@exigir_admin
def listar_todas_respostas():
    respostas = _respostas_query().all()
    if _prefer_html():
        contexto = contexto_dashboard()
        contexto.update(
            {
                "respostas": respostas,
                "total_respostas": len(respostas),
                "filtros": request.args,
            }
        )
        return render_template("admin/forum_respostas.html", **contexto)

    return resposta_sucesso(dados=[resposta.to_dict() for resposta in respostas])


@bp.get("/usuarios")
@exigir_admin
def listar_usuarios():
    usuarios = _usuarios_query().all()
    if _prefer_html():
        contexto = contexto_dashboard()
        contexto.update(
            {
                "usuarios": usuarios,
                "total_usuarios": len(usuarios),
                "filtros": request.args,
                "roles_validas": ["usuario", "moderador", "admin"],
            }
        )
        return render_template("admin/usuarios.html", **contexto)

    return resposta_sucesso(dados=[usuario.to_dict() for usuario in usuarios])


def _alterar_role_usuario(usuario, nova_role):
    if nova_role not in ROLES_VALIDAS:
        return resposta_erro("Role invalida", 400, {"roles_validas": sorted(ROLES_VALIDAS)})
    if usuario.id == current_user.id and nova_role != "admin":
        return resposta_erro("Voce nao pode remover sua propria permissao de admin", 400)

    usuario.role = nova_role
    db.session.commit()
    return None


@bp.patch("/usuarios/<int:usuario_id>/role")
@exigir_admin
def alterar_role_usuario(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        return resposta_erro("Usuario nao encontrado", 404)

    dados = request.get_json(silent=True)
    if not dados:
        return resposta_erro("JSON vazio ou invalido", 400)

    nova_role = dados.get("role")
    response = _alterar_role_usuario(usuario, nova_role)
    if response:
        return response

    return resposta_sucesso("Role atualizada com sucesso", dados=usuario.to_dict())


@bp.post("/usuarios/<int:usuario_id>/role")
@exigir_admin
def alterar_role_usuario_html(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        return resposta_erro("Usuario nao encontrado", 404)

    response = _alterar_role_usuario(usuario, request.form.get("role"))
    if response:
        return response

    destino = safe_redirect_target(request.form.get("next"), url_for("admin.listar_usuarios"))
    return redirect(destino)


@bp.patch("/usuarios/<int:usuario_id>/desativar")
@exigir_admin
def desativar_usuario(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        return resposta_erro("Usuario nao encontrado", 404)
    if usuario.id == current_user.id:
        return resposta_erro("Voce nao pode desativar sua propria conta", 400)

    usuario.ativo = False
    db.session.commit()
    return resposta_sucesso("Usuario desativado com sucesso", dados=usuario.to_dict())


@bp.patch("/forum/topicos/<int:topico_id>/desativar")
@exigir_admin
def desativar_topico(topico_id):
    topico = db.session.get(ForumTopico, topico_id)
    if not topico:
        return resposta_erro("Topico nao encontrado", 404)

    topico.status = "desativado"
    db.session.commit()
    return resposta_sucesso("Topico desativado com sucesso", dados=topico.to_dict())


@bp.post("/forum/topicos/<int:topico_id>/status")
@exigir_admin
def alterar_status_topico_html(topico_id):
    topico = db.session.get(ForumTopico, topico_id)
    if not topico:
        return resposta_erro("Topico nao encontrado", 404)

    status = request.form.get("status")
    if status not in {"aberto", "resolvido", "fechado", "desativado"}:
        return resposta_erro("Status invalido", 400)

    topico.status = status
    db.session.commit()
    return redirect(safe_redirect_target(request.form.get("next"), url_for("admin.listar_todos_topicos")))


@bp.patch("/forum/respostas/<int:resposta_id>/desativar")
@exigir_admin
def desativar_resposta(resposta_id):
    resposta = db.session.get(ForumResposta, resposta_id)
    if not resposta:
        return resposta_erro("Resposta nao encontrada", 404)

    resposta.status = "desativado"
    db.session.commit()
    return resposta_sucesso("Resposta desativada com sucesso", dados=resposta.to_dict())


@bp.patch("/forum/respostas/<int:resposta_id>/restaurar")
@exigir_admin
def restaurar_resposta(resposta_id):
    resposta = db.session.get(ForumResposta, resposta_id)
    if not resposta:
        return resposta_erro("Resposta nao encontrada", 404)

    resposta.status = "ativo"
    db.session.commit()
    return resposta_sucesso("Resposta restaurada com sucesso", dados=resposta.to_dict())


@bp.post("/forum/respostas/<int:resposta_id>/status")
@exigir_admin
def alterar_status_resposta_html(resposta_id):
    resposta = db.session.get(ForumResposta, resposta_id)
    if not resposta:
        return resposta_erro("Resposta nao encontrada", 404)

    status = request.form.get("status")
    if status not in {"ativo", "editado", "desativado"}:
        return resposta_erro("Status invalido", 400)

    resposta.status = status
    db.session.commit()
    return redirect(safe_redirect_target(request.form.get("next"), url_for("admin.listar_todas_respostas")))
