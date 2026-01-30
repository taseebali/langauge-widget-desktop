"""Statistics window showing learning progress."""

import sys
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QPushButton, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.history_tracker import HistoryTracker
from src.core.gamification_tracker import GamificationTracker


class StatsWindow(QDialog):
    """Window displaying learning statistics and progress."""
    
    def __init__(self, history_tracker: HistoryTracker, gamification_tracker: GamificationTracker = None, parent=None):
        super().__init__(parent)
        self.history_tracker = history_tracker
        self.gamification_tracker = gamification_tracker
        self.setWindowTitle("Learning Statistics")
        self.setMinimumSize(500, 500)
        self._setup_ui()
        self._update_stats()
        
    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Your Learning Progress")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Statistics grid
        stats_group = QGroupBox("Overview")
        stats_layout = QGridLayout(stats_group)
        
        # Create labels
        self.total_words_label = QLabel("0")
        self.unique_words_label = QLabel("0")
        self.streak_label = QLabel("0 days")
        self.time_spent_label = QLabel("0 minutes")
        
        # Style value labels
        for label in [self.total_words_label, self.unique_words_label, 
                      self.streak_label, self.time_spent_label]:
            font = QFont()
            font.setPointSize(24)
            font.setBold(True)
            label.setFont(font)
            label.setAlignment(Qt.AlignCenter)
        
        # Add to grid
        stats_layout.addWidget(QLabel("Total Words Viewed:"), 0, 0)
        stats_layout.addWidget(self.total_words_label, 1, 0)
        
        stats_layout.addWidget(QLabel("Unique Words:"), 0, 1)
        stats_layout.addWidget(self.unique_words_label, 1, 1)
        
        stats_layout.addWidget(QLabel("Current Streak:"), 2, 0)
        stats_layout.addWidget(self.streak_label, 3, 0)
        
        stats_layout.addWidget(QLabel("Time Spent Learning:"), 2, 1)
        stats_layout.addWidget(self.time_spent_label, 3, 1)
        
        layout.addWidget(stats_group)
        
        # Gamification stats (if available)
        if self.gamification_tracker:
            gamif_group = QGroupBox("Daily Goals & Achievements")
            gamif_layout = QGridLayout(gamif_group)
            
            self.daily_progress_label = QLabel("0 / 20")
            self.daily_streak_label = QLabel("0 days")
            self.longest_streak_label = QLabel("0 days")
            
            for label in [self.daily_progress_label, self.daily_streak_label, self.longest_streak_label]:
                font = QFont()
                font.setPointSize(18)
                font.setBold(True)
                label.setFont(font)
                label.setAlignment(Qt.AlignCenter)
            
            gamif_layout.addWidget(QLabel("Today's Progress:"), 0, 0)
            gamif_layout.addWidget(self.daily_progress_label, 1, 0)
            
            gamif_layout.addWidget(QLabel("Current Streak:"), 0, 1)
            gamif_layout.addWidget(self.daily_streak_label, 1, 1)
            
            gamif_layout.addWidget(QLabel("Longest Streak:"), 2, 0)
            gamif_layout.addWidget(self.longest_streak_label, 3, 0)
            
            layout.addWidget(gamif_group)
        
        # Category breakdown
        category_group = QGroupBox("Category Breakdown")
        category_layout = QVBoxLayout(category_group)
        
        self.category_label = QLabel("No data yet")
        self.category_label.setAlignment(Qt.AlignCenter)
        category_layout.addWidget(self.category_label)
        
        layout.addWidget(category_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._update_stats)
        button_layout.addWidget(refresh_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def _update_stats(self):
        """Update statistics from history tracker."""
        history = self.history_tracker.history
        
        # Total words viewed (sum of all times_shown)
        total_views = sum(
            entry.get('times_shown', 0) 
            for entry in history.values()
        )
        self.total_words_label.setText(str(total_views))
        
        # Unique words
        unique_count = len(history)
        self.unique_words_label.setText(str(unique_count))
        
        # Calculate streak (consecutive days with activity)
        streak = self._calculate_streak()
        self.streak_label.setText(f"{streak} day{'s' if streak != 1 else ''}")
        
        # Estimate time spent (assuming 5 seconds per view)
        time_minutes = (total_views * 5) // 60
        if time_minutes >= 60:
            hours = time_minutes // 60
            mins = time_minutes % 60
            self.time_spent_label.setText(f"{hours}h {mins}m")
        else:
            self.time_spent_label.setText(f"{time_minutes} minutes")
        
        # Update gamification stats
        if self.gamification_tracker:
            progress = self.gamification_tracker.get_daily_progress()
            goal = self.gamification_tracker.get_daily_goal()
            self.daily_progress_label.setText(f"{progress} / {goal}")
            
            current_streak = self.gamification_tracker.get_current_streak()
            self.daily_streak_label.setText(f"{current_streak} day{'s' if current_streak != 1 else ''}")
            
            longest_streak = self.gamification_tracker.get_longest_streak()
            self.longest_streak_label.setText(f"{longest_streak} day{'s' if longest_streak != 1 else ''}")
        
        # Category breakdown (simplified for now)
        if unique_count > 0:
            self.category_label.setText(
                f"{unique_count} unique words learned\n"
                f"Average: {total_views / unique_count:.1f} views per word"
            )
        else:
            self.category_label.setText("Start learning to see statistics!")
    
    def _calculate_streak(self):
        """Calculate consecutive days with learning activity."""
        history = self.history_tracker.history
        
        if not history:
            return 0
        
        # Get all dates with activity
        dates = set()
        for entry in history.values():
            if 'last_shown' in entry and entry['last_shown']:
                try:
                    dt = datetime.fromisoformat(entry['last_shown'])
                    dates.add(dt.date())
                except:
                    pass
        
        if not dates:
            return 0
        
        # Sort dates
        sorted_dates = sorted(dates, reverse=True)
        
        # Calculate streak from today
        today = datetime.now().date()
        streak = 0
        
        for i, date in enumerate(sorted_dates):
            expected_date = today - timedelta(days=i)
            if date == expected_date:
                streak += 1
            else:
                break
        
        return streak
