from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QCheckBox


# ╭────────────────────────────────────────────────╮
# │                     Colors                     │
# ╰────────────────────────────────────────────────╯
class Colors:
    BG          = "#0f1115"
    PANEL       = "#151922"
    CARD        = "#1a1f29"
    BORDER      = "#262d3a"
    BORDER_HI   = "#343d4e"
    TEXT        = "#e6e9ef"
    MUTED       = "#8b93a3"
    FAINT       = "#5b6372"
    ACCENT      = "#5b8cff"
    ACCENT_HI   = "#7aa2ff"
    ACCENT_LO   = "#4a76e0"
    ACCENT_SOFT = "rgba(91, 140, 255, 0.14)"
    SUCCESS     = "#3ecf8e"
    WARNING     = "#f5a524"
    ERROR       = "#f16b6b"
    CONSOLE     = "#0b0d11"


MONO_FAMILIES = ["JetBrains Mono", "Cascadia Mono", "Consolas", "DejaVu Sans Mono", "monospace"]


def mono_font(size=10):
    font = QFont()
    font.setFamilies(MONO_FAMILIES)
    font.setStyleHint(QFont.StyleHint.Monospace)
    font.setPointSize(size)
    return font


# ╭────────────────────────────────────────────────╮
# │                   Stylesheet                   │
# ╰────────────────────────────────────────────────╯
C = Colors
STYLESHEET = f"""
* {{
    font-family: "Segoe UI", "Inter", "Noto Sans", sans-serif;
    font-size: 13px;
    color: {C.TEXT};
}}

QMainWindow, QDialog {{
    background: {C.BG};
}}

QToolTip {{
    background: {C.CARD};
    border: 1px solid {C.BORDER_HI};
    padding: 4px 8px;
}}

/* ── panels / cards ───────────────────────────── */
#sidebar {{
    background: {C.PANEL};
    border-right: 1px solid {C.BORDER};
}}

#card {{
    background: {C.CARD};
    border: 1px solid {C.BORDER};
    border-radius: 12px;
}}

#appTitle {{
    font-size: 20px;
    font-weight: 700;
}}

#appSubtitle, #muted {{
    color: {C.MUTED};
}}

#cardTitle {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    color: {C.MUTED};
}}

#fieldLabel {{
    color: {C.MUTED};
}}

/* ── scroll area ──────────────────────────────── */
QScrollArea, QScrollArea > QWidget > QWidget {{
    background: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {C.BORDER_HI};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {C.FAINT};
}}
QScrollBar::add-line, QScrollBar::sub-line,
QScrollBar::add-page, QScrollBar::sub-page {{
    background: none;
    height: 0px;
}}

/* ── chips (sources / carriers) ───────────────── */
QPushButton#chip {{
    background: transparent;
    border: 1px solid {C.BORDER_HI};
    border-radius: 15px;
    padding: 6px 10px;
    color: {C.MUTED};
}}
QPushButton#chip:hover {{
    border-color: {C.FAINT};
    color: {C.TEXT};
}}
QPushButton#chip:checked {{
    background: {C.ACCENT_SOFT};
    border-color: {C.ACCENT};
    color: {C.ACCENT_HI};
    font-weight: 600;
}}
QPushButton#chip:disabled {{
    color: {C.FAINT};
    border-color: {C.BORDER};
}}
QPushButton#chip:checked:disabled {{
    background: rgba(91, 140, 255, 0.07);
    border-color: rgba(91, 140, 255, 0.35);
    color: rgba(122, 162, 255, 0.6);
}}

/* ── small text buttons ───────────────────────── */
QPushButton#link {{
    background: transparent;
    border: none;
    color: {C.MUTED};
    padding: 2px 6px;
    font-size: 12px;
}}
QPushButton#link:hover {{
    color: {C.ACCENT_HI};
}}
QPushButton#link:disabled {{
    color: {C.FAINT};
}}

/* ── primary button ───────────────────────────── */
QPushButton#primary {{
    background: {C.ACCENT};
    border: none;
    border-radius: 10px;
    padding: 12px;
    font-size: 15px;
    font-weight: 700;
    color: white;
}}
QPushButton#primary:hover {{
    background: {C.ACCENT_HI};
}}
QPushButton#primary:pressed {{
    background: {C.ACCENT_LO};
}}
QPushButton#primary:disabled {{
    background: {C.BORDER_HI};
    color: {C.MUTED};
}}

/* ── secondary button ─────────────────────────── */
QPushButton#secondary {{
    background: transparent;
    border: 1px solid {C.BORDER_HI};
    border-radius: 8px;
    padding: 5px 12px;
    color: {C.MUTED};
}}
QPushButton#secondary:hover {{
    color: {C.TEXT};
    border-color: {C.FAINT};
}}

/* ── disclosure (advanced) ────────────────────── */
QToolButton#disclosure {{
    background: transparent;
    border: none;
    color: {C.MUTED};
    font-size: 12px;
    padding: 2px 0px;
}}
QToolButton#disclosure:hover {{
    color: {C.TEXT};
}}

/* ── inputs ───────────────────────────────────── */
QLineEdit, QSpinBox {{
    background: {C.BG};
    border: 1px solid {C.BORDER_HI};
    border-radius: 8px;
    padding: 6px 10px;
    selection-background-color: {C.ACCENT};
}}
QLineEdit:focus, QSpinBox:focus {{
    border-color: {C.ACCENT};
}}
QLineEdit:disabled, QSpinBox:disabled {{
    color: {C.FAINT};
}}

/* ── console ──────────────────────────────────── */
QPlainTextEdit#console {{
    background: {C.CONSOLE};
    border: 1px solid {C.BORDER};
    border-radius: 12px;
    padding: 10px;
    selection-background-color: {C.ACCENT};
}}

/* ── status pill ──────────────────────────────── */
QLabel#pill {{
    border-radius: 11px;
    padding: 3px 12px;
    font-size: 12px;
    font-weight: 600;
    background: {C.BORDER};
    color: {C.MUTED};
}}
QLabel#pill[state="running"] {{
    background: rgba(91, 140, 255, 0.18);
    color: {C.ACCENT_HI};
}}
QLabel#pill[state="done"] {{
    background: rgba(62, 207, 142, 0.16);
    color: {C.SUCCESS};
}}
QLabel#pill[state="waiting"] {{
    background: rgba(245, 165, 36, 0.16);
    color: {C.WARNING};
}}

/* ── progress ─────────────────────────────────── */
QLabel#serviceBlock {{
    border: 1px solid {C.BORDER_HI};
    border-radius: 7px;
    background: transparent;
    color: {C.MUTED};
    font-size: 11px;
    font-weight: 700;
}}
QLabel#serviceBlock[state="active"] {{
    background: {C.ACCENT};
    border-color: {C.ACCENT};
    color: white;
}}
QLabel#serviceBlock[state="done"] {{
    background: rgba(62, 207, 142, 0.16);
    border-color: {C.SUCCESS};
    color: {C.SUCCESS};
}}
QLabel#serviceBlock[state="skipped"] {{
    border-style: dashed;
    border-color: {C.BORDER_HI};
    color: {C.FAINT};
}}

QFrame#serviceLink {{
    background: {C.BORDER_HI};
    border: none;
}}
QFrame#serviceLink[state="done"] {{
    background: {C.SUCCESS};
}}

QLabel#progressService {{
    font-size: 14px;
    font-weight: 600;
}}
QLabel#progressPercent {{
    font-size: 24px;
    font-weight: 700;
}}
QLabel#progressCount {{
    font-size: 11px;
    color: {C.MUTED};
}}

QProgressBar#trackingBar {{
    background: {C.BORDER};
    border: none;
    border-radius: 4px;
}}
QProgressBar#trackingBar::chunk {{
    background: {C.ACCENT};
    border-radius: 4px;
}}

QLabel#stat {{
    font-size: 12px;
    font-weight: 600;
    padding: 0px 4px;
}}
"""


