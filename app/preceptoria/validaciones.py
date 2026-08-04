# app/preceptoria/validaciones.py

# Porcentaje de inasistencias (sobre el total de clases registradas) a
# partir del cual se considera que un alumno está en riesgo por
# inasistencias prolongadas. No confirmado por el instituto como valor
# definitivo — ajustar acá si corresponde otro número. Mismo patrón que
# NOTA_MINIMA_APROBACION en app/secretaria/validaciones.py: constante de
# módulo, editable solo desde el código (no hay pantalla de configuración).
UMBRAL_ALERTA_INASISTENCIA = 0.25


def calcular_porcentaje_inasistencia(asistencias):
    """
    asistencias: lista de objetos Asistencia de una misma Inscripcion.
    'Justificado' no cuenta como inasistencia a los fines de la alerta,
    solo 'Ausente'. Devuelve un float entre 0 y 1.
    """
    total = len(asistencias)
    if total == 0:
        return 0.0
    ausentes = sum(1 for a in asistencias if a.estado == 'Ausente')
    return ausentes / total


def en_riesgo_por_inasistencia(asistencias):
    return calcular_porcentaje_inasistencia(asistencias) >= UMBRAL_ALERTA_INASISTENCIA