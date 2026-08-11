# app/calendario/routes.py

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app import db
from app.calendario import calendario_bp
from app.calendario.models import Evento, MesaExamen, InscripcionMesa
from app.calendario.forms import (
    EventoForm, MesaExamenForm, InscripcionMesaLoteForm, ResultadosMesaLoteForm
)
from app.calendario.validaciones import (
    ValidacionError, validar_materia_habilitada_para_mesa,
    inscribir_alumno_mesa, registrar_resultado_mesa
)
from app.secretaria.models import Alumno
from app.materias.models import Materia
from app.auth.models import Persona, LogAuditoria
from app.auth.decorators import rol_requerido


@calendario_bp.route('/calendario')
def index():
    # Sin @login_required en el original: se deja así.
    eventos = Evento.get_proximos()
    return render_template('calendario/index.html', eventos=eventos)


# --- Eventos genéricos ---

@calendario_bp.route('/calendario/evento/crear', methods=['GET', 'POST'])
@login_required
@rol_requerido('Secretaria', 'Administrador')
def crear_evento():
    form = EventoForm()
    if form.validate_on_submit():
        evento = Evento(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            fecha_inicio=form.fecha_inicio.data,
            fecha_fin=form.fecha_fin.data,
            tipo=form.tipo.data,
        )
        evento.save()

        LogAuditoria.registrar(
            usuario=current_user,
            accion='ALTA',
            entidad_afectada='Eventos',
            id_entidad_afectada=evento.id_evento,
            detalle=f'Alta de evento "{evento.nombre}" ({evento.tipo})',
        )

        flash(f'Evento "{evento.nombre}" creado correctamente.', 'success')
        return redirect(url_for('calendario_bp.listado_eventos'))
    return render_template('calendario/evento_form.html', form=form, titulo='Nuevo evento')


@calendario_bp.route('/calendario/evento/editar/<int:id_evento>', methods=['GET', 'POST'])
@login_required
@rol_requerido('Secretaria', 'Administrador')
def editar_evento(id_evento):
    evento = Evento.get_by_id(id_evento)
    if evento is None or evento.tipo == 'Examen':
        # Las mesas de examen se editan desde su propia pantalla (no hay
        # ficha genérica de Evento para tipo 'Examen')
        flash('Evento no encontrado.', 'danger')
        return redirect(url_for('calendario_bp.listado_eventos'))

    form = EventoForm(obj=evento)
    if form.validate_on_submit():
        evento.nombre = form.nombre.data
        evento.descripcion = form.descripcion.data
        evento.fecha_inicio = form.fecha_inicio.data
        evento.fecha_fin = form.fecha_fin.data
        evento.tipo = form.tipo.data
        db.session.commit()

        LogAuditoria.registrar(
            usuario=current_user,
            accion='MODIFICACION',
            entidad_afectada='Eventos',
            id_entidad_afectada=evento.id_evento,
            detalle=f'Edición de evento "{evento.nombre}"',
        )

        flash(f'Evento "{evento.nombre}" actualizado.', 'success')
        return redirect(url_for('calendario_bp.listado_eventos'))

    return render_template(
        'calendario/evento_form.html', form=form, titulo='Editar evento', evento=evento
    )


@calendario_bp.route('/calendario/evento/listado')
@login_required
@rol_requerido('Secretaria', 'Preceptora', 'Administrador')
def listado_eventos():
    # Solo lectura: no se loguea. Preceptora tiene acceso de consulta.
    tipo_filtro = request.args.get('tipo', '')
    query = Evento.query
    if tipo_filtro:
        query = query.filter_by(tipo=tipo_filtro)
    eventos = query.order_by(Evento.fecha_inicio).all()
    return render_template(
        'calendario/listado_eventos.html', eventos=eventos, tipo_filtro=tipo_filtro,
        tipos=['Examen', 'Evento Académico', 'Feriado', 'Inscripciones'],
    )


