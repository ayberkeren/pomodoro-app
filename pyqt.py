# test_gui.py
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
import sys

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Merhaba Raspberry Pi!")
layout = QVBoxLayout()

label = QLabel("PyQt5 başarıyla çalışıyor 🎉")
layout.addWidget(label)

window.setLayout(layout)
window.show()

sys.exit(app.exec_())

