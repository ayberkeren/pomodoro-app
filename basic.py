import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QCheckBox, QScrollArea, QFrame, QSizePolicy,
    QDialog, QLineEdit, QMenu, QTextEdit
)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QCursor, QAction
from PySide6.QtMultimedia import QSoundEffect

TASKS_FILE = "pomodoro_tasks.json"

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

class CustomDescriptionPopup(QDialog):
    def __init__(self, parent=None, text=""):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setFixedSize(350, 220)
        self.result = False
        self.desc_text = ""

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
        card_layout.setSpacing(12)
        title_label = QLabel("Açıklama Ekle/Düzenle")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #eb5539; background: none; border: none;")
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)
        self.input = QTextEdit()
        self.input.setFont(QFont("Segoe UI", 13))
        self.input.setPlaceholderText("Açıklama girin...")
        self.input.setText(text)
        self.input.setMaximumHeight(110)
        self.input.setMinimumHeight(60)
        self.input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #f5ce95;
                border-radius: 8px;
                padding: 8px 10px;
                background-color: #fff;
                color: #014f68;
            }
            QTextEdit QScrollBar:vertical {
                background: #f5f5f5;
                width: 10px;
                margin: 2px 0 2px 0;
                border-radius: 5px;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: #2ec4b6;
                min-height: 20px;
                border-radius: 5px;
            }
        """)
        card_layout.addWidget(self.input)
        card_layout.addSpacing(8)
        button_row = QHBoxLayout()
        cancel_btn = OvalButton("İptal")
        cancel_btn.setFixedSize(100, 40)
        cancel_btn.clicked.connect(self.reject)
        button_row.addWidget(cancel_btn)
        add_btn = OvalButton("Kaydet")
        add_btn.setFixedSize(100, 40)
        add_btn.clicked.connect(self.accept)
        button_row.addWidget(add_btn)
        card_layout.addLayout(button_row)
        outer_layout.addWidget(card)
    def accept(self):
        self.result = True
        self.desc_text = self.input.toPlainText()
        super().accept()
    def reject(self):
        self.result = False
        super().reject()

class PomodoroApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro ve Yapılacaklar")
        self.setFixedSize(400, 700)
        self.setStyleSheet("QWidget { background-color: #fff1d5; border: none; }")
        self.tasks = []
        self.active_tab = "Pomodoro"
        self.pomodoro_duration = 25 * 60
        self.short_break = 5 * 60
        self.long_break = 10 * 60
        self.current_time = self.pomodoro_duration
        self.timer_running = False
        self.mode = "work"
        self.pomodoro_count = 0
        self.active_task = None

        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile("assets/sounds/ding.wav"))
        self.sound.setVolume(0.5)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.build_ui()
        self.load_data()

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
        self.active_task_label = QLabel("<b>Aktif Görev:</b> Yok")
        self.active_task_label.setFont(QFont("Segoe UI", 15))
        self.active_task_label.setStyleSheet("color: #014f68; background-color: #fffbee;")
        card_layout.addWidget(self.active_task_label)
        divider1 = QFrame()
        divider1.setFrameShape(QFrame.HLine)
        divider1.setFixedHeight(1)
        divider1.setStyleSheet("background-color: #efece3; border: none; margin-top: 6px; margin-bottom: 6px;")
        card_layout.addWidget(divider1)
        todo_title_row = QHBoxLayout()
        todo_title = QLabel("Yapılacaklar")
        todo_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        todo_title.setStyleSheet("color: #014f68; background-color: #fffbee;")
        todo_title_row.addWidget(todo_title)
        todo_title_row.addStretch()
        self.todo_three_dots = QPushButton("⋮")
        self.todo_three_dots.setFont(QFont("Segoe UI", 17))
        self.todo_three_dots.setStyleSheet("QPushButton { color: #ababab; background: transparent; border: none; } QPushButton:hover { color: #2ec4b6; }")
        self.todo_three_dots.setCursor(Qt.PointingHandCursor)
        self.todo_three_dots.setFixedWidth(32)
        self.todo_three_dots.clicked.connect(self.show_all_tasks_menu)
        todo_title_row.addWidget(self.todo_three_dots)
        card_layout.addLayout(todo_title_row)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { background-color: transparent; border: none; }
            QScrollBar:vertical {
                background: #f5f5f5;
                width: 10px;
                margin: 2px 0 2px 0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #2ec4b6;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                border: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.task_container = QWidget()
        self.task_container.setStyleSheet("background-color: #fffbee; border: none;")
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setAlignment(Qt.AlignTop)
        self.task_layout.setSpacing(12)
        scroll.setWidget(self.task_container)
        card_layout.addWidget(scroll)
        ekle_row = QHBoxLayout()
        self.plus_label = QLabel("+")
        self.plus_label.setFont(QFont("Segoe UI", 17, QFont.Bold))
        self.plus_label.setStyleSheet("color: #2ec4b6; background-color: #fffbee;")
        self.plus_label.setCursor(Qt.PointingHandCursor)
        self.plus_label.mousePressEvent = self.add_task
        ekle_row.addWidget(self.plus_label)
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

        # Pomodoro Sayacı Label (en alta ekle)
        self.pomodoro_counter_label = QLabel()
        self.pomodoro_counter_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.pomodoro_counter_label.setStyleSheet("color: #eb5539; background: none;")
        self.pomodoro_counter_label.setAlignment(Qt.AlignCenter)
        self.update_pomodoro_counter()
        card_layout.addWidget(self.pomodoro_counter_label)

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
            self.update_pomodoro_counter()
            self.save_data()
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

    def update_pomodoro_counter(self):
        self.pomodoro_counter_label.setText(f"Toplam Pomodoro: {self.pomodoro_count}")

    def show_popup(self):
        messages = {
            "Pomodoro": "Odaklanma zamanı!",
            "Kısa Mola": "Kısa mola zamanı!",
            "Uzun Mola": "Uzun mola zamanı!"
        }
        popup = CustomPopup(self.active_tab, messages[self.active_tab], self)
        popup.move(self.geometry().center() - popup.rect().center())
        popup.show()

    def add_task(self, event=None):
        popup = CustomTaskPopup(self)
        popup.exec()
        if popup.result and popup.task_text.strip():
            text = popup.task_text.strip()
            desc = popup.desc_text.strip() if hasattr(popup, "desc_text") else ""
            self._add_task_widget(text, desc, False, None)
            self.save_data()

    def _add_task_widget(self, text, desc, done, completed_time):
        task_widget = QWidget()
        task_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        row = QHBoxLayout(task_widget)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        checkbox = QCheckBox()
        checkbox.setFont(QFont("Segoe UI", 15))
        checkbox.setChecked(done)
        checkbox.setStyleSheet("""
            QCheckBox {
                color: #014f68;
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
        task_label = QLabel(text)
        task_label.setFont(QFont("Segoe UI", 15))
        task_label.setWordWrap(True)
        task_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        task_label.setStyleSheet("""
            QLabel {
                color: #014f68;
                background-color: #fffbee;
            }
        """)
        if desc:
            task_label.setToolTip(desc)
        if done:
            task_label.setStyleSheet(task_label.styleSheet() + "QLabel { color: #6c757d; text-decoration: line-through; }")
        def label_click(event, lbl=task_label, cb=checkbox):
            if not cb.isChecked():
                self.set_active_task(lbl.text(), lbl.toolTip())
        task_label.mousePressEvent = label_click
        def check_callback(state, lbl=task_label, cb=checkbox):
            self.handle_check(lbl, cb)
        checkbox.stateChanged.connect(check_callback)
        three_dots = QPushButton("⋮")
        three_dots.setFont(QFont("Segoe UI", 17))
        three_dots.setStyleSheet("QPushButton { color: #ababab; background: transparent; border: none; } QPushButton:hover { color: #2ec4b6; }")
        three_dots.setCursor(Qt.PointingHandCursor)
        three_dots.setFixedWidth(32)
        three_dots.clicked.connect(lambda _, w=task_widget, lbl=task_label, cb=checkbox: self.show_task_menu(w, lbl, cb))
        row.addWidget(checkbox)
        row.addWidget(task_label, 1)
        row.addWidget(three_dots)
        row.setAlignment(Qt.AlignVCenter)
        # Tamamlanan görevler listenin en başına, zaman sırasına göre eklenir
        data = (task_widget, task_label, checkbox, completed_time)
        if done:
            idx = 0
            while idx < len(self.tasks) and self.tasks[idx][2].isChecked() and \
                    (self.tasks[idx][3] or 0) <= (completed_time or 0):
                idx += 1
            self.tasks.insert(idx, data)
            self.task_layout.insertWidget(idx, task_widget)
        else:
            self.tasks.append(data)
            self.task_layout.insertWidget(self.task_layout.count() - 1, task_widget)

    def show_task_menu(self, task_widget, task_label, checkbox):
        menu = QMenu()
        edit_action = QAction("Düzenle", self)
        desc_action = QAction("Açıklama Ekle/Düzenle", self)
        delete_action = QAction("Sil", self)
        def edit_task():
            popup = CustomTaskPopup(self, task_label.text(), task_label.toolTip())
            popup.exec()
            if popup.result and popup.task_text.strip():
                task_label.setText(popup.task_text.strip())
                if hasattr(popup, "desc_text") and popup.desc_text.strip():
                    task_label.setToolTip(popup.desc_text.strip())
                else:
                    task_label.setToolTip("")
                self.save_data()
        def add_description():
            popup = CustomDescriptionPopup(self, task_label.toolTip())
            popup.exec()
            if popup.result:
                task_label.setToolTip(popup.desc_text)
                self.save_data()
        def delete_task():
            self.task_layout.removeWidget(task_widget)
            task_widget.deleteLater()
            self.tasks = [t for t in self.tasks if t[0] != task_widget]
            self.save_data()
        edit_action.triggered.connect(edit_task)
        desc_action.triggered.connect(add_description)
        delete_action.triggered.connect(delete_task)
        menu.addAction(edit_action)
        menu.addAction(desc_action)
        menu.addAction(delete_action)
        menu.exec(QCursor.pos())

    def show_all_tasks_menu(self):
        menu = QMenu()
        complete_all = QAction("Hepsini Tamamla", self)
        delete_all = QAction("Hepsini Sil", self)
        delete_completed = QAction("Tamamlananları Sil", self)
        def do_complete_all():
            import time
            now = time.time()
            for idx, (widget, label, checkbox, completed_time) in enumerate(self.tasks):
                if not checkbox.isChecked():
                    checkbox.setChecked(True)
                    self.tasks[idx] = (widget, label, checkbox, now + idx)
            self.reorder_tasks()
            self.save_data()
        def do_delete_all():
            for task_widget, _, _, _ in self.tasks:
                self.task_layout.removeWidget(task_widget)
                task_widget.deleteLater()
            self.tasks.clear()
            self.save_data()
        def do_delete_completed():
            to_remove = [t for t in self.tasks if t[2].isChecked()]
            for task_widget, _, _, _ in to_remove:
                self.task_layout.removeWidget(task_widget)
                task_widget.deleteLater()
                self.tasks.remove((task_widget, _, _, _))
            self.save_data()
        complete_all.triggered.connect(do_complete_all)
        delete_all.triggered.connect(do_delete_all)
        delete_completed.triggered.connect(do_delete_completed)
        menu.addAction(complete_all)
        menu.addAction(delete_all)
        menu.addAction(delete_completed)
        menu.exec(QCursor.pos())

    def set_active_task(self, text, desc=None):
        if not text:
            self.active_task_label.setText("<b>Aktif Görev:</b> Yok")
            return
        self.active_task_label.setText(f"<b>Aktif Görev:</b> {text}" +
                                       (f"<br><span style='color:#ababab;font-size:12px'>{desc}</span>" if desc else ""))
        self.active_task = text

    def handle_check(self, label, checkbox):
        # Aktif görev tamamlanırsa aktif görev boşalır
        if checkbox.isChecked():
            label.setStyleSheet(label.styleSheet() + "QLabel { color: #6c757d; text-decoration: line-through; }")
            if self.active_task_label.text().find(label.text()) != -1:
                self.set_active_task("")
            import time
            # Tamamlanma zamanını kaydet
            for idx, (widget, lbl, cb, completed_time) in enumerate(self.tasks):
                if lbl == label:
                    self.tasks[idx] = (widget, lbl, cb, time.time())
        else:
            label.setStyleSheet(label.styleSheet() + "QLabel { color: #014f68; text-decoration: none; }")
            for idx, (widget, lbl, cb, completed_time) in enumerate(self.tasks):
                if lbl == label:
                    self.tasks[idx] = (widget, lbl, cb, None)
        self.reorder_tasks()
        self.save_data()

    def reorder_tasks(self):
        # Tamamlananlar en üste, tamamlanma sırasına göre
        completed = sorted([t for t in self.tasks if t[2].isChecked()],
                           key=lambda x: x[3] or 0)
        not_completed = [t for t in self.tasks if not t[2].isChecked()]
        # Task layout sıfırlanır ve eklenir
        while self.task_layout.count() > 1:
            w = self.task_layout.takeAt(0).widget()
            if w:
                w.setParent(None)
        self.tasks = completed + not_completed
        for t in self.tasks:
            self.task_layout.insertWidget(self.tasks.index(t), t[0])

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

    def save_data(self):
        data = {
            "pomodoro_count": self.pomodoro_count,
            "tasks": []
        }
        for task_widget, label, checkbox, completed_time in self.tasks:
            data["tasks"].append({
                "text": label.text(),
                "desc": label.toolTip() if label.toolTip() else "",
                "done": checkbox.isChecked(),
                "completed_time": completed_time
            })
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        if not os.path.exists(TASKS_FILE):
            return
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {}
        self.pomodoro_count = data.get("pomodoro_count", 0)
        self.update_pomodoro_counter()
        for task in data.get("tasks", []):
            self._add_task_widget(task["text"], task.get("desc", ""), task.get("done", False), task.get("completed_time", None))

class CustomTaskPopup(QDialog):
    def __init__(self, parent=None, text="", desc=""):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setFixedSize(350, 380)
        self.result = False
        self.task_text = ""
        self.desc_text = ""
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
        card_layout.setSpacing(10)
        title_label = QLabel("Görevi Düzenle" if text else "Yeni Görev")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #eb5539; background: none; border: none;")
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)
        self.input = QLineEdit()
        self.input.setFont(QFont("Segoe UI", 14))
        self.input.setPlaceholderText("Görev girin...")
        self.input.setText(text)
        self.input.setMaxLength(50)
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
        hint = QLabel("Maksimum 50 karakter")
        hint.setFont(QFont("Segoe UI", 9))
        hint.setStyleSheet("color: #bababa; border: none; margin-right: 4px;")
        hint.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        card_layout.addWidget(hint)
        self.desc_input = QTextEdit()
        self.desc_input.setFont(QFont("Segoe UI", 12))
        self.desc_input.setPlaceholderText("Açıklama (isteğe bağlı)")
        self.desc_input.setText(desc)
        self.desc_input.setMaximumHeight(100)
        self.desc_input.setMinimumHeight(60)
        self.desc_input.setStyleSheet("""
            QTextEdit {
                border: 1.5px solid #e5be8e;
                border-radius: 6px;
                padding: 6px 9px;
                background-color: #fff;
                color: #666;
            }
            QTextEdit QScrollBar:vertical {
                background: #f5f5f5;
                width: 10px;
                margin: 2px 0 2px 0;
                border-radius: 5px;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: #2ec4b6;
                min-height: 20px;
                border-radius: 5px;
            }
        """)
        card_layout.addWidget(self.desc_input)
        card_layout.addSpacing(8)
        button_row = QHBoxLayout()
        cancel_btn = OvalButton("İptal")
        cancel_btn.setFixedSize(100, 40)
        cancel_btn.clicked.connect(self.reject)
        button_row.addWidget(cancel_btn)
        add_btn = OvalButton("Kaydet" if text else "Ekle")
        add_btn.setFixedSize(100, 40)
        add_btn.clicked.connect(self.accept)
        button_row.addWidget(add_btn)
        card_layout.addLayout(button_row)
        outer_layout.addWidget(card)
    def accept(self):
        self.result = True
        self.task_text = self.input.text()
        self.desc_text = self.desc_input.toPlainText()
        super().accept()
    def reject(self):
        self.result = False
        super().reject()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PomodoroApp()
    win.show()
    sys.exit(app.exec())
