from decimal import Decimal, InvalidOperation

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user

from unihub.ext.db import db
from unihub.forms import MoradiaForm
from unihub.models import Moradia, Usuario
from unihub.utils.auth import (
    usuario_atual_pode_moderar,
    resposta_proibida,
    exigir_login,
    obter_usuario_atual_id,
)
from unihub.utils.responses import resposta_erro, resposta_sucesso
from unihub.utils.view_helpers import contexto_dashboard, prefere_html


bp = Blueprint("moradias", __name__, url_prefix="/moradias")
MORADIA_IMAGEM_PADRAO = "imgs/moradias/imagem padrao moradia.png"
STATUS_MORADIA_VALIDOS = {"disponivel", "pausado", "preenchido", "desativado"}


def _payload():
    data = request.get_json(silent=True)
    if not data:
        return None, resposta_erro("JSON vazio ou invalido", 400)
    return data, None


def _as_bool(value):
    if value is None:
        return None
    return str(value).lower() in ["1", "true", "sim", "yes"]


def _prefer_html():
    return prefere_html()


def _base_contexto():
    return contexto_dashboard()


def _bairros_disponiveis():
    bairros = [
        bairro
        for (bairro,) in db.session.query(Moradia.bairro)
        .filter(Moradia.status != "desativado")
        .distinct()
        .order_by(Moradia.bairro.asc())
        .all()
    ]
    bairros_padrao = ["Boa Vista", "Itapua", "Jardim da Penha", "Praia da Costa"]
    return sorted(set(bairros + bairros_padrao))


def _get_moradia_or_404(moradia_id):
    moradia = db.session.get(Moradia, moradia_id)
    if not moradia:
        return None, resposta_erro("Moradia nao encontrada", 404)
    return moradia, None


def _usuario_pode_gerenciar_moradia(moradia):
    return moradia.anunciante_id == obter_usuario_atual_id() or usuario_atual_pode_moderar()


def _validar_moradia(data, partial=False):
    obrigatorios = ["titulo", "descricao", "bairro", "preco_mensal", "numero_vagas"]
    if not partial:
        faltando = [field for field in obrigatorios if data.get(field) in [None, ""]]
        if faltando:
            return resposta_erro("Campos obrigatorios ausentes", 400, {"campos": faltando})

    if "preco_mensal" in data and Decimal(str(data["preco_mensal"])) < 0:
        return resposta_erro("preco_mensal nao pode ser negativo", 400)
    if "numero_vagas" in data and int(data["numero_vagas"]) < 1:
        return resposta_erro("numero_vagas deve ser maior ou igual a 1", 400)
    if "status" in data and data["status"] not in STATUS_MORADIA_VALIDOS:
        return resposta_erro("Status invalido", 400)
    return None


def _dados_formulario_moradia(form):
    data = {
        "titulo": form.titulo.data.strip(),
        "descricao": form.descricao.data.strip(),
        "bairro": form.bairro.data.strip(),
        "preco_mensal": form.preco_mensal.data.strip(),
        "numero_vagas": form.numero_vagas.data,
        "perto_uvv": form.perto_uvv.data,
        "aceita_dividir_quarto": form.aceita_dividir_quarto.data,
        "status": form.status.data,
        "contato_externo": form.contato_externo.data.strip() if form.contato_externo.data else None,
        "imagem_url": form.imagem_url.data.strip() if form.imagem_url.data else None,
    }
    if "preco_mensal" in data:
        data["preco_mensal"] = data["preco_mensal"].replace(".", "").replace(",", ".")
    return data


def _filtrar_moradias():
    query = Moradia.query

    status = request.args.get("status")
    if status:
        query = query.filter(Moradia.status == status)
    else:
        query = query.filter(Moradia.status != "desativado")

    bairro = request.args.get("bairro")
    if bairro:
        query = query.filter(Moradia.bairro.ilike(f"%{bairro}%"))

    try:
        vagas = request.args.get("vagas")
        if vagas:
            query = query.filter(Moradia.numero_vagas >= int(vagas))
    except ValueError:
        return None, resposta_erro("vagas deve ser um numero valido", 400)

    for campo in ["perto_uvv", "aceita_dividir_quarto"]:
        valor = _as_bool(request.args.get(campo))
        if valor is not None:
            query = query.filter(getattr(Moradia, campo) == valor)

    try:
        preco_min = request.args.get("preco_min")
        preco_max = request.args.get("preco_max")
        if preco_min:
            query = query.filter(Moradia.preco_mensal >= Decimal(preco_min))
        if preco_max:
            query = query.filter(Moradia.preco_mensal <= Decimal(preco_max))
    except InvalidOperation:
        return None, resposta_erro("preco_min e preco_max devem ser numeros validos", 400)

    busca = request.args.get("busca")
    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            db.or_(
                Moradia.titulo.ilike(termo),
                Moradia.descricao.ilike(termo),
                Moradia.bairro.ilike(termo),
            )
        )

    ordenacao = request.args.get("ordenacao", "recentes")
    if ordenacao == "menor_preco":
        query = query.order_by(Moradia.preco_mensal.asc())
    elif ordenacao == "maior_preco":
        query = query.order_by(Moradia.preco_mensal.desc())
    else:
        query = query.order_by(Moradia.criado_em.desc())

    return query, None


