import tkinter as tk
from datetime import datetime, timedelta
from database import toggle_completed


class NotificationManager:
    def __init__(self, app, check_interval=30000):
        self.app = app
        self.check_interval = check_interval
        self._notified_ids = set()
        self._after_id = None
        self._active_windows = []

    def start(self):
        self._check()
        self._schedule()

    def check_now(self):
        self._check()

    def stop(self):
        if self._after_id:
            self.app.after_cancel(self._after_id)
            self._after_id = None
        for w in self._active_windows:
            try:
                w.destroy()
            except:
                pass

    def _schedule(self):
        self._after_id = self.app.after(self.check_interval, self._check_and_schedule)

    def _check_and_schedule(self):
        self._check()
        self._schedule()

    def _check(self):
        now = datetime.now()
        for task in self.app.tasks:
            if task.get("completed"):
                continue
            if task["id"] in self._notified_ids:
                continue

            task_date = task.get("task_date")
            task_time = task.get("task_time")
            if not task_date or not task_time:
                continue

            try:
                dt_str = f"{task_date} {task_time}"
                task_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            except:
                continue

            reminder = task.get("reminder")
            if reminder is None:
                notify_time = task_dt
            else:
                notify_time = task_dt - timedelta(minutes=reminder)

            if notify_time <= now <= task_dt:
                self._notified_ids.add(task["id"])
                self.app.after(0, self._show_notification, task)

        # Birthday reminders
        from database import get_setting, get_contacts_with_birthday_this_month
        if get_setting("birthday_reminder", "1") == "1":
            today = now.strftime("%m-%d")
            for c in get_contacts_with_birthday_this_month():
                cid = f"bday_{c['id']}"
                if cid in self._notified_ids:
                    continue
                bday = c.get("birthday", "")
                if bday and bday[5:] == today:
                    self._notified_ids.add(cid)
                    self.app.after(0, self._show_birthday_notification, c)

    def _show_notification(self, task):
        # Close existing notification for this task
        for w in self._active_windows:
            try:
                w.destroy()
            except:
                pass
        self._active_windows.clear()

        win = tk.Toplevel(self.app)
        win.title("Lembrete")
        win.geometry("380x200")
        win.resizable(False, False)
        win.transient(self.app)
        win.grab_set()
        win.attributes("-topmost", True)

        self._active_windows.append(win)

        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - 190
        y = (win.winfo_screenheight() // 2) - 100
        win.geometry(f"+{x}+{y}")

        from utils import PRIORITIES, format_time
        prio = PRIORITIES[task.get("priority", 1)]

        frame = tk.Frame(win, bg=prio["color"], padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame, text="⏰ Lembrete",
            font=("Segoe UI", 14, "bold"), bg=frame["bg"], fg="white"
        ).pack(anchor="w")

        tk.Label(
            frame, text=task["title"],
            font=("Segoe UI", 18, "bold"), bg=frame["bg"], fg="white"
        ).pack(anchor="w", pady=(8, 2))

        time_str = format_time(task.get("task_time", ""))
        if time_str:
            tk.Label(
                frame, text=time_str,
                font=("Segoe UI", 12), bg=frame["bg"], fg="white"
            ).pack(anchor="w")

        btn_frame = tk.Frame(frame, bg=frame["bg"])
        btn_frame.pack(fill="x", pady=(16, 0))

        tk.Button(
            btn_frame, text="Adiar 10 min",
            font=("Segoe UI", 10), bg="white",
            fg=prio["color"], bd=0, padx=14, pady=4,
            command=lambda: self._snooze(win, task)
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_frame, text="Concluir",
            font=("Segoe UI", 10, "bold"), bg="white",
            fg=prio["color"], bd=0, padx=14, pady=4,
            command=lambda: self._complete(win, task)
        ).pack(side="right")

    def _complete(self, win, task):
        toggle_completed(task["id"])
        self.app.refresh_all()
        try:
            win.destroy()
        except:
            pass

    def _show_birthday_notification(self, contact):
        for w in self._active_windows:
            try:
                w.destroy()
            except:
                pass
        self._active_windows.clear()

        win = tk.Toplevel(self.app)
        win.title("Aniversário!")
        win.geometry("380x160")
        win.resizable(False, False)
        win.transient(self.app)
        win.grab_set()
        win.attributes("-topmost", True)

        self._active_windows.append(win)

        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - 190
        y = (win.winfo_screenheight() // 2) - 80
        win.geometry(f"+{x}+{y}")

        frame = tk.Frame(win, bg="#FF9500")
        frame.pack(fill="both", expand=True, padx=0, pady=0)

        tk.Label(
            frame, text="🎂 Aniversário",
            font=("Segoe UI", 14, "bold"), bg=frame["bg"], fg="white"
        ).pack(anchor="w", padx=20, pady=(20, 4))

        tk.Label(
            frame, text=contact["name"],
            font=("Segoe UI", 20, "bold"), bg=frame["bg"], fg="white"
        ).pack(anchor="w", padx=20, pady=(0, 8))

        tk.Button(
            frame, text="Fechar",
            font=("Segoe UI", 10, "bold"), bg="white",
            fg="#FF9500", bd=0, padx=14, pady=4, cursor="hand2",
            command=lambda: self._close_notification(win)
        ).pack(anchor="w", padx=20)

    def _close_notification(self, win):
        try:
            win.destroy()
        except:
            pass

    def _snooze(self, win, task):
        try:
            win.destroy()
        except:
            pass
        # Re-schedule notification in 10 minutes
        self._notified_ids.discard(task["id"])
