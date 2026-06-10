from flask_wtf import FlaskForm
from wtforms import RadioField, SelectField, StringField, TextAreaField
from wtforms.validators import AnyOf, DataRequired, Length, Optional


class TopicoForm(FlaskForm):
    titulo = StringField("Titulo", validators=[DataRequired(), Length(max=180)])
    descricao = TextAreaField("Descricao", validators=[DataRequired()])
    curso = StringField("Curso", validators=[DataRequired(), Length(max=120)])
    disciplina = StringField("Disciplina", validators=[DataRequired(), Length(max=120)])
    categoria = StringField("Categoria", validators=[DataRequired(), Length(max=80)])
    tipo = RadioField(
        "Tipo",
        choices=[("topico", "Topico comum"), ("aviso", "Aviso oficial")],
        default="topico",
        validators=[Optional(), AnyOf(["topico", "aviso"])],
    )
    status = SelectField(
        "Status",
        choices=[
            ("aberto", "Aberto"),
            ("resolvido", "Resolvido"),
            ("fechado", "Fechado"),
            ("desativado", "Desativado"),
        ],
        default="aberto",
        validators=[Optional(), AnyOf(["aberto", "resolvido", "fechado", "desativado"])],
    )


class RespostaForm(FlaskForm):
    conteudo = TextAreaField("Resposta", validators=[DataRequired()])
