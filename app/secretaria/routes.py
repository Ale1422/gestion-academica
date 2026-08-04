from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required

from datetime import date
from app import db
from app.secretaria import secretaria_bp
from app.secretaria.models import Alumno, Comision, Inscripcion, Nota
from app.secretaria.forms import ComisionForm, AlumnoForm, LoteComisionForm, InscripcionLoteForm, NotasLoteForm
from app.secretaria.validaciones import inscribir_alumno, registrar_nota, ValidacionError
from app.auth.models import Persona

from app.materias.models import Carrera, Materia, Docente 

# --- Comisiones ---

@secretaria_bp.route("/secretaria")
def index():
    return render_template("secretaria/index.html")

@secretaria_bp.route('/secretaria/alumno/crear', methods=['GET', 'POST'])
@login_required
def crear_alumno():
    form = AlumnoForm()
    if form.validate_on_submit():
        # Patrón ya establecido: Persona primero, después el registro
        # dependiente, en la misma transacción.
        persona = Persona(
            dni=form.dni.data,
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            fecha_nacimiento=form.fecha_nacimiento.data,
            email=form.email.data or None,
            telefono=form.telefono.data,
            direccion=form.direccion.data,
        )
        db.session.add(persona)
        db.session.flush()  # asigna persona.id_persona sin cerrar la transacción

        alumno = Alumno(
            id_persona=persona.id_persona,
            legajo=form.legajo.data,
            estado_academico=form.estado_academico.data,
        )
        db.session.add(alumno)
        db.session.commit()

        flash(f'Alumno {persona.nombre_completo} creado correctamente (legajo {alumno.legajo}).', 'success')
        return redirect(url_for('secretaria_bp.listado_alumnos'))

    return render_template('secretaria/alumno_form.html', form=form, titulo='Nuevo alumno')


@secretaria_bp.route('/secretaria/alumno/editar/<int:id_persona>', methods=['GET', 'POST'])
@login_required
def editar_alumno(id_persona):
    alumno = Alumno.get_by_id(id_persona)
    if alumno is None:
        flash('Alumno no encontrado.', 'danger')
        return redirect(url_for('secretaria_bp.listado_alumnos'))

    persona = alumno.persona
    form = AlumnoForm(id_persona_actual=id_persona)

    if request.method == 'GET':
        form.nombre.data = persona.nombre
        form.apellido.data = persona.apellido
        form.dni.data = persona.dni
        form.fecha_nacimiento.data = persona.fecha_nacimiento
        form.email.data = persona.email
        form.telefono.data = persona.telefono
        form.direccion.data = persona.direccion
        form.legajo.data = alumno.legajo
        form.estado_academico.data = alumno.estado_academico

    if form.validate_on_submit():
        persona.dni = form.dni.data
        persona.nombre = form.nombre.data
        persona.apellido = form.apellido.data
        persona.fecha_nacimiento = form.fecha_nacimiento.data
        persona.email = form.email.data or None
        persona.telefono = form.telefono.data
        persona.direccion = form.direccion.data

        alumno.legajo = form.legajo.data
        alumno.estado_academico = form.estado_academico.data

        db.session.commit()
        flash(f'Datos de {persona.nombre_completo} actualizados.', 'success')
        return redirect(url_for('secretaria_bp.listado_alumnos'))

    return render_template('secretaria/alumno_form.html', form=form, titulo='Editar alumno', alumno=alumno)


@secretaria_bp.route('/secretaria/alumno/listado')
@login_required
def listado_alumnos():
    q = request.args.get('q', '').strip()
    estado_filtro = request.args.get('estado_academico', '')

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
    if estado_filtro:
        query = query.filter(Alumno.estado_academico == estado_filtro)

    alumnos = query.order_by(Persona.apellido, Persona.nombre).all()

    return render_template(
        'secretaria/alumno_listado.html',
        alumnos=alumnos,
        q=q,
        estado_filtro=estado_filtro,
        estados=['Regular', 'Libre', 'Egresado', 'Pasivo'],
    )


@secretaria_bp.route('/secretaria/alumno/ficha/<int:id_persona>')
@login_required
def ficha_alumno(id_persona):
    alumno = Alumno.get_by_id(id_persona)
    if alumno is None:
        flash('Alumno no encontrado.', 'danger')
        return redirect(url_for('secretaria_bp.listado_alumnos'))

    return render_template('secretaria/alumno_ficha.html', alumno=alumno)