def _criar_moradia(data):
    try:
        validation = _validar_moradia(data)
    except (InvalidOperation, ValueError):
        return None, resposta_erro("preco_mensal e numero_vagas devem ser validos", 400)
    if validation:
        return None, validation

    anunciante_id = obter_usuario_atual_id()
    if not db.session.get(Usuario, anunciante_id):
        return None, resposta_erro("Anunciante nao encontrado", 404)

    moradia = Moradia(
        titulo=data["titulo"],
        descricao=data["descricao"],
        bairro=data["bairro"],
        preco_mensal=data["preco_mensal"],
        numero_vagas=data["numero_vagas"],
        perto_uvv=_as_bool(data.get("perto_uvv")) is True,
        aceita_dividir_quarto=_as_bool(data.get("aceita_dividir_quarto")) is True,
        status=data.get("status", "disponivel"),
        contato_externo=data.get("contato_externo") or None,
        imagem_url=data.get("imagem_url") or None,
        anunciante_id=anunciante_id,
    )
    db.session.add(moradia)
    db.session.commit()
    return moradia, None


def _atualizar_moradia(moradia, data):
    try:
        validation = _validar_moradia(data, partial=False)
    except (InvalidOperation, ValueError):
        return resposta_erro("preco_mensal e numero_vagas devem ser validos", 400)
    if validation:
        return validation

    for campo in ["titulo", "descricao", "bairro", "preco_mensal", "numero_vagas", "status", "contato_externo"]:
        if campo in data:
            setattr(moradia, campo, data[campo])

    for campo in ["perto_uvv", "aceita_dividir_quarto"]:
        if campo in data:
            setattr(moradia, campo, _as_bool(data[campo]) is True)

    if "imagem_url" in data:
        moradia.imagem_url = data.get("imagem_url") or None

    db.session.commit()
    return None


@bp.get("")
def listar_moradias():
    if _prefer_html():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.tela_login"))

        query, response = _filtrar_moradias()
        if response:
            return response

        contexto = _base_contexto()
        contexto.update(
            {
                "moradias": query.all(),
                "total_moradias": query.count(),
                "filtros": request.args,
                "bairros": _bairros_disponiveis(),
            }
        )
        return render_template("moradias/index.html", **contexto)

    query, response = _filtrar_moradias()
    if response:
        return response

    moradias = query.all()
    return resposta_sucesso(dados=[moradia.to_dict() for moradia in moradias])


@bp.route("/anunciar", methods=["GET", "POST"])
@exigir_login
def anunciar_moradia():
    form = MoradiaForm()
    contexto = _base_contexto()
    contexto.update(
        {
            "form": form,
            "bairros": _bairros_disponiveis(),
            "dados": request.form,
        }
    )

    if request.method == "POST":
        if not form.validate_on_submit():
            contexto["erro"] = "Confira os campos obrigatorios e tente novamente."
            return render_template("moradias/anunciar.html", **contexto), 400

        moradia, response = _criar_moradia(_dados_formulario_moradia(form))
        if response:
            contexto["erro"] = "Confira os campos obrigatorios e tente novamente."
            return render_template("moradias/anunciar.html", **contexto), 400

        return redirect(url_for("moradias.detalhar_moradia", moradia_id=moradia.id))

    return render_template("moradias/anunciar.html", **contexto)


@bp.get("/meus-anuncios")
@exigir_login
def meus_anuncios():
    moradias = Moradia.query.filter_by(
        anunciante_id=obter_usuario_atual_id(),
    ).order_by(Moradia.criado_em.desc()).all()

    if _prefer_html():
        contexto = _base_contexto()
        contexto.update(
            {
                "moradias": moradias,
                "imagem_padrao": MORADIA_IMAGEM_PADRAO,
                "ordenacao": request.args.get("ordenacao", "recentes"),
            }
        )
        return render_template("moradias/meus_anuncios.html", **contexto)

    return resposta_sucesso(dados=[moradia.to_dict() for moradia in moradias])


@bp.get("/<int:moradia_id>")
def detalhar_moradia(moradia_id):
    moradia, response = _get_moradia_or_404(moradia_id)
    if response:
        return response

    moradia.visualizacoes += 1
    db.session.commit()

    if _prefer_html():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.tela_login"))

        contexto = _base_contexto()
        contexto.update(
            {
                "moradia": moradia,
                "imagem_padrao": MORADIA_IMAGEM_PADRAO,
                "moradias_relacionadas": Moradia.query.filter(
                    Moradia.id != moradia.id,
                    Moradia.status != "desativado",
                )
                .order_by(Moradia.criado_em.desc())
                .limit(3)
                .all(),
            }
        )
        return render_template("moradias/detalhes.html", **contexto)

    return resposta_sucesso(dados=moradia.to_dict())


