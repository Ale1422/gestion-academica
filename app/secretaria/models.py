from app import db


class Alumno(db.Model):
    """
    Extiende a Persona con los datos propios de un alumno.
    id_persona es a la vez PK y FK: un Alumno siempre parte de una
    Persona ya existente (patrón compartido con Usuario y Docente).
    """
    __tablename__ = 'Alumnos'

    id_persona = db.Column(db.Integer, db.ForeignKey('Personas.id_persona'), primary_key=True)
    legajo = db.Column(db.String(20), unique=True, nullable=False)
    estado_academico = db.Column(
        db.Enum('Regular', 'Libre', 'Egresado', 'Pasivo'),
        default='Regular'
    )

    persona = db.relationship('Persona', back_populates='alumno')

    def __repr__(self):
        return f'<Alumno legajo={self.legajo}>'

    @property
    def nombre_completo(self):
        return self.persona.nombre_completo

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id_persona):
        return Alumno.query.get(id_persona)

    @staticmethod
    def get_by_legajo(legajo):
        return Alumno.query.filter_by(legajo=legajo).first()

    @staticmethod
    def get_all():
        return Alumno.query.all()