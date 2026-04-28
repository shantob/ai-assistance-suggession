python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
/
pip install -r requirements.txt



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

For Build .EXE
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "AI-Assistant" main.py
```

