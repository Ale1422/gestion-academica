# Estructura del proyecto

Este documento describe la organización de carpetas y archivos del proyecto, junto con una descripción de los módulos y rutas principales.

## Raíz del proyecto

- `.gitignore` - archivos y carpetas ignorados por Git.
- `README.md` - descripción general del proyecto y guía de uso.
- `requirements.txt` - dependencias de Python necesarias.
- `run.py` - punto de entrada para iniciar la aplicación Flask.
- `app/` - código principal de la aplicación Flask.
- `env/` - entorno virtual de Python (no se listan los archivos internos).

## app/

- `app/__init__.py` - configuración de la aplicación Flask, inicialización de extensiones (`LoginManager`, `SQLAlchemy`, `Migrate`) y registro de blueprints.
- `app/config.example.py` - plantilla de configuración con ejemplos de variables.
- `app/config.py` - configuración real de la aplicación cargada en `create_app()`.

### app/auth/

- `app/auth/__init__.py` - define el blueprint `auth_bp` para el módulo de autenticación.
- `app/auth/decorators.py` - lugar para decoradores personalizados de autenticación/autorización.
- `app/auth/forms.py` - formularios WTForms para `LoginForm` y `SignupForm`.
- `app/auth/models.py` - modelos SQLAlchemy `User` y `Rol` para usuarios, roles y datos relacionados.
- `app/auth/routes.py` - rutas de autenticación y gestión de usuarios:
  - `GET/POST /login` - formulario de inicio de sesión y autenticación.
  - `GET/POST /usuario/crear` - crear un nuevo usuario con rol.
  - `GET /usuario/listado` - mostrar listado de usuarios.
  - `POST /estadousuario/<int:usuario_id>` - cambiar estado activo/inactivo del usuario.
  - `GET /logout` - cerrar sesión del usuario.
- `app/auth/templates/auth/listadoUsuarios.html` - plantilla para mostrar el listado de usuarios.
- `app/auth/templates/auth/login_form.html` - plantilla del formulario de login.
- `app/auth/templates/auth/signup_form.html` - plantilla del formulario de registro de usuarios.

### app/direccion/

- `app/direccion/__init__.py` - define el blueprint `direccion_bp`.
- `app/direccion/routes.py` - ruta principal de `direccion`:
  - `GET /direccion` - muestra la página de dirección.
- `app/direccion/templates/direccion/index.html` - plantilla de la sección de dirección.

### app/errors/

- `app/errors/__init__.py` - define el blueprint `errors_bp`.
- `app/errors/handlers.py` - maneja errores HTTP:
  - `404 Not Found` - renderiza `errors/404.html`.
  - `500 Internal Server Error` - renderiza `errors/500.html`.
- `app/errors/templates/errors/404.html` - página de error 404.
- `app/errors/templates/errors/500.html` - página de error 500.

### app/materias/

- `app/materias/__init__.py` - define el blueprint `materia_bp`.
- `app/materias/routes.py` - ruta principal de materias.
- `app/materias/models.py` - modelo SQLAlchemy `Docente`.
- `app/materias/templates/materias/index.html` - plantilla de la sección de materias.

### app/preceptoria/

- `app/preceptoria/__init__.py` - define el blueprint `preceptoria_bp`.
- `app/preceptoria/routes.py` - ruta principal de preceptoría:
  - `GET /preceptoria` - muestra la página de preceptoría.
- `app/preceptoria/templates/preceptoria/index.html` - plantilla de la sección de preceptoría.

### app/public/

- `app/public/__init__.py` - define el blueprint `public_bp`.
- `app/public/routes.py` - ruta pública principal:
  - `GET /` - página de inicio pública.
- `app/public/templates/public/index.html` - plantilla de la página de inicio.

### app/secretaria/

- `app/secretaria/__init__.py` - define el blueprint `secretaria_bp`.
- `app/secretaria/routes.py` - ruta principal de secretaria:
  - `GET /secretaria` - muestra la página de secretaria.
- `app/secretaria/models.py` - modelo SQLAlchemy `Alumno`.
- `app/secretaria/templates/secretaria/index.html` - plantilla de la sección de secretaria.

### app/static/

- `app/static/base.css` - hoja de estilos CSS principal.
- `app/static/img/icono.png` - imagen de icono.
- `app/static/img/IconoIES-Photoroom.jpg` - imagen usada posiblemente en la interfaz.

### app/templates/

- `app/templates/500.html` - plantilla de error 500 de propósito general.
- `app/templates/base_template.html` - plantilla base compartida para otras vistas.
