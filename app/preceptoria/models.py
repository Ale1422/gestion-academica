from app import db


class Asistencia(db.Model):
    """
    Registro de asistencia de un alumno a una clase concreta, dentro del
    contexto de una Inscripcion (alumno + comisión). Ver
    gestion_academica_pro.sql, sección 3 (Asistencias).
    """
    __tablename__ = 'Asistencias'

    id_asistencia = db.Column(db.Integer, primary_key=True)
    id_inscripcion = db.Column(db.Integer, db.ForeignKey('Inscripciones.id_inscripcion'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    estado = db.Column(db.Enum('Presente', 'Ausente', 'Justificado'), nullable=False)

    inscripcion = db.relationship('Inscripcion', back_populates='asistencias')

    def __repr__(self):
        return f'<Asistencia inscripcion={self.id_inscripcion} {self.fecha} {self.estado}>'

    @staticmethod
    def registrar(id_inscripcion, fecha, estado):
        """
        Upsert: si ya existe un registro para esa inscripción+fecha lo
        actualiza, si no lo crea. No hace commit (lo hace el caller,
        para poder guardar todo el lote de una sola transacción).
        """
        existente = Asistencia.query.filter_by(
            id_inscripcion=id_inscripcion, fecha=fecha
        ).first()
        if existente:
            existente.estado = estado
        else:
            existente = Asistencia(
                id_inscripcion=id_inscripcion, fecha=fecha, estado=estado
            )
            db.session.add(existente)
        return existente

    @staticmethod
    def get_by_inscripcion(id_inscripcion):
        return (
            Asistencia.query
            .filter_by(id_inscripcion=id_inscripcion)
            .order_by(Asistencia.fecha)
            .all()
        )

    @staticmethod
    def get_by_comision_y_fecha(id_comision, fecha):
        # import local para evitar ciclo con secretaria.models
        from app.secretaria.models import Inscripcion
        return (
            Asistencia.query
            .join(Inscripcion, Asistencia.id_inscripcion == Inscripcion.id_inscripcion)
            .filter(Inscripcion.id_comision == id_comision, Asistencia.fecha == fecha)
            .all()
        )