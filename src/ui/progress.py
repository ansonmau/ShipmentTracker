from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget,
)


# ╭────────────────────────────────────────────────╮
# │                    Helpers                     │
# ╰────────────────────────────────────────────────╯
# key (as used in settings / tracker) -> (block text, display name)
SERVICES = {
    "canada post": ("CP",  "Canada Post"),
    "purolator":   ("PUR", "Purolator"),
    "ups":         ("UPS", "UPS"),
    "canpar":      ("CPR", "Canpar"),
    "fedex":       ("FDX", "FedEx"),
}


def _repolish(widget, state):
    widget.setProperty("state", state)
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def _card(title:str):
    card = QFrame()
    card.setObjectName("card")
    lyt = QVBoxLayout(card)
    lyt.setContentsMargins(16, 12, 16, 14)
    lyt.setSpacing(10)

    title_lbl = QLabel(title.upper())
    title_lbl.setObjectName("cardTitle")
    lyt.addWidget(title_lbl)

    return card, lyt


# ╭────────────────────────────────────────────────╮
# │                Service Progress                │
# ╰────────────────────────────────────────────────╯
class ServiceProgress(QWidget):
    """ Row of blocks, one per carrier, lit up in order as tracking moves along """
    PENDING = "pending"
    ACTIVE  = "active"
    DONE    = "done"
    SKIPPED = "skipped"

    def __init__(self):
        super().__init__()
        self.services = []      # keys, in display order
        self.states   = {}      # key -> state
        self.blocks   = {}      # key -> QLabel
        self.links    = []      # QFrame between blocks[i] and blocks[i+1]

        self.lyt = QHBoxLayout(self)
        self.lyt.setContentsMargins(0, 0, 0, 0)
        self.lyt.setSpacing(6)

        self.empty_lbl = QLabel("No carriers selected")
        self.empty_lbl.setObjectName("muted")

    def set_services(self, services:list, skipped:list = None):
        skipped = skipped or []
        self.services = list(services) + [s for s in skipped if s not in services]
        self.states   = {s: (self.SKIPPED if s in skipped else self.PENDING) for s in self.services}
        self._rebuild()

    def set_current(self, service:str):
        """ marks every active service before `service` as done and `service` as active """
        if service not in self.states:
            return

        for s in self.services:
            if s == service:
                self.states[s] = self.ACTIVE
                break
            if self.states[s] != self.SKIPPED:
                self.states[s] = self.DONE
        self._refresh()

    def set_done(self, service:str):
        if service in self.states:
            self.states[service] = self.DONE
            self._refresh()

    def _rebuild(self):
        while self.lyt.count():
            w = self.lyt.takeAt(0).widget()
            if w and w is not self.empty_lbl:
                w.deleteLater()
        self.blocks = {}
        self.links  = []

        if not self.services:
            self.lyt.addWidget(self.empty_lbl)
            self.empty_lbl.show()
            return
        self.empty_lbl.hide()

        for i, s in enumerate(self.services):
            if i > 0:
                link = QFrame()
                link.setObjectName("serviceLink")
                link.setFixedHeight(2)
                link.setMinimumWidth(6)
                self.lyt.addWidget(link, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)
                self.links.append(link)

            short, name = SERVICES.get(s, (s[:3].upper(), s.title()))
            block = QLabel(short)
            block.setObjectName("serviceBlock")
            block.setAlignment(Qt.AlignmentFlag.AlignCenter)
            block.setFixedSize(46, 32)
            block.setToolTip(name)
            self.lyt.addWidget(block)
            self.blocks[s] = block

        self._refresh()

    def _refresh(self):
        for s, block in self.blocks.items():
            _repolish(block, self.states[s])

        # a link is lit once the block before it is done
        for i, link in enumerate(self.links):
            _repolish(link, self.DONE if self.states[self.services[i]] == self.DONE else self.PENDING)


