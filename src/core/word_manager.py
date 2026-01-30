"""Word manager for loading and selecting vocabulary."""

import random
from typing import Dict, List, Optional
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.helpers import load_json_safe, validate_word_schema, get_vocabulary_dir
from src.core.history_tracker import HistoryTracker


class WordManager:
    """Manages vocabulary loading, selection, and weighting."""
    
    def __init__(self, vocab_dir: Optional[Path] = None):
        """
        Initialize word manager.
        
        Args:
            vocab_dir: Path to vocabulary directory. If None, uses default.
        """
        self.vocab_dir = vocab_dir or get_vocabulary_dir()
        self.words: List[Dict] = []
        self.word_index: Dict[int, Dict] = {}
        self._load_vocabulary()
        
    def _load_vocabulary(self):
        """Load all vocabulary JSON files from vocab_dir."""
        if not self.vocab_dir.exists():
            print(f"Vocabulary directory not found: {self.vocab_dir}")
            return
        
        # Load all JSON files in vocabulary directory
        for json_file in self.vocab_dir.glob('*.json'):
            data = load_json_safe(str(json_file))
            if data and 'words' in data:
                # Validate and add words
                for word in data['words']:
                    if validate_word_schema(word):
                        self.words.append(word)
                        self.word_index[word['id']] = word
                    else:
                        print(f"Invalid word schema in {json_file}: {word}")
        
        print(f"Loaded {len(self.words)} words from {self.vocab_dir}")
    
    def get_word_by_id(self, word_id: int) -> Optional[Dict]:
        """
        Get word by ID.
        
        Args:
            word_id: Word ID
            
        Returns:
            Word dictionary or None if not found
        """
        return self.word_index.get(word_id)
    
    def get_all_words(self) -> List[Dict]:
        """Get all loaded words."""
        return self.words
    
    def calculate_word_weight(self, word: Dict, history_tracker: HistoryTracker, 
                             current_id: Optional[int] = None) -> float:
        """
        Calculate selection weight for a word based on display history.
        
        Formula: (hours_since_shown + 1)^2 / (times_shown + 1)
        Multipliers:
        - Never shown: 2x
        - Marked difficult: 1.5x
        - Marked known: 0.3x
        - Current word: 0 (excluded)
        
        Args:
            word: Word dictionary
            history_tracker: HistoryTracker instance
            current_id: ID of currently displayed word (to exclude)
            
        Returns:
            Selection weight (higher = more likely to be selected)
        """
        word_id = word['id']
        
        # Never select the current word
        if current_id is not None and word_id == current_id:
            return 0.0
        
        # Get history data
        hours_since = history_tracker.get_hours_since_shown(word_id)
        times_shown = history_tracker.get_times_shown(word_id)
        
        # If never shown, use large base value
        if hours_since is None:
            hours_since = 1000
        
        # Base weight calculation: time decay / frequency
        base_weight = ((hours_since + 1) ** 2) / (times_shown + 1)
        
        # Apply user multipliers
        multiplier = 1.0
        
        if times_shown == 0:
            # Never shown - prioritize
            multiplier = 2.0
        elif history_tracker.is_marked_difficult(word_id):
            # Difficult - show more often
            multiplier = 1.5
        elif history_tracker.is_marked_known(word_id):
            # Known - show less often
            multiplier = 0.3
        
        return base_weight * multiplier
    
    def select_next_word(self, history_tracker: HistoryTracker, 
                        current_id: Optional[int] = None,
                        enabled_categories: Optional[List[str]] = None) -> Optional[Dict]:
        """
        Select next word using weighted random selection.
        
        Args:
            history_tracker: HistoryTracker instance
            current_id: ID of currently displayed word (to exclude)
            enabled_categories: List of enabled categories (None or ['all'] = all categories)
            
        Returns:
            Selected word dictionary or None if no words available
        """
        if not self.words:
            return None
        
        # Filter by categories
        candidate_pool = self.words
        if enabled_categories and 'all' not in enabled_categories and len(enabled_categories) > 0:
            candidate_pool = [w for w in self.words if w.get('category') in enabled_categories]
        
        if not candidate_pool:
            # No words in enabled categories, fallback to all
            candidate_pool = self.words
        
        # Calculate weights for all words
        weights = []
        candidates = []
        
        for word in candidate_pool:
            weight = self.calculate_word_weight(word, history_tracker, current_id)
            if weight > 0:  # Only include words with positive weight
                weights.append(weight)
                candidates.append(word)
        
        if not candidates:
            # Fallback: if all weights are 0, just pick random (shouldn't happen)
            return random.choice(candidate_pool)
        
        # Weighted random selection
        selected_word = random.choices(candidates, weights=weights, k=1)[0]
        return selected_word
    
    def get_words_by_category(self, category: str) -> List[Dict]:
        """
        Get all words in a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of words in that category
        """
        return [w for w in self.words if w.get('category') == category]
    
    def get_categories(self) -> List[str]:
        """Get list of all unique categories."""
        categories = set()
        for word in self.words:
            if 'category' in word:
                categories.add(word['category'])
        return sorted(list(categories))
