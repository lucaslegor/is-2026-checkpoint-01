CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    legajo VARCHAR(50) UNIQUE NOT NULL,
    feature VARCHAR(50) NOT NULL,
    servicio VARCHAR(50) NOT NULL,
    estado VARCHAR(20) DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO','INACTIVO'))
);

INSERT INTO members (nombre, apellido, legajo, feature, servicio) 
VALUES
    ('Lucas','Legorburu','33497','Feature 01','Infraestructura y coordinación'),
    ('Tomas','Bellizzi','33431','Feature 02','Frontend'),
    ('Luca','Giordani','33382','Feature 03','Backend'),
    ('Facundo','Devida','33539','Feature 04','Base de datos'),
    ('Joaquin','Rodriguez','33402','Feature 05','Panel de monitoreo'),
    ('Leonel','Piquet','33725','Feature 06','Administración BD');