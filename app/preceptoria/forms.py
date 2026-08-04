from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, FieldList, FormField, HiddenField, SubmitField
from wtforms.validators import DataRequired


class AsistenciaFilaForm(FlaskForm):
    class Meta:
        csrf = False  # el CSRF token va una sola vez, en el form padre

    id_inscripcion = HiddenField()
    estado = SelectField(
        choices=[('Presente', 'Presente'), ('Ausente', 'Ausente'), ('Justificado', 'Justificado')],
        default='Presente',
        render_kw={'class': 'form-control form-control-sm'},
    )


class AsistenciaLoteForm(FlaskForm):
    fecha = DateField('Fecha', validators=[DataRequired()], format='%Y-%m-%d',
                       render_kw={'class': 'form-control'})
    filas = FieldList(FormField(AsistenciaFilaForm))
    submit = SubmitField('Guardar asistencia', render_kw={'class': 'btn btn-primary'})