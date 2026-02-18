"""
Match card widget for VCT Display Demo
"""
import os
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSizePolicy, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QPen, QPainterPath, QCursor, QAction

from utils import get_card_background_path, get_tournament_icon_path, get_team_icon_path


class MatchCard(QFrame):
    """A single match display card - clickable to edit"""
    card_double_clicked = pyqtSignal(int)  # Emits card index
    card_clicked = pyqtSignal(int)  # Emits card index for selection
    card_deleted = pyqtSignal(int)  # Emits card index for deletion
    card_copy = pyqtSignal(int)  # Emits card index for copy
    
    def __init__(self, match_data, card_index, cn_font_family, en_font_family, region_colors, parent=None, scale_factor=1.0):
        super().__init__(parent)
        self.cn_font_family = cn_font_family
        self.en_font_family = en_font_family
        self.card_index = card_index
        self.match_data = match_data
        self.selected = False
        self.scale_factor = scale_factor
        
        # Scale dimensions
        sf = scale_factor
        font_size = int(12 * sf)
        remarks_font_size = int(10 * sf)
        icon_size = int(24 * sf)
        team_icon_size = int(32 * sf)
        margin_h = int(10 * sf)
        margin_v = int(8 * sf)
        spacing = int(6 * sf)
        match_height = int(40 * sf)
        vs_width = int(40 * sf)
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Make card capture mouse events (don't let children intercept)
        self.setMouseTracking(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Set fixed height to prevent stretching
        self.setFixedHeight(int(100 * sf))
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
        layout.setContentsMargins(margin_h, margin_v, margin_h, margin_v)
        layout.setSpacing(spacing)
        
        # Fonts - English for team names/tournament, Chinese for date/time/remarks
        en_font = QFont(en_font_family, font_size, QFont.Weight.Bold)
        cn_font = QFont(cn_font_family, font_size, QFont.Weight.Bold)
        
        # Top row: Date | Time | Tournament
        top_layout = QHBoxLayout()
        top_layout.setSpacing(int(10 * sf))
        
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
        tournament_layout.setSpacing(int(4 * sf))
        
        icon_path = get_tournament_icon_path(tournament_val)
        if icon_path and os.path.exists(icon_path):
            icon_label = QLabel()
            pixmap = QPixmap(icon_path).scaled(icon_size, icon_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
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
        match_widget.setFixedHeight(match_height)
        match_layout = QHBoxLayout(match_widget)
        match_layout.setContentsMargins(0, 0, 0, 0)
        match_layout.setSpacing(0)
        
        # Team A (icon + name) - left aligned
        team_a_widget = QWidget()
        team_a_widget.setStyleSheet("background: transparent;")
        team_a_layout = QHBoxLayout(team_a_widget)
        team_a_layout.setContentsMargins(0, 0, 0, 0)
        team_a_layout.setSpacing(int(4 * sf))
        
        icon_path_a = get_team_icon_path(team_a)
        if icon_path_a and os.path.exists(icon_path_a):
            icon_label_a = QLabel()
            icon_label_a.setFixedSize(team_icon_size, team_icon_size)
            pixmap_a = QPixmap(icon_path_a).scaled(team_icon_size, team_icon_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
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
        vs_label.setFixedWidth(vs_width)
        match_layout.addWidget(vs_label, 0)
        
        # Team B (name + icon) - right aligned
        team_b_widget = QWidget()
        team_b_widget.setStyleSheet("background: transparent;")
        team_b_layout = QHBoxLayout(team_b_widget)
        team_b_layout.setContentsMargins(0, 0, 0, 0)
        team_b_layout.setSpacing(int(4 * sf))
        
        team_b_layout.addStretch()
        
        team_b_label = QLabel(team_b.upper())
        team_b_label.setFont(en_font)
        team_b_label.setStyleSheet(f"color: {color_name}; background: transparent;")
        team_b_layout.addWidget(team_b_label)
        
        icon_path_b = get_team_icon_path(team_b)
        if icon_path_b and os.path.exists(icon_path_b):
            icon_label_b = QLabel()
            icon_label_b.setFixedSize(team_icon_size, team_icon_size)
            pixmap_b = QPixmap(icon_path_b).scaled(team_icon_size, team_icon_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label_b.setPixmap(pixmap_b)
            icon_label_b.setStyleSheet("background: transparent;")
            team_b_layout.addWidget(icon_label_b)
        
        match_layout.addWidget(team_b_widget, 2)
        layout.addWidget(match_widget)
        
        # Bottom row: Remarks (if any)
        if remarks_val.strip():
            remarks_label = QLabel(remarks_val)
            remarks_label.setFont(QFont(cn_font_family, remarks_font_size, QFont.Weight.Bold))
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
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        sf = self.scale_factor
        border_adj = int(2 * sf)
        corner_radius = int(8 * sf)
        
        # Draw rounded rect background with white base
        rect = self.rect().adjusted(border_adj, border_adj, -border_adj, -border_adj)
        
        # Create rounded rect path for clipping
        clip_path = QPainterPath()
        clip_path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), corner_radius, corner_radius)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRoundedRect(rect, corner_radius, corner_radius)
        
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
            pen.setWidth(int(4 * sf))
        else:
            pen = QPen(QColor(self.border_color))
            pen.setWidth(int(2 * sf))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, corner_radius, corner_radius)
        
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
