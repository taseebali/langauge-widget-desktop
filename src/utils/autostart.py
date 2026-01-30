"""Windows autostart utilities for registry management."""

import sys
import winreg
from pathlib import Path


def get_startup_registry_key():
    """Get the Windows startup registry key."""
    return winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
    )


def is_autostart_enabled(app_name="GermanVocabularyWallpaper"):
    """
    Check if autostart is currently enabled.
    
    Args:
        app_name: Name of the registry entry
        
    Returns:
        bool: True if autostart is enabled
    """
    try:
        key = get_startup_registry_key()
        try:
            value, _ = winreg.QueryValueEx(key, app_name)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception as e:
        print(f"Error checking autostart status: {e}")
        return False


def enable_autostart(app_name="GermanVocabularyWallpaper", exe_path=None):
    """
    Enable Windows autostart by adding registry entry.
    
    Args:
        app_name: Name of the registry entry
        exe_path: Path to executable. If None, uses current Python script/exe
        
    Returns:
        bool: True if successful
    """
    try:
        if exe_path is None:
            # Get path to current executable or script
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                exe_path = sys.executable
            else:
                # Running as script - use pythonw to avoid console window
                python_exe = sys.executable.replace("python.exe", "pythonw.exe")
                if not Path(python_exe).exists():
                    python_exe = sys.executable
                
                # Get main script path
                main_script = Path(__file__).parent.parent / "main.py"
                exe_path = f'"{python_exe}" "{main_script}"'
        
        key = get_startup_registry_key()
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, str(exe_path))
        winreg.CloseKey(key)
        
        print(f"Autostart enabled: {exe_path}")
        return True
    
    except Exception as e:
        print(f"Error enabling autostart: {e}")
        return False


def disable_autostart(app_name="GermanVocabularyWallpaper"):
    """
    Disable Windows autostart by removing registry entry.
    
    Args:
        app_name: Name of the registry entry
        
    Returns:
        bool: True if successful
    """
    try:
        key = get_startup_registry_key()
        try:
            winreg.DeleteValue(key, app_name)
            print("Autostart disabled")
            success = True
        except FileNotFoundError:
            # Entry doesn't exist, consider it success
            success = True
        
        winreg.CloseKey(key)
        return success
    
    except Exception as e:
        print(f"Error disabling autostart: {e}")
        return False
