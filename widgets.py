"""
Custom widgets for VCT Display Demo
"""
import os
from PyQt6.QtWidgets import QSpinBox, QWidget, QVBoxLayout, QLabel, QComboBox, QInputDialog, QMessageBox
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon

from config import TEAMS_BY_REGION
from utils import get_tournament_icon_path, get_team_icon_path


class TwoDigitSpinBox(QSpinBox):
    """QSpinBox that always displays two digits with leading zero"""
    def textFromValue(self, value: int) -> str:
        return f"{value:02d}"


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
        self.team_combo.activated.connect(self.on_team_selected)
        layout.addWidget(self.team_combo)
        
        # Initialize teams for first region
        if self.region_combo.count() > 0:
            self.update_teams(0)
            
    def on_team_selected(self, index):
        """Handle team selection, check for manual input"""
        current_text = self.team_combo.itemText(index)
        if current_text == "手动输入" or current_text == "MANUAL INPUT":
            text, ok = QInputDialog.getText(self, "手动输入队伍", "请输入队伍名称:")
            if ok and text.strip():
                # Add new item before the last one (manual input)
                count = self.team_combo.count()
                self.team_combo.insertItem(count - 1, text.upper(), text.strip())
                self.team_combo.setCurrentIndex(count - 1)
            else:
                # Revert or clear selection if cancelled? 
                # Just keeping "手动输入" selected is fine, or revert to 0
                pass
    
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
        team_lower = team_name.lower().strip()
        if not team_lower:
            return
            
        found = False
        # Find region for this team
        for region, teams in TEAMS_BY_REGION.items():
            if team_lower in teams:
                found = True
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
        
        # If not found in predefined lists, add to current region as custom
        # But wait, we should probably switch to 'others' region for custom teams?
        if not found:
            # Switch to 'others' if not already there
            others_idx = -1
            for i in range(self.region_combo.count()):
                if self.region_combo.itemData(i) == "others":
                    others_idx = i
                    break
            
            if others_idx >= 0:
                self.region_combo.setCurrentIndex(others_idx)
                # Add custom team to valid position (before "手动输入")
                count = self.team_combo.count()
                # Check if "手动输入" is last
                last_text = self.team_combo.itemText(count - 1)
                insert_pos = count - 1 if (last_text == "手动输入" or last_text == "MANUAL INPUT") else count
                
                self.team_combo.insertItem(insert_pos, team_name.upper(), team_name)
                self.team_combo.setCurrentIndex(insert_pos)

    def get_team(self):
        # Prefer currentText if currentData is empty or Manual Input
        data = self.team_combo.currentData()
        text = self.team_combo.currentText()
        
        if text == "手动输入" or text == "MANUAL INPUT":
            return ""
            
        return data if data else text
    
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
