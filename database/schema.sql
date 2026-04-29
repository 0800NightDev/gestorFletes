CREATE TABLE IF NOT EXISTS camiones (
    placa TEXT PRIMARY KEY,
    modelo TEXT NOT NULL,
    serial_motor TEXT UNIQUE NOT NULL,
    kilometraje REAL DEFAULT 0.0,
    prox_cambio_aceite REAL DEFAULT 10000.0, -- km target para el 2do cambio etc.
    estado TEXT DEFAULT 'ACTIVO'
);

CREATE TABLE IF NOT EXISTS conductores (
    licencia TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    telefono TEXT
);

CREATE TABLE IF NOT EXISTS viajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placa_camion TEXT NOT NULL,
    licencia_conductor TEXT NOT NULL,
    codigo_hex TEXT,
    codigo_bin TEXT,
    estado TEXT DEFAULT 'EN CURSO', -- EN CURSO, FINALIZADO
    punto_a TEXT,
    punto_b TEXT,
    fecha_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_fin DATETIME,
    FOREIGN KEY (placa_camion) REFERENCES camiones(placa),
    FOREIGN KEY (licencia_conductor) REFERENCES conductores(licencia)
);

CREATE TABLE IF NOT EXISTS telemetria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placa_camion TEXT NOT NULL,
    latitud REAL,
    longitud REAL,
    nivel_gasolina REAL, -- Porcentaje 0 a 100
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (placa_camion) REFERENCES camiones(placa)
);

CREATE TABLE IF NOT EXISTS alertas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placa_camion TEXT NOT NULL,
    tipo TEXT NOT NULL, -- DETENCION_PROLONGADA, MANTENIMIENTO, etc.
    mensaje TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    resuelta INTEGER DEFAULT 0,
    FOREIGN KEY (placa_camion) REFERENCES camiones(placa)
);
