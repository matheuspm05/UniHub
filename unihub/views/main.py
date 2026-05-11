from flask import Blueprint

from unihub.utils.responses import resposta_sucesso


bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    return resposta_sucesso(
        mensagem="API UniHub funcionando",
        dados={"message": "API UniHub funcionando"},
    )


@bp.get("/health")
def health():
    return resposta_sucesso(
        mensagem="Status OK",
        dados={"status": "ok", "app": "UniHub"},
    )
