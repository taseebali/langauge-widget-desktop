"""Text-to-speech engine for pronouncing German words."""

import sys
import os
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class SpeechEngine:
    """Wrapper for text-to-speech with pyttsx3 and gTTS fallback."""
    
    def __init__(self):
        """Initialize the speech engine."""
        self.engine = None
        self.engine_type = None
        self._initialize_engine()
        
    def _initialize_engine(self):
        """Initialize pyttsx3 or gTTS as fallback."""
        # Try pyttsx3 first (offline, faster)
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine_type = 'pyttsx3'
            
            # Try to set German voice
            voices = self.engine.getProperty('voices')
            german_voice = None
            
            for voice in voices:
                if 'german' in voice.name.lower() or 'de' in voice.id.lower():
                    german_voice = voice.id
                    break
            
            if german_voice:
                self.engine.setProperty('voice', german_voice)
            
            print(f"TTS: Initialized pyttsx3 engine")
            
        except Exception as e:
            print(f"pyttsx3 initialization failed: {e}")
            print("Falling back to gTTS (requires internet)")
            self.engine_type = 'gtts'
    
    def set_volume(self, volume: int):
        """
        Set speech volume.
        
        Args:
            volume: Volume level 0-100
        """
        if self.engine_type == 'pyttsx3' and self.engine:
            try:
                self.engine.setProperty('volume', volume / 100.0)
            except Exception as e:
                print(f"Error setting volume: {e}")
    
    def pronounce(self, text: str, volume: int = 80):
        """
        Pronounce the given text.
        
        Args:
            text: Text to pronounce
            volume: Volume level 0-100
        """
        if not text:
            return
        
        self.set_volume(volume)
        
        if self.engine_type == 'pyttsx3' and self.engine:
            self._pronounce_pyttsx3(text)
        elif self.engine_type == 'gtts':
            self._pronounce_gtts(text)
    
    def _pronounce_pyttsx3(self, text: str):
        """Pronounce using pyttsx3."""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"pyttsx3 pronunciation error: {e}")
    
    def _pronounce_gtts(self, text: str):
        """Pronounce using gTTS (requires internet)."""
        try:
            from gtts import gTTS
            import tempfile
            import os
            
            # Create temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_path = fp.name
            
            # Generate speech
            tts = gTTS(text=text, lang='de')
            tts.save(temp_path)
            
            # Play using default player
            if os.name == 'nt':  # Windows
                os.system(f'start /min "" "{temp_path}"')
            
            # Note: We don't delete the file immediately since it's playing
            # In a production app, you'd want a cleanup mechanism
            
        except Exception as e:
            print(f"gTTS pronunciation error: {e}")
    
    def stop(self):
        """Stop current speech."""
        if self.engine_type == 'pyttsx3' and self.engine:
            try:
                self.engine.stop()
            except:
                pass
