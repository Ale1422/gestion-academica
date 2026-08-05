# app/calendario/forms.py

from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, SubmitField, DecimalField,
    HiddenField, BooleanField, FieldList, FormField
)
from wtforms.fields import DateTimeField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError

from app.materias.models import Materia


class EventoForm(FlaskForm):
    """
    Alta/edición de un Evento institucional genérico (jornada académica,
    acto, feriado, período de inscripciones). Para Mesas de Examen se
    usa MesaExamenForm, que crea el Evento y la Mesa juntos.
    """
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    descripcion = TextAreaField('Descripción', validators=[Optional()])
    fecha_inicio = DateTimeField(
        'Fecha y hora de inicio', format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()], render_kw={'type': 'datetime-local'}
    )
    fecha_fin = DateTimeField(
        'Fecha y hora de fin', format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()], render_kw={'type': 'datetime-local'}
    )
    tipo = SelectField(
        'Tipo de evento',
        choices=[
            ('Evento Académico', 'Evento Académico'),
            ('Feriado', 'Feriado'),
            ('Inscripciones', 'Inscripciones'),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField('Guardar', render_kw={'class': 'btn btn-primary'})

    def validate_fecha_fin(self, field):
        if self.fecha_inicio.data and field.data and field.data < self.fecha_inicio.data:
            raise ValidationError('La fecha de fin no puede ser anterior a la de inicio.')


class MesaExamenForm(FlaskForm):
    """
    Crea el Evento (tipo 'Examen', fijo) y la MesaExamen en un único
    formulario — no tiene sentido un Evento tipo Examen sin Mesa, ni una
    Mesa sin la fecha/hora que le da el Evento.
    """
    nombre = StringField(
        'Nombre del evento', validators=[Optional(), Length(max=100)],
        render_kw={'placeholder': 'Se autogenera si se deja vacío'}
    )
    descripcion = TextAreaField('Descripción', validators=[Optional()])
    fecha_inicio = DateTimeField(
        'Fecha y hora de inicio', format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()], render_kw={'type': 'datetime-local'}
    )
    fecha_fin = DateTimeField(
        'Fecha y hora de fin', format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()], render_kw={'type': 'datetime-local'}
    )
    id_materia = SelectField(
        'Materia', coerce=int, validators=[DataRequired()],
        render_kw={'class': 'form-control'}
    )
    llamado = SelectField(
        'Llamado',
        choices=[
            ('1er Llamado', '1er Llamado'),
            ('2do Llamado', '2do Llamado'),
            ('3er Llamado', '3er Llamado'),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField('Guardar', render_kw={'class': 'btn btn-primary'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtro de UI: solo materias con instancia de final. La
        # validación de negocio real está en
        # calendario/validaciones.py:validar_materia_habilitada_para_mesa
        self.id_materia.choices = [
            (m.id_materia, f'{m.nombre} ({m.carrera.nombre})')
            for m in Materia.query.filter(
                Materia.modalidad_aprobacion.in_(['Final', 'Ambas'])
            ).order_by(Materia.nombre).all()
        ]

    def validate_fecha_fin(self, field):
        if self.fecha_inicio.data and field.data and field.data < self.fecha_inicio.data:
            raise ValidationError('La fecha de fin no puede ser anterior a la de inicio.')


class InscripcionMesaFilaForm(FlaskForm):
    """Fila individual del lote de inscripción a una mesa."""
    id_alumno = HiddenField()
    seleccionado = BooleanField('Inscribir')

    class Meta:
        # Los subforms de un FieldList no llevan su propio CSRF token,
        # ya lo trae el form padre.
        csrf = False


class InscripcionMesaLoteForm(FlaskForm):
    filas = FieldList(FormField(InscripcionMesaFilaForm))
    submit = SubmitField('Inscribir seleccionados', render_kw={'class': 'btn btn-primary'})


class ResultadoEntryForm(FlaskForm):
    """Fila individual del lote de carga de resultados."""
    id_alumno = HiddenField()
    resultado = SelectField(
        'Resultado',
        choices=[
            ('Pendiente', 'Pendiente'),
            ('Aprobado', 'Aprobado'),
            ('Desaprobado', 'Desaprobado'),
            ('Ausente', 'Ausente'),
        ],
    )
    nota_final = DecimalField(
        'Nota', validators=[Optional(), NumberRange(min=0, max=10)], places=2
    )

    class Meta:
        csrf = False


class ResultadosMesaLoteForm(FlaskForm):
    filas = FieldList(FormField(ResultadoEntryForm))
    submit = SubmitField('Guardar resultados', render_kw={'class': 'btn btn-primary'})