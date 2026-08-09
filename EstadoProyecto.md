# Estado del proyecto — Sistema de Gestión de Alumnos

> Actualizar este archivo al cierre de cada módulo y volver a subirlo al
> proyecto, para que las conversaciones nuevas arranquen con el estado real.

## 1. Auth (Seguridad y Gestión de Usuarios)
- [x] Modelos: `Persona`, `Usuario`, `Rol` (app/auth/models.py)
- [x] Rutas: login, crear usuario, listado, cambiar estado, logout
- [x] Templates: login_form, listadoUsuarios, signup_form
- [x] Usuario admin inicial (script SQL)
- [x] `decorators.py`: control de acceso por rol (hoy cualquier logueado
      entra a cualquier ruta — falta diferenciar Secretaria/Preceptora/Admin)
- [ ] LogsAuditoria (tabla ya existe en el DDL, falta modelo + integración)
- [x] Import de `Alumno` en `secretaria/routes.py` (necesario para que
      SQLAlchemy registre la clase — sigue sin hacerse, ver módulo 3)

## 2. Carreras y Materias — CERRADO
- [x] Modelos: `Carrera`, `Materia`, `Correlatividad` (app/materias/models.py)
- [x] Formularios: `CarreraForm`, `MateriaForm`, `CorrelatividadForm`
      (app/materias/forms.py, archivo nuevo)
- [x] Rutas y templates: alta/edición/listado de carreras y materias
- [x] Gestión de correlatividades (para cursar / para rendir final),
      restringida por UI a materias de la misma carrera
- [x] `base_template.html` confirmado como el vigente (no
      `base_template2.html`); adaptado a Bootstrap 4.1.3 (el proyecto NO
      usa Bootstrap 5) y con el submenú "Materias" del sidebar apuntando
      a `materia_bp.listado_carreras` / `materia_bp.listado_materias`
- [x] Validado a mano por el usuario: alta de carrera, alta de materia,
      alta de correlatividad — funcionando
- [x] Fix Bootstrap 5→4 en `materias_listado.html` (usaba `form-select` y
      `text-end`, que rompían el estilo del `<select>` con BS 4.1.3 cargado)

**Pendiente relacionado, no bloqueante:**
- Validar cruces de negocio en la capa de aplicación (no en el DDL):
  `modalidad_aprobacion` de la materia vs. `estado_cursada` posible en
  `Inscripciones` (ej. no debería poder promocionar una materia
  `'Final'`), y `modalidad_aprobacion` vs. `tipo_requisito` en
  `Correlatividades` (no debería poder exigirse "Para Rendir Final" de
  una materia puramente `'Promocional'`). Se decidió resolver esto
  cuando se implemente el módulo de Comisiones e Inscripciones, que es
  donde se carga el estado de cursada.

## 3. Alumnos (Secretaria) — CERRADO
- [x] Modelo: `Alumno` (app/secretaria/models.py)
- [x] Rename `modesl.py` → `models.py` (typo de archivo corregido)
- [x] Import de `Alumno` en `secretaria/routes.py`
- [x] Formulario: `AlumnoForm` (app/secretaria/forms.py, archivo nuevo)
- [x] Rutas: crear, editar, listado (con búsqueda y filtro por estado), ficha
- [x] Templates: alumno_form, alumno_listado, alumno_ficha
- [x] Decisión tomada: alta de Alumno NO crea Usuario/login — es solo
      registro académico gestionado por la Secretaria (revisar si en el
      futuro se agrega portal de autogestión para alumnos)

## 4. Comisiones e Inscripciones — CERRADO
- [x] Modelos: `Comision`, `Inscripcion`
- [x] Rutas: crear comisión (materia + docente + ciclo lectivo),
      inscribir alumno a comisión
- [x] Validar correlatividades "Para Cursar" antes de inscribir
- [x] Validar `cupo_maximo` de la comisión
- [x] Validar `modalidad_aprobacion` vs. `estado_cursada` al cargar/cerrar
      la cursada (ver pendiente anotado en módulo 2)
- [x] Alta en lote de Comisiones (`/comision/crear_lote`) — genera varias
      comisiones de una carrera/año/ciclo lectivo en un solo submit,
      docente por materia, cuatrimestre/turno/cupo generales para el lote.
- [x] Inscripción en lote de Alumnos a una Comisión (`/comision/<id>/inscribir`)
      — reemplaza el select único por tabla con checkboxes y buscador;
      reutiliza `inscribir_alumno()` por cada alumno tildado, sin frenar
      el lote si alguno falla por cupo o correlatividades.

