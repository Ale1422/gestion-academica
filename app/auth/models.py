from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from app import db


class Rol(db.Model):
    __tablename__ = 'Roles'

    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50), nullable=False)
    permisos = db.Column(db.Text)

    usuarios = db.relationship('Usuario', back_populates='rol')

    def __repr__(self):
        return f'<Rol {self.nombre_rol}>'


class Persona(db.Model):
    """
    Datos personales compartidos por Alumnos, Docentes y cualquier
    Usuario del sistema (Secretaria, Preceptora, Administradores).
    Los modelos Alumno y Docente (a definir en sus propios módulos)
    tendrán id_persona como PK/FK contra esta tabla.
    """
    __tablename__ = 'Personas'

    id_persona = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(15), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    email = db.Column(db.String(100), unique=True)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(100))

    usuario = db.relationship('Usuario', back_populates='persona', uselist=False)
    # 'Alumno' y 'Docente' se definen en app/secretaria/models.py y
    # app/materias/models.py respectivamente. SQLAlchemy resuelve estas
    # referencias por nombre de clase, así que no hace falta importarlas
    # acá — solo que ambos módulos se carguen al iniciar la app (ya
    # ocurre porque cada blueprint importa sus modelos en routes.py).
    alumno = db.relationship('Alumno', back_populates='persona', uselist=False)
    docente = db.relationship('Docente', back_populates='persona', uselist=False)

    def __repr__(self):
        return f'<Persona {self.nombre} {self.apellido}>'

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'


class Usuario(UserMixin, db.Model):
    __tablename__ = 'Usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('Personas.id_persona'), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('Roles.id_rol'))
    estado = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    persona = db.relationship('Persona', back_populates='usuario')
    rol = db.relationship('Rol', back_populates='usuarios')
    logs_auditoria = db.relationship('LogAuditoria', back_populates='usuario')

    def __init__(self, username, id_persona, id_rol=None):
        self.username = username
        self.id_persona = id_persona
        self.id_rol = id_rol
        self.fecha_creacion = datetime.utcnow()

    def __repr__(self):
        return f'<Usuario {self.username}>'

    # Flask-Login usa por defecto self.id para get_id(); como la PK acá
    # se llama id_usuario, hay que sobreescribirlo explícitamente.
    def get_id(self):
        return str(self.id_usuario)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save(self):
        if not self.id_usuario:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id_usuario):
        return Usuario.query.get(id_usuario)

    def get_rol(self):
        return self.rol.nombre_rol if self.rol else None

    @staticmethod
    def get_by_username(username):
        return Usuario.query.filter_by(username=username, estado=True).first()

    @staticmethod
    def get_all():
        return Usuario.query.all()


class LogAuditoria(db.Model):
    """
    Registro de auditoría de acciones del sistema (módulo Seguridad y
    Gestión de Usuarios). Mapea la tabla LogsAuditoria del DDL
    (ModeloDatos.sql, sección 5).

    Convención de `accion` (no es ENUM en el DDL, es VARCHAR libre —
    se mantiene consistencia por convención de código, no por
    constraint de base):
        'ALTA'          - creación de un registro
        'MODIFICACION'  - edición de un registro existente
        'BAJA'          - eliminación de un registro
        'LOGIN'         - inicio de sesión exitoso
        'LOGOUT'        - cierre de sesión (extensión propia, no viene
                          de un ejemplo del DDL, pero es consistente)

    Decisión de diseño: NO se loguean los intentos de login fallidos,
    porque id_usuario es NOT NULL en el DDL y, antes de autenticar, no
    hay un Usuario válido para asociar la fila. Si en el futuro se
    quiere auditar también los fallos, hay que revisar el esquema
    (columna nullable, o una tabla separada para intentos fallidos).
    """
    __tablename__ = 'LogsAuditoria'

    id_log = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuarios.id_usuario'), nullable=False)
    accion = db.Column(db.String(100), nullable=False)
    entidad_afectada = db.Column(db.String(50))
    id_entidad_afectada = db.Column(db.Integer)
    detalle = db.Column(db.Text)
    fecha_hora = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    usuario = db.relationship('Usuario', back_populates='logs_auditoria')

    def __repr__(self):
        return f'<LogAuditoria {self.accion} {self.entidad_afectada}={self.id_entidad_afectada}>'

    @staticmethod
    def registrar(usuario, accion, entidad_afectada=None, id_entidad_afectada=None, detalle=None):
        """
        Crea y persiste una fila de auditoría.

        Hace su propio commit, SEPARADO de la transacción de negocio
        que originó la acción (ver nota de diseño en la respuesta que
        acompaña este archivo). Se llama siempre DESPUÉS de que el
        cambio de negocio ya se guardó con éxito.

        `usuario`: el Usuario autenticado que ejecutó la acción
        (típicamente current_user de Flask-Login).
        """
        log = LogAuditoria(
            id_usuario=usuario.id_usuario,
            accion=accion,
            entidad_afectada=entidad_afectada,
            id_entidad_afectada=id_entidad_afectada,
            detalle=detalle,
        )
        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def get_by_usuario(id_usuario):
        return LogAuditoria.query.filter_by(id_usuario=id_usuario).order_by(
            LogAuditoria.fecha_hora.desc()
        ).all()

    @staticmethod
    def get_recientes(limite=100):
        return LogAuditoria.query.order_by(LogAuditoria.fecha_hora.desc()).limit(limite).all()