@secretaria_bp.route('/comision/crear', methods=['GET', 'POST'])
@login_required
def crear_comision():
    form = ComisionForm()
    if form.validate_on_submit():
        comision = Comision(
            id_materia=form.id_materia.data,
            id_docente=form.id_docente.data,
            ciclo_lectivo=form.ciclo_lectivo.data,
            cuatrimestre=form.cuatrimestre.data,
            turno=form.turno.data,
            cupo_maximo=form.cupo_maximo.data,
        )
        comision.save()
        flash('Comisión creada correctamente.', 'success')
        return redirect(url_for('secretaria_bp.listado_comisiones'))
    return render_template('secretaria/comision_form.html', form=form)


@secretaria_bp.route('/comision/listado')
@login_required
def listado_comisiones():
    comisiones = Comision.get_all()
    return render_template('secretaria/listado_comisiones.html', comisiones=comisiones)


@secretaria_bp.route('/comision/<int:id_comision>')
@login_required
def ficha_comision(id_comision):
    comision = Comision.get_by_id(id_comision)
    if comision is None:
        flash('La comisión no existe.', 'warning')
        return redirect(url_for('secretaria_bp.listado_comisiones'))
    return render_template('secretaria/ficha_comision.html', comision=comision)


# --- Inscripciones (pantalla separada) ---

@secretaria_bp.route('/comision/<int:id_comision>/inscribir', methods=['GET', 'POST'])
@login_required
def inscribir_alumno_comision(id_comision):
    comision = Comision.get_by_id(id_comision)
    if comision is None:
        flash('La comisión no existe.', 'warning')
        return redirect(url_for('secretaria_bp.listado_comisiones'))

    form = InscripcionLoteForm()

    if request.method == 'POST':
        if not form.validate_on_submit():
            flash('Token de seguridad inválido, reintentá.', 'danger')
            return redirect(url_for('secretaria_bp.inscribir_alumno_comision', id_comision=id_comision))

        ids_alumnos = request.form.getlist('alumnos[]', type=int)
        if not ids_alumnos:
            flash('No seleccionaste ningún alumno.', 'warning')
            return redirect(url_for('secretaria_bp.inscribir_alumno_comision', id_comision=id_comision))

        inscriptos = []
        rechazados = []
        for id_alumno in ids_alumnos:
            try:
                inscribir_alumno(id_alumno=id_alumno, id_comision=id_comision)
                alumno = Alumno.get_by_id(id_alumno)
                inscriptos.append(alumno.nombre_completo if alumno else str(id_alumno))
            except ValidacionError as e:
                alumno = Alumno.get_by_id(id_alumno)
                nombre = alumno.nombre_completo if alumno else str(id_alumno)
                rechazados.append(f'{nombre}: {e}')

        if inscriptos:
            flash(f'Se inscribieron {len(inscriptos)} alumnos: {", ".join(inscriptos)}.', 'success')
        if rechazados:
            flash('No se pudieron inscribir: ' + ' | '.join(rechazados), 'warning')

        return redirect(url_for('secretaria_bp.ficha_comision', id_comision=id_comision))

    # GET — listado de candidatos, excluyendo a los ya inscriptos
    q = request.args.get('q', '').strip()

    ya_inscriptos_ids = [i.id_alumno for i in comision.inscripciones]

    query = Alumno.query.join(Persona).filter(Alumno.id_persona.notin_(ya_inscriptos_ids or [0]))
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
    candidatos = query.order_by(Persona.apellido, Persona.nombre).all()

    return render_template(
        'secretaria/inscripcion_form.html',
        form=form, comision=comision, candidatos=candidatos, q=q,
    )

