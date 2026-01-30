"""Gamification tracker for daily goals, streaks, and achievements."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class GamificationTracker:
    """Track learning progress, achievements, and daily goals."""
    
    def __init__(self, data_file: Path):
        """
        Initialize gamification tracker.
        
        Args:
            data_file: Path to gamification data JSON file
        """
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load gamification data from file."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading gamification data: {e}")
        
        # Default data structure
        return {
            "daily_goal": 20,  # Words per day
            "current_streak": 0,
            "longest_streak": 0,
            "total_words_learned": 0,
            "total_study_days": 0,
            "achievements": [],
            "daily_progress": {},  # {date: word_count}
            "last_activity_date": None
        }
    
    def save_data(self):
        """Save gamification data to file."""
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving gamification data: {e}")
    
    def record_word_viewed(self):
        """Record that a word was viewed today."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Update daily progress
        if today not in self.data['daily_progress']:
            self.data['daily_progress'][today] = 0
        
        self.data['daily_progress'][today] += 1
        self.data['total_words_learned'] += 1
        
        # Update streak
        self._update_streak(today)
        
        # Check achievements
        self._check_achievements()
        
        self.save_data()
    
    def _update_streak(self, today: str):
        """Update current streak based on activity."""
        last_activity = self.data.get('last_activity_date')
        
        if last_activity is None:
            # First activity
            self.data['current_streak'] = 1
            self.data['total_study_days'] = 1
        elif last_activity == today:
            # Same day, no streak change
            pass
        else:
            # Check if yesterday
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            if last_activity == yesterday:
                # Consecutive day
                self.data['current_streak'] += 1
                self.data['total_study_days'] += 1
            else:
                # Streak broken
                self.data['current_streak'] = 1
                self.data['total_study_days'] += 1
        
        # Update longest streak
        if self.data['current_streak'] > self.data['longest_streak']:
            self.data['longest_streak'] = self.data['current_streak']
        
        self.data['last_activity_date'] = today
    
    def _check_achievements(self):
        """Check and award new achievements."""
        achievements = self.data.get('achievements', [])
        new_achievements = []
        
        # Streak achievements
        if self.data['current_streak'] >= 7 and '7_day_streak' not in achievements:
            new_achievements.append('7_day_streak')
        if self.data['current_streak'] >= 30 and '30_day_streak' not in achievements:
            new_achievements.append('30_day_streak')
        if self.data['current_streak'] >= 100 and '100_day_streak' not in achievements:
            new_achievements.append('100_day_streak')
        
        # Word count achievements
        if self.data['total_words_learned'] >= 100 and '100_words' not in achievements:
            new_achievements.append('100_words')
        if self.data['total_words_learned'] >= 500 and '500_words' not in achievements:
            new_achievements.append('500_words')
        if self.data['total_words_learned'] >= 1000 and '1000_words' not in achievements:
            new_achievements.append('1000_words')
        
        # Daily goal achievements
        today = datetime.now().strftime("%Y-%m-%d")
        if today in self.data['daily_progress']:
            words_today = self.data['daily_progress'][today]
            if words_today >= self.data['daily_goal'] and f'daily_goal_{today}' not in achievements:
                new_achievements.append(f'daily_goal_{today}')
        
        # Add new achievements
        for achievement in new_achievements:
            if achievement not in achievements:
                achievements.append(achievement)
        
        self.data['achievements'] = achievements
        return new_achievements
    
    def get_daily_progress(self) -> int:
        """Get progress towards today's goal."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.data['daily_progress'].get(today, 0)
    
    def get_daily_goal(self) -> int:
        """Get daily word goal."""
        return self.data.get('daily_goal', 20)
    
    def set_daily_goal(self, goal: int):
        """Set daily word goal."""
        self.data['daily_goal'] = goal
        self.save_data()
    
    def get_current_streak(self) -> int:
        """Get current consecutive day streak."""
        return self.data.get('current_streak', 0)
    
    def get_longest_streak(self) -> int:
        """Get longest ever streak."""
        return self.data.get('longest_streak', 0)
    
    def get_total_words(self) -> int:
        """Get total words learned."""
        return self.data.get('total_words_learned', 0)
    
    def get_achievements(self) -> List[str]:
        """Get list of earned achievements."""
        return self.data.get('achievements', [])
    
    def get_achievement_name(self, achievement_id: str) -> str:
        """Get human-readable achievement name."""
        achievement_names = {
            '7_day_streak': '🔥 Week Warrior - 7 day streak!',
            '30_day_streak': '🔥 Monthly Master - 30 day streak!',
            '100_day_streak': '🔥 Century Streak - 100 days!',
            '100_words': '📚 First Hundred - 100 words learned',
            '500_words': '📚 Half Thousand - 500 words learned',
            '1000_words': '📚 Thousand Club - 1000 words learned'
        }
        
        if achievement_id.startswith('daily_goal_'):
            return '⭐ Daily Goal Complete!'
        
        return achievement_names.get(achievement_id, achievement_id)
