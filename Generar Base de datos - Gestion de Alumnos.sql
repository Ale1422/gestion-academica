CREATE DATABASE gestion_alumnos;
USE gestion_alumnos;

CREATE TABLE Alumnos (
    id_alumno INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    direccion VARCHAR(100),
    correo VARCHAR(100),
    telefono VARCHAR(20),
    estado_academico ENUM('Regular', 'Libre', 'Promocionado') DEFAULT 'Regular'
);

CREATE TABLE Carreras (
    id_carrera INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

CREATE TABLE Materias (
    id_materia INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    id_carrera INT NOT NULL,
    tipo ENUM('Promocional', 'Final') DEFAULT 'Promocional',
    anio INT NOT NULL,
    FOREIGN KEY (id_carrera) REFERENCES Carreras(id_carrera) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Correlatividades (
    id_materia INT,
    id_materia_correlativa INT,
    PRIMARY KEY (id_materia, id_materia_correlativa),
    FOREIGN KEY (id_materia) REFERENCES Materias(id_materia) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_materia_correlativa) REFERENCES Materias(id_materia) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Inscripciones (
    id_inscripcion INT AUTO_INCREMENT PRIMARY KEY,
    id_alumno INT NOT NULL,
    id_materia INT NOT NULL,
    fecha_inscripcion DATE NOT NULL,
    FOREIGN KEY (id_alumno) REFERENCES Alumnos(id_alumno) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES Materias(id_materia) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Notas (
    id_nota INT AUTO_INCREMENT PRIMARY KEY,
    id_alumno INT NOT NULL,
    id_materia INT NOT NULL,
    nota DECIMAL(4, 2) NOT NULL,
    fecha DATE NOT NULL,
    FOREIGN KEY (id_alumno) REFERENCES Alumnos(id_alumno) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES Materias(id_materia) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Asistencias (
    id_asistencia INT AUTO_INCREMENT PRIMARY KEY,
    id_alumno INT NOT NULL,
    id_materia INT NOT NULL,
    fecha DATE NOT NULL,
    asistio BOOLEAN NOT NULL,
    FOREIGN KEY (id_alumno) REFERENCES Alumnos(id_alumno) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES Materias(id_materia) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Eventos (
    id_evento INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    fecha DATE NOT NULL,
    tipo ENUM('Examen', 'Evento Académico', 'Acto Institucional') NOT NULL
);

CREATE TABLE Roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Nombre_Rol VARCHAR(50) NOT NULL,
    Permisos TEXT
);

-- CREATE TABLE Usuarios (
--     id_usuario INT AUTO_INCREMENT PRIMARY KEY,
--     nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
--     contrasena VARCHAR(255) NOT NULL,
--     rol ENUM('Secretaria', 'Preceptora', 'Administrador') NOT NULL
-- );

CREATE TABLE Usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(50) NOT NULL,
    Apellido VARCHAR(50) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Contraseña VARCHAR(255) NOT NULL,
    Rol INT,
    Fecha_Creación TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Estado ENUM('activo', 'inactivo') DEFAULT 'activo',
    FOREIGN KEY (Rol) REFERENCES Roles(id)
);

CREATE TABLE Logs_Acceso (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    accion VARCHAR(255) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id) 
        ON DELETE CASCADE ON UPDATE CASCADE
);
