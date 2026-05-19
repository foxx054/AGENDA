import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from utils import PRIORITIES, REMINDER_OPTIONS, REPEAT_OPTIONS, today_str
from database import save_task


class TaskFormDialog(tk.Toplevel):
    def __init__(self, parent, app, task=None):
        super().__init__(parent)
        self.app = app
        self.task = task

        self.title("Editar Tarefa" if task else "Nova Tarefa")
        self.geometry("480x620")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_form()
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 240
        y = (self.winfo_screenheight() // 2) - 310
        self.geometry(f"+{x}+{y}")

    def _build_form(self):
        bg = "#F5F5F7"
        surface = "white"
        text = "#1C1C1E"
        text_sec = "#8E8E93"
        border = "#E5E5EA"
        accent = "#007AFF"

        main = tk.Frame(self, padx=24, pady=24, bg=bg)
        main.pack(fill="both", expand=True)

        # Title
        tk.Label(main, text="Título", font=("Segoe UI", 11, "bold"),
                 bg=bg, fg=text).pack(anchor="w")
        entry_frame = tk.Frame(main, bg=border, bd=0)
        entry_frame.pack(fill="x", pady=(0, 14))
        self.title_entry = tk.Entry(
            entry_frame, font=("Segoe UI", 14),
            bg=surface, fg=text, relief="flat", bd=0
        )
        self.title_entry.pack(fill="x", ipady=2)
        if self.task:
            self.title_entry.insert(0, self.task["title"])
        else:
            self.title_entry.focus_set()

        # Date & Time row
        row = tk.Frame(main, bg=bg)
        row.pack(fill="x")

        left = tk.Frame(row, bg=bg)
        left.pack(side="left", fill="x", expand=True, padx=(0, 6))

        tk.Label(left, text="Data", font=("Segoe UI", 10, "bold"),
                 bg=bg, fg=text).pack(anchor="w")
        df = tk.Frame(left, bg=border, bd=0)
        df.pack(fill="x", pady=(0, 10))
        self.date_entry = tk.Entry(
            df, font=("Segoe UI", 12), bg=surface, fg=text,
            relief="flat", bd=0
        )
        self.date_entry.pack(fill="x", ipady=2)
        default_date = self.task["task_date"] if self.task and self.task.get("task_date") else today_str()
        self.date_entry.insert(0, default_date)

        right = tk.Frame(row, bg=bg)
        right.pack(side="left", fill="x", expand=True, padx=(6, 0))

        tk.Label(right, text="Horário", font=("Segoe UI", 10, "bold"),
                 bg=bg, fg=text).pack(anchor="w")
        tf = tk.Frame(right, bg=border, bd=0)
        tf.pack(fill="x", pady=(0, 10))
        self.time_entry = tk.Entry(
            tf, font=("Segoe UI", 12), bg=surface, fg=text,
            relief="flat", bd=0
        )
        self.time_entry.pack(fill="x", ipady=2)
        default_time = self.task["task_time"] if self.task and self.task.get("task_time") else ""
        self.time_entry.insert(0, default_time)

        # Priority
        tk.Label(main, text="Prioridade", font=("Segoe UI", 11, "bold"),
                 bg=bg, fg=text).pack(anchor="w", pady=(6, 4))
        prio_frame = tk.Frame(main, bg=bg)
        prio_frame.pack(fill="x")
        self.priority_var = tk.IntVar(value=self.task["priority"] if self.task else 1)
        for p in PRIORITIES:
            btn = tk.Button(
                prio_frame, text=f"{p['icon']} {p['label']}",
                font=("Segoe UI", 10), bg=surface, fg=p["color"],
                relief="flat", bd=1, highlightbackground=border,
                padx=14, pady=4, cursor="hand2",
                command=lambda v=p["id"]: self.priority_var.set(v)
            )
            btn.pack(side="left", padx=2)

        # Reminder
        tk.Label(main, text="Lembrete", font=("Segoe UI", 11, "bold"),
                 bg=bg, fg=text).pack(anchor="w", pady=(6, 4))
        rem_frame = tk.Frame(main, bg=bg)
        rem_frame.pack(fill="x")
        self.reminder_var = tk.IntVar(
            value=self.task["reminder"] if self.task and self.task.get("reminder") is not None else -1
        )
        tk.Radiobutton(
            rem_frame, text="Sem", variable=self.reminder_var,
            value=-1, font=("Segoe UI", 10), bg=bg, selectcolor="#E8F0FE"
        ).pack(side="left", padx=2)
        for label, val in REMINDER_OPTIONS:
            tk.Radiobutton(
                rem_frame, text=label, variable=self.reminder_var,
                value=val, font=("Segoe UI", 10),
                bg=bg, selectcolor="#E8F0FE"
            ).pack(side="left", padx=2)

        # Project
        tk.Label(main, text="Projeto", font=("Segoe UI", 11, "bold"),
                 bg=bg, fg=text).pack(anchor="w", pady=(6, 4))
        pf = tk.Frame(main, bg=border, bd=0)
        pf.pack(fill="x", pady=(0, 10))
        self.project_entry = tk.Entry(
            pf, font=("Segoe UI", 12), bg=surface, fg=text,
            relief="flat", bd=0
        )
        self.project_entry.pack(fill="x", ipady=2)
        if self.task and self.task.get("project"):
            self.project_entry.insert(0, self.task["project"])

        # Repeat
        tk.Label(main, text="Repetir", font=("Segoe UI", 11, "bold"),
                 bg=bg, fg=text).pack(anchor="w", pady=(0, 4))
        repeat_frame = tk.Frame(main, bg=bg)
        repeat_frame.pack(fill="x")

        default_repeat = self.task["repeat_type"] if self.task and self.task.get("repeat_type") else ""
        self.repeat_var = tk.StringVar(value=default_repeat)
        for label, val in REPEAT_OPTIONS:
            tk.Radiobutton(
                repeat_frame, text=label, variable=self.repeat_var,
                value=val, font=("Segoe UI", 10),
                bg=bg, selectcolor="#E8F0FE",
                command=self._toggle_repeat_custom
            ).pack(side="left", padx=2)

        self.custom_frame = tk.Frame(main, bg=bg)
        tk.Label(
            self.custom_frame, text="A cada quantos dias?",
            font=("Segoe UI", 10), bg=bg, fg=text_sec
        ).pack(side="left", padx=(0, 6))
        cif = tk.Frame(self.custom_frame, bg=border, bd=0)
        cif.pack(side="left")
        self.repeat_interval_entry = tk.Entry(
            cif, font=("Segoe UI", 11), width=6,
            bg=surface, fg=text, relief="flat", bd=0
        )
        self.repeat_interval_entry.pack()
        default_interval = str(self.task["repeat_interval"]) if self.task and self.task.get("repeat_interval") else "1"
        self.repeat_interval_entry.insert(0, default_interval)
        if default_repeat == "custom":
            self.custom_frame.pack(fill="x", pady=(4, 8))
        else:
            self.custom_frame.pack_forget()

        # Description
        tk.Label(main, text="Descrição", font=("Segoe UI", 11, "bold"),
                 bg=bg, fg=text).pack(anchor="w", pady=(6, 4))
        desc_frame = tk.Frame(main, bg=border, bd=0)
        desc_frame.pack(fill="x", pady=(0, 12))
        self.desc_text = tk.Text(
            desc_frame, height=2, font=("Segoe UI", 11),
            bg=surface, fg=text, relief="flat", bd=0
        )
        self.desc_text.pack(fill="x")
        if self.task and self.task.get("description"):
            self.desc_text.insert("1.0", self.task["description"])

        # Buttons
        btn_frame = tk.Frame(main, bg=bg)
        btn_frame.pack(fill="x", pady=(8, 0))

        tk.Button(
            btn_frame, text="Cancelar", font=("Segoe UI", 12),
            bg="white", fg=text_sec, relief="flat", bd=1,
            highlightbackground=border, padx=20, pady=8, cursor="hand2",
            command=self.destroy
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            btn_frame, text="Salvar", font=("Segoe UI", 12, "bold"),
            bg=accent, fg="white", relief="flat", bd=0,
            padx=24, pady=8, cursor="hand2",
            command=self._save
        ).pack(side="right")

    def _toggle_repeat_custom(self):
        if self.repeat_var.get() == "custom":
            self.custom_frame.pack(fill="x", pady=(4, 8))
        else:
            self.custom_frame.pack_forget()

    def _save(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Atenção", "O título é obrigatório.")
            return

        repeat_type = self.repeat_var.get()
        repeat_interval = 0
        if repeat_type == "custom":
            try:
                repeat_interval = int(self.repeat_interval_entry.get().strip())
                if repeat_interval < 1:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Atenção", "Intervalo deve ser um número > 0.")
                return

        task_data = {
            "title": title,
            "description": self.desc_text.get("1.0", "end-1c").strip(),
            "task_date": self.date_entry.get().strip() or None,
            "task_time": self.time_entry.get().strip() or None,
            "priority": self.priority_var.get(),
            "reminder": None if self.reminder_var.get() == -1 else self.reminder_var.get(),
            "completed": 0,
            "project": self.project_entry.get().strip(),
            "tags": "",
            "repeat_type": repeat_type,
            "repeat_interval": repeat_interval,
        }
        if self.task:
            task_data["id"] = self.task["id"]
            task_data["completed"] = self.task.get("completed", 0)
            from database import get_task_by_id
            existing = get_task_by_id(self.task["id"])
            if existing:
                task_data["subtasks"] = existing.get("subtasks", [])

        save_task(task_data)
        self.app.refresh_all()
        self.destroy()
