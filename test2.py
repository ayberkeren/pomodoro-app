from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QListWidget, QListWidgetItem, QCheckBox, QInputDialog, QFrame
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
        painter.drawRoundedRect(self.rect(), 25, 25)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Segoe UI", 14, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())

class PomodoroApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro ve Yapılacaklar")
        self.setFixedSize(360, 620)
        self.setStyleSheet("background-color: #fdf6e3; font-family: 'Segoe UI';")

        self.pomodoro_duration = 25 * 60
        self.short_break = 5 * 60
        self.long_break = 10 * 60
        self.current_time = self.pomodoro_duration
        self.timer_running = False
        self.mode = "work"
        self.pomodoro_count = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Üst sekmeler
        tab_layout = QHBoxLayout()
        self.tabs = {}
        for label, mode in [("Pomodoro", "work"), ("Kısa Mola", "short_break"), ("Uzun Mola", "long_break")]:
            tab = QLabel(label)
            tab.setFont(QFont("Segoe UI", 12, QFont.Bold if mode == "work" else QFont.Normal))
            tab.setStyleSheet(f"color: {'#e63946' if mode == 'work' else '#1d3557'}; padding: 8px;")
            self.tabs[mode] = tab
            tab_layout.addWidget(tab, alignment=Qt.AlignCenter)
        layout.addLayout(tab_layout)

        # Kart görünümü
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #fff4e6;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        card_layout = QVBoxLayout(card)

        # Zamanlayıcı
        self.time_label = QLabel(self.format_time(self.current_time))
        self.time_label.setFont(QFont("Segoe UI", 42, QFont.Bold))
        self.time_label.setStyleSheet("color: #1d3557; margin-top: 10px;")
        self.time_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.time_label)

        # Başlat butonu
        self.start_button = OvalButton("Başlat")
        self.start_button.setFixedSize(120, 50)
        self.start_button.clicked.connect(self.toggle_timer)
        card_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        # Aktif görev
        self.active_task_label = QLabel("Aktif Görev: Görev başlığı")
        self.active_task_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.active_task_label.setStyleSheet("color: #1d3557; margin-top: 15px;")
        card_layout.addWidget(self.active_task_label)

        # Yapılacaklar başlık
        todo_title = QLabel("Yapılacaklar")
        todo_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        todo_title.setStyleSheet("color: #1d3557; margin-top: 10px;")
        card_layout.addWidget(todo_title)

        # Görev listesi
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                background-color: #fff4e6;
                border: none;
                padding: 0 5px;
            }
        """)
        card_layout.addWidget(self.task_list)

        # + Ekle
        self.add_button = QPushButton("+  Ekle")
        self.add_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.add_button.setStyleSheet("""
            QPushButton {
                color: #1d3557;
                background-color: transparent;
                border: none;
                margin-top: 5px;
                margin-left: 5px;
            }
        """)
        self.add_button.clicked.connect(self.add_task)
        card_layout.addWidget(self.add_button, alignment=Qt.AlignLeft)

        layout.addWidget(card)

    def format_time(self, secs):
        return f"{secs // 60:02d}:{secs % 60:02d}"

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
            if self.pomodoro_count % 4 == 0:
                self.mode = "long_break"
                self.current_time = self.long_break
            else:
                self.mode = "short_break"
                self.current_time = self.short_break
        else:
            self.mode = "work"
            self.current_time = self.pomodoro_duration
        self.time_label.setText(self.format_time(self.current_time))

    def add_task(self):
        text, ok = QInputDialog.getText(self, "Yeni Görev", "Görev:")
        if ok and text:
            item = QListWidgetItem()
            checkbox = QCheckBox(text)
            checkbox.setFont(QFont("Segoe UI", 12))
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #1d3557;
                    spacing: 10px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox:checked {
                    color: #6c757d;
                    text-decoration: line-through;
                }
            """)
            checkbox.stateChanged.connect(lambda state, t=text: self.set_active_task(t))
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, checkbox)

    def set_active_task(self, text):
        self.active_task_label.setText(f"Aktif Görev: {text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PomodoroApp()
    win.show()
    sys.exit(app.exec())
