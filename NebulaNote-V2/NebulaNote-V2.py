# -*- coding: utf-8 -*-
"""
Nebula Note  Professional
Modern floating input logger & note assistant.
Author : ma.ad.gh mahanneman
GitHub : https://github.com/mahanneman/cosmic-keylogger

Improvements in :
- Cleaner architecture & better error handling
- Persistent settings (JSON config)
- Professional UI polish (spacing, hover states, status feedback)
- Fixed SnippetsDialog language handling
- Complete dependency check (including openpyxl)
- Session naming support
- Improved counter & stats
- Memory leak fixes in I18nRegistry
- Cross-platform sound fallback
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
import threading
import json
import os
import time
import datetime
import webbrowser
import base64
import re
import sys
import traceback
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any, Set
from collections import Counter

from pynput import keyboard, mouse
from pystray import Icon as TrayIcon, Menu as TrayMenu, MenuItem as TrayMenuItem
from PIL import Image, ImageDraw
import pandas as pd

# Optional sound support
try:
    import winsound
    HAS_SOUND = True
except Exception:
    HAS_SOUND = False

# ═══════════════════════════════════════════════════════════
# BOOTSTRAP & CRASH HANDLER
# ═══════════════════════════════════════════════════════════
def _ck_log_dir() -> str:
    d = os.path.join(os.path.expanduser("~"), "CosmicKeylogger")
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        pass
    return d

def _ck_write_log(et, ev, tb):
    try:
        p = os.path.join(_ck_log_dir(), "crash.log")
        with open(p, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 60 + "\n" + datetime.datetime.now().isoformat() + "\n")
            traceback.print_exception(et, ev, tb, file=f)
    except Exception:
        pass

def _ck_hook(et, ev, tb):
    _ck_write_log(et, ev, tb)
    try:
        traceback.print_exception(et, ev, tb)
    except Exception:
        pass
    try:
        if sys.stdin and sys.stdin.isatty():
            input("Press Enter to exit...")
    except Exception:
        pass

sys.excepthook = _ck_hook
try:
    threading.excepthook = lambda a: _ck_hook(a.exc_type, a.exc_value, a.exc_traceback)
except Exception:
    pass

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

try:
    if os.name == "nt":
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
except Exception:
    pass

def _ck_check_deps() -> List[str]:
    missing = []
    for mod, pkg in [
        ("pynput", "pynput"),
        ("pystray", "pystray"),
        ("PIL", "Pillow"),
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"),
    ]:
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    return missing

# ═══════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════
APP_NAME = "Nebula Note"
APP_VER = "4.4 Final"
APP_REPO = "https://github.com/mahanneman/cosmic-keylogger"
CONFIG_PATH = os.path.join(_ck_log_dir(), "settings.json")

C = {
    "bg": "#07071a",
    "bg_light": "#0f0f28",
    "surface": "#16163a",
    "surface_hi": "#22224c",
    "border": "#2a2a5a",
    "accent": "#00d9ff",
    "accent2": "#b14aff",
    "accent3": "#ff2e97",
    "success": "#00ffa3",
    "warning": "#ffd93d",
    "danger": "#ff3860",
    "text": "#e0e0ff",
    "text_dim": "#6a6a92",
    "white": "#ffffff",
}

F = {
    "title": ("Segoe UI Emoji", 10, "bold"),
    "body": ("Segoe UI Emoji", 9),
    "small": ("Segoe UI Emoji", 8),
    "tiny": ("Segoe UI Emoji", 7),
    "nano": ("Segoe UI Emoji", 6),
    "mono": ("Consolas", 9),
}

NORM_MOD = {
    "ctrl_l": "ctrl", "ctrl_r": "ctrl",
    "shift_l": "shift", "shift_r": "shift",
    "alt_l": "alt", "alt_r": "alt",
    "cmd_l": "cmd", "cmd_r": "cmd",
}

# ═══════════════════════════════════════════════════════════
# I18N
# ═══════════════════════════════════════════════════════════
I18N = {
    "fa": {
        "start": "▶ شروع", "stop": "⏹ توقف", "save": "💾 ذخیره",
        "mode_typing": "تایپ", "mode_macro": "ماکرو",
        "status_ready": "آماده", "status_rec": "● در حال ضبط", "status_saved": "✓ ذخیره شد",
        "status_playing": "▶ پخش...", "status_countdown": "شمارش معکوس: {}",
        "mouse_on": "🖱 روشن", "mouse_off": "🖱 خاموش",
        "scroll_on": "⇅ روشن", "scroll_off": "⇅ خاموش",
        "events": "رویداد",
        "btn_start": "▶ شروع", "btn_stop": "⏹ توقف", "btn_save": "💾 ذخیره",
        "btn_mode": "🔄 حالت", "btn_clear": "🗑 پاک", "btn_files": "📁 فایل",
        "btn_export": "📤 خروجی", "btn_lang": "🌐 زبان", "btn_ui": "🗣 رابط",
        "btn_preview": "◈ پیش", "btn_help": "❓ راهنما", "btn_settings": "⚙ تنظیمات",
        "btn_top": "📌 بالا", "btn_replay": "▶ پخش", "btn_stats": "📊 آمار",
        "btn_import": "📥 ایمپورت", "btn_sound": "🔊 صدا", "btn_auto": "💾 خودکار",
        "btn_font_up": "A+", "btn_font_dn": "A−", "btn_mouse": "🖱 ماوس", "btn_scroll": "⇅ اسکرول",
        "btn_copyall": "📋 کپی همه", "btn_readonly": "🔒 قفل", "btn_snippets": "✂ الگو",
        "help_title": "راهنما", "export_title": "خروجی", "lang_title": "زبان‌های ورودی",
        "ui_lang_title": "زبان رابط", "files_title": "فایل‌ها",
        "settings_title": "تنظیمات", "stats_title": "آمار جلسه", "snippets_title": "الگوهای آماده",
        "close": "بستن", "confirm": "تأیید", "cancel": "لغو", "all": "همه", "none": "هیچ",
        "installed": "نصب‌شده", "saved_at": "ذخیره شد", "no_events": "رویدادی وجود ندارد",
        "credits": "made by ma.ad.gh mahanneman · github",
        "hotkeys_bar": "Ctrl+Shift+1/2/3 الگو   |   Ctrl+Shift  Q شروع  W ذخیره  E حالت  A بالا  Z پخش  X شناور\nC پاک  S الگوها  F فایل  G خروجی  R زبان  T ماوس  V ایمپورت  B اسکرول  H راهنما  K تنظیمات",
        "menu_copy": "کپی", "menu_cut": "برش", "menu_paste": "چسباندن",
        "menu_select_all": "انتخاب همه", "menu_undo": "واگرد", "menu_redo": "ازنو",
        "menu_find": "جستجو", "menu_clear_all": "پاک کردن متن",
        "menu_dup_line": "تکرار خط", "menu_copy_all": "کپی همه متن",
        "tip_record": "شروع/توقف ضبط (Ctrl+Shift+Q)", "tip_save": "ذخیره (Ctrl+Shift+W)",
        "tip_mode": "تایپ/ماکرو (Ctrl+Shift+E)", "tip_clear": "پاک (Ctrl+Shift+C)",
        "tip_help": "راهنما (Ctrl+Shift+H)", "tip_files": "فایل‌ها (Ctrl+Shift+F)",
        "tip_export": "خروجی (Ctrl+Shift+G)", "tip_lang": "زبان ورودی (Ctrl+Shift+R)",
        "tip_ui_lang": "زبان رابط (Ctrl+Shift+U)", "tip_mouse": "ماوس (Ctrl+Shift+T)",
        "tip_scroll": "اسکرول (Ctrl+Shift+B)", "tip_top": "همیشه بالا (Ctrl+Shift+A)",
        "tip_replay": "پخش (Ctrl+Shift+Z)", "tip_drag": "برای جابه‌جایی بکش",
        "tip_close": "بستن", "tip_min": "آیکون شناور (Ctrl+Shift+X)", "tip_max": "حداکثر",
        "tip_link": APP_REPO, "tip_settings": "تنظیمات (Ctrl+Shift+K)",
        "tip_stats": "آمار (Ctrl+Shift+I)", "tip_import": "ایمپورت JSON (Ctrl+Shift+V)",
        "tip_sound": "صدا (Ctrl+Shift+L)", "tip_autosave": "ذخیره خودکار (Ctrl+Shift+Y)",
        "tip_font_up": "فونت+ (Ctrl+Shift+P)", "tip_font_dn": "فونت− (Ctrl+Shift+M)",
        "tip_opacity": "شفافیت (Ctrl+Shift+J)", "tip_preview": "پیش‌نمایش (Ctrl+Shift+9)",
        "tip_copyall": "کپی همه متن به کلیپ‌بورد",
        "tip_readonly": "قفل/باز کردن ویرایش (Ctrl+Shift+F1)",
        "tip_snippets": "درج الگوی آماده (Ctrl+Shift+S)",
        "tip_export_json": "داده کامل", "tip_export_jsonl": "هر رویداد در خط",
        "tip_export_excel": "جدول اکسل", "tip_export_text": "فقط کاراکترها",
        "tip_export_auto": "اسکریپت پایتون", "tip_export_enc": "JSON رمزنگاری",
        "tip_export_md": "Markdown (.md)",
        "export_json": "JSON", "export_jsonl": "JSONL", "export_excel": "Excel",
        "export_text": "متن ساده", "export_auto": "🐍 اسکریپت پایتون",
        "export_encrypted": "🔒 JSON رمزنگاری‌شده", "export_md": "📝 Markdown",
        "pl_rep": "تعداد تکرار", "pl_delay": "تأخیر (ث)", "pl_speed": "سرعت",
        "pl_dur": "مدت (ث، 0=کامل)", "pl_run": "▶ اجرا", "pl_stop": "⏹ توقف", "pl_ready": "آماده",
        "set_autosave": "ذخیره خودکار (ث، 0=خاموش)", "set_countdown": "شمارش معکوس (ث)",
        "set_sound": "صدای شروع/توقف", "set_encrypt": "رمزنگاری هنگام خروجی",
        "set_opacity": "شفافیت (0.5-1.0)", "set_font": "اندازه فونت",
        "set_filter": "فعال‌سازی فیلتر زبان",
        "set_apply": "اعمال", "set_reset": "بازنشانی",
        "stats_total": "کل رویدادها", "stats_keys": "کلیدها", "stats_clicks": "کلیک‌ها",
        "stats_scrolls": "اسکرول", "stats_moves": "حرکت ماوس", "stats_duration": "مدت",
        "stats_langs": "زبان‌ها", "stats_top": "پرکاربردترین", "stats_session": "جلسه",
        "stats_none": "(خالی)", "import_ok": "وارد شد", "import_err": "خطای ایمپورت",
        "encrypt_pwd": "رمز:", "pwd_title": "رمزنگاری XOR", "countdown_go": "برو!",
        "find_title": "جستجو", "find_what": "جستجو:", "find_with": "جایگزین:",
        "find_next": "بعدی", "find_prev": "قبلی", "find_all": "همه", "replace": "جایگزین",
        "copied": "کپی شد", "readonly_on": "🔒 قفل شد", "readonly_off": "🔓 باز شد",
        "snip_meeting": "— جلسه —\n[تاریخ] [ساعت]\nموضوع:\nحاضران:\n",
        "snip_todo": "☐ کار جدید\n☐ کار بعدی\n",
        "snip_idea": "💡 ایده:\n",
        "snip_log": "[LOG] ",
        "snip_sep": "----------------------------------------\n",
        "snip_time": "[HH:MM:SS] ",
        "snip_date": "[YYYY-MM-DD] ",
        "snip_bullet": "• ",
        "snip_code": "```\n\n```",
        "snip_link": "[متن](https://)",
        "recent_title": "اخیر",
        "help_body": """راهنمای Nebula Note  Professional
ساخته شده توسط ma.ad.gh mahanneman

شورتکات‌های سراسری (Ctrl+Shift+...):
  Q  شروع/توقف ضبط      W  ذخیره
  E  تغییر حالت تایپ/ماکرو   A  always-on-top
  Z  پخش مجدد           X  آیکون شناور
  C  پاک کردن           F  فایل‌ها
  G  خروجی              R  زبان‌های ورودی
  U  زبان رابط          T  ماوس
  B  اسکرول             H  این راهنما
  I  آمار               K  تنظیمات
  V  ایمپورت JSON       L  صدای بازخورد
  Y  ذخیره خودکار       P  فونت بزرگتر
  M  فونت کوچکتر        J  شفافیت چرخشی
  D  کپی فایل           N  فایل جدید
  O  باز کردن پوشه      S  الگوهای آماده
  F1 قفل/باز ویرایش     ↑↓ سرعت پخش

ابزارهای یادداشت:
  0  خط جداکننده    6  درج ساعت
  7  درج تاریخ      8  درج نقطه‌سر
  9  پیش‌نمایش زنده

زبان رابط: 1=فارسی 2=English 3=العربية 4=Deutsch 5=Français

شورتکات‌های محلی (داخل کادر متن):
  Ctrl+C کپی  Ctrl+X برش  Ctrl+V چسباندن
  Ctrl+A انتخاب همه  Ctrl+Z واگرد  Ctrl+Y ازنو
  Ctrl+D تکرار خط  Ctrl+F جستجو و جایگزین
  Ctrl+Wheel زوم فونت  راست‌کلیک منوی سریع

نکته: فیلتر زبان پیش‌فرض خاموش است تا همه زبان‌ها کار کنند.
برای فعال‌سازی: ⚙ تنظیمات → فیلتر زبان
"""
    },
    "en": {
        "start": "▶ Start", "stop": "⏹ Stop", "save": "💾 Save",
        "mode_typing": "Typing", "mode_macro": "Macro",
        "status_ready": "Ready", "status_rec": "● Recording", "status_saved": "✓ Saved",
        "status_playing": "▶ Playing...", "status_countdown": "Countdown: {}",
        "mouse_on": "🖱 On", "mouse_off": "🖱 Off", "scroll_on": "⇅ On", "scroll_off": "⇅ Off",
        "events": "events",
        "btn_start": "▶ Start", "btn_stop": "⏹ Stop", "btn_save": "💾 Save",
        "btn_mode": "🔄 Mode", "btn_clear": "🗑 Clear", "btn_files": "📁 Files",
        "btn_export": "📤 Export", "btn_lang": "🌐 Lang", "btn_ui": "🗣 UI",
        "btn_preview": "◈ Preview", "btn_help": "❓ Help", "btn_settings": "⚙ Settings",
        "btn_top": "📌 Top", "btn_replay": "▶ Replay", "btn_stats": "📊 Stats",
        "btn_import": "📥 Import", "btn_sound": "🔊 Sound", "btn_auto": "💾 Auto",
        "btn_font_up": "A+", "btn_font_dn": "A−", "btn_mouse": "🖱 Mouse", "btn_scroll": "⇅ Scroll",
        "btn_copyall": "📋 Copy All", "btn_readonly": "🔒 Lock", "btn_snippets": "✂ Snippets",
        "help_title": "Help", "export_title": "Export", "lang_title": "Input Languages",
        "ui_lang_title": "UI Language", "files_title": "Saved Files",
        "settings_title": "Settings", "stats_title": "Session Stats", "snippets_title": "Snippets",
        "close": "Close", "confirm": "Confirm", "cancel": "Cancel", "all": "All", "none": "None",
        "installed": "Installed", "saved_at": "Saved", "no_events": "No events",
        "credits": "made by ma.ad.gh mahanneman · github",
        "hotkeys_bar": "Ctrl+Shift+1/2/3 Snippets   |   Ctrl+Shift  Q Start  W Save  E Mode  A Top  Z Replay  X Float\nC Clear  S Snippets  F Files  G Export  R Lang  T Mouse  V Import  B Scroll  H Help  K Settings",
        "menu_copy": "Copy", "menu_cut": "Cut", "menu_paste": "Paste",
        "menu_select_all": "Select All", "menu_undo": "Undo", "menu_redo": "Redo",
        "menu_find": "Find & Replace", "menu_clear_all": "Clear text",
        "menu_dup_line": "Duplicate line", "menu_copy_all": "Copy all text",
        "tip_record": "Start/Stop (Ctrl+Shift+Q)", "tip_save": "Save (Ctrl+Shift+W)",
        "tip_mode": "Mode (Ctrl+Shift+E)", "tip_clear": "Clear (Ctrl+Shift+C)",
        "tip_help": "Help (Ctrl+Shift+H)", "tip_files": "Files (Ctrl+Shift+F)",
        "tip_export": "Export (Ctrl+Shift+G)", "tip_lang": "Input langs (Ctrl+Shift+R)",
        "tip_ui_lang": "UI lang (Ctrl+Shift+U)", "tip_mouse": "Mouse (Ctrl+Shift+T)",
        "tip_scroll": "Scroll (Ctrl+Shift+B)", "tip_top": "Always top (Ctrl+Shift+A)",
        "tip_replay": "Replay (Ctrl+Shift+Z)", "tip_drag": "Drag to move",
        "tip_close": "Close", "tip_min": "Float (Ctrl+Shift+X)", "tip_max": "Maximize",
        "tip_link": APP_REPO, "tip_settings": "Settings (Ctrl+Shift+K)",
        "tip_stats": "Stats (Ctrl+Shift+I)", "tip_import": "Import JSON (Ctrl+Shift+V)",
        "tip_sound": "Sound (Ctrl+Shift+L)", "tip_autosave": "Autosave (Ctrl+Shift+Y)",
        "tip_font_up": "Font+ (Ctrl+Shift+P)", "tip_font_dn": "Font− (Ctrl+Shift+M)",
        "tip_opacity": "Opacity (Ctrl+Shift+J)", "tip_preview": "Preview (Ctrl+Shift+9)",
        "tip_copyall": "Copy all text to clipboard",
        "tip_readonly": "Lock/Unlock editing (Ctrl+Shift+F1)",
        "tip_snippets": "Insert snippet (Ctrl+Shift+S)",
        "tip_export_json": "Full data", "tip_export_jsonl": "One JSON per line",
        "tip_export_excel": "Excel table", "tip_export_text": "Only characters",
        "tip_export_auto": "Python script", "tip_export_enc": "Encrypted JSON",
        "tip_export_md": "Markdown (.md)",
        "export_json": "JSON", "export_jsonl": "JSONL", "export_excel": "Excel",
        "export_text": "Plain text", "export_auto": "🐍 Python Script",
        "export_encrypted": "🔒 Encrypted JSON", "export_md": "📝 Markdown",
        "pl_rep": "Repeat", "pl_delay": "Delay (s)", "pl_speed": "Speed",
        "pl_dur": "Duration (s, 0=full)", "pl_run": "▶ Run", "pl_stop": "⏹ Stop", "pl_ready": "Ready",
        "set_autosave": "Autosave (sec, 0=off)", "set_countdown": "Countdown (sec)",
        "set_sound": "Start/Stop sound", "set_encrypt": "Encrypt on export",
        "set_opacity": "Opacity (0.5-1.0)", "set_font": "Font size",
        "set_filter": "Enable language filter",
        "set_apply": "Apply", "set_reset": "Reset",
        "stats_total": "Total events", "stats_keys": "Keys", "stats_clicks": "Clicks",
        "stats_scrolls": "Scrolls", "stats_moves": "Mouse moves", "stats_duration": "Duration",
        "stats_langs": "Languages", "stats_top": "Top keys", "stats_session": "Session",
        "stats_none": "(empty)", "import_ok": "Imported", "import_err": "Import error",
        "encrypt_pwd": "Password:", "pwd_title": "XOR Encryption", "countdown_go": "Go!",
        "find_title": "Find & Replace", "find_what": "Find:", "find_with": "Replace:",
        "find_next": "Next", "find_prev": "Prev", "find_all": "All", "replace": "Replace",
        "copied": "Copied", "readonly_on": "🔒 Locked", "readonly_off": "🔓 Unlocked",
        "snip_meeting": "— Meeting —\n[Date] [Time]\nTopic:\nAttendees:\n",
        "snip_todo": "☐ New task\n☐ Next task\n",
        "snip_idea": "💡 Idea: ",
        "snip_log": "[LOG] ",
        "snip_sep": "----------------------------------------\n",
        "snip_time": "[HH:MM:SS] ",
        "snip_date": "[YYYY-MM-DD] ",
        "snip_bullet": "• ",
        "snip_code": "```\n\n```",
        "snip_link": "[text](https://)",
        "recent_title": "Recent",
        "help_body": """Nebula Note Professional Help
