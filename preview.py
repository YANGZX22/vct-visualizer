"""
Preview widget for VCT Display Demo
"""
import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QGridLayout, QMessageBox,
                             QFileDialog)
from PyQt6.QtCore import Qt, QDate, QRect
from PyQt6.QtGui import QFont, QColor, QShortcut, QKeySequence, QPixmap, QPainter, QImage

from cards import MatchCard
from dialogs import MatchEditDialog
from api_import import show_vlr_import_dialog


class BackgroundContainer(QWidget):
    """Container widget that can display a background image"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.background_pixmap = None
    
    def set_background(self, path):
        """Set the background image from path"""
        if path and os.path.exists(path):
            self.background_pixmap = QPixmap(path)
        else:
            self.background_pixmap = None
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Fill with default color first
        painter.fillRect(self.rect(), QColor("#f5f5f5"))
        
        # Draw background if set
        if self.background_pixmap and not self.background_pixmap.isNull():
            # Scale to widget width, keeping aspect ratio
            scaled_bg = self.background_pixmap.scaledToWidth(
                self.width(), Qt.TransformationMode.SmoothTransformation
            )
            bg_height = scaled_bg.height()
            
            # Tile vertically if needed
            y = 0
            while y < self.height():
                painter.drawPixmap(0, y, scaled_bg)
                y += bg_height
        
        painter.end()


class PreviewWidget(QWidget):
    DATA_FILE = "matches.json"
    SETTINGS_FILE = "settings.json"
    
    def __init__(self, cn_font_family="Microsoft YaHei", en_font_family="Microsoft YaHei"):
        super().__init__()
        self.cn_font_family = cn_font_family
        self.en_font_family = en_font_family
        self.data = []  # Store match data
        self.selected_index = -1  # Currently selected card index
        self.clipboard_data = None  # For copy/paste
        self.cards = []  # Keep track of card widgets
        self.background_path = None  # Background image path for export
        
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
        
        self.vlr_import_btn = QPushButton("↓ 从 VLR.gg 导入赛程")
        self.vlr_import_btn.clicked.connect(self.import_from_vlr)
        btn_layout.addWidget(self.vlr_import_btn)
        
        btn_layout.addStretch()
        
        self.import_bg_btn = QPushButton("导入背景")
        self.import_bg_btn.clicked.connect(self.import_background)
        btn_layout.addWidget(self.import_bg_btn)
        
        self.export_btn = QPushButton("导出图片")
        self.export_btn.clicked.connect(self.export_image)
        btn_layout.addWidget(self.export_btn)
        
        self.main_layout.addLayout(btn_layout)
        
        # Scroll area for the cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #f5f5f5; }")
        
        # Container widget for the grid
        self.container = BackgroundContainer()
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
            "ascensions": QColor("#0DB397"),
            "national tournament": QColor("#D6B200"),
            "others": QColor("#6b7280")
        }
        
        # Load settings (including background path)
        self.load_settings()

    def load_settings(self):
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.background_path = settings.get('background_path', None)
                    # Update container background preview
                    self.container.set_background(self.background_path)
        except:
            pass
    
    def save_settings(self):
        """Save settings to JSON file"""
        try:
            settings = {'background_path': self.background_path}
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def import_background(self):
        """导入背景图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择背景图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.webp);;All Files (*)"
        )
        if file_path:
            self.background_path = file_path
            self.save_settings()
            # Update container background preview
            self.container.set_background(self.background_path)
    
    def import_from_vlr(self):
        """从VLR.gg导入赛程"""
        matches = show_vlr_import_dialog(self)
        if matches:
            self.data.extend(matches)
            self.refresh_cards()
            self.save_data()
            QMessageBox.information(self, "成功", f"已导入 {len(matches)} 场比赛")
    
    def export_image(self):
        """导出为竖向1080px宽图片"""
        if not self.data:
            QMessageBox.warning(self, "提示", "没有比赛数据可导出")
            return
        
        # Ask for save path
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存图片", "schedule.png",
            "图片文件 (*.png);;JPEG文件 (*.jpg)"
        )
        if not file_path:
            return
        
        # Constants for export
        EXPORT_WIDTH = 1080
        CARD_WIDTH = 480  # Each card width
        CARD_HEIGHT = 100
        CARD_SPACING = 10
        MARGIN = 55  # Side margins ((1080 - 480*2 - 10) / 2 = 55)
        TOP_MARGIN = 40
        BOTTOM_MARGIN = 40
        
        # Calculate number of rows (2 cards per row)
        num_rows = (len(self.data) + 1) // 2
        content_height = TOP_MARGIN + num_rows * (CARD_HEIGHT + CARD_SPACING) - CARD_SPACING + BOTTOM_MARGIN
        
        # Create the final image
        final_image = QImage(EXPORT_WIDTH, content_height, QImage.Format.Format_ARGB32)
        final_image.fill(QColor(255, 255, 255))  # White fallback
        
        painter = QPainter(final_image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Draw background (repeat if too short, clip if too long)
        if self.background_path and os.path.exists(self.background_path):
            bg_pixmap = QPixmap(self.background_path)
            if not bg_pixmap.isNull():
                # Scale to width 1080, keeping aspect ratio
                scaled_bg = bg_pixmap.scaledToWidth(EXPORT_WIDTH, Qt.TransformationMode.SmoothTransformation)
                bg_height = scaled_bg.height()
                
                # Tile vertically if needed
                y = 0
                while y < content_height:
                    painter.drawPixmap(0, y, scaled_bg)
                    y += bg_height
        
        # Render each card
        for idx, row_data in enumerate(self.data):
            # Create a temporary card widget
            card = MatchCard(row_data, idx, self.cn_font_family, self.en_font_family, self.region_colors)
            card.setFixedSize(CARD_WIDTH, CARD_HEIGHT)
            
            # Calculate position in grid
            row = idx // 2
            col = idx % 2
            x = MARGIN + col * (CARD_WIDTH + CARD_SPACING)
            y = TOP_MARGIN + row * (CARD_HEIGHT + CARD_SPACING)
            
            # Render card to pixmap
            card_pixmap = QPixmap(card.size())
            card_pixmap.fill(Qt.GlobalColor.transparent)
            card.render(card_pixmap)
            
            # Draw card onto final image
            painter.drawPixmap(x, y, card_pixmap)
            
            # Clean up
            card.deleteLater()
        
        painter.end()
        
        # Save the image
        if final_image.save(file_path):
            QMessageBox.information(self, "成功", f"图片已保存到:\n{file_path}")
        else:
            QMessageBox.warning(self, "失败", "图片保存失败")

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
                ["2026.3.1", "01:00", "masters", "m8 vs edg", "第一轮", "BO3"],
                ["2026.3.1", "03:00", "masters", "t1 vs tl", "第一轮", "BO3"],
                ["2026.3.2", "01:00", "masters", "g2 vs prx", "第一轮", "BO3"],
                ["2026.3.2", "03:00", "masters", "xlg vs nrg", "第一轮", "BO3"],
                ["2026.3.3", "01:00", "masters", "待定 vs 待定", "第二轮 (1-0)", "BO3"],
                ["2026.3.3", "03:00", "masters", "待定 vs 待定", "第二轮 (1-0)", "BO3"],
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
