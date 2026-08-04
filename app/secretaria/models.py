from app import db
from datetime import datetime


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
    inscripciones = db.relationship('Inscripcion', back_populates='alumno')

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

class Comision(db.Model):
    """
    La puesta en marcha de una Materia en un ciclo lectivo/turno
    concreto, a cargo de un Docente. Ver gestion_academica_pro.sql
    sección 3.
    """
    __tablename__ = 'Comisiones'

    id_comision = db.Column(db.Integer, primary_key=True)
    id_materia = db.Column(db.Integer, db.ForeignKey('Materias.id_materia'), nullable=False)
    id_docente = db.Column(db.Integer, db.ForeignKey('Docentes.id_persona'), nullable=False)
    ciclo_lectivo = db.Column(db.Integer, nullable=False)  # YEAR en el DDL
    cuatrimestre = db.Column(db.Enum('1', '2', 'Anual'), nullable=False)
    turno = db.Column(db.Enum('Mañana', 'Tarde', 'Noche'), nullable=False)
    cupo_maximo = db.Column(db.Integer, default=30)

    materia = db.relationship('Materia', back_populates='comisiones')
    docente = db.relationship('Docente', back_populates='comisiones')
    inscripciones = db.relationship(
        'Inscripcion', back_populates='comision', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Comision materia={self.id_materia} {self.ciclo_lectivo}-{self.cuatrimestre}>'

    @property
    def cupos_disponibles(self):
        ocupados = Inscripcion.query.filter(
            Inscripcion.id_comision == self.id_comision,
            Inscripcion.estado_cursada.notin_(['Abandonada', 'Libre'])
        ).count()
        return self.cupo_maximo - ocupados

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id_comision):
        return Comision.query.get(id_comision)

    @staticmethod
    def get_all():
        return Comision.query.all()

    @staticmethod
    def get_by_materia(id_materia):
        return Comision.query.filter_by(id_materia=id_materia).all()


class Inscripcion(db.Model):
    """
    Vínculo entre un Alumno y una Comisión específica, con el
    progreso del alumno en esa cursada.
    """
    __tablename__ = 'Inscripciones'

    id_inscripcion = db.Column(db.Integer, primary_key=True)
    id_alumno = db.Column(db.Integer, db.ForeignKey('Alumnos.id_persona'), nullable=False)
    id_comision = db.Column(db.Integer, db.ForeignKey('Comisiones.id_comision'), nullable=False)
    fecha_inscripcion = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    estado_cursada = db.Column(
        db.Enum(
            'Cursando', 'Promocionado', 'Regular', 'Libre',
            'Aprobada', 'Reprobada', 'Abandonada'
        ),
        default='Cursando'
    )

    alumno = db.relationship('Alumno', back_populates='inscripciones')
    comision = db.relationship('Comision', back_populates='inscripciones')
    notas = db.relationship('Nota', back_populates='inscripcion', cascade='all, delete-orphan')
    asistencias = db.relationship(
        'Asistencia', back_populates='inscripcion', cascade='all, delete-orphan'
    )

    __table_args__ = (
        db.UniqueConstraint('id_alumno', 'id_comision', name='uq_alumno_comision'),
    )

    def __repr__(self):
        return f'<Inscripcion alumno={self.id_alumno} comision={self.id_comision}>'

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id_inscripcion):
        return Inscripcion.query.get(id_inscripcion)

    @staticmethod
    def get_by_alumno(id_alumno):
        return Inscripcion.query.filter_by(id_alumno=id_alumno).all()

class Nota(db.Model):
    """
    Nota registrada para una Inscripcion en una instancia evaluativa
    puntual (parcial, recuperatorio, final, TP). Ver gestion_academica_pro.sql
    sección 3.
    """
    __tablename__ = 'Notas'

    id_nota = db.Column(db.Integer, primary_key=True)
    id_inscripcion = db.Column(db.Integer, db.ForeignKey('Inscripciones.id_inscripcion'), nullable=False)
    instancia = db.Column(
        db.Enum('1er Parcial', '2do Parcial', 'Recuperatorio', 'Final', 'TP'),
        nullable=False
    )
    valor = db.Column(db.Numeric(4, 2), nullable=False)
    fecha = db.Column(db.Date, nullable=False)

    inscripcion = db.relationship('Inscripcion', back_populates='notas')

    def __repr__(self):
        return f'<Nota inscripcion={self.id_inscripcion} {self.instancia}={self.valor}>'

    @staticmethod
    def get_by_inscripcion(id_inscripcion):
        return Nota.query.filter_by(id_inscripcion=id_inscripcion).order_by(Nota.fecha).all()