# PERSONAL ADVICE — AI Desktop Assistant

A WhatsApp-style desktop AI companion built for a university **Artificial
Intelligence** course project. It watches how active you are on your
computer, chats with you, and sends emotion-aware suggestions — using
a completely self-contained decision engine that you own end-to-end.
**No third-party AI, no API key, and no internet connection required
— every decision is made by logic written for this project.**

---

## ✨ Features

- **Floating chat bubble** that expands into a full WhatsApp-style chat window
- **Activity monitoring** — classifies you as `active`, `tired`, or `idle`
  based on real keyboard/mouse input (idle-time detection)
- **Own weighted decision engine** — no external AI service of any kind.
  User messages are scored against a hand-built, weighted keyword lexicon
  (English + Bengali); the highest-scoring category wins and drives the
  reply
- **Short-term conversation memory** — the engine tracks recent categories
  and adapts (e.g. escalates its response if sadness is detected several
  times in a row)
- **Proactive suggestions** — motivational, wellness, and productivity
  tips sent automatically on a cooldown timer
- **Idle alert** with a one-click safe shutdown option
- **Bilingual** — understands and can reply to English or Bengali input
- **Minimizes to a small floating icon** instead of closing, so it keeps
  running quietly in the background

---

## 📁 Project Structure

```
AI-Assistant/
├── main.py              # Entry point — starts the UI and background worker
├── ui.py                # Full chat UI, notifications, window management
├── chatbot.py           # Self-contained AI decision engine (own logic only)
├── monitor.py            # Cross-platform idle-time detection + state logic
├── settings.py            # Configuration
├── data/
│   └── messages.json      # Knowledge base — replies by emotion/state
├── requirements.txt
├── START_ASSISTANT.bat    # Windows double-click launcher
└── README.md
```

---

## 🚀 Getting Started

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
python main.py
```

On Windows you can also just double-click `START_ASSISTANT.bat`.

No API keys, accounts, or internet connection are needed at any point —
the assistant is 100% self-contained.

## 🏗️ Building a Standalone .exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "Personal-Advice" main.py
```

---

## 🧠 AI Concepts Demonstrated

This project was built to demonstrate several core Artificial
Intelligence concepts covered in coursework — all implemented as the
project's own logic, with no third-party AI model involved:

- **Finite-state reasoning** — activity classification into
  active / tired / idle states (`monitor.py`)
- **Weighted rule-based decision engine** — a hand-built keyword lexicon
  scores each incoming message per category; the highest-scoring,
  above-threshold category is selected (`chatbot.py`)
- **Short-term memory & adaptive escalation** — the engine tracks recent
  decisions and changes its response when a pattern (e.g. repeated
  sadness) is detected
- **Bilingual NLU** — keyword recognition in both English and Bengali

A full project report is available separately (see the accompanying
documentation file).
