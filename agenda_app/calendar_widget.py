import calendar as cal_mod
import tkinter as tk
from datetime import datetime, timedelta
from utils import WEEKDAYS, MONTHS, PRIORITIES, today_str, to_date_str, get_priority_info
from database import get_tasks_by_date, get_tasks_by_date_range


class CalendarWidget(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#FAFAFA")
        self.app = app
        self.current_date = datetime.now().replace(day=1)
        self.selected_date = datetime.now()
        self._build_ui()
        self._render()

    def _build_ui(self):
        # Header
        self.header = tk.Frame(self, bg="white", padx=16, pady=10)
        self.header.pack(fill="x")

        tk.Button(
            self.header, text="<", font=("Segoe UI", 16, "bold"),
            bg="white", fg="#007AFF", bd=0,
            command=self._prev_month
        ).pack(side="left")

        self.title_label = tk.Label(
            self.header, font=("Segoe UI", 18, "bold"),
            bg="white", fg="#1A1A2E"
        )
        self.title_label.pack(side="left", expand=True)

        tk.Button(
            self.header, text=">", font=("Segoe UI", 16, "bold"),
            bg="white", fg="#007AFF", bd=0,
            command=self._next_month
        ).pack(side="right")

        # Weekday headers
        wd_frame = tk.Frame(self, bg="white", padx=8)
        wd_frame.pack(fill="x")
        for d in WEEKDAYS:
            tk.Label(
                wd_frame, text=d, font=("Segoe UI", 9, "bold"),
                bg="white", fg="#6B7280", width=10
            ).pack(side="left", expand=True)

        # Grid + events split
        self.top_frame = tk.Frame(self, bg="#FAFAFA")
        self.top_frame.pack(fill="both", expand=True, padx=8)

        self.canvas = tk.Canvas(self.top_frame, bg="#FAFAFA", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.top_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable = tk.Frame(self.canvas, bg="#FAFAFA")

        self.scrollable.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _prev_month(self):
        y, m = self.current_date.year, self.current_date.month
        m -= 1
        if m < 1:
            m = 12
            y -= 1
        self.current_date = self.current_date.replace(year=y, month=m)
        self._render()

    def _next_month(self):
        y, m = self.current_date.year, self.current_date.month
        m += 1
        if m > 12:
            m = 1
            y += 1
        self.current_date = self.current_date.replace(year=y, month=m)
        self._render()

    def refresh(self):
        self._render()

    def _render(self):
        for w in self.scrollable.winfo_children():
            w.destroy()

        year = self.current_date.year
        month = self.current_date.month
        self.title_label.config(text=f"{MONTHS[month-1]} {year}")

        # Calendar grid
        grid = tk.Frame(self.scrollable, bg="white")
        grid.pack(fill="x", pady=(0, 12))

        cal = cal_mod.Calendar()
        days = list(cal.itermonthdates(year, month))

        # Get tasks for visible month range
        if days:
            first_day = to_date_str(days[0])
            last_day = to_date_str(days[-1])
            month_tasks = get_tasks_by_date_range(first_day, last_day)
            task_map = {}
            for t in month_tasks:
                d = t.get("task_date")
                if d:
                    if d not in task_map:
                        task_map[d] = []
                    task_map[d].append(t)

        row_frame = tk.Frame(grid)
        row_frame.pack(fill="x")
        today = datetime.now()

        for i, d in enumerate(days):
            if i > 0 and i % 7 == 0:
                row_frame = tk.Frame(grid)
                row_frame.pack(fill="x")

            d_str = to_date_str(d)
            day_tasks = task_map.get(d_str, [])
            n_pending = sum(1 for t in day_tasks if not t["completed"])
            is_selected = d == self.selected_date.date()
            is_today = d == today.date()
            is_current = d.month == month

            bg_color = "#007AFF" if is_selected else ("#E8F0FE" if is_today else "white")
            fg_color = "white" if is_selected else ("#007AFF" if is_today else ("#9CA3AF" if not is_current else "#1A1A2E"))

            cell = tk.Frame(
                row_frame, height=70,
                bg=bg_color, highlightthickness=1,
                highlightbackground="#F3F4F6"
            )
            cell.pack(side="left", expand=True, fill="both")
            cell.pack_propagate(False)

            tk.Label(
                cell, text=str(d.day), font=("Segoe UI", 11, "bold"),
                bg=bg_color, fg=fg_color
            ).pack(pady=(4, 0))

            if n_pending > 0:
                tk.Label(
                    cell, text="●" * min(n_pending, 3),
                    font=("Segoe UI", 6), bg=bg_color, fg="#FF3B30"
                ).pack()

            cell.bind("<Button-1>", lambda e, date=d: self._select_date(date))

        # Selected date tasks
        self._render_day_tasks()

    def _select_date(self, date):
        self.selected_date = datetime(date.year, date.month, date.day)
        self._render_day_tasks()

    def _render_day_tasks(self):
        # Remove existing day section if any
        for w in self.scrollable.winfo_children():
            if hasattr(w, "_is_day_section"):
                w.destroy()

        d_str = to_date_str(self.selected_date)
        tasks = get_tasks_by_date(d_str)

        section = tk.Frame(self.scrollable, bg="#FAFAFA")
        section._is_day_section = True
        section.pack(fill="x", padx=8, pady=(0, 12))

        tk.Label(
            section, text=f"Tarefas - {self.selected_date.strftime('%d/%m/%Y')}",
            font=("Segoe UI", 14, "bold"),
            bg="#FAFAFA", fg="#1A1A2E"
        ).pack(anchor="w", pady=(0, 8))

        if not tasks:
            tk.Label(
                section, text="Nenhuma tarefa neste dia",
                font=("Segoe UI", 11), bg="#FAFAFA", fg="#9CA3AF"
            ).pack(anchor="w")
        else:
            for task in tasks:
                self._create_task_card(section, task)

    def _create_task_card(self, parent, task):
        is_completed = task.get("completed", 0)
        prio = get_priority_info(task.get("priority", 1))
        card_bg = "#F0FDF4" if is_completed else "white"

        card = tk.Frame(parent, bg=card_bg, padx=12, pady=6, highlightthickness=0)
        card.pack(fill="x", pady=2)

        bar = tk.Frame(card, bg=prio["color"], width=4)
        bar.pack(side="left", fill="y")
        bar.pack_propagate(False)

        content = tk.Frame(card, bg=card_bg)
        content.pack(side="left", fill="x", expand=True, padx=(8, 0))

        tk.Label(
            content, text=task["title"],
            font=("Segoe UI", 12, "bold" if not is_completed else "italic"),
            bg=card_bg, fg="#9CA3AF" if is_completed else "#1A1A2E"
        ).pack(anchor="w")

        meta = tk.Frame(content, bg=card_bg)
        meta.pack(anchor="w")
        if task.get("task_time"):
            tk.Label(
                meta, text=task["task_time"][:5],
                font=("Segoe UI", 10), bg=card_bg, fg="#6B7280"
            ).pack(side="left", padx=(0, 6))
        tk.Label(
            meta, text=prio["label"],
            font=("Segoe UI", 9, "bold"), bg=prio["light"],
            fg=prio["color"], padx=6, pady=1
        ).pack(side="left")

        task_id = task["id"]
        card.bind("<Button-1>", lambda e: self.app.show_task_detail(task_id))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e: self.app.show_task_detail(task_id))
