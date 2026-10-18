import threading
import logging
from PySide6.QtCore import QObject, Qt, Signal, Slot, QThread
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton
)

from src.ShipmentTracker import run as run_main_app

class RunWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.pause_event = threading.Event()

        main_layout = QVBoxLayout()
    
        self.btn_run = QPushButton("Run")
        self.btn_run.setObjectName("primary")
        self.btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_run.setMinimumHeight(48)
        self.btn_run.clicked.connect(self.run_btn_clicked)

        main_layout.addWidget(self.btn_run)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.setLayout(main_layout)
    
    def run_btn_clicked(self):
        self.window().save_settings()
        self.window().add_terminal_to_window()
        self.set_running(True)
        self.window().on_run_started()
        self.start_main_thread()

    def set_running(self, running):
        self.btn_run.setEnabled(not running)
        self.btn_run.setText("Running…" if running else "Run")

    def on_run_finished(self):
        self.set_running(False)
        self.window().on_run_finished()


    def start_main_thread(self):
        self.worker = Worker(self.pause_event)
        self.w_thread = QThread()
        
        self.worker.moveToThread(self.w_thread)
        self.w_thread.started.connect(self.worker.run)

        self.worker.pause_signal.connect(self.window().show_continue_dialog)

        progress = self.window().progress_widget
        self.worker.services_update.connect(progress.set_active_services)
        self.worker.status_update.connect(progress.update_progress)
        self.worker.result_update.connect(progress.update_results)

        self.worker.finished.connect(self.on_run_finished)
        self.worker.finished.connect(self.w_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.w_thread.finished.connect(self.w_thread.deleteLater)

        self.w_thread.start()

    def unpause_worker(self):
        self.pause_event.set()
        

class Worker(QObject):
    finished = Signal()
    pause_signal = Signal()
    stop_signal = Signal()
    status_update = Signal(str, str, int, int)  # phase, item, current, total
    result_update = Signal(int, int, int)        # success, fail, crash
    services_update = Signal(list)               # carriers to be tracked, in order

    def __init__(self, pause_event):
        super().__init__()
        self.pause_event = pause_event

    @Slot()
    def run(self):
        try:
            run_main_app(self)
        except Exception:
            logging.getLogger("Shipment Tracker").exception("Run crashed")
        finally:
            self.finished.emit()

