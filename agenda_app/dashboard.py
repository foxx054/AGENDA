import tkinter as tk
from datetime import datetime
from utils import (
    MONTHS, WEEKDAYS, PRIORITIES, today_str,
    format_time, get_priority_info,
    LIGHT_RED, LIGHT_ORANGE
)
from database import get_today_tasks, get_overdue_tasks, toggle_completed


class Dashboard(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#FAFAFA")
        self.app = app
        self._build_ui()

    def _build_ui(self):
        self.canvas = tk.Canvas(self, bg="#FAFAFA", highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
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
        for w in self.scrollable.winfo_children():
            w.destroy()

        now = datetime.now()
        weekday = WEEKDAYS[now.weekday()]
        month = MONTHS[now.month - 1]

        # Header
        header = tk.Frame(self.scrollable, bg="white", padx=24, pady=20)
        header.pack(fill="x")

        tk.Label(
            header, text=f"Bom dia!",
            font=("Segoe UI", 24, "bold"), bg="white", fg="#1A1A2E"
        ).pack(anchor="w")

        tk.Label(
            header, text=f"{weekday}, {now.day} de {month} de {now.year}",
            font=("Segoe UI", 13), bg="white", fg="#6B7280"
        ).pack(anchor="w")

        # Summary
        today_tasks = get_today_tasks()
        overdue = get_overdue_tasks()
        pending = len(today_tasks)

        summary = tk.Frame(self.scrollable, bg="white", padx=24, pady=12)
        summary.pack(fill="x", pady=(0, 8))

        summary_row = tk.Frame(summary, bg="white")
        summary_row.pack()

        for label, count, color, light in [
            ("Pendentes", pending, "#FF3B30", LIGHT_RED),
            ("Atrasadas", len(overdue), "#FF9500", LIGHT_ORANGE),
        ]:
            card = tk.Frame(summary_row, bg=light, padx=16, pady=10, highlightthickness=0)
            card.pack(side="left", padx=(0, 12))

            tk.Label(
                card, text=str(count), font=("Segoe UI", 22, "bold"),
                bg=light, fg=color
            ).pack()
            tk.Label(
                card, text=label, font=("Segoe UI", 10),
                bg=light, fg=color
            ).pack()

        # Overdue warning
        if overdue:
            warn = tk.Frame(self.scrollable, bg="#FFF3E0", padx=16, pady=8)
            warn.pack(fill="x", padx=16, pady=(0, 8))
            tk.Label(
                warn, text=f"⚠ {len(overdue)} tarefa(s) atrasada(s)!",
                font=("Segoe UI", 11, "bold"),
                bg="#FFF3E0", fg="#FF9500"
            ).pack()

        # Today's tasks
        section = tk.Frame(self.scrollable, bg="#FAFAFA", padx=16)
        section.pack(fill="x", pady=(8, 0))

        tk.Label(
            section, text="Hoje", font=("Segoe UI", 16, "bold"),
            bg="#FAFAFA", fg="#1A1A2E"
        ).pack(anchor="w", pady=(0, 8))

        all_today = get_today_tasks()
        if not all_today:
            tk.Label(
                section, text="Nenhuma tarefa para hoje. Aproveite o dia! 🎉",
                font=("Segoe UI", 12), bg="#FAFAFA", fg="#9CA3AF"
            ).pack(pady=20)
        else:
            for task in all_today:
                self._create_task_card(section, task)

        # New task quick button
        tk.Button(
            self.scrollable, text="+ Nova Tarefa",
            font=("Segoe UI", 12, "bold"),
            bg="#007AFF", fg="white",
            activebackground="#005BB5",
            bd=0, padx=16, pady=10,
            command=lambda: self.app._new_task()
        ).pack(padx=16, pady=(16, 24), fill="x")

    def _create_task_card(self, parent, task):
        is_completed = task.get("completed", 0)
        prio = get_priority_info(task.get("priority", 1))
        card_bg = "#F0FDF4" if is_completed else "white"

        card = tk.Frame(parent, bg=card_bg, padx=12, pady=8, highlightthickness=0)
        card.pack(fill="x", pady=3)

        # Priority bar
        bar = tk.Frame(card, bg=prio["color"], width=4)
        bar.pack(side="left", fill="y")
        bar.pack_propagate(False)

        # Checkbox
        chk_frame = tk.Frame(card, bg=card_bg)
        chk_frame.pack(side="left", padx=(8, 8))

        chk_text = "✓" if is_completed else "○"
        chk_color = "#34C759" if is_completed else "#D1D5DB"
        chk = tk.Label(
            chk_frame, text=chk_text,
            font=("Segoe UI", 16), bg=card_bg, fg=chk_color,
            cursor="hand2"
        )
        chk.pack()

        # Content
        content = tk.Frame(card, bg=card_bg)
        content.pack(side="left", fill="x", expand=True)

        title_fg = "#9CA3AF" if is_completed else "#1A1A2E"
        title_font = ("Segoe UI", 12, "bold") if not is_completed else ("Segoe UI", 12, "italic")
        tk.Label(
            content, text=task["title"],
            font=title_font, bg=card_bg, fg=title_fg,
            anchor="w"
        ).pack(fill="x")

        # Meta row
        meta = tk.Frame(content, bg=card_bg)
        meta.pack(fill="x")

        if task.get("task_time"):
            tk.Label(
                meta, text=format_time(task["task_time"]),
                font=("Segoe UI", 10), bg=card_bg, fg="#6B7280"
            ).pack(side="left", padx=(0, 8))

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
                font=("Segoe UI", 9, "bold"), bg=card_bg,
                fg="#34C759"
            ).pack(side="right")

        task_id = task["id"]
        chk.bind("<Button-1>", lambda e: self._toggle(task_id))
        card.bind("<Button-1>", lambda e: self.app.show_task_detail(task_id))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e: self.app.show_task_detail(task_id))

        # Subtask summary
        subtasks = task.get("subtasks", [])
        if subtasks:
            st_done = sum(1 for s in subtasks if s["completed"])
            tk.Label(
                content, text=f"  {st_done}/{len(subtasks)} subtarefas",
                font=("Segoe UI", 9), bg=card_bg, fg="#9CA3AF"
            ).pack(anchor="w")

    def _toggle(self, task_id):
        toggle_completed(task_id)
        self.app.refresh_all()
