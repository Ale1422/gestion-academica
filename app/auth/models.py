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