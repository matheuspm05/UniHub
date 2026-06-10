from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class PerfilForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    email = EmailField("E-mail", validators=[DataRequired(), Length(max=120)])
    curso = StringField("Curso", validators=[DataRequired(), Length(max=120)])
    periodo = StringField("Periodo", validators=[DataRequired(), Length(max=50)])
    cidade = StringField("Cidade", validators=[DataRequired(), Length(max=120)])
    bio = TextAreaField("Bio", validators=[Optional()])
