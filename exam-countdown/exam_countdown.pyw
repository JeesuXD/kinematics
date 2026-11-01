#!/usr/bin/env python3
"""Exam Countdown: a small desktop widget showing the hours left until your exams.

Only uses the Python standard library (tkinter), so it runs on Windows, macOS
and Linux without installing anything extra.

    Drag with the left mouse button to move it (the position is remembered).
    Right-click for: Always on top, Reload dates, Edit dates, Quit.

Exam dates live in exams.json next to this file. Times are Indian Standard
Time, so the countdown stays right even if the laptop clock is set to another
time zone.
"""

import json
import os
import subprocess
import sys
import tkinter as tk
from datetime import datetime, timedelta, timezone
from pathlib import Path

IST = timezone(timedelta(hours=5, minutes=30))
HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "exams.json"
STATE_PATH = HERE / ".widget_state.json"

DEFAULT_CONFIG = {
    "exams": [
        {"name": "JEE Main (Session 1)", "date": "2027-01-20 09:00", "confirmed": False},
        {"name": "CBSE Class 12 Boards", "date": "2027-02-16 10:30", "confirmed": False},
        {"name": "JEE Advanced", "date": "2027-05-16 09:00", "confirmed": False},
    ],
    "opacity": 0.92,
    "always_on_top": False,
}

BG = "#11141c"
CARD = "#1a1f2b"
TEXT = "#f2f4f8"
DIM = "#8a93a6"
ACCENTS = ["#ff9f43", "#4dabf7", "#b197fc", "#63e6be", "#ff6b6b"]
DONE = "#51cf66"

if sys.platform.startswith("win"):
    FONT = "Segoe UI"
elif sys.platform == "darwin":
    FONT = "Helvetica Neue"
else:
    FONT = "DejaVu Sans"

REFRESH_MS = 30_000  # hours only change once an hour, but keep it fresh after sleep


def load_config():
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding="utf-8")
        return dict(DEFAULT_CONFIG)
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return dict(DEFAULT_CONFIG)
    exams = []
    for exam in cfg.get("exams", []):
        try:
            when = datetime.strptime(exam["date"], "%Y-%m-%d %H:%M").replace(tzinfo=IST)
        except (KeyError, ValueError):
            continue
        exams.append({
            "name": str(exam.get("name", "Exam")),
            "when": when,
            "confirmed": bool(exam.get("confirmed", False)),
        })
    cfg["exams"] = exams
    return cfg


def load_state():
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(state):
    try:
        STATE_PATH.write_text(json.dumps(state), encoding="utf-8")
    except OSError:
        pass


