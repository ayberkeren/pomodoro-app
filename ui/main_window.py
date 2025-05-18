# ui/main_window.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QInputDialog,
    QMenu, QFrame
)
from PySide6.QtGui import QFont, QColor, QPalette, QPixmap
from PySide6.QtCore import QTimer, Qt, QUrl
from PySide6.QtMultimedia import QSoundEffect

from ui.task_row import TaskRow
from utils.styles import BG_COLOR, HIGHLIGHT
import os


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro")
        self.resize(1280, 720)

        self.pomodoro_duration = 30
        self.short_break_duration = 15
        self.long_break_duration = 30
        self.remaining_time = self.pomodoro_duration
        self.current_mode = "Pomodoro"
        self.timer_running = False
        self.pomodoro_count = 0

        self.original_palette = QPalette()
        self.original_palette.setColor(QPalette.Window, QColor(BG_COLOR))
        self.setPalette(self.original_palette)

        self.alert_palette = QPalette()
        self.alert_palette.setColor(QPalette.Window, QColor("#FFDDD2"))

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_timer)

        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile("assets/sounds/ding.wav"))

        self.setup_ui()

    def setup_ui(self):
        main = QVBoxLayout(self)
        self.tabs = {}

        tabs = QHBoxLayout()
        for name in ["Pomodoro", "Kısa Mola", "Uzun Mola"]:
            label = QLabel(name)
            label.setStyleSheet("font-size: 16px; padding: 8px 12px;")
            self.tabs[name] = label
            tabs.addWidget(label)
        tabs.addStretch()
        tabs.addWidget(QLabel("🌞"))
        main.addLayout(tabs)
        self.highlight_tab("Pomodoro")

        content = QHBoxLayout()
        left = QVBoxLayout()
        left.setContentsMargins(60, 0, 0, 0)

        self.stat = QLabel("Bugün 0 Pomodoro tamamladın       14:30")
        left.addWidget(self.stat)

        self.timer_label = QLabel("00:30")
        self.timer_label.setFont(QFont("Arial", 48, QFont.Bold))
        left.addWidget(self.timer_label)

        self.start_button = QPushButton("Başlat")
        self.start_button.setFixedSize(200, 60)
        self.start_button.setStyleSheet(f"""
            background-color: {HIGHLIGHT};
            color: white;
            font-size: 20px;
            border-radius: 30px;
        """)
        self.start_button.clicked.connect(self.toggle_timer)
        left.addWidget(self.start_button, alignment=Qt.AlignLeft)

        self.active_label = QLabel("Aktif Görev: Henüz yok")
        self.active_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 10px;")
        left.addWidget(self.active_label)

        row = QHBoxLayout()
        row.addWidget(QLabel("Yapılacaklar"))
        trash = QPushButton("🗑")
        trash.setStyleSheet("border: none; font-size: 18px;")
        trash.clicked.connect(self.show_trash_menu)
        row.addStretch()
        row.addWidget(trash)
        left.addLayout(row)

        self.task_layout = QVBoxLayout()
        self.task_container = QWidget()
        self.task_container.setLayout(self.task_layout)
        self.task_container.setStyleSheet("""
            background: repeating-linear-gradient(
                to bottom,
                #ffffff,
                #ffffff 23px,
                #e0e0e0 24px,
                #ffffff 25px
            );
        """)
        left.addWidget(self.task_container)

        for task in ["Görev 1", "Görev 2"]:
            self.add_task(task)

        row = QHBoxLayout()
        row.addStretch()
        self.add_task_btn = QPushButton("+")
        self.add_task_btn.setStyleSheet(f"""
            background-color: {HIGHLIGHT};
            color: white;
            font-size: 24px;
            border-radius: 21px;
        """)
        self.add_task_btn.setFixedSize(42, 42)
        self.add_task_btn.clicked.connect(self.show_add_popup)
        row.addWidget(self.add_task_btn)
        row.addStretch()
        left.addLayout(row)

        left.addStretch()
        content.addLayout(left, 3)

        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        content.addWidget(divider)

        right = QVBoxLayout()
        msg = QLabel("Unutma, en büyük ilerlemeler küçük adımlarla başlar.")
        right.addWidget(msg)

        cover = QLabel()
        cover_path = "assets/icons/lofi.jpg"
        if os.path.exists(cover_path):
            pixmap = QPixmap(cover_path).scaled(240, 240, Qt.KeepAspectRatio)
            cover.setPixmap(pixmap)
        else:
            cover.setText("Lofi resmi eksik.")
        cover.setAlignment(Qt.AlignCenter)
        right.addWidget(cover)
        right.addStretch()

        content.addLayout(right, 2)
        main.addLayout(content)
        self.setLayout(main)

    def highlight_tab(self, name):
        for tab, label in self.tabs.items():
            label.setStyleSheet(f"""
                font-size: 16px;
                padding: 8px 12px;
                {'border-bottom: 3px solid ' + HIGHLIGHT if tab == name else ''}
            """)

    def toggle_timer(self):
        if self.timer_running:
            self.timer.stop()
            self.start_button.setText("Başlat")
        else:
            self.timer.start()
            self.start_button.setText("Duraklat")
        self.timer_running = not self.timer_running

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            m, s = divmod(self.remaining_time, 60)
            self.timer_label.setText(f"{m:02d}:{s:02d}")
        else:
            self.timer.stop()
            self.sound.play()
            self.setPalette(self.alert_palette)
            QTimer.singleShot(3000, self.reset_palette)
            self.start_button.setText("Başlat")
            self.timer_running = False

            if self.current_mode == "Pomodoro":
                self.pomodoro_count += 1
                self.stat.setText(f"Bugün {self.pomodoro_count} Pomodoro tamamladın       14:30")
                mode = "Uzun Mola" if self.pomodoro_count % 4 == 0 else "Kısa Mola"
                duration = self.long_break_duration if mode == "Uzun Mola" else self.short_break_duration
                self.switch_mode(mode, duration)
            else:
                self.switch_mode("Pomodoro", self.pomodoro_duration)

    def reset_palette(self):
        self.setPalette(self.original_palette)

    def switch_mode(self, mode, duration):
        self.current_mode = mode
        self.remaining_time = duration
        self.highlight_tab(mode)
        self.reset_palette()
        m, s = divmod(duration, 60)
        self.timer_label.setText(f"{m:02d}:{s:02d}")

    def show_add_popup(self):
        text, ok = QInputDialog.getText(self, "Yeni Görev", "Görev başlığı:")
        if ok and text.strip():
            self.add_task(text.strip())

    def add_task(self, text):
        task = TaskRow(text, self.task_layout, on_select_callback=self.set_active_task)
        task.setVisible(True)
        self.task_layout.addWidget(task)

    def set_active_task(self, task_text):
        self.active_label.setText(f"Aktif Görev: {task_text}")

    def show_trash_menu(self):
        menu = QMenu()
        menu.addAction("Tüm görevleri sil", self.clear_all_tasks)
        menu.addAction("Tamamlananları sil", self.clear_completed_tasks)
        menu.addAction("Tümünü tamamla", self.mark_all_done)
        menu.exec(self.cursor().pos())

    def clear_all_tasks(self):
        while self.task_layout.count():
            item = self.task_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def clear_completed_tasks(self):
        for i in reversed(range(self.task_layout.count())):
            w = self.task_layout.itemAt(i).widget()
            if isinstance(w, TaskRow) and w.checkbox.isChecked():
                w.deleteLater()

    def mark_all_done(self):
        for i in range(self.task_layout.count()):
            w = self.task_layout.itemAt(i).widget()
            if isinstance(w, TaskRow):
                w.checkbox.setChecked(True)
