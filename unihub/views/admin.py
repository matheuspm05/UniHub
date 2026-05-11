from flask import Blueprint, request

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


bp = Blueprint("admin", __name__, url_prefix="/admin")
ROLES_VALIDAS = {"usuario", "moderador", "admin"}


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
    topicos = ForumTopico.query.order_by(ForumTopico.criado_em.desc()).all()
    return resposta_sucesso(dados=[topico.to_dict() for topico in topicos])


@bp.get("/forum/respostas")
@exigir_admin
def listar_todas_respostas():
    respostas = ForumResposta.query.order_by(ForumResposta.criado_em.desc()).all()
    return resposta_sucesso(dados=[resposta.to_dict() for resposta in respostas])


@bp.get("/usuarios")
@exigir_admin
def listar_usuarios():
    usuarios = Usuario.query.order_by(Usuario.nome.asc()).all()
    return resposta_sucesso(dados=[usuario.to_dict() for usuario in usuarios])


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
    if nova_role not in ROLES_VALIDAS:
        return resposta_erro("Role invalida", 400, {"roles_validas": sorted(ROLES_VALIDAS)})

    usuario.role = nova_role
    db.session.commit()
    return resposta_sucesso("Role atualizada com sucesso", dados=usuario.to_dict())


@bp.patch("/usuarios/<int:usuario_id>/desativar")
@exigir_admin
def desativar_usuario(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        return resposta_erro("Usuario nao encontrado", 404)

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


@bp.patch("/forum/respostas/<int:resposta_id>/desativar")
@exigir_admin
def desativar_resposta(resposta_id):
    resposta = db.session.get(ForumResposta, resposta_id)
    if not resposta:
        return resposta_erro("Resposta nao encontrada", 404)

    resposta.status = "desativado"
    db.session.commit()
    return resposta_sucesso("Resposta desativada com sucesso", dados=resposta.to_dict())
