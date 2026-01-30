"""Word display widget showing German vocabulary with glassmorphic styling."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QRectF
from PyQt5.QtGui import QFont, QPainter, QPen, QColor
from typing import Dict, Optional
import math


class WordDisplay(QWidget):
    """Widget for displaying a single German word with all its information."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WordCard")
        self.current_word = None
        self.progress_visible = True
        self.progress_value = 0.0  # 0.0 to 1.0
        self.is_minimal = False  # Minimal mode state
        self._setup_ui()
        
        # Timer for progress animation
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self._update_progress)
        
    def start_progress(self, duration_ms: int):
        """
        Start the progress countdown animation.
        
        Args:
            duration_ms: Total duration in milliseconds
        """
        self.progress_value = 0.0
        self.total_duration = duration_ms
        self.elapsed_time = 0
        self.progress_timer.start(1000)  # Update every second
        self.update()
    
    def _update_progress(self):
        """Update progress value."""
        self.elapsed_time += 1000
        self.progress_value = min(1.0, self.elapsed_time / self.total_duration)
        self.update()  # Trigger repaint
    
    def stop_progress(self):
        """Stop the progress animation."""
        self.progress_timer.stop()
        self.progress_value = 0.0
        self.update()
        
    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(10)
        
        # Top row: Gender and badges
        top_row = QHBoxLayout()
        self.gender_label = QLabel()
        self.gender_label.setObjectName("Gender")
        top_row.addWidget(self.gender_label)
        top_row.addStretch()
        
        # Category and difficulty badges
        self.category_badge = QLabel()
        self.category_badge.setObjectName("CategoryBadge")
        self.difficulty_badge = QLabel()
        self.difficulty_badge.setObjectName("DifficultyBadge")
        top_row.addWidget(self.category_badge)
        top_row.addWidget(self.difficulty_badge)
        
        layout.addLayout(top_row)
        layout.addSpacing(10)
        
        # German word (main focus)
        self.german_label = QLabel()
        self.german_label.setObjectName("GermanWord")
        self.german_label.setAlignment(Qt.AlignCenter)
        self.german_label.setWordWrap(True)
        layout.addWidget(self.german_label)
        
        # Pronunciation
        self.pronunciation_label = QLabel()
        self.pronunciation_label.setObjectName("Pronunciation")
        self.pronunciation_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.pronunciation_label)
        
        layout.addSpacing(15)
        
        # English translation
        self.english_label = QLabel()
        self.english_label.setObjectName("EnglishWord")
        self.english_label.setAlignment(Qt.AlignCenter)
        self.english_label.setWordWrap(True)
        layout.addWidget(self.english_label)
        
        layout.addSpacing(20)
        
        # Example sentences
        self.example_german = QLabel()
        self.example_german.setObjectName("ExampleGerman")
        self.example_german.setAlignment(Qt.AlignCenter)
        self.example_german.setWordWrap(True)
        layout.addWidget(self.example_german)
        
        self.example_english = QLabel()
        self.example_english.setObjectName("ExampleEnglish")
        self.example_english.setAlignment(Qt.AlignCenter)
        self.example_english.setWordWrap(True)
        layout.addWidget(self.example_english)
        
        layout.addStretch()
    
    def paintEvent(self, event):
        """Custom paint event to draw progress ring."""
        super().paintEvent(event)
        
        if not self.progress_visible or self.progress_value <= 0:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get widget dimensions
        rect = self.rect()
        
        # Draw progress ring around the border
        pen = QPen(QColor("#e94560"))
        pen.setWidth(3)
        painter.setPen(pen)
        
        # Calculate arc angle (0-360 degrees)
        # Qt uses 1/16th of a degree, starts at 3 o'clock, goes clockwise
        start_angle = 90 * 16  # Start at top (12 o'clock)
        span_angle = -int(self.progress_value * 360 * 16)  # Negative for clockwise
        
        # Draw arc with small margin from edge
        margin = 5
        arc_rect = QRectF(margin, margin, 
                         rect.width() - 2*margin, 
                         rect.height() - 2*margin)
        
        painter.drawArc(arc_rect, start_angle, span_angle)
    
    def set_progress_visible(self, visible: bool):
        """Set progress indicator visibility."""
        self.progress_visible = visible
        self.update()
        
    def set_word(self, word: Dict):
        """
        Update the display with a new word.
        
        Args:
            word: Word dictionary containing german, english, etc.
        """
        self.current_word = word
        
        # German word
        self.german_label.setText(word.get('german', ''))
        
        # Gender/Article
        gender = word.get('gender', '')
        gender_map = {
            'masculine': 'der (m)',
            'feminine': 'die (f)',
            'neuter': 'das (n)'
        }
        self.gender_label.setText(gender_map.get(gender, ''))
        
        # Set gender property for CSS styling
        self.gender_label.setProperty('gender', gender)
        self.gender_label.style().unpolish(self.gender_label)
        self.gender_label.style().polish(self.gender_label)
        
        # English translation
        self.english_label.setText(word.get('english', ''))
        
        # Pronunciation
        pronunciation = word.get('pronunciation', '')
        self.pronunciation_label.setText(f"[{pronunciation}]" if pronunciation else '')
        
        # Category and difficulty
        category = word.get('category', 'unknown')
        self.category_badge.setText(category.upper())
        
        difficulty = word.get('difficulty', 'A1')
        self.difficulty_badge.setText(difficulty)
        
        # Example sentences
        examples = word.get('examples', [])
        if examples and len(examples) > 0:
            first_example = examples[0]
            self.example_german.setText(f'"{first_example.get("german", "")}"')
            self.example_english.setText(first_example.get('english', ''))
        else:
            self.example_german.setText('')
            self.example_english.setText('')
    
    def get_current_word(self) -> Optional[Dict]:
        """Get the currently displayed word."""
        return self.current_word
    
    def fade_out(self, duration: int = 300, callback=None):
        """
        Fade out animation.
        
        Args:
            duration: Animation duration in milliseconds
            callback: Function to call when animation finishes
        """
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        if callback:
            self.animation.finished.connect(callback)
        
        self.animation.start()
    
    def fade_in(self, duration: int = 300):
        """
        Fade in animation.
        
        Args:
            duration: Animation duration in milliseconds
        """
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()
    
    def set_minimal_mode(self, minimal: bool):
        """
        Enable or disable minimal mode.
        
        Args:
            minimal: True to enable minimal mode, False to disable
        """
        self.is_minimal = minimal
        
        if minimal:
            # In minimal mode, hide details initially
            self.english_label.setGraphicsEffect(None)
            self.example_german.setGraphicsEffect(None)
            self.example_english.setGraphicsEffect(None)
            self.english_label.setVisible(False)
            self.example_german.setVisible(False)
            self.example_english.setVisible(False)
            self.pronunciation_label.setVisible(False)
        else:
            # In normal mode, show all details
            self.english_label.setVisible(True)
            self.example_german.setVisible(True)
            self.example_english.setVisible(True)
            self.pronunciation_label.setVisible(True)
    
    def enterEvent(self, event):
        """Mouse enter event - expand if in minimal mode."""
        if self.is_minimal:
            self.english_label.setVisible(True)
            self.example_german.setVisible(True)
            self.example_english.setVisible(True)
            self.pronunciation_label.setVisible(True)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Mouse leave event - collapse if in minimal mode."""
        if self.is_minimal:
            self.english_label.setVisible(False)
            self.example_german.setVisible(False)
            self.example_english.setVisible(False)
            self.pronunciation_label.setVisible(False)
        super().leaveEvent(event)
