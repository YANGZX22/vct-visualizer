import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QSplitter, QDialog, QDateEdit, QTimeEdit, 
                             QComboBox, QFormLayout, QDialogButtonBox, QListWidget, QStackedWidget,
                             QCalendarWidget, QSpinBox, QListWidgetItem, QGridLayout, QFrame,
                             QScrollArea, QSizePolicy, QGraphicsDropShadowEffect, QMenu)
from PyQt6.QtCore import Qt, QDate, QTime, QSize, pyqtSignal, QMimeData, QPoint
from PyQt6.QtGui import (QColor, QFont, QBrush, QFontDatabase, QIcon, QPixmap, QPainter, 
                         QPen, QPainterPath, QDrag, QShortcut, QKeySequence, QAction, QCursor)

# Asset paths
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
FONT_PATH = os.path.join(ASSETS_DIR, "font", "FoundryGridnikW03-ExtraBold.ttf")
CN_FONT_PATH = os.path.join(ASSETS_DIR, "font", "HarmonyOS_Sans_SC_Bold.ttf")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")

HEADERS = ["日期", "时间", "赛事", "对阵信息", "备注"]

# Columns for the new match display format
HEADERS_EXTENDED = ["日期", "时间", "赛事", "Team A", "vs", "Team B", "备注"]

# Teams by region - names match asset filenames (without .png)
TEAMS_BY_REGION = {
    "pacific": ["dfm", "drx", "fs", "ge", "geng", "nongshim", "prx", "rrq", "t1", "ts", "vl", "zeta"], 
    "emea": ["bbl", "fnc", "fut", "gx", "kc", "m8", "navi", "pcf", "th", "tl", "ulf", "vit"], 
    "amer": ["100t", "cloud9", "eg", "envy", "furia", "g2", "kru", "lev", "loud", "mibr", "nrg", "sen"],
    "cn": ["ag", "blg", "drg", "edg", "fpx", "jdg", "nova", "te", "tec", "tyl", "wol", "xlg"],
    "others": ["5fw", "aq", "待定"]
}

# Tournaments - names match vct folder filenames (without .png)
TOURNAMENTS = ["pacific", "emea", "americas", "cn", "masters", "champions", "others"]

def get_team_icon_path(team_name):
    """Get the icon path for a team"""
    team_lower = team_name.lower()
    for region, teams in TEAMS_BY_REGION.items():
        if team_lower in teams:
            return os.path.join(IMAGES_DIR, region, f"{team_lower}.png")
    return None

def get_tournament_icon_path(tournament_name):
    """Get the icon path for a tournament"""
    name = tournament_name.lower()
    # Handle mapping for amer -> americas
    if name == "amer":
        name = "americas"
    # Check for png first, then jpg
    png_path = os.path.join(IMAGES_DIR, "vct", f"{name}.png")
    if os.path.exists(png_path):
        return png_path
    jpg_path = os.path.join(IMAGES_DIR, "vct", f"{name}.jpg")
    if os.path.exists(jpg_path):
        return jpg_path
    return png_path  # Return png path as default

def get_card_background_path(tournament_name):
    """Get the card background image path for a tournament"""
    name = tournament_name.lower()
    # Map tournament names to card filenames
    if name == "amer":
        name = "americas"
    return os.path.join(IMAGES_DIR, "card", f"{name}_card.png")

# --- Picker Dialogs ---

class TwoDigitSpinBox(QSpinBox):
    """QSpinBox that always displays two digits with leading zero"""
    def textFromValue(self, value: int) -> str:
        return f"{value:02d}"


class DatePickerDialog(QDialog):
    def __init__(self, parent=None, current_value=""):
        super().__init__(parent)
        self.setWindowTitle("选择日期")
        self.setModal(True)
        layout = QVBoxLayout(self)
        
        # Use QCalendarWidget for full calendar view
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        
        # Parse current value (supports Y.M.D or M.D format)
        try:
            parts = current_value.split('.')
            if len(parts) == 3:
                y, m, d = map(int, parts)
            else:
                m, d = map(int, parts)
                y = QDate.currentDate().year()
            self.calendar.setSelectedDate(QDate(y, m, d))
        except:
            self.calendar.setSelectedDate(QDate.currentDate())
        
        layout.addWidget(self.calendar)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_value(self):
        date = self.calendar.selectedDate()
        return f"{date.year()}.{date.month()}.{date.day()}"

class TimePickerDialog(QDialog):
    def __init__(self, parent=None, current_value=""):
        super().__init__(parent)
        self.setWindowTitle("选择时间")
        self.setModal(True)
        self.resize(300, 200)
        
        layout = QVBoxLayout(self)
        
        # Create horizontal layout for hour and minute spinboxes
        time_layout = QHBoxLayout()
        
        # Hour spinbox (0-23, wrapping)
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setWrapping(True)
        self.hour_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hour_spin.setMinimumSize(100, 80)
        self.hour_spin.setStyleSheet("QSpinBox { font-size: 36px; padding: 10px; } QSpinBox::up-button, QSpinBox::down-button { width: 30px; }")
        
        # Separator label
        colon_label = QLabel(":")
        colon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        colon_label.setStyleSheet("font-size: 36px; font-weight: bold;")
        
        # Minute spinbox (0-59, wrapping)
        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setWrapping(True)
        self.minute_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.minute_spin.setMinimumSize(100, 80)
        self.minute_spin.setStyleSheet("QSpinBox { font-size: 36px; padding: 10px; } QSpinBox::up-button, QSpinBox::down-button { width: 30px; }")
        
        time_layout.addWidget(self.hour_spin)
        time_layout.addWidget(colon_label)
        time_layout.addWidget(self.minute_spin)
        
        layout.addLayout(time_layout)
        
        # Parse current value
        try:
            h, m = map(int, current_value.split(':'))
            self.hour_spin.setValue(h)
            self.minute_spin.setValue(m)
        except:
            now = QTime.currentTime()
            self.hour_spin.setValue(now.hour())
            self.minute_spin.setValue(now.minute())
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_value(self):
        return f"{self.hour_spin.value():02d}:{self.minute_spin.value():02d}"

