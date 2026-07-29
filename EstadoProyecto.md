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

## 2. Carreras y Materias
- [ ] Modelos: `Carrera`, `Materia`, `Correlatividad`
- [ ] Rutas y templates: alta/listado de carreras y materias
- [ ] Gestión de correlatividades (para cursar / para rendir final)

## 3. Alumnos (Secretaria)
- [x] Modelo: `Alumno` (app/secretaria/models.py)
- [ ] Import de `Alumno` en `secretaria/routes.py` (pendiente, necesario
      para que SQLAlchemy registre la clase)
- [ ] Rutas: alta, edición, listado, ficha de alumno
- [ ] Templates correspondientes

## 4. Comisiones e Inscripciones
- [ ] Modelos: `Comision`, `Inscripcion`
- [ ] Rutas: crear comisión (materia + docente + ciclo lectivo),
      inscribir alumno a comisión

## 5. Notas
- [ ] Modelo: `Nota`
- [ ] Rutas: carga de notas por inscripción, historial académico del alumno

## 6. Asistencia (Preceptoria)
- [ ] Modelo: `Asistencia`
- [ ] Rutas: registro diario, historial por alumno, alertas de inasistencia

## 7. Calendario y Eventos
- [ ] Definir en qué blueprint vive (¿nuevo blueprint `calendario`?)
- [ ] Modelos: `Evento`, `MesaExamen`, `InscripcionMesa`
- [ ] Rutas: programar eventos/mesas, inscripción de alumnos a mesas

## 8. Docentes (mejora futura, sin apuro)
- [x] Modelo: `Docente` (app/materias/models.py)
- [ ] Import de `Docente` en `materias/routes.py`
- [ ] Rutas y templates

---

## Decisiones ya tomadas (no reabrir sin avisar)
- Login por email, almacenado internamente como `Usuario.username`.
- `Usuario.estado` es Boolean, no Enum de texto.
- Patrón Persona → Usuario/Alumno/Docente: siempre se crea la Persona
  primero (commit), después el registro dependiente.
- Fuente de verdad del esquema: `gestion_academica_pro.sql`. Los scripts
  SQL viejos (`Generar Base de datos V2.sql` y `V2 GEMINI.sql`) quedaron
  descartados.