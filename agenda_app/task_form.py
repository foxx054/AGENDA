import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from utils import PRIORITIES, REMINDER_OPTIONS, REPEAT_OPTIONS, today_str
from database import save_task, get_all_tasks


class TaskFormDialog(tk.Toplevel):
    def __init__(self, parent, app, task=None):
        super().__init__(parent)
        self.app = app
        self.task = task

        self.title("Editar Tarefa" if task else "Nova Tarefa")
        self.geometry("480x650")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_form()
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 240
        y = (self.winfo_screenheight() // 2) - 325
        self.geometry(f"+{x}+{y}")

    def _build_form(self):
        main = tk.Frame(self, padx=20, pady=20, bg="#FAFAFA")
        main.pack(fill="both", expand=True)

        # Title
        tk.Label(main, text="Título", font=("Segoe UI", 11, "bold"),
                 bg="#FAFAFA", fg="#1A1A2E").pack(anchor="w")
        self.title_entry = tk.Entry(main, font=("Segoe UI", 14),
                                    relief="solid", bd=1)
        self.title_entry.pack(fill="x", pady=(0, 12))
        if self.task:
            self.title_entry.insert(0, self.task["title"])
        else:
            self.title_entry.focus_set()

        # Date & Time
        row = tk.Frame(main, bg="#FAFAFA")
        row.pack(fill="x")

        left = tk.Frame(row, bg="#FAFAFA")
        left.pack(side="left", fill="x", expand=True, padx=(0, 6))

        tk.Label(left, text="Data", font=("Segoe UI", 10, "bold"),
                 bg="#FAFAFA", fg="#1A1A2E").pack(anchor="w")
        self.date_entry = tk.Entry(left, font=("Segoe UI", 11),
                                   relief="solid", bd=1)
        self.date_entry.pack(fill="x", pady=(0, 6))
        default_date = self.task["task_date"] if self.task and self.task.get("task_date") else today_str()
        self.date_entry.insert(0, default_date)

        right = tk.Frame(row, bg="#FAFAFA")
        right.pack(side="left", fill="x", expand=True, padx=(6, 0))

        tk.Label(right, text="Horário", font=("Segoe UI", 10, "bold"),
                 bg="#FAFAFA", fg="#1A1A2E").pack(anchor="w")
        self.time_entry = tk.Entry(right, font=("Segoe UI", 11),
                                   relief="solid", bd=1)
        self.time_entry.pack(fill="x", pady=(0, 6))
        default_time = self.task["task_time"] if self.task and self.task.get("task_time") else ""
        self.time_entry.insert(0, default_time)

        # Priority
        tk.Label(main, text="Prioridade", font=("Segoe UI", 11, "bold"),
                 bg="#FAFAFA", fg="#1A1A2E").pack(anchor="w", pady=(8, 4))
        prio_frame = tk.Frame(main, bg="#FAFAFA")
        prio_frame.pack(fill="x")

        self.priority_var = tk.IntVar(value=self.task["priority"] if self.task else 1)
        for p in PRIORITIES:
            btn = tk.Button(
                prio_frame, text=f"{p['icon']} {p['label']}",
                font=("Segoe UI", 10),
                bg="white", fg=p["color"],
                relief="solid", bd=1, padx=12, pady=4,
                command=lambda v=p["id"]: self.priority_var.set(v)
            )
            btn.pack(side="left", padx=2)

        # Reminder
        tk.Label(main, text="Lembrete", font=("Segoe UI", 11, "bold"),
                 bg="#FAFAFA", fg="#1A1A2E").pack(anchor="w", pady=(8, 4))
        rem_frame = tk.Frame(main, bg="#FAFAFA")
        rem_frame.pack(fill="x")
        self.reminder_var = tk.IntVar(
            value=self.task["reminder"] if self.task and self.task.get("reminder") is not None else -1
        )
        tk.Radiobutton(
            rem_frame, text="Sem lembrete", variable=self.reminder_var,
            value=-1, font=("Segoe UI", 10), bg="#FAFAFA", selectcolor="#E8F0FE"
        ).pack(side="left", padx=2)
        for label, val in REMINDER_OPTIONS:
            rb = tk.Radiobutton(
                rem_frame, text=label, variable=self.reminder_var,
                value=val, font=("Segoe UI", 10),
                bg="#FAFAFA", selectcolor="#E8F0FE"
            )
            rb.pack(side="left", padx=2)

        # Project
        tk.Label(main, text="Projeto", font=("Segoe UI", 11, "bold"),
                 bg="#FAFAFA", fg="#1A1A2E").pack(anchor="w", pady=(8, 4))
        self.project_entry = tk.Entry(main, font=("Segoe UI", 11),
                                      relief="solid", bd=1)
        self.project_entry.pack(fill="x", pady=(0, 12))
        if self.task and self.task.get("project"):
            self.project_entry.insert(0, self.task["project"])

        # Repeat
        tk.Label(main, text="Repetir", font=("Segoe UI", 11, "bold"),
                 bg="#FAFAFA", fg="#1A1A2E").pack(anchor="w", pady=(0, 4))
        repeat_frame = tk.Frame(main, bg="#FAFAFA")
        repeat_frame.pack(fill="x")

        default_repeat = self.task["repeat_type"] if self.task and self.task.get("repeat_type") else ""
        self.repeat_var = tk.StringVar(value=default_repeat)
        for label, val in REPEAT_OPTIONS:
            rb = tk.Radiobutton(
                repeat_frame, text=label, variable=self.repeat_var,
                value=val, font=("Segoe UI", 10),
                bg="#FAFAFA", selectcolor="#E8F0FE",
                command=self._toggle_repeat_custom
            )
            rb.pack(side="left", padx=2)

        self.custom_frame = tk.Frame(main, bg="#FAFAFA")
        tk.Label(
            self.custom_frame, text="A cada quantos dias?",
            font=("Segoe UI", 10), bg="#FAFAFA", fg="#6B7280"
        ).pack(side="left", padx=(0, 6))
        self.repeat_interval_entry = tk.Entry(
            self.custom_frame, font=("Segoe UI", 11),
            width=6, relief="solid", bd=1
        )
        self.repeat_interval_entry.pack(side="left")
        default_interval = str(self.task["repeat_interval"]) if self.task and self.task.get("repeat_interval") else "1"
        self.repeat_interval_entry.insert(0, default_interval)
        if default_repeat == "custom":
            self.custom_frame.pack(fill="x", pady=(4, 8))
        else:
            self.custom_frame.pack_forget()

        # Description
        tk.Label(main, text="Descrição", font=("Segoe UI", 11, "bold"),
                 bg="#FAFAFA", fg="#1A1A2E").pack(anchor="w", pady=(8, 4))
        self.desc_text = tk.Text(main, height=2, font=("Segoe UI", 11),
                                 relief="solid", bd=1)
        self.desc_text.pack(fill="x", pady=(0, 12))
        if self.task and self.task.get("description"):
            self.desc_text.insert("1.0", self.task["description"])

        # Buttons
        btn_frame = tk.Frame(main, bg="#FAFAFA")
        btn_frame.pack(fill="x", pady=(8, 0))

        tk.Button(
            btn_frame, text="Cancelar",
            font=("Segoe UI", 11), bg="white", fg="#6B7280",
            relief="solid", bd=1, padx=16, pady=6,
            command=self.destroy
        ).pack(side="right", padx=(6, 0))

        tk.Button(
            btn_frame, text="Salvar",
            font=("Segoe UI", 11, "bold"),
            bg="#007AFF", fg="white",
            relief="solid", bd=0, padx=16, pady=6,
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
                messagebox.showwarning("Atenção", "Intervalo personalizado deve ser um número maior que 0.")
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
