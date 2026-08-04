-- ============================================================
-- SISTEMA DE GESTIÓN DE ALUMNOS - MODELO DE DATOS ACTUALIZADO
-- ============================================================
-- Cambios integrados respecto a la versión inicial:
--  1. Materias: se agrega modalidad de aprobación (Promocional/Final/Ambas)
--  2. Correlatividades: se distingue "Para Cursar" vs "Para Rendir Final"
--  3. Inscripciones: estado_cursada ampliado (Promocionado, Regular, Libre)
--  4. Nuevas tablas MesasExamen / InscripcionesMesa para gestionar
--     la inscripción y el resultado de los alumnos en cada mesa
--  5. Nueva tabla LogsAuditoria para el módulo de Seguridad
--  6. Personas: se elimina tipo_persona por ser redundante con Roles.
--     El rol de cada persona (Alumno, Docente, Secretaria, Preceptora,
--     Admin, etc.) queda como única fuente de verdad en Roles/Usuarios.
-- ============================================================
 
CREATE DATABASE gestion_academica;
USE gestion_academica;
 
-- ==========================================
-- 1. ENTIDADES DE PERSONAS Y SEGURIDAD
-- ==========================================
 
CREATE TABLE Personas (
    id_persona INT AUTO_INCREMENT PRIMARY KEY,
    dni VARCHAR(15) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    fecha_nacimiento DATE,
    email VARCHAR(100) UNIQUE,
    telefono VARCHAR(20),
    direccion VARCHAR(100)
);
 
CREATE TABLE Alumnos (
    id_persona INT PRIMARY KEY,
    legajo VARCHAR(20) UNIQUE NOT NULL,
    estado_academico ENUM('Regular', 'Libre', 'Egresado', 'Pasivo') DEFAULT 'Regular',
    FOREIGN KEY (id_persona) REFERENCES Personas(id_persona) ON DELETE CASCADE
);
 
CREATE TABLE Docentes (
    id_persona INT PRIMARY KEY,
    cuil VARCHAR(15) UNIQUE NOT NULL,
    especialidad TEXT,
    fecha_ingreso DATE,
    FOREIGN KEY (id_persona) REFERENCES Personas(id_persona) ON DELETE CASCADE
);
 
CREATE TABLE Roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL, -- 'Admin', 'Secretaria', 'Preceptora', 'Alumno', 'Docente'
    permisos TEXT
);
 
CREATE TABLE Usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- Siempre usar Hash, nunca texto plano
    id_rol INT,
    estado BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_persona) REFERENCES Personas(id_persona),
    FOREIGN KEY (id_rol) REFERENCES Roles(id_rol)
);
 
-- ==========================================
-- 2. ESTRUCTURA ACADÉMICA (PLAN DE ESTUDIOS)
-- ==========================================
 
CREATE TABLE Carreras (
    id_carrera INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    duracion_anios INT NOT NULL,
    codigo_plan VARCHAR(20) UNIQUE
);
 
CREATE TABLE Materias (
    id_materia INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    id_carrera INT NOT NULL,
    anio_sugerido INT NOT NULL,
    tipo_dictado ENUM('Anual', 'Cuatrimestral') DEFAULT 'Cuatrimestral',
    carga_horaria_total INT,
    -- NUEVO (punto 1): clasificación pedida explícitamente en la especificación
    modalidad_aprobacion ENUM('Promocional', 'Final', 'Ambas') NOT NULL DEFAULT 'Final',
    FOREIGN KEY (id_carrera) REFERENCES Carreras(id_carrera) ON DELETE CASCADE
);
 
CREATE TABLE Correlatividades (
    id_materia INT,
    id_materia_requerida INT,
    -- NUEVO (punto 2): distingue si la correlativa se pide para cursar
    -- o para rendir el final de la materia
    tipo_requisito ENUM('Para Cursar', 'Para Rendir Final') NOT NULL DEFAULT 'Para Cursar',
    PRIMARY KEY (id_materia, id_materia_requerida, tipo_requisito),
    FOREIGN KEY (id_materia) REFERENCES Materias(id_materia),
    FOREIGN KEY (id_materia_requerida) REFERENCES Materias(id_materia)
);
 
-- ==========================================
-- 3. GESTIÓN DE CURSADAS Y CALIFICACIONES
-- ==========================================
 
-- Comisiones: La puesta en marcha de una materia en un tiempo y espacio
CREATE TABLE Comisiones (
    id_comision INT AUTO_INCREMENT PRIMARY KEY,
    id_materia INT NOT NULL,
    id_docente INT NOT NULL, -- ID de la tabla Docentes (id_persona)
    ciclo_lectivo YEAR NOT NULL,
    cuatrimestre ENUM('1', '2', 'Anual') NOT NULL,
    turno ENUM('Mañana', 'Tarde', 'Noche') NOT NULL,
    cupo_maximo INT DEFAULT 30,
    FOREIGN KEY (id_materia) REFERENCES Materias(id_materia),
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_persona)
);
 
