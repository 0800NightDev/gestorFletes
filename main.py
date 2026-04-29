import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QStackedWidget, QLabel, QSpacerItem, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QCursor
from qt_material import apply_stylesheet

from models.db_manager import DBManager
from core.telemetry_simulator import TelemetrySimulator
from views.dashboard_window import DashboardWindow
from views.reports_window import ReportsWindow
from views.trucks_window import TrucksWindow

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Alexander Moya - Monitoreo de Flota")
        self.resize(1100, 750)
        
        self.db = DBManager()
        self.telemetry = TelemetrySimulator(self.db)
        self.telemetry.start()
        
        self.current_theme = 'dark_blue.xml'
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

                
        header = QFrame()
        header.setFixedHeight(60)
                                                                                
        header.setStyleSheet("border-bottom: 1px solid palette(divider);")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 5, 15, 5)

                        
        self.logo_label = ClickableLabel()
        self.logo_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        logo_path = os.path.join(os.path.dirname(__file__), 'svg', 'logo_clean.svg')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaledToHeight(40, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        self.logo_label.clicked.connect(self.toggle_sidebar)
        header_layout.addWidget(self.logo_label)

        title_label = QLabel("Alexander Moya")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; border: none;")
        header_layout.addWidget(title_label)

        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        header_layout.addItem(spacer)

        self.theme_btn = QPushButton("Cambiar Tema")
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_btn)

                     
        test_stop_btn = QPushButton("Test Stop")
        test_stop_btn.clicked.connect(self.test_stop_truck)
        header_layout.addWidget(test_stop_btn)

        main_layout.addWidget(header)

                                  
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

                 
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("border-right: 1px solid palette(divider);")
        self.sidebar.setVisible(False)                   
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        dash_btn = QPushButton("Panel de Control")
        dash_btn.clicked.connect(lambda: self.switch_view(0))
        trucks_btn = QPushButton("Gestión de Camiones")
        trucks_btn.clicked.connect(lambda: self.switch_view(1))
        reports_btn = QPushButton("Reportes")
        reports_btn.clicked.connect(lambda: self.switch_view(2))
        
                                               
        for btn in [dash_btn, trucks_btn, reports_btn]:
            btn.setStyleSheet("text-align: left; padding: 15px; border: none;")
            sidebar_layout.addWidget(btn)

                      
        self.stacked_widget = QStackedWidget()
        self.dashboard_view = DashboardWindow(self.db)
        self.trucks_view = TrucksWindow(self.db)
        self.reports_view = ReportsWindow(self.db)
        
        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.trucks_view)
        self.stacked_widget.addWidget(self.reports_view)

        body_layout.addWidget(self.sidebar)
        body_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(body_widget)

    def toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def switch_view(self, index):
        if index == 0:
            self.dashboard_view.refresh_trucks()
        elif index == 1:
            self.trucks_view.load_trucks()
        elif index == 2:
            self.reports_view.refresh_trucks()
        self.stacked_widget.setCurrentIndex(index)

    def toggle_theme(self):
        self.current_theme = 'light_blue.xml' if self.current_theme == 'dark_blue.xml' else 'dark_blue.xml'
        apply_stylesheet(app, theme=self.current_theme)

    def test_stop_truck(self):
        placa = self.dashboard_view.current_placa
        if placa:
            self.telemetry.stop_truck(placa)
            print(f"Camión {placa} detenido artificialmente por > 45 mins.")

    def closeEvent(self, event):
        self.telemetry.stop_simulation()
        self.telemetry.join()
        super().closeEvent(event)

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_blue.xml')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
