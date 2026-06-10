from flask_wtf import FlaskForm
from wtforms import RadioField, SelectField, StringField, TextAreaField
from wtforms.validators import AnyOf, DataRequired, Length, Optional

from unihub.options import CURSOS, TOPICO_CATEGORIAS


class TopicoForm(FlaskForm):
    titulo = StringField("Titulo", validators=[DataRequired(), Length(max=180)])
    descricao = TextAreaField("Descricao", validators=[DataRequired()])
    curso = SelectField("Curso", choices=[("", "Selecione o curso"), *CURSOS], validators=[DataRequired()])
    categoria = SelectField(
        "Categoria",
        choices=[("", "Selecione a categoria"), *TOPICO_CATEGORIAS],
        validators=[DataRequired()],
    )
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
