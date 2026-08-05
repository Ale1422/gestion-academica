# app/calendario/validaciones.py

from app.calendario.models import MesaExamen, InscripcionMesa
from app.secretaria.models import Inscripcion, Comision
from app.materias.models import Correlatividad


class ValidacionError(Exception):
    """Excepción de negocio para errores de validación del módulo de Calendario."""
    pass


# Mismo criterio que ESTADOS_CUMPLE_PARA_FINAL en secretaria/validaciones.py:
# un requisito 'Para Rendir Final' solo se considera cumplido si el alumno
# ya tiene la materia requerida completamente aprobada.
ESTADOS_CUMPLE_PARA_FINAL = {'Aprobada'}

# Estados de cursada de la PROPIA materia que habilitan a rendir su final.
ESTADOS_HABILITAN_RENDIR = {'Regular', 'Promocionado', 'Aprobada'}

# Máximo de veces que un alumno puede inscribirse a rendir el final de
# una materia. Igual que NOTA_MINIMA_APROBACION (módulo 5) y
# UMBRAL_ALERTA_INASISTENCIA (módulo 6): constante de código, no
# configurable desde la UI salvo que se avise lo contrario.
MAX_INTENTOS_FINAL = 3

# Resultados que consumen un intento. 'Pendiente' no cuenta (la mesa
# todavía no se rindió). Asumo que 'Ausente' SÍ consume intento —lo
# marco como supuesto a confirmar, igual que las otras constantes: si
# el instituto quiere que una ausencia no cuente como intento rendido,
# hay que sacar 'Ausente' de este set.
ESTADOS_CONSUMEN_INTENTO = {'Desaprobado', 'Ausente'}


def validar_limite_intentos_final(id_alumno, id_materia):
    """
    Bloquea la inscripción si el alumno ya agotó sus intentos para
    rendir el final de esta materia. No cuenta la mesa actual (todavía
    no tiene resultado cargado).
    """
    intentos = InscripcionMesa.query.join(MesaExamen).filter(
        InscripcionMesa.id_alumno == id_alumno,
        MesaExamen.id_materia == id_materia,
        InscripcionMesa.resultado.in_(ESTADOS_CONSUMEN_INTENTO)
    ).count()

    if intentos >= MAX_INTENTOS_FINAL:
        raise ValidacionError(
            f'El alumno ya agotó los {MAX_INTENTOS_FINAL} intentos '
            f'permitidos para rendir el final de esta materia.'
        )


def validar_materia_habilitada_para_mesa(materia):
    """
    Una materia 'Promocional' pura no tiene instancia de final —no puede
    tener Mesas de Examen asociadas (cierra el pendiente anotado en el
    módulo 2 de EstadoProyecto.md).
    """
    if materia.modalidad_aprobacion == 'Promocional':
        raise ValidacionError(
            f'La materia "{materia.nombre}" es puramente Promocional: '
            f'no tiene instancia de final y no puede tener mesas de examen.'
        )


def validar_cursada_habilita_final(id_alumno, id_materia):
    """
    El alumno tiene que tener la cursada de ESTA materia en condiciones
    de rendir (Regular/Promocionado/Aprobada) — no alcanza con cumplir
    las correlativas de otras materias.
    """
    cursada = Inscripcion.query.join(Comision).filter(
        Inscripcion.id_alumno == id_alumno,
        Comision.id_materia == id_materia,
        Inscripcion.estado_cursada.in_(ESTADOS_HABILITAN_RENDIR)
    ).first()
    if not cursada:
        raise ValidacionError(
            'El alumno no tiene la cursada de esta materia en condiciones '
            'de rendir el final (debe estar Regular, Promocionado o Aprobada).'
        )


def validar_correlatividades_para_rendir_final(id_alumno, id_materia):
    """
    Verifica las correlatividades 'Para Rendir Final' de la materia,
    mismo esquema que validar_correlatividades_para_cursar() en
    secretaria/validaciones.py pero con tipo_requisito distinto.
    """
    requisitos = Correlatividad.query.filter_by(
        id_materia=id_materia, tipo_requisito='Para Rendir Final'
    ).all()

    faltantes = []
    for req in requisitos:
        cumple = Inscripcion.query.filter(
            Inscripcion.id_alumno == id_alumno,
            Inscripcion.id_comision.in_(
                Comision.query.with_entities(Comision.id_comision)
                .filter_by(id_materia=req.id_materia_requerida)
            ),
            Inscripcion.estado_cursada.in_(ESTADOS_CUMPLE_PARA_FINAL)
        ).first()
        if not cumple:
            faltantes.append(req.id_materia_requerida)

    if faltantes:
        raise ValidacionError(
            f'El alumno no cumple las correlatividades para rendir el '
            f'final (materias pendientes: {faltantes})'
        )


def inscribir_alumno_mesa(id_alumno, id_mesa):
    """
    Orquesta las validaciones y crea la InscripcionMesa. Uso: llamar
    desde la ruta dentro de un try/except ValidacionError — mismo patrón
    que inscribir_alumno() en secretaria/validaciones.py.
    """
    mesa = MesaExamen.get_by_id(id_mesa)
    if mesa is None:
        raise ValidacionError('La mesa de examen indicada no existe.')

    if InscripcionMesa.get(id_mesa, id_alumno) is not None:
        raise ValidacionError('El alumno ya está inscripto en esta mesa.')

    validar_cursada_habilita_final(id_alumno, mesa.id_materia)
    validar_correlatividades_para_rendir_final(id_alumno, mesa.id_materia)
    validar_limite_intentos_final(id_alumno, mesa.id_materia)   # <-- nuevo

    inscripcion = InscripcionMesa(id_mesa=id_mesa, id_alumno=id_alumno)
    inscripcion.save()
    return inscripcion


def registrar_resultado_mesa(id_mesa, id_alumno, resultado, nota_final=None):
    """
    Carga el resultado de un alumno en una mesa. Si el resultado es
    'Aprobado', además actualiza a 'Aprobada' el estado_cursada de la
    Inscripcion (Comision) más reciente de esa materia — mismo criterio
    que registrar_nota() en secretaria/validaciones.py con la instancia
    'Final' (ver EstadoProyecto.md, módulo 5).
    """
    inscripcion_mesa = InscripcionMesa.get(id_mesa, id_alumno)
    if inscripcion_mesa is None:
        raise ValidacionError('El alumno no está inscripto en esta mesa.')

    if resultado == 'Aprobado' and nota_final is None:
        raise ValidacionError('Un resultado "Aprobado" requiere nota final.')

    inscripcion_mesa.resultado = resultado
    inscripcion_mesa.nota_final = nota_final

    if resultado == 'Aprobado':
        mesa = inscripcion_mesa.mesa
        cursada = Inscripcion.query.join(Comision).filter(
            Inscripcion.id_alumno == id_alumno,
            Comision.id_materia == mesa.id_materia
        ).order_by(Comision.ciclo_lectivo.desc()).first()
        if cursada:
            cursada.estado_cursada = 'Aprobada'

    inscripcion_mesa.save()
    return inscripcion_mesa
