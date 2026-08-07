"""
chatbot.py — Self-Contained AI Decision Engine
==================================================
This is the assistant's entire "brain" — there is no external AI
service, no API key, and no internet call anywhere in this module.
Every decision is made locally using logic written for this project.

Design (own decision-making pipeline):

    1. TOKENIZE          — normalize the user's text (English + Bengali)
    2. SCORE              — weigh the text against a hand-built keyword
                             lexicon, one weighted score per category
    3. DECIDE              — pick the winning category using the scores,
                              the current activity state, and short-term
                              conversation memory (so repeated moods are
                              recognised and escalated)
    4. RESPOND             — pull a fitting reply from the local
                              knowledge base (data/messages.json)

This mirrors a classic rule-based / weighted expert-system decision
pipeline: perceive → score → decide → act — entirely self-contained.
"""
import json
import os
import random
import re
import time

from settings import SETTINGS

DECISION_THRESHOLD = SETTINGS.get("decision_threshold", 1)

_msg_cache = None
_last_msg = ""
_last_time = 0.0


# ══════════════════════════════════════════════════════════════════════
# CONVERSATION MEMORY (own short-term context — no external storage)
# ══════════════════════════════════════════════════════════════════════
class _Memory:
    """Tracks the last few categories detected so the engine can notice
    a *pattern* (e.g. sadness repeated 3 times) and adapt its decision,
    instead of treating every message in isolation."""

    def __init__(self, size: int = 5):
        self.history = []
        self.size = size

    def push(self, category: str):
        self.history.append(category)
        if len(self.history) > self.size:
            self.history.pop(0)

    def streak(self, category: str) -> int:
        count = 0
        for c in reversed(self.history):
            if c == category:
                count += 1
            else:
                break
        return count


_memory = _Memory()


# ══════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE
# ══════════════════════════════════════════════════════════════════════
def _load_messages() -> dict:
    global _msg_cache
    if _msg_cache is None:
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "data", "messages.json")
        with open(path, "r", encoding="utf-8") as f:
            _msg_cache = json.load(f)
    return _msg_cache


# ══════════════════════════════════════════════════════════════════════
# WEIGHTED LEXICON — the engine's own "knowledge" of intent & emotion
# Each keyword carries a hand-tuned weight; stronger/clearer signals
# score higher than weak/ambiguous ones.
# ══════════════════════════════════════════════════════════════════════
LEXICON = {
    "greeting": {
        "hello": 3, "hi": 3, "hey": 2, "yo": 1,
        "হ্যালো": 3, "হাই": 3, "সালাম": 3, "আসসালামু": 3,
    },
    "sad": {
        "sad": 3, "unhappy": 3, "depressed": 4, "crying": 3, "upset": 2,
        "lonely": 3, "hurt": 2, "down": 1, "heartbroken": 4,
        "কষ্ট": 3, "দুঃখ": 3, "কাঁদছি": 3, "মন খারাপ": 4, "একা": 2,
    },
    "angry": {
        "angry": 3, "mad": 3, "frustrated": 3, "annoyed": 2, "furious": 4,
        "hate": 3, "irritated": 2,
        "রাগ": 3, "বিরক্ত": 3, "রেগে": 3,
    },
    "tired": {
        "tired": 3, "sleepy": 3, "exhausted": 4, "fatigue": 3, "drained": 3,
        "sleepy": 3, "burnt": 3,
        "ক্লান্ত": 3, "ঘুম": 2, "ঘুমাতে": 2,
    },
    "happy": {
        "happy": 3, "great": 2, "awesome": 3, "good": 1, "amazing": 3,
        "excited": 3, "glad": 2, "wonderful": 3,
        "ভালো": 2, "খুশি": 3, "আনন্দ": 3,
    },
    "motivation": {
        "motivate": 4, "inspire": 4, "encourage": 3, "confidence": 2,
        "মোটিভেশন": 4, "অনুপ্রেরণা": 4,
    },
    "wellness": {
        "health": 3, "water": 2, "break": 2, "rest": 2, "exercise": 2,
        "স্বাস্থ্য": 3, "বিরতি": 2, "পানি": 2,
    },
    "productive": {
        "work": 2, "task": 2, "focus": 3, "productive": 3, "deadline": 3,
        "কাজ": 2, "ফোকাস": 3, "সময়সীমা": 3,
    },
    "shutdown": {
        "shutdown": 4, "close": 2, "quit": 3, "exit": 3, "turn off": 4,
        "বন্ধ": 3,
    },
    "help": {
        "help": 3, "what can you do": 4, "how": 1, "guide": 2,
        "সাহায্য": 3, "কিভাবে": 1,
    },
}

# Priority used only to break near-ties between categories with an
# equal score (earlier = wins).
_PRIORITY = ["shutdown", "greeting", "help", "sad", "angry", "tired",
             "motivation", "happy", "wellness", "productive"]


