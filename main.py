import sys
import logging
from typing import Optional
from PySide6.QtCore import Qt, Slot, Signal, QObject
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QGroupBox, QMainWindow, QPushButton, QStatusBar, QVBoxLayout, QWidget, QPlainTextEdit, QHBoxLayout, QDialog,
    QLabel,
     )

from ui.settings import SettingsWidget
from ui.run import RunWidget

class LogEmitter(QObject):
    log_stream = Signal(str)

    def __init__(self):
        super().__init__()

class LogRedirector(logging.Handler):
    def __init__(self, emitter: LogEmitter):
        super().__init__()
        self.emitter = emitter

    def emit(self, record):
        self.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        record = self.format(record)
        self.emitter.log_stream.emit(record)

    def flush(self):
        pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Shipment Tracker")
        self.resize(300, 650)

        self.has_console = False
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout()

        self.main_layout.addWidget(self.get_starting_widget(), stretch=3)
        self.main_widget.setLayout(self.main_layout)

        self.setCentralWidget(self.main_widget)

        # status bar
        self.setStatusBar(QStatusBar(self))
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

    def get_starting_widget(self):
        self.starting_group = QWidget()
        self.starting_layout = QVBoxLayout()

        self.settings_widget = SettingsWidget()
        self.run_widget = RunWidget()
        
        self.starting_layout.addWidget(self.settings_widget)
        self.starting_layout.addWidget(self.run_widget)

        self.starting_group.setLayout(self.starting_layout)

        return self.starting_group

    @Slot()
    def add_terminal_to_window(self):
        if self.has_console:
            return

        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("font-size: 10pt;")

        self.main_layout.addWidget(self.console, stretch=7)
        self.resize(self.width() + 500, self.height())

        self.log_emitter = LogEmitter()
        self.log_redirector = LogRedirector(self.log_emitter)
        
        self.log_emitter.log_stream.connect(self.console.appendPlainText)
        logging.getLogger().addHandler(self.log_redirector)
        self.has_console = True


    @Slot()
    def add_text_to_console(self, text):
        cursor = self.console.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text)
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()

    @Slot()
    def show_continue_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Manual login")
        dlg.resize(400,200)
        
        continue_btn = QPushButton("Login complete")
        label = QLabel("Complete login to freightcom then click the button once the main page is reached")
        label_font = QFont()

        label_font.setBold(True)
        label_font.setPointSize(15)

        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(label_font)

        continue_btn.setMinimumWidth(dlg.width())
        continue_btn.setMinimumHeight(75)
        continue_btn.clicked.connect(self.run_widget.unpause_worker)
        continue_btn.clicked.connect(dlg.accept)

        layout = QVBoxLayout(dlg)
        layout.addWidget(label)
        layout.addWidget(continue_btn)

        dlg.show()

    @Slot()
    def disable_buttons(self):
        pass

    @Slot()
    def save_settings(self):
        self.settings_widget.save_settings_to_file()

def main():
    app = QApplication()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
