from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpinBox, QToolButton, QVBoxLayout, QWidget,
)

from src.core.settings import Settings
from src.core.log import getLogger
from src.ui.theme import ToggleSwitch


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
    SOURCES  = ["Eshipper", "EMS", "Freightcom"]
    CARRIERS = ["Canada Post", "Purolator", "UPS", "Canpar", "Fedex"]

    def __init__(self):
        super().__init__()
        self.wdgts = []

        overall_layout = QVBoxLayout()
        overall_layout.setContentsMargins(0, 0, 0, 0)
        overall_layout.setSpacing(14)

        overall_layout.addWidget(self._gen_chip_card("Sources", "scrape", self.SOURCES))
        overall_layout.addWidget(self._gen_chip_card("Carriers", "track", self.CARRIERS))
        overall_layout.addWidget(self._gen_options_card())
        overall_layout.addStretch()

        self.setLayout(overall_layout)
        self.load_settings_to_ui()

    # ────────────────────────────< layout helpers >────────────────────────────
    def _gen_card(self, title:str, group_name:str = None):
        card = QFrame()
        card.setObjectName("card")
        lyt = QVBoxLayout(card)
        lyt.setContentsMargins(16, 12, 16, 16)
        lyt.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(0)
        title_lbl = QLabel(title.upper())
        title_lbl.setObjectName("cardTitle")
        header.addWidget(title_lbl)
        header.addStretch()

        if group_name:
            for text, val in [("All", True), ("None", False)]:
                btn = QPushButton(text)
                btn.setObjectName("link")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda _=False, v=val: self._set_group_value(group_name, v))
                header.addWidget(btn)

        lyt.addLayout(header)
        return card, lyt

    def _gen_chip_card(self, title:str, group_name:str, names:list) -> QWidget:
        card, lyt = self._gen_card(title, group_name)

        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)
        for i, name in enumerate(names):
            chip = QPushButton(name)
            chip.setObjectName("chip")
            chip.setCheckable(True)
            chip.setCursor(Qt.CursorShape.PointingHandCursor)
            chip.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            # checkable buttons share isChecked/setChecked with checkboxes
            self.wdgts.append(AppSetting(f"{group_name}.{name.lower()}", chip, "checkbox"))
            grid.addWidget(chip, i // 3, i % 3)

        lyt.addLayout(grid)
        return card

    def _gen_options_card(self) -> QWidget:
        card, lyt = self._gen_card("Options")

        for setting_id, text in [
            ("extras.ignore_already_tracked", "Ignore already tracked shipments"),
            ("extras.reuse_data",             "Re-use data from previous run"),
            ("extras.debug_mode",             "Debug mode"),
        ]:
            s = AppSetting(setting_id, ToggleSwitch(text), "checkbox")
            self.wdgts.append(s)
            lyt.addWidget(s.widget)

        form = QFormLayout()
        form.setContentsMargins(0, 6, 0, 0)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        day_diff = self._gen_spinbox("extras.day_diff", 1, 999, " days")
        day_diff.widget.setToolTip("How many days back to look for shipments")
        form.addRow(self._field_label("Day difference"), day_diff.widget)

        wait = self._gen_spinbox("extras.default_wait_time", 5, 999, " sec")
        wait.widget.setToolTip("Default time to wait for page elements")
        form.addRow(self._field_label("Wait time"), wait.widget)
        lyt.addLayout(form)

        # ── advanced (collapsible) ────────────────────────────────────────
        toggle = QToolButton()
        toggle.setObjectName("disclosure")
        toggle.setText("Advanced")
        toggle.setCheckable(True)
        toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toggle.setArrowType(Qt.ArrowType.RightArrow)
        lyt.addWidget(toggle)

        advanced = QWidget()
        adv_form = QFormLayout(advanced)
        adv_form.setContentsMargins(0, 0, 0, 0)
        adv_form.setHorizontalSpacing(12)
        adv_form.setVerticalSpacing(8)
        adv_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        chrome_dir = AppSetting("extras.chrome_dir", QLineEdit(), "lineedit")
        chrome_dir.widget.setPlaceholderText("Default install")
        self.wdgts.append(chrome_dir)
        adv_form.addRow(self._field_label("Chrome path"), chrome_dir.widget)

        chrome_version = AppSetting("extras.chrome_version", QLineEdit(), "lineedit")
        chrome_version.widget.setPlaceholderText("Auto-detect")
        self.wdgts.append(chrome_version)
        adv_form.addRow(self._field_label("Chrome version"), chrome_version.widget)

        advanced.setVisible(False)
        lyt.addWidget(advanced)

        def on_toggle(checked):
            toggle.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow)
            advanced.setVisible(checked)
        toggle.toggled.connect(on_toggle)

        return card

    def _gen_spinbox(self, setting_id:str, low:int, high:int, suffix:str) -> AppSetting:
        s = AppSetting(setting_id, QSpinBox(), "spinbox")
        s.set_spinbox_range(low, high)
        s.widget.setSuffix(suffix)
        s.widget.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        s.widget.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.wdgts.append(s)
        return s

    @staticmethod
    def _field_label(text:str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("fieldLabel")
        return lbl

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
        



