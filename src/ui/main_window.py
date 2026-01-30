"""Main window with glassmorphic design and word display."""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QMenu, 
                             QAction, QApplication, QDesktopWidget)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QFontDatabase

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ui.word_display import WordDisplay
from src.ui.settings_dialog import SettingsDialog
from src.ui.stats_window import StatsWindow
from src.core.word_manager import WordManager
from src.core.history_tracker import HistoryTracker
from src.core.speech_engine import SpeechEngine
from src.core.gamification_tracker import GamificationTracker
from src.utils.helpers import load_json_safe, save_json_atomic, get_config_path, ensure_data_files_exist, get_styles_dir
from src.utils.notifications import NotificationManager


class MainWindow(QMainWindow):
    """Frameless glassmorphic window with word display and auto-refresh."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize data files
        ensure_data_files_exist()
        
        # Load configuration
        self.config = load_json_safe(str(get_config_path()))
        if not self.config:
            self.config = self._get_default_config()
        
        # Initialize core components
        self.word_manager = WordManager()
        self.history_tracker = HistoryTracker()
        self.speech_engine = SpeechEngine()
        self.gamification_tracker = GamificationTracker(Path('data/gamification.json'))
        self.notification_manager = NotificationManager()
        self.current_word_id = None
        self.stats_window = None
        self.tts_timer = None
        
        # Setup UI
        self._setup_window()
        self._load_stylesheet()
        self._setup_ui()
        self._setup_timer()
        self._apply_appearance_settings()
        
        # Display first word
        self.display_next_word()
        
    def _get_default_config(self):
        """Get default configuration."""
        return {
            "appearance": {
                "theme": "dark",
                "font_size_german": 48,
                "font_size_english": 24,
                "enable_animations": True,
                "opacity": 0.85,
                "show_progress": False
            },
            "behavior": {
                "refresh_interval_seconds": 60,
                "always_on_top": False,
                "auto_pronounce": False,
                "tts_volume": 80,
                "autostart": False,
                "time_based_categories": False
            },
            "learning": {
                "enabled_categories": ["all"],
                "difficulty_range": ["A1", "A2", "B1"],
                "time_rules": {
                    "morning": ["food", "adjectives"],
                    "afternoon": ["verbs", "travel"],
                    "evening": ["animals", "body"],
                    "night": ["core_1000"]
                }
            },
            "window": {
                "width": 600,
                "height": 400,
                "display_mode": "floating",
                "monitor": 0,
                "remember_position": False
            }
        }
    
    def _setup_window(self):
        """Setup window properties."""
        # Window title and basic settings
        self.setWindowTitle("German Vocabulary Wallpaper")
        
        # Frameless window with transparent background (stays on desktop, not on top)
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Get window configuration
        window_config = self.config.get('window', {})
        display_mode = window_config.get('display_mode', 'floating')
        monitor_index = window_config.get('monitor', 0)
        remember_position = window_config.get('remember_position', False)
        
        # Set size based on display mode
        if display_mode == 'corner':
            width, height = 200, 150
        else:  # floating
            width, height = 600, 400
        
        # Get monitor geometry
        desktop = QDesktopWidget()
        screen_count = desktop.screenCount()
        if monitor_index >= screen_count:
            monitor_index = 0
        
        screen_geometry = desktop.availableGeometry(monitor_index)
        
        # Position window
        if remember_position and 'position_x' in window_config:
            # Restore saved position
            x = window_config.get('position_x', 100)
            y = window_config.get('position_y', 100)
        elif display_mode == 'corner':
            # Bottom-right corner with margin
            x = screen_geometry.x() + screen_geometry.width() - width - 20
            y = screen_geometry.y() + screen_geometry.height() - height - 20
        else:
            # Center on screen
            x = screen_geometry.x() + (screen_geometry.width() - width) // 2
            y = screen_geometry.y() + (screen_geometry.height() - height) // 2
        
        self.setGeometry(x, y, width, height)
        
    def _load_stylesheet(self):
        """Load and apply QSS stylesheet."""
        # Get theme from config
        theme = self.config.get('appearance', {}).get('theme', 'dark')
        
        try:
            style_path = get_styles_dir() / f'{theme}.qss'
            if style_path.exists():
                with open(style_path, 'r', encoding='utf-8') as f:
                    stylesheet = f.read()
                    self.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Error loading stylesheet: {e}")
    
    def _apply_appearance_settings(self):
        """Apply appearance settings like opacity."""
        opacity = self.config.get('appearance', {}).get('opacity', 1.0)
        self.setWindowOpacity(opacity)
        
        # Update word display progress indicator visibility
        show_progress = self.config.get('appearance', {}).get('show_progress', True)
        self.word_display.set_progress_visible(show_progress)
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Central widget
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Word display widget
        self.word_display = WordDisplay()
        
        # Apply minimal mode if enabled
        minimal_mode = self.config.get('window', {}).get('minimal_mode', False)
        self.word_display.set_minimal_mode(minimal_mode)
        
        layout.addWidget(self.word_display)
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
    def _setup_timer(self):
        """Setup auto-refresh timer."""
        interval = self.config.get('behavior', {}).get('refresh_interval_seconds', 60)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_next_word)
        self.timer.start(interval * 1000)  # Convert to milliseconds
        
        # Start progress indicator
        self.word_display.start_progress(interval * 1000)
        
    def display_next_word(self):
        """Display the next word with animation."""
        # Get enabled categories from config
        enabled_categories = self.config.get('learning', {}).get('enabled_categories', ['all'])
        
        # Apply time-based filtering if enabled
        if self.config.get('behavior', {}).get('time_based_categories', False):
            from datetime import datetime
            hour = datetime.now().hour
            time_rules = self.config.get('learning', {}).get('time_rules', {})
            
            if 5 <= hour < 12:  # Morning (5 AM - 12 PM)
                time_categories = time_rules.get('morning', [])
            elif 12 <= hour < 17:  # Afternoon (12 PM - 5 PM)
                time_categories = time_rules.get('afternoon', [])
            elif 17 <= hour < 22:  # Evening (5 PM - 10 PM)
                time_categories = time_rules.get('evening', [])
            else:  # Night (10 PM - 5 AM)
                time_categories = time_rules.get('night', [])
            
            if time_categories and enabled_categories != ['all']:
                # Intersect time categories with enabled categories
                enabled_categories = list(set(enabled_categories) & set(time_categories))
                if not enabled_categories:
                    enabled_categories = time_categories
            elif time_categories:
                enabled_categories = time_categories
        
        # Select next word
        next_word = self.word_manager.select_next_word(
            self.history_tracker, 
            self.current_word_id,
            enabled_categories
        )
        
        if not next_word:
            print("No words available!")
            return
        
        # Check if animations are enabled
        enable_animations = self.config.get('appearance', {}).get('enable_animations', True)
        
        if enable_animations and self.current_word_id is not None:
            # Animate transition
            self._animate_word_transition(next_word)
        else:
            # Direct update without animation
            self._update_word(next_word)
        
        # Schedule TTS pronunciation (1.5 seconds after word change)
        if self.config.get('behavior', {}).get('auto_pronounce', False):
            if self.tts_timer:
                self.tts_timer.stop()
            self.tts_timer = QTimer()
            self.tts_timer.setSingleShot(True)
            self.tts_timer.timeout.connect(lambda: self._pronounce_word(next_word))
            self.tts_timer.start(1500)  # 1.5 second delay
    
    def _animate_word_transition(self, next_word):
        """Animate fade out, update, fade in."""
        # Fade out
        fade_out = QPropertyAnimation(self.word_display, b"windowOpacity")
        fade_out.setDuration(300)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Connect to update and fade in
        fade_out.finished.connect(lambda: self._finish_transition(next_word))
        fade_out.start()
        
        # Store animation reference to prevent garbage collection
        self._current_animation = fade_out
    
    def _finish_transition(self, next_word):
        """Complete the transition: update word and fade in."""
        # Update word
        self._update_word(next_word)
        
        # Fade in
        fade_in = QPropertyAnimation(self.word_display, b"windowOpacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.InOutQuad)
        fade_in.start()
        
        # Store animation reference
        self._current_animation = fade_in
    
    def _update_word(self, word):
        """Update the displayed word and record in history."""
        self.word_display.set_word(word)
        self.current_word_id = word['id']
        self.history_tracker.record_display(word['id'])
        
        # Track gamification progress
        self.gamification_tracker.record_word_viewed()
        self._check_daily_goal()
        
        # Restart progress indicator
        interval = self.config.get('behavior', {}).get('refresh_interval_seconds', 60)
        self.word_display.start_progress(interval * 1000)
    
    def _check_daily_goal(self):
        """Check if daily goal was reached and show notification."""
        progress = self.gamification_tracker.get_daily_progress()
        goal = self.gamification_tracker.get_daily_goal()
        streak = self.gamification_tracker.get_current_streak()
        
        # Check for daily goal
        if progress == goal:
            # Daily goal reached! Show notification
            self.notification_manager.show_daily_goal(goal, streak)
        
        # Check for streak milestones
        if progress == 1 and streak in [7, 14, 30, 50, 100, 365]:
            self.notification_manager.show_streak_milestone(streak)

        
    def _pronounce_word(self, word):
        """Pronounce the current German word."""
        volume = self.config.get('behavior', {}).get('tts_volume', 80)
        german_word = word.get('german', '')
        self.speech_engine.pronounce(german_word, volume)
    
    def _show_context_menu(self, position):
        """Show context menu on right-click."""
        menu = QMenu(self)
        
        # Statistics action
        stats_action = QAction("Statistics...", self)
        stats_action.triggered.connect(self._show_statistics)
        menu.addAction(stats_action)
        
        # Settings action
        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self._show_settings)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)
        
        menu.exec_(self.mapToGlobal(position))
    
    def _show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.config, self.word_manager, self)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.exec_()
    
    def _show_statistics(self):
        """Show statistics window."""
        if self.stats_window is None or not self.stats_window.isVisible():
            self.stats_window = StatsWindow(
                self.history_tracker, 
                self.gamification_tracker,
                self
            )
        self.stats_window.show()
    
    def _show_csv_import(self):
        """Show CSV import dialog."""
        from src.ui.csv_import_dialog import CSVImportDialog
        from src.utils.helpers import get_vocabulary_dir
        
        dialog = CSVImportDialog(get_vocabulary_dir(), self)
        dialog.exec_()
        self.stats_window.raise_()
        self.stats_window.activateWindow()
    
    def _on_settings_changed(self, new_config):
        """Handle settings changes."""
        self.config = new_config
        
        # Reload stylesheet if theme changed
        self._load_stylesheet()
        
        # Reapply appearance settings
        self._apply_appearance_settings()
        
        # Update minimal mode
        minimal_mode = self.config.get('window', {}).get('minimal_mode', False)
        self.word_display.set_minimal_mode(minimal_mode)
        
        # Restart timer with new interval
        interval = self.config.get('behavior', {}).get('refresh_interval_seconds', 60)
        self.timer.stop()
        self.timer.start(interval * 1000)
        
        # Reposition/resize window if display mode changed
        self._setup_window()
    

    
    def keyPressEvent(self, event):
        """Handle keyboard events (minimal - just pass through)."""
        super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        """Enable window dragging."""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle window dragging."""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def closeEvent(self, event):
        """Cleanup on close."""
        # Force save history
        self.history_tracker.save_history(force=True)
        
        # Save window position if enabled
        if self.config.get('window', {}).get('remember_position', False):
            geometry = self.geometry()
            self.config['window']['position_x'] = geometry.x()
            self.config['window']['position_y'] = geometry.y()
            save_json_atomic(str(get_config_path()), self.config)
        
        # Stop TTS
        if self.tts_timer:
            self.tts_timer.stop()
        self.speech_engine.stop()
        
        event.accept()
