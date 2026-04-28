def generate_reply(user_text, state):
    t = user_text.lower()

    if any(k in t for k in ["sad", "down"]):
        return "I’m here with you. Taking a short break or a walk can help."
    if "tired" in t:
        return "You seem tired. A quick rest can recharge you."
    if "shutdown" in t:
        return "If you’re done for today, you can use the shutdown button below."
    if "help" in t:
        return "I can monitor activity, suggest breaks, and help you stay productive."

    # state-aware fallback
    if state == "idle":
        return "You’ve been inactive for a while. Need a break or shutdown?"
    if state == "tired":
        return "You might be getting tired. Consider a short break."
    return "Got it. Tell me more."