from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user

from unihub.ext.db import db
from unihub.models import Mensagem, Notificacao
from unihub.utils.auth import exigir_login, obter_usuario_atual_id
from unihub.utils.responses import resposta_erro, resposta_sucesso


bp = Blueprint("notificacoes", __name__, url_prefix="/notificacoes")


def _as_bool(value):
    if value is None:
        return None
    return str(value).lower() in ["1", "true", "sim", "yes"]


def _iniciais(nome):
    partes = [parte for parte in nome.split() if parte]
    if not partes:
        return "U"
    return "".join(parte[0].upper() for parte in partes[:2])


def _prefer_html():
    return request.accept_mimetypes.best_match(["text/html", "application/json"]) == "text/html"


def _base_contexto():
    usuario_id = obter_usuario_atual_id()
    return {
        "iniciais": _iniciais,
        "notificacoes_count": Notificacao.query.filter_by(
            usuario_id=usuario_id,
            lida=False,
        ).count(),
        "mensagens_count": Mensagem.query.filter_by(
            destinatario_id=usuario_id,
            lida=False,
        ).count(),
    }


def _notificacoes_demo():
    return [
        {
            "grupo": "Hoje",
            "itens": [
                ("message-circle", "Joao Pedro respondeu ao topico \"Duvida sobre Algoritmos de Ordenacao\"", "Ciencia da Computacao  •  Estruturas de Dados", "\"Acho que o Merge Sort e mais eficiente nesses casos...\"", "10:24", "bg-blue-50 text-[#0B5FEA]", True),
                ("thumbs-up", "Ana Clara curtiu seu comentario no topico \"Como organizar os estudos para as provas?\"", "Ciencia da Computacao  •  Dicas de Estudo", "", "09:15", "bg-emerald-50 text-emerald-600", True),
                ("at-sign", "Voce foi mencionado por Mariana Santos", "No topico \"Projeto Integrador - Entrega Final\"", "\"@Lucas Almeida poderia revisar a parte de banco de dados?\"", "08:47", "bg-violet-50 text-violet-600", True),
            ],
        },
        {
            "grupo": "Ontem",
            "itens": [
                ("calendar", "Novo evento proximo: Workshop: Git e GitHub", "Sabado, 24 de maio as 14:00", "Laboratorio de Informatica 2", "Ontem, 16:30", "bg-orange-50 text-orange-500", True),
                ("circle-check", "Seu topico \"Indicacao de grupo de estudos\" foi marcado como resolvido", "Ciencia da Computacao  •  Organizacao", "", "Ontem, 14:22", "bg-emerald-50 text-emerald-600", False),
                ("bookmark", "Voce salvou o topico \"Material de estudo para prova\"", "Ciencia da Computacao  •  Materiais", "", "Ontem, 11:08", "bg-violet-50 text-violet-600", False),
            ],
        },
        {
            "grupo": "Esta semana",
            "itens": [
                ("megaphone", "Aviso oficial publicado: Alteracao de data da prova", "Estruturas de Dados", "", "Terca, 20:10", "bg-red-50 text-red-500", False),
            ],
        },
    ]


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
                "notificacoes_demo": _notificacoes_demo(),
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
