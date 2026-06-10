from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField
from wtforms.validators import DataRequired, Length, NumberRange


class MensagemForm(FlaskForm):
    destinatario_id = IntegerField(
        "Destinatario",
        validators=[DataRequired(), NumberRange(min=1)],
    )
    conteudo = StringField("Mensagem", validators=[DataRequired(), Length(max=2000)])
