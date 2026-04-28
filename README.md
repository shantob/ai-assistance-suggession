# 🤖 PERSONAL ADVICE AI Assistant v2.0

A fully-featured AI Desktop Assistant with emotion monitoring, smart notifications, and WhatsApp-style chat UI.

---

## ✅ Features

| Feature | Status |
|---|---|
| WhatsApp-style chat UI | ✅ |
| Floating icon with unread badge | ✅ |
| Auto emotion-aware messages | ✅ |
| Toast notification popups | ✅ |
| Idle detection + Shutdown alert | ✅ |
| Chat with AI | ✅ |
| Quick reply buttons | ✅ |
| Minimise / Hide / Close | ✅ |
| 100s of messages (all emotions) | ✅ |
| Runs on double-click | ✅ |

---

## 🚀 How to Run

### Option 1 — Double-click (Windows)
Double-click `START_ASSISTANT.bat`

### Option 2 — Command line
```bash
python main.py
```

---

## 📋 Requirements

- **Python 3.10+** (tkinter is built-in)
- Windows 10/11 recommended (for idle detection via WinAPI)
- Linux/Mac: install `pynput` for idle detection:
  ```bash
  pip install pynput
  ```

---

## 🎨 UI Guide

| Button | Action |
|---|---|
| 💬 (floating icon) | Open chat window |
| ─ | Minimise back to icon |
| 👁 | Hide window (runs in background) |
| ✕ | Close assistant completely |
| 🔴 (in footer) | Shutdown PC |
| Quick reply buttons | One-tap common messages |

---

## 💬 Message Categories

The AI sends contextual messages based on detected state:

- **active** — Encouragement & focus tips
- **tired** — Rest suggestions & wellness tips
- **idle** — Wake-up alerts + shutdown option
- **happy** — Positive reinforcement
- **sad** — Comfort & support
- **angry** — Calming techniques
- **motivational** — Inspirational quotes
- **wellness** — Health reminders
- **productive** — Productivity tips

---

## ⚙️ Configuration (`settings.py`)

```python
SETTINGS = {
    "idle_time": 300,    # seconds before idle alert (default: 5 min)
    "interval": 15,      # how often to check activity (seconds)
    "cooldown": 45,      # min gap between auto-messages (seconds)
    "notification_duration": 6000,  # toast popup duration (ms)
}
```

---

## 📁 Project Structure

```
ai-assistant/
├── main.py              # Entry point
├── ui.py                # Full chat UI + notifications
├── chatbot.py           # Message generation + AI replies
├── monitor.py           # Idle detection + state logic
├── settings.py          # Configuration
├── data/
│   └── messages.json    # 100+ messages for all emotions
├── requirements.txt
├── START_ASSISTANT.bat  # Windows double-click launcher
└── README.md
```

---

## 🔧 Building Executable (.exe)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "AI-Assistant" main.py
```

The `.exe` will be in the `dist/` folder.

---

*PERSONAL ADVICE AI Assistant v2.0 — Built with Python & tkinter*
