from app import db
from datetime import datetime


class Evento(db.Model):
    """
    Evento institucional genérico: mesas de examen, jornadas académicas,
    actos, feriados, períodos de inscripción, etc. (DDL sección 4).
    Una Mesa de Examen es un Evento de tipo 'Examen' que además tiene
    una fila asociada en MesasExamen con la materia y el llamado —
    ambos se crean juntos desde calendario/routes.py:crear_mesa().
    """
    __tablename__ = 'Eventos'

    id_evento = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    tipo = db.Column(
        db.Enum('Examen', 'Evento Académico', 'Feriado', 'Inscripciones'),
        nullable=False
    )

    mesa_examen = db.relationship(
        'MesaExamen', back_populates='evento', uselist=False,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Evento {self.nombre} ({self.tipo})>'

    def save(self):
        if not self.id_evento:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id_evento):
        return Evento.query.get(id_evento)

    @staticmethod
    def get_all():
        return Evento.query.order_by(Evento.fecha_inicio).all()

    @staticmethod
    def get_proximos(desde=None):
        desde = desde or datetime.utcnow()
        return (
            Evento.query.filter(Evento.fecha_fin >= desde)
            .order_by(Evento.fecha_inicio)
            .all()
        )


class MesaExamen(db.Model):
    """
    La puesta en marcha de un final de una Materia en una fecha concreta
    (vía su Evento). Mismo patrón de "extiende a" que Comision respecto
    de Materia+Docente en secretaria/models.py.
    """
    __tablename__ = 'MesasExamen'

    id_mesa = db.Column(db.Integer, primary_key=True)
    id_evento = db.Column(db.Integer, db.ForeignKey('Eventos.id_evento'), nullable=False)
    id_materia = db.Column(db.Integer, db.ForeignKey('Materias.id_materia'), nullable=False)
    llamado = db.Column(
        db.Enum('1er Llamado', '2do Llamado', '3er Llamado'), default='1er Llamado'
    )

    evento = db.relationship('Evento', back_populates='mesa_examen')
    materia = db.relationship('Materia', back_populates='mesas_examen')
    inscripciones = db.relationship(
        'InscripcionMesa', back_populates='mesa', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<MesaExamen materia={self.id_materia} llamado={self.llamado}>'

    def save(self):
        if not self.id_mesa:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id_mesa):
        return MesaExamen.query.get(id_mesa)

    @staticmethod
    def get_all():
        return MesaExamen.query.join(Evento).order_by(Evento.fecha_inicio).all()

    @staticmethod
    def get_by_materia(id_materia):
        return MesaExamen.query.filter_by(id_materia=id_materia).all()


class InscripcionMesa(db.Model):
    """
    Vínculo entre un Alumno y una MesaExamen específica, con su
    resultado. Clave primaria compuesta, igual que en ModeloDatos.sql.
    """
    __tablename__ = 'InscripcionesMesa'

    id_mesa = db.Column(db.Integer, db.ForeignKey('MesasExamen.id_mesa'), primary_key=True)
    id_alumno = db.Column(db.Integer, db.ForeignKey('Alumnos.id_persona'), primary_key=True)
    fecha_inscripcion = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    resultado = db.Column(
        db.Enum('Pendiente', 'Aprobado', 'Desaprobado', 'Ausente'), default='Pendiente'
    )
    nota_final = db.Column(db.Numeric(4, 2))

    mesa = db.relationship('MesaExamen', back_populates='inscripciones')
    alumno = db.relationship('Alumno', back_populates='inscripciones_mesa')

    def __repr__(self):
        return f'<InscripcionMesa mesa={self.id_mesa} alumno={self.id_alumno}>'

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get(id_mesa, id_alumno):
        return InscripcionMesa.query.get((id_mesa, id_alumno))

    @staticmethod
    def get_by_mesa(id_mesa):
        return InscripcionMesa.query.filter_by(id_mesa=id_mesa).all()

    @staticmethod
    def get_by_alumno(id_alumno):
        return InscripcionMesa.query.filter_by(id_alumno=id_alumno).all()