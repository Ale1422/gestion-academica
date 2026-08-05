"""
seed_tecnicatura_software.py

Seed de la carrera "Tecnicatura Superior en Desarrollo de Software" y sus
materias (1°, 2° y 3° año), tomadas del plan de estudios provisto por el
usuario.

USO
---
Correr desde la raíz del proyecto (donde está run.py), con el entorno
virtual activado:

    python seed_tecnicatura_software.py

Es idempotente: si la Carrera ya existe (buscada por codigo_plan), no la
vuelve a crear; y por cada Materia, si ya existe una con el mismo nombre
para esa carrera, la saltea en vez de duplicarla. Podés correrlo más de
una vez sin miedo a generar registros repetidos.

DECISIONES TOMADAS (avisadas por el usuario o inferidas del pedido)
---------------------------------------------------------------------
- codigo_plan = '1' (dato provisorio, indicado explícitamente por el
  usuario).
- modalidad_aprobacion = 'Ambas' para TODAS las materias (indicado
  explícitamente por el usuario).
- tipo_dictado = 'Anual' para todas: así figura en la columna "RÉGIMEN"
  de las tres imágenes del plan de estudios, ninguna materia es
  cuatrimestral.
- carga_horaria_total = valor de la columna "HS/AÑO" de cada imagen
  (interpretación ya registrada en EstadoProyecto.md: total de horas de
  todo el dictado según tipo_dictado, no un valor semanal).
- anio_sugerido = 1, 2 o 3 según la imagen de la que sale cada materia.

⚠️ PUNTO A REVISAR CON EL USUARIO (no bloqueante, no lo resolví solo):
La materia N° 5 de Segundo Año aparece en la imagen como "Sistemas de
Información Empresaria I". No hay una "Sistemas de Información
Empresarial II" en ningún otro año, así que probablemente sea un typo de
la fuente original por "Sistemas de Información Empresarial" (sin el
", I" final). La dejo tal cual salió en la imagen — si el usuario
confirma el nombre correcto, es un simple UPDATE, no hace falta volver a
correr el seed completo.
"""

from app import create_app, db
from app.materias.models import Carrera, Materia


# --- Datos de la carrera ---

CARRERA_NOMBRE = "Tecnicatura Superior en Desarrollo de Software"
CARRERA_DURACION_ANIOS = 3
CARRERA_CODIGO_PLAN = "1"


# --- Materias por año, tal como figuran en las imágenes del plan ---
# Cada tupla: (nombre, hs_sem, hs_anio)
# hs_sem no se persiste (el modelo Materia no tiene ese campo), se deja
# comentado al lado de cada materia solo como referencia de dónde salió
# el dato de carga_horaria_total.

MATERIAS_ANIO_1 = [
    ("Ciudadanía y Espacio Público", 2, 60),
    ("Introducción a la Informática", 4, 120),
    ("Introducción a Redes", 3, 90),
    ("Bases de Datos I", 4, 120),
    ("Matemática I", 3, 90),
    ("Programación I", 5, 150),
    ("Inglés Técnico I", 2, 60),
    ("Estructura de Datos y Algoritmos", 3, 90),
    ("Taller de Programación I", 4, 120),
]

MATERIAS_ANIO_2 = [
    ("Programación II", 5, 150),
    ("Estadística Aplicada", 3, 90),
    ("Base de Datos II", 3, 90),
    ("Matemática II", 3, 90),
    # Ver nota sobre posible typo en el docstring del módulo.
    ("Sistemas de Información Empresaria I", 2, 60),
    ("Inglés Técnico II", 2, 60),
    ("Redes y Seguridad Informática", 3, 90),
    ("Análisis y Diseño de Sistemas", 4, 120),
    ("Laboratorio de Programación", 4, 120),
    ("Taller de Programación II", 5, 150),
]

MATERIAS_ANIO_3 = [
    ("Emprendimientos Tecnológicos", 2, 60),
    ("Gestión de Proyectos y Software de Calidad", 4, 120),
    ("Desarrollo Empresarial", 3, 90),
    ("Programación III", 5, 150),
    ("Inglés Técnico III", 2, 60),
    ("Ética y Deontología Profesional", 2, 60),
    ("Legislación de Software", 2, 60),
    ("Técnicas Avanzadas de Programación", 4, 120),
    ("Taller de Programación III", 7, 210),
]

MATERIAS_POR_ANIO = {
    1: MATERIAS_ANIO_1,
    2: MATERIAS_ANIO_2,
    3: MATERIAS_ANIO_3,
}


def get_or_create_carrera():
    carrera = Carrera.query.filter_by(codigo_plan=CARRERA_CODIGO_PLAN).first()
    if carrera:
        print(f'Carrera ya existe (id_carrera={carrera.id_carrera}): "{carrera.nombre}" — no se recrea.')
        return carrera

    carrera = Carrera(
        nombre=CARRERA_NOMBRE,
        duracion_anios=CARRERA_DURACION_ANIOS,
        codigo_plan=CARRERA_CODIGO_PLAN,
    )
    carrera.save()
    print(f'Carrera creada (id_carrera={carrera.id_carrera}): "{carrera.nombre}".')
    return carrera


def get_or_create_materia(carrera, nombre, anio_sugerido, carga_horaria_total):
    existente = Materia.query.filter_by(
        id_carrera=carrera.id_carrera, nombre=nombre
    ).first()
    if existente:
        print(f'  - Materia ya existe, se saltea: "{nombre}"')
        return existente

    materia = Materia(
        nombre=nombre,
        id_carrera=carrera.id_carrera,
        anio_sugerido=anio_sugerido,
        tipo_dictado="Anual",
        carga_horaria_total=carga_horaria_total,
        modalidad_aprobacion="Ambas",
    )
    materia.save()
    print(f'  + Materia creada: "{nombre}" (año {anio_sugerido}, {carga_horaria_total} hs/año)')
    return materia


def run_seed():
    carrera = get_or_create_carrera()

    for anio, materias in MATERIAS_POR_ANIO.items():
        print(f"\nMaterias de año {anio}:")
        for nombre, _hs_sem, hs_anio in materias:
            get_or_create_materia(carrera, nombre, anio, hs_anio)

    total = sum(len(m) for m in MATERIAS_POR_ANIO.values())
    print(f"\nListo. {total} materias procesadas para la carrera \"{carrera.nombre}\".")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        run_seed()