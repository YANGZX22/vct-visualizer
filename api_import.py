"""
VLR.gg API Integration for importing match schedules
"""
import urllib.request
import urllib.error
import json
import re
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QSpinBox, QCheckBox,
                             QProgressBar, QListWidget, QListWidgetItem,
                             QMessageBox, QGroupBox, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from utils import normalize_team_name


# VLR.gg API base URL
API_BASE_URL = "https://vlrggapi.vercel.app/v2/match"

# Known event keywords to tournament mapping (order matters - more specific first)
EVENT_TO_TOURNAMENT = {
    # Masters/Champions (check first - highest priority)
    "masters": "masters",
    "champions": "champions",
    "lock//in": "masters",
    "lock-in": "masters",
    
    # Ascension / National tournaments
    "ascension": "ascensions",
    "challengers": "national tournament",
    "national": "national tournament",
    
    # Pacific region variations
    "pacific": "pacific",
    "apac": "pacific",
    "asia-pacific": "pacific",
    "japan": "pacific",
    "korea": "pacific",
    "sea": "pacific",
    "southeast asia": "pacific",
    
    # EMEA region variations
    "emea": "emea",
    "europe": "emea",
    "eu": "emea",
    "cis": "emea",
    "turkey": "emea",
    "mena": "emea",
    
    # Americas region variations
    "americas": "americas",
    "amer": "americas",
    "na": "americas",
    "north america": "americas",
    "latam": "americas",
    "latin america": "americas",
    "brazil": "americas",
    "br": "americas",
    
    # China region variations
    "china": "cn",
    "cn": "cn",
    "chinese": "cn",
}


class FetchWorker(QThread):
    """Worker thread for fetching API data"""
    finished = pyqtSignal(list, str)  # matches, error_message
    progress = pyqtSignal(int, int)  # current, total
    
    def __init__(self, query_type="upcoming", num_pages=1):
        super().__init__()
        self.query_type = query_type
        self.num_pages = num_pages
    
    def run(self):
        try:
            all_matches = []
            for page in range(1, self.num_pages + 1):
                self.progress.emit(page, self.num_pages)
                url = f"{API_BASE_URL}?q={self.query_type}&from_page={page}&to_page={page}"
                
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'VCT Display Demo/1.0'
                })
                
                with urllib.request.urlopen(req, timeout=30) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    if data.get('status') == 'success' and data.get('data'):
                        segments = data['data'].get('segments', [])
                        all_matches.extend(segments)
            
            self.finished.emit(all_matches, "")
        except urllib.error.URLError as e:
            self.finished.emit([], f"网络错误: {str(e)}")
        except Exception as e:
            self.finished.emit([], f"错误: {str(e)}")


