-- ============================================================
-- SCRIPT: Crear usuario Administrador inicial
-- ============================================================
-- Contraseña en texto plano (guardarla, no se puede recuperar
-- desde el hash): !CY%u3jW0KRb@J=7
--
-- El hash fue generado con Werkzeug 2.0.3 (misma versión que usa
-- el proyecto, ver requirements.txt) usando
-- generate_password_hash(), método pbkdf2:sha256.
-- Si cambiás el algoritmo de hashing en el futuro, este hash
-- dejará de ser válido y habrá que regenerarlo.
-- ============================================================

USE gestion_academica_pro;

-- 1. Rol Administrador (si no existe ya)
INSERT INTO Roles (nombre_rol, permisos)
SELECT 'Administrador', 'Acceso completo al sistema'
WHERE NOT EXISTS (
    SELECT 1 FROM Roles WHERE nombre_rol = 'Administrador'
);

-- 2. Persona asociada al usuario admin
INSERT INTO Personas (dni, nombre, apellido, email)
VALUES ('00000000', 'ADMIN', 'SISTEMA', 'ADMIN@INSTITUTO.EDU');

-- 3. Usuario admin, vinculado a la Persona y al Rol recién creados
INSERT INTO Usuarios (id_persona, username, password_hash, id_rol, estado)
VALUES (
    LAST_INSERT_ID(),  -- id_persona de la Persona insertada arriba
    'ADMIN@INSTITUTO.EDU',
    'pbkdf2:sha256:260000$KqEu4WSzIEb6AUfN$5333d4d3c2d40cf6762832a6ed05b43c0d3e0921dcfbff816d0b37097e71abf1',
    (SELECT id_rol FROM Roles WHERE nombre_rol = 'Administrador'),
    TRUE
);

-- Verificación rápida
SELECT u.id_usuario, u.username, p.nombre, p.apellido, r.nombre_rol
FROM Usuarios u
JOIN Personas p ON u.id_persona = p.id_persona
JOIN Roles r ON u.id_rol = r.id_rol
WHERE u.username = 'ADMIN@INSTITUTO.EDU';
