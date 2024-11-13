from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()],render_kw={"class": "form-control"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"class": "form-control"})
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Login',render_kw={"class": "btn btn-primary"})

class SignupForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=64)],render_kw={"class": "form-control"})
    lastName = StringField('Apellido', validators=[DataRequired(), Length(max=64)],render_kw={"class": "form-control"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"class": "form-control"})
    email = StringField('Email', validators=[DataRequired(), Email()],render_kw={"class": "form-control"})
    rol = SelectField('Rol', validators=[DataRequired()],render_kw={"class": "form-control"})
    submit = SubmitField('Registrar',render_kw={"class": "btn btn-primary"})