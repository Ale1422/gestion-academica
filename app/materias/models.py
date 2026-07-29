from app import db


class Docente(db.Model):
    """
    Extiende a Persona con los datos propios de un docente.
    id_persona es a la vez PK y FK, mismo patrón que Alumno y Usuario.
    """
    __tablename__ = 'Docentes'

    id_persona = db.Column(db.Integer, db.ForeignKey('Personas.id_persona'), primary_key=True)
    cuil = db.Column(db.String(15), unique=True, nullable=False)
    especialidad = db.Column(db.Text)
    fecha_ingreso = db.Column(db.Date)

    persona = db.relationship('Persona', back_populates='docente')

    def __repr__(self):
        return f'<Docente cuil={self.cuil}>'

    @property
    def nombre_completo(self):
        return self.persona.nombre_completo

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id_persona):
        return Docente.query.get(id_persona)

    @staticmethod
    def get_all():
        return Docente.query.all()