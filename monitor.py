"""
monitor.py — Cross-platform idle time detection & state management
"""
import sys
import time
import threading

# ── platform-specific idle detection ──────────────────────────────────────────
if sys.platform == "win32":
    import ctypes

    def _get_idle_seconds():
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(lii)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
        return (ctypes.windll.kernel32.GetTickCount() - lii.dwTime) / 1000.0

else:
    # Linux/Mac fallback using mouse position tracking
    _last_activity = time.time()
    _monitor_lock = threading.Lock()

    try:
        from pynput import mouse, keyboard

        def _on_activity(*args, **kwargs):
            global _last_activity
            with _monitor_lock:
                _last_activity = time.time()

        mouse.Listener(on_move=_on_activity, on_click=_on_activity).start()
        keyboard.Listener(on_press=_on_activity).start()
    except ImportError:
        pass  # pynput not available, use time-based fallback

    def _get_idle_seconds():
        with _monitor_lock:
            return time.time() - _last_activity


def get_idle_time():
    """Returns seconds since last user input."""
    try:
        return _get_idle_seconds()
    except Exception:
        return 0.0


def get_state(idle_limit: float) -> str:
    """
    Returns one of: 'active', 'tired', 'idle'
    based on how long the user has been idle.
    """
    idle = get_idle_time()
    if idle > idle_limit:
        return "idle"
    elif idle > idle_limit * 0.5:
        return "tired"
    else:
        return "active"


def do_shutdown():
    """Initiate OS shutdown."""
    import os
    if sys.platform == "win32":
        os.system("shutdown /s /t 5")
    elif sys.platform == "darwin":
        os.system("sudo shutdown -h now")
    else:
        os.system("shutdown -h now")
