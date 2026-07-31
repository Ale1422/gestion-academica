# app/secretaria/forms.py

from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField, StringField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, NumberRange, Length, Optional, Email, ValidationError


from app.materias.models import Materia, Docente
from app.auth.models import Persona
from app.secretaria.models import Alumno


class ComisionForm(FlaskForm):
    id_materia = SelectField(
        'Materia', coerce=int, validators=[DataRequired()],
        render_kw={'class': 'form-control'}
    )
    id_docente = SelectField(
        'Docente', coerce=int, validators=[DataRequired()],
        render_kw={'class': 'form-control'}
    )
    ciclo_lectivo = IntegerField(
        'Ciclo lectivo', validators=[DataRequired(), NumberRange(min=2000, max=2100)],
        render_kw={'class': 'form-control'}
    )
    cuatrimestre = SelectField(
        'Cuatrimestre', choices=[('1', '1°'), ('2', '2°'), ('Anual', 'Anual')],
        validators=[DataRequired()], render_kw={'class': 'form-control'}
    )
    turno = SelectField(
        'Turno',
        choices=[('Mañana', 'Mañana'), ('Tarde', 'Tarde'), ('Noche', 'Noche')],
        validators=[DataRequired()], render_kw={'class': 'form-control'}
    )
    cupo_maximo = IntegerField(
        'Cupo máximo', validators=[DataRequired(), NumberRange(min=1, max=200)],
        default=30, render_kw={'class': 'form-control'}
    )
    submit = SubmitField('Guardar', render_kw={'class': 'btn btn-primary'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_materia.choices = [
            (m.id_materia, f'{m.nombre} ({m.carrera.nombre})') for m in Materia.get_all()
        ]
        self.id_docente.choices = [
            (d.id_persona, d.nombre_completo) for d in Docente.get_all()
        ]


class InscripcionForm(FlaskForm):
    id_alumno = SelectField(
        'Alumno', coerce=int, validators=[DataRequired()],
        render_kw={'class': 'form-control'}
    )
    submit = SubmitField('Inscribir', render_kw={'class': 'btn btn-primary'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # el import va acá adentro para evitar import circular con Alumno
        from app.secretaria.models import Alumno
        self.id_alumno.choices = [
            (a.id_persona, f'{a.legajo} - {a.nombre_completo}') for a in Alumno.get_all()
        ]

class AlumnoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=50)])
    apellido = StringField('Apellido', validators=[DataRequired(), Length(max=50)])
    dni = StringField('DNI', validators=[DataRequired(), Length(max=15)])
    fecha_nacimiento = DateField('Fecha de nacimiento', validators=[Optional()], format='%Y-%m-%d')
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    direccion = StringField('Dirección', validators=[Optional(), Length(max=100)])
    legajo = StringField('Legajo', validators=[DataRequired(), Length(max=20)])
    estado_academico = SelectField(
        'Estado académico',
        choices=[
            ('Regular', 'Regular'),
            ('Libre', 'Libre'),
            ('Egresado', 'Egresado'),
            ('Pasivo', 'Pasivo'),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField('Guardar')

    def __init__(self, id_persona_actual=None, *args, **kwargs):
        """
        id_persona_actual: se pasa al editar, para que las validaciones de
        unicidad (dni/email/legajo) ignoren el propio registro que se está
        editando. En alta (crear_alumno) queda en None.
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

    def validate_legajo(self, field):
        alumno = Alumno.query.filter_by(legajo=field.data).first()
        if alumno and alumno.id_persona != self._id_persona_actual:
            raise ValidationError('Ya existe un alumno con ese legajo.')