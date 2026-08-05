# app/materia/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, Email, ValidationError
from app.auth.models import Persona
from app.materias.models import Materia, Docente  


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
        render_kw={'class': 'form-control'},
    )
    anio_sugerido = IntegerField(
        'Año sugerido',
        validators=[DataRequired(), NumberRange(min=1, max=10)],
        render_kw={'class': 'form-control'},
    )
    tipo_dictado = SelectField(
        'Tipo de dictado',
        choices=[('Cuatrimestral', 'Cuatrimestral'), ('Anual', 'Anual')],
        render_kw={'class': 'form-control'},
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
        render_kw={'class': 'form-control'},
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
        render_kw={'class': 'form-control'},
    )
    tipo_requisito = SelectField(
        'Requisito',
        choices=[
            ('Para Cursar', 'Para Cursar'),
            ('Para Rendir Final', 'Para Rendir Final'),
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-control'},
    )
    submit = SubmitField('Agregar correlatividad', render_kw={'class': 'btn btn-primary'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_materia_requerida.choices = []

class DocenteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=50)],
                          render_kw={'class': 'form-control'})
    apellido = StringField('Apellido', validators=[DataRequired(), Length(max=50)],
                            render_kw={'class': 'form-control'})
    dni = StringField('DNI', validators=[DataRequired(), Length(max=15)],
                       render_kw={'class': 'form-control'})
    fecha_nacimiento = DateField('Fecha de nacimiento', validators=[Optional()],
                                  format='%Y-%m-%d', render_kw={'class': 'form-control'})
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)],
                         render_kw={'class': 'form-control'})
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=20)],
                            render_kw={'class': 'form-control'})
    direccion = StringField('Dirección', validators=[Optional(), Length(max=100)],
                             render_kw={'class': 'form-control'})
    cuil = StringField('CUIL', validators=[DataRequired(), Length(max=15)],
                        render_kw={'class': 'form-control', 'placeholder': '20-12345678-9'})
    especialidad = TextAreaField('Especialidad', validators=[Optional()],
                                  render_kw={'class': 'form-control', 'rows': 3})
    fecha_ingreso = DateField('Fecha de ingreso', validators=[Optional()],
                               format='%Y-%m-%d', render_kw={'class': 'form-control'})
    submit = SubmitField('Guardar', render_kw={'class': 'btn btn-primary'})

    def __init__(self, id_persona_actual=None, *args, **kwargs):
        """
        id_persona_actual: se pasa al editar, mismo patrón que AlumnoForm,
        para que las validaciones de unicidad ignoren el propio registro.
        """
        super().__init__(*args, **kwargs)
        self._id_persona_actual = id_persona_actual

    def validate_dni(self, field):
        persona = Persona.query.filter_by(dni=field.data).first()
        if persona and persona.id_persona != self._id_persona_actual:
            raise ValidationError('Ya existe una persona registrada con ese DNI.')

    def validate_email(self, field):
        if not field.data:
            return
        persona = Persona.query.filter_by(email=field.data).first()
        if persona and persona.id_persona != self._id_persona_actual:
            raise ValidationError('Ya existe una persona registrada con ese email.')

    def validate_cuil(self, field):
        docente = Docente.query.filter_by(cuil=field.data).first()
        if docente and docente.id_persona != self._id_persona_actual:
            raise ValidationError('Ya existe un docente con ese CUIL.')