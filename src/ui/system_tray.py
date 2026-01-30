"""System tray integration for the German Wallpaper App."""

import sys
import os
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class SystemTray(QSystemTrayIcon):
    """System tray icon with menu for show/hide/exit."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._setup_tray()
        
    def _setup_tray(self):
        """Setup the system tray icon and menu."""
        # Set icon (using a default for now - can be customized later)
        # For now, use a simple colored icon from Qt
        from PyQt5.QtGui import QPixmap, QPainter, QColor
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(QColor("#e94560"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        painter.end()
        
        self.setIcon(QIcon(pixmap))
        self.setToolTip("German Vocabulary Wallpaper")
        
        # Create context menu
        menu = QMenu()
        
        # Show/Hide action
        self.show_hide_action = QAction("Hide", menu)
        self.show_hide_action.triggered.connect(self._toggle_visibility)
        menu.addAction(self.show_hide_action)
        
        menu.addSeparator()
        
        # Statistics action
        stats_action = QAction("Statistics...", menu)
        stats_action.triggered.connect(self._show_statistics)
        menu.addAction(stats_action)
        
        # Settings action
        settings_action = QAction("Settings...", menu)
        settings_action.triggered.connect(self._show_settings)
        menu.addAction(settings_action)
        
        # Import CSV action
        import_action = QAction("Import CSV...", menu)
        import_action.triggered.connect(self._import_csv)
        menu.addAction(import_action)
        
        menu.addSeparator()
        
        # Mute toggle
        self.mute_action = QAction("Mute Audio", menu)
        self.mute_action.setCheckable(True)
        self.mute_action.triggered.connect(self._toggle_mute)
        menu.addAction(self.mute_action)
        
        menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", menu)
        exit_action.triggered.connect(self._exit_app)
        menu.addAction(exit_action)
        
        self.setContextMenu(menu)
        
        # Double-click to show/hide
        self.activated.connect(self._on_activated)
        
        # Show tray icon
        self.show()
    
    def _toggle_visibility(self):
        """Toggle main window visibility."""
        if self.parent_window:
            if self.parent_window.isVisible():
                self.parent_window.hide()
                self.show_hide_action.setText("Show")
            else:
                self.parent_window.show()
                self.show_hide_action.setText("Hide")
    
    def _on_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            self._toggle_visibility()
    
    def _show_statistics(self):
        """Show statistics window."""
        if self.parent_window:
            self.parent_window._show_statistics()
    
    def _show_settings(self):
        """Show settings dialog."""
        if self.parent_window:
            self.parent_window._show_settings()
    
    def _import_csv(self):
        """Show CSV import dialog."""
        if self.parent_window:
            self.parent_window._show_csv_import()
    
    def _toggle_mute(self, checked):
        """Toggle audio mute."""
        if self.parent_window and hasattr(self.parent_window, 'config'):
            self.parent_window.config['behavior']['auto_pronounce'] = not checked
    
    def _exit_app(self):
        """Exit the application."""
        if self.parent_window:
            self.parent_window.close()
        from PyQt5.QtWidgets import QApplication
        QApplication.quit()
