"""Main entry point for the German Vocabulary Wallpaper App."""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.main_window import MainWindow
from src.ui.system_tray import SystemTray


def main():
    """Initialize and run the application."""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("German Vocabulary Wallpaper")
    app.setOrganizationName("GermanVocab")
    
    # Set application to stay running even when window is hidden
    app.setQuitOnLastWindowClosed(False)
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Create system tray
    tray = SystemTray(window)
    
    # Store references to prevent garbage collection
    app.main_window = window
    app.system_tray = tray
    
    # Run application
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
