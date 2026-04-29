from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
                             QPushButton, QLabel, QFrame, QMessageBox, QScrollArea, QSplitter)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
import os
import folium
import io
import requests
from core.freight_validator import FreightValidator
from views.components.circular_gauge import CircularGauge

class DashboardWindow(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_placa = None
        self.init_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_realtime_data)
        self.timer.start(2000)

    def init_ui(self):
        self.setObjectName("MainContent")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

                                        
        search_layout = QHBoxLayout()
        search_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        lbl_disp = QLabel("Disponibles:")
        search_layout.addWidget(lbl_disp)
        
        self.combo_disponibles = QComboBox()
        self.combo_disponibles.setMinimumWidth(180)
        self.combo_disponibles.activated.connect(lambda: self.on_truck_selected('disponibles'))
        search_layout.addWidget(self.combo_disponibles)
        
        search_layout.addSpacing(30)
        
        lbl_ruta = QLabel("En Ruta:")
        search_layout.addWidget(lbl_ruta)
        
        self.combo_en_ruta = QComboBox()
        self.combo_en_ruta.setMinimumWidth(180)
        self.combo_en_ruta.activated.connect(lambda: self.on_truck_selected('en_ruta'))
        search_layout.addWidget(self.combo_en_ruta)
        
        self.refresh_trucks()
        
        search_layout.addStretch()
        layout.addLayout(search_layout)

                  
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
                          
        self.map_panel = QWidget()
        map_layout = QVBoxLayout(self.map_panel)
        map_layout.setContentsMargins(0, 0, 0, 0)
        
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.join(os.path.dirname(__file__), '../svg/logo_letras.svg')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
            
        self.web_view = QWebEngineView()
        self.web_view.setVisible(False)
        
        map_layout.addWidget(self.logo_label)
        map_layout.addWidget(self.web_view)
        
                                  
        self.info_scroll = QScrollArea()
        self.info_scroll.setWidgetResizable(True)
        self.info_scroll.setVisible(False)
        
        info_container = QWidget()
        self.info_layout = QVBoxLayout(info_container)
        self.info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.info_layout.setSpacing(15)
        
        self.build_cards()
        self.info_scroll.setWidget(info_container)
        
        self.splitter.addWidget(self.map_panel)
        self.splitter.addWidget(self.info_scroll)
        self.splitter.setStretchFactor(0, 6)
        self.splitter.setStretchFactor(1, 4)
        
        layout.addWidget(self.splitter)

    def refresh_trucks(self):
        self.combo_disponibles.clear()
        self.combo_en_ruta.clear()
        
        self.combo_disponibles.addItem("")
        self.combo_en_ruta.addItem("")
        
        disp = self.db.get_trucks_by_state("ACTIVO")
        ruta = self.db.get_trucks_by_state("EN RUTA")
        
        if disp: self.combo_disponibles.addItems(disp)
        if ruta: self.combo_en_ruta.addItems(ruta)

    def on_truck_selected(self, source):
        if source == 'disponibles':
            placa = self.combo_disponibles.currentText().strip().upper()
            if placa:
                                                                          
                self.combo_en_ruta.blockSignals(True)
                self.combo_en_ruta.setCurrentIndex(0)
                self.combo_en_ruta.blockSignals(False)
                self.search_truck(placa)
        else:
            placa = self.combo_en_ruta.currentText().strip().upper()
            if placa:
                self.combo_disponibles.blockSignals(True)
                self.combo_disponibles.setCurrentIndex(0)
                self.combo_disponibles.blockSignals(False)
                self.search_truck(placa)

    def search_truck(self, placa):
        if not placa: return
        info = self.db.get_truck_info(placa)
        if info:
            if placa != self.current_placa:
                self.punto_a_input.setText("Caracas, Clinicas Piedra Azul")
                self.punto_b_input.setText("")
            self.current_placa = placa
            self.logo_label.setVisible(False)
            self.web_view.setVisible(True)
            self.info_scroll.setVisible(True)
            self.update_ui_with_info(info)
        else:
            self.current_placa = None
            self.info_scroll.setVisible(False)
            self.web_view.setVisible(False)
            self.logo_label.setVisible(True)
            QMessageBox.warning(self, "Error", "Camión no encontrado")

    def build_cards(self):
        card_style = "QFrame { border: 1px solid palette(divider); border-radius: 8px; } QLabel { border: none; }"
        
                           
        card1 = QFrame()
        card1.setStyleSheet(card_style)
        c1_layout = QVBoxLayout(card1)
        self.truck_lbl = QLabel("Camión: -")
        self.truck_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.engine_lbl = QLabel("Serial: -")
        self.driver_lbl = QLabel("Conductor: -")
        c1_layout.addWidget(self.truck_lbl)
        c1_layout.addWidget(self.engine_lbl)
        c1_layout.addWidget(self.driver_lbl)
        self.info_layout.addWidget(card1)
        
                            
        card2 = QFrame()
        card2.setStyleSheet(card_style)
        c2_layout = QHBoxLayout(card2)
        
        data_layout = QVBoxLayout()
        self.location_lbl = QLabel("GPS: Calculando...")
        self.km_lbl = QLabel("Km: -")
        self.eta_lbl = QLabel("ETA: -")
        data_layout.addWidget(self.location_lbl)
        data_layout.addWidget(self.km_lbl)
        data_layout.addWidget(self.eta_lbl)
        
        self.gas_gauge = CircularGauge()
        self.gas_gauge.setFixedSize(100, 100)
        
        c2_layout.addLayout(data_layout)
        c2_layout.addWidget(self.gas_gauge)
        self.info_layout.addWidget(card2)
        
                                      
        card3 = QFrame()
        card3.setStyleSheet(card_style + " QLineEdit { font-family: monospace; }")
        c3_layout = QVBoxLayout(card3)
        self.trip_status_lbl = QLabel("Estado del Viaje: -")
        c3_layout.addWidget(self.trip_status_lbl)
        
                                
        ruta_layout = QHBoxLayout()
        self.punto_a_input = QLineEdit()
        self.punto_a_input.setPlaceholderText("Origen (Ej. Caracas)")
        self.punto_b_input = QLineEdit()
        self.punto_b_input.setPlaceholderText("Destino (Ej. Maracaibo)")
        ruta_layout.addWidget(self.punto_a_input)
        ruta_layout.addWidget(self.punto_b_input)
        c3_layout.addLayout(ruta_layout)

        c3_layout.addWidget(QLabel("HEX (Salida):"))
        self.hex_input = QLineEdit()
        self.hex_input.setReadOnly(True)
        c3_layout.addWidget(self.hex_input)
        
        c3_layout.addWidget(QLabel("BIN (Tránsito):"))
        self.bin_input = QLineEdit()
        self.bin_input.setReadOnly(True)
        c3_layout.addWidget(self.bin_input)
        
        action_layout = QHBoxLayout()
        self.start_trip_btn = QPushButton("Iniciar Viaje")
        self.start_trip_btn.clicked.connect(self.start_trip)
        self.validate_arrival_btn = QPushButton("Validar Llegada")
        self.validate_arrival_btn.clicked.connect(self.validate_arrival)
        
        self.accident_btn = QPushButton("Reportar Accidente")
        self.accident_btn.clicked.connect(self.report_accident)
        self.accident_btn.setStyleSheet("background-color: #d32f2f; color: white;")
        self.accident_btn.setEnabled(False)
        
        action_layout.addWidget(self.start_trip_btn)
        action_layout.addWidget(self.validate_arrival_btn)
        action_layout.addWidget(self.accident_btn)
        c3_layout.addLayout(action_layout)
        
        self.info_layout.addWidget(card3)



    def generate_map(self, lat, lon):
        m = folium.Map(location=[lat, lon], zoom_start=14, control_scale=True)
        folium.Marker(
            [lat, lon], 
            popup=self.current_placa, 
            icon=folium.Icon(color="blue", icon="truck", prefix='fa')
        ).add_to(m)
        
        data = io.BytesIO()
        m.save(data, close_file=False)
        self.web_view.setHtml(data.getvalue().decode())

    def update_ui_with_info(self, info):
        camion = info['camion']
        estado_camion = camion['estado']
        color = "red" if estado_camion == "ACCIDENTE" else "green" if estado_camion == "EN RUTA" else "white"
        
        self.truck_lbl.setText(f"{camion['modelo']} - {camion['placa']} (<span style='color:{color};'>{estado_camion}</span>)")
        self.truck_lbl.setTextFormat(Qt.TextFormat.RichText)
        
        self.engine_lbl.setText(f"Serial: {camion['serial_motor']}")
        self.km_lbl.setText(f"Km: {camion['kilometraje']}")

        viaje = info['viaje']
        if viaje:
            self.driver_lbl.setText(f"Cond: {viaje['licencia_conductor']}")
            self.trip_status_lbl.setText(f"Estado: {viaje['estado']}")
            self.hex_input.setText(viaje['codigo_hex'])
            self.bin_input.setText(viaje['codigo_bin'] or 'No convertido')
            self.punto_a_input.setText(viaje['punto_a'])
            self.punto_b_input.setText(viaje['punto_b'])
            self.punto_a_input.setEnabled(False)
            self.punto_b_input.setEnabled(False)
            self.start_trip_btn.setEnabled(False)
            self.validate_arrival_btn.setEnabled(True)
            self.accident_btn.setEnabled(estado_camion != "ACCIDENTE")
        else:
            self.driver_lbl.setText("Cond: N/A")
            self.trip_status_lbl.setText("Estado: SIN VIAJE")
            self.hex_input.setText("")
            self.bin_input.setText("")
            self.punto_a_input.setEnabled(True)
            self.punto_b_input.setEnabled(True)
            
                                                                                  
            if not self.start_trip_btn.isEnabled():
                self.punto_b_input.setText("")
                self.punto_a_input.setText("Caracas, Clinicas Piedra Azul")
                
            self.start_trip_btn.setEnabled(estado_camion != "ACCIDENTE")
            self.validate_arrival_btn.setEnabled(False)
            self.accident_btn.setEnabled(False)

        telemetria = info['telemetria']
        if telemetria:
            lat = telemetria['latitud']
            lon = telemetria['longitud']
            self.location_lbl.setText(f"GPS: {lat:.4f}, {lon:.4f}")
            self.gas_gauge.setValue(telemetria['nivel_gasolina'])
            
                                                
            app_window = self.window()
            eta_text = "N/A"
            if hasattr(app_window, 'telemetry'):
                state = app_window.telemetry.truck_states.get(self.current_placa, {})
                eta_text = state.get('eta_text', 'N/A')
            self.eta_lbl.setText(f"ETA: {eta_text}")
            
            if not hasattr(self, 'last_lat') or abs(self.last_lat - lat) > 0.0001:
                self.last_lat = lat
                self.generate_map(lat, lon)
        else:
            self.location_lbl.setText("GPS: (Sin datos)")
            self.gas_gauge.setValue(0)

    def update_realtime_data(self):
                                                                               
        activos = self.db.get_trucks_by_state("ACTIVO")
        if (self.combo_disponibles.count() - 1) != len(activos):
            disp_sel = self.combo_disponibles.currentText()
            ruta_sel = self.combo_en_ruta.currentText()
            
            self.refresh_trucks()
            
                                    
            if disp_sel: self.combo_disponibles.setCurrentText(disp_sel)
            if ruta_sel: self.combo_en_ruta.setCurrentText(ruta_sel)
            
        if self.current_placa:
            info = self.db.get_truck_info(self.current_placa)
            if info:
                self.update_ui_with_info(info)

    def geocode_city(self, city):
        """Consulta Nominatim (OSM) para obtener latitud y longitud de una ciudad"""
        url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
        try:
                                                       
            headers = {'User-Agent': 'AlexanderMoyaFleetApp/1.0'}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 0:
                    return float(data[0]['lat']), float(data[0]['lon'])
        except Exception as e:
            print(f"Error geocoding {city}: {e}")
        return None, None

    def start_trip(self):
        if not self.current_placa: return
        punto_a = self.punto_a_input.text().strip()
        punto_b = self.punto_b_input.text().strip()
        
        if not punto_a or not punto_b:
            QMessageBox.warning(self, "Error", "Debe especificar el Punto A (Origen) y Punto B (Destino).")
            return
            
                      
        self.start_trip_btn.setText("Geocodificando...")
        self.start_trip_btn.setEnabled(False)
        QApplication.processEvents()                             
        
        lat1, lon1 = self.geocode_city(punto_a)
        lat2, lon2 = self.geocode_city(punto_b)
        
        if not lat1 or not lat2:
            QMessageBox.critical(self, "Error de Geocodificación", "No se pudo encontrar la ubicación exacta de las ciudades especificadas en OpenStreetMap.")
            self.start_trip_btn.setText("Iniciar Viaje")
            self.start_trip_btn.setEnabled(True)
            return

        licencia = "LIC-001" 
        codigo_base = f"FLETE-{self.current_placa}-{punto_b}"
        hex_code = FreightValidator.generate_hex_code(codigo_base)
        
        self.db.start_trip(self.current_placa, licencia, hex_code, punto_a, punto_b)
        bin_code = FreightValidator.hex_to_bin(hex_code)
        self.db.update_trip_binary(self.current_placa, bin_code)
        
                                                
        self.db.update_truck_state(self.current_placa, "EN RUTA")
        
                                                                                            
        app_window = self.window()
        if hasattr(app_window, 'telemetry'):
            app_window.telemetry.start_custom_route(self.current_placa, lat1, lon1, lat2, lon2)
            
        self.start_trip_btn.setText("Iniciar Viaje")
        QMessageBox.information(self, "Viaje Iniciado", f"Ruta trazada.\nCódigo HEX emitido: {hex_code}")
        self.update_realtime_data()

    def report_accident(self):
        if not self.current_placa: return
        reply = QMessageBox.question(self, "Confirmar Accidente", 
                                     f"¿Está seguro de reportar un accidente para el camión {self.current_placa}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.update_truck_state(self.current_placa, "ACCIDENTE")
            self.db.log_alert(self.current_placa, "ACCIDENTE", f"El camión {self.current_placa} sufrió un accidente en ruta.")
            
                                  
            app_window = self.window()
            if hasattr(app_window, 'telemetry'):
                app_window.telemetry.stop_truck(self.current_placa)
                
            QMessageBox.critical(self, "Alerta de Accidente", "Accidente registrado. Unidades de emergencia han sido notificadas.")
            self.update_realtime_data()

    def validate_arrival(self):
        if not self.current_placa: return
        info = self.db.get_truck_info(self.current_placa)
        viaje = info['viaje']
        if not viaje: return
        
        hex_original = viaje['codigo_hex']
        bin_transito = viaje['codigo_bin']
        is_valid, hex_llegada = FreightValidator.validate_arrival(hex_original, bin_transito)
        
        if is_valid:
            QMessageBox.information(self, "Validación Exitosa (2 Puntos)", 
                f"El código coincide.\nHEX Original: {hex_original}\nHEX Llegada: {hex_llegada}\nFlete entregado.")
            self.db.end_trip(self.current_placa)
            self.db.update_truck_state(self.current_placa, "ACTIVO")
        else:
            QMessageBox.critical(self, "Error", "Los códigos no coinciden. Posible manipulación.")
        
        self.update_realtime_data()
