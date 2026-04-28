"""
ui.py — Complete AI Assistant UI
WhatsApp-style chat + floating notification bubbles + tray icon behavior
"""
import tkinter as tk
from tkinter import messagebox, font as tkfont
import threading
import time
import os
import sys
from settings import SETTINGS


# ─── Colour palette ───────────────────────────────────────────────────────────
C = {
    "primary":      "#075E54",   # dark green header
    "secondary":    "#128C7E",   # medium green
    "accent":       "#25D366",   # WhatsApp green
    "bg":           "#ECE5DD",   # chat background
    "bubble_bot":   "#DCF8C6",   # bot bubble
    "bubble_user":  "#FFFFFF",   # user bubble
    "text_dark":    "#111B21",   # dark text
    "text_light":   "#FFFFFF",   # white text
    "text_muted":   "#667781",   # grey text
    "input_bg":     "#FFFFFF",   # input box
    "shadow":       "#00000033", # light shadow
    "notif_bg":     "#1F2C34",   # dark notification bg
    "notif_text":   "#FFFFFF",
    "red":          "#E74C3C",
    "orange":       "#F39C12",
    "idle_bg":      "#FF6B6B",
}


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


# ─── Notification Popup (small toast, bottom-right) ──────────────────────────
class NotificationToast:
    """Small floating notification bubble that auto-dismisses."""

    _stack = []  # active toasts
    _lock = threading.Lock()

    def __init__(self, root, message: str, duration: int = 5000,
                 on_click=None, tag: str = ""):
        self.root = root
        self.msg = message
        self.duration = duration
        self.on_click = on_click
        self.tag = tag
        self._win = None
        self._after_id = None
        root.after(0, self._create)

    def _create(self):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w, h = 320, 80

        # stack offset
        with NotificationToast._lock:
            stack_offset = len(NotificationToast._stack) * (h + 8)
            NotificationToast._stack.append(self)

        y = sh - 160 - stack_offset
        x = sw - w - 20

        self._win = tk.Toplevel(self.root)
        self._win.overrideredirect(True)
        self._win.attributes("-topmost", True)
        self._win.attributes("-alpha", 0.0)
        self._win.geometry(f"{w}x{h}+{x}+{y}")
        self._win.configure(bg=C["notif_bg"])

        # rounded look via frame
        outer = tk.Frame(self._win, bg=C["notif_bg"], padx=0, pady=0)
        outer.pack(fill="both", expand=True)

        # coloured left accent bar
        bar = tk.Frame(outer, bg=C["accent"], width=5)
        bar.pack(side="left", fill="y")

        inner = tk.Frame(outer, bg=C["notif_bg"], padx=10, pady=8)
        inner.pack(side="left", fill="both", expand=True)

        # Header row
        head = tk.Frame(inner, bg=C["notif_bg"])
        head.pack(fill="x")
        tk.Label(head, text="🤖 " + SETTINGS["app_name"],
                 bg=C["notif_bg"], fg=C["accent"],
                 font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Label(head, text="✕",
                 bg=C["notif_bg"], fg=C["text_muted"],
                 font=("Segoe UI", 9), cursor="hand2").pack(side="right")
        head.children[list(head.children)[-1]].bind("<Button-1>", lambda e: self.dismiss())

        # Message
        lines = message[:120] + ("…" if len(message) > 120 else "")
        tk.Label(inner, text=lines,
                 bg=C["notif_bg"], fg=C["notif_text"],
                 font=("Segoe UI", 9),
                 wraplength=260, justify="left").pack(anchor="w", pady=(2, 0))

        # Click whole window opens chat
        for widget in [outer, inner, bar]:
            widget.bind("<Button-1>", self._clicked)

        # Fade in
        self._fade_in()
        self._after_id = self._win.after(self.duration, self.dismiss)

    def _clicked(self, event=None):
        if self.on_click:
            self.on_click()
        self.dismiss()

    def _fade_in(self, alpha=0.0):
        if not self._win or not self._win.winfo_exists():
            return
        if alpha < 0.93:
            self._win.attributes("-alpha", alpha)
            self._win.after(20, lambda: self._fade_in(alpha + 0.07))
        else:
            self._win.attributes("-alpha", 0.93)

    def _fade_out(self, alpha=0.93):
        if not self._win or not self._win.winfo_exists():
            return
        if alpha > 0.0:
            self._win.attributes("-alpha", alpha)
            self._win.after(20, lambda: self._fade_out(alpha - 0.09))
        else:
            self._destroy()

    def dismiss(self):
        if self._after_id:
            try:
                self._win.after_cancel(self._after_id)
            except Exception:
                pass
        self._fade_out()

    def _destroy(self):
        with NotificationToast._lock:
            if self in NotificationToast._stack:
                NotificationToast._stack.remove(self)
        if self._win and self._win.winfo_exists():
            self._win.destroy()


# ─── Idle Shutdown Alert ──────────────────────────────────────────────────────
class IdleAlert:
    """Custom styled idle alert with shutdown option."""

    def __init__(self, root, on_shutdown, on_cancel):
        self.root = root
        self._win = None
        root.after(0, lambda: self._create(on_shutdown, on_cancel))

    def _create(self, on_shutdown, on_cancel):
        self._win = tk.Toplevel(self.root)
        self._win.title("Inactivity Detected")
        self._win.overrideredirect(True)
        self._win.attributes("-topmost", True)
        self._win.configure(bg=C["primary"])

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w, h = 340, 200
        self._win.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        # Header
        hdr = tk.Frame(self._win, bg=C["idle_bg"], height=45)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⏰  Inactivity Detected",
                 bg=C["idle_bg"], fg="white",
                 font=("Segoe UI", 11, "bold")).pack(pady=10)

        # Body
        body = tk.Frame(self._win, bg=C["primary"], pady=15, padx=20)
        body.pack(fill="both", expand=True)

        tk.Label(body,
                 text=("You have been inactive for a while.\n\n"
                       "Would you like to shut down your PC?"),
                 bg=C["primary"], fg="white",
                 font=("Segoe UI", 10),
                 justify="center", wraplength=280).pack(pady=5)

        # Buttons
        btn_row = tk.Frame(body, bg=C["primary"])
        btn_row.pack(pady=10)

        def _yes():
            self._win.destroy()
            on_shutdown()

        def _no():
            self._win.destroy()
            on_cancel()

        tk.Button(btn_row, text="  🔴  Shutdown  ",
                  bg=C["red"], fg="white",
                  font=("Segoe UI", 10, "bold"),
                  bd=0, padx=12, pady=6, cursor="hand2",
                  command=_yes).pack(side="left", padx=8)

        tk.Button(btn_row, text="  ✅  Stay  ",
                  bg=C["accent"], fg="white",
                  font=("Segoe UI", 10, "bold"),
                  bd=0, padx=12, pady=6, cursor="hand2",
                  command=_no).pack(side="left", padx=8)


