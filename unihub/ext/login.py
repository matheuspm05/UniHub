from flask import redirect, request, url_for
from flask_login import LoginManager

from unihub.ext.db import db
from unihub.models import Usuario
from unihub.utils.responses import resposta_erro


login_manager = LoginManager()


@login_manager.user_loader
def carregar_usuario(usuario_id):
    try:
        return db.session.get(Usuario, int(usuario_id))
    except (TypeError, ValueError):
        return None


@login_manager.unauthorized_handler
def usuario_nao_autenticado():
    if request.accept_mimetypes.best_match(["text/html", "application/json"]) == "text/html":
        return redirect(url_for("auth.tela_login"))
    return resposta_erro("Autenticacao obrigatoria", 401)


def init_app(app):
    login_manager.init_app(app)
