import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from utils import parse_datetime


class NotificationManager:
    def __init__(self, app, check_interval=30000):
        self.app = app
        self.check_interval = check_interval
        self._notified_ids = set()
        self._after_id = None

    def start(self):
        self._check()
        self._schedule()

    def stop(self):
        if self._after_id:
            self.app.after_cancel(self._after_id)
            self._after_id = None

    def _schedule(self):
        self._after_id = self.app.after(self.check_interval, self._check_and_schedule)

    def _check_and_schedule(self):
        self._check()
        self._schedule()

    def _check(self):
        now = datetime.now()
        for event in self.app.events:
            start = parse_datetime(event["start_date"])
            end = parse_datetime(event["end_date"])
            if start <= now <= end and event["id"] not in self._notified_ids:
                self._notified_ids.add(event["id"])
                self.app.after(0, self._show_notification, event)

    def _show_notification(self, event):
        win = tk.Toplevel(self.app)
        win.title("Compromisso agora!")
        win.geometry("400x200")
        win.resizable(False, False)
        win.transient(self.app)
        win.grab_set()

        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - 200
        y = (win.winfo_screenheight() // 2) - 100
        win.geometry(f"+{x}+{y}")

        frame = tk.Frame(win, bg=event.get("color", "#4A90D9"), padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame, text="📅 Compromisso agora!",
            font=("Segoe UI", 14, "bold"), bg=frame["bg"],
            fg="white"
        ).pack(anchor="w")

        tk.Label(
            frame, text=event["title"],
            font=("Segoe UI", 18, "bold"), bg=frame["bg"],
            fg="white"
        ).pack(anchor="w", pady=(8, 4))

        start = parse_datetime(event["start_date"])
        end = parse_datetime(event["end_date"])
        tk.Label(
            frame, text=f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}",
            font=("Segoe UI", 12), bg=frame["bg"],
            fg="white"
        ).pack(anchor="w")

        btn_frame = tk.Frame(frame, bg=frame["bg"])
        btn_frame.pack(fill="x", pady=(16, 0))

        tk.Button(
            btn_frame, text="OK",
            font=("Segoe UI", 11, "bold"),
            bg="white", fg=event.get("color", "#4A90D9"),
            padx=20, command=win.destroy
        ).pack(side="right")

        if event.get("description"):
            desc = event["description"]
            if len(desc) > 80:
                desc = desc[:77] + "..."
            tk.Label(
                frame, text=desc,
                font=("Segoe UI", 10), bg=frame["bg"],
                fg="white", wraplength=360
            ).pack(anchor="w", pady=(8, 0))
