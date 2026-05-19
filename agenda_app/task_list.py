import tkinter as tk
from datetime import datetime, timedelta
from utils import (
    PRIORITIES, today_str, to_date_str, format_time, get_priority_info
)
from database import (
    get_all_tasks, get_tasks_by_date_range, get_high_priority_tasks,
    search_tasks, toggle_completed, get_overdue_tasks, get_tasks_no_date
)


class TaskListView(tk.Frame):
    def __init__(self, parent, app, colors, mode="all"):
        super().__init__(parent, bg=colors["bg"])
        self.app = app
        self.C = colors
        self.mode = mode
        self._build_ui()

    def _build_ui(self):
        search_frame = tk.Frame(self, bg=self.C["surface"], padx=20, pady=16)
        search_frame.pack(fill="x")

        titles = {
            "week": "Próximos 7 dias",
            "all": "Todas as Tarefas",
            "important": "Importante",
        }
        tk.Label(
            search_frame, text=titles.get(self.mode, "Tarefas"),
            font=("Segoe UI", 20, "bold"), bg=self.C["surface"], fg=self.C["text"]
        ).pack(anchor="w")

        entry_frame = tk.Frame(search_frame, bg=self.C["border"], bd=0, highlightthickness=0)
        entry_frame.pack(fill="x", pady=(8, 0))

        self.search_entry = tk.Entry(
            entry_frame, font=("Segoe UI", 12),
            bg="#F5F5F7", fg=self.C["text"],
            relief="flat", bd=0
        )
        self.search_entry.pack(fill="x", ipady=4)
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter())

        # List container
        container = tk.Frame(self, bg=self.C["bg"])
        container.pack(fill="both", expand=True, padx=20, pady=(12, 20))

        self.canvas = tk.Canvas(container, bg=self.C["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable = tk.Frame(self.canvas, bg=self.C["bg"])

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

        for date_str in sorted(groups.keys()):
            date_tasks = groups[date_str]
            d = datetime.strptime(date_str, "%Y-%m-%d")
            label = d.strftime("%A, %d/%m").capitalize()
            if date_str == today_str():
                label = "Hoje"
            elif date_str == (now + timedelta(days=1)).strftime("%Y-%m-%d"):
                label = "Amanhã"

            group_frame = tk.Frame(self.scrollable, bg=self.C["bg"])
            group_frame.pack(fill="x", pady=(4, 0))

            tk.Label(
                group_frame, text=label,
                font=("Segoe UI", 14, "bold"),
                bg=self.C["bg"], fg=self.C["text"]
            ).pack(anchor="w", pady=(12, 4))

            for t in date_tasks:
                self._create_task_card(t)

        if no_date:
            group_frame = tk.Frame(self.scrollable, bg=self.C["bg"])
            group_frame.pack(fill="x", pady=(4, 0))

            tk.Label(
                group_frame, text="Sem data",
                font=("Segoe UI", 14, "bold"),
                bg=self.C["bg"], fg=self.C["text_sec"]
            ).pack(anchor="w", pady=(12, 4))
            for t in no_date:
                self._create_task_card(t)

        if not groups and not no_date:
            empty = tk.Frame(
                self.scrollable, bg=self.C["surface"], padx=28, pady=32,
                highlightthickness=1, highlightbackground=self.C["border"]
            )
            empty.pack(fill="x", pady=20)
            tk.Label(
                empty, text="Nenhuma tarefa encontrada",
                font=("Segoe UI", 13), bg=self.C["surface"], fg=self.C["text_sec"]
            ).pack()

    def _create_task_card(self, task):
        is_completed = task.get("completed", 0)
        prio = get_priority_info(task.get("priority", 1))

        card = tk.Frame(
            self.scrollable, bg=self.C["surface"], padx=16, pady=12,
            highlightthickness=1, highlightbackground=self.C["border"]
        )
        card.pack(fill="x", pady=2)

        # Priority bar
        prio_bar = tk.Frame(card, bg=prio["color"], width=3)
        prio_bar.pack(side="left", fill="y")
        prio_bar.pack_propagate(False)

        # Checkbox
        chk_frame = tk.Frame(card, bg=self.C["surface"])
        chk_frame.pack(side="left", padx=(10, 8))

        chk_text = "✓" if is_completed else "○"
        chk_color = "#34C759" if is_completed else "#C7C7CC"
        chk = tk.Label(
            chk_frame, text=chk_text,
            font=("Segoe UI", 18), bg=self.C["surface"], fg=chk_color,
            cursor="hand2"
        )
        chk.pack()

        # Content
        content = tk.Frame(card, bg=self.C["surface"])
        content.pack(side="left", fill="x", expand=True)

        title_fg = self.C["text_sec"] if is_completed else self.C["text"]
        tk.Label(
            content, text=task["title"],
            font=("Segoe UI", 13, "bold" if not is_completed else "italic"),
            bg=self.C["surface"], fg=title_fg, anchor="w"
        ).pack(fill="x")

        # Meta row
        meta = tk.Frame(content, bg=self.C["surface"])
        meta.pack(anchor="w", pady=(4, 0))

        if task.get("task_time"):
            tk.Label(
                meta, text=format_time(task["task_time"]),
                font=("Segoe UI", 11), bg=self.C["surface"], fg=self.C["text_sec"]
            ).pack(side="left", padx=(0, 8))

        # Priority badge
        prio_badge = tk.Frame(meta, bg=prio["light"], padx=6, pady=1)
        prio_badge.pack(side="left", padx=(0, 4))
        tk.Label(
            prio_badge, text=prio["label"],
            font=("Segoe UI", 9, "bold"),
            bg=prio["light"], fg=prio["color"]
        ).pack()

        if task.get("project"):
            proj_badge = tk.Frame(meta, bg="#E8F0FE", padx=6, pady=1)
            proj_badge.pack(side="left", padx=(0, 4))
            tk.Label(
                proj_badge, text=task["project"],
                font=("Segoe UI", 9), bg="#E8F0FE", fg="#007AFF"
            ).pack()

        if task.get("repeat_type"):
            tk.Label(
                meta, text="↻", font=("Segoe UI", 12),
                bg=self.C["surface"], fg="#007AFF"
            ).pack(side="left", padx=(2, 0))

        # Subtask summary
        subtasks = task.get("subtasks", [])
        if subtasks:
            st_done = sum(1 for s in subtasks if s["completed"])
            tk.Label(
                content, text=f"  {st_done}/{len(subtasks)} subtarefas",
                font=("Segoe UI", 10), bg=self.C["surface"], fg=self.C["text_sec"]
            ).pack(anchor="w")

        task_id = task["id"]
        chk.bind("<Button-1>", lambda e: self._toggle(task_id))
        card.bind("<Button-1>", lambda e: self.app.show_task_detail(task_id))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e: self.app.show_task_detail(task_id))

    def _toggle(self, task_id):
        toggle_completed(task_id)
        self.app.refresh_all()
