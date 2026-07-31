from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required

from app import db
from app.secretaria import secretaria_bp
from app.secretaria.models import Alumno, Comision, Inscripcion  # Alumno: import pendiente, ver EstadoProyecto
from app.secretaria.forms import ComisionForm, InscripcionForm, AlumnoForm
from app.secretaria.validaciones import inscribir_alumno, ValidacionError
from app.auth.models import Persona


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

    form = InscripcionForm()
    if form.validate_on_submit():
        try:
            inscribir_alumno(id_alumno=form.id_alumno.data, id_comision=id_comision)
            flash('Alumno inscripto correctamente.', 'success')
            return redirect(url_for('secretaria_bp.ficha_comision', id_comision=id_comision))
        except ValidacionError as e:
            flash(str(e), 'danger')

    return render_template(
        'secretaria/inscripcion_form.html', form=form, comision=comision
    )