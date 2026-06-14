from flask import request

from unihub.models import Notificacao
from unihub.utils.auth import obter_usuario_atual_id

ROLE_LABELS = {
    "usuario": "Usuario comum",
    "moderador": "Representante",
    "admin": "Admin",
}


def prefere_html():
    return request.accept_mimetypes.best_match(["text/html", "application/json"]) == "text/html"


def iniciais(nome):
    partes = [parte for parte in nome.split() if parte]
    if not partes:
        return "U"
    return "".join(parte[0].upper() for parte in partes[:2])


def role_label(role):
    return ROLE_LABELS.get(role, str(role).capitalize())


def is_admin_user(user):
    return bool(user and getattr(user, "role", None) == "admin")


def contexto_dashboard():
    usuario_id = obter_usuario_atual_id()
    return {
        "iniciais": iniciais,
        "notificacoes_count": Notificacao.query.filter_by(
            usuario_id=usuario_id,
            lida=False,
        ).count(),
    }
