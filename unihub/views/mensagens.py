from flask import Blueprint, redirect, render_template, request, url_for

from unihub.ext.db import db
from unihub.models import Mensagem, Usuario
from unihub.utils.auth import exigir_login, obter_usuario_atual_id
from unihub.utils.responses import resposta_erro, resposta_sucesso
from unihub.utils.view_helpers import contexto_dashboard, iniciais, mensagem_visivel_para_usuario, prefere_html


bp = Blueprint("mensagens", __name__, url_prefix="/mensagens")


def _prefer_html():
    return prefere_html()


def _iniciais(nome):
    return iniciais(nome)


def _base_contexto():
    return contexto_dashboard()


def _payload():
    data = request.get_json(silent=True)
    if not data:
        return None, resposta_erro("JSON vazio ou invalido", 400)
    return data, None


def _get_mensagem_do_usuario(mensagem_id):
    usuario_atual_id = obter_usuario_atual_id()
    mensagem = db.session.get(Mensagem, mensagem_id)
    if not mensagem:
        return None, resposta_erro("Mensagem nao encontrada", 404)

    if usuario_atual_id not in [mensagem.remetente_id, mensagem.destinatario_id]:
        return None, resposta_erro("Voce nao tem permissao para acessar esta mensagem", 403)

    return mensagem, None


def _mensagens_do_usuario():
    usuario_atual_id = obter_usuario_atual_id()
    return (
        Mensagem.query.filter(mensagem_visivel_para_usuario(usuario_atual_id))
        .order_by(Mensagem.criado_em.desc())
        .all()
    )


def _conversas_do_usuario():
    usuario_atual_id = obter_usuario_atual_id()
    conversas = {}
    for mensagem in _mensagens_do_usuario():
        outro_id = (
            mensagem.destinatario_id
            if mensagem.remetente_id == usuario_atual_id
            else mensagem.remetente_id
        )
        if outro_id not in conversas:
            usuario = db.session.get(Usuario, outro_id)
            conversas[outro_id] = {
                "usuario": usuario,
                "ultima_mensagem": mensagem,
                "nao_lidas": 0,
                "atualizado_em": mensagem.criado_em.isoformat() if mensagem.criado_em else None,
            }
        if mensagem.destinatario_id == usuario_atual_id and not mensagem.lida:
            conversas[outro_id]["nao_lidas"] += 1
    return list(conversas.values())


def _mensagens_com_usuario(usuario_id):
    usuario_atual_id = obter_usuario_atual_id()
    return (
        Mensagem.query.filter(
            db.or_(
                db.and_(
                    Mensagem.remetente_id == usuario_atual_id,
                    Mensagem.destinatario_id == usuario_id,
                    Mensagem.removida_pelo_remetente.is_(False),
                ),
                db.and_(
                    Mensagem.remetente_id == usuario_id,
                    Mensagem.destinatario_id == usuario_atual_id,
                    Mensagem.removida_pelo_destinatario.is_(False),
                ),
            )
        )
        .order_by(Mensagem.criado_em.asc())
        .all()
    )


def _renderizar_mensagens(usuario_id=None):
    conversas = _conversas_do_usuario()
    if usuario_id is None and conversas:
        usuario_id = conversas[0]["usuario"].id

    usuario_selecionado = db.session.get(Usuario, usuario_id) if usuario_id else None
    mensagens = []
    if usuario_selecionado:
        mensagens = _mensagens_com_usuario(usuario_selecionado.id)
        for mensagem in mensagens:
            if (
                mensagem.remetente_id == usuario_selecionado.id
                and mensagem.destinatario_id == obter_usuario_atual_id()
            ):
                mensagem.lida = True
        db.session.commit()

    contexto = _base_contexto()
    contexto.update(
        {
            "conversas": conversas,
            "mensagens": mensagens,
            "usuario_selecionado": usuario_selecionado,
            "usuarios": Usuario.query.filter(
                Usuario.id != obter_usuario_atual_id(),
                Usuario.ativo.is_(True),
            ).order_by(Usuario.nome.asc()).all(),
            "mostrar_nova_mensagem": request.args.get("nova") == "1",
        }
    )
    return render_template("mensagens/index.html", **contexto)


