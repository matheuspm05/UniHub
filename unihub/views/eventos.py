import calendar
from datetime import date, datetime

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from unihub.ext.db import db
from unihub.forms import EventoForm
from unihub.models import AgendaEvento, Evento, Usuario
from unihub.utils.auth import (
    usuario_atual_e_admin,
    usuario_atual_pode_moderar,
    resposta_proibida,
    exigir_login,
    exigir_moderador,
    obter_usuario_atual_id,
)
from unihub.utils.responses import resposta_erro, resposta_sucesso
from unihub.utils.security import safe_redirect_target
from unihub.utils.view_helpers import contexto_dashboard, iniciais, prefere_html


bp = Blueprint("eventos", __name__, url_prefix="/eventos")
agenda_bp = Blueprint("agenda", __name__)
EVENTO_IMAGEM_PADRAO = "imgs/eventos/foto padrao evento.png"
STATUS_EVENTO_VALIDOS = {"ativo", "cancelado", "encerrado", "desativado"}
MESES_PT_BR = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Marco",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


def _payload():
    data = request.get_json(silent=True)
    if not data:
        return None, resposta_erro("JSON vazio ou invalido", 400)
    return data, None


def _prefer_html():
    return prefere_html()


def _iniciais(nome):
    return iniciais(nome)


def _base_contexto():
    return contexto_dashboard()


def _missing_fields(data, fields):
    return [field for field in fields if data.get(field) in [None, ""]]


def _parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def _get_evento_or_404(evento_id):
    evento = db.session.get(Evento, evento_id)
    if not evento:
        return None, resposta_erro("Evento nao encontrado", 404)
    return evento, None


def _ids_eventos_salvos():
    if not current_user.is_authenticated:
        return set()
    return {
        evento_id
        for (evento_id,) in db.session.query(AgendaEvento.evento_id)
        .filter_by(usuario_id=obter_usuario_atual_id())
        .all()
    }


def _categorias_disponiveis():
    categorias = [
        categoria
        for (categoria,) in db.session.query(Evento.categoria)
        .filter(Evento.status != "desativado")
        .distinct()
        .order_by(Evento.categoria.asc())
        .all()
    ]
    padroes = ["Workshop", "Palestra", "Festa", "Extensao", "Monitoria", "Atletica", "Cultura"]
    return sorted(set(categorias + padroes))


def _locais_disponiveis():
    return [
        local
        for (local,) in db.session.query(Evento.local)
        .filter(Evento.status != "desativado")
        .distinct()
        .order_by(Evento.local.asc())
        .all()
    ]


def _pode_gerenciar_evento(evento):
    return evento.organizador_id == obter_usuario_atual_id() or usuario_atual_e_admin()


def _dados_evento_formulario(form):
    return {
        "titulo": form.titulo.data.strip(),
        "descricao": form.descricao.data.strip(),
        "categoria": form.categoria.data.strip(),
        "data_evento": form.data_evento.data.strip(),
        "horario": form.horario.data.strip(),
        "local": form.local.data.strip(),
        "status": form.status.data,
        "banner_url": form.banner_url.data.strip() if form.banner_url.data else None,
    }


def _criar_evento_com_dados(data):
    obrigatorios = ["titulo", "descricao", "categoria", "data_evento", "horario", "local"]
    faltando = _missing_fields(data, obrigatorios)
    if faltando:
        return None, resposta_erro("Campos obrigatorios ausentes", 400, {"campos": faltando})

    organizador_id = obter_usuario_atual_id()
    if not db.session.get(Usuario, organizador_id):
        return None, resposta_erro("Organizador nao encontrado", 404)

    try:
        data_evento = _parse_date(data["data_evento"])
    except ValueError:
        return None, resposta_erro("data_evento deve estar no formato YYYY-MM-DD", 400)

    status = data.get("status", "ativo")
    if status not in STATUS_EVENTO_VALIDOS:
        return None, resposta_erro("Status invalido", 400)

    evento = Evento(
        titulo=data["titulo"],
        descricao=data["descricao"],
        categoria=data["categoria"],
        data_evento=data_evento,
        horario=data["horario"],
        local=data["local"],
        status=status,
        banner_url=data.get("banner_url"),
        organizador_id=organizador_id,
    )
    db.session.add(evento)
    db.session.commit()
    return evento, None


