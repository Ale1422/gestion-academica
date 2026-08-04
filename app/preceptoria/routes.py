from datetime import date
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required

from app import db
from app.preceptoria import preceptoria_bp
from app.preceptoria.models import Asistencia
from app.preceptoria.forms import AsistenciaLoteForm
from app.secretaria.models import Comision, Alumno
from app.preceptoria.validaciones import (
    UMBRAL_ALERTA_INASISTENCIA, calcular_porcentaje_inasistencia,
)


@preceptoria_bp.route('/preceptoria')
def index():
    comisiones = Comision.get_all()
    return render_template('preceptoria/index.html', comisiones=comisiones)


@preceptoria_bp.route('/preceptoria/comision/<int:id_comision>/reporte')
@login_required
def reporte_asistencia(id_comision):
    comision = Comision.get_by_id(id_comision)
    if comision is None:
        flash('La comisión no existe.', 'warning')
        return redirect(url_for('preceptoria_bp.index'))

    inscripciones = [
        i for i in comision.inscripciones
        if i.estado_cursada not in ('Abandonada', 'Libre')
    ]

    filas = []
    for insc in inscripciones:
        asistencias = insc.asistencias
        porcentaje = calcular_porcentaje_inasistencia(asistencias)
        filas.append({
            'inscripcion': insc,
            'total_clases': len(asistencias),
            'porcentaje_inasistencia': porcentaje,
            'en_riesgo': porcentaje >= UMBRAL_ALERTA_INASISTENCIA,
        })

    # Alumnos con más inasistencias primero, para que la Preceptora vea
    # los casos de riesgo arriba de la tabla sin tener que ordenar a mano
    filas.sort(key=lambda f: f['porcentaje_inasistencia'], reverse=True)

    return render_template(
        'preceptoria/reporte_asistencia.html',
        comision=comision, filas=filas, umbral=UMBRAL_ALERTA_INASISTENCIA,
    )


@preceptoria_bp.route('/preceptoria/comision/<int:id_comision>/asistencia', methods=['GET', 'POST'])
@login_required
def registrar_asistencia(id_comision):
    comision = Comision.get_by_id(id_comision)
    if comision is None:
        flash('La comisión no existe.', 'warning')
        return redirect(url_for('preceptoria_bp.index'))

    # No tiene sentido tomar asistencia de alumnos libres o que abandonaron
    inscripciones = [
        i for i in comision.inscripciones
        if i.estado_cursada not in ('Abandonada', 'Libre')
    ]

    form = AsistenciaLoteForm()

    if request.method == 'GET':
        fecha_qs = request.args.get('fecha')
        form.fecha.data = date.fromisoformat(fecha_qs) if fecha_qs else date.today()

        existentes = {
            a.id_inscripcion: a.estado
            for a in Asistencia.get_by_comision_y_fecha(id_comision, form.fecha.data)
        }
        for insc in inscripciones:
            form.filas.append_entry({
                'id_inscripcion': insc.id_inscripcion,
                'estado': existentes.get(insc.id_inscripcion, 'Presente'),
            })

    if form.validate_on_submit():
        for fila in form.filas:
            Asistencia.registrar(
                id_inscripcion=int(fila.id_inscripcion.data),
                fecha=form.fecha.data,
                estado=fila.estado.data,
            )
        db.session.commit()
        flash(f'Asistencia del {form.fecha.data.strftime("%d/%m/%Y")} guardada.', 'success')
        return redirect(url_for(
            'preceptoria_bp.registrar_asistencia',
            id_comision=id_comision, fecha=form.fecha.data.isoformat()
        ))

    # Para el template: cada fila del FieldList emparejada con su Inscripcion
    filas_con_alumno = list(zip(form.filas, inscripciones))

    return render_template(
        'preceptoria/registro_asistencia.html',
        form=form, comision=comision, filas_con_alumno=filas_con_alumno,
    )


@preceptoria_bp.route('/preceptoria/alumno/<int:id_persona>/historial')
@login_required
def historial_asistencia(id_persona):
    alumno = Alumno.get_by_id(id_persona)
    if alumno is None:
        flash('Alumno no encontrado.', 'danger')
        return redirect(url_for('preceptoria_bp.index'))

    # Una fila de historial por cada Inscripcion (= por cada comisión
    # cursada), mismo criterio que el historial académico de alumno_ficha
    filas = []
    for insc in alumno.inscripciones:
        asistencias = sorted(insc.asistencias, key=lambda a: a.fecha)
        porcentaje = calcular_porcentaje_inasistencia(asistencias)
        filas.append({
            'inscripcion': insc,
            'asistencias': asistencias,
            'porcentaje_inasistencia': porcentaje,
            'en_riesgo': porcentaje >= UMBRAL_ALERTA_INASISTENCIA,
        })

    return render_template(
        'preceptoria/historial_asistencia.html',
        alumno=alumno, filas=filas, umbral=UMBRAL_ALERTA_INASISTENCIA,
    )