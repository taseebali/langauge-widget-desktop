"""
Build script to create standalone executable for German Wallpaper App.
Run this script to generate the .exe file.
"""

import PyInstaller.__main__
import os
import shutil
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent

# Clean previous builds
dist_dir = project_root / 'dist'
build_dir = project_root / 'build'

print("Cleaning previous builds...")
if dist_dir.exists():
    shutil.rmtree(dist_dir)
if build_dir.exists():
    shutil.rmtree(build_dir)

# Data files to include
data_files = [
    (str(project_root / 'data'), 'data'),
    (str(project_root / 'assets'), 'assets'),
]

# Hidden imports needed
hidden_imports = [
    'pyttsx3.drivers',
    'pyttsx3.drivers.sapi5',
    'win32com',
    'win32com.client',
    'gtts',
    'qtawesome',
    'pyqtgraph',
    'win10toast',
    'psutil',
]

# Build the executable
print("\nBuilding executable...")
print("This may take a few minutes...\n")

# Build arguments list
args = [
    str(project_root / 'src' / 'main.py'),
    '--name=GermanWallpaper',
    '--onefile',
    '--windowed',
    f'--add-data={project_root / "data"}{os.pathsep}data',
    '--hidden-import=pyttsx3.drivers',
    '--hidden-import=pyttsx3.drivers.sapi5',
    '--hidden-import=win32com.client',
    '--hidden-import=gtts',
    '--hidden-import=qtawesome',
    '--hidden-import=pyqtgraph',
    '--hidden-import=win10toast',
    '--hidden-import=psutil',
    '--collect-all=pyttsx3',
    '--collect-all=gtts',
    '--noconfirm',
    '--clean',
]

# Add optional icon if it exists
if (project_root / 'assets' / 'icon.ico').exists():
    args.append(f'--icon={project_root / "assets" / "icon.ico"}')

# Add optional assets folder
if (project_root / 'assets').exists():
    args.append(f'--add-data={project_root / "assets"}{os.pathsep}assets')

PyInstaller.__main__.run(args)

print("\n" + "="*60)
print("Build complete!")
print("="*60)
print(f"\nExecutable location: {dist_dir / 'GermanWallpaper.exe'}")
print("\nYou can now:")
print("1. Run the executable directly from the dist folder")
print("2. Enable autostart from Settings > Behavior > Start with Windows")
print("3. Move the .exe to any location (it will create data folders automatically)")
print("\nNote: The executable includes all necessary files and dependencies.")
print("="*60)
