import sqlite3
import os
import random
import string

class DBManager:
    def __init__(self, db_path='database/fleet.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        schema_path = os.path.join(os.path.dirname(__file__), '../database/schema.sql')
        with sqlite3.connect(self.db_path) as conn:
            with open(schema_path, 'r') as f:
                conn.executescript(f.read())
            
                                
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM camiones")
            if cursor.fetchone()[0] == 0:
                self._seed_data(conn)

    def _seed_data(self, conn):
        cursor = conn.cursor()
        
                                     
        modelos = ['Volvo FH16', 'Scania R500', 'Mercedes-Benz Actros', 'MAN TGX', 'Iveco S-Way']
        
        insert_camiones = []
        for _ in range(10):
            placa = f"{''.join(random.choices(string.ascii_uppercase, k=3))}-{random.randint(1000, 9999)}"
            modelo = random.choice(modelos)
            serial = f"ENG-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
            km = round(random.uniform(1000.0, 50000.0), 1)
            prox_maint = km + 10000.0
            estado = 'ACTIVO'
            insert_camiones.append((placa, modelo, serial, km, prox_maint, estado))
            
        cursor.executemany("""
            INSERT INTO camiones (placa, modelo, serial_motor, kilometraje, prox_cambio_aceite, estado) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, insert_camiones)
        
        cursor.executescript("""
            INSERT INTO conductores (licencia, nombre, telefono) VALUES 
            ('LIC-001', 'Juan Perez', '555-0101'),
            ('LIC-002', 'Maria Gonzalez', '555-0202'),
            ('LIC-003', 'Carlos Rodriguez', '555-0303'),
            ('LIC-004', 'Luis Martinez', '555-0404');
        """)
        conn.commit()

    def get_truck_info(self, placa):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM camiones WHERE placa = ?", (placa,))
            camion = cursor.fetchone()
            
            if not camion:
                return None
                
                                  
            cursor.execute("SELECT * FROM telemetria WHERE placa_camion = ? ORDER BY timestamp DESC LIMIT 1", (placa,))
            telemetria = cursor.fetchone()
            
                             
            cursor.execute("SELECT * FROM viajes WHERE placa_camion = ? AND estado = 'EN CURSO'", (placa,))
            viaje = cursor.fetchone()
            
            return {
                'camion': dict(camion),
                'telemetria': dict(telemetria) if telemetria else None,
                'viaje': dict(viaje) if viaje else None
            }

    def start_trip(self, placa, licencia, hex_code, punto_a, punto_b):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO viajes (placa_camion, licencia_conductor, codigo_hex, punto_a, punto_b) 
                VALUES (?, ?, ?, ?, ?)
            """, (placa, licencia, hex_code, punto_a, punto_b))
            conn.commit()

    def update_trip_binary(self, placa, bin_code):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE viajes SET codigo_bin = ? WHERE placa_camion = ? AND estado = 'EN CURSO'
            """, (bin_code, placa))
            conn.commit()

    def end_trip(self, placa):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE viajes SET estado = 'FINALIZADO', fecha_fin = CURRENT_TIMESTAMP 
                WHERE placa_camion = ? AND estado = 'EN CURSO'
            """, (placa,))
            conn.commit()

    def add_telemetry(self, placa, lat, lon, gas):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO telemetria (placa_camion, latitud, longitud, nivel_gasolina) 
                VALUES (?, ?, ?, ?)
            """, (placa, lat, lon, gas))
            conn.commit()

    def log_alert(self, placa, tipo, mensaje):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO alertas (placa_camion, tipo, mensaje) VALUES (?, ?, ?)
            """, (placa, tipo, mensaje))
            conn.commit()
            
    def get_all_trucks(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT placa FROM camiones")
            return [row['placa'] for row in cursor.fetchall()]

    def get_all_trucks_details(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM camiones")
            return [dict(row) for row in cursor.fetchall()]

    def get_trucks_by_state(self, estado):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT placa FROM camiones WHERE estado = ?", (estado,))
            return [row['placa'] for row in cursor.fetchall()]

    def register_truck(self, placa, modelo, serial_motor, prox_mantenimiento):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
                                                             
            cursor.execute("""
                INSERT INTO camiones (placa, modelo, serial_motor, kilometraje, prox_cambio_aceite, estado) 
                VALUES (?, ?, ?, 0.0, ?, 'ACTIVO')
            """, (placa, modelo, serial_motor, float(prox_mantenimiento)))
            conn.commit()

    def update_truck_state(self, placa, estado):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE camiones SET estado = ? WHERE placa = ?", (estado, placa))
            conn.commit()

    def get_general_reports(self, period):
        modifiers = {
            'semanal': '-7 days',
            'quincenal': '-15 days',
            'mensual': '-1 month',
            'trimestral': '-3 months',
            'semestral': '-6 months',
            'anual': '-1 year'
        }
        mod = modifiers.get(period, '-7 days')
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT 'VIAJE' as evento, placa_camion as placa, fecha_inicio as fecha, 
                       estado as estado_detalle, punto_a || ' -> ' || punto_b as ruta_mensaje 
                FROM viajes WHERE fecha_inicio >= date('now', '{mod}')
                UNION ALL
                SELECT 'ALERTA' as evento, placa_camion as placa, timestamp as fecha, 
                       tipo as estado_detalle, mensaje as ruta_mensaje 
                FROM alertas WHERE timestamp >= date('now', '{mod}')
                ORDER BY fecha DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