## 5. Notas — CERRADO
- [x] Todo lo ya cerrado (ver historial de este archivo)
- [x] **Ajuste por módulo 7 (opción A), aplicado:** el final de una
      materia se rinde SIEMPRE a través de una `MesaExamen` (módulo 7 —
      Calendario), nunca como una `Nota` suelta con `instancia='Final'`
- [x] `NotaEntryForm`: sacado `'Final'` de las `choices` de `instancia`
      (quedan `'1er Parcial'`, `'2do Parcial'`, `'Recuperatorio'`, `'TP'`)
- [x] `registrar_nota()`: sacada la rama que actualizaba `estado_cursada`
      cuando `instancia == 'Final'`; ahora **rechaza explícitamente**
      `instancia='Final'` con `ValidacionError` en vez de aceptarla sin
      efecto, para no reabrir una segunda vía silenciosa de aprobar un
      final por fuera de las mesas
- [x] Decisión tomada: el `ENUM` de `Notas.instancia` en el DDL **no se
      tocó** (se deja `'Final'` ahí por compatibilidad con datos
      históricos ya cargados); el cambio fue solo en las choices del
      formulario y en `registrar_nota()`, no en el esquema — no
      requirió migración
- [x] **Bug preexistente corregido de paso:** `validaciones.py` usaba
      `db.session.add()` / `db.session.commit()` en `registrar_nota()`
      sin importar `db` (`from app import db` faltaba) — probablemente
      rompía con `NameError` en cualquier alta de nota. Agregado el
      import. **Pendiente de que el usuario confirme a mano** que la
      carga de notas funciona ahora sin errores ocultos detrás de ese bug.
**Punto abierto, no bloqueante:**
- `NOTA_MINIMA_APROBACION = 6` quedó definida en `validaciones.py` pero,
  tras sacar la rama de `'Final'`, ya no la usa nada en ese archivo.
  Revisar si conviene eliminarla o si se va a reusar para alguna regla
  de `Recuperatorio` a futuro.

## 6. Asistencia (Preceptoria) — CERRADO
- [x] Modelo: `Asistencia` (app/preceptoria/models.py, blueprint y archivo
      nuevos) — mapea la tabla `Asistencias` del DDL
- [x] Relación `Inscripcion.asistencias` agregada en
      `app/secretaria/models.py` (cascade='all, delete-orphan', mismo
      patrón que `notas`)
- [x] `Asistencia.registrar()`: upsert por `(id_inscripcion, fecha)` a
      nivel aplicación — sigue siendo la vía correcta para cargar/editar
      asistencia (no dispara error de duplicado, actualiza el registro
      existente).
- [x] `UNIQUE(id_inscripcion, fecha)` agregado a la tabla `Asistencias`
      (constraint `uq_inscripcion_fecha`), tanto en el DDL de referencia
      (`ModeloDatos.sql`) como en `__table_args__` del modelo
      `Asistencia`. Blinda a nivel base lo que antes solo garantizaba la
      aplicación. **Aplicado directamente por SQL** (`ALTER TABLE
      Asistencias ADD CONSTRAINT uq_inscripcion_fecha UNIQUE
      (id_inscripcion, fecha)`) sobre la base ya existente, previa
      limpieza de duplicados si los había. **Pendiente no bloqueante:**
      generar igual la migración correspondiente con `flask db migrate`
      (revisando que el `upgrade()` sea consistente con lo ya aplicado a
      mano) para que el historial de Alembic no quede desincronizado del
      estado real de la base de cara al resto del equipo o a un deploy
      nuevo.
- [x] Formularios: `AsistenciaFilaForm`, `AsistenciaLoteForm`
      (app/preceptoria/forms.py, archivo nuevo) — mismo patrón de
      FieldList/FormField que `NotasLoteForm` del módulo 5
- [x] Rutas (app/preceptoria/routes.py):
  - `GET/POST /preceptoria` → `index`, listado de comisiones
  - `GET/POST /preceptoria/comision/<id>/asistencia` → `registrar_asistencia`,
    carga en lote por comisión + fecha (una fila por alumno inscripto,
    excluye `Abandonada`/`Libre`); el selector de fecha recarga el form
    vía querystring para poder editar un día ya cargado
  - `GET /preceptoria/alumno/<id_persona>/historial` → `historial_asistencia`,
    detalle por alumno agrupado por inscripción/comisión
  - `GET /preceptoria/comision/<id>/reporte` → `reporte_asistencia`,
    listado de % de inasistencia por alumno de la comisión, ordenado de
    mayor a menor riesgo