by ma.ad.gh mahanneman

Global shortcuts (Ctrl+Shift+...):
  Q Start/Stop · W Save · E Mode · A Top · Z Replay
  X Float · C Clear · F Files · G Export · R Input Langs
  U UI Lang · T Mouse · B Scroll · H Help · I Stats
  K Settings · V Import · L Sound · Y Autosave
  P Font+ · M Font− · J Opacity · D Dup · N New · O Folder
  S Snippets · F1 Lock  ·  Up/Down Playback speed

Note tools (Ctrl+Shift+...):
  0 Insert horizontal line
  6 Insert time · 7 Insert date · 8 Insert bullet · 9 Preview

Local shortcuts (inside text box):
  Ctrl+C Copy · Ctrl+X Cut · Ctrl+V Paste
  Ctrl+A Select All · Ctrl+Z Undo · Ctrl+Y Redo
  Ctrl+D Duplicate line · Ctrl+F Find & Replace
  Ctrl+Wheel Zoom · Right-click context menu
"""
    },
    "ar": {
        "start": "▶ بدء", "stop": "⏹ إيقاف", "save": "💾 حفظ", "mode_typing": "كتابة",
        "mode_macro": "ماكرو", "status_ready": "جاهز", "status_rec": "● يسجل",
        "status_saved": "✓ حفظ", "status_playing": "▶ تشغيل...", "status_countdown": "العد: {}",
        "mouse_on": "🖱 مفعل", "mouse_off": "🖱 معطل", "scroll_on": "⇅ مفعل", "scroll_off": "⇅ معطل",
        "events": "أحداث", "btn_start": "▶ بدء", "btn_stop": "⏹ إيقاف", "btn_save": "💾 حفظ",
        "btn_mode": "🔄 وضع", "btn_clear": "🗑 مسح", "btn_files": "📁 ملفات",
        "btn_export": "📤 تصدير", "btn_lang": "🌐 لغة", "btn_ui": "🗣 واجهة",
        "btn_preview": "◈ معاينة", "btn_help": "❓ مساعدة", "btn_settings": "⚙ إعدادات",
        "btn_top": "📌 أعلى", "btn_replay": "▶ تشغيل", "btn_stats": "📊 إحصاء",
        "btn_import": "📥 استيراد", "btn_sound": "🔊 صوت", "btn_auto": "💾 تلقائي",
        "btn_font_up": "A+", "btn_font_dn": "A−", "btn_mouse": "🖱 ماوس", "btn_scroll": "⇅ تمرير",
        "btn_copyall": "📋 نسخ الكل", "btn_readonly": "🔒 قفل", "btn_snippets": "✂ قوالب",
        "help_title": "مساعدة", "export_title": "تصدير", "lang_title": "لغات الإدخال",
        "ui_lang_title": "لغة الواجهة", "files_title": "ملفات",
        "settings_title": "إعدادات", "stats_title": "إحصاء", "snippets_title": "قوالب",
        "close": "إغلاق", "confirm": "تأكيد", "cancel": "إلغاء", "all": "الكل", "none": "لا شيء",
        "installed": "مثبت", "saved_at": "حفظ", "no_events": "لا أحداث",
        "credits": "من ma.ad.gh mahanneman · github",
        "hotkeys_bar": "Ctrl+Shift  Q بدء  W حفظ  E وضع  A أعلى  Z تشغيل  X عائم  C مسح\nF ملفات  G تصدير  R لغة  U واجهة  T ماوس  B تمرير  H مساعدة  I إحصاء  K إعدادات\nV استيراد  L صوت  Y تلقائي  S قوالب  F1 قفل  0-9 أدوات",
        "menu_copy": "نسخ", "menu_cut": "قص", "menu_paste": "لصق", "menu_select_all": "تحديد الكل",
        "menu_undo": "تراجع", "menu_redo": "إعادة", "menu_find": "بحث", "menu_clear_all": "مسح النص",
        "menu_dup_line": "تكرار السطر", "menu_copy_all": "نسخ الكل",
        "readonly_on": "🔒 مقفل", "readonly_off": "🔓 مفتوح",
        "help_body": "مساعدة Nebula Note \n\nاختصارات Ctrl+Shift+Q/W/E/A/Z/X/C/F/G/R/U/T/B/H/I/K/V/L/Y/P/M/J/S/F1"
    },
    "de": {
        "start": "▶ Start", "stop": "⏹ Stop", "save": "💾 Speichern",
        "mode_typing": "Tippen", "mode_macro": "Makro", "status_ready": "Bereit",
        "status_rec": "● Aufnahme", "status_saved": "✓ Gespeichert",
        "status_playing": "▶ Wiedergabe...", "status_countdown": "Countdown: {}",
        "mouse_on": "🖱 An", "mouse_off": "🖱 Aus", "scroll_on": "⇅ An", "scroll_off": "⇅ Aus",
        "events": "Ereignisse", "btn_start": "▶ Start", "btn_stop": "⏹ Stop", "btn_save": "💾 Speichern",
        "btn_mode": "🔄 Modus", "btn_clear": "🗑 Löschen", "btn_files": "📁 Dateien",
        "btn_export": "📤 Export", "btn_lang": "🌐 Sprache", "btn_ui": "🗣 UI",
        "btn_preview": "◈ Vorschau", "btn_help": "❓ Hilfe", "btn_settings": "⚙ Einst.",
        "btn_top": "📌 Oben", "btn_replay": "▶ Abspielen", "btn_stats": "📊 Stat",
        "btn_import": "📥 Import", "btn_sound": "🔊 Ton", "btn_auto": "💾 Auto",
        "btn_font_up": "A+", "btn_font_dn": "A−", "btn_mouse": "🖱 Maus", "btn_scroll": "⇅ Scroll",
        "btn_copyall": "📋 Alle kopieren", "btn_readonly": "🔒 Sperre", "btn_snippets": "✂ Schnipsel",
        "help_title": "Hilfe", "export_title": "Export", "lang_title": "Sprachen",
        "ui_lang_title": "UI-Sprache", "files_title": "Dateien",
        "settings_title": "Einstellungen", "stats_title": "Statistik", "snippets_title": "Schnipsel",
        "close": "Schließen", "confirm": "OK", "cancel": "Abbrechen", "all": "Alle", "none": "Keine",
        "installed": "Installiert", "saved_at": "Gespeichert", "no_events": "Keine",
        "credits": "von ma.ad.gh mahanneman · github",
        "hotkeys_bar": "Ctrl+Shift+ Q Start · W Speichern · E Modus · A Oben · Z Abspielen · X Float · C Löschen · F Dateien · G Export · R Sprachen · U UI · T Maus · B Scroll · H Hilfe · I Stat · K Einst · V Import · L Ton · Y Auto · S Schnipsel · F1 Sperre · 0-9 Tools",
        "menu_copy": "Kopieren", "menu_cut": "Ausschneiden", "menu_paste": "Einfügen",
        "menu_select_all": "Alles markieren", "menu_undo": "Rückgängig", "menu_redo": "Wiederholen",
        "menu_find": "Suchen", "menu_clear_all": "Text leeren",
        "menu_dup_line": "Zeile duplizieren", "menu_copy_all": "Alles kopieren",
        "readonly_on": "🔒 Gesperrt", "readonly_off": "🔓 Entsperrt",
        "help_body": "Nebula Note  Hilfe\n\nCtrl+Shift+Q/W/E/A/Z/X/C/F/G/R/U/T/B/H/I/K/V/L/Y/P/M/J/S/F1"
    },
    "fr": {
        "start": "▶ Démarrer", "stop": "⏹ Arrêter", "save": "💾 Enregistrer",
        "mode_typing": "Saisie", "mode_macro": "Macro", "status_ready": "Prêt",
        "status_rec": "● Enregistrement", "status_saved": "✓ Enregistré",
        "status_playing": "▶ Lecture...", "status_countdown": "Compte: {}",
        "mouse_on": "🖱 Activé", "mouse_off": "🖱 Désactivé",
        "scroll_on": "⇅ Activé", "scroll_off": "⇅ Désactivé",
        "events": "événements", "btn_start": "▶ Démarrer", "btn_stop": "⏹ Arrêter",
        "btn_save": "💾 Enregistrer", "btn_mode": "🔄 Mode", "btn_clear": "🗑 Effacer",
        "btn_files": "📁 Fichiers", "btn_export": "📤 Exporter", "btn_lang": "🌐 Langue",
        "btn_ui": "🗣 UI", "btn_preview": "◈ Aperçu", "btn_help": "❓ Aide",
        "btn_settings": "⚙ Param.", "btn_top": "📌 Haut", "btn_replay": "▶ Lire",
        "btn_stats": "📊 Stats", "btn_import": "📥 Importer", "btn_sound": "🔊 Son",
        "btn_auto": "💾 Auto", "btn_font_up": "A+", "btn_font_dn": "A−",
        "btn_mouse": "🖱 Souris", "btn_scroll": "⇅ Défiler",
        "btn_copyall": "📋 Tout copier", "btn_readonly": "🔒 Verr.", "btn_snippets": "✂ Extraits",
        "help_title": "Aide", "export_title": "Exporter", "lang_title": "Langues",
        "ui_lang_title": "Langue UI", "files_title": "Fichiers",
        "settings_title": "Paramètres", "stats_title": "Statistiques", "snippets_title": "Extraits",
        "close": "Fermer", "confirm": "Confirmer", "cancel": "Annuler", "all": "Tous", "none": "Aucun",
        "installed": "Installés", "saved_at": "Enregistré", "no_events": "Aucun",
        "credits": "par ma.ad.gh mahanneman · github",
        "hotkeys_bar": "Ctrl+Shift+ Q Démarrer · W Enr · E Mode · A Haut · Z Lire · X Float · C Effacer · F Fich · G Export · R Langues · U UI · T Souris · B Défiler · H Aide · I Stats · K Param · V Import · L Son · Y Auto · S Extraits · F1 Verr. · 0-9 Outils",
        "menu_copy": "Copier", "menu_cut": "Couper", "menu_paste": "Coller",
        "menu_select_all": "Tout sélectionner", "menu_undo": "Annuler", "menu_redo": "Refaire",
        "menu_find": "Rechercher", "menu_clear_all": "Effacer le texte",
        "menu_dup_line": "Dupliquer ligne", "menu_copy_all": "Tout copier",
        "readonly_on": "🔒 Verrouillé", "readonly_off": "🔓 Déverrouillé",
        "help_body": "Nebula Note  Aide\n\nCtrl+Shift+Q/W/E/A/Z/X/C/F/G/R/U/T/B/H/I/K/V/L/Y/P/M/J/S/F1"
    },
}


def T(key: str, lang: str = "fa") -> str:
    return I18N.get(lang, I18N["fa"]).get(key, I18N["fa"].get(key, key))


UI_LANGS = ["fa", "en", "ar", "de", "fr"]
LANG_NAMES = {
    "fa": "فارسی", "ar": "العربية", "en": "English", "de": "Deutsch", "fr": "Français",
    "es": "Español", "ru": "Русский", "zh": "中文", "ja": "日本語", "ko": "한국어",
    "he": "עברית", "hi": "हिन्दी", "tr": "Türkçe", "it": "Italiano", "ur": "اردو"
}
LANG_RANGES = {
    "fa": [("\u0600", "\u06FF"), ("\u0750", "\u077F")],
    "ar": [("\u0600", "\u06FF")], "ur": [("\u0600", "\u06FF")],
    "en": [("\u0041", "\u007A"), ("\u00C0", "\u024F")],
    "de": [("\u0041", "\u007A"), ("\u00C0", "\u024F")],
    "fr": [("\u0041", "\u007A"), ("\u00C0", "\u024F")],
    "es": [("\u0041", "\u007A"), ("\u00C0", "\u024F")],
    "ru": [("\u0400", "\u04FF")], "zh": [("\u4E00", "\u9FFF")],
    "ja": [("\u3040", "\u30FF")], "ko": [("\uAC00", "\uD7AF")],
    "he": [("\u0590", "\u05FF")], "hi": [("\u0900", "\u097F")],
    "tr": [("\u0041", "\u007A"), ("\u00C0", "\u024F")],
    "it": [("\u0041", "\u007A"), ("\u00C0", "\u024F")],
}
FA_SPECIFIC = {0x067E, 0x0686, 0x0698, 0x06A9, 0x06AF, 0x06CC}


def detect_installed_languages() -> Set[str]:
    found: Set[str] = set()
    try:
        import ctypes
        n = ctypes.windll.user32.GetKeyboardLayoutList(0, None)
        arr = (ctypes.c_void_p * n)()
        ctypes.windll.user32.GetKeyboardLayoutList(n, arr)
        m = {
            0x01: "ar", 0x04: "zh", 0x07: "de", 0x09: "en", 0x0a: "es", 0x0c: "fr",
            0x0d: "he", 0x10: "it", 0x11: "ja", 0x12: "ko", 0x19: "ru", 0x1f: "tr",
            0x29: "fa", 0x39: "hi", 0x20: "ur"
        }
        for layout in arr:
            if not layout:
                continue
            code = m.get((layout & 0xFFFF) & 0x3FF)
            if code:
                found.add(code)
    except Exception as e:
        print(f"[lang] {e}")
    return found


def char_to_lang(ch: str) -> str:
    if not ch:
        return ""
    cp = ord(ch)
    for code, ranges in LANG_RANGES.items():
        for lo, hi in ranges:
            if ord(lo) <= cp <= ord(hi):
                if code in ("fa", "ar", "ur"):
                    return "fa" if cp in FA_SPECIFIC else "ar"
                if code in ("en", "de", "fr", "es", "it", "tr"):
                    return "en"
                return code
    return ""


def xor_encrypt(text: str, password: str) -> str:
    if not password:
        return text
    key = password.encode("utf-8")
    data = text.encode("utf-8")
    out = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    return base64.b64encode(out).decode("ascii")


# ═══════════════════════════════════════════════════════════
# CONFIG MANAGER + SNIPPETS
# ═══════════════════════════════════════════════════════════
DEFAULT_SNIPPETS = [
    {"id": "line", "label": "──── خط جداکننده", "text": "\n--------------------------------------------------------------------------------\n", "slot": 1},
    {"id": "date", "label": "📆 تاریخ", "text": "[YYYY-MM-DD] ", "slot": 2},
    {"id": "time", "label": "🕐 ساعت", "text": "[HH:MM:SS] ", "slot": 3},
    {"id": "example", "label": "📌 EXAMPLE", "text": "EXAMPLE: ", "slot": 0},
    {"id": "todo", "label": "☐ کار", "text": "☐ ", "slot": 0},
    {"id": "idea", "label": "💡 ایده", "text": "💡 ", "slot": 0},
    {"id": "log", "label": "[LOG]", "text": "[LOG] ", "slot": 0},
    {"id": "bullet", "label": "• نقطه", "text": "• ", "slot": 0},
    {"id": "sep", "label": "─── جداکننده بلند", "text": "\n========================================\n", "slot": 0},
    {"id": "meeting", "label": "📅 جلسه", "text": "— جلسه —\n[تاریخ] [ساعت]\nموضوع:\nحاضران:\n", "slot": 0},
]

class ConfigManager:
    DEFAULTS = {
        "ui_lang": "fa",
        "autosave_interval": 30,
        "countdown": 0,
        "sound_enabled": True,
        "font_size": 9,
        "window_opacity": 1.0,
        "encrypt_export": False,
        "filter_enabled": False,
        "record_mouse": True,
        "record_scroll": True,
        "mode": "typing",
        "always_on_top": True,
        "snippets": None,  # filled at load
    }

    def __init__(self, path: str = CONFIG_PATH):
        self.path = path
        self.data = self.DEFAULTS.copy()
        self.data["snippets"] = [dict(s) for s in DEFAULT_SNIPPETS]
        self.load()

    def load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                for k, v in saved.items():
                    if k == "snippets" and isinstance(v, list):
                        self.data["snippets"] = v
                    elif k in self.DEFAULTS:
                        self.data[k] = v
        except Exception as e:
            print(f"[config] load error: {e}")

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[config] save error: {e}")

    def get(self, key: str, default=None):
        return self.data.get(key, default if default is not None else self.DEFAULTS.get(key))

    def set(self, key: str, value):
        self.data[key] = value

    def get_snippets(self) -> list:
        return self.data.get("snippets") or [dict(s) for s in DEFAULT_SNIPPETS]

    def set_snippets(self, snippets: list):
        self.data["snippets"] = snippets
        self.save()

    def get_slot(self, slot: int) -> Optional[dict]:
        """Return snippet assigned to slot 1/2/3 or None"""
        for s in self.get_snippets():
            if s.get("slot") == slot:
                return s
        return None


# ═══════════════════════════════════════════════════════════
# I18N REGISTRY
# ═══════════════════════════════════════════════════════════
class I18nRegistry:
    def __init__(self):
        self.lang = "fa"
        self.items: List[tuple] = []
        self.tooltips: List = []

    def register(self, widget, key: str, attr: str = "text"):
        self.items.append((widget, key, attr))
        try:
            # Tkinter widgets need .config() / dict-style assignment, not setattr
            if attr == "text":
                widget.config(text=T(key, self.lang))
            else:
                widget.config(**{attr: T(key, self.lang)})
        except Exception:
            try:
                widget[attr] = T(key, self.lang)
            except Exception:
                pass

    def apply_all(self):
        alive = []
        for w, k, a in self.items:
            try:
                if w.winfo_exists():
                    if a == "text":
                        w.config(text=T(k, self.lang))
                    else:
                        w.config(**{a: T(k, self.lang)})
                    alive.append((w, k, a))
            except Exception:
                try:
                    w[a] = T(k, self.lang)
                    alive.append((w, k, a))
                except Exception:
                    pass
        self.items = alive
        for t in list(self.tooltips):
            try:
                t.refresh()
            except Exception:
                pass

    def set_lang(self, lang: str):
        if lang not in I18N:
            return
        self.lang = lang
        self.apply_all()


# ═══════════════════════════════════════════════════════════
# TOOLTIP
# ═══════════════════════════════════════════════════════════
class Tooltip:
    def __init__(self, widget, key, registry, delay=500):
        self.widget = widget
        self.key = key
        self.registry = registry
        self.delay = delay
        self._id = None
        self._tip = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")
        registry.tooltips.append(self)

    def _schedule(self, _=None):
        self._cancel()
        try:
            self._id = self.widget.after(self.delay, self._show)
        except Exception:
            pass

    def _cancel(self):
        if self._id:
            try:
                self.widget.after_cancel(self._id)
            except Exception:
                pass
            self._id = None

    def _show(self):
        if self._tip:
            return
        try:
            if not self.widget.winfo_exists():
                return
        except Exception:
            return
        text = T(self.key, self.registry.lang)
        if not text:
            return
        try:
            x = self.widget.winfo_rootx() + 12
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        except Exception:
            return
        try:
            self._tip = tk.Toplevel(self.widget)
            self._tip.wm_overrideredirect(True)
            self._tip.wm_geometry(f"+{x}+{y}")
            self._tip.attributes("-topmost", True)
            fr = tk.Frame(self._tip, bg=C["accent"], bd=0)
            fr.pack()
            tk.Label(
                fr, text=text, bg=C["surface"], fg=C["text"],
                font=F["small"], padx=8, pady=4, justify="left", wraplength=340
            ).pack(padx=1, pady=1)
        except Exception:
            self._tip = None

    def _hide(self, _=None):
        self._cancel()
        if self._tip:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None

    def refresh(self):
        if self._tip:
            self._hide()
            self._show()


# ═══════════════════════════════════════════════════════════
# DATA MODEL
# ═══════════════════════════════════════════════════════════
@dataclass
class InputEvent:
    kind: str
    action: str
    timestamp: float
    key: str = ""
    key_char: str = ""
    vk: Optional[int] = None
    modifiers: List[str] = field(default_factory=list)
    button: str = ""
    x: int = 0
    y: int = 0
    dx: int = 0
    dy: int = 0
    lang: str = ""


# ═══════════════════════════════════════════════════════════
# INPUT ENGINE
# ═══════════════════════════════════════════════════════════
class InputEngine:
    _SPECIAL_NAMES = [
        "ctrl", "ctrl_l", "ctrl_r", "shift", "shift_l", "shift_r",
        "alt", "alt_l", "alt_r", "alt_gr", "cmd", "cmd_l", "cmd_r",
        "enter", "tab", "space", "backspace", "delete", "esc",
        "up", "down", "left", "right", "home", "end", "page_up", "page_down",
        "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12"
    ]
    SPECIAL: Dict = {}
    MODIFIER_KEYS: Set = set()
    MODIFIER_NAMES: Set = {
        "ctrl", "ctrl_l", "ctrl_r", "shift", "shift_l", "shift_r",
        "alt", "alt_l", "alt_r", "alt_gr", "cmd", "cmd_l", "cmd_r"
    }

    for _name in _SPECIAL_NAMES:
        try:
            _k = getattr(keyboard.Key, _name)
            SPECIAL[_k] = _name
        except AttributeError:
            pass
    for _n in _SPECIAL_NAMES:
        try:
            MODIFIER_KEYS.add(getattr(keyboard.Key, _n))
        except AttributeError:
            pass

    def __init__(self, on_event=None):
        self.on_event = on_event
        self.is_recording = False
        self.events: List[InputEvent] = []
        self._lock = threading.Lock()
        self._active_mods: Set[str] = set()
        self._start = 0.0
        self.allowed_langs: Set[str] = set(LANG_NAMES.keys())
        self.filter_enabled = False
        self.record_mouse = True
        self.record_scroll = True
        self.mode = "typing"
        self._kb = self._ms = None
        self._last_move = 0.0

    def _name(self, key):
        if key in self.SPECIAL:
            return self.SPECIAL[key]
        if hasattr(key, "char") and key.char:
            return key.char
        if hasattr(key, "vk") and key.vk is not None:
            return f"vk_{key.vk}"
        return str(key)

    def _char(self, key):
        try:
            if hasattr(key, "char") and key.char:
                return key.char
        except Exception:
            pass
        return ""

    def _is_mod(self, key) -> bool:
        return key in self.MODIFIER_KEYS

    def start(self):
        self.events.clear()
        self._active_mods.clear()
        self._start = time.time()
        self.is_recording = True
        self._kb = keyboard.Listener(on_press=self._kbp, on_release=self._kbr)
        self._kb.start()
        self._ms = mouse.Listener(on_click=self._mc, on_scroll=self._msc, on_move=self._mm)
        self._ms.start()

    def stop(self) -> List[InputEvent]:
        self.is_recording = False
        for l in (self._kb, self._ms):
            if l:
                try:
                    l.stop()
                except Exception:
                    pass
        self._kb = self._ms = None
        with self._lock:
            return list(self.events)

    def _emit(self, ev):
        with self._lock:
            self.events.append(ev)
        if self.on_event:
            try:
                self.on_event(ev)
            except Exception:
                pass

    def _kbp(self, key):
        if not self.is_recording:
            return
        t = time.time() - self._start
        name = self._name(key)
        ch = self._char(key)
        vk = getattr(key, "vk", None)
        is_mod = self._is_mod(key)
        with self._lock:
            if is_mod:
                self._active_mods.add(NORM_MOD.get(name, name))
            mods = sorted(self._active_mods)
        if ch and self.filter_enabled:
            lang = char_to_lang(ch)
            if lang and lang not in self.allowed_langs:
                return
        self._emit(InputEvent(
            kind="key", action="press", timestamp=t,
            key=name, key_char=ch, vk=vk, modifiers=mods,
            lang=char_to_lang(ch) if ch else ""
        ))

    def _kbr(self, key):
        if not self.is_recording:
            return
        t = time.time() - self._start
        name = self._name(key)
        vk = getattr(key, "vk", None)
        with self._lock:
            if self._is_mod(key):
                self._active_mods.discard(NORM_MOD.get(name, name))
            mods = sorted(self._active_mods)
        self._emit(InputEvent(
            kind="key", action="release", timestamp=t,
            key=name, vk=vk, modifiers=mods
        ))

    def _mc(self, x, y, button, pressed):
        if not self.is_recording or not self.record_mouse:
            return
        if not pressed:
            return
        t = time.time() - self._start
        btn = str(button).split(".")[-1]
        self._emit(InputEvent(
            kind="mouse", action="click", timestamp=t,
            button=btn, x=int(x), y=int(y)
        ))

    def _msc(self, x, y, dx, dy):
        if not self.is_recording or not self.record_scroll:
            return
        t = time.time() - self._start
        self._emit(InputEvent(
            kind="mouse", action="scroll", timestamp=t,
            x=int(x), y=int(y), dx=int(dx), dy=int(dy)
        ))

    def _mm(self, x, y):
        if not self.is_recording or not self.record_mouse:
            return
        if self.mode != "macro":
            return
        now = time.time()
        if now - self._last_move < 0.05:
            return
        self._last_move = now
        self._emit(InputEvent(
            kind="mouse", action="move", timestamp=now - self._start,
            x=int(x), y=int(y)
        ))


# ═══════════════════════════════════════════════════════════
# FILE MANAGER
# ═══════════════════════════════════════════════════════════
class FileManager:
    def __init__(self, directory: Optional[str] = None):
        self.dir = directory or str(Path.home() / "NebulaNote")
        os.makedirs(self.dir, exist_ok=True)
        self.active: Optional[str] = None
        self.recent: List[str] = []

    def new(self, name: Optional[str] = None) -> str:
        if not name:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"note_{ts}.txt"
        p = os.path.join(self.dir, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write("")
        self.active = p
        self._push_recent(p)
        return p

    def save(self, content: str, path: Optional[str] = None) -> str:
        path = path or self.active or self.new()
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self.active = path
        self._push_recent(path)
        return path

    def list(self) -> List[Dict[str, Any]]:
        out = []
        try:
            for f in os.listdir(self.dir):
                p = os.path.join(self.dir, f)
                if os.path.isfile(p):
                    st = os.stat(p)
                    out.append({
                        "name": f, "path": p, "size": st.st_size,
                        "modified": datetime.datetime.fromtimestamp(st.st_mtime)
                    })
        except Exception:
            pass
        return sorted(out, key=lambda x: x["modified"], reverse=True)

    def preview(self, path: str, n: int = 30) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return "".join(f.readlines()[:n])
        except Exception as e:
            return f"({e})"

    def _push_recent(self, p):
        if p in self.recent:
            self.recent.remove(p)
        self.recent.insert(0, p)
        self.recent = self.recent[:10]


# ═══════════════════════════════════════════════════════════
# EXPORTER
# ═══════════════════════════════════════════════════════════
class Exporter:
    @staticmethod
    def to_json(events, path, password=None):
        payload = {
            "exported_at": datetime.datetime.now().isoformat(),
            "count": len(events),
            "events": [asdict(e) for e in events]
        }
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        if password:
            text = xor_encrypt(text, password)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    @staticmethod
    def to_jsonl(events, path):
        with open(path, "w", encoding="utf-8") as f:
            for e in events:
                f.write(json.dumps(asdict(e), ensure_ascii=False) + "\n")

    @staticmethod
    def to_excel(events, path):
        df = pd.DataFrame([asdict(e) for e in events])
        if "modifiers" in df.columns:
            df["modifiers"] = df["modifiers"].apply(
                lambda x: ",".join(x) if isinstance(x, list) else ""
            )
        df.to_excel(path, index=False, engine="openpyxl")

    @staticmethod
    def to_text(events, path):
        with open(path, "w", encoding="utf-8") as f:
            for e in events:
                if e.kind == "key" and e.action == "press":
                    if e.key_char:
                        f.write(e.key_char)
                    elif e.key == "enter":
                        f.write("\n")
                    elif e.key == "space":
                        f.write(" ")
                    elif e.key == "tab":
                        f.write("\t")

    @staticmethod
    def to_markdown(events, path):
        lines = [
            "# Nebula Note Export",
            "",
            f"**Exported:** {datetime.datetime.now().isoformat()}",
            f"**Events:** {len(events)}",
            "",
            "| # | Time | Kind | Action | Key/Button | Details |",
            "|---|------|------|--------|-----------|---------|"
        ]
        for i, e in enumerate(events, 1):
            ts = f"{e.timestamp:.3f}s"
            detail = ""
            if e.kind == "key":
                detail = f"`{e.key}`" + (f" char=`{e.key_char}`" if e.key_char else "")
                if e.modifiers:
                    detail = "+".join(e.modifiers) + "+" + detail
            elif e.kind == "mouse":
                if e.action == "click":
                    detail = f"({e.x},{e.y}) btn={e.button}"
                elif e.action == "scroll":
                    detail = f"({e.x},{e.y}) dx={e.dx} dy={e.dy}"
                elif e.action == "move":
                    detail = f"({e.x},{e.y})"
            lines.append(f"| {i} | {ts} | {e.kind} | {e.action} | {e.key or e.button} | {detail} |")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    @staticmethod
    def to_auto_script(events, path, ui_lang="fa"):
        data = [asdict(e) for e in events]
        data_json = json.dumps(data, ensure_ascii=False)
        T_map = I18N.get(ui_lang, I18N["fa"])
        labels = {k: T_map.get(k, k) for k in
                  ["pl_rep", "pl_delay", "pl_speed", "pl_dur", "pl_run", "pl_stop", "pl_ready"]}
        labels_json = json.dumps(labels, ensure_ascii=False)
        script = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auto-generated playback script by Nebula Note """