@bp.get("")
@exigir_login
def listar_conversas():
    if _prefer_html():
        return _renderizar_mensagens()

    conversas = []
    for conversa in _conversas_do_usuario():
        conversas.append(
            {
                "usuario": conversa["usuario"].to_dict() if conversa["usuario"] else None,
                "ultima_mensagem": conversa["ultima_mensagem"].to_dict(),
                "nao_lidas": conversa["nao_lidas"],
                "atualizado_em": conversa["atualizado_em"],
            }
        )
    return resposta_sucesso(dados=conversas)


@bp.get("/<int:usuario_id>")
@exigir_login
def listar_conversa(usuario_id):
    usuario_atual_id = obter_usuario_atual_id()
    if not db.session.get(Usuario, usuario_id):
        return resposta_erro("Usuario nao encontrado", 404)

    mensagens = _mensagens_com_usuario(usuario_id)

    for mensagem in mensagens:
        if mensagem.remetente_id == usuario_id and mensagem.destinatario_id == usuario_atual_id:
            mensagem.lida = True
    db.session.commit()

    if _prefer_html():
        return _renderizar_mensagens(usuario_id)

    return resposta_sucesso(dados=[mensagem.to_dict() for mensagem in mensagens])


@bp.post("")
@exigir_login
def enviar_mensagem():
    if request.form:
        data = {
            "destinatario_id": request.form.get("destinatario_id"),
            "conteudo": request.form.get("conteudo", "").strip(),
        }
    else:
        data, response = _payload()
        if response:
            return response

    faltando = [campo for campo in ["destinatario_id", "conteudo"] if not data.get(campo)]
    if faltando:
        return resposta_erro("Campos obrigatorios ausentes", 400, {"campos": faltando})

    destinatario_id = int(data["destinatario_id"])
    if destinatario_id == obter_usuario_atual_id():
        return resposta_erro("Nao e possivel enviar mensagem para voce mesmo", 400)
    if not db.session.get(Usuario, destinatario_id):
        return resposta_erro("Destinatario nao encontrado", 404)

    mensagem = Mensagem(
        remetente_id=obter_usuario_atual_id(),
        destinatario_id=destinatario_id,
        conteudo=data["conteudo"],
    )
    db.session.add(mensagem)
    db.session.commit()
    if _prefer_html():
        return redirect(url_for("mensagens.listar_conversa", usuario_id=destinatario_id))
    return resposta_sucesso("Mensagem enviada com sucesso", dados=mensagem.to_dict(), codigo_status=201)


@bp.patch("/<int:mensagem_id>/ler")
@exigir_login
def marcar_mensagem_como_lida(mensagem_id):
    mensagem, response = _get_mensagem_do_usuario(mensagem_id)
    if response:
        return response

    if mensagem.destinatario_id != obter_usuario_atual_id():
        return resposta_erro("Somente o destinatario pode marcar a mensagem como lida", 403)

    mensagem.lida = True
    db.session.commit()
    return resposta_sucesso("Mensagem marcada como lida", dados=mensagem.to_dict())


@bp.delete("/<int:mensagem_id>")
@exigir_login
def excluir_mensagem(mensagem_id):
    mensagem, response = _get_mensagem_do_usuario(mensagem_id)
    if response:
        return response

    usuario_atual_id = obter_usuario_atual_id()
    if mensagem.remetente_id == usuario_atual_id:
        mensagem.removida_pelo_remetente = True
    if mensagem.destinatario_id == usuario_atual_id:
        mensagem.removida_pelo_destinatario = True
    db.session.commit()
    return resposta_sucesso("Mensagem removida com sucesso")
