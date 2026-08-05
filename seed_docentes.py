"""
seed_docentes.py

Seed de 15 Docentes de prueba, con datos de contacto random (DNI, CUIL,
teléfono, dirección, email) para no chocar con nada real. Es solo para
poder probar el módulo de Comisiones (que necesita id_docente) sin tener
que cargar docentes a mano uno por uno.

USO
---
Correr desde la raíz del proyecto (donde está run.py), con el entorno
virtual activado. Se recomienda correr primero seed_tecnicatura_software.py
si todavía no cargaste la carrera/materias, aunque este script no depende
de eso (Docente no tiene FK directa a Materia — la relación docente↔materia
se da a través de Comision, que se carga aparte).

    python seed_docentes.py

Es idempotente: antes de crear un Docente, chequea si ya existe una
Persona con ese DNI (buscando por dni, que es UNIQUE); si existe, saltea
ese registro en vez de duplicarlo. Podés correrlo más de una vez sin
generar duplicados.

DECISIONES / SUPUESTOS
-----------------------
- Nombre, apellido y "especialidad" NO son random: los elegí a propósito
  para que, entre los 15 docentes, quede cubierta al menos un área afín
  a cada una de las 28 materias de la Tecnicatura (así la Secretaria
  tiene de dónde elegir al crear cada Comisión). El campo `especialidad`
  de Docente es texto libre, así que lo uso para dejar anotado a qué
  materias está pensado que dicte cada uno — es solo referencia, no se
  usa en ninguna validación del sistema.
- DNI, CUIL, teléfono, dirección y fecha_ingreso sí son generados
  al azar (rangos plausibles para Argentina), porque el pedido explícito
  fue "datos random, es solo para pruebas".
- CUIL: se arma con prefijo 20/23/24/27 + DNI + un dígito verificador
  random al final. OJO: no se calcula el dígito verificador real según
  el algoritmo de AFIP — para datos de prueba no importa, pero si en
  algún momento se agrega una validación de CUIL real al formulario,
  estos valores de seed no la van a pasar.
- email: se arma como nombre.apellido@instituto-test.local (dominio
  claramente de prueba, para no generar direcciones que parezcan reales).
- fecha_nacimiento de la Persona: se deja en None (columna nullable en
  el modelo) — no es un dato relevante para probar Comisiones y así se
  evita generar fechas de nacimiento inventadas.
"""

import random
from datetime import date, timedelta

from app import create_app, db
from app.auth.models import Persona
from app.materias.models import Docente


# (nombre, apellido, especialidad de referencia — no validada por el sistema)
DOCENTES = [
    ("Martín", "Gómez", "Programación I, II y III"),
    ("Lucía", "Fernández", "Bases de Datos I y II"),
    ("Diego", "Ramírez", "Matemática I y II"),
    ("Sofía", "Torres", "Inglés Técnico I, II y III"),
    ("Pablo", "Ibáñez", "Introducción a Redes / Redes y Seguridad Informática"),
    ("Carla", "Medina", "Estructura de Datos y Algoritmos"),
    ("Nicolás", "Acosta", "Análisis y Diseño de Sistemas"),
    ("Valentina", "Rojas", "Estadística Aplicada"),
    ("Federico", "Suárez", "Introducción a la Informática"),
    ("Agustina", "Molina", "Ciudadanía y Espacio Público"),
    ("Rodrigo", "Paz", "Taller de Programación I, II y III"),
    ("Camila", "Ortiz", "Sistemas de Información Empresarial"),
    ("Julián", "Herrera", "Laboratorio de Programación"),
    ("Florencia", "Castro", "Gestión de Proyectos y Software de Calidad / Desarrollo Empresarial"),
    ("Emiliano", "Vega", "Ética y Deontología Profesional / Legislación de Software / Emprendimientos Tecnológicos"),
]

CALLES = [
    "Av. Aconquija", "Calle Congreso", "San Martín", "24 de Septiembre",
    "Av. Solano Vera", "Mendoza", "Laprida", "Av. Roca", "Balcarce", "Junín",
]

PREFIJOS_CUIL = ["20", "23", "24", "27"]

DOMINIO_EMAIL_TEST = "instituto-test.local"


def _dni_random(usados):
    while True:
        dni = str(random.randint(20_000_000, 45_000_000))
        if dni not in usados:
            usados.add(dni)
            return dni


def _cuil_random(dni):
    prefijo = random.choice(PREFIJOS_CUIL)
    verificador = random.randint(0, 9)
    return f"{prefijo}-{dni}-{verificador}"


def _telefono_random():
    return f"381{random.randint(4000000, 5999999)}"


def _direccion_random():
    calle = random.choice(CALLES)
    numero = random.randint(100, 3500)
    return f"{calle} {numero}"


def _fecha_ingreso_random():
    # Entre 1 y 12 años atrás desde hoy, fecha random dentro de ese rango.
    dias_atras = random.randint(365, 12 * 365)
    return date.today() - timedelta(days=dias_atras)


def get_or_create_docente(nombre, apellido, especialidad, dnis_usados):
    persona_existente = Persona.query.filter_by(nombre=nombre, apellido=apellido).first()
    if persona_existente and persona_existente.docente:
        print(f'  - Docente ya existe, se saltea: "{nombre} {apellido}"')
        return persona_existente.docente

    dni = _dni_random(dnis_usados)
    email = f"{nombre.lower()}.{apellido.lower()}@{DOMINIO_EMAIL_TEST}"
    # Evita choque si por casualidad ya existe ese email (muy poco
    # probable con nombres fijos + dominio de prueba, pero por las dudas).
    if Persona.query.filter_by(email=email).first():
        email = f"{nombre.lower()}.{apellido.lower()}.{dni[-4:]}@{DOMINIO_EMAIL_TEST}"

    persona = Persona(
        dni=dni,
        nombre=nombre,
        apellido=apellido,
        fecha_nacimiento=None,
        email=email,
        telefono=_telefono_random(),
        direccion=_direccion_random(),
    )
    db.session.add(persona)
    db.session.flush()  # asigna persona.id_persona sin cerrar la transacción

    docente = Docente(
        id_persona=persona.id_persona,
        cuil=_cuil_random(dni),
        especialidad=especialidad,
        fecha_ingreso=_fecha_ingreso_random(),
    )
    docente.save()

    print(f'  + Docente creado: "{nombre} {apellido}" — {especialidad} (CUIL {docente.cuil})')
    return docente


def run_seed():
    dnis_usados = {p.dni for p in Persona.query.with_entities(Persona.dni).all()}

    print(f"Cargando {len(DOCENTES)} docentes de prueba...\n")
    for nombre, apellido, especialidad in DOCENTES:
        get_or_create_docente(nombre, apellido, especialidad, dnis_usados)

    print(f"\nListo. {len(DOCENTES)} docentes procesados.")


if __name__ == "__main__":
    random.seed()  # semilla del sistema, no fija — cada corrida genera datos distintos
    app = create_app()
    with app.app_context():
        run_seed()