import tkinter as tk
from database import init_db, get_all_tasks
from dashboard import Dashboard
from calendar_widget import CalendarWidget
from task_list import TaskListView
from task_form import TaskFormDialog
from notifications import NotificationManager


SIDEBAR_ITEMS = [
    ("hoje",     "📅", "Hoje"),
    ("semana",   "📋", "Próximos 7 dias"),
    ("mes",      "🗓️", "Calendário"),
    ("todas",    "📂", "Todas"),
    ("importante", "🔴", "Importante"),
]

SIDEBAR_WIDTH = 220
COLORS = {
    "sidebar_bg": "#1C1C1E",
    "sidebar_hover": "#2C2C2E",
    "sidebar_active": "#2C2C2E",
    "sidebar_text": "#8E8E93",
    "sidebar_text_active": "#FFFFFF",
    "accent": "#007AFF",
    "bg": "#F5F5F7",
    "surface": "#FFFFFF",
    "text": "#1C1C1E",
    "text_sec": "#8E8E93",
    "border": "#E5E5EA",
}


class AgendaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minhas Tarefas")
        self.geometry("1000x700")
        self.minsize(800, 500)
        self.configure(bg=COLORS["bg"])
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
        self.sidebar = tk.Frame(self, bg=COLORS["sidebar_bg"], width=SIDEBAR_WIDTH)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.sidebar_btns = []

        # App title
        title_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        title_frame.pack(fill="x", pady=(24, 32))

        tk.Label(
            title_frame, text="Minhas\nTarefas",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["sidebar_bg"], fg="white", justify="left"
        ).pack(anchor="w", padx=20)

        # Separator
        sep = tk.Frame(self.sidebar, bg="#38383A", height=1)
        sep.pack(fill="x", padx=16, pady=(0, 8))

        # Nav items
        self.nav_var = tk.StringVar(value="hoje")
        for item_id, icon, label in SIDEBAR_ITEMS:
            btn_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"], cursor="hand2")
            btn_frame.pack(fill="x", padx=8, pady=1)

            indicator = tk.Frame(btn_frame, bg=COLORS["accent"], width=3)
            indicator.pack(side="left", fill="y")

            icon_lbl = tk.Label(
                btn_frame, text=icon,
                font=("Segoe UI", 13), bg=COLORS["sidebar_bg"],
                fg=COLORS["sidebar_text"]
            )
            icon_lbl.pack(side="left", padx=(12, 8), pady=10)

            text_lbl = tk.Label(
                btn_frame, text=label,
                font=("Segoe UI", 12), bg=COLORS["sidebar_bg"],
                fg=COLORS["sidebar_text"], anchor="w"
            )
            text_lbl.pack(side="left", fill="x", expand=True, pady=10)

            def make_handler(i=item_id, fr=btn_frame, ind=indicator, il=icon_lbl, tl=text_lbl):
                for stored_id, stored_ind, stored_il, stored_tl in self.sidebar_btns:
                    bg = COLORS["sidebar_bg"]
                    stored_ind.configure(bg=bg)
                    stored_il.configure(fg=COLORS["sidebar_text"])
                    stored_tl.configure(fg=COLORS["sidebar_text"])
                ind.configure(bg=COLORS["accent"])
                il.configure(fg="white")
                tl.configure(fg="white")
                self._switch_view(i)

            btn_frame.bind("<Button-1>", lambda e, h=make_handler: h())
            indicator.bind("<Button-1>", lambda e, h=make_handler: h())
            icon_lbl.bind("<Button-1>", lambda e, h=make_handler: h())
            text_lbl.bind("<Button-1>", lambda e, h=make_handler: h())

            self.sidebar_btns.append((item_id, indicator, icon_lbl, text_lbl))

        # Spacer
        tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"]).pack(expand=True)

        # New task button
        btn_container = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        btn_container.pack(fill="x", padx=12, pady=(0, 12))

        tk.Button(
            btn_container, text="+ Nova Tarefa",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["accent"], fg="white",
            activebackground="#005BB5",
            relief="flat", bd=0, padx=16, pady=10,
            cursor="hand2",
            command=self._new_task
        ).pack(fill="x")

        tk.Button(
            btn_container, text="🔔 Testar Notificação",
            font=("Segoe UI", 10),
            bg="#2C2C2E", fg="#8E8E93",
            activebackground="#3D3D3F", activeforeground="white",
            relief="flat", bd=0, padx=16, pady=8,
            cursor="hand2",
            command=self._test_notification
        ).pack(fill="x", pady=(6, 0))

        # Main content
        self.content = tk.Frame(self, bg=COLORS["bg"])
        self.content.pack(side="left", fill="both", expand=True)

        self.views = {}
        self._current_view = None
        self.views["hoje"] = Dashboard(self.content, self, COLORS)
        self.views["semana"] = TaskListView(self.content, self, COLORS, mode="week")
        self.views["mes"] = CalendarWidget(self.content, self, COLORS)
        self.views["todas"] = TaskListView(self.content, self, COLORS, mode="all")
        self.views["importante"] = TaskListView(self.content, self, COLORS, mode="important")

        self._switch_view("hoje")

    def _switch_view(self, view_id):
        if self._current_view:
            self._current_view.pack_forget()
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
            self.notif_mgr._show_notification(self.tasks[0])
        else:
            from tkinter import messagebox
            messagebox.showinfo("Aviso", "Crie uma tarefa primeiro.")

    def show_task_detail(self, task_id):
        from task_detail import TaskDetailDialog
        TaskDetailDialog(self, self, task_id, COLORS)

    def _setup_notifications(self):
        self.notif_mgr = NotificationManager(self)
        self.notif_mgr.start()

    def refresh_all(self):
        self._load_tasks()
        if self._current_view:
            self._current_view.refresh()
