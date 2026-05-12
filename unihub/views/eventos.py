from datetime import datetime

from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError

from unihub.ext.db import db
from unihub.models import AgendaEvento, Evento, Usuario
from unihub.utils.auth import (
    usuario_atual_e_admin,
    resposta_proibida,
    exigir_login,
    exigir_moderador,
    obter_usuario_atual_id,
)
from unihub.utils.responses import resposta_erro, resposta_sucesso


bp = Blueprint("eventos", __name__, url_prefix="/eventos")
agenda_bp = Blueprint("agenda", __name__)


def _payload():
    data = request.get_json(silent=True)
    if not data:
        return None, resposta_erro("JSON vazio ou invalido", 400)
    return data, None


def _missing_fields(data, fields):
    return [field for field in fields if data.get(field) in [None, ""]]


def _parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def _get_evento_or_404(evento_id):
    evento = db.session.get(Evento, evento_id)
    if not evento:
        return None, resposta_erro("Evento nao encontrado", 404)
    return evento, None


def _pode_gerenciar_evento(evento):
    return evento.organizador_id == obter_usuario_atual_id() or usuario_atual_e_admin()


@bp.get("")
def listar_eventos():
    query = Evento.query

    status = request.args.get("status")
    if status:
        query = query.filter(Evento.status == status)
    else:
        query = query.filter(Evento.status != "desativado")

    for campo in ["categoria", "local"]:
        valor = request.args.get(campo)
        if valor:
            query = query.filter(getattr(Evento, campo).ilike(f"%{valor}%"))

    busca = request.args.get("busca")
    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            db.or_(
                Evento.titulo.ilike(termo),
                Evento.descricao.ilike(termo),
                Evento.local.ilike(termo),
                Evento.categoria.ilike(termo),
            )
        )

    eventos = query.order_by(Evento.data_evento.asc()).all()
    return resposta_sucesso(dados=[evento.to_dict() for evento in eventos])


@bp.get("/<int:evento_id>")
def detalhar_evento(evento_id):
    evento, response = _get_evento_or_404(evento_id)
    if response:
        return response

    evento.visualizacoes += 1
    db.session.commit()
    return resposta_sucesso(dados=evento.to_dict())


@bp.post("")
@exigir_moderador
def criar_evento():
    data, response = _payload()
    if response:
        return response

    obrigatorios = ["titulo", "descricao", "categoria", "data_evento", "horario", "local"]
    faltando = _missing_fields(data, obrigatorios)
    if faltando:
        return resposta_erro("Campos obrigatorios ausentes", 400, {"campos": faltando})

    organizador_id = obter_usuario_atual_id()
    if not db.session.get(Usuario, organizador_id):
        return resposta_erro("Organizador nao encontrado", 404)

    try:
        data_evento = _parse_date(data["data_evento"])
    except ValueError:
        return resposta_erro("data_evento deve estar no formato YYYY-MM-DD", 400)

    evento = Evento(
        titulo=data["titulo"],
        descricao=data["descricao"],
        categoria=data["categoria"],
        data_evento=data_evento,
        horario=data["horario"],
        local=data["local"],
        status=data.get("status", "ativo"),
        banner_url=data.get("banner_url"),
        organizador_id=organizador_id,
    )
    db.session.add(evento)
    db.session.commit()
    return resposta_sucesso("Evento criado com sucesso", dados=evento.to_dict(), codigo_status=201)


@bp.put("/<int:evento_id>")
@exigir_moderador
def editar_evento(evento_id):
    evento, response = _get_evento_or_404(evento_id)
    if response:
        return response
    if not _pode_gerenciar_evento(evento):
        return resposta_proibida("Somente o organizador ou um admin pode editar este evento")

    data, response = _payload()
    if response:
        return response

    for campo in ["titulo", "descricao", "categoria", "horario", "local", "status", "banner_url"]:
        if campo in data:
            setattr(evento, campo, data[campo])

    if "data_evento" in data:
        try:
            evento.data_evento = _parse_date(data["data_evento"])
        except ValueError:
            return resposta_erro("data_evento deve estar no formato YYYY-MM-DD", 400)

    db.session.commit()
    return resposta_sucesso("Evento atualizado com sucesso", dados=evento.to_dict())


def _alterar_status_evento(evento_id, status, mensagem):
    evento, response = _get_evento_or_404(evento_id)
    if response:
        return response
    if not _pode_gerenciar_evento(evento):
        return resposta_proibida("Somente o organizador ou um admin pode alterar este evento")

    evento.status = status
    db.session.commit()
    return resposta_sucesso(mensagem, dados=evento.to_dict())


@bp.patch("/<int:evento_id>/cancelar")
@exigir_moderador
def cancelar_evento(evento_id):
    return _alterar_status_evento(evento_id, "cancelado", "Evento cancelado com sucesso")


@bp.patch("/<int:evento_id>/encerrar")
@exigir_moderador
def encerrar_evento(evento_id):
    return _alterar_status_evento(evento_id, "encerrado", "Evento encerrado com sucesso")


@bp.delete("/<int:evento_id>")
@exigir_moderador
def desativar_evento(evento_id):
    return _alterar_status_evento(evento_id, "desativado", "Evento desativado com sucesso")


@bp.post("/<int:evento_id>/salvar")
@exigir_login
def salvar_evento(evento_id):
    evento, response = _get_evento_or_404(evento_id)
    if response:
        return response

    agenda = AgendaEvento(usuario_id=obter_usuario_atual_id(), evento_id=evento.id)
    db.session.add(agenda)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return resposta_sucesso("Evento ja esta salvo na agenda")

    return resposta_sucesso("Evento salvo na agenda", dados=agenda.to_dict(), codigo_status=201)


@bp.delete("/<int:evento_id>/remover-agenda")
@exigir_login
def remover_evento_agenda(evento_id):
    agenda = AgendaEvento.query.filter_by(
        usuario_id=obter_usuario_atual_id(),
        evento_id=evento_id,
    ).first()
    if not agenda:
        return resposta_erro("Evento nao esta salvo na agenda", 404)

    db.session.delete(agenda)
    db.session.commit()
    return resposta_sucesso("Evento removido da agenda")


@bp.get("/meus-eventos")
@exigir_login
def meus_eventos():
    eventos = Evento.query.filter_by(
        organizador_id=obter_usuario_atual_id(),
    ).order_by(Evento.data_evento.asc()).all()
    return resposta_sucesso(dados=[evento.to_dict() for evento in eventos])


@agenda_bp.get("/agenda")
@exigir_login
def listar_agenda():
    agenda = (
        AgendaEvento.query.filter_by(usuario_id=obter_usuario_atual_id())
        .join(Evento)
        .order_by(Evento.data_evento.asc())
        .all()
    )
    return resposta_sucesso(dados=[item.to_dict() for item in agenda])
