import tkinter as tk
from datetime import datetime, timedelta
from utils import PRIORITIES, today_str, to_date_str, format_time, get_priority_info
from database import (
    get_all_tasks, get_tasks_by_date_range, get_high_priority_tasks,
    search_tasks, toggle_completed, get_overdue_tasks, get_tasks_no_date
)


class TaskListView(tk.Frame):
    def __init__(self, parent, app, mode="all"):
        super().__init__(parent, bg="#FAFAFA")
        self.app = app
        self.mode = mode
        self._build_ui()

    def _build_ui(self):
        # Search bar
        search_frame = tk.Frame(self, bg="white", padx=16, pady=12)
        search_frame.pack(fill="x")

        titles = {
            "week": "Próximos 7 dias",
            "all": "Todas as Tarefas",
            "important": "Importante",
        }
        tk.Label(
            search_frame, text=titles.get(self.mode, "Tarefas"),
            font=("Segoe UI", 18, "bold"), bg="white", fg="#1A1A2E"
        ).pack(anchor="w")

        self.search_entry = tk.Entry(
            search_frame, font=("Segoe UI", 12),
            relief="solid", bd=1
        )
        self.search_entry.pack(fill="x", pady=(6, 0))
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter())

        # List container
        container = tk.Frame(self, bg="#FAFAFA")
        container.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        self.canvas = tk.Canvas(container, bg="#FAFAFA", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable = tk.Frame(self.canvas, bg="#FAFAFA")

        self.scrollable.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh(self):
        self._filter()

    def _filter(self):
        for w in self.scrollable.winfo_children():
            w.destroy()

        query = self.search_entry.get().strip()
        now = datetime.now()

        if query:
            tasks = search_tasks(query)
        elif self.mode == "week":
            start = to_date_str(now)
            end = to_date_str(now + timedelta(days=7))
            tasks = get_tasks_by_date_range(start, end)
        elif self.mode == "important":
            tasks = get_high_priority_tasks()
        else:
            tasks = get_all_tasks()

        # Group by date
        groups = {}
        no_date = []
        for t in tasks:
            d = t.get("task_date")
            if d:
                if d not in groups:
                    groups[d] = []
                groups[d].append(t)
            else:
                no_date.append(t)

        # Render grouped
        for date_str in sorted(groups.keys()):
            date_tasks = groups[date_str]
            d = datetime.strptime(date_str, "%Y-%m-%d")
            label = d.strftime("%A, %d/%m").capitalize()
            if date_str == today_str():
                label = "Hoje"
            elif date_str == (now + timedelta(days=1)).strftime("%Y-%m-%d"):
                label = "Amanhã"

            tk.Label(
                self.scrollable, text=label,
                font=("Segoe UI", 13, "bold"),
                bg="#FAFAFA", fg="#1A1A2E"
            ).pack(anchor="w", pady=(12, 4))

            for t in date_tasks:
                self._create_task_card(t)

        if no_date:
            tk.Label(
                self.scrollable, text="Sem data",
                font=("Segoe UI", 13, "bold"),
                bg="#FAFAFA", fg="#6B7280"
            ).pack(anchor="w", pady=(12, 4))
            for t in no_date:
                self._create_task_card(t)

        if not groups and not no_date:
            tk.Label(
                self.scrollable, text="Nenhuma tarefa encontrada",
                font=("Segoe UI", 12), bg="#FAFAFA", fg="#9CA3AF"
            ).pack(pady=30)

    def _create_task_card(self, task):
        is_completed = task.get("completed", 0)
        prio = get_priority_info(task.get("priority", 1))
        card_bg = "#F0FDF4" if is_completed else "white"

        card = tk.Frame(self.scrollable, bg=card_bg, padx=12, pady=8, highlightthickness=0)
        card.pack(fill="x", pady=2)

        bar = tk.Frame(card, bg=prio["color"], width=4)
        bar.pack(side="left", fill="y")
        bar.pack_propagate(False)

        chk_frame = tk.Frame(card, bg=card_bg)
        chk_frame.pack(side="left", padx=(8, 8))

        chk_text = "✓" if is_completed else "○"
        chk = tk.Label(
            chk_frame, text=chk_text,
            font=("Segoe UI", 16), bg=card_bg,
            fg="#34C759" if is_completed else "#D1D5DB",
            cursor="hand2"
        )
        chk.pack()

        content = tk.Frame(card, bg=card_bg)
        content.pack(side="left", fill="x", expand=True)

        fg = "#9CA3AF" if is_completed else "#1A1A2E"
        tk.Label(
            content, text=task["title"],
            font=("Segoe UI", 12, "bold" if not is_completed else "italic"),
            bg=card_bg, fg=fg
        ).pack(anchor="w")

        meta = tk.Frame(content, bg=card_bg)
        meta.pack(anchor="w")

        if task.get("task_time"):
            tk.Label(
                meta, text=format_time(task["task_time"]),
                font=("Segoe UI", 10), bg=card_bg, fg="#6B7280"
            ).pack(side="left", padx=(0, 6))

        tk.Label(
            meta, text=prio["label"],
            font=("Segoe UI", 9, "bold"), bg=prio["light"],
            fg=prio["color"], padx=6, pady=1
        ).pack(side="left")

        if task.get("project"):
            tk.Label(
                meta, text=task["project"],
                font=("Segoe UI", 9), bg="#E8F0FE",
                fg="#007AFF", padx=6, pady=1
            ).pack(side="left", padx=(4, 0))

        if is_completed:
            tk.Label(
                meta, text="Finalizado",
                font=("Segoe UI", 9, "bold"), bg=card_bg, fg="#34C759"
            ).pack(side="right")

        subtasks = task.get("subtasks", [])
        if subtasks:
            st_done = sum(1 for s in subtasks if s["completed"])
            tk.Label(
                content, text=f"  {st_done}/{len(subtasks)} subtarefas",
                font=("Segoe UI", 9), bg=card_bg, fg="#9CA3AF"
            ).pack(anchor="w")

        task_id = task["id"]
        chk.bind("<Button-1>", lambda e: self._toggle(task_id))
        card.bind("<Button-1>", lambda e: self.app.show_task_detail(task_id))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e: self.app.show_task_detail(task_id))

    def _toggle(self, task_id):
        toggle_completed(task_id)
        self.app.refresh_all()