import tkinter as tk
import json, time, threading, sys
try:
    from pynput import keyboard, mouse
except ImportError:
    print("Install: py -m pip install pynput"); sys.exit(1)

EVENTS = json.loads(r"""{data_json}""")
LABELS = json.loads(r"""{labels_json}""")

SPECIAL_MAP = {{}}
for _n in ["ctrl","ctrl_l","ctrl_r","shift","shift_l","shift_r","alt","alt_l",
           "alt_r","alt_gr","cmd","cmd_l","cmd_r","enter","tab","space","backspace",
           "delete","esc","up","down","left","right","home","end","page_up",
           "page_down","f1","f2","f3","f4","f5","f6","f7","f8","f9","f10","f11","f12"]:
    try: SPECIAL_MAP[_n] = getattr(keyboard.Key, _n)
    except AttributeError: pass

def resolve(ev):
    n = ev.get("key",""); c = ev.get("key_char","")
    if n in SPECIAL_MAP: return SPECIAL_MAP[n]
    if c: return c
    if len(n) == 1: return n
    return None

def play_once(events, k, m, speed, duration, stop):
    events = sorted(events, key=lambda e: e["timestamp"])
    prev = 0.0; t0 = time.time()
    for ev in events:
        if stop[0]: return
        if duration > 0 and (time.time() - t0) > duration: return
        d = (ev["timestamp"] - prev) / max(0.01, speed)
        if d > 0: time.sleep(d)
        prev = ev["timestamp"]
        try:
            if ev["kind"] == "key":
                kk = resolve(ev)
                if kk is None: continue
                if ev["action"] == "press": k.press(kk)
                else: k.release(kk)
            elif ev["kind"] == "mouse":
                a = ev["action"]
                if a == "click":
                    m.position = (ev["x"], ev["y"])
                    b = {{"left":mouse.Button.left,"right":mouse.Button.right,
                         "middle":mouse.Button.middle}}.get(ev.get("button","left"), mouse.Button.left)
                    m.click(b)
                elif a == "scroll":
                    m.position = (ev["x"], ev["y"])
                    m.scroll(ev.get("dx",0), ev.get("dy",0))
                elif a == "move":
                    m.position = (ev["x"], ev["y"])
        except Exception: pass

BG="#07071a"; SURF="#16163a"; ACC="#00d9ff"; TXT="#e0e0ff"
root = tk.Tk(); root.title("Nebula Playback"); root.geometry("380x360")
root.configure(bg=BG); root.attributes("-topmost", True)
tk.Label(root, text="✦ Nebula Playback", bg=BG, fg=ACC,
         font=("Segoe UI Emoji",12,"bold")).pack(pady=10)
frame = tk.Frame(root, bg=BG); frame.pack(padx=20, pady=6, fill="x")
def row(label, default):
    f = tk.Frame(frame, bg=BG); f.pack(fill="x", pady=3)
    tk.Label(f, text=label, bg=BG, fg=TXT, width=22, anchor="w",
             font=("Segoe UI Emoji",9)).pack(side="left")
    e = tk.Entry(f, bg=SURF, fg=TXT, insertbackground=ACC,
                 font=("Segoe UI Emoji",9), bd=0, relief="flat")
    e.insert(0, str(default))
    e.pack(side="right", fill="x", expand=True, ipady=3, padx=(6,0))
    return e
e_rep = row(LABELS.get("pl_rep","Repeat"), 1)
e_delay = row(LABELS.get("pl_delay","Delay"), 2.0)
e_speed = row(LABELS.get("pl_speed","Speed"), 1.0)
e_dur = row(LABELS.get("pl_dur","Duration"), 0)
status = tk.Label(root, text=LABELS.get("pl_ready","Ready"), bg=BG, fg=TXT,
                  font=("Segoe UI Emoji",9))
