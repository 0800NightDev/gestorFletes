from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF

class CircularGauge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.max_value = 100
        self.setMinimumSize(100, 100)

    def setValue(self, value):
        self.value = max(0, min(value, self.max_value))
        self.update()

    def paintEvent(self, event):
        width = self.width()
        height = self.height()
        
                                                 
        size = min(width, height) - 20
        rect = QRectF((width - size) / 2, (height - size) / 2, size, size)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
                                
        bg_pen = QPen(QColor(50, 50, 50, 100))
        bg_pen.setWidth(10)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(rect, 0, 360 * 16)
        
                              
        progress_color = QColor(76, 175, 80)        
        if self.value < 20:
            progress_color = QColor(244, 67, 54)      
        elif self.value < 50:
            progress_color = QColor(255, 152, 0)         
            
        fg_pen = QPen(progress_color)
        fg_pen.setWidth(10)
        fg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(fg_pen)
        
                                            
                                                                           
                                              
        span_angle = int(-(self.value / self.max_value) * 360 * 16)
        start_angle = 90 * 16
        painter.drawArc(rect, start_angle, span_angle)
        
                   
        painter.setPen(Qt.GlobalColor.white)
        font = QFont("Arial", 14, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{int(self.value)}%")
        
        painter.end()
