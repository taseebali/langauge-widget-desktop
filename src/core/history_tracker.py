"""History tracker for managing word display history."""

from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.helpers import load_json_safe, save_json_atomic, get_history_path


class HistoryTracker:
    """Tracks when and how often words have been displayed."""
    
    def __init__(self, history_path: Optional[Path] = None):
        """
        Initialize history tracker.
        
        Args:
            history_path: Path to history JSON file. If None, uses default.
        """
        self.history_path = history_path or get_history_path()
        self.history = self._load_history()
        self.save_counter = 0  # For debounced saves
        
    def _load_history(self) -> Dict:
        """Load history from JSON file."""
        data = load_json_safe(str(self.history_path))
        return data if data is not None else {}
    
    def save_history(self, force: bool = False):
        """
        Save history to JSON file.
        
        Args:
            force: If True, always save. If False, only save every 5 updates.
        """
        if force:
            save_json_atomic(str(self.history_path), self.history)
            self.save_counter = 0
        else:
            self.save_counter += 1
            if self.save_counter >= 5:
                save_json_atomic(str(self.history_path), self.history)
                self.save_counter = 0
    
    def record_display(self, word_id: int):
        """
        Record that a word was displayed.
        
        Args:
            word_id: ID of the word that was displayed
        """
        word_key = str(word_id)
        
        if word_key not in self.history:
            self.history[word_key] = {
                'times_shown': 0,
                'last_shown': None,
                'first_shown': datetime.now().isoformat()
            }
        
        self.history[word_key]['times_shown'] += 1
        self.history[word_key]['last_shown'] = datetime.now().isoformat()
        
        # Debounced save
        self.save_history(force=False)
    
    def get_word_history(self, word_id: int) -> Optional[Dict]:
        """
        Get history for a specific word.
        
        Args:
            word_id: ID of the word
            
        Returns:
            Dictionary with times_shown, last_shown, first_shown or None
        """
        return self.history.get(str(word_id))
    
    def get_hours_since_shown(self, word_id: int) -> Optional[float]:
        """
        Get hours since word was last shown.
        
        Args:
            word_id: ID of the word
            
        Returns:
            Hours since last shown, or None if never shown
        """
        word_history = self.get_word_history(word_id)
        if not word_history or not word_history.get('last_shown'):
            return None
        
        last_shown = datetime.fromisoformat(word_history['last_shown'])
        hours = (datetime.now() - last_shown).total_seconds() / 3600
        return hours
    
    def get_times_shown(self, word_id: int) -> int:
        """
        Get number of times word has been shown.
        
        Args:
            word_id: ID of the word
            
        Returns:
            Number of times shown (0 if never shown)
        """
        word_history = self.get_word_history(word_id)
        return word_history['times_shown'] if word_history else 0
    
    def mark_known(self, word_id: int):
        """Mark a word as known by the user."""
        word_key = str(word_id)
        if word_key not in self.history:
            self.history[word_key] = {
                'times_shown': 0,
                'last_shown': None,
                'first_shown': datetime.now().isoformat()
            }
        self.history[word_key]['marked_known'] = True
        self.history[word_key]['marked_difficult'] = False
        self.save_history(force=True)
    
    def mark_difficult(self, word_id: int):
        """Mark a word as difficult for the user."""
        word_key = str(word_id)
        if word_key not in self.history:
            self.history[word_key] = {
                'times_shown': 0,
                'last_shown': None,
                'first_shown': datetime.now().isoformat()
            }
        self.history[word_key]['marked_difficult'] = True
        self.history[word_key]['marked_known'] = False
        self.save_history(force=True)
    
    def is_marked_known(self, word_id: int) -> bool:
        """Check if word is marked as known."""
        word_history = self.get_word_history(word_id)
        return word_history.get('marked_known', False) if word_history else False
    
    def is_marked_difficult(self, word_id: int) -> bool:
        """Check if word is marked as difficult."""
        word_history = self.get_word_history(word_id)
        return word_history.get('marked_difficult', False) if word_history else False
    
    def cleanup_old_entries(self, max_entries: int = 1000):
        """
        Remove oldest entries to keep history size manageable.
        
        Args:
            max_entries: Maximum number of entries to keep
        """
        if len(self.history) <= max_entries:
            return
        
        # Sort by last_shown date, keep most recent
        sorted_items = sorted(
            self.history.items(),
            key=lambda x: x[1].get('last_shown', ''),
            reverse=True
        )
        
        self.history = dict(sorted_items[:max_entries])
        self.save_history(force=True)
