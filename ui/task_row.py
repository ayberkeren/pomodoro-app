# ui/task_row.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QCheckBox, QPushButton, QMenu, QInputDialog
from PySide6.QtGui import QAction
from utils.styles import TASK_DONE_COLOR
import time

class TaskRow(QWidget):
    def __init__(self, text, parent_layout, on_select_callback):
        super().__init__()
        self.text = text
        self.description = ""
        self.parent_layout = parent_layout
        self.created_at = time.time()
        self.done_at = None
        self.on_select = on_select_callback

        self.checkbox = QCheckBox()
        self.label = QLabel(text)
        self.label.setStyleSheet("font-size: 14px;")

        self.menu_button = QPushButton("⋮")
        self.menu_button.setFixedSize(24, 24)
        self.menu_button.setStyleSheet("border: none; font-size: 18px;")
        self.menu_button.clicked.connect(self.open_menu)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.menu_button)
        self.setLayout(layout)

        self.checkbox.stateChanged.connect(self.toggle_done)
        self.label.mousePressEvent = self.select_as_active

    def toggle_done(self, state):
        if state == 2:
            self.done_at = time.time()
            self.label.setStyleSheet(f"font-size: 14px; color: {TASK_DONE_COLOR}; text-decoration: line-through;")
        else:
            self.done_at = None
            self.label.setStyleSheet("font-size: 14px; color: black; text-decoration: none;")
        self.reorder()

    def reorder(self):
        self.setParent(None)
        self.parent_layout.removeWidget(self)

        widgets = []
        for i in range(self.parent_layout.count()):
            w = self.parent_layout.itemAt(i).widget()
            if w and isinstance(w, TaskRow):
                widgets.append(w)

        widgets.append(self)
        widgets.sort(key=lambda w: (w.done_at is None, w.done_at if w.done_at else 0))

        while self.parent_layout.count():
            item = self.parent_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        for w in widgets:
            self.parent_layout.addWidget(w)

    def select_as_active(self, event):
        self.on_select(self.label.text())

    def open_menu(self):
        menu = QMenu()
        menu.addAction("Başlığı Düzenle", self.edit_title)
        menu.addAction("Açıklama Ekle/Göster", self.edit_description)
        menu.addSeparator()
        menu.addAction("Görevi Sil", self.delete_task)
        menu.exec(self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft()))

    def edit_title(self):
        text, ok = QInputDialog.getText(self, "Başlık Düzenle", "Yeni başlık:", text=self.label.text())
        if ok and text.strip():
            self.label.setText(text.strip())

    def edit_description(self):
        text, ok = QInputDialog.getMultiLineText(self, "Açıklama", "Açıklama girin:", self.description)
        if ok:
            self.description = text.strip()

    def delete_task(self):
        self.setParent(None)
        self.parent_layout.removeWidget(self)
        self.deleteLater()
