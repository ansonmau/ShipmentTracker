import threading
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
        self.pause_event = threading.Event()

        main_layout = QVBoxLayout()
    
        self.btn_run = QPushButton("Run")
        self.btn_run.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.btn_run.clicked.connect(self.run_btn_clicked)

        main_layout.addWidget(self.btn_run)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.setLayout(main_layout)
    
    def run_btn_clicked(self):
        self.window().add_terminal_to_window()
        self.window().save_settings()
        self.start_main_thread()

    def start_main_thread(self):
        self.worker = Worker(self.pause_event)
        self.w_thread = QThread()
        
        self.worker.moveToThread(self.w_thread)
        self.w_thread.started.connect(self.worker.run)

        self.worker.pause_signal.connect(self.window().show_continue_dialog)

        self.worker.finished.connect(self.w_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.w_thread.finished.connect(self.w_thread.deleteLater)

        self.w_thread.start()

    def unpause_worker(self):
        self.pause_event.set()
        

class Worker(QObject):
    progress = Signal(int)
    finished = Signal()
    pause_signal = Signal()
    def __init__(self, pause_event):
        super().__init__()
        self.pause_event = pause_event

    @Slot()
    def run(self):
        run_main_app(self)
        self.finished.emit()

