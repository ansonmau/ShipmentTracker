from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit, QSizePolicy, QSpinBox, QWidget,
    QVBoxLayout, QPushButton, QLabel, QStatusBar,
    QCheckBox, QGroupBox, QHBoxLayout
)

from app import run as run_main_app

class RunWidget(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
    
        self.btn_run = QPushButton("Run")
        self.btn_run.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.btn_run.clicked.connect(self.run_btn_clicked)

        main_layout.addWidget(self.btn_run)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.setLayout(main_layout)
    
    def run_btn_clicked(self):
        self.worker = Worker()
        self.w_thread = QThread()
        
        self.worker.moveToThread(self.w_thread)
        self.w_thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.w_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.w_thread.finished.connect(self.w_thread.deleteLater)

        self.w_thread.start()

        
class ConsoleStream(QObject):
    txt_stream = Signal(str)

    def write(self, text):
        if text:
            self.txt_stream.emit(str(text))


class Worker(QObject):
    progress = Signal(int)
    finished = Signal()

    @Slot()
    def run(self):
        run_main_app()
        self.finished.emit()

