from flask import Blueprint, request

from unihub.ext.db import db
from unihub.models import Notificacao
from unihub.utils.auth import obter_usuario_atual_id
from unihub.utils.responses import resposta_erro, resposta_sucesso


bp = Blueprint("notificacoes", __name__, url_prefix="/notificacoes")


def _as_bool(value):
    if value is None:
        return None
    return str(value).lower() in ["1", "true", "sim", "yes"]


@bp.get("")
def listar_notificacoes():
    query = Notificacao.query.filter_by(usuario_id=obter_usuario_atual_id())

    tipo = request.args.get("tipo")
    if tipo:
        query = query.filter(Notificacao.tipo == tipo)

    lida = _as_bool(request.args.get("lida"))
    if lida is not None:
        query = query.filter(Notificacao.lida == lida)

    notificacoes = query.order_by(Notificacao.criado_em.desc()).all()
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
def marcar_como_lida(notificacao_id):
    notificacao, response = _get_notificacao_or_404(notificacao_id)
    if response:
        return response

    notificacao.lida = True
    db.session.commit()
    return resposta_sucesso("Notificacao marcada como lida", dados=notificacao.to_dict())


@bp.patch("/<int:notificacao_id>/nao-lida")
def marcar_como_nao_lida(notificacao_id):
    notificacao, response = _get_notificacao_or_404(notificacao_id)
    if response:
        return response

    notificacao.lida = False
    db.session.commit()
    return resposta_sucesso("Notificacao marcada como nao lida", dados=notificacao.to_dict())


@bp.patch("/ler-todas")
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
def excluir_notificacao(notificacao_id):
    notificacao, response = _get_notificacao_or_404(notificacao_id)
    if response:
        return response

    db.session.delete(notificacao)
    db.session.commit()
    return resposta_sucesso("Notificacao removida com sucesso")
