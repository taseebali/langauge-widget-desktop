# German Wallpaper Thing

Got bored one weekend trying to learn German. Made a floaty desktop widget that shows random German words. It's actually kinda helpful?

## What it does

- Shows German words on your desktop with English translations
- Color-coded by gender (blue/pink/green for der/die/das)
- Auto-refreshes every 60 seconds
- Can pronounce words out loud (sometimes works, sometimes doesn't)
- Tracks what you've seen so you don't get repeats too often
- Dark theme because obviously

## Running it

```bash
pip install -r requirements.txt
python src/main.py
```

Right-click to quit. That's it.

## Features I added because why not

- System tray icon (pink dot in your taskbar)
- Stats tracking (streak counter and stuff)
- CSV import if you want to add your own words
- Corner mode for a tiny version
- Auto-start with Windows option
- Achievement badges (yeah I got carried away)

## How to use

Just let it sit there. You'll learn words passively. Or not. No pressure.

Drag it around, right-click for settings, double-click the tray icon to hide/show.

## Files

- `src/` - All the Python code
- `data/vocabulary/` - Word lists (120+ words across animals, food, verbs, etc.)
- `data/history.json` - Tracks what you've seen
- `data/config.json` - Your settings

## License

GPL-3.0 I guess