def _atualizar_evento_com_dados(evento, data):
    if "status" in data and data["status"] not in STATUS_EVENTO_VALIDOS:
        return resposta_erro("Status invalido", 400)

    for campo in ["titulo", "descricao", "categoria", "horario", "local", "status", "banner_url"]:
        if campo in data:
            setattr(evento, campo, data[campo])

    if "data_evento" in data:
        try:
            evento.data_evento = _parse_date(data["data_evento"])
        except ValueError:
            return resposta_erro("data_evento deve estar no formato YYYY-MM-DD", 400)

    db.session.commit()
    return None


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

    ordenacao = request.args.get("ordenacao", "recentes")
    if ordenacao == "recentes":
        query = query.order_by(Evento.criado_em.desc())
    else:
        query = query.order_by(Evento.data_evento.asc())

    eventos = query.all()
    if _prefer_html():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.tela_login"))

        contexto = _base_contexto()
        contexto.update(
            {
                "eventos": eventos,
                "total_eventos": len(eventos),
                "eventos_salvos_ids": _ids_eventos_salvos(),
                "filtros": request.args,
                "imagem_padrao": EVENTO_IMAGEM_PADRAO,
                "categorias": _categorias_disponiveis(),
                "locais": _locais_disponiveis(),
                "usuario_pode_moderar": usuario_atual_pode_moderar(),
            }
        )
        return render_template("eventos/index.html", **contexto)

    return resposta_sucesso(dados=[evento.to_dict() for evento in eventos])


@bp.get("/<int:evento_id>")
def detalhar_evento(evento_id):
    evento, response = _get_evento_or_404(evento_id)
    if response:
        return response

    evento.visualizacoes += 1
    db.session.commit()

    if _prefer_html():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.tela_login"))

        contexto = _base_contexto()
        contexto.update(
            {
                "evento": evento,
                "imagem_padrao": EVENTO_IMAGEM_PADRAO,
                "evento_salvo": evento.id in _ids_eventos_salvos(),
                "usuario_pode_gerenciar": _pode_gerenciar_evento(evento),
            }
        )
        return render_template("eventos/detalhes.html", **contexto)

    return resposta_sucesso(dados=evento.to_dict())


@bp.post("")
@exigir_moderador
def criar_evento():
    data, response = _payload()
    if response:
        return response

    evento, response = _criar_evento_com_dados(data)
    if response:
        return response
    return resposta_sucesso("Evento criado com sucesso", dados=evento.to_dict(), codigo_status=201)


@bp.route("/criar", methods=["GET", "POST"])
@exigir_moderador
def criar_evento_html():
    form = EventoForm()
    if request.method == "POST":
        if not form.validate_on_submit():
            return _renderizar_formulario_evento("eventos/criar.html", form), 400

        evento, response = _criar_evento_com_dados(_dados_evento_formulario(form))
        if response:
            return response
        return redirect(url_for("eventos.detalhar_evento", evento_id=evento.id))

    return _renderizar_formulario_evento("eventos/criar.html", form)


def _renderizar_formulario_evento(template, form, evento=None):
    contexto = _base_contexto()
    contexto.update(
        {
            "form": form,
            "evento": evento,
            "categorias": _categorias_disponiveis(),
            "locais": _locais_disponiveis(),
        }
    )
    if evento:
        contexto["imagem_padrao"] = EVENTO_IMAGEM_PADRAO
    return render_template(template, **contexto)


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

    response = _atualizar_evento_com_dados(evento, data)
    if response:
        return response
    return resposta_sucesso("Evento atualizado com sucesso", dados=evento.to_dict())


@bp.route("/<int:evento_id>/editar", methods=["GET", "POST"])
@exigir_moderador
def editar_evento_html(evento_id):
    evento, response = _get_evento_or_404(evento_id)
    if response:
        return response
    if not _pode_gerenciar_evento(evento):
        return resposta_proibida("Somente o organizador ou um admin pode editar este evento")

    form = EventoForm(obj=evento)
    if request.method == "POST":
        if not form.validate_on_submit():
            return _renderizar_formulario_evento("eventos/editar.html", form, evento), 400

        response = _atualizar_evento_com_dados(evento, _dados_evento_formulario(form))
        if response:
            return response
        return redirect(url_for("eventos.detalhar_evento", evento_id=evento.id))

    return _renderizar_formulario_evento("eventos/editar.html", form, evento)