class VLRImportDialog(QDialog):
    """Dialog for importing matches from VLR.gg API"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("从 VLR.gg 导入赛程")
        self.setMinimumSize(600, 500)
        self.fetched_matches = []
        self.selected_matches = []
        self.worker = None
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Query settings
        settings_group = QGroupBox("查询设置")
        settings_layout = QHBoxLayout(settings_group)
        
        settings_layout.addWidget(QLabel("数据类型:"))
        self.query_combo = QComboBox()
        self.query_combo.addItems(["upcoming", "upcoming_extended", "live_score", "results"])
        self.query_combo.setCurrentIndex(1)  # Default to upcoming_extended
        settings_layout.addWidget(self.query_combo)
        
        settings_layout.addWidget(QLabel("页数:"))
        self.pages_spin = QSpinBox()
        self.pages_spin.setRange(1, 10)
        self.pages_spin.setValue(5)
        settings_layout.addWidget(self.pages_spin)
        
        settings_layout.addStretch()
        
        self.fetch_btn = QPushButton("获取赛程")
        self.fetch_btn.clicked.connect(self.fetch_matches)
        settings_layout.addWidget(self.fetch_btn)
        
        layout.addWidget(settings_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Event filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("筛选赛事:"))
        self.event_filter = QComboBox()
        self.event_filter.addItem("全部赛事", "")
        self.event_filter.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.event_filter, 1)
        
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.clicked.connect(self.select_all)
        filter_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("取消全选")
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        filter_layout.addWidget(self.deselect_all_btn)
        
        layout.addLayout(filter_layout)
        
        # Match list
        self.match_list = QListWidget()
        self.match_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.match_list, 1)
        
        # Status label
        self.status_label = QLabel('点击"获取赛程"开始')
        self.status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.status_label)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.import_btn = QPushButton("导入选中")
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.import_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def fetch_matches(self):
        """Fetch matches from API"""
        self.fetch_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.match_list.clear()
        self.status_label.setText("正在获取数据...")
        
        self.worker = FetchWorker(
            self.query_combo.currentText(),
            self.pages_spin.value()
        )
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_fetch_finished)
        self.worker.start()
    
    def on_progress(self, current, total):
        """Update progress bar"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
    
    def on_fetch_finished(self, matches, error):
        """Handle fetch completion"""
        self.fetch_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if error:
            self.status_label.setText(f"错误: {error}")
            return
        
        self.fetched_matches = matches
        self.populate_event_filter()
        self.populate_match_list()
        self.status_label.setText(f"共获取 {len(matches)} 场比赛")
    
    def populate_event_filter(self):
        """Populate event filter dropdown"""
        events = set()
        for match in self.fetched_matches:
            event = match.get('match_event', '')
            if event:
                events.add(event)
        
        self.event_filter.blockSignals(True)
        self.event_filter.clear()
        self.event_filter.addItem("全部赛事", "")
        for event in sorted(events):
            self.event_filter.addItem(event, event)
        self.event_filter.blockSignals(False)
    
    def populate_match_list(self, filter_event=""):
        """Populate match list with fetched data"""
        self.match_list.clear()
        
        for i, match in enumerate(self.fetched_matches):
            event = match.get('match_event', '')
            if filter_event and event != filter_event:
                continue
            
            team1 = match.get('team1', '?')
            team2 = match.get('team2', '?')
            time_until = match.get('time_until_match', '')
            timestamp = match.get('unix_timestamp', '')
            series = match.get('match_series', '')
            
            # Format display text
            display = f"{team1} vs {team2}"
            if timestamp:
                display = f"[{timestamp}] {display}"
            elif time_until:
                display = f"[{time_until}] {display}"
            if series:
                display += f" ({series})"
            
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, i)  # Store original index
            self.match_list.addItem(item)
        
        self.import_btn.setEnabled(self.match_list.count() > 0)
    
    def apply_filter(self):
        """Apply event filter"""
        filter_event = self.event_filter.currentData()
        self.populate_match_list(filter_event)
    
    def select_all(self):
        """Select all visible items"""
        for i in range(self.match_list.count()):
            self.match_list.item(i).setSelected(True)
    
    def deselect_all(self):
        """Deselect all items"""
        self.match_list.clearSelection()
    
    def get_selected_matches(self):
        """Get selected matches converted to app format"""
        result = []
        
        for item in self.match_list.selectedItems():
            idx = item.data(Qt.ItemDataRole.UserRole)
            match = self.fetched_matches[idx]
            converted = self.convert_match(match)
            if converted:
                result.append(converted)
        
        return result
    
    def _round_time(self, dt):
        """Round datetime to nearest 30 minutes (common match start times)"""
        minute = dt.minute
        # Round to nearest 30: 0, 30
        if minute < 15:
            new_minute = 0
        elif minute < 45:
            new_minute = 30
        else:
            new_minute = 0
            dt = dt + timedelta(hours=1)
        
        return dt.replace(minute=new_minute, second=0, microsecond=0)
    
    def convert_match(self, match_data):
        """Convert VLR match data to app format [date, time, tournament, match_info, remarks, bo]"""
        team1_raw = match_data.get('team1', '?')
        team2_raw = match_data.get('team2', '?')
        event = match_data.get('match_event', '')
        series = match_data.get('match_series', '')
        timestamp = match_data.get('unix_timestamp', '')  # Format: "2024-04-24 21:00:00"
        time_until = match_data.get('time_until_match', '')  # Format: "51m from now", "2h from now", "1d from now"
        
        # Normalize team names to abbreviations
        team1 = normalize_team_name(team1_raw)
        team2 = normalize_team_name(team2_raw)
        
        # Parse timestamp
        date_str = ""
        time_str = ""
        
        # Try unix_timestamp first
        if timestamp:
            try:
                dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                # Round to nearest 30 minutes
                dt = self._round_time(dt)
                date_str = f"{dt.year}.{dt.month}.{dt.day}"
                time_str = dt.strftime("%H:%M")
            except:
                pass
        
        # If no timestamp, calculate from time_until_match
        if not date_str and time_until:
            try:
                now = datetime.now()
                dt = now
                
                # Parse relative time like "51m from now", "2h from now", "1d 2h from now"
                time_part = time_until.lower().replace("from now", "").strip()
                
                # Parse days
                if 'd' in time_part:
                    days_match = re.search(r'(\d+)\s*d', time_part)
                    if days_match:
                        dt = dt + timedelta(days=int(days_match.group(1)))
                
                # Parse hours
                if 'h' in time_part:
                    hours_match = re.search(r'(\d+)\s*h', time_part)
                    if hours_match:
                        dt = dt + timedelta(hours=int(hours_match.group(1)))
                
                # Parse minutes
                if 'm' in time_part and 'mo' not in time_part:  # avoid matching "months"
                    mins_match = re.search(r'(\d+)\s*m(?!o)', time_part)
                    if mins_match:
                        dt = dt + timedelta(minutes=int(mins_match.group(1)))
                
                # Round to nearest 30 minutes
                dt = self._round_time(dt)
                date_str = f"{dt.year}.{dt.month}.{dt.day}"
                time_str = dt.strftime("%H:%M")
            except:
                pass
        
        # Determine tournament from event name
        tournament = "others"
        event_lower = event.lower()
        for keyword, tour in EVENT_TO_TOURNAMENT.items():
            if keyword in event_lower:
                tournament = tour
                break
        
        # Build match info
        match_info = f"{team1} vs {team2}"
        
        # Remarks from series
        remarks = series if series else ""
        
        # Default BO3
        bo = "BO3"
        
        return [date_str, time_str, tournament, match_info, remarks, bo]


def show_vlr_import_dialog(parent=None):
    """Show the VLR import dialog and return selected matches"""
    dialog = VLRImportDialog(parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_selected_matches()
    return []
