import sys
import html
import logging
import re
from datetime import datetime

from PySide6.QtCore import Qt, Slot, Signal, QObject, QElapsedTimer, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QFrame, QMainWindow, QPushButton, QVBoxLayout, QWidget, QPlainTextEdit, QHBoxLayout, QDialog,
    QLabel, QScrollArea,
     )

from src.core.settings import Settings
from src.core.utils import ROOT
from src.ui.settings import SettingsWidget
from src.ui.run import RunWidget
from src.ui.progress import ProgressWidget
from src.ui.theme import STYLESHEET, Colors, mono_font


class LogEmitter(QObject):
    log_stream = Signal(str, int, str)  # message, level, logger name

    def __init__(self):
        super().__init__()

class LogRedirector(logging.Handler):
    def __init__(self, emitter: LogEmitter):
        super().__init__()
        self.emitter = emitter
        self.log_level = logging.DEBUG # default value; use setter at runtime

    def emit(self, record):
        msg = record.getMessage()
        if record.exc_info:
            msg += "\n" + logging.Formatter().formatException(record.exc_info)
        self.emitter.log_stream.emit(msg, record.levelno, record.name)

    def set_level(self, level):
        self.log_level = level
        self.setLevel(level)

    def flush(self):
        pass

class MainWindow(QMainWindow):
    # matches Result.__str__ output, e.g. "(Fail) Failed after 3 attempts" or "Success"
    RESULT_PATTERN = re.compile(r"^\(?(Success|Fail|Crash)\)?(\s|$)")

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Shipment Tracker")
        self.setWindowIcon(QIcon(str(ROOT / "data" / "icons" / "rbt.ico")))
        self.resize(1180, 760)
        self.setMinimumSize(1000, 600)

        self.has_console = False
        self.counts = {"Success": 0, "Fail": 0, "Crash": 0}

        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.main_layout.addWidget(self.get_starting_widget())
        self.main_layout.addWidget(self.get_activity_widget(), stretch=1)
        self.main_widget.setLayout(self.main_layout)

        self.setCentralWidget(self.main_widget)

        # elapsed time shown in the status pill while running
        self.elapsed = QElapsedTimer()
        self.tick_timer = QTimer(self)
        self.tick_timer.setInterval(1000)
        self.tick_timer.timeout.connect(self.update_elapsed)

    # ╭────────────────────────────────────────────────╮
    # │                     Layout                     │
    # ╰────────────────────────────────────────────────╯
    def get_starting_widget(self):
        self.starting_group = QFrame()
        self.starting_group.setObjectName("sidebar")
        self.starting_group.setFixedWidth(390)
        self.starting_layout = QVBoxLayout(self.starting_group)
        self.starting_layout.setContentsMargins(20, 22, 20, 20)
        self.starting_layout.setSpacing(16)

        # header
        title = QLabel("Shipment Tracker")
        title.setObjectName("appTitle")
        subtitle = QLabel("Pick sources to scrape and carriers to track.")
        subtitle.setObjectName("appSubtitle")
        header = QVBoxLayout()
        header.setSpacing(2)
        header.addWidget(title)
        header.addWidget(subtitle)
        self.starting_layout.addLayout(header)

        # settings (scrollable)
        self.settings_widget = SettingsWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(self.settings_widget)
        self.starting_layout.addWidget(scroll, stretch=1)

        self.run_widget = RunWidget()
        self.starting_layout.addWidget(self.run_widget)

        return self.starting_group

    def get_activity_widget(self):
        container = QWidget()
        lyt = QVBoxLayout(container)
        lyt.setContentsMargins(24, 22, 24, 24)
        lyt.setSpacing(12)

        # header row: title, result counters, status pill, clear
        header = QHBoxLayout()
        header.setSpacing(10)
        title = QLabel("Activity")
        title.setObjectName("appTitle")
        header.addWidget(title)
        header.addStretch()

        self.stat_labels = {}
        for key, color in [("Success", Colors.SUCCESS), ("Fail", Colors.WARNING), ("Crash", Colors.ERROR)]:
            lbl = QLabel()
            lbl.setObjectName("stat")
            lbl.setStyleSheet(f"color: {color};")
            lbl.setToolTip(f"{key} count for this session")
            self.stat_labels[key] = lbl
            header.addWidget(lbl)
        self.update_counts()

        self.status_pill = QLabel()
        self.status_pill.setObjectName("pill")
        header.addWidget(self.status_pill)
        self.set_status("idle", "Idle")

        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("secondary")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self.clear_console)
        header.addWidget(clear_btn)
        lyt.addLayout(header)

        self.progress_widget = ProgressWidget()
        self.progress_widget.set_enabled_services(self.settings_widget.get_enabled("track"))
        self.settings_widget.carriers_changed.connect(self.progress_widget.set_enabled_services)
        lyt.addWidget(self.progress_widget)

        self.console = QPlainTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        self.console.setFont(mono_font(10))
        self.console.setPlaceholderText("Logs will appear here once a run starts.")
        self.console.setMaximumBlockCount(5000)
        lyt.addWidget(self.console, stretch=1)

        return container

    # ╭────────────────────────────────────────────────╮
    # │                    Console                     │
    # ╰────────────────────────────────────────────────╯
    @Slot()
    def add_terminal_to_window(self):
        log_level = logging.DEBUG if Settings.get_settings()['extras']['debug_mode'] else logging.INFO

        if self.has_console:
            self.log_redirector.set_level(log_level)
            return

        self.log_emitter = LogEmitter()
        self.log_redirector = LogRedirector(self.log_emitter)
        self.log_redirector.set_level(log_level)

        self.log_emitter.log_stream.connect(self.add_log_line)
        logging.getLogger().addHandler(self.log_redirector)

        self.has_console = True

    @Slot(str, int, str)
    def add_log_line(self, msg, level, name):
        result = self.RESULT_PATTERN.match(msg) if name == "tracker" else None
        if result:
            self.counts[result.group(1)] += 1
            self.update_counts()

        if result:
            color = {"Success": Colors.SUCCESS, "Fail": Colors.WARNING, "Crash": Colors.ERROR}[result.group(1)]
        elif level >= logging.ERROR:
            color = Colors.ERROR
        elif level >= logging.WARNING:
            color = Colors.WARNING
        elif level <= logging.DEBUG:
            color = Colors.MUTED
        else:
            color = Colors.TEXT

        time_str = datetime.now().strftime("%H:%M:%S")
        prefix = f'<span style="color:{Colors.FAINT}">{time_str}</span>&nbsp;&nbsp;'
        if self.log_redirector.log_level == logging.DEBUG:
            prefix += f'<span style="color:{Colors.ACCENT}">{html.escape(name)}</span>&nbsp;&nbsp;'

        body = html.escape(msg).replace("\n", "<br>")
        self.console.appendHtml(f'{prefix}<span style="color:{color}">{body}</span>')

    @Slot()
    def add_text_to_console(self, text):
        cursor = self.console.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text)
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()

    @Slot()
    def clear_console(self):
        self.console.clear()
        self.counts = {k: 0 for k in self.counts}
        self.update_counts()

    def update_counts(self):
        symbols = {"Success": "✓", "Fail": "✗", "Crash": "⚠"}
        for key, lbl in self.stat_labels.items():
            lbl.setText(f"{symbols[key]} {self.counts[key]}")

    # ╭────────────────────────────────────────────────╮
    # │                     Status                     │
    # ╰────────────────────────────────────────────────╯
    def set_status(self, state, text):
        self.status_pill.setText(text)
        self.status_pill.setProperty("state", state)
        self.status_pill.style().unpolish(self.status_pill)
        self.status_pill.style().polish(self.status_pill)

    def _elapsed_str(self):
        secs = self.elapsed.elapsed() // 1000
        return f"{secs // 60:02d}:{secs % 60:02d}"

    @Slot()
    def update_elapsed(self):
        if self.status_pill.property("state") == "running":
            self.set_status("running", f"Running · {self._elapsed_str()}")

    def on_run_started(self):
        self.disable_buttons()
        self.progress_widget.reset()
        self.elapsed.start()
        self.tick_timer.start()
        self.set_status("running", "Running · 00:00")

    def on_run_finished(self):
        self.tick_timer.stop()
        self.progress_widget.finish()
        self.settings_widget.setEnabled(True)
        self.set_status("done", f"Finished · {self._elapsed_str()}")

    # ╭────────────────────────────────────────────────╮
    # │                    Dialogs                     │
    # ╰────────────────────────────────────────────────╯
    @Slot()
    def show_continue_dialog(self):
        self.set_status("waiting", "Waiting for login")

        dlg = QDialog(self)
        dlg.setWindowTitle("Manual login")
        dlg.setMinimumWidth(440)

        title = QLabel("Complete the Freightcom login")
        title.setObjectName("appTitle")
        label = QLabel("Finish logging in (including any captcha) in the browser window, "
                       "then continue once the main page has loaded.")
        label.setObjectName("muted")
        label.setWordWrap(True)

        continue_btn = QPushButton("Login complete")
        continue_btn.setObjectName("primary")
        continue_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        continue_btn.setMinimumHeight(46)
        continue_btn.clicked.connect(self.run_widget.unpause_worker)
        continue_btn.clicked.connect(lambda: self.set_status("running", f"Running · {self._elapsed_str()}"))
        continue_btn.clicked.connect(dlg.accept)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(label)
        layout.addSpacing(8)
        layout.addWidget(continue_btn)

        dlg.show()

    @Slot()
    def disable_buttons(self):
        self.settings_widget.setEnabled(False)

    @Slot()
    def save_settings(self):
        self.settings_widget.save_settings_to_file()

def main():
    app = QApplication()
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
