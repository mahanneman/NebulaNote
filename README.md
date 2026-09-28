[🇬🇧 English](README.md) | [🇮🇷 فارسی](README.FA.md)

# Nebula Note

**Modern floating note assistant & input logger**

Nebula Note is a lightweight desktop tool for fast note-taking, macro recording, and session export. It runs as a compact always-on-top window with global shortcuts, a floating triangle icon, live preview, and multi-format export.

> **Author:** ma.ad.gh mahanneman  
> **Repository:** [https://github.com/mahanneman/NebulaNote](https://github.com/mahanneman/NebulaNote)

---

## Table of contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Run](#run)
- [Main shortcuts](#main-shortcuts)
- [How to use](#how-to-use)
- [Export formats](#export-formats)
- [Settings & files](#settings--files)
- [Troubleshooting](#troubleshooting)
- [Privacy & ethics](#privacy--ethics)
- [License](#license)
- [Persian documentation](#persian-documentation)

---

## Features

### Note-taking
- Floating, always-on-top window with a clean dark UI
- Native typing with full Unicode support (including Persian RTL)
- Snippets system with custom templates and **Ctrl+Shift+1 / 2 / 3** (also Numpad)
- Quick inserts: separator line, date, time, bullets, log tags (**Ctrl+1 … 9** when the window is focused)
- Autosave, file browser, duplicate file, open folder
- Find & replace, undo/redo, copy/cut/paste
- Confirm before mode switch or exit so you do not lose work by accident

### Recording & macros
- **Typing mode** — write notes normally (Windows keyboard layout is respected)
- **Macro mode** — record keyboard + mouse (clicks / optional move tracking / scroll)
- Numpad keys supported
- Replay dialog: repeats, start delay, speed, rest between cycles, skip long silences, max duration
- On-screen timer during playback
- Stop with **ESC** or **Ctrl+Shift+Esc** (including during the start countdown)
- Starting a new recording archives the previous session so older text is kept

### Floating icon
- Draggable triangle icon
- Left-click → restore the main window (works even if a dialog was open)
- Right-click menu: record, save, snippets, line/date/time, export, replay, help, settings

### Live Preview
- Always-on-top mini window
- Auto-scrolls to the **newest** lines

### Other
- Multi-language UI: Persian, English, Arabic, German, French
- System tray menu
- Settings saved to `settings.json`
- Crash log for debugging unexpected exits

---

## Requirements

### System
| Item | Detail |
|------|--------|
| OS | **Windows 10/11** recommended (global hotkeys, tray, `.bat` one-click run) |
| Python | **3.8 or newer** (3.10+ recommended) |
| Display | Any resolution; window is compact and resizable |
| Permissions | For reliable global hotkeys, run as **Administrator** if needed |

### Python packages

| Package | Why it is needed |
|---------|------------------|
| `pynput` | Keyboard / mouse capture and global hotkeys |
| `pystray` | System tray icon |
| `Pillow` | Tray / icon images |
| `pandas` | Excel export |
| `openpyxl` | `.xlsx` writer used by pandas |

Optional (only if you use certain exports on other machines):
- **AutoHotkey** — only if you export and run `.ahk` scripts
- **PowerShell** — built into Windows for `.ps1` exports

---

## Installation

1. Install [Python](https://www.python.org/downloads/) and enable **Add Python to PATH**.
2. Open PowerShell or Command Prompt:

```bash
py -m pip install --upgrade pip
py -m pip install pynput pystray Pillow pandas openpyxl
```

Equivalent with `pip` if that is what your system uses:

```bash
pip install pynput pystray Pillow pandas openpyxl
```

3. Download or clone this repository, then place `NebulaNote_Final.py` (or the version file you use) in a folder of your choice.

---

## Run

```bash
py NebulaNote_Final.py
```

If your file uses another name (for example a versioned release):

```bash
py NebulaNote_Final.py
```

**Tips**
- If global shortcuts do not work, open the terminal **as Administrator** and run again.
- First run may create config/log files under your user profile folder.
- Keep the window focused when using **Ctrl+1 … 9** quick inserts (local shortcuts).

---

## Main shortcuts

Primary shortcuts use **Ctrl+Shift** unless noted.

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
| **1 / 2 / 3** | Quick snippet slots (also Numpad with Ctrl+Shift) |
| **Ctrl+1 … 9** | Quick inserts (line, date, time, …) when the window is focused |
| **ESC** | Stop macro playback |

---

## How to use

1. **Notes** — type in the main box; use snippets and quick inserts as needed.
2. **Macro** — switch to Macro mode, press Start, perform actions, press Stop.
3. **Replay** — open Replay, set cycles / delay / speed / rest, press Start; use ESC to abort.
4. **One-click macro file** — Export → Python double-click → run the generated `.bat` (settings dialog opens first).
5. **Float** — Ctrl+Shift+X or the triangle button; click the triangle to return.

---

## Export formats

| Format | Use |
|--------|-----|
| JSON / JSONL | Full event data |
| Excel (`.xlsx`) | Spreadsheet analysis |
| CSV | Universal tables |
| HTML | Shareable report |
| Markdown | Documentation |
| Plain text | Characters only |
| Python + **`.bat`** | One-click run (asks for cycles / delay / speed) |
| AutoHotkey (`.ahk`) | Run without Python (if AHK is installed) |
| PowerShell (`.ps1`) | Windows scripting |
| Session summary | Stats and top keys |
| Encrypted JSON | Password-protected export |

---

## Settings & files

- App settings are stored in **`settings.json`** (created automatically on first run).
- Crash information is written to a log file if something fails unexpectedly.
- Notes and exports are saved where you choose in the save/export dialogs, or to the app’s default notes folder.

You can open the notes folder from the **Files** dialog inside the app.

---

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| Shortcuts do nothing | Run as Administrator; close apps that capture the same hotkeys |
| Persian / English mix-up while typing | Switch Windows layout with **Win+Space**, then click inside the text box |
| Triangle does not restore the window | Right-click the icon → Open / Restore; close blocking dialogs |
| `.bat` macro does not start | Install Python and ensure `py` or `python` is on PATH |
| Missing package error | Re-run `py -m pip install pynput pystray Pillow pandas openpyxl` |

---

## Privacy & ethics

This tool can record keyboard and mouse input **only while recording is active**. Use it only on machines and accounts you own, and only for legitimate personal productivity, testing, or accessibility purposes. Do not use it to capture other people’s data without consent.

---

## License

Use and modify for personal and educational purposes. Attribution to **ma.ad.gh mahanneman** is appreciated.

---

## Persian documentation

مستندات فارسی: **[README.FA.md](README.FA.md)**
