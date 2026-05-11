from flask import Blueprint, request

from unihub.ext.db import db
from unihub.models import Mensagem, Usuario
from unihub.utils.auth import obter_usuario_atual_id
from unihub.utils.responses import resposta_erro, resposta_sucesso


bp = Blueprint("mensagens", __name__, url_prefix="/mensagens")


def _payload():
    data = request.get_json(silent=True)
    if not data:
        return None, resposta_erro("JSON vazio ou invalido", 400)
    return data, None


@bp.get("")
def listar_conversas():
    usuario_atual_id = obter_usuario_atual_id()
    mensagens = (
        Mensagem.query.filter(
            db.or_(
                Mensagem.remetente_id == usuario_atual_id,
                Mensagem.destinatario_id == usuario_atual_id,
            )
        )
        .order_by(Mensagem.criado_em.desc())
        .all()
    )

    conversas = {}
    for mensagem in mensagens:
        outro_id = (
            mensagem.destinatario_id
            if mensagem.remetente_id == usuario_atual_id
            else mensagem.remetente_id
        )
        if outro_id not in conversas:
            usuario = db.session.get(Usuario, outro_id)
            conversas[outro_id] = {
                "usuario": usuario.to_dict() if usuario else None,
                "ultima_mensagem": mensagem.to_dict(),
                "nao_lidas": 0,
                "atualizado_em": mensagem.criado_em.isoformat() if mensagem.criado_em else None,
            }
        if mensagem.destinatario_id == usuario_atual_id and not mensagem.lida:
            conversas[outro_id]["nao_lidas"] += 1

    return resposta_sucesso(dados=list(conversas.values()))


@bp.get("/<int:usuario_id>")
def listar_conversa(usuario_id):
    usuario_atual_id = obter_usuario_atual_id()
    if not db.session.get(Usuario, usuario_id):
        return resposta_erro("Usuario nao encontrado", 404)

    mensagens = (
        Mensagem.query.filter(
            db.or_(
                db.and_(Mensagem.remetente_id == usuario_atual_id, Mensagem.destinatario_id == usuario_id),
                db.and_(Mensagem.remetente_id == usuario_id, Mensagem.destinatario_id == usuario_atual_id),
            )
        )
        .order_by(Mensagem.criado_em.asc())
        .all()
    )

    for mensagem in mensagens:
        if mensagem.remetente_id == usuario_id and mensagem.destinatario_id == usuario_atual_id:
            mensagem.lida = True
    db.session.commit()

    return resposta_sucesso(dados=[mensagem.to_dict() for mensagem in mensagens])


@bp.post("")
def enviar_mensagem():
    data, response = _payload()
    if response:
        return response

    faltando = [campo for campo in ["destinatario_id", "conteudo"] if not data.get(campo)]
    if faltando:
        return resposta_erro("Campos obrigatorios ausentes", 400, {"campos": faltando})

    if not db.session.get(Usuario, data["destinatario_id"]):
        return resposta_erro("Destinatario nao encontrado", 404)

    mensagem = Mensagem(
        remetente_id=obter_usuario_atual_id(),
        destinatario_id=data["destinatario_id"],
        conteudo=data["conteudo"],
    )
    db.session.add(mensagem)
    db.session.commit()
    return resposta_sucesso("Mensagem enviada com sucesso", dados=mensagem.to_dict(), codigo_status=201)


@bp.patch("/<int:mensagem_id>/ler")
def marcar_mensagem_como_lida(mensagem_id):
    mensagem = db.session.get(Mensagem, mensagem_id)
    if not mensagem:
        return resposta_erro("Mensagem nao encontrada", 404)

    mensagem.lida = True
    db.session.commit()
    return resposta_sucesso("Mensagem marcada como lida", dados=mensagem.to_dict())


@bp.delete("/<int:mensagem_id>")
def excluir_mensagem(mensagem_id):
    mensagem = db.session.get(Mensagem, mensagem_id)
    if not mensagem:
        return resposta_erro("Mensagem nao encontrada", 404)

    # Futuramente pode virar soft delete com status/removida_em no model.
    db.session.delete(mensagem)
    db.session.commit()
    return resposta_sucesso("Mensagem removida com sucesso")