@secretaria_bp.route('/comision/crear_lote', methods=['GET', 'POST'])
@login_required
def crear_comisiones_lote():
    form = LoteComisionForm()

    if request.method == 'POST':
        if not form.validate_on_submit():
            flash('Token de seguridad inválido, reintentá.', 'danger')
            return redirect(url_for('secretaria_bp.crear_comisiones_lote'))

        ciclo_lectivo = request.form.get('ciclo_lectivo', type=int)
        cuatrimestre = request.form.get('cuatrimestre')
        turno = request.form.get('turno')
        cupo_maximo = request.form.get('cupo_maximo', type=int) or 30
        materias_ids = request.form.getlist('materias[]', type=int)

        if not materias_ids:
            flash('No seleccionaste ninguna materia.', 'warning')
            return redirect(url_for('secretaria_bp.crear_comisiones_lote'))

        creadas = 0
        omitidas = []
        for id_materia in materias_ids:
            id_docente = request.form.get(f'docente_{id_materia}', type=int)
            if not id_docente:
                materia = Materia.get_by_id(id_materia)
                omitidas.append(materia.nombre if materia else str(id_materia))
                continue
            db.session.add(Comision(
                id_materia=id_materia,
                id_docente=id_docente,
                ciclo_lectivo=ciclo_lectivo,
                cuatrimestre=cuatrimestre,
                turno=turno,
                cupo_maximo=cupo_maximo,
            ))
            creadas += 1

        db.session.commit()

        if creadas:
            flash(f'Se crearon {creadas} comisiones correctamente.', 'success')
        if omitidas:
            flash(f'Se omitieron (sin docente elegido): {", ".join(omitidas)}.', 'warning')

        return redirect(url_for('secretaria_bp.listado_comisiones'))

    # GET — paso 1 (filtro) y, si ya vienen los parámetros, paso 2 (tabla)
    carreras = Carrera.get_all()
    docentes = Docente.get_all()

    id_carrera = request.args.get('id_carrera', type=int)
    anio_sugerido = request.args.get('anio_sugerido', type=int)
    ciclo_lectivo = request.args.get('ciclo_lectivo', type=int)
    cuatrimestre = request.args.get('cuatrimestre', '')
    turno = request.args.get('turno', '')
    cupo_maximo = request.args.get('cupo_maximo', type=int) or 30

    materias = []
    if id_carrera and anio_sugerido:
        materias = Materia.query.filter_by(
            id_carrera=id_carrera, anio_sugerido=anio_sugerido
        ).order_by(Materia.nombre).all()

    return render_template(
        'secretaria/comision_lote_form.html',
        form=form,
        carreras=carreras,
        docentes=docentes,
        materias=materias,
        id_carrera=id_carrera,
        anio_sugerido=anio_sugerido,
        ciclo_lectivo=ciclo_lectivo,
        cuatrimestre=cuatrimestre,
        turno=turno,
        cupo_maximo=cupo_maximo,
    )

# --- Notas (carga en lote por comisión) ---

@secretaria_bp.route('/comision/<int:id_comision>/notas', methods=['GET', 'POST'])
@login_required
def cargar_notas_comision(id_comision):
    comision = Comision.get_by_id(id_comision)
    if comision is None:
        flash('La comisión no existe.', 'warning')
        return redirect(url_for('secretaria_bp.listado_comisiones'))

    inscripciones = sorted(
        comision.inscripciones,
        key=lambda i: (i.alumno.persona.apellido, i.alumno.persona.nombre)
    )

    form = NotasLoteForm()

    if request.method == 'GET':
        form.entradas.entries = []
        for insc in inscripciones:
            form.entradas.append_entry({'id_inscripcion': insc.id_inscripcion})

    if form.validate_on_submit():
        cargadas = 0
        errores = []
        for entrada in form.entradas:
            if not entrada.instancia.data or entrada.valor.data is None:
                continue  # fila vacía, se ignora
            id_insc = int(entrada.id_inscripcion.data)
            try:
                registrar_nota(
                    id_inscripcion=id_insc,
                    instancia=entrada.instancia.data,
                    valor=entrada.valor.data,
                    fecha=entrada.fecha.data or date.today(),
                )
                cargadas += 1
            except ValidacionError as e:
                insc = Inscripcion.get_by_id(id_insc)
                errores.append(f'{insc.alumno.nombre_completo}: {e}')

        if cargadas:
            flash(f'{cargadas} nota(s) cargada(s) correctamente.', 'success')
        for err in errores:
            flash(err, 'danger')

        return redirect(url_for('secretaria_bp.ficha_comision', id_comision=id_comision))

    filas = list(zip(inscripciones, form.entradas))

    return render_template(
        'secretaria/notas_comision_form.html',
        form=form, comision=comision, filas=filas
    )

