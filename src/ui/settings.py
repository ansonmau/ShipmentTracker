from PySide6.QtWidgets import (
    QLineEdit, QSpinBox, QWidget,
    QVBoxLayout, QPushButton, QLabel,
    QCheckBox, QGroupBox, QHBoxLayout
)

from src.core.settings import Settings
from src.core.log import getLogger


# ╭────────────────────────────────────────────────╮
# │                Settings Wrapper                │
# ╰────────────────────────────────────────────────╯
class AppSetting:
    logger = getLogger("settings.AppSettings") 
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
        if (not(self._widget) or not(self._widget_type)):
            return None

        get_fnc = self._get_widget_get_function()
        if (get_fnc):
            return get_fnc()
        else:
            self.logger.debug(f"Cannot get value of unknown widget type: {self._widget_type}")

        return None

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
        if (not(self._widget) or not(self._widget_type)):
            return 

        set_fnc = self._get_widget_set_function()
        if (set_fnc):
            set_fnc(value)
        else:
            self.logger.debug("Cannot set value for unknown widget type: {}".format(self._widget_type))

    def set_spinbox_range(self, low, high):
        if (not(self._widget) or not(self._widget_type == "spinbox")):
            return 

        self._widget.setMinimum(low)
        self._widget.setMaximum(high)

    def _get_widget_set_function(self):
        if (not(self._widget) or not(self._widget_type)):
            raise RuntimeError("Tried to get widget set function without assigning a widget first")

        w = self._widget
        wt = self._widget_type

        if wt == "checkbox":
            return w.setChecked
        if wt == "spinbox":
            return w.setValue
        if wt == "lineedit":
            return w.setText

        self.logger.debug(f"Cannot find value setter function for undefined widget type: {wt}")
        return None

    def _get_widget_get_function(self):
        if (not(self._widget) or not(self._widget_type)):
            raise RuntimeError("Tried to get widget get function without assigning a widget first")

        w = self._widget
        wt = self._widget_type

        if wt == "checkbox":
            return w.isChecked
        if wt == "spinbox":
            return w.value
        if wt == "lineedit":
            return w.text

        self.logger.debug(f"Cannot find value getter function for undefined widget type: {wt}")
        return None

# ╭────────────────────────────────────────────────╮
# │              Main Settings Widget              │
# ╰────────────────────────────────────────────────╯

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
        self.wdgts.append(AppSetting("label.waittime", QLabel("Wait time (seconds):"), "label"))
        self.wdgts.append(AppSetting("extras.default_wait_time", QSpinBox(), "spinbox"))
        self.wdgts[-1].set_spinbox_range(5,999)
        self.wdgts.append(AppSetting("label.chrome_dir", QLabel("Custom chrome location: "), "label"))
        self.wdgts.append(AppSetting("extras.chrome_dir", QLineEdit(), "lineedit"))
        self.wdgts.append(AppSetting("label.chrome_version", QLabel("Custom chrome version: "), "label"))
        self.wdgts.append(AppSetting("extras.chrome_version", QLineEdit(), "lineedit"))
        self.wdgts.append(AppSetting("extras.debug_mode", QCheckBox("Debug mode"), "checkbox"))

        for i in range(extras_start_index, len(self.wdgts)):
            extras_layout.addWidget(self.wdgts[i].widget)

        extras_container.setLayout(extras_layout)

        overall_layout.addWidget(scrape_container)
        overall_layout.addWidget(self._gen_group_actions_container("scrape"))
        overall_layout.addWidget(carrier_container)
        overall_layout.addWidget(self._gen_group_actions_container("track"))
        overall_layout.addWidget(extras_container)

        self.setLayout(overall_layout)
        self.load_settings_to_ui()

    def _gen_group_actions_container(self, group_name:str)->QWidget:
        small_button_stylesheet = """
                              QPushButton {
                                  padding: 4px 10px;
                                  font-size: 11px;
                                  margin: 0px;
                                  }
                              """ 
        btn_all =   QPushButton("O")
        btn_none =  QPushButton("/")

        btn_all.setStyleSheet(small_button_stylesheet)
        btn_all.clicked.connect(lambda: self.all_btn_func(group_name))
        btn_none.setStyleSheet(small_button_stylesheet)
        btn_none.clicked.connect(lambda: self.none_btn_func(group_name))

        container = QWidget()
        lyt = QHBoxLayout()
        lyt.addWidget(btn_all)
        lyt.addWidget(btn_none)
        lyt.addStretch()
        container.setLayout(lyt)

        return container


    def all_btn_func(self, group_name:str):
        self._set_group_value(group_name, True)

    def none_btn_func(self, group_name:str):
        self._set_group_value(group_name, False)

    def _set_group_value(self, group_name:str, val):
        for w in self.wdgts:
            w_group = (w.id.split('.'))[0]
            if (w_group.lower() == group_name.lower()):
                w.value = val

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
                    val = settings.get(key[0])
                    if val:
                        val = val.get(key[1])
                else:
                    val = settings.get(key[0])

                if not val or isinstance(val, dict):
                    # may be dict if it gets stuck on the way to a value
                    continue

                s.value = val
        else:
            self._set_group_value(".", False)

    def save_settings_to_file(self):
        settings = Settings.get_settings()

        for s in self.wdgts:
            # ── ignore labels ─────────────────────────────────────────────────────
            if s.widget_type == "label":
                continue 

            # ── value fixing ──────────────────────────────────────────────────────
            if (isinstance(s.value, str)):
                # remove leading/trailing quotes and spaces
                s.value = s.value.strip().strip('"').strip()

            # ── set values ────────────────────────────────────────────────────────
            key = s.id.split('.')
            if (len(key) == 2):
                settings[key[0]][key[1]] = s.value
            else:
                settings[key[0]] = s.value

        Settings.write_to_file()

    def close_self(self):
        self.close()
        



