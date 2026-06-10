from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user

from unihub.ext.db import db
from unihub.forms import PerfilForm
from unihub.models import AgendaEvento, Evento, ForumResposta, ForumTopico, Notificacao, Usuario
from unihub.options import CURSOS, PERIODOS
from unihub.utils.responses import resposta_sucesso
from unihub.utils.view_helpers import iniciais


bp = Blueprint("main", __name__)


def _dashboard_contexto():
    usuario_id = current_user.id
    topicos = (
        ForumTopico.query.order_by(ForumTopico.criado_em.desc())
        .limit(3)
        .all()
    )
    eventos = (
        Evento.query.filter_by(status="ativo")
        .order_by(Evento.data_evento.asc())
        .limit(3)
        .all()
    )
    conexoes = (
        Usuario.query.filter(
            Usuario.id != usuario_id,
            Usuario.ativo.is_(True),
            Usuario.role != "admin",
        )
        .order_by(Usuario.nome.asc())
        .limit(2)
        .all()
    )
    eventos_agenda = (
        AgendaEvento.query.filter_by(usuario_id=usuario_id)
        .join(Evento)
        .order_by(Evento.data_evento.asc())
        .limit(3)
        .all()
    )
    return {
        "iniciais": iniciais,
        "topicos": topicos,
        "eventos": eventos,
        "eventos_agenda": [item.evento for item in eventos_agenda],
        "conexoes": conexoes,
        "notificacoes_count": Notificacao.query.filter_by(
            usuario_id=usuario_id,
            lida=False,
        ).count(),
    }


def _perfil_contexto():
    contexto = _dashboard_contexto()
    usuario_id = current_user.id
    topicos_usuario = ForumTopico.query.filter_by(autor_id=usuario_id).all()
    respostas_usuario = ForumResposta.query.filter_by(autor_id=usuario_id).all()
    eventos_salvos = AgendaEvento.query.filter_by(usuario_id=usuario_id).count()

    atividades = []
    topicos_recentes = sorted(
        topicos_usuario,
        key=lambda item: item.atualizado_em or item.criado_em,
        reverse=True,
    )[:2]
    for topico in topicos_recentes:
        atividades.append(
            (
                "pencil",
                "Criou ou atualizou o topico",
                topico.titulo,
                topico.atualizado_em.strftime("%d/%m/%Y %H:%M") if topico.atualizado_em else "",
                "bg-violet-50 text-violet-600",
            )
        )

    resposta_recente = (
        ForumResposta.query.filter_by(autor_id=usuario_id)
        .order_by(ForumResposta.atualizado_em.desc())
        .first()
    )
    if resposta_recente:
        atividades.append(
            (
                "messages-square",
                "Respondeu no forum",
                resposta_recente.topico.titulo if resposta_recente.topico else "Topico removido",
                resposta_recente.atualizado_em.strftime("%d/%m/%Y %H:%M") if resposta_recente.atualizado_em else "",
                "bg-blue-50 text-[#0B5FEA]",
            )
        )

    contexto.update(
        {
            "estatisticas": [
                ("clipboard-list", "Topicos criados", len(topicos_usuario), "bg-blue-50 text-[#0B5FEA]"),
                ("messages-square", "Respostas", len(respostas_usuario), "bg-emerald-50 text-emerald-600"),
                ("eye", "Visualizacoes recebidas", sum(topico.visualizacoes for topico in topicos_usuario), "bg-violet-50 text-violet-600"),
                ("calendar-check", "Eventos salvos", eventos_salvos, "bg-amber-50 text-amber-600"),
            ],
            "atividades": atividades,
            "redes": [
                ("instagram", "Instagram", current_user.instagram),
                ("linkedin", "LinkedIn", current_user.linkedin),
                ("message-circle-more", "WhatsApp", current_user.whatsapp),
            ],
        }
    )
    return contexto


@bp.get("/")
def index():
    return render_template("main/index.html")


@bp.get("/dashboard")
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.tela_login"))
    return render_template("main/home.html", **_dashboard_contexto())


@bp.get("/perfil")
def perfil():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.tela_login"))
    return render_template("main/perfil.html", **_perfil_contexto())


@bp.route("/perfil/editar", methods=["GET", "POST"])
def editar_perfil():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.tela_login"))

    form = PerfilForm(obj=current_user)
    contexto = _perfil_contexto()
    contexto["form"] = form
    contexto["cursos"] = [valor for valor, _ in CURSOS]
    contexto["periodos"] = [valor for valor, _ in PERIODOS]
    if request.method == "POST":
        if not form.validate_on_submit():
            contexto["erro"] = "Confira os dados do perfil e tente novamente."
            return render_template("main/perfil_editar.html", **contexto), 400

        email = form.email.data.strip()
        if email and Usuario.query.filter(Usuario.email == email, Usuario.id != current_user.id).first():
            contexto["erro"] = "Este e-mail ja esta em uso."
            return render_template("main/perfil_editar.html", **contexto), 400

        for campo in ["nome", "cidade", "bio", "instagram", "linkedin", "whatsapp"]:
            valor = getattr(form, campo).data
            if valor is not None:
                setattr(current_user, campo, valor.strip())

        current_user.curso = form.curso.data.strip()
        current_user.periodo = form.periodo.data.strip()

        if email:
            current_user.email = email

        db.session.commit()
        return redirect(url_for("main.perfil"))

    return render_template("main/perfil_editar.html", **contexto)


@bp.get("/configuracoes")
def configuracoes():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.tela_login"))
    return render_template("main/configuracoes.html", **_perfil_contexto())


@bp.get("/api")
def api_status():
    return resposta_sucesso(
        mensagem="API UniHub funcionando",
        dados={"message": "API UniHub funcionando"},
    )


@bp.get("/health")
def health():
    return resposta_sucesso(
        mensagem="Status OK",
        dados={"status": "ok", "app": "UniHub"},
    )