- [x] Templates: `index.html`, `registro_asistencia.html`,
      `historial_asistencia.html`, `reporte_asistencia.html`
      (app/preceptoria/templates/preceptoria/)
- [x] Submenú "Asistencia" agregado en `base_template.html` para el rol
      `PRECEPTORA` (antes el sidebar solo tenía ramas para
      `ADMINISTRADOR` y `SECRETARIA`)

**Decisión pendiente de confirmar (no cerrada, revisar con el usuario real
del instituto):**
- `UMBRAL_ALERTA_INASISTENCIA = 0.25` en `app/preceptoria/validaciones.py`
  es un default asumido (25% de clases `'Ausente'` sobre el total de
  clases registradas en esa cursada), no un dato confirmado por el
  instituto. **Decisión explícita del usuario:** por ahora queda como
  constante de módulo, editable solo desde el código — no se agrega
  pantalla de configuración para esto todavía.
- `'Justificado'` no cuenta como inasistencia a los fines del cálculo de
  alerta, solo `'Ausente'`. Si el instituto quiere que las justificadas
  también sumen (aunque sea a una tasa distinta), hay que revisar
  `calcular_porcentaje_inasistencia()`.

## 7. Calendario y Eventos — CERRADO
- [x] Blueprint nuevo `calendario_bp` (app/calendario/__init__.py,
      routes.py, models.py, forms.py, validaciones.py,
      templates/calendario/*.html)
- [x] Modelos: `Evento`, `MesaExamen`, `InscripcionMesa`
      (app/calendario/models.py) — mapean las tablas ya existentes en el
      DDL (`ModeloDatos.sql`, sección 4), que estaban sin usar
- [x] Relaciones cruzadas agregadas: `Materia.mesas_examen`
      (app/materias/models.py) y `Alumno.inscripciones_mesa`
      (app/secretaria/models.py), mismo patrón que `Materia.comisiones` /
      `Alumno.inscripciones`
- [x] Alta de Mesa de Examen: un solo formulario crea el `Evento`
      (`tipo='Examen'`) y la `MesaExamen` juntos, mismo patrón
      Persona→Alumno (flush intermedio, misma transacción)
- [x] Eventos genéricos (Evento Académico, Feriado, Inscripciones):
      alta/edición/listado/baja independientes de las mesas
- [x] Validado: `validar_materia_habilitada_para_mesa()` bloquea mesas de
      examen sobre materias `modalidad_aprobacion='Promocional'` (cierra
      el pendiente anotado en el módulo 2)
- [x] Inscripción a mesa: `validar_cursada_habilita_final()` (la cursada
      de ESA materia debe estar Regular/Promocionado/Aprobada) +
      `validar_correlatividades_para_rendir_final()` (tipo_requisito
      'Para Rendir Final' de otras materias)
- [x] Límite de intentos para rendir final: `MAX_INTENTOS_FINAL = 3`
      (constante de módulo, mismo criterio que `NOTA_MINIMA_APROBACION`
      del módulo 5 y `UMBRAL_ALERTA_INASISTENCIA` del módulo 6 — no
      editable desde la UI). Cuenta como intento consumido
      `'Desaprobado'` y `'Ausente'` (`ESTADOS_CONSUMEN_INTENTO`) — **ver
      nota de decisión pendiente más abajo**
- [x] `registrar_resultado_mesa()`: si el resultado es `'Aprobado'`,
      actualiza `Inscripcion.estado_cursada` a `'Aprobada'`. Si es
      `'Desaprobado'` o `'Ausente'`, **no toca** `estado_cursada` (el
      alumno sigue `'Regular'` y puede volver a inscribirse mientras no
      agote los 3 intentos) — confirmado con el usuario real del
      instituto
- [x] Inscripción a mesa en lote (checkboxes + buscador), mismo patrón
      que la inscripción a Comisión del módulo 4
- [x] Carga de resultados en lote por mesa (una fila por alumno
      inscripto, resultado + nota), mismo patrón que la carga de notas
      del módulo 5
- [x] Templates: index (próximos eventos), evento_form, listado_eventos,
      mesa_form, listado_mesas, ficha_mesa, inscripcion_mesa_lote,
      resultados_mesa_lote
- [x] Sidebar en `base_template.html`: submenú "Calendario" para
      `SECRETARIA` (acceso completo — crear eventos, crear mesas,
      inscribir, cargar resultados) y para `PRECEPTORA` (acceso de
      consulta — solo "Próximos eventos" y "Mesas de examen", sin links
      de alta/edición; **el control real de acceso sigue pendiente del
      punto abierto en el módulo 1**, esto solo esconde los links)
**Decisión pendiente de confirmar (no cerrada, revisar con el usuario real
del instituto):**
- `ESTADOS_CONSUMEN_INTENTO = {'Desaprobado', 'Ausente'}` en
  `calendario/validaciones.py` es un supuesto: que faltar a una mesa
  (`'Ausente'`) consume uno de los 3 intentos igual que desaprobarla. Si
  el instituto quiere que una ausencia NO cuente como intento rendido,
  hay que sacar `'Ausente'` de ese set.

## 8. Docentes
- [x] Modelo: `Docente` (app/materias/models.py)
- [x] Import de `Docente` en `materias/routes.py` (resuelto de paso al
      construir el módulo de Carreras y Materias, que ya lo necesitaba)
- [x] Rutas y templates propios de Docentes (alta/listado/ficha)

---

## Decisiones ya tomadas (no reabrir sin avisar)
- Login por email, almacenado internamente como `Usuario.username`.
- `Usuario.estado` es Boolean, no Enum de texto.
- Patrón Persona → Usuario/Alumno/Docente: siempre se crea la Persona
  primero (commit), después el registro dependiente.
- Fuente de verdad del esquema: `ModeloDatos.sql`. Los scripts
  SQL viejos (`Generar Base de datos V2.sql` y `V2 GEMINI.sql`) quedaron
  descartados.
- `Materias.carga_horaria_total`: se deja como está en el DDL, sin
  aclarar unidad. Interpretación adoptada (no forzada por constraint
  alguno): es el total de horas de todo el dictado de la materia según
  su `tipo_dictado` (si es `Cuatrimestral`, total del cuatrimestre; si es
  `Anual`, total del año) — no un valor normalizado a un año. Si en el
  futuro se necesita comparar carga horaria semanal entre materias
  anuales y cuatrimestrales, esto habrá que revisitarlo (posible campo
  auxiliar `carga_horaria_semanal`).
- `base_template.html` es el vigente (se descarta/ignora
  `base_template2.html` si no se usa en ningún `extends`). El proyecto
  usa Bootstrap 4.1.3, no Bootstrap 5 — cualquier template nuevo debe
  usar clases BS4 (`form-control` para selects, `text-right`,
  `form-inline`, etc.), no las de BS5 (`form-select`, `text-end`, `g-2`,
  `form-label`).
- Correlatividades solo se permiten entre materias de la misma carrera
  (restricción de UI/negocio; el DDL no lo impide).
- Al eliminar una `Carrera` con materias asociadas, se bloquea el borrado
  en vez de hacer cascada silenciosa.
- `UMBRAL_ALERTA_INASISTENCIA` (módulo 6) y `NOTA_MINIMA_APROBACION`
  (módulo 5) son constantes de código, no configuración editable desde
  la UI — decisión explícita del usuario, no agregar pantalla de
  configuración para esto sin avisar.
- `Asistencias` tiene `UNIQUE(id_inscripcion, fecha)` (constraint
  `uq_inscripcion_fecha`), tanto en el DDL como en el modelo. Cualquier
  alta directa de `Asistencia` (fuera de `Asistencia.registrar()`) debe
  contemplar que puede fallar por duplicado — usar siempre
  `Asistencia.registrar()` para cargar o editar.
- Un final SIEMPRE se rinde a través de una `MesaExamen` (módulo 7) — el
  módulo de Notas (5) no admite más instancia `'Final'` suelta. Ver
  ajuste pendiente anotado arriba en el punto 5.
- Un alumno desaprobado en un final sigue `'Regular'` (no cambia su
  `estado_cursada`) y puede volver a inscribirse a otra mesa, hasta un
  máximo de 3 intentos totales por materia (`MAX_INTENTOS_FINAL`).
- Una materia `modalidad_aprobacion='Promocional'` (pura) no puede tener
  Mesas de Examen asociadas — no tiene instancia de final.
- `MAX_INTENTOS_FINAL` (módulo 7) es constante de código, mismo criterio
  que `NOTA_MINIMA_APROBACION` (módulo 5) y `UMBRAL_ALERTA_INASISTENCIA`
  (módulo 6) — no editable desde la UI sin avisar.