import logging
from pathlib import Path

from flask import Flask

from unihub.ext.db import db


def create_app(test_config=None):
    base_dir = Path(__file__).resolve().parent
    flask_app = Flask(
        __name__,
        template_folder=str(base_dir / "templates"),
        static_folder=str(base_dir / "static"),
    )

    if flask_app.debug:
        flask_app.logger.setLevel(logging.DEBUG)

    from unihub.ext.config import init_app as init_config
    init_config(flask_app, test_config)

    from unihub.ext.db import init_app as init_db
    init_db(flask_app)

    from unihub.ext.db import register_models
    register_models()

    from unihub.ext.login import init_app as init_login
    init_login(flask_app)

    from unihub.utils.security import init_app as init_security
    init_security(flask_app)

    from unihub.views import init_app as init_views
    init_views(flask_app)

    from unihub.ext.swagger import init_app as init_swagger
    init_swagger(flask_app)

    from unihub.services.seed import register_seed_command
    register_seed_command(flask_app)

    from unihub.models import (
        AgendaEvento,
        Evento,
        ForumResposta,
        ForumTopico,
        Mensagem,
        Moradia,
        Notificacao,
        Usuario,
    )

    @flask_app.shell_context_processor
    def make_shell_context():
        return {
            "db": db,
            "AgendaEvento": AgendaEvento,
            "Evento": Evento,
            "ForumResposta": ForumResposta,
            "ForumTopico": ForumTopico,
            "Mensagem": Mensagem,
            "Moradia": Moradia,
            "Notificacao": Notificacao,
            "Usuario": Usuario,
        }

    return flask_app


app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
