from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, PasswordField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, Optional, ValidationError

from unihub.options import CURSOS, PERIODOS


def _validar_senha(form, field):
    senha = field.data or ""
    if not any(char.isalpha() for char in senha) or not any(char.isdigit() for char in senha):
        raise ValidationError("A senha deve conter letras e numeros.")


class LoginForm(FlaskForm):
    email = EmailField(
        "E-mail",
        validators=[DataRequired(message="Informe o e-mail."), Length(max=120)],
    )
    senha = PasswordField("Senha", validators=[DataRequired(message="Informe a senha.")])
    lembrar = BooleanField("Lembrar-me")


class CadastroForm(FlaskForm):
    nome = StringField("Nome completo", validators=[DataRequired(), Length(max=120)])
    email = EmailField("E-mail", validators=[DataRequired(), Length(max=120)])
    curso = SelectField("Curso", choices=[("", "Selecione seu curso"), *CURSOS], validators=[DataRequired()])
    periodo = SelectField(
        "Periodo",
        choices=[("", "Selecione seu periodo"), *PERIODOS],
        validators=[DataRequired()],
    )
    cidade = StringField("Cidade", validators=[DataRequired(), Length(max=120)])
    senha = PasswordField(
        "Senha",
        validators=[DataRequired(), Length(min=8, message="A senha deve ter pelo menos 8 caracteres."), _validar_senha],
    )
    confirmacao_senha = PasswordField(
        "Confirmar senha",
        validators=[DataRequired(), EqualTo("senha", message="As senhas nao conferem.")],
    )
    bio = TextAreaField("Bio", validators=[Optional(), Length(max=500)])
