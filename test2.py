from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QCheckBox, QInputDialog, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPainter, QBrush
import sys

class OvalButton(QPushButton):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor("#e63946")))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 30, 30)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Segoe UI", 16, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())

class PomodoroApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro ve Yapılacaklar")
        self.setFixedSize(360, 640)
        self.setStyleSheet("background-color: #fdf6e3; font-family: 'Segoe UI';")
        self.tasks = []

        self.pomodoro_duration = 25 * 60
        self.short_break = 5 * 60
        self.long_break = 10 * 60
        self.current_time = self.pomodoro_duration
        self.timer_running = False
        self.mode = "work"
        self.pomodoro_count = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 10, 15, 10)

        # Sekmeler (kart dışında, üstte)
        tab_layout = QHBoxLayout()
        tab_layout.setSpacing(30)
        self.tabs = {}
        for label, mode in [("Pomodoro", "work"), ("Kısa Mola", "short_break"), ("Uzun Mola", "long_break")]:
            tab = QLabel(label)
            tab.setFont(QFont("Segoe UI", 13, QFont.Bold if mode == "work" else QFont.Normal))
            tab.setStyleSheet(f"color: {'#e63946' if mode == 'work' else '#1d3557'};")
            self.tabs[mode] = tab
            tab_layout.addWidget(tab, alignment=Qt.AlignCenter)
        main_layout.addLayout(tab_layout)

        # Ana kart
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #fff4e6;
                border-radius: 18px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(10)

        # Zaman
        self.time_label = QLabel(self.format_time(self.current_time))
        self.time_label.setFont(QFont("Segoe UI", 46, QFont.Black))
        self.time_label.setStyleSheet("color: #1d3557;")
        self.time_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.time_label)

        # Başlat/Durdur butonu
        self.start_button = OvalButton("Başlat")
        self.start_button.setFixedSize(160, 52)
        self.start_button.clicked.connect(self.toggle_timer)
        card_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        # Aktif Görev
        self.active_task_label = QLabel("Aktif Görev:  Görev başlığı")
        self.active_task_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.active_task_label.setStyleSheet("color: #1d3557; margin-top: 10px;")
        card_layout.addWidget(self.active_task_label)

        # Yapılacaklar Başlığı
        todo_title = QLabel("Yapılacaklar")
        todo_title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        todo_title.setStyleSheet("color: #1d3557; margin-top: 5px;")
        card_layout.addWidget(todo_title)

        # Liste
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        self.task_container = QWidget()
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setAlignment(Qt.AlignTop)
        self.task_layout.setSpacing(12)
        scroll.setWidget(self.task_container)
        card_layout.addWidget(scroll)

        # + Ekle
        ekle_row = QHBoxLayout()
        plus = QLabel("+")
        plus.setFont(QFont("Segoe UI", 15, QFont.Bold))
        plus.setStyleSheet("color: #2ec4b6;")
        ekle_row.addWidget(plus)

        add_button = QPushButton("Ekle")
        add_button.setFont(QFont("Segoe UI", 14, QFont.Bold))
        add_button.setStyleSheet("""
            QPushButton {
                color: #1d3557;
                background-color: transparent;
                border: none;
            }
        """)
        add_button.clicked.connect(self.add_task)
        ekle_row.addWidget(add_button)
        ekle_row.addStretch()
        card_layout.addLayout(ekle_row)

        main_layout.addWidget(card)

    def format_time(self, seconds):
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def toggle_timer(self):
        self.timer_running = not self.timer_running
        self.start_button.setText("Durdur" if self.timer_running else "Başlat")
        if self.timer_running:
            self.timer.start(1000)
        else:
            self.timer.stop()

    def update_timer(self):
        if self.current_time > 0:
            self.current_time -= 1
            self.time_label.setText(self.format_time(self.current_time))
        else:
            self.timer.stop()
            self.timer_running = False
            self.start_button.setText("Başlat")
            self.switch_mode()

    def switch_mode(self):
        if self.mode == "work":
            self.pomodoro_count += 1
            self.mode = "long_break" if self.pomodoro_count % 4 == 0 else "short_break"
        else:
            self.mode = "work"
        self.current_time = {
            "work": self.pomodoro_duration,
            "short_break": self.short_break,
            "long_break": self.long_break
        }[self.mode]
        self.time_label.setText(self.format_time(self.current_time))

    def add_task(self):
        text, ok = QInputDialog.getText(self, "Yeni Görev", "Görev:")
        if not ok or not text.strip():
            return

        checkbox = QCheckBox(text)
        checkbox.setFont(QFont("Segoe UI", 14))
        checkbox.setStyleSheet("""
            QCheckBox {
                color: #1d3557;
                spacing: 20px;
            }
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
                border: 2px solid #2ec4b6;
                border-radius: 4px;
                background: #fdf6e3;
            }
            QCheckBox::indicator:checked {
                image: none;
                background-color: #2ec4b6;
            }
        """)
        checkbox.stateChanged.connect(lambda state, txt=text, cb=checkbox: self.handle_check(txt, cb))
        self.task_layout.addWidget(checkbox)
        self.tasks.append(checkbox)

    def handle_check(self, text, checkbox):
        if checkbox.isChecked():
            checkbox.setStyleSheet(checkbox.styleSheet() + "QCheckBox { color: #6c757d; text-decoration: line-through; }")
        else:
            checkbox.setStyleSheet(checkbox.styleSheet() + "QCheckBox { color: #1d3557; text-decoration: none; }")
        self.active_task_label.setText(f"Aktif Görev:  {text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PomodoroApp()
    win.show()
    sys.exit(app.exec())