class TournamentPickerDialog(QDialog):
    def __init__(self, parent=None, current_value=""):
        super().__init__(parent)
        self.setWindowTitle("选择赛事")
        self.setModal(True)
        self.resize(300, 350)
        layout = QVBoxLayout(self)
        
        # Use list widget with icons
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(48, 48))
        self.list_widget.setSpacing(5)
        
        for tournament in TOURNAMENTS:
            icon_path = get_tournament_icon_path(tournament)
            item = QListWidgetItem(tournament.upper())
            if icon_path and os.path.exists(icon_path):
                item.setIcon(QIcon(icon_path))
            self.list_widget.addItem(item)
        
        # Select current value
        current_lower = current_value.lower()
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).text().lower() == current_lower:
                self.list_widget.setCurrentRow(i)
                break
        
        layout.addWidget(self.list_widget)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_value(self):
        item = self.list_widget.currentItem()
        return item.text().lower() if item else ""

class TeamPickerWidget(QWidget):
    """Two-level team picker: Region ComboBox + Team ComboBox"""
    def __init__(self, label="", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        if label:
            title_label = QLabel(label)
            title_label.setObjectName("fieldLabel")
            layout.addWidget(title_label)
        
        # Region ComboBox with icons
        self.region_combo = QComboBox()
        self.region_combo.setIconSize(QSize(24, 24))
        self.region_combo.setMinimumHeight(40)
        self.region_combo.setMinimumWidth(140)
        self.region_combo.view().setMinimumWidth(160)
        for region in TEAMS_BY_REGION.keys():
            icon_path = get_tournament_icon_path(region)
            if icon_path and os.path.exists(icon_path):
                self.region_combo.addItem(QIcon(icon_path), region.upper(), region)
            else:
                self.region_combo.addItem(region.upper(), region)
        self.region_combo.currentIndexChanged.connect(self.update_teams)
        layout.addWidget(self.region_combo)
        
        # Team ComboBox with icons
        self.team_combo = QComboBox()
        self.team_combo.setIconSize(QSize(24, 24))
        self.team_combo.setMinimumHeight(40)
        self.team_combo.setMinimumWidth(140)
        self.team_combo.view().setMinimumWidth(160)
        layout.addWidget(self.team_combo)
        
        # Initialize teams for first region
        if self.region_combo.count() > 0:
            self.update_teams(0)
    
    def update_teams(self, index):
        self.team_combo.clear()
        region = self.region_combo.currentData()
        if region and region in TEAMS_BY_REGION:
            for team in TEAMS_BY_REGION[region]:
                icon_path = get_team_icon_path(team)
                if icon_path and os.path.exists(icon_path):
                    self.team_combo.addItem(QIcon(icon_path), team.upper(), team)
                else:
                    self.team_combo.addItem(team.upper(), team)
    
    def set_team(self, team_name):
        team_lower = team_name.lower()
        # Find region for this team
        for region, teams in TEAMS_BY_REGION.items():
            if team_lower in teams:
                # Select region
                for i in range(self.region_combo.count()):
                    if self.region_combo.itemData(i) == region:
                        self.region_combo.setCurrentIndex(i)
                        break
                # Select team
                for i in range(self.team_combo.count()):
                    if self.team_combo.itemData(i) == team_lower:
                        self.team_combo.setCurrentIndex(i)
                        break
                return
    
    def get_team(self):
        return self.team_combo.currentData() or ""
    
    def lock_region(self, region):
        """Lock the region selector to a specific region"""
        region_lower = region.lower()
        for i in range(self.region_combo.count()):
            if self.region_combo.itemData(i) == region_lower:
                self.region_combo.setCurrentIndex(i)
                break
        self.region_combo.setEnabled(False)
    
    def unlock_region(self):
        """Unlock the region selector"""
        self.region_combo.setEnabled(True)

class MatchPickerDialog(QDialog):
    """Dialog to pick Team A vs Team B"""
    def __init__(self, parent=None, current_value=""):
        super().__init__(parent)
        self.setWindowTitle("选择对阵")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Parse current value "A vs B"
        team_a, team_b = "", ""
        if " vs " in current_value:
            team_a, team_b = current_value.split(" vs ", 1)
        
        # Team A picker
        self.team_a_picker = TeamPickerWidget("Team A (主队):")
        if team_a:
            self.team_a_picker.set_team(team_a)
        layout.addWidget(self.team_a_picker)
        
        layout.addWidget(QLabel("vs"))
        
        # Team B picker
        self.team_b_picker = TeamPickerWidget("Team B (客队):")
        if team_b:
            self.team_b_picker.set_team(team_b)
        layout.addWidget(self.team_b_picker)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_value(self):
        team_a = self.team_a_picker.get_team()
        team_b = self.team_b_picker.get_team()
        if team_a and team_b:
            return f"{team_a} vs {team_b}"
        return team_a or team_b or ""


class MatchEditDialog(QDialog):
    """Comprehensive dialog to edit all match fields"""
    def __init__(self, parent=None, match_data=None):
        super().__init__(parent)
        self.setWindowTitle("编辑比赛信息")
        self.setModal(True)
        self.resize(760, 720)
        
        if match_data is None:
            match_data = ["", "", "", "", "", "BO3"]
        
        date_val = match_data[0] if len(match_data) > 0 else ""
        time_val = match_data[1] if len(match_data) > 1 else ""
        tournament_val = match_data[2] if len(match_data) > 2 else ""
        match_val = match_data[3] if len(match_data) > 3 else ""
        remarks_val = match_data[4] if len(match_data) > 4 else ""
        bo_val = match_data[5] if len(match_data) > 5 else "BO3"
        
        self.setObjectName("matchEditDialog")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # Title
        title = QLabel("编辑比赛信息")
        title.setObjectName("dialogTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(title)

        def make_section(title_text: str) -> tuple[QFrame, QVBoxLayout]:
            frame = QFrame()
            frame.setObjectName("sectionCard")
            frame_layout = QVBoxLayout(frame)
            frame_layout.setContentsMargins(14, 12, 14, 12)
            frame_layout.setSpacing(10)

            if title_text:
                section_title = QLabel(title_text)
                section_title.setObjectName("sectionTitle")
                frame_layout.addWidget(section_title)

            shadow = QGraphicsDropShadowEffect(frame)
            shadow.setBlurRadius(18)
            shadow.setOffset(0, 4)
            shadow.setColor(QColor(0, 0, 0, 38))
            frame.setGraphicsEffect(shadow)
            return frame, frame_layout
        
        # Date & Time row
        datetime_section, datetime_section_layout = make_section("日期与时间")
        datetime_layout = QHBoxLayout()
        datetime_layout.setSpacing(16)
        
        # Date
        date_group = QVBoxLayout()
        date_group.setSpacing(8)
        date_label = QLabel("日期")
        date_label.setObjectName("fieldLabel")
        date_group.addWidget(date_label)
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setFixedHeight(230)
        try:
            parts = date_val.split('.')
            if len(parts) == 3:
                y, m, d = map(int, parts)
            else:
                m, d = map(int, parts)
                y = QDate.currentDate().year()
            self.calendar.setSelectedDate(QDate(y, m, d))
        except:
            self.calendar.setSelectedDate(QDate.currentDate())
        date_group.addWidget(self.calendar)
        datetime_layout.addLayout(date_group)
        
        # Time
        time_group = QVBoxLayout()
        time_group.setSpacing(8)
        time_label = QLabel("时间")
        time_label.setObjectName("fieldLabel")
        time_group.addWidget(time_label)
        time_inner = QHBoxLayout()
        time_inner.setSpacing(8)
        self.hour_spin = TwoDigitSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setWrapping(True)
        self.hour_spin.setMinimumSize(130, 64)
        self.hour_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hour_spin.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        
        colon = QLabel(":")
        colon.setObjectName("timeColon")
        
        self.minute_spin = TwoDigitSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setWrapping(True)
        self.minute_spin.setMinimumSize(130, 64)
        self.minute_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.minute_spin.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        
        try:
            h, m = map(int, time_val.split(':'))
            self.hour_spin.setValue(h)
            self.minute_spin.setValue(m)
        except:
            self.hour_spin.setValue(12)
            self.minute_spin.setValue(0)
        
        time_inner.addWidget(self.hour_spin)
        time_inner.addWidget(colon)
        time_inner.addWidget(self.minute_spin)
        time_inner.addStretch()
        time_group.addLayout(time_inner)
        
        # BO selection (below time)
        bo_label = QLabel("赛制")
        bo_label.setObjectName("fieldLabel")
        time_group.addWidget(bo_label)
        bo_inner = QHBoxLayout()
        bo_inner.setSpacing(8)
        self.bo_buttons = []
        for bo in ["BO1", "BO3", "BO5"]:
            btn = QPushButton(bo)
            btn.setCheckable(True)
            btn.setMinimumSize(60, 40)
            btn.setObjectName("boButton")
            btn.clicked.connect(lambda checked, b=bo: self.select_bo(b))
            if bo == bo_val:
                btn.setChecked(True)
            self.bo_buttons.append(btn)
            bo_inner.addWidget(btn)
        bo_inner.addStretch()
        time_group.addLayout(bo_inner)
        time_group.addStretch()
        datetime_layout.addLayout(time_group)

        datetime_section_layout.addLayout(datetime_layout)
        layout.addWidget(datetime_section)
        
        # Tournament
        tournament_section, tournament_section_layout = make_section("赛事")
        self.tournament_list = QListWidget()
        self.tournament_list.setIconSize(QSize(32, 32))
        self.tournament_list.setFixedHeight(100)
        self.tournament_list.setFlow(QListWidget.Flow.LeftToRight)
        self.tournament_list.setWrapping(False)
        self.tournament_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tournament_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tournament_list.setSpacing(8)
        for t in TOURNAMENTS:
            icon_path = get_tournament_icon_path(t)
            item = QListWidgetItem(t.upper())
            if icon_path and os.path.exists(icon_path):
                item.setIcon(QIcon(icon_path))
            self.tournament_list.addItem(item)
        # Select current
        for i in range(self.tournament_list.count()):
            if self.tournament_list.item(i).text().lower() == tournament_val.lower():
                self.tournament_list.setCurrentRow(i)
                break
        tournament_section_layout.addWidget(self.tournament_list)
        layout.addWidget(tournament_section)
        
        # Match (Team A vs Team B)
        match_section, match_section_layout = make_section("对阵")
        team_a, team_b = "", ""
        if " vs " in match_val:
            team_a, team_b = match_val.split(" vs ", 1)
        
        match_layout = QHBoxLayout()
        match_layout.setSpacing(12)
        self.team_a_picker = TeamPickerWidget("Team A:")
        if team_a:
            self.team_a_picker.set_team(team_a)
        match_layout.addWidget(self.team_a_picker)
        
        vs_label = QLabel("vs")
        vs_label.setObjectName("vsLabel")
        vs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        match_layout.addWidget(vs_label)
        
        self.team_b_picker = TeamPickerWidget("Team B:")
        if team_b:
            self.team_b_picker.set_team(team_b)
        match_layout.addWidget(self.team_b_picker)
        match_section_layout.addLayout(match_layout)
        layout.addWidget(match_section)
        
        # Connect tournament selection to update team pickers
        self.tournament_list.itemSelectionChanged.connect(self.on_tournament_changed)
        # Initialize region lock based on current tournament
        self.on_tournament_changed()
        
        # Remarks
        remarks_section, remarks_section_layout = make_section("备注")
        from PyQt6.QtWidgets import QLineEdit
        self.remarks_edit = QLineEdit()
        self.remarks_edit.setText(remarks_val)
        self.remarks_edit.setPlaceholderText("输入备注信息...")
        remarks_section_layout.addWidget(self.remarks_edit)
        layout.addWidget(remarks_section)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        if ok_btn is not None:
            ok_btn.setText("保存")
            ok_btn.setObjectName("primaryButton")
            ok_btn.setDefault(True)
        if cancel_btn is not None:
            cancel_btn.setText("取消")
            cancel_btn.setObjectName("secondaryButton")
        layout.addWidget(buttons)

        # Dialog-wide styling (only affects this dialog via objectName)
        self.setStyleSheet("""
        QDialog#matchEditDialog {
            background: #f5f5f5;
        }

        QLabel#dialogTitle {
            font-size: 20px;
            font-weight: 800;
            color: #111827;
            padding: 2px 2px 6px 2px;
        }

        QFrame#sectionCard {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
        }

        QLabel#sectionTitle {
            font-size: 13px;
            font-weight: 800;
            color: #374151;
        }

        QLabel#fieldLabel {
            font-size: 12px;
            font-weight: 700;
            color: #374151;
        }

        QLabel#timeColon {
            font-size: 22px;
            font-weight: 800;
            color: #111827;
            padding: 0px 4px;
        }

        QLabel#vsLabel {
            font-size: 16px;
            font-weight: 900;
            color: #6b7280;
            padding: 0 6px;
        }

        QSpinBox {
            background: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 10px;
            padding: 8px 34px 8px 12px;
            font-size: 22px;
            font-weight: 800;
            color: #111827;
        }

        QSpinBox::up-button, QSpinBox::down-button {
            subcontrol-origin: padding;
            width: 24px;
            background: #e5e7eb;
        }

        QSpinBox::up-button {
            subcontrol-position: top right;
            border-top-right-radius: 9px;
            border-bottom: 1px solid #d1d5db;
        }

        QSpinBox::down-button {
            subcontrol-position: bottom right;
            border-bottom-right-radius: 9px;
            border-top: 1px solid #d1d5db;
        }

        QSpinBox::up-button:hover {
            background: #d1d5db;
        }

        QSpinBox::down-button:hover {
            background: #d1d5db;
        }

        QSpinBox:focus {
            border: 1px solid #6b7280;
        }

        QLineEdit {
            background: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 10px;
            padding: 10px 12px;
            font-size: 14px;
            color: #111827;
        }

        QLineEdit:focus {
            border: 1px solid #6b7280;
        }

        QComboBox {
            background: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 10px;
            padding: 8px 12px;
            font-size: 14px;
            font-weight: 700;
            color: #111827;
        }

        QComboBox:hover {
            border: 1px solid #9ca3af;
        }

        QComboBox:focus {
            border: 1px solid #0ea5e9;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: center right;
            width: 28px;
            border: none;
        }

        QComboBox QAbstractItemView, QComboBox QListView {
            background: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 4px;
            selection-background-color: transparent;
            selection-color: #111827;
            outline: 0;
            color: #111827;
            font-size: 14px;
            font-weight: 700;
            min-width: 160px;
        }

        QComboBox QAbstractItemView::item, QComboBox QListView::item {
            padding: 8px 36px 8px 12px;
            min-height: 36px;
            color: #111827;
            background: transparent;
            border: 2px solid transparent;
            border-radius: 6px;
        }

        QComboBox QAbstractItemView::item:selected, QComboBox QListView::item:selected {
            background: transparent;
            color: #0c4a6e;
            border: 2px solid #0ea5e9;
        }

        QComboBox QAbstractItemView::item:hover, QComboBox QListView::item:hover {
            background: rgba(0, 0, 0, 0.04);
            color: #111827;
        }

        QListWidget {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 6px;
            outline: 0;
        }

        QListWidget::item {
            background: transparent;
            border: 2px solid transparent;
            border-radius: 10px;
            padding: 12px 14px;
            margin: 4px;
            color: #111827;
            font-weight: 800;
        }

        QListWidget::item:selected {
            background: #e0f2fe;
            border: 2px solid #0ea5e9;
            color: #0c4a6e;
        }

        QPushButton {
            min-height: 36px;
            border-radius: 10px;
            padding: 8px 14px;
            font-weight: 800;
        }

        QPushButton#primaryButton {
            background: #111827;
            color: #ffffff;
            border: 1px solid #111827;
        }

        QPushButton#primaryButton:hover {
            background: #0b1220;
        }

        QPushButton#secondaryButton {
            background: #ffffff;
            color: #111827;
            border: 1px solid #d1d5db;
        }

        QPushButton#secondaryButton:hover {
            background: #f3f4f6;
        }

        QCalendarWidget QWidget {
            alternate-background-color: #f3f4f6;
        }

        QWidget#qt_calendar_navigationbar {
            background: #111827;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }

        QCalendarWidget QToolButton {
            background: transparent;
            border: none;
            color: #ffffff;
            font-weight: 800;
            padding: 6px;
        }

        QCalendarWidget QToolButton:hover {
            background: rgba(255, 255, 255, 20);
            border-radius: 8px;
        }

        QCalendarWidget QAbstractItemView {
            background: #ffffff;
            color: #111827;
            selection-background-color: #2563eb;
            selection-color: #ffffff;
            outline: 0;
            font-weight: 700;
        }

        QCalendarWidget QAbstractItemView::item:selected {
            background: #2563eb;
            color: #ffffff;
            border-radius: 4px;
        }

        QCalendarWidget QAbstractItemView::item:hover {
            background: #dbeafe;
            border-radius: 4px;
        }

        QCalendarWidget QHeaderView::section {
            background: #f3f4f6;
            color: #111827;
            border: none;
            padding: 6px 0px;
            font-weight: 800;
        }

        QCalendarWidget QSpinBox {
            font-size: 14px;
            font-weight: 700;
            padding: 4px 8px;
        }

        QPushButton#boButton {
            background: #ffffff;
            border: 2px solid #d1d5db;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 700;
            color: #374151;
        }

        QPushButton#boButton:hover {
            border-color: #9ca3af;
            background: #f9fafb;
        }

        QPushButton#boButton:checked {
            background: #2563eb;
            border-color: #2563eb;
            color: #ffffff;
        }
        """)
    
    # Mapping from tournament to region (for regional tournaments)
    TOURNAMENT_TO_REGION = {
        "pacific": "pacific",
        "emea": "emea",
        "americas": "amer",
        "cn": "cn",
    }
    
    def select_bo(self, bo):
        """Select BO option and uncheck others"""
        for btn in self.bo_buttons:
            btn.setChecked(btn.text() == bo)
    
    def on_tournament_changed(self):
        """Update team picker region lock based on selected tournament"""
        tournament_item = self.tournament_list.currentItem()
        if not tournament_item:
            return
        
        tournament = tournament_item.text().lower()
        
        # Regional tournaments lock the region
        if tournament in self.TOURNAMENT_TO_REGION:
            region = self.TOURNAMENT_TO_REGION[tournament]
            self.team_a_picker.lock_region(region)
            self.team_b_picker.lock_region(region)
        else:
            # Masters and Champions allow free selection
            self.team_a_picker.unlock_region()
            self.team_b_picker.unlock_region()
    
    def get_data(self):
        date = self.calendar.selectedDate()
        date_str = f"{date.year()}.{date.month()}.{date.day()}"
        time_str = f"{self.hour_spin.value():02d}:{self.minute_spin.value():02d}"
        
        tournament_item = self.tournament_list.currentItem()
        tournament_str = tournament_item.text().lower() if tournament_item else ""
        
        team_a = self.team_a_picker.get_team()
        team_b = self.team_b_picker.get_team()
        match_str = f"{team_a} vs {team_b}" if team_a and team_b else ""
        
        remarks_str = self.remarks_edit.text()
        
        bo_str = "BO3"
        for btn in self.bo_buttons:
            if btn.isChecked():
                bo_str = btn.text()
                break
        
        return [date_str, time_str, tournament_str, match_str, remarks_str, bo_str]


# EditorWidget is no longer needed since we edit directly on cards


class MatchCard(QFrame):
    """A single match display card - clickable to edit"""
    card_double_clicked = pyqtSignal(int)  # Emits card index
    card_clicked = pyqtSignal(int)  # Emits card index for selection
    card_deleted = pyqtSignal(int)  # Emits card index for deletion
    card_copy = pyqtSignal(int)  # Emits card index for copy
    
    def __init__(self, match_data, card_index, cn_font_family, en_font_family, region_colors, parent=None):
        super().__init__(parent)
        self.cn_font_family = cn_font_family
        self.en_font_family = en_font_family
        self.card_index = card_index
        self.match_data = match_data
        self.selected = False
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Make card capture mouse events (don't let children intercept)
        self.setMouseTracking(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Set fixed height to prevent stretching
        self.setFixedHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Parse data: [date, time, tournament, match_info, remarks]
        date_val = match_data[0] if len(match_data) > 0 else ""
        time_val = match_data[1] if len(match_data) > 1 else ""
        tournament_val = match_data[2] if len(match_data) > 2 else ""
        match_val = match_data[3] if len(match_data) > 3 else ""
        remarks_val = match_data[4] if len(match_data) > 4 else ""
        
        # Parse match_info into team_a and team_b
        team_a, team_b = "", ""
        if " vs " in match_val:
            team_a, team_b = match_val.split(" vs ", 1)
        else:
            team_a = match_val
        
        # Get color based on tournament
        region_raw = tournament_val.strip().lower()
        row_color = region_colors.get(region_raw, QColor("#4BACC6"))
        color_name = row_color.name()
        
        # Store background image path for painting
        self.background_path = get_card_background_path(tournament_val)
        self.border_color = color_name
        
        # Set frame style
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            MatchCard {{
                background-color: transparent;
                border: none;
            }}
            QLabel {{
                background: transparent;
            }}
            QWidget {{
                background: transparent;
            }}
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)
        
        # Fonts - English for team names/tournament, Chinese for date/time/remarks
        en_font = QFont(en_font_family, 12, QFont.Weight.Bold)
        cn_font = QFont(cn_font_family, 12, QFont.Weight.Bold)
        
        # Top row: Date | Time | Tournament
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        # Date
        date_label = QLabel(date_val)
        date_label.setFont(en_font)
        date_label.setStyleSheet(f"color: {color_name}; background: transparent;")
        top_layout.addWidget(date_label)
        
        # Time
        time_label = QLabel(time_val)
        time_label.setFont(en_font)
        time_label.setStyleSheet(f"color: {color_name}; background: transparent;")
        top_layout.addWidget(time_label)
        
        # BO (after date and time)
        bo_val = match_data[5] if len(match_data) > 5 else ""
        if bo_val:
            bo_label = QLabel(bo_val)
            bo_label.setFont(en_font)
            bo_label.setStyleSheet(f"color: {color_name}; background: transparent;")
            top_layout.addWidget(bo_label)
        
        top_layout.addStretch()
        
        # Tournament with icon
        tournament_widget = QWidget()
        tournament_widget.setStyleSheet("background: transparent;")
        tournament_layout = QHBoxLayout(tournament_widget)
        tournament_layout.setContentsMargins(0, 0, 0, 0)
        tournament_layout.setSpacing(4)
        
        icon_path = get_tournament_icon_path(tournament_val)
        if icon_path and os.path.exists(icon_path):
            icon_label = QLabel()
            pixmap = QPixmap(icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            icon_label.setStyleSheet("background: transparent;")
            tournament_layout.addWidget(icon_label)
        
        tournament_label = QLabel(tournament_val.upper())
        tournament_label.setFont(en_font)
        tournament_label.setStyleSheet(f"color: {color_name}; background: transparent;")
        tournament_layout.addWidget(tournament_label)
        
        top_layout.addWidget(tournament_widget)
        layout.addLayout(top_layout)
        
        # Middle row: Team A vs Team B with icons - use fixed positions
        match_widget = QWidget()
        match_widget.setStyleSheet("background: transparent;")
        match_widget.setFixedHeight(40)
        match_layout = QHBoxLayout(match_widget)
        match_layout.setContentsMargins(0, 0, 0, 0)
        match_layout.setSpacing(0)
        
        # Team A (icon + name) - left aligned
        team_a_widget = QWidget()
        team_a_widget.setStyleSheet("background: transparent;")
        team_a_layout = QHBoxLayout(team_a_widget)
        team_a_layout.setContentsMargins(0, 0, 0, 0)
        team_a_layout.setSpacing(4)
        
        icon_path_a = get_team_icon_path(team_a)
        if icon_path_a and os.path.exists(icon_path_a):
            icon_label_a = QLabel()
            icon_label_a.setFixedSize(32, 32)
            pixmap_a = QPixmap(icon_path_a).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label_a.setPixmap(pixmap_a)
            icon_label_a.setStyleSheet("background: transparent;")
            team_a_layout.addWidget(icon_label_a)
        
        team_a_label = QLabel(team_a.upper())
        team_a_label.setFont(en_font)
        team_a_label.setStyleSheet(f"color: {color_name}; background: transparent;")
        team_a_layout.addWidget(team_a_label)
        team_a_layout.addStretch()
        
        match_layout.addWidget(team_a_widget, 2)
        
        # VS - centered
        vs_label = QLabel("vs")
        vs_label.setFont(en_font)
        vs_label.setStyleSheet(f"color: {color_name}; background: transparent;")
        vs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs_label.setFixedWidth(40)
        match_layout.addWidget(vs_label, 0)
        
        # Team B (name + icon) - right aligned
        team_b_widget = QWidget()
        team_b_widget.setStyleSheet("background: transparent;")
        team_b_layout = QHBoxLayout(team_b_widget)
        team_b_layout.setContentsMargins(0, 0, 0, 0)
        team_b_layout.setSpacing(4)
        
        team_b_layout.addStretch()
        
        team_b_label = QLabel(team_b.upper())
        team_b_label.setFont(en_font)
        team_b_label.setStyleSheet(f"color: {color_name}; background: transparent;")
        team_b_layout.addWidget(team_b_label)
        
        icon_path_b = get_team_icon_path(team_b)
        if icon_path_b and os.path.exists(icon_path_b):
            icon_label_b = QLabel()
            icon_label_b.setFixedSize(32, 32)
            pixmap_b = QPixmap(icon_path_b).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label_b.setPixmap(pixmap_b)
            icon_label_b.setStyleSheet("background: transparent;")
            team_b_layout.addWidget(icon_label_b)
        
        match_layout.addWidget(team_b_widget, 2)
        layout.addWidget(match_widget)
        
        # Bottom row: Remarks (if any)
        if remarks_val.strip():
            remarks_label = QLabel(remarks_val)
            remarks_label.setFont(QFont(cn_font_family, 10, QFont.Weight.Bold))
            remarks_label.setStyleSheet("color: #666666; background: transparent;")
            remarks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(remarks_label)
        
        # Make all child widgets transparent to mouse events so card receives clicks
        self._set_children_mouse_transparent(self)
    
    def _set_children_mouse_transparent(self, widget):
        """Recursively set all child widgets to be transparent to mouse events"""
        for child in widget.children():
            if hasattr(child, 'setAttribute'):
                child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
                self._set_children_mouse_transparent(child)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw rounded rect background with white base
        rect = self.rect().adjusted(2, 2, -2, -2)
        
        # Create rounded rect path for clipping
        clip_path = QPainterPath()
        clip_path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), 8, 8)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRoundedRect(rect, 8, 8)
        
        # Draw background image with 30% opacity if exists
        if self.background_path and os.path.exists(self.background_path):
            pixmap = QPixmap(self.background_path)
            if not pixmap.isNull():
                painter.setOpacity(0.3)
                scaled_pixmap = pixmap.scaled(rect.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                # Center crop with rounded clipping
                x_offset = (scaled_pixmap.width() - rect.width()) // 2
                y_offset = (scaled_pixmap.height() - rect.height()) // 2
                painter.setClipPath(clip_path)
                painter.drawPixmap(rect.x() - x_offset, rect.y() - y_offset, scaled_pixmap)
                painter.setOpacity(1.0)
        
        # Draw border
        painter.setClipping(False)
        if self.selected:
            # Selected state - thicker blue border
            pen = QPen(QColor("#0ea5e9"))
            pen.setWidth(4)
        else:
            pen = QPen(QColor(self.border_color))
            pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, 8, 8)
        
        painter.end()
    
    def set_selected(self, selected):
        """Set selection state"""
        self.selected = selected
        self.update()
    
    def show_context_menu(self, pos):
        """Show right-click context menu"""
        menu = QMenu(self)
        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        menu.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        menu.setWindowFlags(menu.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 6px 0px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 24px;
                margin: 0px 4px;
                color: #111827;
                font-weight: 600;
            }
            QMenu::item:selected {
                background-color: #f3f4f6;
                border-radius: 4px;
            }
        """)
        
        copy_action = QAction("复制", self)
        copy_action.triggered.connect(lambda: self.card_copy.emit(self.card_index))
        menu.addAction(copy_action)
        
        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(lambda: self.card_double_clicked.emit(self.card_index))
        menu.addAction(edit_action)
        
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self.card_deleted.emit(self.card_index))
        menu.addAction(delete_action)
        
        menu.exec(self.mapToGlobal(pos))
    
    def mousePressEvent(self, event):
        """Handle mouse press for selection"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.card_clicked.emit(self.card_index)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Emit signal when card is double-clicked"""
        self.card_double_clicked.emit(self.card_index)
        super().mouseDoubleClickEvent(event)


class PreviewWidget(QWidget):
    DATA_FILE = "matches.json"
    
    def __init__(self, cn_font_family="Microsoft YaHei", en_font_family="Microsoft YaHei"):
        super().__init__()
        self.cn_font_family = cn_font_family
        self.en_font_family = en_font_family
        self.data = []  # Store match data
        self.selected_index = -1  # Currently selected card index
        self.clipboard_data = None  # For copy/paste
        self.cards = []  # Keep track of card widgets
        
        # Enable focus for keyboard shortcuts
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Setup keyboard shortcuts
        self.copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self)
        self.copy_shortcut.activated.connect(self.copy_selected)
        self.paste_shortcut = QShortcut(QKeySequence.StandardKey.Paste, self)
        self.paste_shortcut.activated.connect(self.paste_match)
        self.delete_shortcut = QShortcut(QKeySequence.StandardKey.Delete, self)
        self.delete_shortcut.activated.connect(self.delete_selected)
        
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        # Title
        self.title = QLabel("直播安排表预览")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont(cn_font_family, 16, QFont.Weight.Bold))
        self.main_layout.addWidget(self.title)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("+ 添加比赛")
        self.add_btn.clicked.connect(self.add_match)
        btn_layout.addWidget(self.add_btn)
        
        self.sort_btn = QPushButton("▲ 按时间排序")
        self.sort_btn.clicked.connect(self.sort_by_time)
        btn_layout.addWidget(self.sort_btn)
        
        self.clear_btn = QPushButton("× 清空全部")
        self.clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.clear_btn)
        
        btn_layout.addStretch()
        self.main_layout.addLayout(btn_layout)
        
        # Scroll area for the cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #f5f5f5; }")
        
        # Container widget for the grid
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #f5f5f5;")
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        
        self.scroll_area.setWidget(self.container)
        self.main_layout.addWidget(self.scroll_area)
        
        # Region colors
        self.region_colors = {
            "pacific": QColor("#00B5E2"),
            "emea": QColor("#004667"),
            "americas": QColor("#DE4500"),
            "amer": QColor("#DE4500"),
            "cn": QColor("#E04F4F"),
            "masters": QColor("#9B59B6"),
            "champions": QColor("#C6B275"),
            "others": QColor("#6b7280")
        }

    def load_data(self):
        """Load data from JSON file"""
        try:
            if os.path.exists(self.DATA_FILE):
                with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                return True
        except:
            pass
        return False
    
    def save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def populate_initial_data(self):
        """Load saved data or initialize with sample data"""
        if not self.load_data():
            # No saved data, use sample
            self.data = [
                ["2026.3.3", "01:00", "masters", "m8 vs edg", "第一轮", "BO3"],
                ["2026.3.3", "03:00", "masters", "t1 vs tl", "第一轮", "BO3"],
                ["2026.3.3", "05:00", "masters", "g2 vs prx", "第一轮", "BO3"],
                ["2026.3.3", "07:00", "masters", "xlg vs nrg", "第一轮", "BO3"],
                ["2026.3.3", "01:00", "masters", "待定 vs 待定", "第二轮 (0-1)", "BO3"],
                ["2026.3.3", "03:00", "masters", "待定 vs 待定", "第二轮 (0-1)", "BO3"],
                ["2026.3.4", "01:00", "masters", "待定 vs 待定", "第二轮 (0-1)", "BO3"],
                ["2026.3.4", "03:00", "masters", "待定 vs 待定", "第二轮 (0-1)", "BO3"],
                ["2026.3.5", "01:00", "masters", "待定 vs 待定", "第三轮 (1-1)", "BO3"],
                ["2026.3.5", "03:00", "masters", "待定 vs 待定", "第三轮 (1-1)", "BO3"],
            ]
        self.refresh_cards()

    def add_match(self):
        """Add a new match and open edit dialog"""
        new_data = ["", "", "pacific", "", "", "BO3"]
        dialog = MatchEditDialog(self, new_data)
        if dialog.exec():
            self.data.append(dialog.get_data())
            self.refresh_cards()
            self.save_data()

    def edit_match(self, index):
        """Edit match at given index"""
        if 0 <= index < len(self.data):
            dialog = MatchEditDialog(self, self.data[index])
            if dialog.exec():
                self.data[index] = dialog.get_data()
                self.refresh_cards()
                self.save_data()

    def delete_match(self, index):
        """Delete match at given index"""
        if 0 <= index < len(self.data):
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(self, "确认删除", "确定要删除这场比赛吗？",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                del self.data[index]
                self.refresh_cards()
                self.save_data()

    def refresh_cards(self):
        """Refresh the card display"""
        # Clear existing cards
        self.cards = []
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add match cards in 2-column layout
        for idx, row_data in enumerate(self.data):
            card = MatchCard(row_data, idx, self.cn_font_family, self.en_font_family, self.region_colors)
            card.card_double_clicked.connect(self.edit_match)
            card.card_clicked.connect(self.select_card)
            card.card_copy.connect(self.copy_match)
            card.card_deleted.connect(self.delete_match)
            self.cards.append(card)
            row = idx // 2
            col = idx % 2
            self.grid_layout.addWidget(card, row, col, Qt.AlignmentFlag.AlignTop)
        
        # Restore selection if valid
        if 0 <= self.selected_index < len(self.cards):
            self.cards[self.selected_index].set_selected(True)
        else:
            self.selected_index = -1
        
        # Add stretch at the bottom
        self.grid_layout.setRowStretch(len(self.data) // 2 + 1, 1)
    
    def select_card(self, index):
        """Select a card by index"""
        # Deselect previous
        if 0 <= self.selected_index < len(self.cards):
            self.cards[self.selected_index].set_selected(False)
        
        # Select new
        self.selected_index = index
        if 0 <= index < len(self.cards):
            self.cards[index].set_selected(True)
            self.setFocus()  # Take focus for keyboard shortcuts
    
    def copy_match(self, index):
        """Copy match data at index to clipboard"""
        if 0 <= index < len(self.data):
            self.clipboard_data = list(self.data[index])  # Copy the data
    
    def copy_selected(self):
        """Copy currently selected match"""
        if self.selected_index >= 0:
            self.copy_match(self.selected_index)
    
    def paste_match(self):
        """Paste copied match data"""
        if self.clipboard_data:
            # Insert after selected, or at end
            insert_pos = self.selected_index + 1 if self.selected_index >= 0 else len(self.data)
            self.data.insert(insert_pos, list(self.clipboard_data))
            self.selected_index = insert_pos
            self.refresh_cards()
            self.save_data()
    
    def delete_selected(self):
        """Delete currently selected match"""
        if self.selected_index >= 0:
            self.delete_match(self.selected_index)
    
    def sort_by_time(self):
        """Sort matches by date and time"""
        def parse_datetime(match_data):
            date_str = match_data[0] if len(match_data) > 0 else ""
            time_str = match_data[1] if len(match_data) > 1 else "00:00"
            
            # Parse date (Y.M.D or M.D format)
            try:
                parts = date_str.split('.')
                if len(parts) == 3:
                    year, month, day = map(int, parts)
                elif len(parts) == 2:
                    month, day = map(int, parts)
                    year = QDate.currentDate().year()
                else:
                    year, month, day = 9999, 12, 31
            except:
                year, month, day = 9999, 12, 31
            
            # Parse time (HH:MM format)
            try:
                hour, minute = map(int, time_str.split(':'))
            except:
                hour, minute = 0, 0
            
            return (year, month, day, hour, minute)
        
        self.data.sort(key=parse_datetime)
        self.selected_index = -1
        self.refresh_cards()
        self.save_data()
    
    def clear_all(self):
        """清空所有比赛数据"""
        if not self.data:
            return
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "确认清空", "确定要清空所有比赛吗？",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.data = []
            self.selected_index = -1
            self.refresh_cards()
            self.save_data()
    
    def mousePressEvent(self, event):
        """Deselect when clicking on empty space"""
        # Check if click is on a card
        child = self.childAt(event.pos())
        if child is None or not isinstance(child, MatchCard):
            # Deselect
            if 0 <= self.selected_index < len(self.cards):
                self.cards[self.selected_index].set_selected(False)
            self.selected_index = -1
        super().mousePressEvent(event)

    def get_data(self):
        """Return current data"""
        return self.data


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VCT Display Demo - Schedule Visualizer")
        self.resize(900, 700)

        # Load custom fonts
        self.cn_font_family = "Microsoft YaHei"  # Fallback for Chinese
        self.en_font_family = "Microsoft YaHei"  # Fallback for English
        
        # Load HarmonyOS Sans for Chinese
        if os.path.exists(CN_FONT_PATH):
            cn_font_id = QFontDatabase.addApplicationFont(CN_FONT_PATH)
            if cn_font_id >= 0:
                cn_families = QFontDatabase.applicationFontFamilies(cn_font_id)
                if cn_families:
                    self.cn_font_family = cn_families[0]
        
        # Load FoundryGridnik for English
        if os.path.exists(FONT_PATH):
            en_font_id = QFontDatabase.addApplicationFont(FONT_PATH)
            if en_font_id >= 0:
                en_families = QFontDatabase.applicationFontFamilies(en_font_id)
                if en_families:
                    self.en_font_family = en_families[0]

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Initialize preview widget (now the only widget)
        self.preview_widget = PreviewWidget(self.cn_font_family, self.en_font_family)
        main_layout.addWidget(self.preview_widget)
        
        # Initialize with sample data
        self.preview_widget.populate_initial_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
