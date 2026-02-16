"""
Dialog classes for VCT Display Demo
"""
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QDialogButtonBox, 
                             QLabel, QSpinBox, QListWidget, QListWidgetItem,
                             QCalendarWidget, QFrame, QGraphicsDropShadowEffect,
                             QPushButton, QLineEdit)
from PyQt6.QtCore import Qt, QDate, QTime, QSize
from PyQt6.QtGui import QColor, QIcon

from config import TOURNAMENTS
from utils import get_tournament_icon_path
from widgets import TwoDigitSpinBox, TeamPickerWidget


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
        self.team_a_picker = TeamPickerWidget("Team A:")
        if team_a:
            self.team_a_picker.set_team(team_a)
        layout.addWidget(self.team_a_picker)
        
        layout.addWidget(QLabel("vs"))
        
        # Team B picker
        self.team_b_picker = TeamPickerWidget("Team B:")
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
    
    # Mapping from tournament to region (for regional tournaments)
    TOURNAMENT_TO_REGION = {
        "pacific": "pacific",
        "emea": "emea",
        "americas": "amer",
        "cn": "cn",
    }
    
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

        # Apply dialog styling
        self._apply_stylesheet()
    
    def _apply_stylesheet(self):
        """Apply dialog-wide styling"""
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
