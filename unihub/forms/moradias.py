from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField
from wtforms.validators import AnyOf, DataRequired, Length, Optional


class MoradiaForm(FlaskForm):
    titulo = StringField("Titulo", validators=[DataRequired(), Length(max=180)])
    descricao = TextAreaField("Descricao", validators=[DataRequired(), Length(max=500)])
    bairro = StringField("Bairro", validators=[DataRequired(), Length(max=120)])
    preco_mensal = StringField("Preco mensal", validators=[DataRequired()])
    numero_vagas = SelectField(
        "Numero de vagas",
        choices=[("", "Selecione"), *[(str(numero), str(numero)) for numero in range(1, 6)]],
        validators=[DataRequired()],
    )
    perto_uvv = SelectField(
        "Perto da UVV",
        choices=[("", "Selecione"), ("true", "Sim"), ("false", "Nao")],
        validators=[DataRequired(), AnyOf(["true", "false"])],
    )
    aceita_dividir_quarto = SelectField(
        "Aceita dividir quarto",
        choices=[("", "Selecione"), ("true", "Sim"), ("false", "Nao")],
        validators=[DataRequired(), AnyOf(["true", "false"])],
    )
    status = SelectField(
        "Status",
        choices=[
            ("disponivel", "Disponivel"),
            ("pausado", "Pausado"),
            ("preenchido", "Preenchido"),
            ("desativado", "Desativado"),
        ],
        default="disponivel",
        validators=[DataRequired()],
    )
    imagem_url = StringField("Imagem", validators=[Optional(), Length(max=255)])
