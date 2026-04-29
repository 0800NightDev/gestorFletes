from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame,
                             QPushButton, QLabel, QLineEdit, QMessageBox, QFormLayout, QGridLayout)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QDoubleValidator

class TrucksWindow(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()

    def init_ui(self):
        self.setObjectName("MainContent")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Gestión de Camiones")
        title.setObjectName("Title")
        layout.addWidget(title)

                                                           
        main_layout = QHBoxLayout()
        
                                                                                                                           
        form_panel = QWidget()
        form_layout = QVBoxLayout(form_panel)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        form_title = QLabel("Registrar Nuevo Camión")
        form_title.setObjectName("Subtitle")
        form_layout.addWidget(form_title)
        
        f_layout = QFormLayout()
        self.input_placa = QLineEdit()
        self.input_placa.setPlaceholderText("Ej. ABC-1234")
        self.input_placa.setMaxLength(10)
        placa_validator = QRegularExpressionValidator(QRegularExpression(r"^[A-Za-z0-9-]+$"))
        self.input_placa.setValidator(placa_validator)
        
        self.input_modelo = QLineEdit()
        self.input_modelo.setPlaceholderText("Ej. Volvo FH16")
        self.input_modelo.setMaxLength(30)
        
        self.input_serial = QLineEdit()
        self.input_serial.setPlaceholderText("Ej. ENG-000000")
        self.input_serial.setMaxLength(20)
        serial_validator = QRegularExpressionValidator(QRegularExpression(r"^[A-Za-z0-9-]+$"))
        self.input_serial.setValidator(serial_validator)
        
        self.input_prox_mantenimiento = QLineEdit()
        self.input_prox_mantenimiento.setPlaceholderText("Target en km (Ej. 10000)")
        double_validator = QDoubleValidator(0.0, 9999999.0, 2)
        double_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.input_prox_mantenimiento.setValidator(double_validator)
        
        f_layout.addRow("Placa:", self.input_placa)
        f_layout.addRow("Modelo:", self.input_modelo)
        f_layout.addRow("Serial de Motor:", self.input_serial)
        f_layout.addRow("Prox. Mantenimiento:", self.input_prox_mantenimiento)
        
        form_layout.addLayout(f_layout)
        
        register_btn = QPushButton("Registrar Camión")
        register_btn.clicked.connect(self.register_truck)
        form_layout.addWidget(register_btn)
        
                                                 
        list_panel = QWidget()
        list_layout = QVBoxLayout(list_panel)
        list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        top_list_layout = QHBoxLayout()
        list_title = QLabel("Camiones en Flota")
        list_title.setObjectName("Subtitle")
        
        refresh_btn = QPushButton("Actualizar")
        refresh_btn.clicked.connect(self.load_trucks)
        
        top_list_layout.addWidget(list_title)
        top_list_layout.addStretch()
        top_list_layout.addWidget(refresh_btn)
        list_layout.addLayout(top_list_layout)
        
                               
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.cards_layout.setSpacing(15)
        
        self.scroll_area.setWidget(self.cards_container)
        list_layout.addWidget(self.scroll_area)
        
                                            
        main_layout.addWidget(form_panel, 1)               
        main_layout.addWidget(list_panel, 2)               
        
        layout.addLayout(main_layout)
        self.setLayout(layout)
        
                                
        self.load_trucks()

    def load_trucks(self):
        camiones = self.db.get_all_trucks_details()
        
                             
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        card_style = """
            QFrame {
                background-color: #1e2736;
                border-radius: 10px;
                border: 1px solid #37474f;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """
        
        col = 0
        row = 0
        max_cols = 2
        
        for camion in camiones:
            card = QFrame()
            card.setStyleSheet(card_style)
            card.setMinimumHeight(120)
            
            c_layout = QVBoxLayout(card)
            
                                    
            header_layout = QHBoxLayout()
            placa_lbl = QLabel(camion['placa'])
            placa_lbl.setStyleSheet("color: #64b5f6; font-weight: bold; font-size: 18px;")
            
            estado = camion['estado']
            if estado == "ACTIVO":
                color_estado = "#4caf50"
            elif estado == "EN RUTA":
                color_estado = "#ffb300"
            elif estado == "ACCIDENTE":
                color_estado = "#f44336"
            else:
                color_estado = "#e0e0e0"
                
            estado_lbl = QLabel(f"● {estado}")
            estado_lbl.setStyleSheet(f"color: {color_estado}; font-weight: bold; font-size: 14px;")
            
            header_layout.addWidget(placa_lbl)
            header_layout.addStretch()
            header_layout.addWidget(estado_lbl)
            c_layout.addLayout(header_layout)
            
                                      
            info_style = "color: #e0e0e0; font-size: 13px;"
            modelo_lbl = QLabel(f"<b>Modelo:</b> {camion['modelo']}")
            modelo_lbl.setStyleSheet(info_style)
            
            serial_lbl = QLabel(f"<b>Serial:</b> {camion['serial_motor']}")
            serial_lbl.setStyleSheet(info_style)
            
            km_lbl = QLabel(f"<b>Kilometraje:</b> {camion['kilometraje']} km")
            km_lbl.setStyleSheet(info_style)
            
            c_layout.addWidget(modelo_lbl)
            c_layout.addWidget(serial_lbl)
            c_layout.addWidget(km_lbl)
            c_layout.addStretch()
            
            self.cards_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def register_truck(self):
        placa = self.input_placa.text().strip().upper()
        modelo = self.input_modelo.text().strip()
        serial = self.input_serial.text().strip()
        prox_mantenimiento = self.input_prox_mantenimiento.text().strip()
        
        if not all([placa, modelo, serial, prox_mantenimiento]):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return
            
        try:
            float(prox_mantenimiento)
        except ValueError:
            QMessageBox.warning(self, "Error", "El próximo mantenimiento debe ser un número (kilómetros).")
            return
            
        try:
            self.db.register_truck(placa, modelo, serial, prox_mantenimiento)
            QMessageBox.information(self, "Éxito", f"Camión {placa} registrado correctamente.")
                            
            self.input_placa.clear()
            self.input_modelo.clear()
            self.input_serial.clear()
            self.input_prox_mantenimiento.clear()
                              
            self.load_trucks()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo registrar el camión. Revisa si la placa o serial ya existen.\nDetalle: {str(e)}")
