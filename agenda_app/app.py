import tkinter as tk
from database import init_db, get_all_tasks
from dashboard import Dashboard
from calendar_widget import CalendarWidget
from task_list import TaskListView
from task_form import TaskFormDialog
from notifications import NotificationManager


SIDEBAR_ITEMS = [
    ("hoje", "📅 Hoje"),
    ("semana", "📋 Próximos 7 dias"),
    ("mes", "🗓️ Calendário"),
    ("todas", "📂 Todas"),
    ("importante", "🔴 Importante"),
]

SIDEBAR_WIDTH = 200


class AgendaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minhas Tarefas")
        self.geometry("1000x700")
        self.minsize(800, 500)
        self.tasks = []

        init_db()
        self._load_tasks()
        self._build_ui()
        self._setup_notifications()

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 500
        y = (self.winfo_screenheight() // 2) - 350
        self.geometry(f"+{x}+{y}")

    def _load_tasks(self):
        self.tasks = get_all_tasks()

    def _build_ui(self):
        self.sidebar = tk.Frame(self, bg="#1A1A2E", width=SIDEBAR_WIDTH)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # App title in sidebar
        tk.Label(
            self.sidebar, text="Minhas Tarefas",
            font=("Segoe UI", 16, "bold"),
            bg="#1A1A2E", fg="white", pady=20
        ).pack(fill="x")

        # Nav items
        self.nav_var = tk.StringVar(value="hoje")
        for item_id, label in SIDEBAR_ITEMS:
            btn = tk.Button(
                self.sidebar, text=label,
                font=("Segoe UI", 12),
                bg="#1A1A2E", fg="#9CA3AF",
                activebackground="#2D2D4E", activeforeground="white",
                bd=0, anchor="w", padx=20, pady=10,
                command=lambda i=item_id: self._switch_view(i)
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#2D2D4E"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#1A1A2E"))

        # New task button at bottom of sidebar
        tk.Frame(self.sidebar, bg="#1A1A2E").pack(expand=True)

        tk.Button(
            self.sidebar, text="+ Nova Tarefa",
            font=("Segoe UI", 12, "bold"),
            bg="#007AFF", fg="white",
            activebackground="#005BB5",
            bd=0, padx=16, pady=10,
            command=self._new_task
        ).pack(fill="x", padx=12, pady=(0, 8))

        tk.Button(
            self.sidebar, text="🔔 Testar Notificação",
            font=("Segoe UI", 10),
            bg="#2D2D4E", fg="#9CA3AF",
            activebackground="#3D3D5E", activeforeground="white",
            bd=0, padx=16, pady=8,
            command=self._test_notification
        ).pack(fill="x", padx=12, pady=(0, 16))

        # Main content area
        self.content = tk.Frame(self, bg="#FAFAFA")
        self.content.pack(side="left", fill="both", expand=True)

        self.views = {}
        self._current_view = None

        # Pre-create all views
        self.views["hoje"] = Dashboard(self.content, self)
        self.views["semana"] = TaskListView(self.content, self, mode="week")
        self.views["mes"] = CalendarWidget(self.content, self)
        self.views["todas"] = TaskListView(self.content, self, mode="all")
        self.views["importante"] = TaskListView(self.content, self, mode="important")

        self._switch_view("hoje")

    def _switch_view(self, view_id):
        if self._current_view:
            self._current_view.pack_forget()

        # Update sidebar highlight
        for i, (item_id, _) in enumerate(SIDEBAR_ITEMS):
            btn = self.sidebar.winfo_children()[i + 1]  # skip title label
            if item_id == view_id:
                btn.configure(bg="#2D2D4E", fg="white")
            else:
                btn.configure(bg="#1A1A2E", fg="#9CA3AF")

        self._current_view = self.views[view_id]
        self._current_view.pack(fill="both", expand=True)
        self._current_view.refresh()

    def _new_task(self):
        TaskFormDialog(self, self)
        self.notif_mgr.check_now()

    def _test_notification(self):
        if self.tasks:
            for t in self.tasks:
                if t.get("task_time") and not t.get("completed"):
                    self.notif_mgr._show_notification(t)
                    return
            # Fallback: show first task
            self.notif_mgr._show_notification(self.tasks[0])
        else:
            from tkinter import messagebox
            messagebox.showinfo("Aviso", "Crie uma tarefa primeiro para testar.")

    def show_task_detail(self, task_id):
        from task_detail import TaskDetailDialog
        TaskDetailDialog(self, self, task_id)

    def _setup_notifications(self):
        self.notif_mgr = NotificationManager(self)
        self.notif_mgr.start()

    def refresh_all(self):
        self._load_tasks()
        if self._current_view:
            self._current_view.refresh()
