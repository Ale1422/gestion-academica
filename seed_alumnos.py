"""
seed_alumnos.py

Seed de 30 Alumnos de prueba, con datos de contacto random (DNI,
teléfono, dirección, email, fecha de nacimiento) para no chocar con
nada real. Pensado para poder probar la inscripción en lote a una
Comisión sin tener que cargar 30 alumnos a mano — 30 es justo el
`cupo_maximo` por defecto que usa el modelo `Comision`.

USO
---
Correr desde la raíz del proyecto (donde está run.py), con el entorno
virtual activado:

    python seed_alumnos.py

No depende de seed_tecnicatura_software.py ni de seed_docentes.py — un
Alumno no tiene FK directa a Carrera ni a Materia (esa relación se da
recién al inscribirlo a una Comisión, vía Inscripcion), así que este
seed corre solo.

Es idempotente: antes de crear un Alumno, chequea si ya existe una
Persona con ese nombre+apellido; si existe, saltea ese registro en vez
de duplicarlo. Podés correrlo más de una vez sin generar duplicados.

DECISIONES / SUPUESTOS
-----------------------
- Nombre y apellido NO son random (lista fija de 30 nombres), para que
  el seed sea reproducible y fácil de reconocer en pantalla durante las
  pruebas ("¿ya inscribí a Bianchi?"). Lo que sí es random es todo el
  resto de los datos de contacto: DNI, teléfono, dirección, fecha de
  nacimiento y legajo.
- legajo: se arma como "2026-XXX" (secuencial, 3 dígitos), simulando la
  cohorte de ingreso 2026. No hay un formato de legajo definido todavía
  en el proyecto (ni en la especificación ni en el DDL, `legajo` es
  solo VARCHAR(20) UNIQUE) — si el instituto usa un formato real
  distinto, este es un buen lugar para ajustarlo.
- estado_academico: la gran mayoría queda en 'Regular' (para que sirvan
  para probar inscripciones a Comisión sin chocar con validaciones de
  correlatividades más adelante), y unos pocos se reparten entre
  'Libre', 'Egresado' y 'Pasivo' a propósito, para tener variedad de
  estados a la hora de probar el listado de Alumnos y sus filtros.
- fecha_nacimiento: random entre 18 y 35 años de edad a la fecha de
  hoy — rango plausible para una Tecnicatura, y útil para probar
  cualquier pantalla que muestre edad o fecha de nacimiento.
- email: nombre.apellido@alumno-test.local (dominio de prueba, distinto
  del que usa seed_docentes.py, para que no compitan entre sí si algún
  día se linkea Persona.email a Usuario.username).
"""

import random
from datetime import date, timedelta

from app import create_app, db
from app.auth.models import Persona
from app.secretaria.models import Alumno


ALUMNOS = [
    ("Ana", "Bianchi"), ("Bruno", "Correa"), ("Camila", "Díaz"),
    ("Damián", "Escobar"), ("Elena", "Farías"), ("Franco", "Gauna"),
    ("Guadalupe", "Heredia"), ("Hernán", "Iturralde"), ("Iara", "Juárez"),
    ("Joaquín", "Klein"), ("Karina", "Lezcano"), ("Leandro", "Maldonado"),
    ("Milagros", "Navarro"), ("Nahuel", "Olmedo"), ("Ornella", "Pereyra"),
    ("Patricio", "Quiroga"), ("Quimey", "Reinoso"), ("Rocío", "Salazar"),
    ("Santiago", "Toledo"), ("Tamara", "Ulloa"), ("Ulises", "Vera"),
    ("Valentina", "Wierna"), ("Walter", "Ximenez"), ("Ximena", "Yapura"),
    ("Yamila", "Zalazar"), ("Zoe", "Abregú"), ("Agustín", "Bravo"),
    ("Belén", "Cardozo"), ("Ciro", "Delgado"), ("Delfina", "Espeche"),
]

CALLES = [
    "Av. Aconquija", "Calle Congreso", "San Martín", "24 de Septiembre",
    "Av. Solano Vera", "Mendoza", "Laprida", "Av. Roca", "Balcarce", "Junín",
]

# Reparto de estado_academico a propósito: mayoría Regular, algunos de
# cada otro estado para tener variedad en listados/filtros de prueba.
ESTADOS_ACADEMICOS = (
    ["Regular"] * 24 + ["Libre"] * 3 + ["Egresado"] * 2 + ["Pasivo"] * 1
)

DOMINIO_EMAIL_TEST = "alumno-test.local"

COHORTE = 2026


def _dni_random(usados):
    while True:
        dni = str(random.randint(35_000_000, 50_000_000))
        if dni not in usados:
            usados.add(dni)
            return dni


def _telefono_random():
    return f"381{random.randint(4000000, 5999999)}"


def _direccion_random():
    calle = random.choice(CALLES)
    numero = random.randint(100, 3500)
    return f"{calle} {numero}"


def _fecha_nacimiento_random():
    # Edad random entre 18 y 35 años, a fecha de hoy.
    edad_dias = random.randint(18 * 365, 35 * 365)
    return date.today() - timedelta(days=edad_dias)


def _legajo(indice):
    return f"{COHORTE}-{str(indice).zfill(3)}"


def get_or_create_alumno(nombre, apellido, legajo, estado_academico, dnis_usados):
    persona_existente = Persona.query.filter_by(nombre=nombre, apellido=apellido).first()
    if persona_existente and persona_existente.alumno:
        print(f'  - Alumno ya existe, se saltea: "{nombre} {apellido}"')
        return persona_existente.alumno

    dni = _dni_random(dnis_usados)
    email = f"{nombre.lower()}.{apellido.lower()}@{DOMINIO_EMAIL_TEST}"
    if Persona.query.filter_by(email=email).first():
        email = f"{nombre.lower()}.{apellido.lower()}.{dni[-4:]}@{DOMINIO_EMAIL_TEST}"

    persona = Persona(
        dni=dni,
        nombre=nombre,
        apellido=apellido,
        fecha_nacimiento=_fecha_nacimiento_random(),
        email=email,
        telefono=_telefono_random(),
        direccion=_direccion_random(),
    )
    db.session.add(persona)
    db.session.flush()  # asigna persona.id_persona sin cerrar la transacción

    # Por si el legajo generado ya existiera (no debería, pero por las
    # dudas ante corridas manuales previas con otro seed/legajo suelto).
    legajo_final = legajo
    sufijo = 1
    while Alumno.query.filter_by(legajo=legajo_final).first():
        sufijo += 1
        legajo_final = f"{legajo}-{sufijo}"

    alumno = Alumno(
        id_persona=persona.id_persona,
        legajo=legajo_final,
        estado_academico=estado_academico,
    )
    alumno.save()

    print(f'  + Alumno creado: "{nombre} {apellido}" — legajo {legajo_final} ({estado_academico})')
    return alumno


def run_seed():
    dnis_usados = {p.dni for p in Persona.query.with_entities(Persona.dni).all()}
    estados = ESTADOS_ACADEMICOS.copy()
    random.shuffle(estados)

    print(f"Cargando {len(ALUMNOS)} alumnos de prueba (cohorte {COHORTE})...\n")
    for i, (nombre, apellido) in enumerate(ALUMNOS, start=1):
        estado = estados[i - 1]
        get_or_create_alumno(nombre, apellido, _legajo(i), estado, dnis_usados)

    print(f"\nListo. {len(ALUMNOS)} alumnos procesados.")


if __name__ == "__main__":
    random.seed()  # semilla del sistema, no fija — cada corrida genera datos distintos
    app = create_app()
    with app.app_context():
        run_seed()