def _alterar_status_evento(evento_id, status, mensagem):
    evento, response = _get_evento_or_404(evento_id)
    if response:
        return response
    if not _pode_gerenciar_evento(evento):
        return resposta_proibida("Somente o organizador ou um admin pode alterar este evento")

    evento.status = status
    db.session.commit()
    if _prefer_html():
        destino = safe_redirect_target(
            request.form.get("next"),
            url_for("eventos.detalhar_evento", evento_id=evento.id),
        )
        return redirect(destino)
    return resposta_sucesso(mensagem, dados=evento.to_dict())


@bp.post("/<int:evento_id>/status")
@exigir_moderador
def alterar_status_evento_html(evento_id):
    status = request.form.get("status")
    if status not in STATUS_EVENTO_VALIDOS:
        return resposta_erro("Status invalido", 400)
    mensagens = {
        "ativo": "Evento ativado com sucesso",
        "cancelado": "Evento cancelado com sucesso",
        "encerrado": "Evento encerrado com sucesso",
        "desativado": "Evento desativado com sucesso",
    }
    return _alterar_status_evento(evento_id, status, mensagens[status])


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
        if _prefer_html():
            destino = safe_redirect_target(request.form.get("next"), url_for("agenda.listar_agenda"))
            return redirect(destino)
        return resposta_sucesso("Evento ja esta salvo na agenda")

    if _prefer_html():
        destino = safe_redirect_target(request.form.get("next"), url_for("agenda.listar_agenda"))
        return redirect(destino)

    return resposta_sucesso("Evento salvo na agenda", dados=agenda.to_dict(), codigo_status=201)


@bp.delete("/<int:evento_id>/remover-agenda")
@exigir_login
def remover_evento_agenda(evento_id):
    return _remover_evento_agenda(evento_id)


@bp.post("/<int:evento_id>/remover-agenda")
@exigir_login
def remover_evento_agenda_html(evento_id):
    return _remover_evento_agenda(evento_id)


def _remover_evento_agenda(evento_id):
    agenda = AgendaEvento.query.filter_by(
        usuario_id=obter_usuario_atual_id(),
        evento_id=evento_id,
    ).first()
    if not agenda:
        return resposta_erro("Evento nao esta salvo na agenda", 404)

    db.session.delete(agenda)
    db.session.commit()
    if _prefer_html():
        destino = safe_redirect_target(request.form.get("next"), url_for("agenda.listar_agenda"))
        return redirect(destino)
    return resposta_sucesso("Evento removido da agenda")


@bp.get("/meus-eventos")
@exigir_login
def meus_eventos():
    eventos = Evento.query.filter_by(
        organizador_id=obter_usuario_atual_id(),
    ).order_by(Evento.data_evento.asc()).all()
    if _prefer_html():
        if not usuario_atual_pode_moderar():
            return resposta_proibida("Somente moderadores podem gerenciar eventos")

        contexto = _base_contexto()
        contexto.update(
            {
                "eventos": eventos,
                "total_eventos": len(eventos),
                "imagem_padrao": EVENTO_IMAGEM_PADRAO,
            }
        )
        return render_template("eventos/meus_eventos.html", **contexto)

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
    if _prefer_html():
        contexto = _base_contexto()
        eventos = [item.evento for item in agenda]
        proximo = eventos[0] if eventos else None
        referencia = proximo.data_evento if proximo else date.today()
        semanas = calendar.Calendar(firstweekday=6).monthdatescalendar(
            referencia.year,
            referencia.month,
        )
        contexto.update(
            {
                "agenda": agenda,
                "eventos": eventos,
                "proximo_evento": proximo,
                "imagem_padrao": EVENTO_IMAGEM_PADRAO,
                "calendario_mes": f"{MESES_PT_BR[referencia.month]} {referencia.year}",
                "calendario_dias": ["D", "S", "T", "Q", "Q", "S", "S"],
                "calendario_semanas": semanas,
                "calendario_hoje": date.today(),
                "calendario_mes_numero": referencia.month,
                "calendario_eventos": {evento.data_evento for evento in eventos},
            }
        )
        return render_template("eventos/agenda.html", **contexto)

    return resposta_sucesso(dados=[item.to_dict() for item in agenda])
