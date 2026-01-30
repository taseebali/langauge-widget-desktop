"""Settings dialog for configuring the German Wallpaper App."""

import sys
import os
import psutil
from PyQt5.QtWidgets import (QDialog, QTabWidget, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSlider, QCheckBox, 
                             QComboBox, QPushButton, QGroupBox, QSpinBox,
                             QRadioButton, QButtonGroup, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.helpers import get_config_path, save_json_atomic
from src.utils.autostart import enable_autostart, disable_autostart, is_autostart_enabled


class SettingsDialog(QDialog):
    """Settings dialog with tabs for different configuration categories."""
    
    settings_changed = pyqtSignal(dict)  # Emits new config when settings change
    
    def __init__(self, config, word_manager=None, parent=None):
        super().__init__(parent)
        self.config = config.copy()  # Work with a copy
        self.word_manager = word_manager
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)
        self._setup_ui()
        
    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Add tabs
        self.tabs.addTab(self._create_behavior_tab(), "Behavior")
        self.tabs.addTab(self._create_appearance_tab(), "Appearance")
        self.tabs.addTab(self._create_learning_tab(), "Learning")
        self.tabs.addTab(self._create_window_tab(), "Window")
        self.tabs.addTab(self._create_monitor_tab(), "Performance")
        
        layout.addWidget(self.tabs)
        
        # Setup resource monitoring timer
        self.resource_timer = QTimer(self)
        self.resource_timer.timeout.connect(self._update_resource_stats)
        self.resource_timer.start(1000)  # Update every second
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self._apply_settings)
        button_layout.addWidget(apply_button)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self._ok_clicked)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def _create_behavior_tab(self):
        """Create the Behavior settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Refresh interval
        refresh_group = QGroupBox("Auto-Refresh")
        refresh_layout = QVBoxLayout(refresh_group)
        
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Refresh interval:"))
        
        self.interval_slider = QSlider(Qt.Horizontal)
        self.interval_slider.setMinimum(30)
        self.interval_slider.setMaximum(300)
        self.interval_slider.setValue(self.config.get('behavior', {}).get('refresh_interval_seconds', 60))
        self.interval_slider.setTickPosition(QSlider.TicksBelow)
        self.interval_slider.setTickInterval(30)
        interval_layout.addWidget(self.interval_slider)
        
        self.interval_label = QLabel(f"{self.interval_slider.value()}s")
        self.interval_label.setMinimumWidth(50)
        interval_layout.addWidget(self.interval_label)
        
        self.interval_slider.valueChanged.connect(
            lambda v: self.interval_label.setText(f"{v}s")
        )
        
        refresh_layout.addLayout(interval_layout)
        layout.addWidget(refresh_group)
        
        # TTS Settings
        tts_group = QGroupBox("Text-to-Speech")
        tts_layout = QVBoxLayout(tts_group)
        
        self.auto_pronounce_checkbox = QCheckBox("Auto-pronounce words")
        self.auto_pronounce_checkbox.setChecked(
            self.config.get('behavior', {}).get('auto_pronounce', False)
        )
        tts_layout.addWidget(self.auto_pronounce_checkbox)
        
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(self.config.get('behavior', {}).get('tts_volume', 80))
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel(f"{self.volume_slider.value()}%")
        self.volume_label.setMinimumWidth(50)
        volume_layout.addWidget(self.volume_label)
        
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_label.setText(f"{v}%")
        )
        
        tts_layout.addLayout(volume_layout)
        layout.addWidget(tts_group)
        
        # Auto-start
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout(startup_group)
        
        self.autostart_checkbox = QCheckBox("Start with Windows")
        self.autostart_checkbox.setChecked(
            self.config.get('behavior', {}).get('autostart', False)
        )
        startup_layout.addWidget(self.autostart_checkbox)
        
        layout.addWidget(startup_group)
        
        # Time-based learning
        time_group = QGroupBox("Time-Based Learning")
        time_layout = QVBoxLayout(time_group)
        
        self.time_based_checkbox = QCheckBox("Adjust categories based on time of day")
        self.time_based_checkbox.setChecked(
            self.config.get('behavior', {}).get('time_based_categories', False)
        )
        time_layout.addWidget(self.time_based_checkbox)
        
        time_help = QLabel("Morning: Food/Adjectives | Afternoon: Verbs/Travel\nEvening: Animals/Body | Night: Common Words")
        time_help.setWordWrap(True)
        time_help.setStyleSheet("color: #888; font-size: 11px;")
        time_layout.addWidget(time_help)
        
        layout.addWidget(time_group)
        layout.addStretch()
        
        return widget
    
    def _create_appearance_tab(self):
        """Create the Appearance settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Theme
        theme_group = QGroupBox("Theme")
        theme_layout = QHBoxLayout(theme_group)
        theme_layout.addWidget(QLabel("Color scheme:"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        current_theme = self.config.get('appearance', {}).get('theme', 'dark')
        self.theme_combo.setCurrentText(current_theme.capitalize())
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        layout.addWidget(theme_group)
        
        # Opacity
        opacity_group = QGroupBox("Transparency")
        opacity_layout = QVBoxLayout(opacity_group)
        
        opacity_slider_layout = QHBoxLayout()
        opacity_slider_layout.addWidget(QLabel("Window opacity:"))
        
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(30)
        self.opacity_slider.setMaximum(100)
        opacity_value = int(self.config.get('appearance', {}).get('opacity', 1.0) * 100)
        self.opacity_slider.setValue(opacity_value)
        opacity_slider_layout.addWidget(self.opacity_slider)
        
        self.opacity_label = QLabel(f"{self.opacity_slider.value()}%")
        self.opacity_label.setMinimumWidth(50)
        opacity_slider_layout.addWidget(self.opacity_label)
        
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        
        opacity_layout.addLayout(opacity_slider_layout)
        layout.addWidget(opacity_group)
        
        # Animations
        animation_group = QGroupBox("Animations")
        animation_layout = QVBoxLayout(animation_group)
        
        self.animations_checkbox = QCheckBox("Enable fade animations")
        self.animations_checkbox.setChecked(
            self.config.get('appearance', {}).get('enable_animations', True)
        )
        animation_layout.addWidget(self.animations_checkbox)
        
        layout.addWidget(animation_group)
        
        # Progress Indicator
        progress_group = QGroupBox("Progress Indicator")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_checkbox = QCheckBox("Show countdown ring")
        self.progress_checkbox.setChecked(
            self.config.get('appearance', {}).get('show_progress', True)
        )
        progress_layout.addWidget(self.progress_checkbox)
        
        layout.addWidget(progress_group)
        layout.addStretch()
        
        return widget
    
    def _create_learning_tab(self):
        """Create the Learning settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Categories
        category_group = QGroupBox("Word Categories")
        category_layout = QVBoxLayout(category_group)
        category_layout.addWidget(QLabel("Enable categories:"))
        
        # Get enabled categories from config
        enabled_categories = self.config.get('learning', {}).get('enabled_categories', [])
        
        # "All Categories" checkbox
        self.category_all = QCheckBox("All Categories")
        self.category_all.setChecked('all' in enabled_categories or len(enabled_categories) == 0)
        self.category_all.stateChanged.connect(self._on_all_categories_changed)
        category_layout.addWidget(self.category_all)
        
        # Dynamic category checkboxes
        self.category_checkboxes = {}
        if self.word_manager:
            categories = self.word_manager.get_categories()
            for category in categories:
                checkbox = QCheckBox(category.title())
                checkbox.setChecked(
                    category in enabled_categories or 'all' in enabled_categories or len(enabled_categories) == 0
                )
                checkbox.stateChanged.connect(self._on_category_changed)
                category_layout.addWidget(checkbox)
                self.category_checkboxes[category] = checkbox
        
        layout.addWidget(category_group)
        
        # Difficulty
        difficulty_group = QGroupBox("Difficulty Level")
        difficulty_layout = QVBoxLayout(difficulty_group)
        difficulty_layout.addWidget(QLabel("Show words from:"))
        
        self.difficulty_a1 = QCheckBox("A1 (Beginner)")
        self.difficulty_a2 = QCheckBox("A2 (Elementary)")
        self.difficulty_b1 = QCheckBox("B1 (Intermediate)")
        
        self.difficulty_a1.setChecked(True)
        self.difficulty_a2.setChecked(True)
        self.difficulty_b1.setChecked(True)
        
        difficulty_layout.addWidget(self.difficulty_a1)
        difficulty_layout.addWidget(self.difficulty_a2)
        difficulty_layout.addWidget(self.difficulty_b1)
        
        layout.addWidget(difficulty_group)
        layout.addStretch()
        
        return widget
    
    def _create_window_tab(self):
        """Create the Window settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Display Mode
        mode_group = QGroupBox("Display Mode")
        mode_layout = QVBoxLayout(mode_group)
        
        self.mode_button_group = QButtonGroup()
        
        self.mode_floating = QRadioButton("Floating (600x400px, centered)")
        self.mode_corner = QRadioButton("Corner (200x150px, bottom-right)")
        
        current_mode = self.config.get('window', {}).get('display_mode', 'floating')
        if current_mode == 'floating':
            self.mode_floating.setChecked(True)
        else:
            self.mode_corner.setChecked(True)
        
        self.mode_button_group.addButton(self.mode_floating)
        self.mode_button_group.addButton(self.mode_corner)
        
        mode_layout.addWidget(self.mode_floating)
        mode_layout.addWidget(self.mode_corner)
        
        # Minimal mode option
        self.minimal_mode = QCheckBox("Minimal mode (show details on hover)")
        self.minimal_mode.setChecked(
            self.config.get('window', {}).get('minimal_mode', False)
        )
        mode_layout.addWidget(self.minimal_mode)
        
        layout.addWidget(mode_group)
        
        # Monitor Selection
        monitor_group = QGroupBox("Monitor")
        monitor_layout = QHBoxLayout(monitor_group)
        monitor_layout.addWidget(QLabel("Display on:"))
        
        self.monitor_combo = QComboBox()
        
        # Detect available monitors
        from PyQt5.QtWidgets import QDesktopWidget
        desktop = QDesktopWidget()
        screen_count = desktop.screenCount()
        
        for i in range(screen_count):
            geometry = desktop.screenGeometry(i)
            self.monitor_combo.addItem(
                f"Monitor {i + 1} ({geometry.width()}x{geometry.height()})",
                i
            )
        
        current_monitor = self.config.get('window', {}).get('monitor', 0)
        self.monitor_combo.setCurrentIndex(current_monitor)
        
        monitor_layout.addWidget(self.monitor_combo)
        monitor_layout.addStretch()
        
        layout.addWidget(monitor_group)
        
        # Position
        position_group = QGroupBox("Position")
        position_layout = QVBoxLayout(position_group)
        
        self.remember_position_checkbox = QCheckBox("Remember window position")
        self.remember_position_checkbox.setChecked(
            self.config.get('window', {}).get('remember_position', False)
        )
        position_layout.addWidget(self.remember_position_checkbox)
        
        layout.addWidget(position_group)
        layout.addStretch()
        
        return widget
    
    def _create_monitor_tab(self):
        """Create the Performance Monitor tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # System Resources Group
        resources_group = QGroupBox("Application Resource Usage")
        resources_layout = QVBoxLayout(resources_group)
        
        # Get current process
        self.process = psutil.Process()
        
        # CPU Usage
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("CPU Usage:"))
        self.cpu_label = QLabel("0.0%")
        self.cpu_label.setMinimumWidth(60)
        cpu_layout.addWidget(self.cpu_label)
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setMaximum(100)
        self.cpu_bar.setTextVisible(False)
        cpu_layout.addWidget(self.cpu_bar)
        resources_layout.addLayout(cpu_layout)
        
        # Memory Usage
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Memory Usage:"))
        self.memory_label = QLabel("0 MB")
        self.memory_label.setMinimumWidth(60)
        memory_layout.addWidget(self.memory_label)
        self.memory_bar = QProgressBar()
        self.memory_bar.setMaximum(500)  # 500 MB max for display
        self.memory_bar.setTextVisible(False)
        memory_layout.addWidget(self.memory_bar)
        resources_layout.addLayout(memory_layout)
        
        # Threads
        threads_layout = QHBoxLayout()
        threads_layout.addWidget(QLabel("Active Threads:"))
        self.threads_label = QLabel("0")
        threads_layout.addWidget(self.threads_label)
        threads_layout.addStretch()
        resources_layout.addLayout(threads_layout)
        
        layout.addWidget(resources_group)
        
        # System Info Group
        system_group = QGroupBox("System Information")
        system_layout = QVBoxLayout(system_group)
        
        # Total System CPU
        total_cpu_layout = QHBoxLayout()
        total_cpu_layout.addWidget(QLabel("System CPU Usage:"))
        self.total_cpu_label = QLabel("0.0%")
        total_cpu_layout.addWidget(self.total_cpu_label)
        total_cpu_layout.addStretch()
        system_layout.addLayout(total_cpu_layout)
        
        # Total System Memory
        mem_info = psutil.virtual_memory()
        total_memory_layout = QHBoxLayout()
        total_memory_layout.addWidget(QLabel("System Memory:"))
        self.total_memory_label = QLabel(
            f"{mem_info.used / (1024**3):.1f} GB / {mem_info.total / (1024**3):.1f} GB"
        )
        total_memory_layout.addWidget(self.total_memory_label)
        total_memory_layout.addStretch()
        system_layout.addLayout(total_memory_layout)
        
        layout.addWidget(system_group)
        
        # Info label
        info_label = QLabel(
            "Resource monitoring shows real-time performance metrics.\n"
            "The application is designed to be lightweight and efficient."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        return widget
    
    def _update_resource_stats(self):
        """Update resource usage statistics."""
        try:
            # CPU usage (0-100%)
            cpu_percent = self.process.cpu_percent()
            self.cpu_label.setText(f"{cpu_percent:.1f}%")
            self.cpu_bar.setValue(int(cpu_percent))
            
            # Memory usage
            mem_info = self.process.memory_info()
            mem_mb = mem_info.rss / (1024 * 1024)
            self.memory_label.setText(f"{mem_mb:.1f} MB")
            self.memory_bar.setValue(int(mem_mb))
            
            # Threads
            num_threads = self.process.num_threads()
            self.threads_label.setText(str(num_threads))
            
            # System CPU
            total_cpu = psutil.cpu_percent()
            self.total_cpu_label.setText(f"{total_cpu:.1f}%")
            
            # System Memory
            sys_mem = psutil.virtual_memory()
            self.total_memory_label.setText(
                f"{sys_mem.used / (1024**3):.1f} GB / {sys_mem.total / (1024**3):.1f} GB "
                f"({sys_mem.percent:.1f}%)"
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    def _on_all_categories_changed(self, state):
        """Handle 'All Categories' checkbox change."""
        checked = state == Qt.Checked
        for checkbox in self.category_checkboxes.values():
            checkbox.setChecked(checked)
    
    def _on_category_changed(self):
        """Handle individual category checkbox change."""
        # If all categories are checked, check "All"
        all_checked = all(cb.isChecked() for cb in self.category_checkboxes.values())
        self.category_all.setChecked(all_checked)
    
    def _apply_settings(self):
        """Apply the current settings."""
        # Update config from UI
        self.config['behavior']['refresh_interval_seconds'] = self.interval_slider.value()
        self.config['behavior']['auto_pronounce'] = self.auto_pronounce_checkbox.isChecked()
        self.config['behavior']['tts_volume'] = self.volume_slider.value()
        self.config['behavior']['autostart'] = self.autostart_checkbox.isChecked()
        self.config['behavior']['time_based_categories'] = self.time_based_checkbox.isChecked()
        
        self.config['appearance']['theme'] = self.theme_combo.currentText().lower()
        self.config['appearance']['opacity'] = self.opacity_slider.value() / 100.0
        self.config['appearance']['enable_animations'] = self.animations_checkbox.isChecked()
        self.config['appearance']['show_progress'] = self.progress_checkbox.isChecked()
        
        # Learning settings
        if self.category_all.isChecked():
            self.config['learning']['enabled_categories'] = ['all']
        else:
            enabled = [cat for cat, cb in self.category_checkboxes.items() if cb.isChecked()]
            self.config['learning']['enabled_categories'] = enabled if enabled else ['all']
        
        self.config['window']['display_mode'] = 'floating' if self.mode_floating.isChecked() else 'corner'
        self.config['window']['monitor'] = self.monitor_combo.currentData()
        self.config['window']['remember_position'] = self.remember_position_checkbox.isChecked()
        self.config['window']['minimal_mode'] = self.minimal_mode.isChecked()
        
        # Handle Windows autostart
        autostart_enabled = self.autostart_checkbox.isChecked()
        current_autostart = is_autostart_enabled()
        
        if autostart_enabled and not current_autostart:
            # Enable autostart
            if not enable_autostart():
                QMessageBox.warning(
                    self, 
                    "Autostart Failed", 
                    "Failed to enable autostart. You may need administrator privileges."
                )
                self.config['behavior']['autostart'] = False
        elif not autostart_enabled and current_autostart:
            # Disable autostart
            disable_autostart()
        
        # Save to file
        save_json_atomic(str(get_config_path()), self.config)
        
        # Emit signal
        self.settings_changed.emit(self.config)
    
    def _ok_clicked(self):
        """Handle OK button click."""
        self._apply_settings()
        self.accept()
