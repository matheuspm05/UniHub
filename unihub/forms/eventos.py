from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField
from wtforms.validators import AnyOf, DataRequired, Length, Optional


STATUS_EVENTO = ["ativo", "cancelado", "encerrado", "desativado"]


class EventoForm(FlaskForm):
    titulo = StringField("Titulo", validators=[DataRequired(), Length(max=180)])
    descricao = TextAreaField("Descricao", validators=[DataRequired()])
    categoria = StringField("Categoria", validators=[DataRequired(), Length(max=80)])
    data_evento = StringField("Data do evento", validators=[DataRequired()])
    horario = StringField("Horario", validators=[DataRequired(), Length(max=20)])
    local = StringField("Local", validators=[DataRequired(), Length(max=180)])
    status = SelectField(
        "Status",
        choices=[(status, status.capitalize()) for status in STATUS_EVENTO],
        default="ativo",
        validators=[DataRequired(), AnyOf(STATUS_EVENTO)],
    )
    banner_url = StringField("Banner", validators=[Optional(), Length(max=255)])
