import tkinter as tk
from tkinter import messagebox
from database import get_task_by_id, delete_task, toggle_completed, add_subtask, toggle_subtask
from utils import PRIORITIES, REMINDER_OPTIONS, REPEAT_OPTIONS, format_time, LIGHT_GREEN


class TaskDetailDialog(tk.Toplevel):
    def __init__(self, parent, app, task_id):
        super().__init__(parent)
        self.app = app
        self.task_id = task_id

        self.title("Detalhes da Tarefa")
        self.geometry("480x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._load_and_show()

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 240
        y = (self.winfo_screenheight() // 2) - 250
        self.geometry(f"+{x}+{y}")

    def _load_and_show(self):
        task = get_task_by_id(self.task_id)
        if not task:
            messagebox.showerror("Erro", "Tarefa não encontrada.")
            self.destroy()
            return

        prio = PRIORITIES[task.get("priority", 1)]

        main = tk.Frame(self, bg=prio["color"])
        main.pack(fill="both", expand=True)

        content = tk.Frame(main, bg="white", padx=20, pady=20)
        content.pack(fill="both", expand=True, padx=2, pady=2)

        # Header with checkbox + title
        hdr = tk.Frame(content, bg="white")
        hdr.pack(fill="x")

        chk_text = "✓" if task.get("completed") else "○"
        chk = tk.Label(
            hdr, text=chk_text,
            font=("Segoe UI", 20), bg="white",
            fg="#34C759" if task.get("completed") else "#D1D5DB",
            cursor="hand2"
        )
        chk.pack(side="left", padx=(0, 8))
        chk.bind("<Button-1>", lambda e: self._toggle())

        tk.Label(
            hdr, text=task["title"],
            font=("Segoe UI", 18, "bold"), bg="white", fg="#1A1A2E"
        ).pack(side="left", fill="x", expand=True)

        if task.get("completed"):
            tk.Label(
                hdr, text="Finalizado", font=("Segoe UI", 10, "bold"),
                bg=LIGHT_GREEN, fg="#34C759", padx=8, pady=2
            ).pack(side="right")

        # Priority badge
        tk.Label(
            content, text=f"{prio['icon']} {prio['label']}",
            font=("Segoe UI", 10, "bold"),
            bg=prio["light"], fg=prio["color"],
            padx=8, pady=2
        ).pack(anchor="w", pady=(8, 0))

        # Info section
        info = tk.Frame(content, bg="white")
        info.pack(fill="x", pady=(12, 0))

        if task.get("task_date"):
            tk.Label(info, text="DATA", font=("Segoe UI", 9, "bold"),
                     bg="white", fg="#6B7280").pack(anchor="w")
            date_str = task["task_date"]
            if task.get("task_time"):
                date_str += f" às {format_time(task['task_time'])}"
            tk.Label(info, text=date_str, font=("Segoe UI", 12),
                     bg="white", fg="#1A1A2E").pack(anchor="w", pady=(0, 8))

        # Reminder
        rem_val = task.get("reminder")
        if rem_val is not None:
            rem_label = "Sem lembrete"
            for l, v in REMINDER_OPTIONS:
                if v == rem_val:
                    rem_label = l
                    break
            tk.Label(info, text="LEMBRETE", font=("Segoe UI", 9, "bold"),
                     bg="white", fg="#6B7280").pack(anchor="w")
            tk.Label(info, text=rem_label, font=("Segoe UI", 12),
                     bg="white", fg="#1A1A2E").pack(anchor="w", pady=(0, 8))

        # Project
        if task.get("project"):
            tk.Label(info, text="PROJETO", font=("Segoe UI", 9, "bold"),
                     bg="white", fg="#6B7280").pack(anchor="w")
            tk.Label(info, text=task["project"], font=("Segoe UI", 12),
                     bg="white", fg="#007AFF").pack(anchor="w", pady=(0, 8))

        # Repeat
        repeat_type = task.get("repeat_type", "")
        if repeat_type:
            repeat_label = next((l for l, v in REPEAT_OPTIONS if v == repeat_type), repeat_type)
            if repeat_type == "custom":
                interval = task.get("repeat_interval", 1)
                repeat_label += f" ({interval} dias)"
            tk.Label(info, text="REPETIR", font=("Segoe UI", 9, "bold"),
                     bg="white", fg="#6B7280").pack(anchor="w")
            tk.Label(info, text=repeat_label, font=("Segoe UI", 12),
                     bg="white", fg="#1A1A2E").pack(anchor="w", pady=(0, 8))

        # Description
        if task.get("description"):
            tk.Label(info, text="DESCRIÇÃO", font=("Segoe UI", 9, "bold"),
                     bg="white", fg="#6B7280").pack(anchor="w")
            tk.Label(info, text=task["description"], font=("Segoe UI", 11),
                     bg="white", fg="#4B5563", wraplength=400,
                     justify="left").pack(anchor="w", pady=(0, 8))

        # Subtasks
        subtasks = task.get("subtasks", [])
        st_frame = tk.Frame(content, bg="white")
        st_frame.pack(fill="x", pady=(8, 0))

        tk.Label(st_frame, text="SUBTAEFAS", font=("Segoe UI", 9, "bold"),
                 bg="white", fg="#6B7280").pack(anchor="w")

        for st in subtasks:
            self._create_subtask_row(st_frame, st)

        # Add subtask input
        add_st = tk.Frame(content, bg="white")
        add_st.pack(fill="x", pady=(4, 0))
        self.st_entry = tk.Entry(add_st, font=("Segoe UI", 10),
                                 relief="solid", bd=1)
        self.st_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Button(
            add_st, text="+", font=("Segoe UI", 11, "bold"),
            bg="#007AFF", fg="white", bd=0, padx=10,
            command=lambda: self._add_subtask(task["id"])
        ).pack(side="right")

        # Buttons
        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(fill="x", pady=(16, 0))

        tk.Button(
            btn_frame, text="Excluir", font=("Segoe UI", 11),
            bg="white", fg="#FF3B30",
            relief="solid", bd=1, padx=14, pady=4,
            command=self._delete
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_frame, text="Editar", font=("Segoe UI", 11, "bold"),
            bg="#007AFF", fg="white",
            relief="solid", bd=0, padx=14, pady=4,
            command=self._edit
        ).pack(side="left")

        tk.Button(
            btn_frame, text="Fechar", font=("Segoe UI", 11),
            bg="white", fg="#6B7280",
            relief="solid", bd=1, padx=14, pady=4,
            command=self.destroy
        ).pack(side="right")

    def _create_subtask_row(self, parent, st):
        row = tk.Frame(parent, bg="white")
        row.pack(fill="x", pady=1)

        chk = tk.Label(
            row, text="✓" if st["completed"] else "○",
            font=("Segoe UI", 12), bg="white",
            fg="#34C759" if st["completed"] else "#D1D5DB",
            cursor="hand2"
        )
        chk.pack(side="left", padx=(0, 4))
        chk.bind("<Button-1>", lambda e, sid=st["id"]: self._toggle_sub(sid))

        fg = "#9CA3AF" if st["completed"] else "#1A1A2E"
        tk.Label(
            row, text=st["title"], font=("Segoe UI", 11),
            bg="white", fg=fg
        ).pack(side="left")

    def _toggle(self):
        toggle_completed(self.task_id)
        self.app.refresh_all()
        self.destroy()

    def _toggle_sub(self, st_id):
        toggle_subtask(st_id)
        self.app.refresh_all()
        self.destroy()

    def _add_subtask(self, task_id):
        title = self.st_entry.get().strip()
        if title:
            add_subtask(task_id, title)
            self.app.refresh_all()
            self.destroy()

    def _edit(self):
        self.destroy()
        from task_form import TaskFormDialog
        task = get_task_by_id(self.task_id)
        if task:
            TaskFormDialog(self.app, self.app, task=task)

    def _delete(self):
        task = get_task_by_id(self.task_id)
        if not task:
            return
        if messagebox.askyesno("Excluir", f'Excluir "{task["title"]}"?'):
            delete_task(self.task_id)
            self.app.refresh_all()
            self.destroy()
