"""
chatbot.py — Auto-message engine with emotion-aware selection
"""
import json
import os
import random
import time

_last_msg = ""
_last_time = 0.0
_msg_cache = None


def _load_messages() -> dict:
    global _msg_cache
    if _msg_cache is None:
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "data", "messages.json")
        with open(path, "r", encoding="utf-8") as f:
            _msg_cache = json.load(f)
    return _msg_cache


def get_auto_message(state: str, cooldown: float) -> str | None:
    """
    Returns a context-aware auto message or None if cooldown hasn't elapsed.
    Rotates between state messages and motivational/wellness tips.
    """
    global _last_msg, _last_time

    now = time.time()
    if now - _last_time < cooldown:
        return None

    data = _load_messages()

    # Build pool based on state + sprinkle motivational/wellness
    pool = []
    pool.extend(data.get(state, []))

    # Every 3rd message mix in motivational or wellness tip
    count = int((now - _last_time) // cooldown)
    if count % 3 == 0:
        pool.extend(data.get("motivational", []))
    if count % 5 == 0:
        pool.extend(data.get("wellness", []))

    if not pool:
        pool = ["Stay focused and keep going! 🚀"]

    # Avoid repeating the same message
    choices = [m for m in pool if m != _last_msg]
    if not choices:
        choices = pool

    msg = random.choice(choices)
    _last_msg = msg
    _last_time = now
    return msg


def generate_reply(user_text: str, state: str) -> str:
    """
    Rule-based + emotion-aware AI reply for user chat messages.
    """
    t = user_text.lower().strip()
    data = _load_messages()

    # Greetings
    if any(k in t for k in ["hello", "hi", "hey", "হ্যালো", "হাই", "সালাম"]):
        return "👋 Hello! I'm your AI Assistant from PERSONAL ADVICE. How can I help you today?"

    # Sad / negative emotions
    if any(k in t for k in ["sad", "unhappy", "depressed", "crying", "upset", "কষ্ট", "দুঃখ", "কাঁদছি"]):
        return random.choice(data.get("sad", ["I'm here for you. 💙"]))

    # Happy
    if any(k in t for k in ["happy", "great", "awesome", "good", "amazing", "ভালো", "খুশি"]):
        return random.choice(data.get("happy", ["That's wonderful! 🌟"]))

    # Angry
    if any(k in t for k in ["angry", "mad", "frustrated", "annoyed", "রাগ", "বিরক্ত"]):
        return random.choice(data.get("angry", ["Take a deep breath. 🌬️"]))

    # Tired
    if any(k in t for k in ["tired", "sleepy", "exhausted", "fatigue", "ক্লান্ত", "ঘুম"]):
        return random.choice(data.get("tired", ["Rest a bit. 😴"]))

    # Motivation request
    if any(k in t for k in ["motivate", "inspire", "encourage", "মোটিভেশন", "অনুপ্রেরণা"]):
        return random.choice(data.get("motivational", ["You've got this! 💪"]))

    # Health / wellness
    if any(k in t for k in ["health", "water", "break", "rest", "স্বাস্থ্য", "বিরতি"]):
        return random.choice(data.get("wellness", ["Take care of yourself! 💧"]))

    # Productivity
    if any(k in t for k in ["work", "task", "focus", "productive", "কাজ", "ফোকাস"]):
        return random.choice(data.get("productive", ["Stay focused! 🎯"]))

    # Shutdown
    if any(k in t for k in ["shutdown", "close", "quit", "exit", "বন্ধ"]):
        return "🔴 You can use the **Shutdown** button at the bottom of the chat to shut down your PC."

    # Help
    if any(k in t for k in ["help", "what", "how", "সাহায্য", "কি", "কিভাবে"]):
        return ("🤖 I'm your AI Assistant! I can:\n"
                "• Monitor your activity & emotions\n"
                "• Send motivational messages\n"
                "• Alert you when you're idle\n"
                "• Help you stay productive & healthy\n"
                "• Chat with you anytime!\n\n"
                "Just type anything and I'll respond! 😊")

    # State-based fallback
    if state == "idle":
        return "⏰ You've been inactive for a while. Need a break or ready to shut down?"
    if state == "tired":
        return random.choice(data.get("tired", ["Consider taking a short break. 😴"]))

    # Generic fallback
    return random.choice(data.get("active", ["I'm here! Tell me more. 😊"]))
