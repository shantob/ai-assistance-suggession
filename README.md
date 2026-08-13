# PERSONAL ADVICE — AI Desktop Assistant

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
