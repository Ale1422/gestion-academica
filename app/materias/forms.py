# app/materia/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


class CarreraForm(FlaskForm):
    nombre = StringField(
        'Nombre de la carrera',
        validators=[DataRequired(), Length(max=100)],
        render_kw={'class': 'form-control', 'placeholder': 'Tecnicatura en Informática'},
    )
    duracion_anios = IntegerField(
        'Duración (años)',
        validators=[DataRequired(), NumberRange(min=1, max=10)],
        render_kw={'class': 'form-control'},
    )
    codigo_plan = StringField(
        'Código de plan',
        validators=[Optional(), Length(max=20)],
        render_kw={'class': 'form-control', 'placeholder': 'Ej: TI-2024'},
    )
    submit = SubmitField('Guardar', render_kw={'class': 'btn btn-primary'})


class MateriaForm(FlaskForm):
    nombre = StringField(
        'Nombre de la materia',
        validators=[DataRequired(), Length(max=100)],
        render_kw={'class': 'form-control'},
    )
    id_carrera = SelectField(
        'Carrera',
        coerce=int,
        validators=[DataRequired()],
        render_kw={'class': 'form-select'},
    )
    anio_sugerido = IntegerField(
        'Año sugerido',
        validators=[DataRequired(), NumberRange(min=1, max=10)],
        render_kw={'class': 'form-control'},
    )
    tipo_dictado = SelectField(
        'Tipo de dictado',
        choices=[('Cuatrimestral', 'Cuatrimestral'), ('Anual', 'Anual')],
        render_kw={'class': 'form-select'},
    )
    carga_horaria_total = IntegerField(
        'Carga horaria total',
        validators=[Optional(), NumberRange(min=0)],
        render_kw={'class': 'form-control'},
    )
    modalidad_aprobacion = SelectField(
        'Modalidad de aprobación',
        choices=[
            ('Promocional', 'Promocional'),
            ('Final', 'Final'),
            ('Ambas', 'Ambas'),
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'},
    )
    submit = SubmitField('Guardar', render_kw={'class': 'btn btn-primary'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Las choices de id_carrera se completan en la vista (routes.py)
        # con Carrera.get_all(), porque dependen de datos en la DB.
        self.id_carrera.choices = []


class CorrelatividadForm(FlaskForm):
    id_materia_requerida = SelectField(
        'Materia requerida',
        coerce=int,
        validators=[DataRequired()],
        render_kw={'class': 'form-select'},
    )
    tipo_requisito = SelectField(
        'Requisito',
        choices=[
            ('Para Cursar', 'Para Cursar'),
            ('Para Rendir Final', 'Para Rendir Final'),
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'},
    )
    submit = SubmitField('Agregar correlatividad', render_kw={'class': 'btn btn-primary'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_materia_requerida.choices = []