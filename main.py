"""
main.py — AI Assistant Entry Point
PERSONAL ADVICE AI Desktop Assistant v2.0

Run by double-clicking (or: python main.py)
"""
import threading
import time
import sys
import os

# Ensure correct working directory (important when run via double-click)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from monitor import get_state
from chatbot import get_auto_message
from settings import SETTINGS
from ui import MessengerUI


def background_worker(ui: MessengerUI):
    """
    Runs in background thread.
    - Checks user activity state every INTERVAL seconds
    - Sends emotion-aware auto messages with cooldown
    - Updates UI state for idle/tired detection
    """
    while True:
        try:
            state = get_state(SETTINGS["idle_time"])

            # Update UI status label
            ui.root.after(0, lambda s=state: ui.set_state(s))

            # Get and display auto message (respects cooldown)
            msg = get_auto_message(state, SETTINGS["cooldown"])
            if msg:
                ui.root.after(0, lambda m=msg: ui.show_auto(m))

        except Exception as e:
            print(f"[Worker Error] {e}")

        time.sleep(SETTINGS["interval"])


def main():
    ui = MessengerUI()

    # Start background monitoring thread
    worker_thread = threading.Thread(
        target=background_worker,
        args=(ui,),
        daemon=True,
        name="ActivityMonitor"
    )
    worker_thread.start()

    print(f"🤖 {SETTINGS['app_name']} AI Assistant v{SETTINGS['version']} started.")
    print("   Close the chat window to exit.")

    ui.run()


if __name__ == "__main__":
    main()
