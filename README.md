# 🇩🇪 German Vocabulary Wallpaper

Beautiful desktop app for passive German learning. Auto-refreshing vocabulary cards with a stunning glassmorphic UI.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-red.svg)

## ✨ Features

### Core Learning
- 🎨 **Gorgeous Glassmorphic Design** - Modern, translucent UI that looks beautiful on your desktop
- 📚 **120+ German Words** - 5 categories: food, travel, body parts, verbs, adjectives
- 🎨 **Gender Color Coding** - Visual learning aid (Blue=der, Pink=die, Green=das)
- ⏱️ **Simple Auto-Refresh** - Words automatically change every 60 seconds (customizable 30s-5min)
- 🧠 **Adaptive Learning** - Prioritizes words you haven't seen recently using weighted selection
- 🖥️ **Desktop Widget** - Stays centered on your desktop, doesn't overlay other apps

### Advanced Features
- 🎤 **Text-to-Speech** - Auto-pronunciation with pyttsx3 (offline) + gTTS fallback
- 📊 **Daily Goals & Gamification** - Track progress, earn achievements, maintain streaks
- 🏆 **Achievement System** - Unlock badges for 7/30/100 day streaks, word milestones
- 🔔 **Windows Notifications** - Toast notifications for goals and achievements
- ⏰ **Time-Based Learning** - Different categories shown at different times of day
- 📁 **CSV Import** - Easily import custom vocabulary from CSV files
- 🎯 **Category Filtering** - Show only selected categories (dynamically loaded)
- 🔍 **Minimal Mode** - Compact view with hover-to-expand details

### Customization
- 🌓 **Theme Support** - Dark and Light themes with smooth transitions
- 💎 **Opacity Control** - Adjust transparency (30%-100%) to match your desktop
- 🖥️ **Multi-Monitor Support** - Choose which monitor to display on
- 📐 **Display Modes** - Floating (600x400) or Corner (200x150) with position memory
- ⏰ **Progress Indicator** - Optional visual countdown ring (disabled by default)
- 🚀 **Windows Autostart** - Launch automatically on Windows startup

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Windows OS (tested on Windows 10/11)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/german-wallpaper-app.git
   cd german-wallpaper-app
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   python src/main.py
   ```

The app will appear **centered on your screen** and automatically cycle through German vocabulary every 60 seconds.

## ⚙️ Settings

Right-click the window or use the system tray icon to access **Settings**:
Settings, Statistics, or Exit
- **System tray icon** (pink dot) provides quick access:
  - Show/Hide window
  - Statistics dashboard
  - Settings dialog
  - Mute/Unmute audio
  - Exit
- **Double-click tray icon** to show/hide the window
- Just let it run - words auto-refresh with smooth animations

## 🎤 Audio Pronunciation

Enable **Auto-Pronounce** in settings to hear each German word:
- Pronunciation starts 1.5 seconds after word appears (gives you time to read first)
- Uses offline pyttsx3 engine (or gTTS as fallback)
- Adjustable volume from system tray or settings
- Quick mute toggle in system tray menu
- **Volume**: Adjust TTS volume (0-100%)
- **Start with Windows**: Auto-launch on system startup

### Appearance Tab
- **Theme**: Dark or Light mode
- **Opacity**: Window transparency (30%-100%)
- **Animations**: Enable/disable fade transitions
- **Progress Ring**: Show/hide countdown indicator

### Learning Tab
- **Categories**: Filter by Animals, Common Words, etc.
- **Difficulty**: Choose A1 (Beginner), A2, B1 levels

### Window Tab
- **Display Mode**: Floating (centered) or Corner (bottom-right)
- **Monitor**: Select which monitor to display on (multi-monitor setup)
- **Remember Position**: Save window position between sessions

## 📊 Statistics

Access **Statistics** from the context menu or system tray to see:
- Total words viewed
- Unique words learned
- Current learning streak (consecutive days)
- Estimated time spent learning
- Category breakdown

## 🖱️ Using the App

- **Left-click and drag** to move the window anywhere on your desktop
- **Right-click** for exit option
- **System tray icon** (pink dot) provides show/hide controls
- **Double-click tray icon** to show/hide the window
- Just let it run - words auto-refresh every 60 seconds for passive learning

## 📊 How It Works

### Intelligent Word Selection

The app uses a sophisticated weighted algorithm to decide which word to show next:

```
Weight = (hours_since_shown + 1)² / (times_shown + 1)
```

**Multipliers:**
- Never shown: **2.0x** (high priority)
- Recently shown: Lower weight (avoids repetition)

This ensures you see new words frequently and recently shown words less often, creating an effective passive learning experience.

### Data Persistence

All your viewing history is automatically saved to [data/history.json](data/history.json).

## 📁 Project Structure

```
german-wallpaper-app/
├── src/
│   ├── main.py              # Application entry point
│   ├── ui/
│   │   ├── main_window.py   # Main window with glassmorphic design
│   │   ├── word_display.py  # Word card widget
│   │   ├── system_tray.py   # System tray integration
│   │   └── styles/
│   │       └── dark.qss     # Glassmorphic stylesheet
│   ├── core/
│   │   ├── word_manager.py     # Vocabulary loading & selection
│   │   └── history_tracker.py  # Learning progress tracking
│   └── utils/
│       └── helpers.py       # Utility functions
├── data/
│   ├── vocabulary/
│   │   ├── animals.json     # Animal vocabulary
│   │   └── core_1000.json   # Common words
│   ├── history.json         # Your learning history (auto-generated)
│   └── config.json          # App configuration (auto-generated)
└── requirements.txt
```

## 🎓 Adding Your Own Vocabulary

Create a new JSON file in `data/vocabulary/`:

```json
{
  "words": [
    {
      "id": 201,
      "german": "das Beispiel",
      "english": "example",
      "gender": "neuter",
      "pronunciation": "dass BY-shpeel",
      "category": "common",
      "difficulty": "A2",
      "examples": [
        {
          "german": "Das ist ein gutes Beispiel.",
          "english": "This is a good example."
        }
Open Settings → Behavior tab, or edit `data/config.json`:
```json
{
  "behavior": {
    "refresh_interval_seconds": 120
  }
}
```

### Switch to Light Theme

Settings → Appearance tab → Theme: "Light"

### Enable Corner Mode

Settings → Window tab → Display Mode: "Corner (200x150px, bottom-right)"

### Disable Animations

Settings → Appearance tab → Uncheck "Enable fade animations"

### Multi-Monitor Setup

Settings → Window tab → Monitor dropdown → Select your preferred display "refresh_interval_seconds": 120
  }
}
```

### Disable Animations

```json
{
  "appearance": {
    "enable_animations": false
  }
}
```

## 🐛 Troubleshooting

### App won't start
- Ensure Python 3.9+ is installed: `python --version`
- Verify dependencies: `pip install -r requirements.txt`
- Check for error messages in the console

### Words not showing
- Ensure vocabulary files exist in `data/vocabulary/`
- Check JSON syntax with a validator
- Review console output for loading errors

### Window positioning issues
- Delete `data/config.json` to reset window position
- Ensure your monitor resolution hasn't changed

## 🛠️ Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
This project follows PEP 8 guidelines. Format code with:
```bash
black src/
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📝 License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyQt5** - For the excellent GUI framework
- **German learners worldwide** - For inspiring this project
- **Open-source community** - For making projects like this possible

## 📮 Contact

Have questions or suggestions? Open an issue on GitHub!

---

**Made with ❤️ for German learners**
