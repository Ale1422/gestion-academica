from functools import wraps
from functools import wraps

from flask import abort
from flask_login import current_user


def role_required(*roles_permitidos):
    """
    Restringe el acceso a la ruta solo a usuarios logueados cuyo rol
    (Usuario.get_rol()) esté entre los indicados.

    Uso:
        @role_required('Administrador')
        @role_required('Administrador', 'Secretaria')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # no logueado -> Unauthorized

            rol_usuario = current_user.get_rol()
            roles_permitidos_upper = [r.upper() for r in roles_permitidos]

            if rol_usuario is None or rol_usuario.upper() not in roles_permitidos_upper:
                abort(403)  # logueado pero sin permiso -> Forbidden

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """
    Atajo para el caso de uso más común del módulo de auth: solo el
    Administrador del Sistema puede gestionar usuarios (ver
    especificación, Módulo de Seguridad y Gestión de Usuarios).
    """
    return role_required('Administrador')(f)