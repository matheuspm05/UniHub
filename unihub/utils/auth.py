from functools import wraps

from flask import request

from unihub.ext.db import db
from unihub.models import Usuario
from unihub.utils.responses import resposta_erro


USUARIO_MOCK_ID = 1
NIVEIS_DE_ROLE = {
    "usuario": 1,
    "moderador": 2,
    "admin": 3,
}


def obter_usuario_atual_id():
    valor = request.headers.get("X-Mock-User-Id") or request.args.get("mock_user_id")
    if not valor:
        return USUARIO_MOCK_ID

    try:
        return int(valor)
    except (TypeError, ValueError):
        return USUARIO_MOCK_ID


def obter_usuario_atual():
    return db.session.get(Usuario, obter_usuario_atual_id())


def usuario_atual_tem_role(role):
    usuario = obter_usuario_atual()
    if not usuario or not usuario.ativo:
        return False

    nivel_necessario = NIVEIS_DE_ROLE.get(role, 0)
    nivel_atual = NIVEIS_DE_ROLE.get(usuario.role, 0)
    return nivel_atual >= nivel_necessario


def usuario_atual_pode_moderar():
    return usuario_atual_tem_role("moderador")


def resposta_proibida(mensagem="Voce nao tem permissao para acessar este recurso"):
    return resposta_erro(mensagem, 403)


def exigir_role(role):
    def decorador(funcao_view):
        @wraps(funcao_view)
        def rota_protegida(*args, **kwargs):
            if not usuario_atual_tem_role(role):
                return resposta_proibida()
            return funcao_view(*args, **kwargs)

        return rota_protegida

    return decorador


def exigir_moderador(funcao_view):
    return exigir_role("moderador")(funcao_view)


def exigir_admin(funcao_view):
    return exigir_role("admin")(funcao_view)
