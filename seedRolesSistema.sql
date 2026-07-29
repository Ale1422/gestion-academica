-- ============================================================
-- SCRIPT: Alta de los roles del sistema (tabla Roles)
-- ============================================================
-- Roles definidos en la especificación funcional del proyecto.
-- Idempotente: se puede correr varias veces sin duplicar registros.
--
-- Recordatorio: 'permisos' es texto libre / documentación, no se
-- parsea en el código. La autorización real se hace comparando
-- Usuario.get_rol() contra el nombre_rol exacto (sin importar
-- mayúsculas/minúsculas) dentro de role_required() / admin_required()
-- en app/auth/decorators.py.
-- ============================================================

USE gestion_academica_pro;

-- 1. Administrador del Sistema
-- Usado en el código como 'Administrador' (ver login() y admin_required)
INSERT INTO Roles (nombre_rol, permisos)
SELECT 'Administrador',
       'Acceso completo al sistema. Gestion de roles y permisos, '
       'autenticacion de usuarios, auditoria de actividades, '
       'encriptacion de datos, supervision de todos los modulos.'
WHERE NOT EXISTS (
    SELECT 1 FROM Roles WHERE nombre_rol = 'Administrador'
);

-- 2. Secretaria
INSERT INTO Roles (nombre_rol, permisos)
SELECT 'Secretaria',
       'Gestion de Alumnos (alta, edicion, estados academicos, notas), '
       'consulta de Carreras y Materias, programacion de Calendario y '
       'Eventos (mesas de examen, jornadas academicas).'
WHERE NOT EXISTS (
    SELECT 1 FROM Roles WHERE nombre_rol = 'Secretaria'
);

-- 3. Preceptora
INSERT INTO Roles (nombre_rol, permisos)
SELECT 'Preceptora',
       'Registro y consulta de asistencia diaria de alumnos, generacion '
       'de reportes de asistencia, consulta de Calendario y Eventos.'
WHERE NOT EXISTS (
    SELECT 1 FROM Roles WHERE nombre_rol = 'Preceptora'
);

-- 4. Administrador Académico
INSERT INTO Roles (nombre_rol, permisos)
SELECT 'Administrador Academico',
       'Creacion y modificacion de Carreras y Materias, definicion de '
       'correlatividades, actualizacion de planes de estudio.'
WHERE NOT EXISTS (
    SELECT 1 FROM Roles WHERE nombre_rol = 'Administrador Academico'
);

-- Verificación
SELECT id_rol, nombre_rol, permisos FROM Roles ORDER BY id_rol;