-- Inscripciones: El vínculo entre el Alumno y la Comisión específica
CREATE TABLE Inscripciones (
    id_inscripcion INT AUTO_INCREMENT PRIMARY KEY,
    id_alumno INT NOT NULL, -- ID de la tabla Alumnos (id_persona)
    id_comision INT NOT NULL,
    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- ACTUALIZADO (punto 3): se agregan 'Promocionado' y 'Libre', estados
    -- reales del progreso del alumno en una materia según la especificación
    estado_cursada ENUM(
        'Cursando',
        'Promocionado',
        'Regular',
        'Libre',
        'Aprobada',
        'Reprobada',
        'Abandonada'
    ) DEFAULT 'Cursando',
    FOREIGN KEY (id_alumno) REFERENCES Alumnos(id_persona),
    FOREIGN KEY (id_comision) REFERENCES Comisiones(id_comision),
    UNIQUE(id_alumno, id_comision)
);
 
CREATE TABLE Notas (
    id_nota INT AUTO_INCREMENT PRIMARY KEY,
    id_inscripcion INT NOT NULL,
    instancia ENUM('1er Parcial', '2do Parcial', 'Recuperatorio', 'Final', 'TP') NOT NULL,
    valor DECIMAL(4, 2) NOT NULL,
    fecha DATE NOT NULL,
    FOREIGN KEY (id_inscripcion) REFERENCES Inscripciones(id_inscripcion) ON DELETE CASCADE
);
 
CREATE TABLE Asistencias (
    id_asistencia INT AUTO_INCREMENT PRIMARY KEY,
    id_inscripcion INT NOT NULL,
    fecha DATE NOT NULL,
    estado ENUM('Presente', 'Ausente', 'Justificado') NOT NULL,
    FOREIGN KEY (id_inscripcion) REFERENCES Inscripciones(id_inscripcion) ON DELETE CASCADE
    UNIQUE (id_inscripcion, fecha) 
);
 
-- ==========================================
-- 4. EXTRAS Y EVENTOS
-- ==========================================
 
CREATE TABLE Eventos (
    id_evento INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME NOT NULL,
    tipo ENUM('Examen', 'Evento Académico', 'Feriado', 'Inscripciones') NOT NULL
);
 
-- NUEVO (punto 4): una mesa de examen es un Evento de tipo 'Examen'
-- vinculado a una materia puntual
CREATE TABLE MesasExamen (
    id_mesa INT AUTO_INCREMENT PRIMARY KEY,
    id_evento INT NOT NULL,
    id_materia INT NOT NULL,
    llamado ENUM('1er Llamado', '2do Llamado', '3er Llamado') DEFAULT '1er Llamado',
    FOREIGN KEY (id_evento) REFERENCES Eventos(id_evento) ON DELETE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES Materias(id_materia)
);
 
-- NUEVO (punto 4): inscripción de un alumno a una mesa de examen específica
-- y su resultado
CREATE TABLE InscripcionesMesa (
    id_mesa INT NOT NULL,
    id_alumno INT NOT NULL,
    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resultado ENUM('Pendiente', 'Aprobado', 'Desaprobado', 'Ausente') DEFAULT 'Pendiente',
    nota_final DECIMAL(4, 2),
    PRIMARY KEY (id_mesa, id_alumno),
    FOREIGN KEY (id_mesa) REFERENCES MesasExamen(id_mesa) ON DELETE CASCADE,
    FOREIGN KEY (id_alumno) REFERENCES Alumnos(id_persona)
);
 
-- ==========================================
-- 5. SEGURIDAD Y AUDITORÍA
-- ==========================================
 
-- NUEVO (punto 5): registro de acciones de los usuarios, requerido
-- explícitamente por el Módulo de Seguridad y Gestión de Usuarios
CREATE TABLE LogsAuditoria (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    accion VARCHAR(100) NOT NULL,          -- ej: 'ALTA', 'MODIFICACION', 'BAJA', 'LOGIN'
    entidad_afectada VARCHAR(50),          -- ej: 'Alumnos', 'Notas', 'Eventos'
    id_entidad_afectada INT,
    detalle TEXT,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);
 
-- ==========================================
-- 6. VISTAS DE CONVENIENCIA (VIEWs)
-- ==========================================
 
-- Vista para ver alumnos con sus datos personales unificados
CREATE VIEW vista_alumnos AS
SELECT a.legajo, p.dni, p.apellido, p.nombre, p.email, a.estado_academico
FROM Alumnos a
JOIN Personas p ON a.id_persona = p.id_persona;
 
-- Vista para ver el listado de clases (Comisiones) con nombres de materias y profes
CREATE VIEW vista_comisiones AS
SELECT c.id_comision, m.nombre AS materia, p.apellido AS profesor, c.ciclo_lectivo, c.turno
FROM Comisiones c
JOIN Materias m ON c.id_materia = m.id_materia
JOIN Personas p ON c.id_docente = p.id_persona;
 
-- NUEVA: vista para ver mesas de examen con materia y fecha del evento
CREATE VIEW vista_mesas_examen AS
SELECT me.id_mesa, m.nombre AS materia, m.modalidad_aprobacion,
       e.fecha_inicio, e.fecha_fin, me.llamado
FROM MesasExamen me
JOIN Materias m ON me.id_materia = m.id_materia
JOIN Eventos e ON me.id_evento = e.id_evento;
 
-- NUEVA: vista para ver el resultado de alumnos inscriptos a una mesa
CREATE VIEW vista_resultados_mesa AS
SELECT im.id_mesa, p.apellido, p.nombre, al.legajo, im.resultado, im.nota_final
FROM InscripcionesMesa im
JOIN Alumnos al ON im.id_alumno = al.id_persona
JOIN Personas p ON al.id_persona = p.id_persona;