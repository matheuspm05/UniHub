from flask import request
from flask_wtf import CSRFProtect


csrf = CSRFProtect()


def init_app(app):
    # Forms rendered by Jinja are protected, while the JSON API keeps its payload contract.
    app.config.setdefault("WTF_CSRF_CHECK_DEFAULT", False)
    if app.config.get("TESTING"):
        app.config["WTF_CSRF_ENABLED"] = False

    csrf.init_app(app)

    @app.before_request
    def proteger_formularios_html():
        if app.config.get("TESTING"):
            return None
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return None
        if not request.form:
            return None
        return csrf.protect()