status.pack(pady=6)
stop = [False]; running = [False]
def run():
    if running[0]: return
    try:
        rep = max(1, int(e_rep.get())); dl = max(0.0, float(e_delay.get()))
        sp = max(0.01, float(e_speed.get())); du = max(0.0, float(e_dur.get()))
    except ValueError:
        status.config(text="Invalid input", fg="#ff3860"); return
    running[0] = True; stop[0] = False
    def worker():
        time.sleep(dl)
        k = keyboard.Controller(); m = mouse.Controller()
        for i in range(rep):
            if stop[0]: break
            status.config(text=f"{{i+1}}/{{rep}}")
            play_once(EVENTS, k, m, sp, du, stop)
        running[0] = False
        root.after(0, lambda: status.config(text=LABELS.get("pl_ready","Ready"), fg=TXT))
    threading.Thread(target=worker, daemon=True).start()
def halt():
    stop[0] = True; running[0] = False
    status.config(text="Stopped", fg="#ff3860")
bf = tk.Frame(root, bg=BG); bf.pack(pady=10)
tk.Button(bf, text=LABELS.get("pl_run","Run"), command=run,
          bg="#00ffa3", fg="#07071a", bd=0, font=("Segoe UI Emoji",10,"bold"),
          padx=18, pady=6, cursor="hand2").pack(side="left", padx=6)
tk.Button(bf, text=LABELS.get("pl_stop","Stop"), command=halt,
          bg="#ff3860", fg="#ffffff", bd=0, font=("Segoe UI Emoji",10,"bold"),
          padx=18, pady=6, cursor="hand2").pack(side="left", padx=6)
tk.Label(root, text="made by ma.ad.gh mahanneman",
         bg=BG, fg="#6a6a92", font=("Segoe UI Emoji",7)).pack(side="bottom", pady=4)
