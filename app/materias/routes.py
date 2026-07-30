from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required

from app import db
from . import materia_bp
from .models import Docente, Carrera, Materia, Correlatividad
from .forms import CarreraForm, MateriaForm, CorrelatividadForm


# ------------------------------------------------------------------
# Índice del módulo (ruta ya existente)
# ------------------------------------------------------------------
@materia_bp.route('/')
@login_required
def index():
    return render_template('materias/index.html')


# ------------------------------------------------------------------
# CARRERAS
# ------------------------------------------------------------------
@materia_bp.route('/carreras', methods=["GET"])
@login_required
def listado_carreras():
    carreras = Carrera.get_all()
    return render_template('materias/carreras_listado.html', carreras=carreras)


@materia_bp.route('/carreras/crear', methods=['GET', 'POST'])
@login_required
def crear_carrera():
    form = CarreraForm()
    if form.validate_on_submit():
        carrera = Carrera(
            nombre=form.nombre.data,
            duracion_anios=form.duracion_anios.data,
            codigo_plan=form.codigo_plan.data or None,
        )
        carrera.save()
        flash(f'Carrera "{carrera.nombre}" creada correctamente.', 'success')
        return redirect(url_for('materia_bp.listado_carreras'))
    return render_template(
        'materias/carrera_form.html', form=form, titulo='Nueva carrera'
    )


@materia_bp.route('/carreras/<int:id_carrera>/editar', methods=['GET', 'POST'])
@login_required
def editar_carrera(id_carrera):
    carrera = Carrera.get_by_id(id_carrera)
    if not carrera:
        flash('Carrera no encontrada.', 'danger')
        return redirect(url_for('materia_bp.listado_carreras'))

    form = CarreraForm(obj=carrera)
    if form.validate_on_submit():
        carrera.nombre = form.nombre.data
        carrera.duracion_anios = form.duracion_anios.data
        carrera.codigo_plan = form.codigo_plan.data or None
        carrera.save()
        flash(f'Carrera "{carrera.nombre}" actualizada.', 'success')
        return redirect(url_for('materia_bp.listado_carreras'))
    return render_template(
        'materias/carrera_form.html', form=form, titulo='Editar carrera'
    )


@materia_bp.route('/carreras/<int:id_carrera>/eliminar', methods=['POST'])
@login_required
def eliminar_carrera(id_carrera):
    carrera = Carrera.get_by_id(id_carrera)
    if not carrera:
        flash('Carrera no encontrada.', 'danger')
        return redirect(url_for('materia_bp.listado_carreras'))

    if carrera.materias:
        # Evitamos el delete en cascada silencioso: si tiene materias
        # cargadas, forzamos a que la secretaria las reasigne o borre
        # explícitamente primero.
        flash(
            f'No se puede eliminar "{carrera.nombre}": tiene '
            f'{len(carrera.materias)} materia(s) asociada(s).',
            'warning',
        )
        return redirect(url_for('materia_bp.listado_carreras'))

    carrera.delete()
    flash('Carrera eliminada.', 'success')
    return redirect(url_for('materia_bp.listado_carreras'))


# ------------------------------------------------------------------
# MATERIAS
# ------------------------------------------------------------------
@materia_bp.route('/materias')
@login_required
def listado_materias():
    id_carrera = request.args.get('id_carrera', type=int)
    if id_carrera:
        materias = Materia.get_by_carrera(id_carrera)
    else:
        materias = Materia.get_all()
    carreras = Carrera.get_all()
    return render_template(
        'materias/materias_listado.html',
        materias=materias,
        carreras=carreras,
        id_carrera_filtro=id_carrera,
    )


@materia_bp.route('/materias/crear', methods=['GET', 'POST'])
@login_required
def crear_materia():
    form = MateriaForm()
    form.id_carrera.choices = [
        (c.id_carrera, c.nombre) for c in Carrera.get_all()
    ]
    if not form.id_carrera.choices:
        flash('Primero tenés que crear al menos una carrera.', 'warning')
        return redirect(url_for('materia_bp.listado_carreras'))

    if form.validate_on_submit():
        materia = Materia(
            nombre=form.nombre.data,
            id_carrera=form.id_carrera.data,
            anio_sugerido=form.anio_sugerido.data,
            tipo_dictado=form.tipo_dictado.data,
            carga_horaria_total=form.carga_horaria_total.data,
            modalidad_aprobacion=form.modalidad_aprobacion.data,
        )
        materia.save()
        flash(f'Materia "{materia.nombre}" creada correctamente.', 'success')
        return redirect(url_for('materia_bp.listado_materias'))
    return render_template(
        'materias/materia_form.html', form=form, titulo='Nueva materia'
    )


