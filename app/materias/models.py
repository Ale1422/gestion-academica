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
    comisiones = db.relationship('Comision', back_populates='docente')

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


class Carrera(db.Model):
    """
    Carrera ofrecida por el instituto (ej. "Tecnicatura en Informática").
    Cada Materia pertenece a exactamente una Carrera (DDL: Materias.id_carrera
    NOT NULL, ON DELETE CASCADE).
    """
    __tablename__ = 'Carreras'

    id_carrera = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    duracion_anios = db.Column(db.Integer, nullable=False)
    codigo_plan = db.Column(db.String(20), unique=True)

    materias = db.relationship(
        'Materia', back_populates='carrera', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Carrera {self.nombre}>'

    def save(self):
        if not self.id_carrera:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id_carrera):
        return Carrera.query.get(id_carrera)

    @staticmethod
    def get_all():
        return Carrera.query.order_by(Carrera.nombre).all()


class Materia(db.Model):
    """
    Materia perteneciente a una Carrera y a un año sugerido del plan.
    modalidad_aprobacion define si la materia se promociona sin final,
    requiere final obligatorio, o admite ambas modalidades (DDL punto 1
    de gestion_academica_pro.sql).
    """
    __tablename__ = 'Materias'

    id_materia = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    id_carrera = db.Column(db.Integer, db.ForeignKey('Carreras.id_carrera'), nullable=False)
    anio_sugerido = db.Column(db.Integer, nullable=False)
    tipo_dictado = db.Column(
        db.Enum('Anual', 'Cuatrimestral'), default='Cuatrimestral'
    )
    carga_horaria_total = db.Column(db.Integer)
    modalidad_aprobacion = db.Column(
        db.Enum('Promocional', 'Final', 'Ambas'), nullable=False, default='Final'
    )

    carrera = db.relationship('Carrera', back_populates='materias')
    comisiones = db.relationship('Comision', back_populates='materia')

    # Correlatividades donde ESTA materia es la que exige el requisito
    # (ej. "Programación II" requiere "Programación I")
    correlatividades_requeridas = db.relationship(
        'Correlatividad',
        foreign_keys='Correlatividad.id_materia',
        back_populates='materia',
        cascade='all, delete-orphan',
    )
    # Correlatividades donde ESTA materia es la exigida por otra
    # (ej. "Programación I" es requisito de "Programación II")
    correlatividades_donde_es_requisito = db.relationship(
        'Correlatividad',
        foreign_keys='Correlatividad.id_materia_requerida',
        back_populates='materia_requerida',
    )

    def __repr__(self):
        return f'<Materia {self.nombre}>'

    def save(self):
        if not self.id_materia:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id_materia):
        return Materia.query.get(id_materia)

    @staticmethod
    def get_all():
        return Materia.query.order_by(Materia.id_carrera, Materia.anio_sugerido).all()

    @staticmethod
    def get_by_carrera(id_carrera):
        return (
            Materia.query.filter_by(id_carrera=id_carrera)
            .order_by(Materia.anio_sugerido, Materia.nombre)
            .all()
        )


class Correlatividad(db.Model):
    """
    Requisito entre materias. tipo_requisito distingue si la correlativa
    aplica "Para Cursar" o "Para Rendir Final" (DDL punto 2).
    Clave primaria compuesta, igual que en gestion_academica_pro.sql.
    """
    __tablename__ = 'Correlatividades'

    id_materia = db.Column(
        db.Integer, db.ForeignKey('Materias.id_materia'), primary_key=True
    )
    id_materia_requerida = db.Column(
        db.Integer, db.ForeignKey('Materias.id_materia'), primary_key=True
    )
    tipo_requisito = db.Column(
        db.Enum('Para Cursar', 'Para Rendir Final'),
        primary_key=True,
        default='Para Cursar',
    )

    materia = db.relationship(
        'Materia',
        foreign_keys=[id_materia],
        back_populates='correlatividades_requeridas',
    )
    materia_requerida = db.relationship(
        'Materia',
        foreign_keys=[id_materia_requerida],
        back_populates='correlatividades_donde_es_requisito',
    )

    def __repr__(self):
        return (
            f'<Correlatividad materia={self.id_materia} '
            f'requiere={self.id_materia_requerida} ({self.tipo_requisito})>'
        )

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_materia(id_materia):
        return Correlatividad.query.filter_by(id_materia=id_materia).all()

    @staticmethod
    def existe(id_materia, id_materia_requerida, tipo_requisito):
        return (
            Correlatividad.query.filter_by(
                id_materia=id_materia,
                id_materia_requerida=id_materia_requerida,
                tipo_requisito=tipo_requisito,
            ).first()
            is not None
        )