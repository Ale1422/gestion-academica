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
- [ ] Decisión tomada: alta de Alumno NO crea Usuario/login — es solo
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
- [x] Modelo: `Nota` (app/secretaria/models.py) + relación `Inscripcion.notas`
- [x] Formularios: `NotaEntryForm`, `NotasLoteForm` (app/secretaria/forms.py)
- [x] Ruta: carga de notas en lote por comisión (`/comision/<id>/notas`),
      tabla con una fila por alumno inscripto (instancia + valor + fecha),
      filas vacías se ignoran, no frena el lote si una fila falla validación
- [x] Historial académico real en `alumno_ficha.html` (antes era un
      placeholder): tabla de inscripciones con estado y notas
- [x] `registrar_nota()` en validaciones.py: al cargar instancia 'Final'
      actualiza automáticamente `estado_cursada` (Aprobada/Reprobada) y
      bloquea Final en materias `modalidad_aprobacion='Promocional'`
      (cierra pendiente del módulo 2)

**Decisión pendiente de confirmar (no cerrada, revisar con el usuario real
del instituto):**
- `NOTA_MINIMA_APROBACION = 6` en `validaciones.py` es un default asumido,
  no un dato confirmado por el instituto. Ajustar ahí si corresponde otro
  valor.
- Solo la instancia `Final` dispara cambio automático de `estado_cursada`.
  `Recuperatorio` no automatiza nada porque el DDL no distingue si recupera
  un parcial o el final — si hace falta, hay que definir esa regla primero.

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

## 7. Calendario y Eventos
- [ ] Definir en qué blueprint vive (¿nuevo blueprint `calendario`?)
- [ ] Modelos: `Evento`, `MesaExamen`, `InscripcionMesa`
- [ ] Rutas: programar eventos/mesas, inscripción de alumnos a mesas
- [ ] Restringir alta de `MesaExamen` a materias con `modalidad_aprobacion`
      en `'Final'` o `'Ambas'` (una materia `'Promocional'` no tiene final)

## 8. Docentes
- [x] Modelo: `Docente` (app/materias/models.py)
- [x] Import de `Docente` en `materias/routes.py` (resuelto de paso al
      construir el módulo de Carreras y Materias, que ya lo necesitaba)
- [ ] Rutas y templates propios de Docentes (alta/listado/ficha)

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