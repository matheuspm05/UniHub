from typing import Any, cast

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from unihub.ext.db import db
from unihub.forms import CadastroForm, LoginForm
from unihub.models import Usuario
from unihub.utils.auth import exigir_login
from unihub.utils.responses import resposta_erro, resposta_sucesso


bp = Blueprint("auth", __name__, url_prefix="/auth")


def _obter_json() -> dict[str, Any] | None:
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict) or not dados:
        return None
    return dados


def _campos_ausentes(dados: dict[str, Any], campos: list[str]):
    return [campo for campo in campos if dados.get(campo) in [None, ""]]


def _erro_senha(senha):
    if len(senha) < 8:
        return "A senha deve ter pelo menos 8 caracteres"
    if not any(char.isalpha() for char in senha) or not any(char.isdigit() for char in senha):
        return "A senha deve conter letras e numeros"
    return None


def _primeiro_erro(form, fallback):
    for erros in form.errors.values():
        if erros:
            return erros[0]
    return fallback


def _autenticar_usuario(email, senha):
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario or not usuario.verificar_senha(senha):
        return None, "Email ou senha invalidos.", 401
    if not usuario.ativo:
        return None, "Usuario desativado.", 403
    return usuario, None, None


@bp.post("/login")
def login():
    if not request.is_json:
        form = LoginForm()
        if not form.validate_on_submit():
            erro = _primeiro_erro(form, "Informe email e senha.")
            return render_template("auth/login.html", form=form, erro=erro), 400

        usuario, erro, status = _autenticar_usuario(form.email.data, form.senha.data)
        if erro:
            return render_template("auth/login.html", form=form, erro=erro), status

        login_user(usuario, remember=form.lembrar.data)
        return redirect(url_for("main.dashboard"))

    dados = _obter_json()
    if dados is None:
        return resposta_erro("JSON vazio ou invalido", 400)

    faltando = _campos_ausentes(dados, ["email", "senha"])
    if faltando:
        return resposta_erro("Campos obrigatorios ausentes", 400, {"campos": faltando})

    email = str(dados["email"])
    senha = str(dados["senha"])

    usuario, erro, status = _autenticar_usuario(email, senha)
    if erro:
        return resposta_erro(erro.rstrip("."), status)

    login_user(usuario, remember=bool(dados.get("lembrar", False)))
    return resposta_sucesso("Login realizado com sucesso", dados=usuario.to_dict())


@bp.get("/login")
def tela_login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("auth/login.html", form=LoginForm())


@bp.post("/logout")
@exigir_login
def logout():
    logout_user()
    if request.form.get("redirect_to_home"):
        return redirect(url_for("main.index"))
    return resposta_sucesso("Logout realizado com sucesso")


@bp.get("/me")
@exigir_login
def usuario_logado():
    usuario = cast(Usuario, current_user)
    return resposta_sucesso(dados=usuario.to_dict())


@bp.post("/cadastro")
def cadastrar_usuario():
    if not request.is_json:
        form = CadastroForm()
        if not form.validate_on_submit():
            erro = _primeiro_erro(form, "Preencha os dados obrigatorios.")
            return render_template("auth/cadastro.html", form=form, erro=erro), 400

        email = form.email.data
        if Usuario.query.filter_by(email=email).first():
            return render_template("auth/cadastro.html", form=form, erro="Email ja cadastrado."), 400

        usuario = _criar_usuario(
            {
                "nome": form.nome.data,
                "email": email,
                "senha": form.senha.data,
                "curso": form.curso.data,
                "periodo": form.periodo.data,
                "cidade": form.cidade.data,
                "bio": form.bio.data,
            }
        )
        login_user(usuario)
        return redirect(url_for("main.dashboard"))

    dados = _obter_json()
    if dados is None:
        return resposta_erro("JSON vazio ou invalido", 400)

    obrigatorios = ["nome", "email", "senha", "curso", "periodo", "cidade"]
    faltando = _campos_ausentes(dados, obrigatorios)
    if faltando:
        return resposta_erro("Campos obrigatorios ausentes", 400, {"campos": faltando})

    confirmacao_senha = dados.get("confirmacao_senha")
    if confirmacao_senha is not None and str(confirmacao_senha) != str(dados["senha"]):
        return resposta_erro("As senhas nao conferem", 400)

    senha = str(dados["senha"])
    erro_senha = _erro_senha(senha)
    if erro_senha:
        return resposta_erro(erro_senha, 400)

    email = str(dados["email"])
    if Usuario.query.filter_by(email=email).first():
        return resposta_erro("Email ja cadastrado", 400)

    usuario = _criar_usuario(dados)
    login_user(usuario)
    return resposta_sucesso("Usuario cadastrado com sucesso", dados=usuario.to_dict(), codigo_status=201)


@bp.get("/cadastro")
def tela_cadastro():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("auth/cadastro.html", form=CadastroForm())


def _criar_usuario(dados):
    usuario = Usuario()
    usuario.nome = str(dados["nome"])
    usuario.email = str(dados["email"])
    usuario.curso = str(dados["curso"])
    usuario.periodo = str(dados["periodo"])
    usuario.cidade = str(dados["cidade"])
    usuario.bio = str(dados["bio"]) if dados.get("bio") else None
    usuario.role = "usuario"
    usuario.selo = "Aluno"
    usuario.definir_senha(str(dados["senha"]))

    db.session.add(usuario)
    db.session.commit()
    return usuario
