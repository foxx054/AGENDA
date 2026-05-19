import tkinter as tk
from tkinter import messagebox
from database import get_task_by_id, delete_task, toggle_completed, add_subtask, toggle_subtask
from utils import PRIORITIES, REMINDER_OPTIONS, REPEAT_OPTIONS, format_time, LIGHT_GREEN


class TaskDetailDialog(tk.Toplevel):
    def __init__(self, parent, app, task_id, colors):
        super().__init__(parent)
        self.app = app
        self.task_id = task_id
        self.C = colors

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
        bg = self.C["bg"]
        surface = self.C["surface"]
        text = self.C["text"]
        text_sec = self.C["text_sec"]
        border = self.C["border"]

        main = tk.Frame(self, bg=bg, padx=0, pady=0)
        main.pack(fill="both", expand=True)

        # Top color bar
        tk.Frame(main, bg=prio["color"], height=4).pack(fill="x")

        content = tk.Frame(main, bg=surface, padx=24, pady=20)
        content.pack(fill="both", expand=True)

        # Header row
        hdr = tk.Frame(content, bg=surface)
        hdr.pack(fill="x")

        chk_text = "✓" if task.get("completed") else "○"
        chk_color = "#34C759" if task.get("completed") else "#C7C7CC"
        chk = tk.Label(
            hdr, text=chk_text, font=("Segoe UI", 22),
            bg=surface, fg=chk_color, cursor="hand2"
        )
        chk.pack(side="left", padx=(0, 10))
        chk.bind("<Button-1>", lambda e: self._toggle())

        tk.Label(
            hdr, text=task["title"],
            font=("Segoe UI", 18, "bold"), bg=surface, fg=text
        ).pack(side="left", fill="x", expand=True)

        if task.get("completed"):
            tk.Label(
                hdr, text="Finalizado", font=("Segoe UI", 10, "bold"),
                bg=LIGHT_GREEN, fg="#34C759", padx=8, pady=2
            ).pack(side="right")

        # Priority badge
        prio_badge = tk.Frame(content, bg=prio["light"], padx=8, pady=2)
        prio_badge.pack(anchor="w", pady=(10, 0))
        tk.Label(
            prio_badge, text=f"{prio['icon']} {prio['label']}",
            font=("Segoe UI", 10, "bold"),
            bg=prio["light"], fg=prio["color"]
        ).pack()

        # Info section
        info = tk.Frame(content, bg=surface)
        info.pack(fill="x", pady=(12, 0))

        if task.get("task_date"):
            row = tk.Frame(info, bg=surface)
            row.pack(fill="x", pady=3)
            tk.Label(row, text="📅", font=("Segoe UI", 11),
                     bg=surface).pack(side="left", padx=(0, 8))
            date_str = task["task_date"]
            if task.get("task_time"):
                date_str += f"  às  {format_time(task['task_time'])}"
            tk.Label(row, text=date_str, font=("Segoe UI", 12),
                     bg=surface, fg=text).pack(side="left")

        rem_val = task.get("reminder")
        if rem_val is not None:
            rem_label = "Sem lembrete"
            for l, v in REMINDER_OPTIONS:
                if v == rem_val:
                    rem_label = l
                    break
            row = tk.Frame(info, bg=surface)
            row.pack(fill="x", pady=3)
            tk.Label(row, text="⏰", font=("Segoe UI", 11),
                     bg=surface).pack(side="left", padx=(0, 8))
            tk.Label(row, text=rem_label, font=("Segoe UI", 12),
                     bg=surface, fg=text).pack(side="left")

        if task.get("project"):
            row = tk.Frame(info, bg=surface)
            row.pack(fill="x", pady=3)
            tk.Label(row, text="📁", font=("Segoe UI", 11),
                     bg=surface).pack(side="left", padx=(0, 8))
            tk.Label(row, text=task["project"], font=("Segoe UI", 12),
                     bg=surface, fg="#007AFF").pack(side="left")

        repeat_type = task.get("repeat_type", "")
        if repeat_type:
            repeat_label = next((l for l, v in REPEAT_OPTIONS if v == repeat_type), repeat_type)
            if repeat_type == "custom":
                interval = task.get("repeat_interval", 1)
                repeat_label += f" ({interval} dias)"
            row = tk.Frame(info, bg=surface)
            row.pack(fill="x", pady=3)
            tk.Label(row, text="↻", font=("Segoe UI", 13),
                     bg=surface).pack(side="left", padx=(0, 8))
            tk.Label(row, text=repeat_label, font=("Segoe UI", 12),
                     bg=surface, fg=text).pack(side="left")

        if task.get("description"):
            tk.Frame(info, bg=border, height=1).pack(fill="x", pady=(12, 8))
            tk.Label(info, text=task["description"], font=("Segoe UI", 11),
                     bg=surface, fg="#4B5563", wraplength=400,
                     justify="left").pack(anchor="w")

        # Subtasks
        subtasks = task.get("subtasks", [])
        if subtasks:
            tk.Frame(info, bg=border, height=1).pack(fill="x", pady=(12, 8))
            tk.Label(info, text="Subtarefas", font=("Segoe UI", 10, "bold"),
                     bg=surface, fg=text_sec).pack(anchor="w", pady=(0, 4))

            for st in subtasks:
                self._create_subtask_row(info, st)

        # Add subtask
        add_st = tk.Frame(content, bg=surface)
        add_st.pack(fill="x", pady=(10, 0))
        st_frame = tk.Frame(add_st, bg=border, bd=0)
        st_frame.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.st_entry = tk.Entry(
            st_frame, font=("Segoe UI", 11), bg=surface, fg=text,
            relief="flat", bd=0
        )
        self.st_entry.pack(fill="x")
        tk.Button(
            add_st, text="+", font=("Segoe UI", 14, "bold"),
            bg=self.C["accent"], fg="white", relief="flat", bd=0,
            padx=12, cursor="hand2",
            command=lambda: self._add_subtask(task["id"])
        ).pack(side="right")

        # Buttons
        btn_frame = tk.Frame(content, bg=surface)
        btn_frame.pack(fill="x", pady=(16, 0))

        tk.Button(
            btn_frame, text="Excluir", font=("Segoe UI", 11),
            bg="white", fg="#FF3B30", relief="flat", bd=1,
            highlightbackground=border, padx=16, pady=6, cursor="hand2",
            command=self._delete
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_frame, text="Editar", font=("Segoe UI", 11, "bold"),
            bg=self.C["accent"], fg="white", relief="flat", bd=0,
            padx=16, pady=6, cursor="hand2",
            command=self._edit
        ).pack(side="left")

        tk.Button(
            btn_frame, text="Fechar", font=("Segoe UI", 11),
            bg="white", fg=text_sec, relief="flat", bd=1,
            highlightbackground=border, padx=16, pady=6, cursor="hand2",
            command=self.destroy
        ).pack(side="right")

    def _create_subtask_row(self, parent, st):
        row = tk.Frame(parent, bg=self.C["surface"])
        row.pack(fill="x", pady=1)

        chk = tk.Label(
            row, text="✓" if st["completed"] else "○",
            font=("Segoe UI", 13), bg=self.C["surface"],
            fg="#34C759" if st["completed"] else "#C7C7CC",
            cursor="hand2"
        )
        chk.pack(side="left", padx=(0, 6))
        chk.bind("<Button-1>", lambda e, sid=st["id"]: self._toggle_sub(sid))

        fg = "#9CA3AF" if st["completed"] else self.C["text"]
        tk.Label(
            row, text=st["title"], font=("Segoe UI", 11),
            bg=self.C["surface"], fg=fg
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
