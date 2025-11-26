import sys
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import (
    QApplication, QGroupBox, QMainWindow, QStatusBar, QVBoxLayout, QWidget, QPlainTextEdit
     )

from ui.settings import SettingsWidget
from ui.run import RunWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Shipment Tracker")
        self.resize(300, 650)

        self.main_widget = self.build_main_widget()

        self.setCentralWidget(self.main_widget)

        # status bar
        self.setStatusBar(QStatusBar(self))
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

    def build_main_widget(self):
        self.main_group = QWidget()
        self.main_layout = QVBoxLayout()

        self.settings_widget = SettingsWidget()
        self.run_widget = RunWidget()
        
        self.main_layout.addWidget(self.settings_widget)
        self.main_layout.addWidget(self.run_widget)

        self.main_group.setLayout(self.main_layout)

        return self.main_group

    @Slot()
    def add_terminal_to_window(self):
        if self.console:
            return
        
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)

        self.main_layout.addWidget(self.console)
        self.resize(self.width() + 400, self.height())

    @Slot()
    def add_text_to_console(self, text):
        cursor = self.console.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text)
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()

def main():
    app = QApplication()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
