import secrets
from hmac import compare_digest
from urllib.parse import urlparse

from flask import abort, request, session
from flask_login import current_user


CSRF_SESSION_KEY = "_csrf_token"
CSRF_FORM_FIELD = "_csrf_token"


def gerar_csrf_token():
    token = session.get(CSRF_SESSION_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        session[CSRF_SESSION_KEY] = token
    return token


def validar_csrf_token(token):
    esperado = session.get(CSRF_SESSION_KEY)
    return bool(token and esperado and compare_digest(str(token), str(esperado)))


def safe_redirect_target(target, fallback):
    if not target:
        return fallback

    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc or not target.startswith("/") or target.startswith("//"):
        return fallback
    return target


def init_app(app):
    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": gerar_csrf_token}

    @app.before_request
    def proteger_formularios_html():
        if app.testing:
            return None
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return None
        if not current_user.is_authenticated or not request.form:
            return None

        token = request.form.get(CSRF_FORM_FIELD) or request.headers.get("X-CSRF-Token")
        if not validar_csrf_token(token):
            abort(400, description="Token CSRF invalido ou ausente")

        return None