root.mainloop()
'''
        with open(path, "w", encoding="utf-8") as f:
            f.write(script)


# ═══════════════════════════════════════════════════════════
# FLOATING ICON (true transparent triangle)
# ═══════════════════════════════════════════════════════════
class FloatingIcon:
    SIZE = 48
    # Magenta key used for transparency on Windows
    TRANS = "#ff00ff"

    def __init__(self, master, on_restore, registry, on_toggle_preview=None):
        self.on_restore = on_restore
        self.registry = registry
        self.on_toggle_preview = on_toggle_preview
        self._rec_state = False
        self._blink_id = None
        self._blink_on = True
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        # True transparency: magenta becomes invisible
        try:
            self.win.wm_attributes("-transparentcolor", self.TRANS)
        except Exception:
            try:
                self.win.attributes("-alpha", 0.92)
            except Exception:
                pass
        self.win.configure(bg=self.TRANS)
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        x = sw - self.SIZE - 20
        y = sh - self.SIZE - 90
        self.win.geometry(f"{self.SIZE}x{self.SIZE}+{x}+{y}")
        self.canvas = tk.Canvas(
            self.win, width=self.SIZE, height=self.SIZE,
            bg=self.TRANS, highlightthickness=0, bd=0
        )
        self.canvas.pack()
        self._draw()
        self.canvas.bind("<Button-1>", self._p)
        self.canvas.bind("<B1-Motion>", self._d)
        self.canvas.bind("<ButtonRelease-1>", self._r)
        self.canvas.bind("<Double-Button-1>", lambda e: self.on_restore())
        self.canvas.bind("<Button-3>", self._rc)
        Tooltip(self.canvas, "tip_min", registry)
        self._st = {"x": 0, "y": 0, "moved": False}

    def set_recording(self, active: bool):
        self._rec_state = active
        if active and self._blink_id is None:
            self._blink()
        elif not active and self._blink_id is not None:
            try:
                self.win.after_cancel(self._blink_id)
            except Exception:
                pass
            self._blink_id = None
            self._blink_on = True
            self._draw()

    def _blink(self):
        if not self._rec_state:
            return
        self._blink_on = not self._blink_on
        self._draw()
        try:
            self._blink_id = self.win.after(450, self._blink)
        except Exception:
            self._blink_id = None

    def _draw(self):
        s = self.SIZE
        cx = cy = s // 2
        self.canvas.delete("all")
        # Outer triangle (glow edge)
        r = s // 2 - 3
        pts = [(cx, cy - r), (cx - r * 0.866, cy + r * 0.5), (cx + r * 0.866, cy + r * 0.5)]
        self.canvas.create_polygon(
            [c for p in pts for c in p],
            fill=C["bg_light"], outline=C["accent"], width=2
        )
        # Inner triangle
        r2 = r * 0.52
        pts2 = [
            (cx, cy - r2 + 1),
            (cx - r2 * 0.866, cy + r2 * 0.5 + 1),
            (cx + r2 * 0.866, cy + r2 * 0.5 + 1)
        ]
        self.canvas.create_polygon(
            [c for p in pts2 for c in p],
            fill=C["surface"], outline=C["accent2"], width=1
        )
        # Center status dot
        dot_color = C["accent"]
        if self._rec_state:
            dot_color = C["danger"] if self._blink_on else C["bg_light"]
        self.canvas.create_oval(cx - 3, cy + 2, cx + 3, cy + 8, fill=dot_color, outline="")

    def _p(self, e):
        self._st = {"x": e.x, "y": e.y, "moved": False}

    def _d(self, e):
        dx = e.x - self._st["x"]
        dy = e.y - self._st["y"]
        if abs(dx) > 3 or abs(dy) > 3:
            self._st["moved"] = True
        x = self.win.winfo_x() + dx
        y = self.win.winfo_y() + dy
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        x = max(0, min(x, sw - self.SIZE))
        y = max(0, min(y, sh - self.SIZE))
        self.win.geometry(f"+{x}+{y}")

    def _r(self, e):
        if not self._st["moved"]:
            self.on_restore()

    def _rc(self, e):
        m = tk.Menu(
            self.win, tearoff=0, bg=C["surface"], fg=C["text"],
            activebackground=C["accent"], activeforeground=C["bg"]
        )
        if self.on_toggle_preview:
            m.add_command(label="◈ Live Preview", command=self.on_toggle_preview)
        m.add_command(label=T("close", self.registry.lang), command=self.win.master.quit)
        try:
            m.tk_popup(e.x_root, e.y_root)
        finally:
            try:
                m.grab_release()
            except Exception:
                pass

    def destroy(self):
        if self._blink_id:
            try:
                self.win.after_cancel(self._blink_id)
            except Exception:
                pass
            self._blink_id = None
        try:
            self.win.destroy()
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════
# MINI PREVIEW
# ═══════════════════════════════════════════════════════════
class MiniPreview:
    W = 280
    H = 110

    def __init__(self, master, registry, text_getter):
        self.text_getter = text_getter
        self.registry = registry
        self.visible = True
        self._alive = True
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        try:
            self.win.attributes("-alpha", 0.94)
        except Exception:
            pass
        self.win.configure(bg=C["bg"])
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        x = sw - self.W - 70
        y = sh - self.H - 120
        self.win.geometry(f"{self.W}x{self.H}+{x}+{y}")
        hdr = tk.Frame(self.win, bg=C["surface"], height=20)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        self.title_lbl = tk.Label(
            hdr, text=" ◈ Live Preview",
            bg=C["surface"], fg=C["accent"],
            font=("Segoe UI Emoji", 8, "bold")
        )
        self.title_lbl.pack(side="left", padx=4)
        tk.Button(
            hdr, text="✕", command=self.hide, bg=C["surface"],
            fg=C["danger"], bd=0, font=("Segoe UI Emoji", 8, "bold"),
            width=2, cursor="hand2", activebackground=C["surface_hi"]
        ).pack(side="right")
        self.content = tk.Label(
            self.win, text="", bg=C["bg_light"],
            fg=C["text"], font=("Consolas", 8),
            anchor="nw", justify="left",
            wraplength=self.W - 12, padx=6, pady=4
        )
        self.content.pack(fill="both", expand=True)
        for w in (hdr, self.title_lbl, self.content):
            w.bind("<Button-1>", self._drag_start)
            w.bind("<B1-Motion>", self._drag_move)
        self._last = None
        self._tick()

    def _drag_start(self, e):
        self._dx = e.x_root - self.win.winfo_x()
        self._dy = e.y_root - self.win.winfo_y()

    def _drag_move(self, e):
        x = e.x_root - self._dx
        y = e.y_root - self._dy
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        x = max(0, min(x, sw - self.W))
        y = max(0, min(y, sh - self.H))
        self.win.geometry(f"+{x}+{y}")

    def _tick(self):
        if not self._alive:
            return
        try:
            t = self.text_getter() or ""
            if t != self._last:
                self._last = t
                preview = t[-400:] if len(t) > 400 else t
                self.content.config(text=preview if preview.strip() else "…")
        except Exception:
            pass
        try:
            self.win.after(150, self._tick)
        except Exception:
            pass

    def show(self):
        self.visible = True
        try:
            self.win.deiconify()
        except Exception:
            pass

    def hide(self):
        self.visible = False
        try:
            self.win.withdraw()
        except Exception:
            pass

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def destroy(self):
        self._alive = False
        try:
            self.win.destroy()
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════
# DIALOGS (Language, UI Lang, Find/Replace, Snippets, Settings, Stats)
# ═══════════════════════════════════════════════════════════
class LanguageDialog:
    def __init__(self, master, current, detected, lang):
        self.result = None
        self.current = set(current)
        self.detected = detected
        self.lang = lang
        self.win = tk.Toplevel(master)
        self.win.title(T("lang_title", lang))
        self.win.geometry("400x540")
        self.win.configure(bg=C["bg"])
        self.win.attributes("-topmost", True)
        try:
            self.win.transient(master)
            self.win.grab_set()
        except Exception:
            pass
        self.vars: Dict[str, tk.BooleanVar] = {}
        tk.Label(
            self.win, text=T("lang_title", lang), bg=C["bg"],
            fg=C["accent"], font=("Segoe UI Emoji", 12, "bold")
        ).pack(pady=10)
        frame = tk.Frame(self.win, bg=C["bg"])
        frame.pack(fill="both", expand=True, padx=14, pady=6)
        for code, name in LANG_NAMES.items():
            r = tk.Frame(frame, bg=C["bg"])
            r.pack(fill="x", pady=1)
            v = tk.BooleanVar(value=(code in self.current))
            self.vars[code] = v
            tk.Checkbutton(
                r, text=f"  {name}   [{code}]", variable=v,
                bg=C["bg"], fg=C["text"], selectcolor=C["surface_hi"],
                activebackground=C["bg"], activeforeground=C["accent"],
                font=F["body"], anchor="w", bd=0, highlightthickness=0
            ).pack(side="left", fill="x", expand=True)
            if code in detected:
                tk.Label(
                    r, text="• " + T("installed", lang), bg=C["bg"],
                    fg=C["success"], font=F["tiny"]
                ).pack(side="right", padx=6)
        bar = tk.Frame(self.win, bg=C["bg"])
        bar.pack(fill="x", padx=14, pady=8)

        def btn(t, cmd, primary=False):
            bg = C["accent"] if primary else C["surface"]
            fg = C["bg"] if primary else C["text"]
            return tk.Button(
                bar, text=t, command=cmd, bg=bg, fg=fg, bd=0,
                font=F["small"], padx=10, pady=4, cursor="hand2",
                activebackground=C["accent2"], activeforeground=C["white"]
            )

        btn(T("all", lang), lambda: [v.set(True) for v in self.vars.values()]).pack(side="left", padx=2)
        btn(T("none", lang), lambda: [v.set(False) for v in self.vars.values()]).pack(side="left", padx=2)
        btn(T("installed", lang), lambda: [self.vars[c].set(c in detected) for c in self.vars]).pack(side="left", padx=2)
        btn(T("confirm", lang), self._ok, True).pack(side="right", padx=2)
        btn(T("cancel", lang), self._cancel).pack(side="right", padx=2)

    def _ok(self):
        self.result = {c for c, v in self.vars.items() if v.get()}
        self.win.destroy()

    def _cancel(self):
        self.result = None
        self.win.destroy()

    def show(self):
        self.win.wait_window()
        return self.result


class UILangDialog:
    def __init__(self, master, current, lang):
        self.result = None
        self.win = tk.Toplevel(master)
        self.win.title(T("ui_lang_title", lang))
        self.win.geometry("300x340")
        self.win.configure(bg=C["bg"])
        self.win.attributes("-topmost", True)
        try:
            self.win.transient(master)
            self.win.grab_set()
        except Exception:
            pass
        tk.Label(
            self.win, text=T("ui_lang_title", lang), bg=C["bg"],
            fg=C["accent"], font=("Segoe UI Emoji", 12, "bold")
        ).pack(pady=12)
        for code in UI_LANGS:
            label = LANG_NAMES.get(code, code)
            marker = "●" if code == current else "○"
            tk.Button(
                self.win, text=f"{marker}  {label}",
                command=lambda c=code: self._pick(c),
                bg=C["surface"], fg=C["text"], bd=0, font=F["body"],
                cursor="hand2", activebackground=C["accent"],
                activeforeground=C["bg"], padx=12, pady=6, width=28
            ).pack(pady=3)

    def _pick(self, code):
        self.result = code
        self.win.destroy()

    def show(self):
        self.win.wait_window()
        return self.result


class FindReplaceDialog:
    def __init__(self, master, text_widget, lang):
        self.text = text_widget
        self.lang = lang
        self.win = tk.Toplevel(master)
        self.win.title(T("find_title", lang))
        self.win.geometry("440x230")
        self.win.configure(bg=C["bg"])
        self.win.attributes("-topmost", True)
        try:
            self.win.transient(master)
        except Exception:
            pass
        tk.Label(
            self.win, text=T("find_what", lang), bg=C["bg"], fg=C["text"],
            font=F["body"]
        ).grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.e_find = tk.Entry(
            self.win, bg=C["surface"], fg=C["text"],
            insertbackground=C["accent"], font=F["body"], bd=0
        )
        self.e_find.grid(row=0, column=1, sticky="ew", padx=8, pady=8, ipady=4)
        tk.Label(
            self.win, text=T("find_with", lang), bg=C["bg"], fg=C["text"],
            font=F["body"]
        ).grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.e_repl = tk.Entry(
            self.win, bg=C["surface"], fg=C["text"],
            insertbackground=C["accent"], font=F["body"], bd=0
        )
        self.e_repl.grid(row=1, column=1, sticky="ew", padx=8, pady=8, ipady=4)
        self.win.grid_columnconfigure(1, weight=1)
        bf = tk.Frame(self.win, bg=C["bg"])
        bf.grid(row=2, column=0, columnspan=2, pady=10)
        for t, cmd in [
            (T("find_prev", lang), self._prev),
            (T("find_next", lang), self._next),
            (T("find_all", lang), self._all),
            (T("replace", lang), self._replace),
            (T("close", lang), self.win.destroy)
        ]:
            tk.Button(
                bf, text=t, command=cmd, bg=C["surface"], fg=C["text"],
                bd=0, font=F["small"], padx=10, pady=4, cursor="hand2",
                activebackground=C["accent"], activeforeground=C["bg"]
            ).pack(side="left", padx=3)
        self.e_find.focus_set()

    def _next(self):
        q = self.e_find.get()
        if not q:
            return
        pos = self.text.search(q, "insert", nocase=True)
        if not pos:
            pos = self.text.search(q, "1.0", nocase=True)
        if pos:
            self.text.mark_set("insert", f"{pos}+{len(q)}c")
            self.text.see(pos)
            self.text.tag_remove("sel", "1.0", "end")
            self.text.tag_add("sel", pos, f"{pos}+{len(q)}c")

    def _prev(self):
        q = self.e_find.get()
        if not q:
            return
        pos = self.text.search(q, "insert", backwards=True, nocase=True)
        if not pos:
            pos = self.text.search(q, "end", backwards=True, nocase=True)
        if pos:
            self.text.mark_set("insert", pos)
            self.text.see(pos)
            self.text.tag_remove("sel", "1.0", "end")
            self.text.tag_add("sel", pos, f"{pos}+{len(q)}c")

    def _all(self):
        q = self.e_find.get()
        if not q:
            return
        self.text.tag_remove("sel", "1.0", "end")
        start = "1.0"
        count = 0
        while True:
            pos = self.text.search(q, start, nocase=True, stopindex="end")
            if not pos:
                break
            self.text.tag_add("sel", pos, f"{pos}+{len(q)}c")
            start = f"{pos}+{len(q)}c"
            count += 1
        messagebox.showinfo("Find", f"{count} matches")

    def _replace(self):
        q = self.e_find.get()
        r = self.e_repl.get()
        if not q:
            return
        pos = self.text.search(q, "insert", nocase=True)
        if not pos:
            pos = self.text.search(q, "1.0", nocase=True)
        if pos:
            self.text.delete(pos, f"{pos}+{len(q)}c")
            self.text.insert(pos, r)


class SnippetsDialog:
    """Full snippet manager: insert, add, edit, delete, assign Ctrl+1/2/3"""

    def __init__(self, master, app, on_insert):
        self.app = app
        self.on_insert = on_insert
        self.lang = app.registry.lang
        self.snippets = [dict(s) for s in app.config.get_snippets()]
        self.win = tk.Toplevel(master)
        self.win.title(T("snippets_title", self.lang))
        self.win.geometry("420x560")
        self.win.configure(bg=C["bg"])
        self.win.attributes("-topmost", True)
        try:
            self.win.transient(master)
            self.win.grab_set()
        except Exception:
            pass

        tk.Label(
            self.win, text="✂ الگوهای آماده  (Ctrl+Shift+1 / 2 / 3)",
            bg=C["bg"], fg=C["accent"], font=("Segoe UI Emoji", 11, "bold")
        ).pack(pady=(10, 4))

        leg = tk.Frame(self.win, bg=C["bg"])
        leg.pack(fill="x", padx=12, pady=2)
        for i, col in [(1, C["success"]), (2, C["warning"]), (3, C["accent2"])]:
            s = self._slot_label(i)
            tk.Label(leg, text=f"  Ctrl+Shift+{i} → {s}  ", bg=C["surface"], fg=col,
                     font=F["tiny"], padx=4, pady=2).pack(side="left", padx=2)

        # List
        list_fr = tk.Frame(self.win, bg=C["bg"])
        list_fr.pack(fill="both", expand=True, padx=12, pady=6)
        self.lb = tk.Listbox(
            list_fr, bg=C["bg_light"], fg=C["text"], font=F["body"],
            selectbackground=C["accent"], selectforeground=C["bg"],
            bd=0, highlightthickness=0, activestyle="none", height=14
        )
        self.lb.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(list_fr, command=self.lb.yview)
        sb.pack(side="right", fill="y")
        self.lb.config(yscrollcommand=sb.set)
        self.lb.bind("<Double-Button-1>", lambda e: self._insert_selected())
        self._refresh_list()

        # Buttons row 1
        bf1 = tk.Frame(self.win, bg=C["bg"])
        bf1.pack(fill="x", padx=12, pady=3)
        for txt, cmd, col in [
            ("▶ درج", self._insert_selected, C["success"]),
            ("＋ جدید", self._add, C["accent"]),
            ("✎ ویرایش", self._edit, C["warning"]),
            ("🗑 حذف", self._delete, C["danger"]),
        ]:
            tk.Button(bf1, text=txt, command=cmd, bg=C["surface"], fg=col,
                      bd=0, font=F["small"], padx=8, pady=4, cursor="hand2",
                      activebackground=col, activeforeground=C["bg"]).pack(side="left", padx=2, fill="x", expand=True)

        # Slot assign row
        bf2 = tk.Frame(self.win, bg=C["bg"])
        bf2.pack(fill="x", padx=12, pady=3)
        tk.Label(bf2, text="اختصاص به:", bg=C["bg"], fg=C["text_dim"], font=F["tiny"]).pack(side="left")
        for slot, col in [(1, C["success"]), (2, C["warning"]), (3, C["accent2"]), (0, C["text_dim"])]:
            label = f"Ctrl+Shift+{slot}" if slot else "هیچ"
            tk.Button(bf2, text=label, command=lambda s=slot: self._assign_slot(s),
                      bg=C["surface"], fg=col, bd=0, font=F["tiny"],
                      padx=6, pady=3, cursor="hand2").pack(side="left", padx=2)

        # Close
        tk.Button(self.win, text=T("close", self.lang), command=self._close,
                  bg=C["surface"], fg=C["text"], bd=0, font=F["small"],
                  padx=14, pady=5, cursor="hand2").pack(pady=8)

    def _slot_label(self, slot):
        for s in self.snippets:
            if s.get("slot") == slot:
                return s.get("label", "?")[:18]
        return "—"

    def _refresh_list(self):
        self.lb.delete(0, "end")
        for s in self.snippets:
            slot = s.get("slot", 0)
            mark = f" [Ctrl+Shift+{slot}]" if slot in (1, 2, 3) else ""
            self.lb.insert("end", f"  {s.get('label', '?')}{mark}")

    def _selected_idx(self):
        sel = self.lb.curselection()
        return sel[0] if sel else None

    def _expand(self, text: str) -> str:
        now = datetime.datetime.now()
        text = text.replace("HH:MM:SS", now.strftime("%H:%M:%S"))
        text = text.replace("YYYY-MM-DD", now.strftime("%Y-%m-%d"))
        text = text.replace("[تاریخ]", now.strftime("%Y-%m-%d"))
        text = text.replace("[ساعت]", now.strftime("%H:%M:%S"))
        text = text.replace("[Date]", now.strftime("%Y-%m-%d"))
        text = text.replace("[Time]", now.strftime("%H:%M:%S"))
        return text

    def _insert_selected(self):
        i = self._selected_idx()
        if i is None:
            return
        text = self._expand(self.snippets[i].get("text", ""))
        self.on_insert(text)
        self._close()

    def _assign_slot(self, slot: int):
        i = self._selected_idx()
        if i is None:
            return
        # Clear previous owner of this slot
        if slot in (1, 2, 3):
            for s in self.snippets:
                if s.get("slot") == slot:
                    s["slot"] = 0
        self.snippets[i]["slot"] = slot
        self._refresh_list()
        self.lb.selection_set(i)

    def _add(self):
        self._edit_dialog(None)

    def _edit(self):
        i = self._selected_idx()
        if i is None:
            return
        self._edit_dialog(i)

    def _edit_dialog(self, idx):
        is_new = idx is None
        data = {"label": "", "text": "", "slot": 0} if is_new else dict(self.snippets[idx])
        d = tk.Toplevel(self.win)
        d.title("الگو" if is_new else "ویرایش")
        d.geometry("360x280")
        d.configure(bg=C["bg"])
        d.attributes("-topmost", True)
        tk.Label(d, text="نام:", bg=C["bg"], fg=C["text"], font=F["small"]).pack(anchor="w", padx=12, pady=(10, 2))
        e_label = tk.Entry(d, bg=C["surface"], fg=C["text"], insertbackground=C["accent"], font=F["body"], bd=0)
        e_label.pack(fill="x", padx=12, ipady=4)
        e_label.insert(0, data.get("label", ""))
        tk.Label(d, text="متن (از YYYY-MM-DD و HH:MM:SS استفاده کن):", bg=C["bg"], fg=C["text"], font=F["small"]).pack(anchor="w", padx=12, pady=(8, 2))
        e_text = tk.Text(d, bg=C["surface"], fg=C["text"], insertbackground=C["accent"],
                         font=F["body"], bd=0, height=5, wrap="word")
        e_text.pack(fill="both", expand=True, padx=12, pady=2)
        e_text.insert("1.0", data.get("text", ""))

        def save():
            label = e_label.get().strip() or "بدون نام"
            text = e_text.get("1.0", "end-1c")
            if is_new:
                import uuid
                self.snippets.append({"id": str(uuid.uuid4())[:8], "label": label, "text": text, "slot": 0})
            else:
                self.snippets[idx]["label"] = label
                self.snippets[idx]["text"] = text
            self._refresh_list()
            d.destroy()

        tk.Button(d, text="ذخیره", command=save, bg=C["accent"], fg=C["bg"],
                  bd=0, font=F["small"], padx=14, pady=5, cursor="hand2").pack(pady=10)

    def _delete(self):
        i = self._selected_idx()
        if i is None:
            return
        del self.snippets[i]
        self._refresh_list()

    def _close(self):
        self.app.config.set_snippets(self.snippets)
        try:
            self.win.destroy()
        except Exception:
            pass


class SettingsDialog:
    def __init__(self, master, app, lang):
        self.app = app
        self.lang = lang
        self.win = tk.Toplevel(master)
        self.win.title(T("settings_title", lang))
        self.win.geometry("420x480")
        self.win.configure(bg=C["bg"])
        self.win.attributes("-topmost", True)
        try:
            self.win.transient(master)
            self.win.grab_set()
        except Exception:
            pass
        tk.Label(
            self.win, text="⚙ " + T("settings_title", lang), bg=C["bg"],
            fg=C["accent"], font=("Segoe UI Emoji", 12, "bold")
        ).pack(pady=10)
        body = tk.Frame(self.win, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=14, pady=6)

        def row(label, default):
            f = tk.Frame(body, bg=C["bg"])
            f.pack(fill="x", pady=4)
            tk.Label(
                f, text=label, bg=C["bg"], fg=C["text"],
                font=F["body"], anchor="w", width=28
            ).pack(side="left")
            e = tk.Entry(
                f, bg=C["surface"], fg=C["text"],
                insertbackground=C["accent"], font=F["body"],
                bd=0, relief="flat", width=10
            )
            e.insert(0, str(default))
            e.pack(side="right", ipady=3, padx=(6, 0))
            return e

        self.e_autosave = row(T("set_autosave", lang), app.autosave_interval)
        self.e_countdown = row(T("set_countdown", lang), app.countdown)
        self.e_font = row(T("set_font", lang), app.font_size)
        self.e_opacity = row(T("set_opacity", lang), app.window_opacity)

        def chk(text, var):
            f = tk.Frame(body, bg=C["bg"])
            f.pack(fill="x", pady=3)
            tk.Checkbutton(
                f, text=text, variable=var, bg=C["bg"], fg=C["text"],
                selectcolor=C["surface_hi"], activebackground=C["bg"],
                activeforeground=C["accent"], font=F["body"],
                anchor="w", bd=0, highlightthickness=0
            ).pack(side="left")

        self.v_sound = tk.BooleanVar(value=app.sound_enabled)
        self.v_encrypt = tk.BooleanVar(value=app.encrypt_export)
        self.v_filter = tk.BooleanVar(value=app.filter_enabled)
        chk(T("set_sound", lang), self.v_sound)
        chk(T("set_encrypt", lang), self.v_encrypt)
        chk(T("set_filter", lang), self.v_filter)

        bar = tk.Frame(self.win, bg=C["bg"])
        bar.pack(fill="x", pady=10)

        def btn(t, cmd, primary=False):
            bg = C["accent"] if primary else C["surface"]
            fg = C["bg"] if primary else C["text"]
            return tk.Button(
                bar, text=t, command=cmd, bg=bg, fg=fg, bd=0,
                font=F["small"], padx=14, pady=5, cursor="hand2",
                activebackground=C["accent2"], activeforeground=C["white"]
            )

        btn(T("set_apply", lang), self._apply, True).pack(side="right", padx=6)
        btn(T("set_reset", lang), self._reset).pack(side="right", padx=6)
        btn(T("cancel", lang), self.win.destroy).pack(side="right", padx=6)

    def _apply(self):
        try:
            self.app.autosave_interval = max(0, int(self.e_autosave.get()))
            self.app.countdown = max(0, int(self.e_countdown.get()))
            self.app.font_size = max(6, min(24, int(self.e_font.get())))
            self.app.window_opacity = max(0.5, min(1.0, float(self.e_opacity.get())))
            self.app.sound_enabled = self.v_sound.get()
            self.app.encrypt_export = self.v_encrypt.get()
            self.app.filter_enabled = self.v_filter.get()
            self.app.engine.filter_enabled = self.app.filter_enabled
            self.app._apply_runtime_settings()
            self.app.config.set("autosave_interval", self.app.autosave_interval)
            self.app.config.set("countdown", self.app.countdown)
            self.app.config.set("font_size", self.app.font_size)
            self.app.config.set("window_opacity", self.app.window_opacity)
            self.app.config.set("sound_enabled", self.app.sound_enabled)
            self.app.config.set("encrypt_export", self.app.encrypt_export)
            self.app.config.set("filter_enabled", self.app.filter_enabled)
            self.app.config.save()
            self.win.destroy()
        except ValueError:
            messagebox.showerror("!", "Invalid value")

    def _reset(self):
        self.e_autosave.delete(0, "end")
        self.e_autosave.insert(0, "30")
        self.e_countdown.delete(0, "end")
        self.e_countdown.insert(0, "0")
        self.e_font.delete(0, "end")
        self.e_font.insert(0, "9")
        self.e_opacity.delete(0, "end")
        self.e_opacity.insert(0, "1.0")
        self.v_sound.set(True)
        self.v_encrypt.set(False)
        self.v_filter.set(False)


class StatsDialog:
    def __init__(self, master, app, lang):
        self.win = tk.Toplevel(master)
        self.win.title(T("stats_title", lang))
        self.win.geometry("440x520")
        self.win.configure(bg=C["bg"])
        self.win.attributes("-topmost", True)
        tk.Label(
            self.win, text="📊 " + T("stats_title", lang), bg=C["bg"],
            fg=C["accent"], font=("Segoe UI Emoji", 12, "bold")
        ).pack(pady=10)
        evs = app.recorded_events
        total = len(evs)
        keys = sum(1 for e in evs if e.kind == "key" and e.action == "press")
        clicks = sum(1 for e in evs if e.kind == "mouse" and e.action == "click")
        scrolls = sum(1 for e in evs if e.kind == "mouse" and e.action == "scroll")
        moves = sum(1 for e in evs if e.kind == "mouse" and e.action == "move")
        dur = (evs[-1].timestamp if evs else 0)
        langs = set()
        for e in evs:
            if e.lang:
                langs.add(e.lang)
        counter = Counter()
        for e in evs:
            if e.kind == "key" and e.action == "press":
                k = e.key_char if e.key_char else e.key
                counter[k] += 1
        top = counter.most_common(12)
        text = scrolledtext.ScrolledText(
            self.win, wrap="word",
            bg=C["bg_light"], fg=C["text"],
            font=("Consolas", 9),
            bd=0, padx=12, pady=10
        )
        text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        L = lang
        lines = [
            f"{T('stats_total', L)}:      {total}",
            f"{T('stats_keys', L)}:       {keys}",
            f"{T('stats_clicks', L)}:     {clicks}",
            f"{T('stats_scrolls', L)}:    {scrolls}",
            f"{T('stats_moves', L)}:      {moves}",
            f"{T('stats_duration', L)}:   {dur:.2f}s",
            f"{T('stats_langs', L)}:      {', '.join(sorted(langs)) or T('stats_none', L)}",
            "",
            f"─ {T('stats_top', L)} ─",
        ]
        for k, n in top:
            disp = k if k else "(special)"
            lines.append(f"  {disp:14s}  →  {n}")
        text.insert("1.0", "\n".join(lines))
        text.config(state="disabled")
        tk.Button(
            self.win, text=T("close", L), command=self.win.destroy,
            bg=C["surface"], fg=C["text"], bd=0, font=F["body"],
            padx=16, pady=6, cursor="hand2"
        ).pack(pady=(0, 10))


# ═══════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════
class NebulaNote:
    HOTKEYS = {
        "start_stop": "<ctrl>+<shift>+q", "save": "<ctrl>+<shift>+w",
        "switch": "<ctrl>+<shift>+e", "ontop": "<ctrl>+<shift>+a",
        "replay": "<ctrl>+<shift>+z", "float": "<ctrl>+<shift>+x",
        "clear": "<ctrl>+<shift>+c", "files": "<ctrl>+<shift>+f",
        "export": "<ctrl>+<shift>+g", "lang": "<ctrl>+<shift>+r",
        "ui_lang": "<ctrl>+<shift>+u", "mouse": "<ctrl>+<shift>+t",
        "scroll": "<ctrl>+<shift>+b", "help": "<ctrl>+<shift>+h",
        "duplicate": "<ctrl>+<shift>+d", "new_file": "<ctrl>+<shift>+n",
        "open_dir": "<ctrl>+<shift>+o",
        "speed_up": "<ctrl>+<shift>+<up>", "speed_down": "<ctrl>+<shift>+<down>",
        "settings": "<ctrl>+<shift>+k", "stats": "<ctrl>+<shift>+i",
        "import": "<ctrl>+<shift>+v", "sound": "<ctrl>+<shift>+l",
        "autosave": "<ctrl>+<shift>+y", "font_up": "<ctrl>+<shift>+p",
        "font_dn": "<ctrl>+<shift>+m", "opacity": "<ctrl>+<shift>+j",
        "preview": "<ctrl>+<shift>+9",
        "snippets": "<ctrl>+<shift>+s",
        "readonly": "<ctrl>+<shift>+<f1>",
        "ins_line": "<ctrl>+<shift>+0", "ins_time": "<ctrl>+<shift>+6",
        "ins_date": "<ctrl>+<shift>+7", "ins_bullet": "<ctrl>+<shift>+8",
        # Quick snippet slots — Ctrl+Shift+1/2/3 (avoids conflict with plain Ctrl)
        "slot1": "<ctrl>+<shift>+1", "slot2": "<ctrl>+<shift>+2", "slot3": "<ctrl>+<shift>+3",
        "ui_fa": "<ctrl>+<shift>+4", "ui_en": "<ctrl>+<shift>+5",
        "ui_ar": "<ctrl>+<shift>+6", "ui_de": "<ctrl>+<shift>+7",
        "ui_fr": "<ctrl>+<shift>+8",
    }

    def __init__(self):
        self.config = ConfigManager()
        self.registry = I18nRegistry()
        self.registry.lang = self.config.get("ui_lang", "fa")

        self.root = tk.Tk()
        self.root.geometry("360x520")
        self.root.minsize(320, 460)
        self.root.configure(bg=C["bg"])
        self.root.attributes("-topmost", True)

        # State from config
        self.is_recording = False
        self.always_on_top = self.config.get("always_on_top", True)
        self.mode = self.config.get("mode", "typing")
        self.detected_langs = detect_installed_languages()
        self.allowed_langs = set(LANG_NAMES.keys())
        self.filter_enabled = self.config.get("filter_enabled", False)
        self.record_mouse = self.config.get("record_mouse", True)
        self.record_scroll = self.config.get("record_scroll", True)
        self.text_buffer = ""
        self.recorded_events: List[InputEvent] = []
        self.replay_speed = 1.0
        self.autosave_interval = self.config.get("autosave_interval", 30)
        self.countdown = self.config.get("countdown", 0)
        self.sound_enabled = self.config.get("sound_enabled", True)
        self.font_size = self.config.get("font_size", 9)
        self.window_opacity = self.config.get("window_opacity", 1.0)
        self.encrypt_export = self.config.get("encrypt_export", False)
        self.readonly = False
        self.auto_indent = True
        self._autosave_id = None
        self._float_icon: Optional[FloatingIcon] = None
        self._mini_preview = None
        self._blink_id = None

        self.engine = InputEngine(on_event=self._on_engine)
        self.engine.allowed_langs = self.allowed_langs
        self.engine.filter_enabled = self.filter_enabled
        self.engine.mode = self.mode
        self.engine.record_mouse = self.record_mouse
        self.engine.record_scroll = self.record_scroll

        self.files = FileManager()
        self.hotkeys = None

        self._build_ui()
        self._setup_drag()
        self._setup_local_binds()
        self._setup_hotkeys()
        self._setup_tray()
        self.files.new()
        self._update_file_label()
        self.registry.set_lang(self.registry.lang)
        self._apply_runtime_settings()
        self.root.protocol("WM_DELETE_WINDOW", self._quit)

    def _reg(self, widget, key, attr="text"):
        self.registry.register(widget, key, attr)
        return widget

    def _tip(self, widget, key):
        Tooltip(widget, key, self.registry)
        return widget

    def _build_ui(self):
        self.root.title(f"  ✦  {APP_NAME}")
        # Title bar
        bar = tk.Frame(self.root, bg=C["surface"], height=32)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        self.title_lbl = tk.Label(
            bar, text=f"  ✦  {APP_NAME}",
            bg=C["surface"], fg=C["accent"], font=F["title"]
        )
        self.title_lbl.pack(side="left", padx=8)
        self._tip(self.title_lbl, "tip_drag")
        for sym, cmd, key in [
            ("◢", self._to_float, "tip_min"),
            ("─", self._to_float, "tip_min"),
            ("▢", self._toggle_max, "tip_max"),
            ("✕", self._quit, "tip_close")
        ]:
            b = tk.Button(
                bar, text=sym, command=cmd, bg=C["surface"],
                fg=C["danger"] if sym == "✕" else C["text_dim"],
                bd=0, font=("Segoe UI Emoji", 9, "bold"), width=3,
                cursor="hand2", activebackground=C["surface_hi"],
                activeforeground=C["accent"]
            )
            b.pack(side="right")
            self._tip(b, key)

        # Status bar
        s = tk.Frame(self.root, bg=C["bg"])
        s.pack(fill="x", padx=10, pady=(6, 2))
        self.status_dot = tk.Canvas(s, width=11, height=11, bg=C["bg"], highlightthickness=0)
        self.status_dot.pack(side="left", padx=(0, 5))
        self._dot = self.status_dot.create_oval(1, 1, 10, 10, fill=C["danger"], outline="")
        self.status_lbl = tk.Label(s, text="", bg=C["bg"], fg=C["text"], font=F["small"])
        self.status_lbl.pack(side="left", padx=2)
        self._reg(self.status_lbl, "status_ready")
        self.mode_lbl = tk.Label(s, text="", bg=C["bg"], fg=C["accent2"], font=F["tiny"])
        self.mode_lbl.pack(side="right", padx=3)
        self.mouse_lbl = tk.Label(s, text="", bg=C["bg"], fg=C["success"], font=F["tiny"])
        self.mouse_lbl.pack(side="right", padx=3)

        # Compact toolbars (3 rows only)
        def make_row():
            return tk.Frame(self.root, bg=C["bg"])

        # Row 1 — main actions
        tb1 = make_row()
        tb1.pack(fill="x", padx=6, pady=2)
        self.record_btn = self._mk(tb1, "", self._toggle_rec, C["success"], "btn_start")
        self.record_btn.pack(side="left", padx=1, fill="x", expand=True)
        self._tip(self.record_btn, "tip_record")
        for cmd, key, tip, col in [
            (self._save, "btn_save", "tip_save", C["accent"]),
            (self._switch_mode, "btn_mode", "tip_mode", C["warning"]),
            (self._clear, "btn_clear", "tip_clear", C["danger"]),
            (self._replay, "btn_replay", "tip_replay", C["success"]),
        ]:
            b = self._mk(tb1, "", cmd, col, key)
            b.pack(side="left", padx=1, fill="x", expand=True)
            self._tip(b, tip)

        # Row 2 — tools
        tb2 = make_row()
        tb2.pack(fill="x", padx=6, pady=2)
        for cmd, key, tip in [
            (self._files_dialog, "btn_files", "tip_files"),
            (self._export_menu, "btn_export", "tip_export"),
            (self._open_snippets, "btn_snippets", "tip_snippets"),
            (self._open_settings, "btn_settings", "tip_settings"),
            (self._open_stats, "btn_stats", "tip_stats"),
            (self._show_help, "btn_help", "tip_help"),
        ]:
            b = self._mk(tb2, "", cmd, C["accent"], key)
            b.pack(side="left", padx=1, fill="x", expand=True)
            self._tip(b, tip)

        # Row 3 — toggles + secondary
        tb3 = make_row()
        tb3.pack(fill="x", padx=6, pady=2)
        for cmd, key, tip, col in [
            (self._toggle_mouse, "btn_mouse", "tip_mouse", C["success"]),
            (self._toggle_scroll, "btn_scroll", "tip_scroll", C["success"]),
            (self._toggle_top, "btn_top", "tip_top", C["accent2"]),
            (self._toggle_preview, "btn_preview", "tip_preview", C["accent2"]),
            (self._copy_all, "btn_copyall", "tip_copyall", C["accent"]),
            (self._toggle_readonly, "btn_readonly", "tip_readonly", C["accent3"]),
            (self._font_up, "btn_font_up", "tip_font_up", C["warning"]),
            (self._font_down, "btn_font_dn", "tip_font_dn", C["warning"]),
        ]:
            b = self._mk(tb3, "", cmd, col, key, w=3 if "font" in key else None)
            b.pack(side="left", padx=1, fill="x", expand=True)
            self._tip(b, tip)

        # Text area
        fr = tk.Frame(self.root, bg=C["border"])
        fr.pack(fill="both", expand=True, padx=8, pady=4)
        inner = tk.Frame(fr, bg=C["bg_light"])
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        self.text = scrolledtext.ScrolledText(
            inner, wrap="word",
            bg=C["bg_light"], fg=C["text"],
            insertbackground=C["accent"],
            font=F["mono"], bd=0, padx=6, pady=4,
            selectbackground=C["surface_hi"],
            relief="flat", undo=True, maxundo=500
        )
        self.text.pack(fill="both", expand=True)
        self.text_menu = self._make_context_menu(self.text)
        self.text.bind("<Button-3>", self._show_text_menu)
        self.text.bind("<Control-MouseWheel>", self._on_ctrl_wheel)
        self.text.bind("<Control-Button-4>", lambda e: self._font_up())
        self.text.bind("<Control-Button-5>", lambda e: self._font_down())

        # Footer (file + counter)
        ft = tk.Frame(self.root, bg=C["bg"])
        ft.pack(fill="x", padx=8, pady=(0, 1))
        self.file_lbl = tk.Label(ft, text="", bg=C["bg"], fg=C["text_dim"], font=F["tiny"], anchor="w")
        self.file_lbl.pack(side="left", fill="x", expand=True)
        self.counter_lbl = tk.Label(ft, text="", bg=C["bg"], fg=C["text_dim"], font=F["tiny"])
        self.counter_lbl.pack(side="right")

        # Clean hotkeys bar (two-line style)
        help_frame = tk.Frame(self.root, bg=C["surface"], bd=0)
        help_frame.pack(fill="x", side="bottom")
        self.hotkeys_bar = tk.Label(
            help_frame, text="",
            bg=C["surface"], fg=C["accent"],
            font=("Consolas", 7),
            anchor="w", padx=8, pady=5,
            wraplength=340, justify="left"
        )
        self.hotkeys_bar.pack(fill="x")
        self._reg(self.hotkeys_bar, "hotkeys_bar")

        # Credits
        cr = tk.Frame(self.root, bg=C["bg"])
        cr.pack(fill="x", padx=8, pady=(1, 3))
        self.credits_lbl = tk.Label(
            cr, text="", bg=C["bg"], fg=C["text_dim"],
            font=("Segoe UI Emoji", 7, "underline"), cursor="hand2"
        )
        self.credits_lbl.pack(side="right")
        self._reg(self.credits_lbl, "credits")
        self.credits_lbl.bind("<Button-1>", lambda e: webbrowser.open(APP_REPO))
        self._tip(self.credits_lbl, "tip_link")

        self._refresh_mode_labels()
        self._update_counter()
        self._apply_text_direction()

    def _mk(self, parent, text, cmd, color, key, w=None):
        b = tk.Button(
            parent, text=text, command=cmd, bg=C["surface"],
            fg=color, bd=0, font=F["small"], padx=3, pady=4,
            cursor="hand2", activebackground=color,
            activeforeground=C["bg"], width=w,
            highlightthickness=0, relief="flat"
        )
        b.bind("<Enter>", lambda e, bb=b: bb.config(bg=C["surface_hi"]))
        b.bind("<Leave>", lambda e, bb=b: bb.config(bg=C["surface"]))
        if key:
            self.registry.register(b, key)
        return b

    def _make_context_menu(self, widget):
        m = tk.Menu(
            widget, tearoff=0, bg=C["surface"], fg=C["text"],
            activebackground=C["accent"], activeforeground=C["bg"],
            bd=0, font=F["small"]
        )
        L = self.registry.lang
        m.add_command(label="📋 " + T("menu_copy", L), command=self._text_copy)
        m.add_command(label="✂ " + T("menu_cut", L), command=self._text_cut)
        m.add_command(label="📥 " + T("menu_paste", L), command=self._text_paste)
        m.add_separator()
        m.add_command(label="⬜ " + T("menu_select_all", L), command=self._text_select_all)
        m.add_command(label="↶ " + T("menu_undo", L), command=self._safe_undo)
        m.add_command(label="↷ " + T("menu_redo", L), command=self._safe_redo)
        m.add_command(label="⎘ " + T("menu_dup_line", L), command=self._dup_line)
        m.add_separator()
        m.add_command(label="📄 " + T("menu_copy_all", L), command=self._copy_all)
        m.add_command(label="🔍 " + T("menu_find", L), command=lambda: FindReplaceDialog(self.root, self.text, L))
        m.add_command(label="🗑 " + T("menu_clear_all", L), command=self._clear)
        return m

    def _show_text_menu(self, e):
        self.text_menu = self._make_context_menu(self.text)
        try:
            self.text_menu.tk_popup(e.x_root, e.y_root)
        finally:
            try:
                self.text_menu.grab_release()
            except Exception:
                pass

    def _text_copy(self):
        try:
            self.root.clipboard_clear()
            sel = self.text.get("sel.first", "sel.last")
            self.root.clipboard_append(sel)
            self.status_lbl.config(text="✓ " + T("copied", self.registry.lang), fg=C["success"])
            self.root.after(900, self._reset_status)
        except tk.TclError:
            pass

    def _text_cut(self):
        try:
            self.root.clipboard_clear()
            sel = self.text.get("sel.first", "sel.last")
            self.root.clipboard_append(sel)
            self.text.delete("sel.first", "sel.last")
        except tk.TclError:
            pass

    def _text_paste(self):
        try:
            data = self.root.clipboard_get()
            self.text.insert("insert", data)
            self.text_buffer += data
            self._update_counter()
        except tk.TclError:
            pass

    def _text_select_all(self):
        self.text.tag_add("sel", "1.0", "end-1c")
        self.text.mark_set("insert", "end-1c")

    def _copy_all(self):
        try:
            content = self.text.get("1.0", "end-1c")
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.status_lbl.config(text="📋 " + T("copied", self.registry.lang), fg=C["success"])
            self.root.after(1200, self._reset_status)
        except Exception:
            pass

    def _dup_line(self):
        try:
            if self.readonly:
                return
            idx = self.text.index("insert")
            line = idx.split(".")[0]
            content = self.text.get(f"{line}.0", f"{line}.end")
            self.text.insert(f"{line}.end", "\n" + content)
            self._sync_buffer_from_widget()
        except Exception:
            pass

    def _sync_buffer_from_widget(self):
        try:
            self.text_buffer = self.text.get("1.0", "end-1c")
            self._update_counter()
        except Exception:
            pass

    def _on_ctrl_wheel(self, e):
        if e.delta > 0:
            self._font_up()
        else:
            self._font_down()
        return "break"

    def _toggle_readonly(self):
        self.readonly = not self.readonly
        state = "disabled" if self.readonly else "normal"
        try:
            self.text.config(state=state)
        except Exception:
            pass
        L = self.registry.lang
        self.status_lbl.config(
            text=T("readonly_on" if self.readonly else "readonly_off", L),
            fg=C["warning"] if self.readonly else C["success"]
        )
        self.root.after(1500, self._reset_status)

    def _open_snippets(self):
        SnippetsDialog(self.root, self, self._insert_text)

    def _insert_slot(self, slot: int):
        """Quick insert from Ctrl+1/2/3 assigned snippet"""
        snip = self.config.get_slot(slot)
        if not snip:
            self.status_lbl.config(text=f"Ctrl+Shift+{slot} خالی است", fg=C["warning"])
            self.root.after(1200, self._reset_status)
            return
        text = snip.get("text", "")
        now = datetime.datetime.now()
        text = text.replace("HH:MM:SS", now.strftime("%H:%M:%S"))
        text = text.replace("YYYY-MM-DD", now.strftime("%Y-%m-%d"))
        text = text.replace("[تاریخ]", now.strftime("%Y-%m-%d"))
        text = text.replace("[ساعت]", now.strftime("%H:%M:%S"))
        text = text.replace("[Date]", now.strftime("%Y-%m-%d"))
        text = text.replace("[Time]", now.strftime("%H:%M:%S"))
        self._insert_text(text)
        self.status_lbl.config(text=f"✂ {snip.get('label', '')}", fg=C["success"])
        self.root.after(1000, self._reset_status)

    def _reset_status(self):
        if not self.is_recording:
            self.status_lbl.config(text=T("status_ready", self.registry.lang), fg=C["text"])

    def _refresh_mode_labels(self):
        L = self.registry.lang
        self.mode_lbl.config(text="• " + T("mode_typing" if self.mode == "typing" else "mode_macro", L))
        self.mouse_lbl.config(
            text=T("mouse_on" if self.record_mouse else "mouse_off", L),
            fg=C["success"] if self.record_mouse else C["text_dim"]
        )

    def _setup_drag(self):
        def start(e):
            self._dx, self._dy = e.x, e.y

        def move(e):
            x = self.root.winfo_x() + (e.x - self._dx)
            y = self.root.winfo_y() + (e.y - self._dy)
            self.root.geometry(f"+{x}+{y}")

        self.title_lbl.bind("<Button-1>", start)
        self.title_lbl.bind("<B1-Motion>", move)

    def _setup_local_binds(self):
        self.text.bind("<Control-z>", lambda e: (self._safe_undo(), "break")[1])
        self.text.bind("<Control-y>", lambda e: (self._safe_redo(), "break")[1])
        self.text.bind("<Control-f>", lambda e: (FindReplaceDialog(self.root, self.text, self.registry.lang), "break")[1])
        self.text.bind("<Control-a>", lambda e: (self._text_select_all(), "break")[1])
        self.text.bind("<Control-d>", lambda e: (self._dup_line(), "break")[1])
        self.text.bind("<Control-c>", lambda e: (self._text_copy(), "break")[1])
        self.text.bind("<Control-x>", lambda e: (self._text_cut(), "break")[1])
        self.text.bind("<Control-v>", lambda e: (self._text_paste(), "break")[1])
        self.text.bind("<Control-C>", lambda e: (self._text_copy(), "break")[1])
        self.text.bind("<Control-X>", lambda e: (self._text_cut(), "break")[1])
        self.text.bind("<Control-V>", lambda e: (self._text_paste(), "break")[1])
        self.text.bind("<Return>", self._on_enter)
        self.text.bind("<KeyRelease>", lambda e: (self._sync_buffer_from_widget(), self._apply_text_direction()))

    def _on_enter(self, e):
        if not self.auto_indent:
            return None
        try:
            idx = self.text.index("insert")
            line = int(idx.split(".")[0])
            content = self.text.get(f"{line}.0", f"{line}.end")
            m = re.match(r"^([ \t]*)", content)
            indent = m.group(1) if m else ""
            if indent:
                self.text.insert("insert", "\n" + indent)
                self._sync_buffer_from_widget()
                return "break"
        except Exception:
            pass
        return None

    def _safe_undo(self):
        try:
            self.text.edit_undo()
        except Exception:
            pass

    def _safe_redo(self):
        try:
            self.text.edit_redo()
        except Exception:
            pass

    def _on_engine(self, ev):
        try:
            if self.root.winfo_exists():
                self.root.after(0, lambda: self._safe_render(ev))
        except Exception:
            pass

    def _safe_render(self, ev):
        try:
            self._render(ev)
        except Exception:
            pass

    def _window_has_focus(self) -> bool:
        """True when our main window (or a child dialog) has keyboard focus."""
        try:
            focused = self.root.focus_displayof()
            if focused is None:
                return False
            # Any widget belonging to this app
            w = focused
            while w is not None:
                if w == self.root:
                    return True
                try:
                    w = w.master
                except Exception:
                    break
            return False
        except Exception:
            return False

    def _render(self, ev):
        if self.readonly:
            return
        try:
            if ev.kind == "key":
                if self.mode == "typing":
                    # When our window has focus, let Tkinter handle typing natively
                    # (perfect Persian / IME support). Only inject when capturing
                    # from other apps.
                    if self._window_has_focus():
                        return
                    if ev.action != "press":
                        return
                    if ev.key_char:
                        self.text_buffer += ev.key_char
                        self.text.insert("end", ev.key_char)
                    elif ev.key == "enter":
                        self.text_buffer += "\n"
                        self.text.insert("end", "\n")
                    elif ev.key == "space":
                        self.text_buffer += " "
                        self.text.insert("end", " ")
                    elif ev.key == "tab":
                        self.text_buffer += "\t"
                        self.text.insert("end", "\t")
                    elif ev.key == "backspace":
                        if self.text_buffer:
                            self.text_buffer = self.text_buffer[:-1]
                            self.text.delete("end-2c", "end-1c")
                    else:
                        return
                else:
                    if ev.action == "press":
                        mods = [m for m in ev.modifiers if m]
                        pre = "+".join(mods) + "+" if mods else ""
                        kd = ev.key_char if ev.key_char else ev.key.upper()
                        self.text.insert("end", f"[{pre}{kd}]")
            elif ev.kind == "mouse":
                if self.mode != "macro":
                    return
                if ev.action == "click":
                    self.text.insert("end", f" [🖱{ev.button}@({ev.x},{ev.y})] ")
                elif ev.action == "scroll":
                    arrow = "↑" if ev.dy > 0 else ("↓" if ev.dy < 0 else "↔")
                    self.text.insert("end", f" [{arrow}{ev.dy}@({ev.x},{ev.y})] ")
            self.text.see("end")
            self._update_counter()
        except Exception:
            pass

    def _update_counter(self):
        try:
            ev_n = len(self.engine.events)
            txt = self.text_buffer if self.text_buffer else ""
            chars = len(txt)
            words = len(txt.split()) if txt.strip() else 0
            lines = txt.count("\n") + 1 if txt else 1
            self.counter_lbl.config(
                text=f"📝 {chars}c · {words}w · {lines}L · {ev_n} {T('events', self.registry.lang)}"
            )
        except Exception:
            pass

    def _setup_hotkeys(self):
        """Robust global hotkey registration — one failure won't kill the rest."""
        H = self.HOTKEYS
        # Core map: action name -> callable
        actions = {
            "start_stop": self._toggle_rec,
            "save": self._save,
            "switch": self._switch_mode,
            "ontop": self._toggle_top,
            "replay": self._replay,
            "float": self._to_float,
            "clear": self._clear,
            "files": self._files_dialog,
            "export": self._export_menu,
            "lang": self._open_lang_dialog,
            "ui_lang": self._open_ui_lang_dialog,
            "mouse": self._toggle_mouse,
            "scroll": self._toggle_scroll,
            "help": self._show_help,
            "duplicate": self._duplicate_file,
            "new_file": self._new_file,
            "open_dir": self._open_dir,
            "speed_up": lambda: self._change_speed(0.25),
            "speed_down": lambda: self._change_speed(-0.25),
            "settings": self._open_settings,
            "stats": self._open_stats,
            "import": self._import_events,
            "sound": self._toggle_sound,
            "autosave": self._toggle_autosave,
            "font_up": self._font_up,
            "font_dn": self._font_down,
            "opacity": self._cycle_opacity,
            "preview": self._toggle_preview,
            "snippets": self._open_snippets,
            "readonly": self._toggle_readonly,
            "ins_line": lambda: self._insert_text("\n" + ("-" * 80) + "\n"),
            "ins_time": lambda: self._insert_text("[" + datetime.datetime.now().strftime("%H:%M:%S") + "] "),
            "ins_date": lambda: self._insert_text("[" + datetime.datetime.now().strftime("%Y-%m-%d") + "] "),
            "ins_bullet": lambda: self._insert_text("\n• "),
            "slot1": lambda: self._insert_slot(1),
            "slot2": lambda: self._insert_slot(2),
            "slot3": lambda: self._insert_slot(3),
            "ui_fa": lambda: self._set_lang("fa"),
            "ui_en": lambda: self._set_lang("en"),
            "ui_ar": lambda: self._set_lang("ar"),
            "ui_de": lambda: self._set_lang("de"),
            "ui_fr": lambda: self._set_lang("fr"),
        }

        def make_cb(fn):
            def _cb():
                try:
                    self.root.after(0, fn)
                except Exception:
                    pass
            return _cb

        # Build mapping carefully — skip any single key that fails
        mapping = {}
        for name, combo in H.items():
            if name not in actions:
                continue
            mapping[combo] = make_cb(actions[name])

        self.hotkeys = None
        self._hotkey_ok = 0
        try:
            self.hotkeys = keyboard.GlobalHotKeys(mapping)
            self.hotkeys.start()
            self._hotkey_ok = len(mapping)
            print(f"[hotkeys] OK — {self._hotkey_ok} shortcuts registered")
        except Exception as e:
            print(f"[hotkeys] GlobalHotKeys failed: {e}")
            core = {
                "<ctrl>+<shift>+q": make_cb(self._toggle_rec),
                "<ctrl>+<shift>+w": make_cb(self._save),
                "<ctrl>+<shift>+s": make_cb(self._open_snippets),
                "<ctrl>+<shift>+x": make_cb(self._to_float),
                "<ctrl>+<shift>+h": make_cb(self._show_help),
                "<ctrl>+<shift>+1": make_cb(lambda: self._insert_slot(1)),
                "<ctrl>+<shift>+2": make_cb(lambda: self._insert_slot(2)),
                "<ctrl>+<shift>+3": make_cb(lambda: self._insert_slot(3)),
            }
            try:
                self.hotkeys = keyboard.GlobalHotKeys(core)
                self.hotkeys.start()
                self._hotkey_ok = len(core)
                print(f"[hotkeys] Fallback OK — {self._hotkey_ok} core shortcuts")
            except Exception as e2:
                print(f"[hotkeys] Fallback also failed: {e2}")
                self._hotkey_ok = 0

        # Local Tk bindings as backup when window has focus
        self._setup_local_hotkeys()

    def _setup_local_hotkeys(self):
        """Backup shortcuts when the window is focused (always reliable via Tk)."""
        def bind_safe(seq, fn):
            def handler(e):
                try:
                    fn()
                except Exception:
                    pass
                return "break"
            try:
                self.root.bind_all(seq, handler)
            except Exception:
                pass

        pairs = [
            ("<Control-Shift-q>", self._toggle_rec),
            ("<Control-Shift-Q>", self._toggle_rec),
            ("<Control-Shift-w>", self._save),
            ("<Control-Shift-W>", self._save),
            ("<Control-Shift-s>", self._open_snippets),
            ("<Control-Shift-S>", self._open_snippets),
            ("<Control-Shift-x>", self._to_float),
            ("<Control-Shift-X>", self._to_float),
            ("<Control-Shift-h>", self._show_help),
            ("<Control-Shift-H>", self._show_help),
            ("<Control-Shift-e>", self._switch_mode),
            ("<Control-Shift-E>", self._switch_mode),
            ("<Control-Shift-c>", self._clear),
            ("<Control-Shift-C>", self._clear),
            ("<Control-Shift-a>", self._toggle_top),
            ("<Control-Shift-A>", self._toggle_top),
            ("<Control-Shift-Key-1>", lambda: self._insert_slot(1)),
            ("<Control-Shift-Key-2>", lambda: self._insert_slot(2)),
            ("<Control-Shift-Key-3>", lambda: self._insert_slot(3)),
            ("<Control-Shift-Key-0>", lambda: self._insert_text("\n" + ("-" * 80) + "\n")),
        ]
        for seq, fn in pairs:
            bind_safe(seq, fn)

    def _insert_text(self, s):
        """Insert snippet/line at cursor — always works even after typing."""
        try:
            if self.readonly:
                try:
                    self.text.config(state="normal")
                except Exception:
                    pass
            # Ensure widget can receive text
            try:
                self.text.focus_set()
            except Exception:
                pass
            self.text.insert("insert", s)
            self.text_buffer = self.text.get("1.0", "end-1c")
            self.text.see("insert")
            self._update_counter()
            if self.readonly:
                try:
                    self.text.config(state="disabled")
                except Exception:
                    pass
        except Exception as e:
            print(f"[insert] {e}")

    def _get_live_text(self) -> str:
        try:
            return self.text.get("1.0", "end-1c")
        except Exception:
            return self.text_buffer or ""

    def _apply_text_direction(self):
        """RTL for Persian/Arabic, LTR otherwise."""
        try:
            rtl = self.registry.lang in ("fa", "ar")
            # Tk Text: tag whole content
            self.text.tag_configure("rtl", justify="right")
            self.text.tag_configure("ltr", justify="left")
            self.text.tag_remove("rtl", "1.0", "end")
            self.text.tag_remove("ltr", "1.0", "end")
            if rtl:
                self.text.tag_add("rtl", "1.0", "end")
                try:
                    self.text.configure(align="right")
                except Exception:
                    pass
            else:
                self.text.tag_add("ltr", "1.0", "end")
                try:
                    self.text.configure(align="left")
                except Exception:
                    pass
        except Exception:
            pass

    def _set_lang(self, code):
        if code not in I18N:
            return
        self.registry.set_lang(code)
        self.config.set("ui_lang", code)
        self.config.save()
        self.root.title(f"  ✦  {APP_NAME}")
        self._refresh_mode_labels()
        self._update_counter()
        self._apply_text_direction()
        self._rebuild_tray()

    def _beep(self, kind="info"):
        if not self.sound_enabled or not HAS_SOUND:
            return
        try:
            if kind == "start":
                winsound.Beep(880, 100)
            elif kind == "stop":
                winsound.Beep(440, 100)
            elif kind == "go":
                winsound.Beep(1200, 80)
            else:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass

    def _toggle_rec(self):
        if self.is_recording:
            self._stop_rec()
        else:
            self._start_rec()

    def _start_rec(self):
        if self.countdown > 0:
            self._countdown_then_start(self.countdown)
        else:
            self._do_start_rec()

    def _countdown_then_start(self, n):
        L = self.registry.lang
        if n <= 0:
            self.status_lbl.config(text=T("countdown_go", L), fg=C["success"])
            self._beep("go")
            self.root.after(300, self._do_start_rec)
            return
        self.status_lbl.config(text=T("status_countdown", L).format(n), fg=C["warning"])
        self._beep("info")
        self.root.after(1000, lambda: self._countdown_then_start(n - 1))

    def _do_start_rec(self):
        self.text_buffer = ""
        self.text.delete("1.0", "end")
        self.engine.allowed_langs = self.allowed_langs
        self.engine.filter_enabled = self.filter_enabled
        self.engine.mode = self.mode
        self.engine.record_mouse = self.record_mouse
        self.engine.record_scroll = self.record_scroll
        self.engine.start()
        self.is_recording = True
        self.status_dot.itemconfig(self._dot, fill=C["success"])
        L = self.registry.lang
        self.status_lbl.config(text=T("status_rec", L), fg=C["success"])
        self.record_btn.config(text=T("btn_stop", L), fg=C["danger"])
        self._blink_status_dot(True)
        if self._float_icon:
            self._float_icon.set_recording(True)
        self._beep("start")
        self._start_autosave_timer()

    def _blink_status_dot(self, active):
        if self._blink_id:
            try:
                self.root.after_cancel(self._blink_id)
            except Exception:
                pass
            self._blink_id = None
        if not active:
            try:
                self.status_dot.itemconfig(self._dot, fill=C["danger"])
            except Exception:
                pass
            return

        def tick(on=True):
            try:
                self.status_dot.itemconfig(self._dot, fill=C["success"] if on else C["bg_light"])
            except Exception:
                return
            if self.is_recording:
                self._blink_id = self.root.after(500, lambda: tick(not on))

        tick(True)

    def _stop_rec(self):
        self.is_recording = False
        self.recorded_events = self.engine.stop()
        self._cancel_autosave_timer()
        L = self.registry.lang
        self.status_dot.itemconfig(self._dot, fill=C["danger"])
        self.status_lbl.config(text=T("status_ready", L), fg=C["text"])
        self.record_btn.config(text=T("btn_start", L), fg=C["success"])
        self._blink_status_dot(False)
        if self._float_icon:
            self._float_icon.set_recording(False)
        self._beep("stop")
        if self.recorded_events:
            self._auto_save()

    def _start_autosave_timer(self):
        self._cancel_autosave_timer()
        if self.autosave_interval > 0:
            self._autosave_id = self.root.after(self.autosave_interval * 1000, self._autosave_tick)

    def _autosave_tick(self):
        if self.is_recording and self.files.active:
            try:
                self.files.save(self.text_buffer, self.files.active)
                L = self.registry.lang
                self.status_lbl.config(text=T("status_saved", L), fg=C["success"])
                self.root.after(1000, lambda: self.status_lbl.config(
                    text=T("status_rec", L), fg=C["success"]) if self.is_recording else None)
            except Exception:
                pass
        self._start_autosave_timer()

    def _cancel_autosave_timer(self):
        if self._autosave_id:
            try:
                self.root.after_cancel(self._autosave_id)
            except Exception:
                pass
            self._autosave_id = None

    def _toggle_autosave(self):
        if self.autosave_interval > 0:
            self.autosave_interval = 0
        else:
            self.autosave_interval = 30
        self.config.set("autosave_interval", self.autosave_interval)
        self.config.save()
        self._apply_runtime_settings()
        self.status_lbl.config(text=f"💾 {self.autosave_interval}s", fg=C["warning"])
        self.root.after(1500, self._reset_status)

    def _apply_runtime_settings(self):
        try:
            self.text.config(font=("Consolas", self.font_size))
            self.root.attributes("-alpha", self.window_opacity)
        except Exception:
            pass
        self._start_autosave_timer()

    def _font_up(self):
        self.font_size = min(24, self.font_size + 1)
        self.config.set("font_size", self.font_size)
        self.config.save()
        self._apply_runtime_settings()
        self.status_lbl.config(text=f"A+ {self.font_size}", fg=C["warning"])
        self.root.after(1200, self._reset_status)

    def _font_down(self):
        self.font_size = max(6, self.font_size - 1)
        self.config.set("font_size", self.font_size)
        self.config.save()
        self._apply_runtime_settings()
        self.status_lbl.config(text=f"A− {self.font_size}", fg=C["warning"])
        self.root.after(1200, self._reset_status)

    def _cycle_opacity(self):
        levels = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
        try:
            i = levels.index(self.window_opacity)
        except ValueError:
            i = 0
        self.window_opacity = levels[(i + 1) % len(levels)]
        self.config.set("window_opacity", self.window_opacity)
        self.config.save()
        self._apply_runtime_settings()
        self.status_lbl.config(text=f"◐ {self.window_opacity:.1f}", fg=C["warning"])
        self.root.after(1200, self._reset_status)

    def _toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.config.set("sound_enabled", self.sound_enabled)
        self.config.save()
        self.status_lbl.config(
            text=("🔊 ON" if self.sound_enabled else "🔇 OFF"),
            fg=C["success"] if self.sound_enabled else C["text_dim"]
        )
        self.root.after(1200, self._reset_status)

    def _auto_save(self):
        self._sync_buffer_from_widget()
        path = self.files.active or self.files.new()
        self.files.save(self.text_buffer, path)
        if self.mode == "macro" and self.recorded_events:
            jp = path.rsplit(".", 1)[0] + "_events.json"
            try:
                Exporter.to_json(self.recorded_events, jp)
            except Exception:
                pass
        self._update_file_label()

    def _save(self):
        if self.is_recording:
            self._stop_rec()
        self._auto_save()
        L = self.registry.lang
        self.status_lbl.config(text=T("status_saved", L), fg=C["success"])
        self.root.after(1500, self._reset_status)

    def _clear(self):
        self.text.delete("1.0", "end")
        self.text_buffer = ""
        self.engine.events.clear()
        self.recorded_events.clear()
        self._update_counter()

    def _new_file(self):
        self.files.new()
        self.text.delete("1.0", "end")
        self.text_buffer = ""
        self._update_file_label()

    def _duplicate_file(self):
        if not self.files.active:
            return
        src = self.files.active
        base = os.path.basename(src)
        name, ext = os.path.splitext(base)
        ts = datetime.datetime.now().strftime("%H%M%S")
        nn = f"{name}_copy_{ts}{ext}"
        try:
            import shutil
            dst = os.path.join(self.files.dir, nn)
            shutil.copy(src, dst)
            self.files.active = dst
            self._update_file_label()
            self.status_lbl.config(text=f"✓ {nn}", fg=C["success"])
            self.root.after(1500, self._reset_status)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _open_dir(self):
        try:
            os.startfile(self.files.dir)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _switch_mode(self):
        self.mode = "macro" if self.mode == "typing" else "typing"
        self.config.set("mode", self.mode)
        self.config.save()
        self._refresh_mode_labels()
        self.text.delete("1.0", "end")
        self.text_buffer = ""

    def _toggle_top(self):
        self.always_on_top = not self.always_on_top
        self.config.set("always_on_top", self.always_on_top)
        self.config.save()
        self.root.attributes("-topmost", self.always_on_top)

    def _toggle_mouse(self):
        self.record_mouse = not self.record_mouse
        self.engine.record_mouse = self.record_mouse
        self.config.set("record_mouse", self.record_mouse)
        self.config.save()
        self._refresh_mode_labels()

    def _toggle_scroll(self):
        self.record_scroll = not self.record_scroll
        self.engine.record_scroll = self.record_scroll
        self.config.set("record_scroll", self.record_scroll)
        self.config.save()
        L = self.registry.lang
        self.status_lbl.config(
            text=T("scroll_on" if self.record_scroll else "scroll_off", L),
            fg=C["success"] if self.record_scroll else C["text_dim"]
        )
        self.root.after(1500, self._reset_status)

    def _change_speed(self, delta):
        self.replay_speed = max(0.25, min(5.0, self.replay_speed + delta))
        self.status_lbl.config(text=f"⚡ {self.replay_speed:.2f}x", fg=C["warning"])
        self.root.after(1200, self._reset_status)

    def _to_float(self):
        self.root.withdraw()
        if self._float_icon is None:
            self._float_icon = FloatingIcon(
                self.root, self._from_float, self.registry, self._toggle_preview
            )
            if self.is_recording:
                self._float_icon.set_recording(True)
        if self._mini_preview is None:
            self._mini_preview = MiniPreview(
                self.root, self.registry, self._get_live_text
            )
        else:
            self._mini_preview.show()

    def _toggle_preview(self):
        if self._mini_preview is None:
            self._mini_preview = MiniPreview(
                self.root, self.registry, self._get_live_text
            )
        else:
            self._mini_preview.toggle()

    def _from_float(self):
        if self._float_icon:
            self._float_icon.destroy()
            self._float_icon = None
        if self._mini_preview:
            self._mini_preview.destroy()
            self._mini_preview = None
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", self.always_on_top)
        self._fit()

    def _fit(self):
        try:
            self.root.update_idletasks()
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            x = max(0, min(self.root.winfo_x(), sw - w))
            y = max(0, min(self.root.winfo_y(), sh - h))
            self.root.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _setup_tray(self):
        try:
            self._tray_img = self._tray_image()
            self._rebuild_tray()
        except Exception as e:
            print(f"[tray] {e}")

    def _rebuild_tray(self):
        L = self.registry.lang
        try:
            if hasattr(self, "tray") and self.tray is not None:
                try:
                    self.tray.stop()
                except Exception:
                    pass
            menu = TrayMenu(
                TrayMenuItem(APP_NAME, self._from_float, default=True),
                TrayMenuItem(T("btn_start", L), lambda: self.root.after(0, self._toggle_rec)),
                TrayMenuItem(T("btn_save", L), lambda: self.root.after(0, self._save)),
                TrayMenu.SEPARATOR,
                TrayMenuItem(T("close", L), self._quit)
            )
            self.tray = TrayIcon(
                "NebulaNote", self._tray_img,
                f"{APP_NAME} — ma.ad.gh mahanneman", menu
            )
            threading.Thread(target=self.tray.run, daemon=True).start()
        except Exception as e:
            print(f"[tray-rebuild] {e}")

    @staticmethod
    def _tray_image(size=64):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        cx = cy = size // 2
        r = 26
        pts = [(cx, cy - r), (cx - r * 0.866, cy + r * 0.5), (cx + r * 0.866, cy + r * 0.5)]
        d.polygon(pts, fill=(15, 15, 40, 255), outline=(0, 217, 255, 255))
        r2 = r * 0.55
        pts2 = [
            (cx, cy - r2 + 2),
            (cx - r2 * 0.866, cy + r2 * 0.5 + 2),
            (cx + r2 * 0.866, cy + r2 * 0.5 + 2)
        ]
        d.polygon(pts2, fill=(34, 34, 76, 255), outline=(177, 74, 255, 255))
        return img

    def _open_lang_dialog(self):
        dlg = LanguageDialog(self.root, self.allowed_langs, self.detected_langs, self.registry.lang)
        r = dlg.show()
        if r is not None:
            self.allowed_langs = r
            self.engine.allowed_langs = r
            self.status_lbl.config(text=f"🌐 {len(r)}", fg=C["accent2"])
            self.root.after(1500, self._reset_status)

    def _open_ui_lang_dialog(self):
        dlg = UILangDialog(self.root, self.registry.lang, self.registry.lang)
        r = dlg.show()
        if r:
            self._set_lang(r)

    def _open_settings(self):
        SettingsDialog(self.root, self, self.registry.lang)

    def _open_stats(self):
        StatsDialog(self.root, self, self.registry.lang)

    def _import_events(self):
        L = self.registry.lang
        p = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("All", "*.*")],
            initialdir=self.files.dir
        )
        if not p:
            return
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            evs_raw = data.get("events", data if isinstance(data, list) else [])
            new_events = []
            for d in evs_raw:
                ev = InputEvent(
                    kind=d.get("kind", "key"), action=d.get("action", "press"),
                    timestamp=float(d.get("timestamp", 0)),
                    key=d.get("key", ""), key_char=d.get("key_char", ""),
                    vk=d.get("vk"), modifiers=d.get("modifiers", []) or [],
                    button=d.get("button", ""), x=int(d.get("x", 0)),
                    y=int(d.get("y", 0)), dx=int(d.get("dx", 0)),
                    dy=int(d.get("dy", 0)), lang=d.get("lang", "")
                )
                new_events.append(ev)
            self.recorded_events = new_events
            self._update_counter()
            messagebox.showinfo("✓", f"{T('import_ok', L)}: {len(new_events)}")
        except Exception as e:
            messagebox.showerror("!", f"{T('import_err', L)}\n{e}")

    def _show_help(self):
        L = self.registry.lang
        win = tk.Toplevel(self.root)
        win.title(T("help_title", L))
        win.geometry("600x680")
        win.configure(bg=C["bg"])
        win.attributes("-topmost", True)
        tk.Label(
            win, text="❓ " + T("help_title", L), bg=C["bg"],
            fg=C["accent"], font=("Segoe UI Emoji", 13, "bold")
        ).pack(pady=10)
        txt = scrolledtext.ScrolledText(
            win, wrap="word",
            bg=C["bg_light"], fg=C["text"],
            font=("Consolas", 9),
            bd=0, padx=12, pady=10
        )
        txt.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        txt.insert("1.0", T("help_body", L))
        txt.config(state="disabled")
        tk.Button(
            win, text=T("close", L), command=win.destroy,
            bg=C["surface"], fg=C["text"], bd=0, font=F["body"],
            padx=16, pady=6, cursor="hand2"
        ).pack(pady=(0, 10))

    def _files_dialog(self):
        L = self.registry.lang
        win = tk.Toplevel(self.root)
        win.title(T("files_title", L))
        win.geometry("520x560")
        win.configure(bg=C["bg"])
        win.attributes("-topmost", True)
        tk.Label(
            win, text=T("files_title", L), bg=C["bg"],
            fg=C["accent"], font=("Segoe UI Emoji", 11, "bold")
        ).pack(pady=8)
        if self.files.recent:
            tk.Label(
                win, text="🕒 " + T("recent_title", L) + ":",
                bg=C["bg"], fg=C["warning"], font=F["small"]
            ).pack(anchor="w", padx=10)
            rframe = tk.Frame(win, bg=C["bg"])
            rframe.pack(fill="x", padx=10, pady=2)
            for p in self.files.recent[:5]:
                nm = os.path.basename(p)
                b = tk.Button(
                    rframe, text="▸ " + nm, bg=C["bg_light"],
                    fg=C["text"], bd=0, font=F["tiny"], anchor="w",
                    cursor="hand2", padx=6, pady=2,
                    activebackground=C["accent"], activeforeground=C["bg"]
                )
                b.config(command=lambda pp=p: self._load_file(pp, win))
                b.pack(fill="x", pady=1)
        lb = tk.Listbox(
            win, bg=C["bg_light"], fg=C["text"], font=F["body"],
            selectbackground=C["accent"], selectforeground=C["bg"],
            bd=0, highlightthickness=0, activestyle="none"
        )
        lb.pack(fill="both", expand=True, padx=10, pady=4)
        files = self.files.list()
        for f in files:
            kb = f["size"] / 1024
            lb.insert("end", f"📄 {f['name']}   ({kb:.1f} KB)")

        def on_sel(e):
            sel = lb.curselection()
            if not sel:
                return
            i = sel[0]
            if i >= len(files):
                return
            self._load_file(files[i]["path"], win)

        lb.bind("<<ListboxSelect>>", on_sel)
        bf = tk.Frame(win, bg=C["bg"])
        bf.pack(pady=6)
        tk.Button(
            bf, text=T("close", L), command=win.destroy,
            bg=C["surface"], fg=C["text"], bd=0, font=F["small"],
            padx=12, pady=4, cursor="hand2"
        ).pack(side="left", padx=4)
        tk.Button(
            bf, text="📂", command=self._open_dir,
            bg=C["surface"], fg=C["accent"], bd=0, font=F["small"],
            padx=10, pady=4, cursor="hand2"
        ).pack(side="left", padx=4)

    def _load_file(self, path, win=None):
        try:
            content = self.files.preview(path)
            self.text.delete("1.0", "end")
            self.text.insert("1.0", content)
            self.text_buffer = content
            self.files.active = path
            self.files._push_recent(path)
            self._update_file_label()
            self._update_counter()
            if win:
                win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update_file_label(self):
        if self.files.active:
            self.file_lbl.config(text=f"📄 {os.path.basename(self.files.active)}")

    def _export_menu(self):
        L = self.registry.lang
        win = tk.Toplevel(self.root)
        win.title(T("export_title", L))
        win.geometry("380x520")
        win.configure(bg=C["bg"])
        win.attributes("-topmost", True)
        tk.Label(
            win, text="📤 " + T("export_title", L), bg=C["bg"],
            fg=C["accent"], font=("Segoe UI Emoji", 11, "bold")
        ).pack(pady=10)

        def do(fmt, ext):
            p = filedialog.asksaveasfilename(
                defaultextension=ext, filetypes=[(fmt.upper(), f"*{ext}")],
                initialdir=self.files.dir
            )
            if not p:
                return
            try:
                evs = self.recorded_events
                if not evs and fmt not in ("text", "md"):
                    messagebox.showinfo("!", T("no_events", L))
                    return
                if fmt == "json":
                    Exporter.to_json(evs, p)
                elif fmt == "jsonl":
                    Exporter.to_jsonl(evs, p)
                elif fmt == "excel":
                    Exporter.to_excel(evs, p)
                elif fmt == "text":
                    Exporter.to_text(evs, p)
                elif fmt == "md":
                    Exporter.to_markdown(evs, p)
                elif fmt == "auto":
                    Exporter.to_auto_script(evs, p, ui_lang=L)
                elif fmt == "enc":
                    pwd = simpledialog.askstring(
                        T("pwd_title", L), T("encrypt_pwd", L),
                        show="*", parent=win
                    )
                    if not pwd:
                        return
                    Exporter.to_json(evs, p, password=pwd)
                messagebox.showinfo("✓", f"{T('saved_at', L)}\n{p}")
                win.destroy()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        options = [
            ("export_json", "json", ".json", "tip_export_json"),
            ("export_jsonl", "jsonl", ".jsonl", "tip_export_jsonl"),
            ("export_excel", "excel", ".xlsx", "tip_export_excel"),
            ("export_text", "text", ".txt", "tip_export_text"),
            ("export_md", "md", ".md", "tip_export_md"),
            ("export_auto", "auto", ".py", "tip_export_auto"),
            ("export_encrypted", "enc", ".json", "tip_export_enc"),
        ]
        for key, fmt, ext, tip_key in options:
            b = tk.Button(
                win, text=T(key, L),
                command=lambda f=fmt, e=ext: do(f, e),
                bg=C["surface"], fg=C["text"], bd=0, font=F["body"],
                cursor="hand2", padx=8, pady=6, width=30,
                activebackground=C["accent"], activeforeground=C["bg"]
            )
            b.pack(pady=3)
            if tip_key:
                Tooltip(b, tip_key, self.registry)

    def _replay(self):
        """Replay with full settings: repeats, delay, speed, rest between cycles."""
        L = self.registry.lang
        if not self.recorded_events:
            messagebox.showinfo("!", T("no_events", L))
            return

        dlg = tk.Toplevel(self.root)
        dlg.title(T("btn_replay", L))
        dlg.geometry("360x340")
        dlg.configure(bg=C["bg"])
        dlg.attributes("-topmost", True)
        try:
            dlg.transient(self.root)
            dlg.grab_set()
        except Exception:
            pass

        tk.Label(dlg, text="▶ " + T("btn_replay", L), bg=C["bg"], fg=C["accent"],
                 font=("Segoe UI Emoji", 12, "bold")).pack(pady=10)

        def row(parent, label, default):
            f = tk.Frame(parent, bg=C["bg"])
            f.pack(fill="x", padx=16, pady=4)
            tk.Label(f, text=label, bg=C["bg"], fg=C["text"], font=F["small"],
                     width=22, anchor="w").pack(side="left")
            e = tk.Entry(f, bg=C["surface"], fg=C["text"], insertbackground=C["accent"],
                         font=F["body"], bd=0, width=10)
            e.insert(0, str(default))
            e.pack(side="right", ipady=3)
            return e

        e_rep = row(dlg, T("pl_rep", L) + " (تعداد تکرار)", 1)
        e_delay = row(dlg, T("pl_delay", L) + " (تأخیر شروع)", 2.0)
        e_speed = row(dlg, T("pl_speed", L), self.replay_speed)
        e_rest = row(dlg, "استراحت بین تکرار (ث)", 1.0)
        e_dur = row(dlg, T("pl_dur", L), 0)

        status = tk.Label(dlg, text=T("pl_ready", L), bg=C["bg"], fg=C["text"], font=F["small"])
        status.pack(pady=6)
        stop_flag = [False]
        running = [False]

        def play_once(kctrl, mctrl, speed, duration):
            events = sorted(self.recorded_events, key=lambda e: e.timestamp)
            prev = 0.0
            t0 = time.time()
            for ev in events:
                if stop_flag[0]:
                    return
                if duration > 0 and (time.time() - t0) > duration:
                    return
                d = (ev.timestamp - prev) / max(0.01, speed)
                if d > 0:
                    time.sleep(d)
                prev = ev.timestamp
                try:
                    if ev.kind == "key":
                        if ev.action == "press":
                            if ev.key_char:
                                kctrl.press(ev.key_char)
                            else:
                                for k, n in InputEngine.SPECIAL.items():
                                    if n == ev.key:
                                        kctrl.press(k)
                                        break
                        else:
                            if ev.key_char:
                                kctrl.release(ev.key_char)
                            else:
                                for k, n in InputEngine.SPECIAL.items():
                                    if n == ev.key:
                                        kctrl.release(k)
                                        break
                    elif ev.kind == "mouse":
                        if ev.action == "click":
                            mctrl.position = (ev.x, ev.y)
                            btn = {
                                "left": mouse.Button.left,
                                "right": mouse.Button.right,
                                "middle": mouse.Button.middle
                            }.get(ev.button, mouse.Button.left)
                            mctrl.click(btn)
                        elif ev.action == "scroll":
                            mctrl.position = (ev.x, ev.y)
                            mctrl.scroll(ev.dx, ev.dy)
                        elif ev.action == "move":
                            mctrl.position = (ev.x, ev.y)
                except Exception:
                    pass

        def start_play():
            if running[0]:
                return
            try:
                rep = max(1, int(e_rep.get()))
                delay = max(0.0, float(e_delay.get()))
                speed = max(0.05, float(e_speed.get()))
                rest = max(0.0, float(e_rest.get()))
                dur = max(0.0, float(e_dur.get()))
            except ValueError:
                status.config(text="مقدار نامعتبر", fg=C["danger"])
                return
            running[0] = True
            stop_flag[0] = False
            self.replay_speed = speed

            def worker():
                time.sleep(delay)
                kctrl = keyboard.Controller()
                mctrl = mouse.Controller()
                for i in range(rep):
                    if stop_flag[0]:
                        break
                    status.config(text=f"{i + 1}/{rep}", fg=C["warning"])
                    play_once(kctrl, mctrl, speed, dur)
                    if i < rep - 1 and rest > 0 and not stop_flag[0]:
                        time.sleep(rest)
                running[0] = False
                self.root.after(0, lambda: (
                    status.config(text=T("pl_ready", L), fg=C["text"]),
                    self._reset_status()
                ))

            self.status_lbl.config(text=T("status_playing", L), fg=C["warning"])
            threading.Thread(target=worker, daemon=True).start()

        def stop_play():
            stop_flag[0] = True
            running[0] = False
            status.config(text="⏹", fg=C["danger"])

        bf = tk.Frame(dlg, bg=C["bg"])
        bf.pack(pady=10)
        tk.Button(bf, text=T("pl_run", L), command=start_play, bg=C["success"], fg=C["bg"],
                  bd=0, font=F["small"], padx=16, pady=6, cursor="hand2").pack(side="left", padx=6)
        tk.Button(bf, text=T("pl_stop", L), command=stop_play, bg=C["danger"], fg=C["white"],
                  bd=0, font=F["small"], padx=16, pady=6, cursor="hand2").pack(side="left", padx=6)
        tk.Button(bf, text=T("close", L), command=dlg.destroy, bg=C["surface"], fg=C["text"],
                  bd=0, font=F["small"], padx=12, pady=6, cursor="hand2").pack(side="left", padx=6)

    def _toggle_max(self):
        try:
            if self.root.state() == "zoomed":
                self.root.state("normal")
            else:
                self.root.state("zoomed")
        except Exception:
            pass

    def _quit(self):
        try:
            self._stop_rec()
        except Exception:
            pass
        self._cancel_autosave_timer()
        if self._blink_id:
            try:
                self.root.after_cancel(self._blink_id)
            except Exception:
                pass
        try:
            if self.hotkeys:
                self.hotkeys.stop()
        except Exception:
            pass
        try:
            if self._float_icon:
                self._float_icon.destroy()
        except Exception:
            pass
        try:
            if self._mini_preview:
                self._mini_preview.destroy()
        except Exception:
            pass
        try:
            if hasattr(self, "tray") and self.tray is not None:
                try:
                    self.tray.stop()
                except Exception:
                    pass
        except Exception:
            pass
        self.config.save()
        try:
            self.root.destroy()
        except Exception:
            pass

    def run(self):
        self.root.mainloop()


def main():
    print("=" * 62)
    print(f"  * {APP_NAME} v{APP_VER}")
    print("  Author : ma.ad.gh mahanneman")
    print(f"  GitHub : {APP_REPO}")
    print("=" * 62)
    print()
    miss = _ck_check_deps()
    if miss:
        print("[!] Missing packages: " + ", ".join(miss))
        print("    Install:  py -m pip install " + " ".join(miss))
        try:
            if sys.stdin and sys.stdin.isatty():
                input("Press Enter to exit...")
        except Exception:
            pass
        return
    print("[OK] Dependencies OK. Opening window...")
    print()
    try:
        NebulaNote().run()
    except Exception:
        traceback.print_exc()
        print()
        print("Crash log: " + os.path.join(_ck_log_dir(), "crash.log"))
        try:
            if sys.stdin and sys.stdin.isatty():
                input("Press Enter to exit...")
        except Exception:
            pass


if __name__ == "__main__":
    main()