# ╭────────────────────────────────────────────────╮
# │                 Progress Card                  │
# ╰────────────────────────────────────────────────╯
class ProgressWidget(QWidget):
    REFRESH_MS = 200

    def __init__(self):
        super().__init__()
        self.enabled_services = []
        self.current_service  = None
        self.completed        = 0
        self.total            = 0
        self.failed           = 0

        # ui refreshes are throttled; signals only store the latest values
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setSingleShot(True)
        self.refresh_timer.setInterval(self.REFRESH_MS)
        self.refresh_timer.timeout.connect(self._refresh)

        lyt = QHBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(12)

        # ── services ──────────────────────────────────────────────────────
        services_card, services_lyt = _card("Services")
        self.service_progress = ServiceProgress()
        services_lyt.addStretch()
        services_lyt.addWidget(self.service_progress)
        services_lyt.addStretch()

        # ── tracking ──────────────────────────────────────────────────────
        tracking_card, tracking_lyt = _card("Tracking")

        top_row = QHBoxLayout()
        self.service_lbl = QLabel()
        self.service_lbl.setObjectName("progressService")
        self.percent_lbl = QLabel()
        self.percent_lbl.setObjectName("progressPercent")
        top_row.addWidget(self.service_lbl, alignment=Qt.AlignmentFlag.AlignBottom)
        top_row.addStretch()
        top_row.addWidget(self.percent_lbl, alignment=Qt.AlignmentFlag.AlignBottom)

        self.bar = QProgressBar()
        self.bar.setObjectName("trackingBar")
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(8)

        self.count_lbl = QLabel()
        self.count_lbl.setObjectName("progressCount")

        tracking_lyt.addLayout(top_row)
        tracking_lyt.addWidget(self.bar)
        tracking_lyt.addWidget(self.count_lbl)

        lyt.addWidget(services_card, stretch=1)
        lyt.addWidget(tracking_card, stretch=1)

        self.reset()

    # ────────────────────────────────< API >──────────────────────────────
    @Slot(list)
    def set_enabled_services(self, services:list):
        """ carriers selected in settings; only shown while not running """
        self.enabled_services = services
        self.service_progress.set_services(services)

    def reset(self):
        self.refresh_timer.stop()
        self.current_service = None
        self.completed = 0
        self.total     = 0
        self.failed    = 0
        self.service_progress.set_services(self.enabled_services)
        self._refresh()

    @Slot(list)
    def set_active_services(self, services:list):
        """ carriers that will actually be tracked; enabled ones without shipments are skipped """
        skipped = [s for s in self.enabled_services if s not in services]
        self.service_progress.set_services(services, skipped)

    @Slot(str, str, int, int)
    def update_progress(self, phase, item, current, total):
        if phase != "track":
            return

        if item != self.current_service:
            self.current_service = item
            self.failed = 0
            self.service_progress.set_current(item)

        self.completed = current
        self.total     = total
        self._schedule_refresh()

    @Slot(int, int, int)
    def update_results(self, success, fail, crash):
        self.failed = fail + crash
        self._schedule_refresh()

    def finish(self):
        if self.current_service and self.total and self.completed >= self.total:
            self.service_progress.set_done(self.current_service)
        self.refresh_timer.stop()
        self._refresh()

    # ───────────────────────────────< private >──────────────────────────────
    def _schedule_refresh(self):
        if not self.refresh_timer.isActive():
            self.refresh_timer.start()

    @Slot()
    def _refresh(self):
        if not self.current_service:
            self.service_lbl.setText("Waiting to start")
            self.percent_lbl.setText("—")
            self.bar.setRange(0, 1)
            self.bar.setValue(0)
            self.count_lbl.setText(" ")
            return

        percent = int((self.completed / self.total) * 100) if self.total else 0
        self.service_lbl.setText(SERVICES.get(self.current_service, ("", self.current_service.title()))[1])
        self.percent_lbl.setText(f"{percent}%")
        self.bar.setRange(0, max(self.total, 1))
        self.bar.setValue(self.completed)

        count_text = f"{self.completed} / {self.total}"
        if self.failed:
            count_text += f"  ·  {self.failed} failed"
        self.count_lbl.setText(count_text)