@materia_bp.route('/materias/<int:id_materia>/editar', methods=['GET', 'POST'])
@login_required
def editar_materia(id_materia):
    materia = Materia.get_by_id(id_materia)
    if not materia:
        flash('Materia no encontrada.', 'danger')
        return redirect(url_for('materia_bp.listado_materias'))

    form = MateriaForm(obj=materia)
    form.id_carrera.choices = [
        (c.id_carrera, c.nombre) for c in Carrera.get_all()
    ]
    if form.validate_on_submit():
        materia.nombre = form.nombre.data
        materia.id_carrera = form.id_carrera.data
        materia.anio_sugerido = form.anio_sugerido.data
        materia.tipo_dictado = form.tipo_dictado.data
        materia.carga_horaria_total = form.carga_horaria_total.data
        materia.modalidad_aprobacion = form.modalidad_aprobacion.data
        materia.save()
        flash(f'Materia "{materia.nombre}" actualizada.', 'success')
        return redirect(url_for('materia_bp.listado_materias'))
    return render_template(
        'materias/materia_form.html', form=form, titulo='Editar materia'
    )


@materia_bp.route('/materias/<int:id_materia>/eliminar', methods=['POST'])
@login_required
def eliminar_materia(id_materia):
    materia = Materia.get_by_id(id_materia)
    if not materia:
        flash('Materia no encontrada.', 'danger')
        return redirect(url_for('materia_bp.listado_materias'))

    # OJO: si ya hay Comisiones/Inscripciones cargadas contra esta materia,
    # el DELETE va a fallar por la FK (Comisiones.id_materia no tiene
    # ON DELETE CASCADE en el DDL). Es el comportamiento correcto: no
    # queremos borrar en cascada el historial académico de un alumno.
    try:
        materia.delete()
        flash('Materia eliminada.', 'success')
    except Exception:
        db.session.rollback()
        flash(
            'No se pudo eliminar: la materia tiene comisiones, '
            'inscripciones o correlatividades asociadas.',
            'danger',
        )
    return redirect(url_for('materia_bp.listado_materias'))


# ------------------------------------------------------------------
# CORRELATIVIDADES
# ------------------------------------------------------------------
@materia_bp.route('/materias/<int:id_materia>/correlatividades', methods=['GET', 'POST'])
@login_required
def correlatividades(id_materia):
    materia = Materia.get_by_id(id_materia)
    if not materia:
        flash('Materia no encontrada.', 'danger')
        return redirect(url_for('materia_bp.listado_materias'))

    # Solo tiene sentido correlacionar contra materias de la MISMA carrera,
    # excluyendo a la propia materia.
    opciones = [
        (m.id_materia, m.nombre)
        for m in Materia.get_by_carrera(materia.id_carrera)
        if m.id_materia != materia.id_materia
    ]

    form = CorrelatividadForm()
    form.id_materia_requerida.choices = opciones

    if not opciones:
        flash(
            'No hay otras materias en esta carrera para definir '
            'correlatividades.',
            'info',
        )
    elif form.validate_on_submit():
        if Correlatividad.existe(
            materia.id_materia, form.id_materia_requerida.data, form.tipo_requisito.data
        ):
            flash('Esa correlatividad ya existe.', 'warning')
        else:
            correlativa = Correlatividad(
                id_materia=materia.id_materia,
                id_materia_requerida=form.id_materia_requerida.data,
                tipo_requisito=form.tipo_requisito.data,
            )
            correlativa.save()
            flash('Correlatividad agregada.', 'success')
        return redirect(url_for('materia_bp.correlatividades', id_materia=id_materia))

    correlatividades_actuales = Correlatividad.get_by_materia(id_materia)
    return render_template(
        'materias/correlatividades.html',
        materia=materia,
        form=form,
        correlatividades=correlatividades_actuales,
    )


@materia_bp.route(
    '/materias/<int:id_materia>/correlatividades/<int:id_materia_requerida>/'
    '<string:tipo_requisito>/eliminar',
    methods=['POST'],
)
@login_required
def eliminar_correlatividad(id_materia, id_materia_requerida, tipo_requisito):
    correlativa = Correlatividad.query.filter_by(
        id_materia=id_materia,
        id_materia_requerida=id_materia_requerida,
        tipo_requisito=tipo_requisito,
    ).first()
    if correlativa:
        correlativa.delete()
        flash('Correlatividad eliminada.', 'success')
    else:
        flash('Correlatividad no encontrada.', 'danger')
    return redirect(url_for('materia_bp.correlatividades', id_materia=id_materia))