@calendario_bp.route('/calendario/evento/eliminar/<int:id_evento>', methods=['POST'])
@login_required
@rol_requerido('Secretaria', 'Administrador')
def eliminar_evento(id_evento):
    evento = Evento.get_by_id(id_evento)
    if evento is None:
        flash('Evento no encontrado.', 'danger')
    else:
        id_evento_borrado = evento.id_evento
        nombre = evento.nombre
        evento.delete()  # cascade='all, delete-orphan' también borra la MesaExamen si es tipo Examen

        LogAuditoria.registrar(
            usuario=current_user,
            accion='BAJA',
            entidad_afectada='Eventos',
            id_entidad_afectada=id_evento_borrado,
            detalle=f'Baja de evento "{nombre}"',
        )

        flash(f'Evento "{nombre}" eliminado.', 'success')
    return redirect(url_for('calendario_bp.listado_eventos'))


# --- Mesas de examen ---

@calendario_bp.route('/calendario/mesa/crear', methods=['GET', 'POST'])
@login_required
@rol_requerido('Secretaria', 'Administrador')
def crear_mesa():
    form = MesaExamenForm()
    if form.validate_on_submit():
        materia = Materia.get_by_id(form.id_materia.data)
        try:
            validar_materia_habilitada_para_mesa(materia)
        except ValidacionError as e:
            flash(str(e), 'danger')
            return render_template(
                'calendario/mesa_form.html', form=form, titulo='Nueva mesa de examen'
            )

        nombre = form.nombre.data or f'Mesa de examen - {materia.nombre} - {form.llamado.data}'

        # Patrón ya establecido: primero el registro "padre" (Evento),
        # flush para obtener el id sin cerrar la transacción, después el
        # registro dependiente (MesaExamen) — igual que Persona->Alumno.
        evento = Evento(
            nombre=nombre,
            descripcion=form.descripcion.data,
            fecha_inicio=form.fecha_inicio.data,
            fecha_fin=form.fecha_fin.data,
            tipo='Examen',
        )
        db.session.add(evento)
        db.session.flush()

        mesa = MesaExamen(
            id_evento=evento.id_evento,
            id_materia=materia.id_materia,
            llamado=form.llamado.data,
        )
        db.session.add(mesa)
        db.session.commit()

        # Se loguea la MesaExamen como entidad principal de la acción
        # (el Evento que la acompaña queda referenciado en el detalle,
        # para no duplicar una fila de log por cada mitad de la alta).
        LogAuditoria.registrar(
            usuario=current_user,
            accion='ALTA',
            entidad_afectada='MesasExamen',
            id_entidad_afectada=mesa.id_mesa,
            detalle=(
                f'Alta de mesa de examen de "{materia.nombre}" '
                f'({form.llamado.data}, evento id={evento.id_evento})'
            ),
        )

        flash(f'Mesa de examen de "{materia.nombre}" creada correctamente.', 'success')
        return redirect(url_for('calendario_bp.ficha_mesa', id_mesa=mesa.id_mesa))

    return render_template('calendario/mesa_form.html', form=form, titulo='Nueva mesa de examen')


@calendario_bp.route('/calendario/mesa/listado')
@login_required
@rol_requerido('Secretaria', 'Preceptora', 'Administrador')
def listado_mesas():
    mesas = MesaExamen.get_all()
    return render_template('calendario/listado_mesas.html', mesas=mesas)


@calendario_bp.route('/calendario/mesa/<int:id_mesa>')
@login_required
@rol_requerido('Secretaria', 'Preceptora', 'Administrador')
def ficha_mesa(id_mesa):
    mesa = MesaExamen.get_by_id(id_mesa)
    if mesa is None:
        flash('La mesa de examen no existe.', 'warning')
        return redirect(url_for('calendario_bp.listado_mesas'))
    return render_template('calendario/ficha_mesa.html', mesa=mesa)


