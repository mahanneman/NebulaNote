[🇬🇧 English](README.md) | [🇮🇷 فارسی](README.fa.md)
# Nebula Note

**Modern floating note assistant & input logger**

Nebula Note is a lightweight desktop tool for fast note-taking, macro recording, and session export. It runs as a compact always-on-top window with global shortcuts, a floating triangle icon, live preview, and multi-format export.

> Author: **ma.ad.gh mahanneman**  
> Repository: [github.com/mahanneman/cosmic-keylogger](https://github.com/mahanneman/cosmic-keylogger)

---

## Features

### Note-taking
- Floating, always-on-top window with a clean dark UI
- Native typing with full Unicode support (including Persian RTL)
- Snippets system with custom templates and **Ctrl+Shift+1 / 2 / 3** (also Numpad)
- Quick inserts: separator line, date, time, bullets, log tags
- Autosave, file browser, duplicate file, open folder
- Find & replace, undo/redo, copy/cut/paste

### Recording & macros
- **Typing mode** — capture text for notes
- **Macro mode** — record keyboard + mouse (clicks / optional moves / scroll)
- Numpad keys supported
- Replay with settings: repeats, start delay, speed, rest between cycles, skip long silences
- On-screen timer during playback
- Stop with **ESC** or **Ctrl+Shift+Esc**

### Floating icon
- Draggable triangle icon
- Left-click → restore main window
- Right-click menu: record, save, snippets, export, replay, help, settings

### Live Preview
- Always-on-top mini window
- Auto-scrolls to the **newest** lines

### Export formats
| Format | Use |
|--------|-----|
| JSON / JSONL | Full event data |
| Excel (.xlsx) | Spreadsheet analysis |
| CSV | Universal tables |
| HTML | Shareable report |
| Markdown | Documentation |
| Plain text | Characters only |
| Python + **.bat** | One-click run (asks for cycles / delay / speed) |
| AutoHotkey (.ahk) | Run without Python (if AHK installed) |
| PowerShell (.ps1) | Windows scripting |
| Session summary | Stats & top keys |
| Encrypted JSON | XOR-protected export |

### Other
- Multi-language UI: Persian, English, Arabic, German, French
- System tray, settings persistence (`settings.json`)
- Confirm before mode switch / exit (optional save)
- Crash log under `~/CosmicKeylogger/`

---

## Requirements

- **Python 3.8+**
- Windows recommended (global hotkeys & tray tested primarily on Windows)

```bash
pip install pynput pystray Pillow pandas openpyxl
```

Or:

```bash
py -m pip install pynput pystray Pillow pandas openpyxl
```

---

## Run

```bash
py NebulaNote_Final.py
```

If global hotkeys do not register, run the terminal **as Administrator**.

---

## Main shortcuts

All shortcuts use **Ctrl+Shift** unless noted.

| Shortcut | Action |
|----------|--------|
| **Q** | Start / stop recording |
| **W** | Save |
| **E** | Switch Typing ↔ Macro |
| **A** | Always on top |
| **Z** | Replay |
| **X** | Float (triangle icon) |
| **C** | Clear |
| **S** | Snippets manager |
| **F** | Files |
| **G** | Export |
| **H** | Help |
| **K** | Settings |
| **1 / 2 / 3** | Quick snippet slots |
| **Ctrl+1 … 9** | Quick inserts (line, date, time, …) when window focused |
| **ESC** | Stop macro playback |

---

## Data location

```
~/CosmicKeylogger/
  ├── settings.json
  ├── crash.log
  └── notes / exports (default)
```

Sessions are archived when you start a new recording so previous text is not lost.

---

## Privacy & ethics

This tool can record keyboard and mouse input **while recording is active**. Use it only on machines and accounts you own, and only for legitimate personal productivity, testing, or accessibility purposes. Do not use it to capture other people’s data without consent.

---

## License

Use and modify for personal and educational purposes. Attribution to **ma.ad.gh mahanneman** is appreciated.

---

## Persian documentation

See **[README.FA.md](README.FA.md)** for the full Persian guide.