# ─── Main Messenger UI ────────────────────────────────────────────────────────
class MessengerUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()           # hide at start; shown on double-click trigger
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        self.is_open = False
        self.is_hidden = False         # minimised to icon
        self.unread = 0
        self.messages = []             # [(role, text, timestamp)]
        self.state = "active"
        self._idle_alerted = False
        self._quick_replies_visible = True

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self._sw = sw
        self._sh = sh

        self._build_icon()
        self.root.deiconify()

        # Welcome message after 1 second
        self.root.after(1000, self._welcome)

    # ═══════════════════════════════════════════════════════════════════════════
    # ICON MODE
    # ═══════════════════════════════════════════════════════════════════════════
    def _build_icon(self):
        """Small floating chat icon (bottom-right corner)."""
        self._clear()
        self.is_open = False
        self.is_hidden = False

        iw = SETTINGS["icon_size"]
        self.root.geometry(f"{iw}x{iw}+{self._sw - iw - 20}+{self._sh - iw - 60}")

        self._icon_frame = tk.Frame(self.root, bg=C["accent"])
        self._icon_frame.pack(fill="both", expand=True)

        self._icon_btn = tk.Button(
            self._icon_frame, text="💬",
            bg=C["accent"], fg="white",
            font=("Segoe UI", 22), bd=0, cursor="hand2",
            activebackground=C["secondary"],
            command=self.open_chat
        )
        self._icon_btn.pack(fill="both", expand=True)

        self._badge_lbl = tk.Label(
            self.root, bg=C["red"], fg="white",
            font=("Segoe UI", 7, "bold"),
            width=2
        )
        self._badge_lbl.place(x=iw - 18, y=2)
        self._update_badge()

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAT WINDOW
    # ═══════════════════════════════════════════════════════════════════════════
    def open_chat(self):
        """Expand to full chat window."""
        if self.is_open:
            return
        self.is_open = True
        self.unread = 0

        cw = SETTINGS["chat_width"]
        ch = SETTINGS["chat_height"]
        self.root.geometry(f"{cw}x{ch}+{self._sw - cw - 10}+{self._sh - ch - 60}")

        self._clear()
        self._build_chat_ui()
        self._update_badge()

    def _build_chat_ui(self):
        """Build the full WhatsApp-style chat UI."""
        main = tk.Frame(self.root, bg=C["bg"])
        main.pack(fill="both", expand=True)

        # ── Header ──────────────────────────────────────────────────────────
        header = tk.Frame(main, bg=C["primary"], height=55)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Avatar circle
        av = tk.Label(header, text="🤖", bg=C["secondary"],
                      font=("Segoe UI", 16), width=2)
        av.pack(side="left", padx=(10, 6), pady=8)

        # Title block
        title_frame = tk.Frame(header, bg=C["primary"])
        title_frame.pack(side="left", fill="y", pady=6)
        tk.Label(title_frame, text=SETTINGS["app_name"],
                 bg=C["primary"], fg="white",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self._status_lbl = tk.Label(title_frame, text="● Active",
                                    bg=C["primary"], fg=C["accent"],
                                    font=("Segoe UI", 8))
        self._status_lbl.pack(anchor="w")

        # Header buttons (right side)
        btn_frame = tk.Frame(header, bg=C["primary"])
        btn_frame.pack(side="right", padx=6)

        # Minimise to icon
        self._hdr_btn(btn_frame, "─", self.minimize, tip="Minimise")
        # Hide (system tray style)
        self._hdr_btn(btn_frame, "👁", self.hide_window, tip="Hide")
        # Close app
        self._hdr_btn(btn_frame, "✕", self._confirm_close, tip="Close")

        # ── Scrollable Chat Area ─────────────────────────────────────────────
        chat_container = tk.Frame(main, bg=C["bg"])
        chat_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(chat_container, bg=C["bg"],
                                highlightthickness=0)
        self.msg_frame = tk.Frame(self.canvas, bg=C["bg"])
        scrollbar = tk.Scrollbar(chat_container, orient="vertical",
                                 command=self.canvas.yview,
                                 troughcolor=C["bg"], bg=C["secondary"])

        self.canvas.configure(yscroommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)
        self._canvas_window = self.canvas.create_window(
            (0, 0), window=self.msg_frame, anchor="nw"
        )

        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.msg_frame.bind("<Configure>", self._on_frame_configure)

        # Mouse wheel scroll
        self.canvas.bind_all("<MouseWheel>",
                             lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        # ── Quick Reply Buttons ──────────────────────────────────────────────
        self._quick_frame = tk.Frame(main, bg=C["bg"])
        self._quick_frame.pack(fill="x", padx=10, pady=(0, 4))
        self._build_quick_replies()

        # ── Footer / Input ───────────────────────────────────────────────────
        footer = tk.Frame(main, bg="#F0F0F0", pady=6, padx=8)
        footer.pack(fill="x", side="bottom")

        # Shutdown button (left of input)
        tk.Button(footer, text="🔴",
                  bg="#F0F0F0", fg=C["red"],
                  font=("Segoe UI", 12), bd=0, cursor="hand2",
                  command=self._confirm_shutdown,
                  activebackground="#F0F0F0").pack(side="left", padx=(0, 4))

        # Text entry
        self.entry = tk.Entry(footer, bg=C["input_bg"], fg=C["text_dark"],
                              font=("Segoe UI", 10), bd=1, relief="flat",
                              insertbackground=C["text_dark"])
        self.entry.pack(side="left", fill="x", expand=True,
                        ipady=6, padx=(0, 6))
        self.entry.bind("<Return>", lambda e: self.send())

        # Send button
        tk.Button(footer, text="➤",
                  bg=C["accent"], fg="white",
                  font=("Segoe UI", 12, "bold"),
                  bd=0, padx=10, pady=4, cursor="hand2",
                  command=self.send,
                  activebackground=C["secondary"]).pack(side="right")

        # ── Replay history ───────────────────────────────────────────────────
        for role, text, ts in self.messages:
            if role == "AI":
                self._add_bot_bubble(text, ts, replay=True)
            else:
                self._add_user_bubble(text, ts, replay=True)

        self.root.after(100, self._scroll_bottom)

    def _hdr_btn(self, parent, text, cmd, tip=""):
        b = tk.Button(parent, text=text,
                      bg=C["primary"], fg="white",
                      font=("Segoe UI", 10), bd=0,
                      cursor="hand2", padx=6, pady=4,
                      activebackground=C["secondary"],
                      command=cmd)
        b.pack(side="left")
        return b

    def _build_quick_replies(self):
        """Quick-tap reply buttons (WhatsApp style)."""
        quick = [
            ("👋 I have a question", "I have a question"),
            ("💡 Tell me more", "Tell me more about what you can do"),
            ("😔 Feeling sad", "I'm feeling sad today"),
            ("💪 Motivate me", "Can you motivate me?"),
        ]
        for label, msg in quick:
            btn = tk.Button(
                self._quick_frame, text=label,
                bg=C["input_bg"], fg=C["primary"],
                font=("Segoe UI", 8), bd=1, relief="solid",
                padx=8, pady=3, cursor="hand2",
                command=lambda m=msg: self._quick_send(m)
            )
            btn.pack(side="left", padx=3, pady=2)

    def _quick_send(self, text):
        """Handle quick reply button tap."""
        self.entry.delete(0, "end")
        self.entry.insert(0, text)
        self.send()

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAT BUBBLES
    # ═══════════════════════════════════════════════════════════════════════════
    def _add_bot_bubble(self, text: str, ts: str = "", replay: bool = False):
        """Add a bot message bubble (left-aligned, green tint)."""
        row = tk.Frame(self.msg_frame, bg=C["bg"])
        row.pack(fill="x", pady=(4, 0), padx=8, anchor="w")

        # Avatar
        tk.Label(row, text="🤖", bg=C["bg"],
                 font=("Segoe UI", 12)).pack(side="left", anchor="s", padx=(0, 4))

        bubble = tk.Frame(row, bg=C["bubble_bot"],
                          padx=10, pady=6)
        bubble.pack(side="left", anchor="w")

        tk.Label(bubble, text=text,
                 bg=C["bubble_bot"], fg=C["text_dark"],
                 font=("Segoe UI", 9),
                 wraplength=240, justify="left").pack(anchor="w")

        if ts:
            tk.Label(bubble, text=ts,
                     bg=C["bubble_bot"], fg=C["text_muted"],
                     font=("Segoe UI", 7)).pack(anchor="e")

        if not replay:
            self.root.after(50, self._scroll_bottom)

    def _add_user_bubble(self, text: str, ts: str = "", replay: bool = False):
        """Add a user message bubble (right-aligned, white)."""
        row = tk.Frame(self.msg_frame, bg=C["bg"])
        row.pack(fill="x", pady=(4, 0), padx=8, anchor="e")

        bubble = tk.Frame(row, bg=C["bubble_user"],
                          padx=10, pady=6)
        bubble.pack(side="right", anchor="e")

        tk.Label(bubble, text=text,
                 bg=C["bubble_user"], fg=C["text_dark"],
                 font=("Segoe UI", 9),
                 wraplength=240, justify="left").pack(anchor="w")

        if ts:
            tk.Label(bubble, text=f"{ts} ✓✓",
                     bg=C["bubble_user"], fg=C["text_muted"],
                     font=("Segoe UI", 7)).pack(anchor="e")

        if not replay:
            self.root.after(50, self._scroll_bottom)

    # ═══════════════════════════════════════════════════════════════════════════
    # SEND / RECEIVE
    # ═══════════════════════════════════════════════════════════════════════════
    def send(self):
        """Send user message and generate AI reply."""
        msg = self.entry.get().strip()
        if not msg:
            return
        self.entry.delete(0, "end")

        ts = time.strftime("%H:%M")
        self.messages.append(("You", msg, ts))

        if self.is_open:
            self._add_user_bubble(msg, ts)

        # Generate reply in background
        threading.Thread(target=self._generate_and_show,
                         args=(msg,), daemon=True).start()

    def _generate_and_show(self, user_msg: str):
        """Background thread: generate reply and dispatch to UI."""
        from chatbot import generate_reply
        # Typing indicator
        self.root.after(0, self._show_typing)
        time.sleep(0.8)  # simulate typing delay
        reply = generate_reply(user_msg, self.state)
        self.root.after(0, lambda: self._receive_reply(reply))

    def _show_typing(self):
        if not self.is_open:
            return
        self._typing_row = tk.Frame(self.msg_frame, bg=C["bg"])
        self._typing_row.pack(fill="x", pady=(4, 0), padx=8, anchor="w")
        tk.Label(self._typing_row, text="🤖  typing…",
                 bg=C["bg"], fg=C["text_muted"],
                 font=("Segoe UI", 8, "italic")).pack(side="left")
        self._scroll_bottom()

    def _receive_reply(self, reply: str):
        # Remove typing indicator
        if hasattr(self, "_typing_row") and self._typing_row.winfo_exists():
            self._typing_row.destroy()

        ts = time.strftime("%H:%M")
        self.messages.append(("AI", reply, ts))

        if self.is_open:
            self._add_bot_bubble(reply, ts)
        else:
            self.unread += 1
            self._update_badge()
            NotificationToast(self.root, reply,
                              duration=SETTINGS["notification_duration"],
                              on_click=self.open_chat)

    # ═══════════════════════════════════════════════════════════════════════════
    # AUTO MESSAGES (from background worker)
    # ═══════════════════════════════════════════════════════════════════════════
    def show_auto(self, msg: str):
        """Called by background worker to inject an auto message."""
        if not msg:
            return
        ts = time.strftime("%H:%M")
        self.messages.append(("AI", msg, ts))

        if self.is_open:
            self._add_bot_bubble(msg, ts)
        else:
            self.unread += 1
            self._update_badge()

        # Always show toast notification
        NotificationToast(
            self.root, msg,
            duration=SETTINGS["notification_duration"],
            on_click=self.open_chat
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # STATE UPDATE (emotion / idle)
    # ═══════════════════════════════════════════════════════════════════════════
    def set_state(self, state: str):
        self.state = state
        self._update_status_label()

        if state == "idle" and not self._idle_alerted:
            self._idle_alerted = True
            IdleAlert(
                self.root,
                on_shutdown=self._do_shutdown,
                on_cancel=self._cancel_idle
            )
        elif state != "idle":
            self._idle_alerted = False

    def _update_status_label(self):
        if not self.is_open:
            return
        try:
            colours = {
                "active": (C["accent"], "● Active"),
                "tired":  (C["orange"], "● Tired"),
                "idle":   (C["red"],    "● Inactive"),
            }
            col, txt = colours.get(self.state, (C["accent"], "● Active"))
            self._status_lbl.config(fg=col, text=txt)
        except Exception:
            pass

    def _cancel_idle(self):
        self._idle_alerted = False

    # ═══════════════════════════════════════════════════════════════════════════
    # WINDOW MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    def minimize(self):
        """Shrink back to floating icon."""
        self._build_icon()

    def hide_window(self):
        """Fully hide window (it still runs in background)."""
        self.root.withdraw()
        self.is_hidden = True

    def show_window(self):
        """Restore hidden window."""
        self.root.deiconify()
        self.is_hidden = False

    def _confirm_close(self):
        """Ask before closing the app."""
        win = tk.Toplevel(self.root)
        win.title("Confirm")
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg=C["primary"])

        sw, sh = self._sw, self._sh
        w, h = 280, 130
        win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

        tk.Label(win, text="Close AI Assistant?",
                 bg=C["primary"], fg="white",
                 font=("Segoe UI", 11, "bold"), pady=15).pack()

        btn_row = tk.Frame(win, bg=C["primary"])
        btn_row.pack(pady=5)
        tk.Button(btn_row, text="  Yes, Close  ",
                  bg=C["red"], fg="white",
                  font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=5,
                  command=self.root.destroy).pack(side="left", padx=8)
        tk.Button(btn_row, text="  Cancel  ",
                  bg=C["accent"], fg="white",
                  font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=5,
                  command=win.destroy).pack(side="left", padx=8)

    def _confirm_shutdown(self):
        """Ask before shutting down the PC."""
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg=C["primary"])

        sw, sh = self._sw, self._sh
        w, h = 300, 140
        win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

        tk.Label(win, text="🔴  Shutdown Computer?",
                 bg=C["primary"], fg="white",
                 font=("Segoe UI", 11, "bold"), pady=15).pack()
        tk.Label(win, text="Your PC will shut down in 5 seconds.",
                 bg=C["primary"], fg=C["text_muted"],
                 font=("Segoe UI", 9)).pack()

        btn_row = tk.Frame(win, bg=C["primary"])
        btn_row.pack(pady=10)

        def _yes():
            win.destroy()
            self._do_shutdown()

        tk.Button(btn_row, text="  🔴 Shutdown  ",
                  bg=C["red"], fg="white",
                  font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=5,
                  command=_yes).pack(side="left", padx=8)
        tk.Button(btn_row, text="  Cancel  ",
                  bg=C["accent"], fg="white",
                  font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=5,
                  command=win.destroy).pack(side="left", padx=8)

    def _do_shutdown(self):
        from monitor import do_shutdown
        do_shutdown()

    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITIES
    # ═══════════════════════════════════════════════════════════════════════════
    def _welcome(self):
        """Send welcome message on startup."""
        welcome = (f"👋 Hi! Welcome to {SETTINGS['app_name']} 🌹🌺\n"
                   "How can we help?")
        self.show_auto(welcome)

    def _update_badge(self):
        try:
            if self.unread > 0:
                self._badge_lbl.config(text=str(self.unread))
            else:
                self._badge_lbl.config(text="")
        except Exception:
            pass

    def _scroll_bottom(self):
        try:
            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1.0)
        except Exception:
            pass

    def _on_frame_configure(self, event=None):
        try:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except Exception:
            pass

    def _on_canvas_resize(self, event=None):
        try:
            self.canvas.itemconfig(self._canvas_window, width=event.width)
        except Exception:
            pass

    def _clear(self):
        """Destroy all child widgets."""
        for w in self.root.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass

    def run(self):
        self.root.mainloop()
