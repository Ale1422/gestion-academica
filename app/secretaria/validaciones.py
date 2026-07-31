# app/secretaria/validaciones.py

from app.secretaria.models import Alumno, Inscripcion, Comision
from app.materias.models import Correlatividad


class ValidacionError(Exception):
    """Excepción de negocio para errores de validación de inscripciones."""
    pass


# Estados que se consideran "cumplido" un requisito Para Cursar
# (el alumno regularizó la materia, aunque no haya rendido el final).
ESTADOS_CUMPLE_PARA_CURSAR = {'Promocionado', 'Regular', 'Aprobada'}

# Estados que se consideran "cumplido" un requisito Para Rendir Final
# (el alumno ya aprobó la materia por completo).
ESTADOS_CUMPLE_PARA_FINAL = {'Aprobada'}

# Estados académicos del alumno habilitados para inscribirse a una
# comisión. 'Egresado' y 'Pasivo' quedan afuera: un egresado ya no
# cursa materias de la carrera, y un pasivo no está habilitado hasta
# regularizar su situación.
ESTADOS_ACADEMICOS_HABILITADOS = {'Regular', 'Libre'}


def validar_estado_alumno(alumno):
    """
    Verifica que el estado académico del alumno permita inscribirse a
    una comisión. Un alumno 'Egresado' o 'Pasivo' no puede inscribirse.
    """
    if alumno.estado_academico not in ESTADOS_ACADEMICOS_HABILITADOS:
        raise ValidacionError(
            f'El alumno {alumno.nombre_completo} tiene estado académico '
            f'"{alumno.estado_academico}" y no puede inscribirse a comisiones.'
        )


def validar_no_inscripto(id_alumno, id_comision):
    """
    Verifica que el alumno no esté ya inscripto en esta comisión.
    Sin este chequeo explícito, un intento de doble inscripción llega
    hasta el INSERT y rompe con un IntegrityError sin capturar (por el
    UNIQUE(id_alumno, id_comision) del DDL) en vez de un mensaje prolijo.
    """
    ya_inscripto = Inscripcion.query.filter_by(
        id_alumno=id_alumno, id_comision=id_comision
    ).first()
    if ya_inscripto:
        raise ValidacionError('El alumno ya está inscripto en esta comisión.')


def validar_correlatividades_para_cursar(id_alumno, id_materia):
    """
    Verifica que el alumno cumpla todas las correlatividades
    'Para Cursar' de la materia antes de inscribirlo a una comisión.
    Lanza ValidacionError si falta alguna.
    """
    requisitos = Correlatividad.query.filter_by(
        id_materia=id_materia, tipo_requisito='Para Cursar'
    ).all()

    faltantes = []
    for req in requisitos:
        cumple = Inscripcion.query.filter(
            Inscripcion.id_alumno == id_alumno,
            Inscripcion.id_comision.in_(
                # comisiones de la materia requerida, cualquier ciclo
                Comision.query.with_entities(Comision.id_comision)
                .filter_by(id_materia=req.id_materia_requerida)
            ),
            Inscripcion.estado_cursada.in_(ESTADOS_CUMPLE_PARA_CURSAR)
        ).first()
        if not cumple:
            faltantes.append(req.id_materia_requerida)

    if faltantes:
        raise ValidacionError(
            f'El alumno no cumple las correlatividades para cursar '
            f'(materias pendientes: {faltantes})'
        )


def validar_cupo(comision):
    """
    Verifica que la comisión tenga cupo disponible. Un alumno 'Libre'
    en la comisión no ocupa vacante (ver Comision.cupos_disponibles).
    """
    if comision.cupos_disponibles <= 0:
        raise ValidacionError('La comisión no tiene cupos disponibles.')


def validar_modalidad_vs_estado(comision, estado_cursada):
    """
    Impide asignar estado_cursada='Promocionado' a una materia cuya
    modalidad_aprobacion sea 'Final' (no admite promoción directa).

    NOTA: no se invoca todavía desde inscribir_alumno, porque ahí el
    estado_cursada siempre arranca en 'Cursando'. Esta validación es
    para cuando se implemente la ruta de actualizar/cerrar cursada
    (pendiente, ver EstadoProyecto.md módulo 4).
    """
    materia = comision.materia
    if estado_cursada == 'Promocionado' and materia.modalidad_aprobacion == 'Final':
        raise ValidacionError(
            f'La materia "{materia.nombre}" es de modalidad Final: '
            f'no admite promoción directa.'
        )


def inscribir_alumno(id_alumno, id_comision):
    """
    Orquesta las validaciones de alta de inscripción y crea la
    Inscripcion si todo es correcto. Uso: llamar desde la ruta
    correspondiente dentro de un try/except ValidacionError.

    Validaciones aplicadas, en orden:
      1. El alumno existe y su estado académico habilita inscribirse.
      2. La comisión existe.
      3. El alumno no está ya inscripto en esa comisión.
      4. La comisión tiene cupo disponible.
      5. El alumno cumple las correlatividades 'Para Cursar' de la materia.

    validar_modalidad_vs_estado NO se aplica acá — ver su docstring.
    """
    alumno = Alumno.get_by_id(id_alumno)
    if alumno is None:
        raise ValidacionError('El alumno indicado no existe.')
    validar_estado_alumno(alumno)

    comision = Comision.get_by_id(id_comision)
    if comision is None:
        raise ValidacionError('La comisión indicada no existe.')

    validar_no_inscripto(id_alumno, id_comision)
    validar_cupo(comision)
    validar_correlatividades_para_cursar(id_alumno, comision.id_materia)

    inscripcion = Inscripcion(
        id_alumno=id_alumno,
        id_comision=id_comision,
        estado_cursada='Cursando'
    )
    inscripcion.save()
    return inscripcion