@bp.route("/<int:moradia_id>/editar", methods=["GET", "POST"])
@exigir_login
def editar_moradia_html(moradia_id):
    moradia, response = _get_moradia_or_404(moradia_id)
    if response:
        return response
    if not _usuario_pode_gerenciar_moradia(moradia):
        return resposta_proibida("Somente o anunciante ou um moderador pode editar este anuncio")

    form = MoradiaForm(obj=moradia)
    contexto = _base_contexto()
    contexto.update(
        {
            "form": form,
            "moradia": moradia,
            "bairros": _bairros_disponiveis(),
            "dados": request.form,
            "imagem_padrao": MORADIA_IMAGEM_PADRAO,
        }
    )

    if request.method == "POST":
        if not form.validate_on_submit():
            contexto["erro"] = "Confira os campos obrigatorios e tente novamente."
            return render_template("moradias/editar.html", **contexto), 400

        response = _atualizar_moradia(moradia, _dados_formulario_moradia(form))
        if response:
            contexto["erro"] = "Confira os campos obrigatorios e tente novamente."
            return render_template("moradias/editar.html", **contexto), 400

        return redirect(url_for("moradias.meus_anuncios"))

    return render_template("moradias/editar.html", **contexto)


@bp.post("/<int:moradia_id>/status")
@exigir_login
def alterar_status_moradia_html(moradia_id):
    status = request.form.get("status")
    if status not in STATUS_MORADIA_VALIDOS:
        return resposta_erro("Status invalido", 400)

    moradia, response = _get_moradia_or_404(moradia_id)
    if response:
        return response
    if not _usuario_pode_gerenciar_moradia(moradia):
        return resposta_proibida("Somente o anunciante ou um moderador pode alterar este anuncio")

    moradia.status = status
    db.session.commit()
    destino = request.form.get("redirect_to", "meus_anuncios")
    if destino == "editar":
        return redirect(url_for("moradias.editar_moradia_html", moradia_id=moradia.id))
    return redirect(url_for("moradias.meus_anuncios"))


@bp.post("")
@exigir_login
def criar_moradia():
    data, response = _payload()
    if response:
        return response

    moradia, response = _criar_moradia(data)
    if response:
        return response

    return resposta_sucesso("Anuncio criado com sucesso", dados=moradia.to_dict(), codigo_status=201)


@bp.put("/<int:moradia_id>")
@exigir_login
def editar_moradia(moradia_id):
    moradia, response = _get_moradia_or_404(moradia_id)
    if response:
        return response
    if not _usuario_pode_gerenciar_moradia(moradia):
        return resposta_proibida("Somente o anunciante ou um moderador pode editar este anuncio")

    data, response = _payload()
    if response:
        return response

    try:
        validation = _validar_moradia(data, partial=True)
    except (InvalidOperation, ValueError):
        return resposta_erro("preco_mensal e numero_vagas devem ser validos", 400)
    if validation:
        return validation

    for campo in ["titulo", "descricao", "bairro", "preco_mensal", "numero_vagas", "status", "contato_externo", "imagem_url"]:
        if campo in data:
            setattr(moradia, campo, data[campo])

    for campo in ["perto_uvv", "aceita_dividir_quarto"]:
        if campo in data:
            setattr(moradia, campo, _as_bool(data[campo]) is True)

    db.session.commit()
    return resposta_sucesso("Anuncio atualizado com sucesso", dados=moradia.to_dict())


def _alterar_status_moradia(moradia_id, status, mensagem):
    moradia, response = _get_moradia_or_404(moradia_id)
    if response:
        return response
    if not _usuario_pode_gerenciar_moradia(moradia):
        return resposta_proibida("Somente o anunciante ou um moderador pode alterar este anuncio")

    moradia.status = status
    db.session.commit()
    return resposta_sucesso(mensagem, dados=moradia.to_dict())


@bp.patch("/<int:moradia_id>/pausar")
@exigir_login
def pausar_moradia(moradia_id):
    return _alterar_status_moradia(moradia_id, "pausado", "Anuncio pausado com sucesso")


@bp.patch("/<int:moradia_id>/preencher")
@exigir_login
def preencher_moradia(moradia_id):
    return _alterar_status_moradia(moradia_id, "preenchido", "Anuncio marcado como preenchido")


@bp.delete("/<int:moradia_id>")
@exigir_login
def desativar_moradia(moradia_id):
    return _alterar_status_moradia(moradia_id, "desativado", "Anuncio desativado com sucesso")
