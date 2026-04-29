from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QHeaderView)
from PyQt6.QtCore import Qt
import openpyxl

class ReportsWindow(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()

    def init_ui(self):
        self.setObjectName("MainContent")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Reporte Global de Flota")
        title.setObjectName("Title")
        layout.addWidget(title)

                  
        controls_layout = QHBoxLayout()
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["semanal", "quincenal", "mensual", "trimestral", "semestral", "anual"])
        
        gen_btn = QPushButton("Generar Reporte Global")
        gen_btn.clicked.connect(self.generate_report)
        
        export_btn = QPushButton("Exportar a Excel (.xlsx)")
        export_btn.clicked.connect(self.export_to_excel)
        
        controls_layout.addWidget(QLabel("Período:"))
        controls_layout.addWidget(self.period_combo)
        controls_layout.addWidget(gen_btn)
        controls_layout.addWidget(export_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)

               
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Fecha", "Evento", "Placa", "Estado / Tipo", "Detalle / Ruta"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        from PyQt6.QtWidgets import QAbstractItemView
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def refresh_trucks(self):
                                                      
        pass

    def generate_report(self):
        period = self.period_combo.currentText()
        reportes = self.db.get_general_reports(period)
        
        self.table.setRowCount(0)        
        
        for i, row in enumerate(reportes):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(row['fecha'])))
            
            evento_item = QTableWidgetItem(row['evento'])
            if row['evento'] == 'ALERTA':
                evento_item.setForeground(Qt.GlobalColor.red)
            else:
                evento_item.setForeground(Qt.GlobalColor.green)
                
            self.table.setItem(i, 1, evento_item)
            self.table.setItem(i, 2, QTableWidgetItem(row['placa']))
            self.table.setItem(i, 3, QTableWidgetItem(row['estado_detalle']))
            self.table.setItem(i, 4, QTableWidgetItem(row['ruta_mensaje']))

    def export_to_excel(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Error", "No hay datos para exportar. Genere el reporte primero.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Reporte", "", "Excel Files (*.xlsx)")
        if not file_path:
            return
            
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Reporte Global"
            
                     
            headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
            ws.append(headers)
            
                  
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")
                ws.append(row_data)
                
            wb.save(file_path)
            QMessageBox.information(self, "Éxito", f"Reporte exportado correctamente a:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al exportar a Excel:\n{e}")
