from PySide6.QtWidgets import (
    QSpinBox, QWidget,
    QVBoxLayout, QPushButton, QLabel,
    QCheckBox, QGroupBox, QHBoxLayout
)

from core.settings import Settings

class SettingsWidget(QWidget):
    checkboxes = {}
    labels = {}

    def __init__(self):
        super().__init__()
        if Settings.file_exists():
            Settings.load_from_file()

        overall_layout = QVBoxLayout()

        scrape_container = QGroupBox("Sources")
        scrape_layout = QVBoxLayout()

        self.cb_eshipper = QCheckBox("Eshipper")
        self.cb_ems = QCheckBox("EMS")
        self.cb_freightcom = QCheckBox("Freightcom")
        
        scrape_layout.addWidget(self.cb_eshipper)
        scrape_layout.addWidget(self.cb_ems)
        scrape_layout.addWidget(self.cb_freightcom)

        scrape_container.setLayout(scrape_layout)

        carrier_container = QGroupBox("Carriers")
        carrier_layout = QVBoxLayout()

        self.cb_canadapost = QCheckBox("Canada Post")
        self.cb_purolator = QCheckBox("Purolator")
        self.cb_ups = QCheckBox("UPS")
        self.cb_canpar = QCheckBox("Canpar")
        self.cb_fedex = QCheckBox("Fedex")

        carrier_layout.addWidget(self.cb_canadapost)
        carrier_layout.addWidget(self.cb_purolator)
        carrier_layout.addWidget(self.cb_ups)
        carrier_layout.addWidget(self.cb_canpar)
        carrier_layout.addWidget(self.cb_fedex)

        carrier_container.setLayout(carrier_layout)

        extras_container = QGroupBox("Extras")
        extras_layout = QVBoxLayout()

        self.cb_ignore_already_tracked = QCheckBox("Ignore already tracked shipments")
        self.cb_reuse_data = QCheckBox("Reuse previous data")
        self.cb_debug = QCheckBox("Debug Mode")
        self.label_day_diff = QLabel("Day difference:")
        self.sb_day_diff = QSpinBox()
        self.sb_day_diff.setMinimum(0)
        self.sb_day_diff.setMaximum(1000)

        extras_layout.addWidget(self.cb_ignore_already_tracked)
        extras_layout.addWidget(self.cb_reuse_data)
        extras_layout.addWidget(self.cb_debug)
        extras_layout.addWidget(self.label_day_diff)
        extras_layout.addWidget(self.sb_day_diff)

        extras_container.setLayout(extras_layout)

        overall_layout.addWidget(scrape_container)
        overall_layout.addWidget(carrier_container)
        overall_layout.addWidget(self._get_button_container())
        overall_layout.addWidget(extras_container)

        self.setLayout(overall_layout)
        self.load_settings_to_ui()

    def _get_button_container(self):
        btn_group = QWidget()
        btn_layout = QHBoxLayout()

        btn_save = QPushButton("Set all")
        btn_reset = QPushButton("Set none")

        btn_save.clicked.connect(self.set_btn_clicked)
        btn_reset.clicked.connect(self.reset_btn_clicked)
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_reset)

        btn_group.setLayout(btn_layout)
        return btn_group

    def set_btn_clicked(self):
        self.set_normal_settings_to(True)

    def set_normal_settings_to(self, val: bool, all: bool = False):
        self.cb_eshipper.setChecked(val)
        self.cb_ems.setChecked(val)
        self.cb_freightcom.setChecked(val)

        self.cb_canadapost.setChecked(val)
        self.cb_purolator.setChecked(val)
        self.cb_ups.setChecked(val)
        self.cb_canpar.setChecked(val)
        self.cb_fedex.setChecked(val)

        if all:
            self.cb_reuse_data.setChecked(val)
            self.cb_ignore_already_tracked.setChecked(val)
            self.sb_day_diff.setValue(3)
            self.cb_debug.setChecked(val)

    def load_settings_to_ui(self):
        if Settings.file_exists():
            self.cb_eshipper.setChecked(Settings.get_settings()['scrape']['eshipper'])
            self.cb_ems.setChecked(Settings.get_settings()['scrape']['ems'])
            self.cb_freightcom.setChecked(Settings.get_settings()['scrape']['freightcom'])

            self.cb_canadapost.setChecked(Settings.get_settings()['track']['canada post'])
            self.cb_purolator.setChecked(Settings.get_settings()['track']['purolator'])
            self.cb_ups.setChecked(Settings.get_settings()['track']['ups'])
            self.cb_canpar.setChecked(Settings.get_settings()['track']['canpar'])
            self.cb_fedex.setChecked(Settings.get_settings()['track']['fedex'])

            self.cb_reuse_data.setChecked(Settings.get_settings()['reuse_data'])
            self.cb_ignore_already_tracked.setChecked(Settings.get_settings()['ignore_already_tracked'])
            self.sb_day_diff.setValue(Settings.get_settings()['day_diff'])
            self.cb_debug.setChecked(Settings.get_settings()['debug'])
        else:
            self.set_normal_settings_to(False, all=True)

    def save_settings_to_file(self):
        s = Settings.get_settings()

        s['scrape']['eshipper'] = self.cb_eshipper.isChecked()
        s['scrape']['ems'] = self.cb_ems.isChecked()
        s['scrape']['freightcom'] = self.cb_freightcom.isChecked()  

        s['track']['canada post'] = self.cb_canadapost.isChecked()
        s['track']['purolator'] = self.cb_purolator.isChecked()   
        s['track']['ups'] = self.cb_ups.isChecked() 
        s['track']['canpar'] = self.cb_canpar.isChecked()
        s['track']['fedex'] = self.cb_fedex.isChecked()

        s['reuse_data'] = self.cb_reuse_data.isChecked()
        s['ignore_already_tracked'] = self.cb_ignore_already_tracked.isChecked()
        s['debug'] = self.cb_debug.isChecked()
        s['day_diff'] = self.sb_day_diff.value()

        Settings.write_to_file()

    def reset_btn_clicked(self):
        self.set_normal_settings_to(False)

    def close_self(self):
        self.close()
        