@calendario_bp.route('/calendario/mesa/<int:id_mesa>/inscribir', methods=['GET', 'POST'])
@login_required
@rol_requerido('Secretaria', 'Administrador')
def inscribir_alumnos_mesa(id_mesa):
    mesa = MesaExamen.get_by_id(id_mesa)
    if mesa is None:
        flash('La mesa de examen no existe.', 'warning')
        return redirect(url_for('calendario_bp.listado_mesas'))

    ya_inscriptos = {i.id_alumno for i in mesa.inscripciones}
    q = request.args.get('q', '').strip()

    query = Alumno.query.join(Persona)
    if q:
        like = f'%{q}%'
        query = query.filter(
            db.or_(
                Persona.apellido.ilike(like),
                Persona.nombre.ilike(like),
                Persona.dni.ilike(like),
                Alumno.legajo.ilike(like),
            )
        )
    candidatos = [
        a for a in query.order_by(Persona.apellido, Persona.nombre).all()
        if a.id_persona not in ya_inscriptos
    ]

    form = InscripcionMesaLoteForm()
    if request.method == 'GET':
        form.filas.entries = []
        for alumno in candidatos:
            form.filas.append_entry({'id_alumno': alumno.id_persona, 'seleccionado': False})

    if form.validate_on_submit():
        inscriptos_ok, errores = 0, []
        for fila in form.filas:
            if not fila.seleccionado.data:
                continue
            id_alumno = int(fila.id_alumno.data)
            try:
                inscribir_alumno_mesa(id_alumno=id_alumno, id_mesa=id_mesa)
                inscriptos_ok += 1
            except ValidacionError as e:
                alumno = Alumno.get_by_id(id_alumno)
                errores.append(f'{alumno.nombre_completo}: {e}')

        # Log resumen (no uno por alumno): inscribir_alumno_mesa() no
        # devuelve la InscripcionMesa creada, así que no tenemos un id
        # propio por fila sin tocar ese archivo — mismo criterio que
        # las altas en lote de Comisiones.
        if inscriptos_ok:
            LogAuditoria.registrar(
                usuario=current_user,
                accion='ALTA',
                entidad_afectada='InscripcionesMesa',
                id_entidad_afectada=id_mesa,
                detalle=f'{inscriptos_ok} alumno(s) inscripto(s) en mesa id={id_mesa}',
            )
            flash(f'{inscriptos_ok} alumno(s) inscripto(s) correctamente.', 'success')
        for err in errores:
            flash(err, 'danger')

        return redirect(url_for('calendario_bp.ficha_mesa', id_mesa=id_mesa))

    return render_template(
        'calendario/inscripcion_mesa_lote.html', form=form, mesa=mesa,
        candidatos=candidatos, q=q,
    )


@calendario_bp.route('/calendario/mesa/<int:id_mesa>/resultados', methods=['GET', 'POST'])
@login_required
@rol_requerido('Secretaria', 'Administrador')
def resultados_mesa(id_mesa):
    mesa = MesaExamen.get_by_id(id_mesa)
    if mesa is None:
        flash('La mesa de examen no existe.', 'warning')
        return redirect(url_for('calendario_bp.listado_mesas'))

    inscripciones = InscripcionMesa.get_by_mesa(id_mesa)
    form = ResultadosMesaLoteForm()

    if request.method == 'GET':
        form.filas.entries = []
        for insc in inscripciones:
            form.filas.append_entry({
                'id_alumno': insc.id_alumno,
                'resultado': insc.resultado,
                'nota_final': insc.nota_final,
            })

    if form.validate_on_submit():
        errores = []
        cargados = 0
        for fila in form.filas:
            id_alumno = int(fila.id_alumno.data)
            try:
                registrar_resultado_mesa(
                    id_mesa=id_mesa, id_alumno=id_alumno,
                    resultado=fila.resultado.data, nota_final=fila.nota_final.data,
                )
                cargados += 1
            except ValidacionError as e:
                alumno = Alumno.get_by_id(id_alumno)
                errores.append(f'{alumno.nombre_completo}: {e}')

        # Log resumen por mesa (mismo criterio que inscripción en lote).
        if cargados:
            LogAuditoria.registrar(
                usuario=current_user,
                accion='MODIFICACION',
                entidad_afectada='InscripcionesMesa',
                id_entidad_afectada=id_mesa,
                detalle=f'Resultados cargados para {cargados} alumno(s) en mesa id={id_mesa}',
            )

        if errores:
            for err in errores:
                flash(err, 'danger')
        else:
            flash('Resultados guardados correctamente.', 'success')
        return redirect(url_for('calendario_bp.ficha_mesa', id_mesa=id_mesa))

    return render_template(
        'calendario/resultados_mesa_lote.html', form=form, mesa=mesa, inscripciones=inscripciones,
    )