from PySide6.QtGui import QFont, QPixmap
from PySide6.QtMultimedia import QSoundEffect

from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QTimer, QUrl
import sys

# 🎨 Renkler
BG_COLOR = "#FDF6E3"
FG_COLOR = "#1F2937"
HIGHLIGHT = "#F25C54"
GRAY_TEXT = "#6B7280"
LINK_COLOR = "#2563EB"

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Timer")
        self.setGeometry(0, 0, 1920, 1080)
        self.setStyleSheet(f"background-color: {BG_COLOR}; color: {FG_COLOR};")

        # Sayaç
        self.pomodoro_duration = 1 * 60  # saniye
        self.remaining_time = self.pomodoro_duration
        self.timer_running = False

        # Timer
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_timer)

        # Zil
        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile("assets/sounds/ding.wav"))

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # 🔹 Sekmeler
        self.tabs = {}
        tab_layout = QHBoxLayout()
        for tab in ["Pomodoro", "Kısa Mola", "Uzun Mola"]:
            label = QLabel(tab)
            label.setStyleSheet("""
                font-weight: bold;
                padding: 12px 16px;
                font-size: 16px;
            """)
            self.tabs[tab] = label
            tab_layout.addWidget(label)
        tab_layout.addStretch()
        tab_layout.addWidget(QLabel("🌞"))
        main_layout.addLayout(tab_layout)

        self.highlight_tab("Pomodoro")

        # 🔸 İçerik Alanı
        content_layout = QHBoxLayout()

        # 🎯 Sol Panel
        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(60, 0, 0, 0)

        stat = QLabel("Bugün 3 Pomodoro tamamladın       14:30")
        stat.setStyleSheet("color: #334155; font-size: 14px;")
        left_panel.addWidget(stat)

        self.timer_label = QLabel("1:00")
        self.timer_label.setFont(QFont("Arial", 48, QFont.Bold))
        self.timer_label.setAlignment(Qt.AlignLeft)
        left_panel.addWidget(self.timer_label)

        self.start_button = QPushButton("Başlat")
        self.start_button.setFixedSize(160, 50)
        self.start_button.setStyleSheet(f"""
            background-color: {HIGHLIGHT};
            color: white;
            font-size: 18px;
            border-radius: 25px;
        """)
        self.start_button.clicked.connect(self.toggle_timer)
        left_panel.addWidget(self.start_button, alignment=Qt.AlignLeft)

        left_panel.addSpacing(20)

        active_task = QLabel("Aktif Görev: Görev başlığı")
        active_task.setStyleSheet("font-size: 16px;")
        left_panel.addWidget(active_task)
        left_panel.addSpacing(8)

        left_panel.addWidget(QLabel("Yapılacaklar"))
        for text, checked in [
            ("Üstü çizili görev 1", True),
            ("Üstü çizili görev 2", True),
            ("Görev 3", False),
            ("Görev 4", False),
        ]:
            cb = QCheckBox(text)
            cb.setChecked(checked)
            cb.setStyleSheet(f"""
                QCheckBox {{
                    spacing: 10px;
                    font-size: 14px;
                    margin-bottom: 4px;
                    color: {'#9CA3AF' if checked else FG_COLOR};
                }}
            """)
            left_panel.addWidget(cb)

        add_label = QLabel("+ Ekle")
        add_label.setStyleSheet(f"color: {LINK_COLOR}; font-size: 14px; margin-top: 10px;")
        left_panel.addWidget(add_label)

        left_panel.addStretch()

        bottom_row = QHBoxLayout()
        detail = QLabel("Detay")
        detail.setStyleSheet(f"color: {LINK_COLOR}; font-size: 14px;")
        notification = QLabel("Bildirim")
        notification.setStyleSheet("font-weight: bold; font-size: 14px;")
        bottom_row.addWidget(detail)
        bottom_row.addStretch()
        bottom_row.addWidget(notification)
        left_panel.addLayout(bottom_row)

        content_layout.addLayout(left_panel, 3)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setStyleSheet("color: #DDD;")
        content_layout.addWidget(divider)

        # 🎵 Sağ Panel
        right_panel = QVBoxLayout()
        motivation = QLabel("Unutma, en büyük ilerlemeler küçük adımlarla başlar.")
        motivation.setWordWrap(True)
        motivation.setStyleSheet("font-size: 16px; margin-bottom: 8px;")
        right_panel.addWidget(motivation)

        cover = QLabel()
        pixmap = QPixmap("assets/icons/lofi.jpg").scaled(280, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        cover.setPixmap(pixmap)
        cover.setAlignment(Qt.AlignCenter)
        cover.setStyleSheet("border-radius: 12px; margin: 10px;")
        right_panel.addWidget(cover, alignment=Qt.AlignCenter)

        song_label = QLabel("Lofi Hip Hop")
        song_label.setAlignment(Qt.AlignCenter)
        song_label.setStyleSheet("font-size: 16px; margin-top: 6px;")
        right_panel.addWidget(song_label)

        controls = QHBoxLayout()
        for text in ["Repeat", "Prev", "Play", "Next"]:
            btn = QLabel(text)
            btn.setAlignment(Qt.AlignCenter)
            btn.setFixedSize(60, 30)
            controls.addWidget(btn)
        controls.setAlignment(Qt.AlignCenter)
        right_panel.addLayout(controls)
        right_panel.addStretch()

        content_layout.addLayout(right_panel, 2)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def toggle_timer(self):
        if self.timer_running:
            self.timer.stop()
            self.start_button.setText("Başlat")
            self.timer_running = False
        else:
            self.timer.start()
            self.start_button.setText("Duraklat")
            self.timer_running = True

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            mins = self.remaining_time // 60
            secs = self.remaining_time % 60
            self.timer_label.setText(f"{mins:02d}:{secs:02d}")
        else:
            self.timer.stop()
            self.timer_running = False
            self.remaining_time = self.pomodoro_duration  # reset
            self.timer_label.setText("25:00")
            self.start_button.setText("Başlat")
            self.highlight_tab("Kısa Mola")
            self.sound.play()

    def highlight_tab(self, tab_name):
        for name, label in self.tabs.items():
            if name == tab_name:
                label.setStyleSheet("""
                    font-weight: bold;
                    padding: 12px 16px;
                    font-size: 16px;
                    border-bottom: 3px solid #F25C54;
                """)
            else:
                label.setStyleSheet("""
                    font-weight: normal;
                    padding: 12px 16px;
                    font-size: 16px;
                """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
