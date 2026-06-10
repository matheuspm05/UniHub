from functools import wraps

from flask import redirect, request, url_for
from flask_login import current_user

from unihub.utils.responses import resposta_erro


NIVEIS_DE_ROLE = {
    "usuario": 1,
    "moderador": 2,
    "admin": 3,
}


def obter_usuario_atual_id():
    if not current_user.is_authenticated:
        return None
    return current_user.id


def usuario_atual_tem_role(role):
    if not current_user.is_authenticated or not current_user.ativo:
        return False

    nivel_necessario = NIVEIS_DE_ROLE.get(role, 0)
    nivel_atual = NIVEIS_DE_ROLE.get(current_user.role, 0)
    return nivel_atual >= nivel_necessario


def usuario_atual_pode_moderar():
    return usuario_atual_tem_role("moderador")


def usuario_atual_e_admin():
    return usuario_atual_tem_role("admin")


def resposta_nao_autenticada(mensagem="Autenticacao obrigatoria"):
    if request.accept_mimetypes.best_match(["text/html", "application/json"]) == "text/html":
        return redirect(url_for("auth.tela_login"))
    return resposta_erro(mensagem, 401)


def resposta_proibida(mensagem="Voce nao tem permissao para acessar este recurso"):
    return resposta_erro(mensagem, 403)


def exigir_login(funcao_view):
    @wraps(funcao_view)
    def rota_protegida(*args, **kwargs):
        if not current_user.is_authenticated:
            return resposta_nao_autenticada()
        if not current_user.ativo:
            return resposta_proibida("Usuario desativado")
        return funcao_view(*args, **kwargs)

    return rota_protegida


def exigir_role(role):
    def decorador(funcao_view):
        @wraps(funcao_view)
        def rota_protegida(*args, **kwargs):
            if not current_user.is_authenticated:
                return resposta_nao_autenticada()
            if not usuario_atual_tem_role(role):
                return resposta_proibida()
            return funcao_view(*args, **kwargs)

        return rota_protegida

    return decorador


def exigir_moderador(funcao_view):
    return exigir_role("moderador")(funcao_view)


def exigir_admin(funcao_view):
    return exigir_role("admin")(funcao_view)
