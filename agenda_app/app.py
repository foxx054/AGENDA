import tkinter as tk
from tkinter import ttk
from database import init_db, get_all_events
from calendar_widget import CalendarWidget
from event_list import EventListView
from event_dialogs import EventFormDialog, EventDetailDialog
from notifications import NotificationManager


class AgendaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minha Agenda Pessoal")
        self.geometry("900x700")
        self.minsize(700, 500)
        self.events = []

        init_db()
        self._load_events()
        self._build_ui()
        self._setup_notifications()

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 450
        y = (self.winfo_screenheight() // 2) - 350
        self.geometry(f"+{x}+{y}")

    def _load_events(self):
        self.events = get_all_events()

    def _build_ui(self):
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: Calendar
        self.calendar_tab = tk.Frame(self.notebook, bg="#F8F9FA")
        self.notebook.add(self.calendar_tab, text="  Calendário  ")

        self.calendar = CalendarWidget(self.calendar_tab, self)
        self.calendar.pack(fill="both", expand=True)

        # Tab 2: List
        self.list_tab = tk.Frame(self.notebook, bg="#F8F9FA")
        self.notebook.add(self.list_tab, text="  Compromissos  ")

        self.event_list = EventListView(self.list_tab, self)
        self.event_list.pack(fill="both", expand=True)

        # FAB-like button (footer)
        footer = tk.Frame(self, bg="white", highlightthickness=0)
        footer.pack(fill="x", side="bottom")

        tk.Button(
            footer, text="+ Novo Evento",
            font=("Segoe UI", 12, "bold"),
            bg="#4A90D9", fg="white",
            relief="solid", bd=0,
            padx=20, pady=10,
            command=self._new_event
        ).pack(side="right", padx=16, pady=8)

    def _setup_notifications(self):
        self.notif_mgr = NotificationManager(self)
        self.notif_mgr.start()

    def _new_event(self):
        selected = self.calendar.get_selected_date()
        EventFormDialog(self, self, selected_date=selected)

    def show_event_detail(self, event_id):
        EventDetailDialog(self, self, event_id)

    def refresh_all(self):
        self._load_events()
        self.calendar.refresh()
        self.event_list.refresh()
