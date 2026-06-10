from flask import Blueprint, render_template, request
from flask_login import current_user

from unihub.ext.db import db
from unihub.models import Usuario
from unihub.options import CURSOS, PERIODOS
from unihub.utils.auth import exigir_login, obter_usuario_atual_id
from unihub.utils.responses import resposta_erro, resposta_sucesso
from unihub.utils.view_helpers import contexto_dashboard, prefere_html


bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")
CURSOS_VALIDOS = {valor for valor, _ in CURSOS}
PERIODOS_VALIDOS = {valor for valor, _ in PERIODOS}


def _usuario_publico(usuario):
    return usuario.to_public_dict()


@bp.get("")
@exigir_login
def listar_usuarios():
    usuarios = (
        Usuario.query.filter(
            Usuario.ativo.is_(True),
            Usuario.role != "admin",
        )
        .order_by(Usuario.nome.asc())
        .all()
    )
    if prefere_html():
        contexto = contexto_dashboard()
        contexto.update(
            {
                "usuarios": usuarios,
                "total_usuarios": len(usuarios),
                "usuario_destaque": None,
                "perfil_sidebar": current_user,
            }
        )
        return render_template("usuarios/index.html", **contexto)
    return resposta_sucesso(dados=[_usuario_publico(usuario) for usuario in usuarios])


@bp.get("/me")
@exigir_login
def usuario_atual():
    usuario = db.session.get(Usuario, obter_usuario_atual_id())
    if not usuario:
        return resposta_erro("Usuario logado nao encontrado", 404)

    return resposta_sucesso(dados=usuario.to_dict())


@bp.patch("/me")
@exigir_login
def atualizar_usuario_atual():
    usuario = db.session.get(Usuario, obter_usuario_atual_id())
    if not usuario:
        return resposta_erro("Usuario logado nao encontrado", 404)

    data = request.get_json(silent=True) or {}
    if not data:
        return resposta_erro("JSON vazio ou invalido", 400)

    if "curso" in data and data["curso"] not in CURSOS_VALIDOS:
        return resposta_erro("Curso invalido", 400)
    if "periodo" in data and data["periodo"] not in PERIODOS_VALIDOS:
        return resposta_erro("Periodo invalido", 400)

    for campo in ["nome", "curso", "periodo", "cidade", "bio", "instagram", "linkedin", "whatsapp"]:
        if campo in data:
            setattr(usuario, campo, data[campo])

    db.session.commit()
    return resposta_sucesso("Usuario atualizado com sucesso", dados=usuario.to_dict())


@bp.get("/<int:usuario_id>")
@exigir_login
def detalhar_usuario(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if not usuario or not usuario.ativo or usuario.role == "admin":
        return resposta_erro("Usuario nao encontrado", 404)

    if prefere_html():
        usuarios = (
            Usuario.query.filter(
                Usuario.ativo.is_(True),
                Usuario.role != "admin",
            )
            .order_by(Usuario.nome.asc())
            .all()
        )
        contexto = contexto_dashboard()
        contexto.update(
            {
                "usuarios": usuarios,
                "total_usuarios": len(usuarios),
                "usuario_destaque": usuario,
                "perfil_sidebar": current_user,
            }
        )
        return render_template("usuarios/index.html", **contexto)

    return resposta_sucesso(dados=_usuario_publico(usuario))