def describe(when, now):
    """Return (big number text, unit text, detail text, finished?) for one exam."""
    seconds = (when - now).total_seconds()
    date_text = f"{when.day} {when:%b %Y}, {when:%a}"
    if seconds > 0:
        hours = int(seconds // 3600)
        days = int(seconds // 86400)
        day_word = "day" if days == 1 else "days"
        return f"{hours:,}", "hrs left", f"{days} {day_word}  ·  {date_text}", False
    if seconds > -12 * 3600:
        return "Today", "", "All the best! You've got this.", True
    return "Done", "", date_text, True


class CountdownWidget:
    def __init__(self, root):
        self.root = root
        self.state = load_state()
        self.cfg = load_config()
        self.drag_from = None

        root.title("Exam Countdown")
        root.overrideredirect(True)  # no title bar, looks like a widget
        root.configure(bg=BG)
        try:
            root.attributes("-alpha", float(self.cfg.get("opacity", 0.92)))
        except (tk.TclError, ValueError):
            pass

        self.on_top = tk.BooleanVar(value=self.state.get("always_on_top", self.cfg.get("always_on_top", False)))
        root.attributes("-topmost", self.on_top.get())

        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_checkbutton(label="Always on top", variable=self.on_top, command=self.toggle_on_top)
        self.menu.add_command(label="Reload dates", command=self.reload)
        self.menu.add_command(label="Edit dates…", command=self.edit_dates)
        self.menu.add_separator()
        self.menu.add_command(label="Quit", command=root.destroy)

        self.body = tk.Frame(root, bg=BG, padx=14, pady=12)
        self.body.pack(fill="both", expand=True)
        self.build()
        self.place_window()
        self.tick()

    # ---------- layout ----------
    def build(self):
        for child in self.body.winfo_children():
            child.destroy()
        self.rows = []

        header = tk.Frame(self.body, bg=BG)
        header.pack(fill="x", pady=(0, 8))
        tk.Label(header, text="EXAM COUNTDOWN", bg=BG, fg=DIM, font=(FONT, 9, "bold")).pack(side="left")
        self.clock = tk.Label(header, text="", bg=BG, fg=DIM, font=(FONT, 9))
        self.clock.pack(side="right")

        for i, exam in enumerate(self.cfg["exams"]):
            accent = ACCENTS[i % len(ACCENTS)]
            card = tk.Frame(self.body, bg=CARD)
            card.pack(fill="x", pady=4)
            tk.Frame(card, bg=accent, width=4).pack(side="left", fill="y")
            inner = tk.Frame(card, bg=CARD, padx=12, pady=8)
            inner.pack(side="left", fill="both", expand=True)

            name = exam["name"] + ("" if exam["confirmed"] else "  (tentative)")
            tk.Label(inner, text=name, bg=CARD, fg=TEXT, font=(FONT, 10, "bold"), anchor="w").pack(fill="x")
            line = tk.Frame(inner, bg=CARD)
            line.pack(fill="x")
            big = tk.Label(line, text="", bg=CARD, fg=accent, font=(FONT, 24, "bold"))
            big.pack(side="left")
            unit = tk.Label(line, text="", bg=CARD, fg=DIM, font=(FONT, 10))
            unit.pack(side="left", anchor="s", padx=(6, 0), pady=(0, 7))
            detail = tk.Label(inner, text="", bg=CARD, fg=DIM, font=(FONT, 9), anchor="w")
            detail.pack(fill="x")
            self.rows.append((exam, big, unit, detail, accent))

        if not self.cfg["exams"]:
            tk.Label(self.body, text="No exams found in exams.json", bg=BG, fg=TEXT, font=(FONT, 10)).pack()

        self.bind_all_children(self.root)

    def bind_all_children(self, widget):
        widget.bind("<ButtonPress-1>", self.start_drag)
        widget.bind("<B1-Motion>", self.do_drag)
        widget.bind("<ButtonRelease-1>", self.end_drag)
        widget.bind("<Button-3>", self.show_menu)
        widget.bind("<Button-2>", self.show_menu)  # right-click on some macOS setups
        widget.bind("<Control-Button-1>", self.show_menu)  # Mac trackpad
        for child in widget.winfo_children():
            if not isinstance(child, tk.Menu):
                self.bind_all_children(child)

    def place_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_reqwidth(), self.root.winfo_reqheight()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x, y = self.state.get("x"), self.state.get("y")
        if x is None or y is None or not (0 <= x < sw - 40 and 0 <= y < sh - 40):
            x, y = sw - w - 30, 60  # top-right corner by default
        self.root.geometry(f"+{x}+{y}")

    # ---------- updates ----------
    def refresh(self):
        now = datetime.now(IST)
        self.clock.config(text=now.strftime("%d %b, %I:%M %p IST"))
        for exam, big, unit, detail, accent in self.rows:
            number, unit_text, detail_text, finished = describe(exam["when"], now)
            big.config(text=number, fg=DONE if finished else accent)
            unit.config(text=unit_text)
            detail.config(text=detail_text)

    def tick(self):
        self.refresh()
        self.root.after(REFRESH_MS, self.tick)

    def reload(self):
        self.cfg = load_config()
        self.build()
        self.refresh()
        self.root.update_idletasks()

    # ---------- interaction ----------
    def start_drag(self, event):
        self.drag_from = (event.x_root - self.root.winfo_x(), event.y_root - self.root.winfo_y())

    def do_drag(self, event):
        if self.drag_from:
            dx, dy = self.drag_from
            self.root.geometry(f"+{event.x_root - dx}+{event.y_root - dy}")

    def end_drag(self, _event):
        self.drag_from = None
        self.state.update(x=self.root.winfo_x(), y=self.root.winfo_y())
        save_state(self.state)

    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)
        self.menu.grab_release()

    def toggle_on_top(self):
        self.root.attributes("-topmost", self.on_top.get())
        self.state["always_on_top"] = self.on_top.get()
        save_state(self.state)

    def edit_dates(self):
        path = str(CONFIG_PATH)
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-t", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except OSError:
            pass


def main():
    root = tk.Tk()
    CountdownWidget(root)
    root.mainloop()


if __name__ == "__main__":
    main()
