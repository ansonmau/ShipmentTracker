from PySide6.QtWidgets import (
    QSpinBox, QWidget,
    QVBoxLayout, QPushButton, QLabel,
    QCheckBox, QGroupBox, QHBoxLayout
)

from src.core.settings import Settings
class AppSetting:
    def __init__(self, id = None, widget = None, widget_type = None, corresponding_setting = None):
        self._id = id 
        self._widget_type = widget_type
        self._widget = widget
        self._corresponding_setting = corresponding_setting
        self._value = None

    @property
    def id(self):
        return self._id

    @property
    def widget_type(self):
        return self._widget_type

    @property
    def widget(self):
        return self._widget

    @property
    def corresponding_setting(self):
        return self._corresponding_setting

    @property
    def value(self):
        val = None
        if (not(self._widget)):
            return val

        if self._widget_type == "checkbox":
            val = self._widget.isChecked()
        elif self._widget_type == "spinbox":
            val = self._widget.value()

        return val

    @id.setter 
    def id(self, value):
        self._id = value

    @widget_type.setter 
    def widget_type(self, value):
        self._widget_type = value

    @widget.setter 
    def widget(self, value):
        self._widget = value

    @corresponding_setting.setter 
    def corresponding_setting(self, value):
        self._corresponding_setting = value

    @value.setter
    def value(self, value):
        if (not(self._widget)):
            return 

        if self._widget_type == "checkbox":
            self._widget.setChecked(value)
        elif self._widget_type == "spinbox":
            self._widget.setValue(value)

    def set_spinbox_range(self, low, high):
        if (not(self._widget) or not(self._widget_type == "spinbox")):
            return 

        self._widget.setMinimum(low)
        self._widget.setMaximum(high)


class SettingsWidget(QWidget):
    wdgts = []

    def __init__(self):
        super().__init__()
        
        overall_layout = QVBoxLayout()

        scrape_container = QGroupBox("Sources")
        scrape_layout = QVBoxLayout()
        
        for name in ["Eshipper", "EMS", "Freightcom"]:
            c = AppSetting()
            c.id = ".".join(["scrape", name.lower()])
            c.widget = QCheckBox(name)
            c.widget_type = "checkbox"
            self.wdgts.append(c)
            scrape_layout.addWidget(c.widget)

        scrape_container.setLayout(scrape_layout)

        carrier_container = QGroupBox("Carriers")
        carrier_layout = QVBoxLayout()

        for name in ["Canada Post", "Purolator", "UPS", "Canpar", "Fedex"]:
            c = AppSetting()
            c.id = ".".join(["track", name.lower()])
            c.widget = QCheckBox(name)
            c.widget_type = "checkbox"
            self.wdgts.append(c)
            carrier_layout.addWidget(c.widget)

        carrier_container.setLayout(carrier_layout)

        extras_container = QGroupBox("Extras")
        extras_layout = QVBoxLayout()

        extras_start_index = len(self.wdgts)
        self.wdgts.append(AppSetting("extras.ignore_already_tracked", QCheckBox("Ignore already tracked shipments"), "checkbox"))
        self.wdgts.append(AppSetting("extras.reuse_data", QCheckBox("Re-use data from previous run"), "checkbox"))
        self.wdgts.append(AppSetting("label.day_diff", QLabel("Day difference:"), "label"))
        self.wdgts.append(AppSetting("extras.day_diff", QSpinBox(), "spinbox"))
        self.wdgts[-1].set_spinbox_range(1,999)
        self.wdgts.append(AppSetting("label.waittime", QLabel("Wait time:"), "label"))
        self.wdgts.append(AppSetting("extras.default_wait_time", QSpinBox(), "spinbox"))
        self.wdgts[-1].set_spinbox_range(5,999)
        self.wdgts.append(AppSetting("extras.debug_mode", QCheckBox("Debug mode"), "checkbox"))

        for i in range(extras_start_index, len(self.wdgts)):
            extras_layout.addWidget(self.wdgts[i].widget)

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

    def set_normal_settings_to(self, val: bool):
        for s in self.wdgts:
            s.value = val

    def load_settings_to_ui(self):
        if Settings.file_exists():
            Settings.load_from_file()
            settings = Settings.get_settings()

            for s in self.wdgts:
                if s.widget_type == "label":
                    continue

                val = None
                key = s.id.split('.')
                if (len(key) == 2): 
                    val = settings[key[0]][key[1]]
                else:
                    val = settings[key[0]]
                s.value = val
        else:
            self.set_normal_settings_to(False)

    def save_settings_to_file(self):
        settings = Settings.get_settings()

        for s in self.wdgts:
            if s.widget_type == "label":
                continue 

            key = s.id.split('.')
            if (len(key) == 2):
                settings[key[0]][key[1]] = s.value
            else:
                settings[key[0]] = s.value

        Settings.write_to_file()

    def reset_btn_clicked(self):
        self.set_normal_settings_to(False)

    def close_self(self):
        self.close()
        



