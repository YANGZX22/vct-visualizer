"""
VCT Display Demo - Main Application Entry Point
"""
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtGui import QFontDatabase, QIcon, QAction

from config import FONT_PATH, CN_FONT_PATH
from preview import PreviewWidget

# Icon path
ICON_PATH = os.path.join(os.path.dirname(__file__), "icon.jpg")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VCT Display Demo - Schedule Visualizer")
        self.resize(900, 700)
        
        # Set window icon
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

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

        # Create menu bar
        self.create_menu_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Initialize preview widget (now the only widget)
        self.preview_widget = PreviewWidget(self.cn_font_family, self.en_font_family)
        main_layout.addWidget(self.preview_widget)
        
        # Initialize with sample data
        self.preview_widget.populate_initial_data()
    
    def create_menu_bar(self):
        """Create the menu bar with Help and License options"""
        menubar = self.menuBar()
        
        # Help action (direct menu item)
        help_action = QAction("帮助", self)
        help_action.triggered.connect(self.show_help)
        menubar.addAction(help_action)
        
        # License action (direct menu item)
        license_action = QAction("许可", self)
        license_action.triggered.connect(self.show_license)
        menubar.addAction(license_action)
    
    def show_help(self):
        """Show help dialog"""
        help_text = """VCT Display Demo 使用说明

【基本操作】
• 添加比赛：点击"+ 添加比赛"按钮
• 编辑比赛：双击卡片
• 删除比赛：选中卡片后按 Delete 键，或右键菜单选择删除
• 复制/粘贴：Ctrl+C / Ctrl+V
• 排序：点击"▲ 按时间排序"

【导入赛程】
• 点击"↓ 导入赛程"从 VLR.gg 自动获取比赛数据
• 支持按赛事筛选和多选导入

【导出图片】
• 点击"导入背景"选择自定义背景图片
• 点击"导出图片"生成高清长图
• 支持多种分辨率：960px / 1080px / 1920px / 2880px

【快捷键】
• Ctrl+C：复制选中比赛
• Ctrl+V：粘贴比赛
• Delete：删除选中比赛
"""
        QMessageBox.information(self, "使用说明", help_text)
    
    def show_license(self):
        """Show license dialog"""
        license_path = os.path.join(os.path.dirname(__file__), "LICENSE")
        content = ""
        
        if os.path.exists(license_path):
            try:
                with open(license_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                content = f"Error reading license file: {str(e)}"
        else:
             # Fallback if file not found locally (e.g. in some frozen environments)
            content = "MIT License\n(License file not found)"

        disclaimer = "---\n本软件使用的图标、图片等素材版权归 Riot Games 或相关赛事方所有。\n本软件仅供学习交流使用，不得用于商业用途。"
        QMessageBox.information(self, "许可证", content + disclaimer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application icon (for taskbar)
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
