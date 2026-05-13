from flask import Blueprint, request

from unihub.ext.db import db
from unihub.models import Usuario
from unihub.utils.auth import exigir_login, obter_usuario_atual_id
from unihub.utils.responses import resposta_erro, resposta_sucesso


bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


def _usuario_publico(usuario):
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "curso": usuario.curso,
        "periodo": usuario.periodo,
        "cidade": usuario.cidade,
        "bio": usuario.bio,
        "role": usuario.role,
        "selo": usuario.selo,
    }


@bp.get("")
@exigir_login
def listar_usuarios():
    usuarios = Usuario.query.filter_by(ativo=True).order_by(Usuario.nome.asc()).all()
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

    for campo in ["nome", "curso", "periodo", "cidade", "bio"]:
        if campo in data:
            setattr(usuario, campo, data[campo])

    db.session.commit()
    return resposta_sucesso("Usuario atualizado com sucesso", dados=usuario.to_dict())


@bp.get("/<int:usuario_id>")
@exigir_login
def detalhar_usuario(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if not usuario or not usuario.ativo:
        return resposta_erro("Usuario nao encontrado", 404)

    return resposta_sucesso(dados=_usuario_publico(usuario))
