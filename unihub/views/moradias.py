from decimal import Decimal, InvalidOperation

from flask import Blueprint, request

from unihub.ext.db import db
from unihub.models import Moradia, Usuario
from unihub.utils.auth import usuario_atual_pode_moderar, resposta_proibida, obter_usuario_atual_id
from unihub.utils.responses import resposta_erro, resposta_sucesso


bp = Blueprint("moradias", __name__, url_prefix="/moradias")


def _payload():
    data = request.get_json(silent=True)
    if not data:
        return None, resposta_erro("JSON vazio ou invalido", 400)
    return data, None


def _as_bool(value):
    if value is None:
        return None
    return str(value).lower() in ["1", "true", "sim", "yes"]


def _get_moradia_or_404(moradia_id):
    moradia = db.session.get(Moradia, moradia_id)
    if not moradia:
        return None, resposta_erro("Moradia nao encontrada", 404)
    return moradia, None


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
    return None


@bp.get("")
def listar_moradias():
    query = Moradia.query

    status = request.args.get("status")
    if status:
        query = query.filter(Moradia.status == status)
    else:
        query = query.filter(Moradia.status != "desativado")

    bairro = request.args.get("bairro")
    if bairro:
        query = query.filter(Moradia.bairro.ilike(f"%{bairro}%"))

    vagas = request.args.get("vagas")
    if vagas:
        query = query.filter(Moradia.numero_vagas >= int(vagas))

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
        return resposta_erro("preco_min e preco_max devem ser numeros validos", 400)

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

    moradias = query.order_by(Moradia.criado_em.desc()).all()
    return resposta_sucesso(dados=[moradia.to_dict() for moradia in moradias])


@bp.get("/<int:moradia_id>")
def detalhar_moradia(moradia_id):
    moradia, response = _get_moradia_or_404(moradia_id)
    if response:
        return response

    moradia.visualizacoes += 1
    db.session.commit()
    return resposta_sucesso(dados=moradia.to_dict())


@bp.post("")
def criar_moradia():
    data, response = _payload()
    if response:
        return response

    try:
        validation = _validar_moradia(data)
    except (InvalidOperation, ValueError):
        return resposta_erro("preco_mensal e numero_vagas devem ser validos", 400)
    if validation:
        return validation

    anunciante_id = data.get("anunciante_id") or obter_usuario_atual_id()
    if not db.session.get(Usuario, anunciante_id):
        return resposta_erro("Anunciante nao encontrado", 404)

    moradia = Moradia(
        titulo=data["titulo"],
        descricao=data["descricao"],
        bairro=data["bairro"],
        preco_mensal=data["preco_mensal"],
        numero_vagas=data["numero_vagas"],
        perto_uvv=bool(data.get("perto_uvv", False)),
        aceita_dividir_quarto=bool(data.get("aceita_dividir_quarto", False)),
        status=data.get("status", "disponivel"),
        imagem_url=data.get("imagem_url"),
        anunciante_id=anunciante_id,
    )
    db.session.add(moradia)
    db.session.commit()
    return resposta_sucesso("Anuncio criado com sucesso", dados=moradia.to_dict(), codigo_status=201)


@bp.put("/<int:moradia_id>")
def editar_moradia(moradia_id):
    moradia, response = _get_moradia_or_404(moradia_id)
    if response:
        return response
    if moradia.anunciante_id != obter_usuario_atual_id() and not usuario_atual_pode_moderar():
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

    for campo in [
        "titulo",
        "descricao",
        "bairro",
        "preco_mensal",
        "numero_vagas",
        "perto_uvv",
        "aceita_dividir_quarto",
        "status",
        "imagem_url",
    ]:
        if campo in data:
            setattr(moradia, campo, data[campo])

    db.session.commit()
    return resposta_sucesso("Anuncio atualizado com sucesso", dados=moradia.to_dict())


def _alterar_status_moradia(moradia_id, status, mensagem):
    moradia, response = _get_moradia_or_404(moradia_id)
    if response:
        return response
    if moradia.anunciante_id != obter_usuario_atual_id() and not usuario_atual_pode_moderar():
        return resposta_proibida("Somente o anunciante ou um moderador pode alterar este anuncio")

    moradia.status = status
    db.session.commit()
    return resposta_sucesso(mensagem, dados=moradia.to_dict())


@bp.patch("/<int:moradia_id>/pausar")
def pausar_moradia(moradia_id):
    return _alterar_status_moradia(moradia_id, "pausado", "Anuncio pausado com sucesso")


@bp.patch("/<int:moradia_id>/preencher")
def preencher_moradia(moradia_id):
    return _alterar_status_moradia(moradia_id, "preenchido", "Anuncio marcado como preenchido")


@bp.delete("/<int:moradia_id>")
def desativar_moradia(moradia_id):
    return _alterar_status_moradia(moradia_id, "desativado", "Anuncio desativado com sucesso")


@bp.get("/meus-anuncios")
def meus_anuncios():
    moradias = Moradia.query.filter_by(
        anunciante_id=obter_usuario_atual_id(),
    ).order_by(Moradia.criado_em.desc()).all()
    return resposta_sucesso(dados=[moradia.to_dict() for moradia in moradias])
