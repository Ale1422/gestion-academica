from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import login_manager, db
from . import auth_bp
from .forms import LoginForm, SignupForm
from .models import Usuario, Rol, Persona
from .decorators import admin_required


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    form = LoginForm()
    if form.validate_on_submit():
        # El login se hace con el email, que internamente se guarda
        # como username en la tabla Usuarios (ver Usuario.username).
        usuario = Usuario.get_by_username(form.email.data.upper())
        if usuario is not None and usuario.check_password(form.password.data):
            login_user(usuario, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                if usuario.get_rol().upper() == "ADMINISTRADOR":
                    next_page = url_for('direccion.index')
                else:
                    next_page = url_for('secretaria.index')
            return redirect(next_page)
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('auth/login_form.html', form=form)


@auth_bp.route("/usuario/crear", methods=["GET", "POST"])
@login_required
@admin_required
def crear():
    form = SignupForm()
    error = None
    usuarios = Usuario.get_all()
    form.rol.choices = [(rol.id_rol, rol.nombre_rol) for rol in Rol.query.all()]

    if form.validate_on_submit():
        nombre = form.name.data.upper()
        apellido = form.lastName.data.upper()
        email = form.email.data.upper()
        dni = form.dni.data
        password = form.password.data
        id_rol = form.rol.data

        # Persona.email y Persona.dni son UNIQUE: validamos antes de crear
        persona_existente = Persona.query.filter(
            (Persona.email == email) | (Persona.dni == dni)
        ).first()

        if persona_existente is not None:
            error = f'Ya existe una persona registrada con ese email o DNI.'
        else:
            persona = Persona(dni=dni, nombre=nombre, apellido=apellido, email=email)
            db.session.add(persona)
            db.session.commit()  # necesitamos persona.id_persona ya generado

            usuario = Usuario(username=email, id_persona=persona.id_persona, id_rol=id_rol)
            usuario.set_password(password)
            usuario.save()

            flash('Usuario creado correctamente.', 'success')
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('auth.listar')
            return redirect(next_page)

    return render_template("auth/signup_form.html", usuarios=usuarios, form=form, error=error)


@auth_bp.route("/usuario/listado", methods=["GET"])
@login_required
@admin_required
def listar():
    try:
        usuarios = Usuario.get_all()
        return render_template("auth/listadoUsuarios.html", usuarios=usuarios)
    except Exception:
        return redirect(url_for('public.index'))


@auth_bp.route('/estadousuario/<int:usuario_id>', methods=['POST'])
@login_required
@admin_required
def cambiar_estado(usuario_id):
    usuario = Usuario.get_by_id(usuario_id)
    nuevo_estado = request.json.get('estado')
    usuario.estado = bool(nuevo_estado)
    try:
        usuario.save()
        flash("El estado del usuario ha sido actualizado correctamente.", "success")
    except Exception:
        db.session.rollback()
        flash("Hubo un error al actualizar el estado.", "danger")

    next_page = request.args.get('next', None)
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('auth.listar')
    return redirect(next_page)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.index'))


@login_manager.user_loader
def load_user(user_id):
    return Usuario.get_by_id(int(user_id))
