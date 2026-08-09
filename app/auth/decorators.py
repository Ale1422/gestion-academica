# app/auth/decorators.py

from functools import wraps
from flask import abort
from flask_login import current_user


def rol_requerido(*roles_permitidos):
    """
    Decorador para restringir una vista a determinados roles.
    Uso:
        @secretaria_bp.route('/secretaria/alumno/crear')
        @login_required
        @rol_requerido('Secretaria', 'Administrador')
        def crear_alumno():
            ...

    Notas:
    - Requiere que @login_required (o equivalente) se ejecute antes,
      así current_user.is_authenticated ya está garantizado. Si se usa
      solo, igual chequea autenticación por seguridad, pero conviene
      mantener el orden explícito por legibilidad.
    - La comparación es case-insensitive (mismo criterio que ya usa
      base_template.html con current_user.get_rol().upper()), para no
      depender de que 'Secretaria' esté cargado con esa capitalización
      exacta en la tabla Roles.
    """
    roles_normalizados = {r.upper() for r in roles_permitidos}

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            rol_usuario = current_user.get_rol()
            if rol_usuario is None or rol_usuario.upper() not in roles_normalizados:
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """
    Atajo para el caso de uso más común del módulo de auth: solo el
    Administrador del Sistema puede gestionar usuarios (ver
    especificación, Módulo de Seguridad y Gestión de Usuarios).
    """
    return rol_requerido('Administrador')(f)