# ╭────────────────────────────────────────────────╮
# │                 Toggle Switch                  │
# ╰────────────────────────────────────────────────╯
class ToggleSwitch(QCheckBox):
    """ QCheckBox drawn as a sliding switch. Keeps the isChecked/setChecked API. """
    TRACK_W = 34
    TRACK_H = 20
    GAP     = 10

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._offset = 0.0

        self._anim = QPropertyAnimation(self, b"offset", self)
        self._anim.setDuration(140)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.toggled.connect(self._on_toggled)

    def _get_offset(self):
        return self._offset

    def _set_offset(self, value):
        self._offset = value
        self.update()

    offset = Property(float, _get_offset, _set_offset)

    def _on_toggled(self, checked):
        end = 1.0 if checked else 0.0
        if not self.isVisible():
            self._anim.stop()
            self._set_offset(end)
            return
        self._anim.stop()
        self._anim.setStartValue(self._offset)
        self._anim.setEndValue(end)
        self._anim.start()

    def sizeHint(self):
        fm = self.fontMetrics()
        w = self.TRACK_W + self.GAP + fm.horizontalAdvance(self.text()) + 2
        h = max(self.TRACK_H, fm.height()) + 6
        return QSize(w, h)

    def minimumSizeHint(self):
        return self.sizeHint()

    def hitButton(self, pos):
        return self.rect().contains(pos)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self.isEnabled():
            p.setOpacity(0.45)

        # track
        top = (self.height() - self.TRACK_H) / 2
        track = QRectF(0, top, self.TRACK_W, self.TRACK_H)
        off_col = QColor(Colors.BORDER_HI)
        on_col  = QColor(Colors.ACCENT)
        t = self._offset
        mix = QColor(
            int(off_col.red()   + (on_col.red()   - off_col.red())   * t),
            int(off_col.green() + (on_col.green() - off_col.green()) * t),
            int(off_col.blue()  + (on_col.blue()  - off_col.blue())  * t),
        )
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(mix)
        p.drawRoundedRect(track, self.TRACK_H / 2, self.TRACK_H / 2)

        # knob
        d = self.TRACK_H - 6
        x = 3 + t * (self.TRACK_W - d - 6)
        p.setBrush(QColor("white"))
        p.drawEllipse(QRectF(x, top + 3, d, d))

        # label
        p.setPen(QColor(Colors.TEXT))
        text_rect = self.rect().adjusted(self.TRACK_W + self.GAP, 0, 0, 0)
        p.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.text())
        p.end()
