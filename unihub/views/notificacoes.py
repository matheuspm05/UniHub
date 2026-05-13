from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user

from unihub.ext.db import db
from unihub.models import Notificacao
from unihub.utils.auth import exigir_login, obter_usuario_atual_id
from unihub.utils.responses import resposta_erro, resposta_sucesso
from unihub.utils.view_helpers import contexto_dashboard, iniciais, prefere_html


bp = Blueprint("notificacoes", __name__, url_prefix="/notificacoes")


def _as_bool(value):
    if value is None:
        return None
    return str(value).lower() in ["1", "true", "sim", "yes"]


def _iniciais(nome):
    return iniciais(nome)


def _prefer_html():
    return prefere_html()


def _base_contexto():
    return contexto_dashboard()


@bp.get("")
def listar_notificacoes():
    if not current_user.is_authenticated:
        if _prefer_html():
            return redirect(url_for("auth.tela_login"))
        return resposta_erro("Autenticacao obrigatoria", 401)

    query = Notificacao.query.filter_by(usuario_id=obter_usuario_atual_id())

    tipo = request.args.get("tipo")
    if tipo:
        query = query.filter(Notificacao.tipo == tipo)

    lida = _as_bool(request.args.get("lida"))
    if lida is not None:
        query = query.filter(Notificacao.lida == lida)

    notificacoes = query.order_by(Notificacao.criado_em.desc()).all()
    if _prefer_html():
        contexto = _base_contexto()
        contexto.update(
            {
                "notificacoes": notificacoes,
            }
        )
        return render_template("main/notificacoes.html", **contexto)

    return resposta_sucesso(dados=[notificacao.to_dict() for notificacao in notificacoes])


def _get_notificacao_or_404(notificacao_id):
    notificacao = Notificacao.query.filter_by(
        id=notificacao_id,
        usuario_id=obter_usuario_atual_id(),
    ).first()
    if not notificacao:
        return None, resposta_erro("Notificacao nao encontrada", 404)
    return notificacao, None


@bp.patch("/<int:notificacao_id>/ler")
@exigir_login
def marcar_como_lida(notificacao_id):
    notificacao, response = _get_notificacao_or_404(notificacao_id)
    if response:
        return response

    notificacao.lida = True
    db.session.commit()
    return resposta_sucesso("Notificacao marcada como lida", dados=notificacao.to_dict())


@bp.patch("/<int:notificacao_id>/nao-lida")
@exigir_login
def marcar_como_nao_lida(notificacao_id):
    notificacao, response = _get_notificacao_or_404(notificacao_id)
    if response:
        return response

    notificacao.lida = False
    db.session.commit()
    return resposta_sucesso("Notificacao marcada como nao lida", dados=notificacao.to_dict())


@bp.patch("/ler-todas")
@exigir_login
def marcar_todas_como_lidas():
    notificacoes = Notificacao.query.filter_by(
        usuario_id=obter_usuario_atual_id(),
        lida=False,
    ).all()
    for notificacao in notificacoes:
        notificacao.lida = True

    db.session.commit()
    return resposta_sucesso(
        "Notificacoes marcadas como lidas",
        dados={"total_atualizadas": len(notificacoes)},
    )


@bp.delete("/<int:notificacao_id>")
@exigir_login
def excluir_notificacao(notificacao_id):
    notificacao, response = _get_notificacao_or_404(notificacao_id)
    if response:
        return response

    db.session.delete(notificacao)
    db.session.commit()
    return resposta_sucesso("Notificacao removida com sucesso")
