"""Utility helper functions for the German Wallpaper App."""

import json
import os
import sys
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path


def get_resource_path(relative_path: str) -> Path:
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    
    When running as a frozen executable (PyInstaller), resources are in a temp folder.
    In development, resources are in the project directory.
    
    Args:
        relative_path: Relative path to resource (e.g., 'data/config.json')
        
    Returns:
        Absolute path to the resource
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = Path(sys._MEIPASS)
    else:
        # Running in development
        base_path = Path(__file__).parent.parent.parent
    
    result = base_path / relative_path.replace('/', os.sep)
    return result


def load_json_safe(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load JSON file safely with error handling.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Parsed JSON dict or None if file doesn't exist or is invalid
    """
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading {filepath}: {e}")
        return None


def save_json_atomic(filepath: str, data: Dict[str, Any]) -> bool:
    """
    Save JSON with atomic write to prevent corruption.
    
    Writes to temporary file first, then renames to target.
    This is atomic on most filesystems.
    
    Args:
        filepath: Target file path
        data: Dictionary to save as JSON
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write to temporary file in same directory
        temp_path = filepath + '.tmp'
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        
        # Atomic rename
        os.replace(temp_path, filepath)
        return True
        
    except (IOError, OSError) as e:
        print(f"Error saving {filepath}: {e}")
        # Clean up temp file if it exists
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return False


def validate_word_schema(word: Dict[str, Any]) -> bool:
    """
    Validate that a word dictionary has required fields.
    
    Args:
        word: Word dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['id', 'german', 'english']
    return all(field in word for field in required_fields)


def get_data_dir() -> Path:
    """Get the data directory path."""
    # In frozen executable, use user's AppData directory for writable data
    if getattr(sys, 'frozen', False):
        app_data = Path(os.getenv('APPDATA')) / 'GermanWallpaper'
        app_data.mkdir(parents=True, exist_ok=True)
        return app_data
    else:
        # Development: use project root data directory
        project_root = Path(__file__).parent.parent.parent
        return project_root / 'data'


def get_vocabulary_dir() -> Path:
    """Get the vocabulary directory path."""
    # Vocabulary is read-only and bundled with the app
    return get_resource_path('data') / 'vocabulary'


def get_styles_dir() -> Path:
    """Get the styles directory path."""
    return get_resource_path('src/ui/styles')


def get_config_path() -> Path:
    """Get the config file path."""
    return get_data_dir() / 'config.json'


def get_history_path() -> Path:
    """Get the history file path."""
    return get_data_dir() / 'history.json'


def ensure_data_files_exist():
    """Ensure default data files exist with initial values."""
    config_path = get_config_path()
    history_path = get_history_path()
    
    # Create default config if it doesn't exist
    if not config_path.exists():
        default_config = {
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
                "autostart": False
            },
            "learning": {
                "enabled_categories": ["all"],
                "difficulty_range": ["A1", "A2", "B1"]
            },
            "window": {
                "width": 600,
                "height": 400,
                "display_mode": "floating",
                "monitor": 0,
                "remember_position": False
            }
        }
        save_json_atomic(str(config_path), default_config)
    
    # Create empty history if it doesn't exist
    if not history_path.exists():
        save_json_atomic(str(history_path), {})
