from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import login_manager
from . import auth_bp
from .forms import LoginForm, SignupForm
from .models import User, Rol

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data.upper())
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                if user.get_rol().upper() == "ADMINISTRADOR":
                    next_page = url_for('direccion.index')
                else:
                    next_page = url_for('secretaria.index')
            return redirect(next_page)
        else:
            print('No se encontro usuario')
    return render_template('auth/login_form.html', form=form)

@auth_bp.route("/usuario/crear", methods=["GET", "POST"])
@login_required
def crear():
    form = SignupForm()
    error = None
    usuarios = User.get_all()
    form.rol.choices = [(role.id, role.nombre_rol) for role in Rol.query.all()]
    if form.validate_on_submit():
        name = form.name.data.upper()
        lastName = form.lastName.data.upper()
        email = form.email.data.upper()
        password = form.password.data
        rol = form.rol.data
        # Comprobamos que no hay ya un usuario con ese email
        user = User.get_by_email(email)
        if user is not None:
            error = f'El email {email} ya está siendo utilizado por otro usuario'
        else:
            # Creamos el usuario y lo guardamos
            user = User(nombre = name, apellido = lastName, email = email, rol = rol)
            user.set_password(password)
            user.save()
            # Dejamos al usuario logueado
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('auth.listar')
            return redirect(next_page)
    return render_template("auth/signup_form.html", usuarios = usuarios, form=form, error=error)

@auth_bp.route("/usuario/listado", methods=["GET"])
@login_required
def listar():
    try:
        usuarios = User.get_all()
        return render_template("auth/listadoUsuarios.html", usuarios = usuarios)
    except:
        return redirect(url_for('public.index'))
    
@auth_bp.route('/estadousuario/<int:usuario_id>', methods = ['POST'])
@login_required
def cambiar_estado(usuario_id):
    user = User.get_by_id(usuario_id)
    estado = request.json.get('estado')
    user.estado = estado
    try:
        user.save()
        flash("El estado del usuario ha sido actualizado correctamente.", "success")
    except:
        user.rollback()
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
    return User.get_by_id(int(user_id))
