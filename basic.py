from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QCheckBox, QScrollArea, QFrame, QSizePolicy,
    QDialog, QLineEdit
)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QFont, QColor, QPainter, QBrush
from PySide6.QtMultimedia import QSoundEffect
import sys

class OvalButton(QPushButton):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor("#eb5539")))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 26, 26)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Segoe UI", 15, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())

class CustomPopup(QWidget):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setFixedSize(320, 220)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #fffbee;
                border: 2px solid #f5ce95;
                border-radius: 20px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #eb5539; background: none; border: none;")
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)

        message_label = QLabel(message)
        message_label.setFont(QFont("Segoe UI", 14))
        message_label.setStyleSheet("color: #014f68; background: none; border: none;")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(message_label)

        ok_button = OvalButton("Tamam")
        ok_button.setFixedSize(150, 42)
        ok_button.clicked.connect(self.close)
        card_layout.addWidget(ok_button, alignment=Qt.AlignCenter)

        outer_layout.addWidget(card)

class PomodoroApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro ve Yapılacaklar")
        self.setFixedSize(400, 700)
        self.setStyleSheet("QWidget { background-color: #fff1d5; border: none; }")
        self.tasks = []
        self.active_tab = "Pomodoro"
        self.pomodoro_duration = 25
        self.short_break = 5
        self.long_break = 10
        self.current_time = self.pomodoro_duration
        self.timer_running = False
        self.mode = "work"
        self.pomodoro_count = 0

        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile("assets/sounds/ding.wav"))
        self.sound.setVolume(0.5)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(10)

        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet("QFrame#card { background-color: #fffbee; border: 2px solid #f5ce95; border-radius: 20px; }")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 30)
        card_layout.setSpacing(14)

        self.tabs = {}
        tab_widget = QWidget()
        tab_widget.setStyleSheet("background-color: #fffbee;")
        tab_layout = QHBoxLayout(tab_widget)
        tab_layout.setSpacing(0)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        for label in ["Pomodoro", "Kısa Mola", "Uzun Mola"]:
            tab = QLabel(label)
            tab.setFont(QFont("Segoe UI", 16, QFont.Bold if label == self.active_tab else QFont.Normal))
            tab.setAlignment(Qt.AlignCenter)
            tab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.tabs[label] = tab
            tab_layout.addWidget(tab)

        self.update_tab_styles()
        card_layout.addWidget(tab_widget)

        underline_all = QFrame()
        underline_all.setFixedHeight(1)
        underline_all.setStyleSheet("background-color: #efece3; border: none;")
        card_layout.addWidget(underline_all)

        self.time_label = QLabel(self.format_time(self.current_time))
        self.time_label.setFont(QFont("Segoe UI", 50, QFont.Black))
        self.time_label.setStyleSheet("color: #014f68; background-color: #fffbee;")
        self.time_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.time_label)

        self.start_button = OvalButton("Başlat")
        self.start_button.setFixedSize(230, 54)
        self.start_button.clicked.connect(self.toggle_timer)
        card_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        self.active_task_label = QLabel("<b>Aktif Görev:</b> Görev başlığı")
        self.active_task_label.setFont(QFont("Segoe UI", 15))
        self.active_task_label.setStyleSheet("color: #014f68; background-color: #fffbee;")
        card_layout.addWidget(self.active_task_label)

        divider1 = QFrame()
        divider1.setFrameShape(QFrame.HLine)
        divider1.setFixedHeight(1)
        divider1.setStyleSheet("background-color: #efece3; border: none; margin-top: 6px; margin-bottom: 6px;")
        card_layout.addWidget(divider1)

        todo_title = QLabel("Yapılacaklar")
        todo_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        todo_title.setStyleSheet("color: #014f68; background-color: #fffbee;")
        card_layout.addWidget(todo_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        self.task_container = QWidget()
        self.task_container.setStyleSheet("background-color: #fffbee; border: none;")
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setAlignment(Qt.AlignTop)
        self.task_layout.setSpacing(12)
        scroll.setWidget(self.task_container)
        card_layout.addWidget(scroll)

        ekle_row = QHBoxLayout()
        plus = QLabel("+")
        plus.setFont(QFont("Segoe UI", 17, QFont.Bold))
        plus.setStyleSheet("color: #2ec4b6; background-color: #fffbee;")
        ekle_row.addWidget(plus)

        add_button = QPushButton("Ekle")
        add_button.setFont(QFont("Segoe UI", 15, QFont.Bold))
        add_button.setStyleSheet("QPushButton { color: #014f68; background-color: #fffbee; border: none; }")
        add_button.clicked.connect(self.add_task)
        ekle_row.addWidget(add_button)
        ekle_row.addStretch()

        ekle_widget = QWidget()
        ekle_widget.setStyleSheet("background-color: #fffbee;")
        ekle_widget.setLayout(ekle_row)
        self.task_layout.addWidget(ekle_widget)

        bottom_divider = QFrame()
        bottom_divider.setFrameShape(QFrame.HLine)
        bottom_divider.setFixedHeight(1)
        bottom_divider.setStyleSheet("background-color: #efece3; border: none; margin-top: 20px;")
        card_layout.addWidget(bottom_divider)

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
            self.sound.play()
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
        self.active_tab = {
            "work": "Pomodoro",
            "short_break": "Kısa Mola",
            "long_break": "Uzun Mola"
        }[self.mode]
        self.update_tab_styles()
        self.show_popup()

    def show_popup(self):
        messages = {
            "Pomodoro": "Odaklanma zamanı!",
            "Kısa Mola": "Kısa mola zamanı!",
            "Uzun Mola": "Uzun mola zamanı!"
        }
        popup = CustomPopup(self.active_tab, messages[self.active_tab], self)
        popup.move(self.geometry().center() - popup.rect().center())
        popup.show()

    def add_task(self):
        popup = CustomTaskPopup(self)
        popup.exec()
        if popup.result and popup.task_text.strip():
            text = popup.task_text.strip()
            checkbox = QCheckBox(text)
            checkbox.setFont(QFont("Segoe UI", 15))
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #014f68;
                    spacing: 20px;
                    background-color: #fffbee;
                }
                QCheckBox::indicator {
                    width: 24px;
                    height: 24px;
                    border: 2px solid #2ec4b6;
                    border-radius: 4px;
                    background: #fffbee;
                }
                QCheckBox::indicator:checked {
                    background-color: #2ec4b6;
                }
            """)
            checkbox.stateChanged.connect(lambda state, txt=text, cb=checkbox: self.handle_check(txt, cb))
            self.task_layout.insertWidget(self.task_layout.count() - 1, checkbox)
            self.tasks.append(checkbox)

    def handle_check(self, text, checkbox):
        if checkbox.isChecked():
            checkbox.setStyleSheet(checkbox.styleSheet() + "QCheckBox { color: #6c757d; text-decoration: line-through; }")
        else:
            checkbox.setStyleSheet(checkbox.styleSheet() + "QCheckBox { color: #014f68; text-decoration: none; }")
        self.active_task_label.setText(f"<b>Aktif Görev:</b> {text}")

    def update_tab_styles(self):
        for label, tab in self.tabs.items():
            is_active = (label == self.active_tab)
            tab.setStyleSheet(f"""
                QLabel {{
                    color: {'#eb5539' if is_active else '#014f68'};
                    background-color: #fffbee;
                    border-bottom: {'3px solid #eb5539' if is_active else 'none'};
                    padding-bottom: 4px;
                }}
            """)

class CustomTaskPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setFixedSize(350, 240)  # Daha ferah

        self.result = False
        self.task_text = ""

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #fffbee;
                border: 2px solid #f5ce95;
                border-radius: 20px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)

        title_label = QLabel("Yeni Görev")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #eb5539; background: none; border: none;")
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)

        self.input = QLineEdit()
        self.input.setFont(QFont("Segoe UI", 14))
        self.input.setPlaceholderText("Görev girin...")
        self.input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #f5ce95;
                border-radius: 8px;
                padding: 6px 10px;
                background-color: #fff;
                color: #014f68;
            }
        """)
        card_layout.addWidget(self.input)

        button_row = QHBoxLayout()
        cancel_btn = OvalButton("İptal")
        cancel_btn.setFixedSize(100, 40)
        cancel_btn.clicked.connect(self.reject)
        button_row.addWidget(cancel_btn)

        add_btn = OvalButton("Ekle")
        add_btn.setFixedSize(100, 40)
        add_btn.clicked.connect(self.accept)
        button_row.addWidget(add_btn)

        card_layout.addLayout(button_row)
        outer_layout.addWidget(card)

    def accept(self):
        self.result = True
        self.task_text = self.input.text()
        super().accept()

    def reject(self):
        self.result = False
        super().reject()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PomodoroApp()
    win.show()
    sys.exit(app.exec())
