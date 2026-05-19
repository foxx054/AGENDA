import calendar as cal_mod
import tkinter as tk
from datetime import datetime, timedelta
from utils import WEEKDAYS, MONTHS, to_date_str, get_priority_info
from database import get_tasks_by_date, get_tasks_by_date_range


class CalendarWidget(tk.Frame):
    def __init__(self, parent, app, colors):
        super().__init__(parent, bg=colors["bg"])
        self.app = app
        self.C = colors
        self.current_date = datetime.now().replace(day=1)
        self.selected_date = datetime.now()
        self._build_ui()
        self._render()

    def _build_ui(self):
        self.header = tk.Frame(self, bg=self.C["surface"], padx=20, pady=12)
        self.header.pack(fill="x")

        tk.Button(
            self.header, text="‹", font=("Segoe UI", 22),
            bg=self.C["surface"], fg=self.C["accent"],
            relief="flat", bd=0, cursor="hand2",
            command=self._prev_month
        ).pack(side="left")

        self.title_label = tk.Label(
            self.header, font=("Segoe UI", 18, "bold"),
            bg=self.C["surface"], fg=self.C["text"]
        )
        self.title_label.pack(side="left", expand=True)

        tk.Button(
            self.header, text="›", font=("Segoe UI", 22),
            bg=self.C["surface"], fg=self.C["accent"],
            relief="flat", bd=0, cursor="hand2",
            command=self._next_month
        ).pack(side="right")

        # Weekday headers
        wd_frame = tk.Frame(self, bg=self.C["surface"])
        wd_frame.pack(fill="x", padx=8)
        for d in WEEKDAYS:
            tk.Label(
                wd_frame, text=d, font=("Segoe UI", 10, "bold"),
                bg=self.C["surface"], fg=self.C["text_sec"],
                width=10, pady=6
            ).pack(side="left", expand=True)

        sep = tk.Frame(self, bg=self.C["border"], height=1)
        sep.pack(fill="x", padx=8)

        # Scrollable area
        self.top_frame = tk.Frame(self, bg=self.C["bg"])
        self.top_frame.pack(fill="both", expand=True, padx=8)

        self.canvas = tk.Canvas(self.top_frame, bg=self.C["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.top_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable = tk.Frame(self.canvas, bg=self.C["bg"])

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
        grid = tk.Frame(self.scrollable, bg=self.C["surface"])
        grid.pack(fill="x", pady=(8, 12))

        cal = cal_mod.Calendar()
        days = list(cal.itermonthdates(year, month))

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

        row_frame = tk.Frame(grid, bg=self.C["surface"])
        row_frame.pack(fill="x")
        today = datetime.now()

        for i, d in enumerate(days):
            if i > 0 and i % 7 == 0:
                row_frame = tk.Frame(grid, bg=self.C["surface"])
                row_frame.pack(fill="x")

            d_str = to_date_str(d)
            day_tasks = task_map.get(d_str, [])
            n_pending = sum(1 for t in day_tasks if not t["completed"])
            is_selected = d == self.selected_date.date()
            is_today = d == today.date()
            is_current = d.month == month

            cell = tk.Frame(
                row_frame, height=64,
                bg=self.C["surface"], highlightthickness=1,
                highlightbackground="#F0F0F0"
            )
            cell.pack(side="left", expand=True, fill="both")
            cell.pack_propagate(False)

            day_fg = self.C["accent"] if is_today else (self.C["text"] if is_current else "#C7C7CC")
            day_bg = self.C["accent"] if is_selected else self.C["surface"]
            if is_selected:
                day_fg = "white"

            tk.Label(
                cell, text=str(d.day), font=("Segoe UI", 12, "bold" if is_today else "normal"),
                bg=day_bg, fg=day_fg
            ).pack(pady=(4, 0))

            if n_pending > 0:
                dots = tk.Frame(cell, bg=day_bg)
                dots.pack()
                for _ in range(min(n_pending, 3)):
                    tk.Label(
                        dots, text="●", font=("Segoe UI", 5),
                        bg=day_bg, fg="#FF3B30"
                    ).pack(side="left", padx=1)

            cell.bind("<Button-1>", lambda e, date=d: self._select_date(date))

        self._render_day_tasks()

    def _select_date(self, date):
        self.selected_date = datetime(date.year, date.month, date.day)
        self._render_day_tasks()

    def _render_day_tasks(self):
        for w in self.scrollable.winfo_children():
            if hasattr(w, "_is_day_section"):
                w.destroy()

        d_str = to_date_str(self.selected_date)
        tasks = get_tasks_by_date(d_str)

        section = tk.Frame(self.scrollable, bg=self.C["bg"])
        section._is_day_section = True
        section.pack(fill="x", padx=4, pady=(0, 12))

        tk.Label(
            section, text=f"Tarefas de {self.selected_date.strftime('%d/%m/%Y')}",
            font=("Segoe UI", 14, "bold"),
            bg=self.C["bg"], fg=self.C["text"]
        ).pack(anchor="w", pady=(8, 6))

        if not tasks:
            empty = tk.Frame(
                section, bg=self.C["surface"], padx=20, pady=24,
                highlightthickness=1, highlightbackground=self.C["border"]
            )
            empty.pack(fill="x")
            tk.Label(
                empty, text="Nenhuma tarefa neste dia",
                font=("Segoe UI", 12), bg=self.C["surface"], fg=self.C["text_sec"]
            ).pack()
        else:
            for task in tasks:
                self._create_task_card(section, task)

    def _create_task_card(self, parent, task):
        is_completed = task.get("completed", 0)
        prio = get_priority_info(task.get("priority", 1))

        card = tk.Frame(
            parent, bg=self.C["surface"], padx=14, pady=10,
            highlightthickness=1, highlightbackground=self.C["border"]
        )
        card.pack(fill="x", pady=2)

        bar = tk.Frame(card, bg=prio["color"], width=3)
        bar.pack(side="left", fill="y")
        bar.pack_propagate(False)

        content = tk.Frame(card, bg=self.C["surface"])
        content.pack(side="left", fill="x", expand=True, padx=(10, 0))

        tk.Label(
            content, text=task["title"],
            font=("Segoe UI", 13, "bold"), bg=self.C["surface"], fg=self.C["text"],
            anchor="w"
        ).pack(fill="x")

        meta = tk.Frame(content, bg=self.C["surface"])
        meta.pack(anchor="w", pady=(2, 0))

        if task.get("task_time"):
            tk.Label(
                meta, text=task["task_time"][:5],
                font=("Segoe UI", 11), bg=self.C["surface"], fg=self.C["text_sec"]
            ).pack(side="left", padx=(0, 6))

        prio_badge = tk.Frame(meta, bg=prio["light"], padx=6, pady=1)
        prio_badge.pack(side="left")
        tk.Label(
            prio_badge, text=prio["label"],
            font=("Segoe UI", 9, "bold"),
            bg=prio["light"], fg=prio["color"]
        ).pack()

        task_id = task["id"]
        card.bind("<Button-1>", lambda e: self.app.show_task_detail(task_id))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e: self.app.show_task_detail(task_id))
