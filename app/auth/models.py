from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime


from app import db

class Rol(db.Model):
    __tablename__ = 'Roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50), nullable=False)
    permisos = db.Column(db.Text)

    users = db.relationship('User', back_populates='rol_relacion')

class User(UserMixin,db.Model):

    __tablename__ = 'Usuarios'
    id = db.Column(db.Integer, primary_key=True, )
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Integer, db.ForeignKey('Roles.id'))
    fecha_creación = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    estado = db.Column(db.Enum('activo', 'inactivo'), default='activo')

    rol_relacion = db.relationship('Rol', back_populates='users')

    def __init__(self, nombre, apellido, email, rol):
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.rol = rol
        self.fecha_creación = datetime.now()

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        self.contraseña = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.contraseña, password)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return User.query.get(id)
    
    def get_rol(self):
        id = self.rol
        rol = Rol.query.get(id)
        return rol.nombre_rol

    @staticmethod
    def get_by_email(email):
        user = User.query.filter_by(email=email, estado='activo').first()
        return user
    @staticmethod
    def get_all():
        return User.query.all()