from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSpinBox, QWidget,
    QVBoxLayout, QPushButton, QLabel, QStatusBar,
    QCheckBox, QGroupBox, QHBoxLayout
)

import core.settings as settings

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        if settings.check_settings_exists():
            settings.load_settings()

        self.settings = settings.settings

        overall_layout = QVBoxLayout()

        scrape_area = QGroupBox("Scrape")
        scrape_layout = QVBoxLayout()

        self.cb_eshipper = QCheckBox("Eshipper")
        self.cb_ems = QCheckBox("EMS")
        self.cb_freightcom = QCheckBox("Freightcom")
        
        scrape_layout.addWidget(self.cb_eshipper)
        scrape_layout.addWidget(self.cb_ems)
        scrape_layout.addWidget(self.cb_freightcom)

        scrape_area.setLayout(scrape_layout)

        carrier_area = QGroupBox("Carriers")
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

        carrier_area.setLayout(carrier_layout)

        extras_area = QGroupBox("Extras")
        extras_layout = QVBoxLayout()

        self.cb_ignore_old = QCheckBox("Ignore previously tracked shipments")
        self.cb_reuse_data = QCheckBox("Reuse previous data")
        self.cb_clear_dls = QCheckBox("Clear current downloads folder")
        self.label_day_diff = QLabel("Day difference:")
        self.sb_day_diff = QSpinBox()
        self.sb_day_diff.setMinimum(0)
        self.sb_day_diff.setMaximum(1000)

        extras_layout.addWidget(self.cb_ignore_old)
        extras_layout.addWidget(self.cb_reuse_data)
        extras_layout.addWidget(self.cb_clear_dls)
        extras_layout.addWidget(self.label_day_diff)
        extras_layout.addWidget(self.sb_day_diff)

        extras_area.setLayout(extras_layout)

        overall_layout.addWidget(scrape_area)
        overall_layout.addWidget(carrier_area)
        overall_layout.addWidget(self._get_button_area())
        overall_layout.addWidget(extras_area)

        self.setLayout(overall_layout)
        self.load_settings_to_ui()

    def _get_button_area(self):
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
            self.cb_clear_dls.setChecked(val)
            self.cb_reuse_data.setChecked(val)
            self.cb_ignore_old.setChecked(val)
            self.sb_day_diff.setValue(3)

    def load_settings_to_ui(self):
        if settings.check_settings_exists():
            self.cb_eshipper.setChecked(self.settings['scrape']['eshipper'])
            self.cb_ems.setChecked(self.settings['scrape']['ems'])
            self.cb_freightcom.setChecked(self.settings['scrape']['freightcom'])

            self.cb_canadapost.setChecked(self.settings['track']['canada post'])
            self.cb_purolator.setChecked(self.settings['track']['purolator'])
            self.cb_ups.setChecked(self.settings['track']['ups'])
            self.cb_canpar.setChecked(self.settings['track']['canpar'])
            self.cb_fedex.setChecked(self.settings['track']['fedex'])

            self.cb_clear_dls.setChecked(self.settings['clear_downloads'])
            self.cb_reuse_data.setChecked(self.settings['reuse_data'])
            self.cb_ignore_old.setChecked(self.settings['ignore_old'])
            self.sb_day_diff.setValue(self.settings['day_diff'])
        else:
            self.set_normal_settings_to(False, all=True)

    def save_settings_to_file(self):
        self.settings['scrape']['eshipper'] = self.cb_eshipper.isChecked()
        self.settings['scrape']['ems'] = self.cb_ems.isChecked()
        self.settings['scrape']['freightcom'] = self.cb_freightcom.isChecked()  

        self.settings['track']['canada post'] = self.cb_canadapost.isChecked()
        self.settings['track']['purolator'] = self.cb_purolator.isChecked()   
        self.settings['track']['ups'] = self.cb_ups.isChecked() 
        self.settings['track']['canpar'] = self.cb_canpar.isChecked()
        self.settings['track']['fedex'] = self.cb_fedex.isChecked()

        self.settings['clear_downloads'] = self.cb_clear_dls.isChecked()
        self.settings['reuse_data'] = self.cb_reuse_data.isChecked()
        self.settings['ignore_old'] = self.cb_ignore_old.isChecked()
        self.settings['day_diff'] = self.sb_day_diff.value()

        if settings.check_settings_exists():
            settings.write_to_settings(self.settings)
        else:
            settings.settings = self.settings
            settings.create_settings_file()

    def reset_btn_clicked(self):
        self.set_normal_settings_to(False)

    def close_self(self):
        self.close()
        