def _tokenize(text: str) -> str:
    """Normalize text for matching. Keeps Unicode (Bengali) intact,
    lowercases ASCII, and collapses whitespace."""
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _score_categories(text: str) -> dict:
    """Own scoring function: sums the weight of every keyword found in
    the message, per category. Substring matching keeps this robust
    for Bengali, where clean word-splitting is unreliable."""
    scores = {cat: 0 for cat in LEXICON}
    for category, keywords in LEXICON.items():
        for kw, weight in keywords.items():
            if kw in text:
                scores[category] += weight
    return scores


def _decide_category(text: str) -> str | None:
    """The engine's own decision step: score, then pick a winner using
    the highest score, tie-broken by category priority, and gated by
    a minimum confidence threshold so weak/no matches fall through to
    the state-based fallback instead of guessing."""
    scores = _score_categories(text)
    best_category, best_score = None, 0
    for cat in _PRIORITY:
        s = scores.get(cat, 0)
        if s > best_score:
            best_category, best_score = cat, s
    if best_score < DECISION_THRESHOLD:
        return None
    return best_category


# ══════════════════════════════════════════════════════════════════════
# PROACTIVE AUTO MESSAGES (background worker, respects cooldown)
# ══════════════════════════════════════════════════════════════════════
def get_auto_message(state: str, cooldown: float) -> str | None:
    """Returns a context-aware auto message, or None if the cooldown
    hasn't elapsed yet. Selection is entirely local/rule-based."""
    global _last_msg, _last_time

    now = time.time()
    if now - _last_time < cooldown:
        return None

    data = _load_messages()
    pool = list(data.get(state, []))

    # Vary the message type over time using a simple internal cycle —
    # the engine's own decision for keeping suggestions fresh.
    cycles = int((now - _last_time) // cooldown) if cooldown else 0
    if cycles % 3 == 0:
        pool.extend(data.get("motivational", []))
    if cycles % 5 == 0:
        pool.extend(data.get("wellness", []))

    if not pool:
        pool = ["Stay focused, you're doing great. 🚀"]

    choices = [m for m in pool if m != _last_msg] or pool
    msg = random.choice(choices)

    _last_msg = msg
    _last_time = now
    return msg


# ══════════════════════════════════════════════════════════════════════
# CHAT REPLIES (user-initiated messages)
# ══════════════════════════════════════════════════════════════════════
def generate_reply(user_text: str, state: str) -> str:
    """
    The full decision pipeline for a user message:
    tokenize → score → decide → (adapt using memory) → respond.
    Entirely self-contained — no network calls of any kind.
    """
    text = _tokenize(user_text)
    data = _load_messages()

    category = _decide_category(text)

    if category is None:
        # No confident keyword match — fall back to the current
        # activity state as the deciding signal.
        _memory.push("none")
        if state == "idle":
            return "⏰ You've been inactive for a while. Would you like a break, or should I help you shut down?"
        if state == "tired":
            return random.choice(data.get("tired", ["Consider taking a short break. 😴"]))
        return random.choice(data.get("active", ["I'm here — tell me more. 😊"]))

    _memory.push(category)
    streak = _memory.streak(category)

    if category == "greeting":
        return f"👋 Hello! I'm your {_app_name()} assistant. How can I help you today?"

    if category == "help":
        return ("🤖 I'm your AI Assistant. I can:\n"
                "• Monitor your activity and mood\n"
                "• Send motivational and wellness tips\n"
                "• Let you know when you've been idle\n"
                "• Chat with you any time\n\n"
                "Just type a message and I'll respond.")

    if category == "shutdown":
        return "You can use the Shutdown button at the bottom of the chat whenever you're ready. 🔴"

    if category == "sad":
        reply = random.choice(data.get("sad", ["I'm here for you. 💙"]))
        if streak >= 3:
            # Own escalation rule: repeated sadness gets a stronger,
            # more attentive response instead of the usual pool.
            reply += " You've mentioned this a few times — please consider talking to someone you trust."
        return reply

    if category == "angry":
        return random.choice(data.get("angry", ["Take a deep breath. 🌬️"]))

    if category == "tired":
        return random.choice(data.get("tired", ["Consider resting for a moment. 😴"]))

    if category == "happy":
        return random.choice(data.get("happy", ["That's wonderful! 🌟"]))

    if category == "motivation":
        return random.choice(data.get("motivational", ["You've got this. 💪"]))

    if category == "wellness":
        return random.choice(data.get("wellness", ["Take care of yourself. 💧"]))

    if category == "productive":
        return random.choice(data.get("productive", ["Stay focused. 🎯"]))

    # Should not normally be reached — safety net.
    return random.choice(data.get("active", ["I'm here — tell me more. 😊"]))


def _app_name() -> str:
    return SETTINGS.get("app_name", "AI")
