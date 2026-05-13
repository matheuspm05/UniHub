from flask import request

from unihub.ext.db import db
from unihub.models import Mensagem, Notificacao
from unihub.utils.auth import obter_usuario_atual_id


def prefere_html():
    return request.accept_mimetypes.best_match(["text/html", "application/json"]) == "text/html"


def iniciais(nome):
    partes = [parte for parte in nome.split() if parte]
    if not partes:
        return "U"
    return "".join(parte[0].upper() for parte in partes[:2])


def contar_mensagens_nao_lidas(usuario_id):
    if not usuario_id:
        return 0
    return Mensagem.query.filter(
        Mensagem.destinatario_id == usuario_id,
        Mensagem.lida.is_(False),
        Mensagem.removida_pelo_destinatario.is_(False),
    ).count()


def contexto_dashboard():
    usuario_id = obter_usuario_atual_id()
    return {
        "iniciais": iniciais,
        "notificacoes_count": Notificacao.query.filter_by(
            usuario_id=usuario_id,
            lida=False,
        ).count(),
        "mensagens_count": contar_mensagens_nao_lidas(usuario_id),
    }


def mensagem_visivel_para_usuario(usuario_id):
    return db.or_(
        db.and_(
            Mensagem.remetente_id == usuario_id,
            Mensagem.removida_pelo_remetente.is_(False),
        ),
        db.and_(
            Mensagem.destinatario_id == usuario_id,
            Mensagem.removida_pelo_destinatario.is_(False),
        ),
    )
