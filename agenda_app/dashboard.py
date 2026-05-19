import tkinter as tk
from datetime import datetime
from utils import (
    MONTHS, WEEKDAYS, PRIORITIES, today_str,
    format_time, get_priority_info
)
from database import get_today_tasks, get_overdue_tasks, toggle_completed


class Dashboard(tk.Frame):
    def __init__(self, parent, app, colors):
        super().__init__(parent, bg=colors["bg"])
        self.app = app
        self.C = colors
        self._build_ui()

    def _build_ui(self):
        self.canvas = tk.Canvas(self, bg=self.C["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
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
        for w in self.scrollable.winfo_children():
            w.destroy()

        now = datetime.now()
        weekday = WEEKDAYS[now.weekday()]
        month = MONTHS[now.month - 1]

        # Header
        header = tk.Frame(self.scrollable, bg=self.C["surface"], padx=28, pady=24)
        header.pack(fill="x")

        tk.Label(
            header, text="Bom dia!",
            font=("Segoe UI", 26, "bold"), bg=self.C["surface"], fg=self.C["text"]
        ).pack(anchor="w")

        tk.Label(
            header, text=f"{weekday}, {now.day} de {month} de {now.year}",
            font=("Segoe UI", 13), bg=self.C["surface"], fg=self.C["text_sec"]
        ).pack(anchor="w")

        # Summary row
        today_tasks = get_today_tasks()
        overdue = get_overdue_tasks()
        pending = len(today_tasks)

        summary = tk.Frame(self.scrollable, bg=self.C["surface"], padx=24)
        summary.pack(fill="x", pady=(0, 32))

        summary_row = tk.Frame(summary, bg=self.C["surface"])
        summary_row.pack()

        cards_data = [
            ("Pendentes", str(pending), "#007AFF", "📋"),
            ("Atrasadas", str(len(overdue)), "#FF9500", "⚠️"),
        ]
        for label, count, color, icon in cards_data:
            card = tk.Frame(
                summary_row, bg="white", padx=20, pady=12,
                highlightthickness=1, highlightbackground=self.C["border"]
            )
            card.pack(side="left", padx=(0, 10))

            tk.Label(
                card, text=icon, font=("Segoe UI", 16),
                bg="white", fg=color
            ).pack(anchor="w")

            tk.Label(
                card, text=count, font=("Segoe UI", 28, "bold"),
                bg="white", fg=color
            ).pack(anchor="w")

            tk.Label(
                card, text=label, font=("Segoe UI", 11),
                bg="white", fg=self.C["text_sec"]
            ).pack(anchor="w")

        # Overdue warning
        if overdue:
            warn = tk.Frame(self.scrollable, bg="#FFF3E0", padx=20, pady=10)
            warn.pack(fill="x", padx=20, pady=(0, 12))

            tk.Label(
                warn, text=f"⚠️  {len(overdue)} tarefa(s) atrasada(s)!",
                font=("Segoe UI", 12, "bold"),
                bg="#FFF3E0", fg="#FF9500"
            ).pack()

        # Today's tasks section
        section = tk.Frame(self.scrollable, bg=self.C["bg"], padx=20)
        section.pack(fill="x")

        section_header = tk.Frame(section, bg=self.C["bg"])
        section_header.pack(fill="x", pady=(0, 8))

        tk.Label(
            section_header, text="Hoje",
            font=("Segoe UI", 18, "bold"), bg=self.C["bg"], fg=self.C["text"]
        ).pack(side="left")

        tk.Label(
            section_header, text=f"{pending} tarefa(s)",
            font=("Segoe UI", 12), bg=self.C["bg"], fg=self.C["text_sec"]
        ).pack(side="left", padx=(8, 0))

        all_today = get_today_tasks()
        if not all_today:
            empty_frame = tk.Frame(section, bg=self.C["surface"], padx=28, pady=32,
                                   highlightthickness=1, highlightbackground=self.C["border"])
            empty_frame.pack(fill="x")
            tk.Label(
                empty_frame, text="Nenhuma tarefa para hoje",
                font=("Segoe UI", 13), bg=self.C["surface"], fg=self.C["text_sec"]
            ).pack()
            tk.Label(
                empty_frame, text="Aproveite o dia! 🎉",
                font=("Segoe UI", 11), bg=self.C["surface"], fg=self.C["text_sec"]
            ).pack(pady=(4, 0))
        else:
            for task in all_today:
                self._create_task_card(section, task)

        # New task button
        btn_frame = tk.Frame(self.scrollable, bg=self.C["bg"], padx=20)
        btn_frame.pack(fill="x", pady=(16, 24))

        tk.Button(
            btn_frame, text="+ Nova Tarefa",
            font=("Segoe UI", 13, "bold"),
            bg=self.C["accent"], fg="white",
            activebackground="#005BB5",
            relief="flat", bd=0, padx=20, pady=12,
            cursor="hand2",
            command=lambda: self.app._new_task()
        ).pack(fill="x")

    def _create_task_card(self, parent, task):
        is_completed = task.get("completed", 0)
        prio = get_priority_info(task.get("priority", 1))

        card = tk.Frame(
            parent, bg=self.C["surface"], padx=16, pady=12,
            highlightthickness=1, highlightbackground=self.C["border"]
        )
        card.pack(fill="x", pady=3)

        # Left: priority indicator
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
