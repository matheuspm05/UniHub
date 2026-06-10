from flask_wtf import FlaskForm
from wtforms import EmailField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from unihub.options import CURSOS, PERIODOS


class PerfilForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    email = EmailField("E-mail", validators=[DataRequired(), Length(max=120)])
    curso = SelectField("Curso", choices=CURSOS, validators=[DataRequired()])
    periodo = SelectField("Periodo", choices=PERIODOS, validators=[DataRequired()])
    cidade = StringField("Cidade", validators=[DataRequired(), Length(max=120)])
    bio = TextAreaField("Bio", validators=[Optional(), Length(max=500)])
    instagram = StringField("Instagram", validators=[Optional(), Length(max=160)])
    linkedin = StringField("LinkedIn", validators=[Optional(), Length(max=160)])
    whatsapp = StringField("WhatsApp", validators=[Optional(), Length(max=160)])
