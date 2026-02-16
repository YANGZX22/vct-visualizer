"""
VCT Display Demo - Main Application Entry Point
"""
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtGui import QFontDatabase, QIcon

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
    
    # Set application icon (for taskbar)
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
