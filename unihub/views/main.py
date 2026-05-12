from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user

from unihub.ext.db import db
from unihub.models import Evento, ForumTopico, Mensagem, Notificacao, Usuario
from unihub.utils.responses import resposta_sucesso


bp = Blueprint("main", __name__)


def _iniciais(nome):
    partes = [parte for parte in nome.split() if parte]
    if not partes:
        return "U"
    return "".join(parte[0].upper() for parte in partes[:2])


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
        Usuario.query.filter(Usuario.id != usuario_id)
        .order_by(Usuario.nome.asc())
        .limit(2)
        .all()
    )
    notificacoes_count = Notificacao.query.filter_by(
        usuario_id=usuario_id,
        lida=False,
    ).count()
    mensagens_count = Mensagem.query.filter_by(
        destinatario_id=usuario_id,
        lida=False,
    ).count()

    return {
        "iniciais": _iniciais,
        "topicos": topicos,
        "eventos": eventos,
        "conexoes": conexoes,
        "notificacoes_count": notificacoes_count,
        "mensagens_count": mensagens_count,
        "agenda_aulas": [
            {
                "horario": "10:00\n12:00",
                "titulo": "Calculo I",
                "local": "Sala 203 - Bloco B",
                "cor": "bg-emerald-500",
            },
            {
                "horario": "14:00\n16:00",
                "titulo": "Estruturas de Dados",
                "local": "Sala 105 - Bloco A",
                "cor": "bg-blue-500",
            },
            {
                "horario": "19:00\n21:00",
                "titulo": "Projeto Integrador",
                "local": "Sala 301 - Bloco C",
                "cor": "bg-violet-500",
            },
        ],
    }


def _perfil_contexto():
    contexto = _dashboard_contexto()
    contexto.update(
        {
            "estatisticas": [
                ("clipboard-list", "Topicos criados", 8, "bg-blue-50 text-[#0B5FEA]"),
                ("messages-square", "Respostas", 24, "bg-emerald-50 text-emerald-600"),
                ("eye", "Visualizacoes recebidas", 156, "bg-violet-50 text-violet-600"),
                ("users", "Conexoes", 18, "bg-amber-50 text-amber-600"),
            ],
            "atividades": [
                ("messages-square", "Respondeu o topico", "Duvida sobre Algoritmos de Ordenacao", "ha 2h", "bg-blue-50 text-[#0B5FEA]"),
                ("pencil", "Criou o topico", "Indicacao de grupo de estudos", "ha 7h", "bg-violet-50 text-violet-600"),
                ("calendar", "Confirmou presenca no evento", "Workshop: Git e GitHub", "ontem", "bg-emerald-50 text-emerald-600"),
            ],
            "interesses": [
                "Inteligencia Artificial",
                "Desenvolvimento Web",
                "Algoritmos",
                "Banco de Dados",
                "UI/UX Design",
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

    contexto = _perfil_contexto()
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if email and Usuario.query.filter(Usuario.email == email, Usuario.id != current_user.id).first():
            contexto["erro"] = "Este e-mail ja esta em uso."
            return render_template("main/perfil_editar.html", **contexto), 400

        for campo in ["nome", "curso", "periodo", "cidade", "bio"]:
            valor = request.form.get(campo)
            if valor is not None:
                setattr(current_user, campo, valor.strip())

        if email:
            current_user.email = email

        db.session.commit()
        return redirect(url_for("main.perfil"))

    return render_template("main/perfil_editar.html", **contexto)


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
