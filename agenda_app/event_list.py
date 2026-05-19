import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from utils import (
    CATEGORIES, format_date, format_time, parse_datetime, to_date_str
)
from database import get_all_events, search_events as db_search


class EventListView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#F8F9FA")
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # Search
        search_frame = tk.Frame(self, bg="white", padx=12, pady=12)
        search_frame.pack(fill="x")

        tk.Label(
            search_frame, text="Buscar compromissos...",
            font=("Segoe UI", 10), bg="white", fg="#6B7280"
        ).pack(anchor="w")

        self.search_entry = tk.Entry(
            search_frame, font=("Segoe UI", 12),
            relief="solid", bd=1
        )
        self.search_entry.pack(fill="x", pady=(4, 0))
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter())

        # Category filter
        filter_frame = tk.Frame(self, bg="#F8F9FA", padx=12, pady=6)
        filter_frame.pack(fill="x")

        self.cat_var = tk.StringVar(value="")
        tk.Radiobutton(
            filter_frame, text="Todas", variable=self.cat_var,
            value="", command=self._filter,
            font=("Segoe UI", 10), bg="#F8F9FA", selectcolor="#E8F0FE"
        ).pack(side="left", padx=2)

        for cat in CATEGORIES:
            rb = tk.Radiobutton(
                filter_frame, text=cat["label"], variable=self.cat_var,
                value=cat["id"], command=self._filter,
                font=("Segoe UI", 10), bg="#F8F9FA",
                selectcolor="#E8F0FE", fg=cat["color"]
            )
            rb.pack(side="left", padx=4)

        # Sort
        sort_frame = tk.Frame(self, bg="#F8F9FA", padx=12)
        sort_frame.pack(fill="x")

        self.sort_var = tk.StringVar(value="date")
        tk.Radiobutton(
            sort_frame, text="Data", variable=self.sort_var,
            value="date", command=self._filter,
            font=("Segoe UI", 10), bg="#F8F9FA", selectcolor="#E8F0FE"
        ).pack(side="left", padx=2)
        tk.Radiobutton(
            sort_frame, text="Título", variable=self.sort_var,
            value="title", command=self._filter,
            font=("Segoe UI", 10), bg="#F8F9FA", selectcolor="#E8F0FE"
        ).pack(side="left", padx=2)

        # List container (scrollable)
        list_container = tk.Frame(self, bg="#F8F9FA")
        list_container.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        self.canvas = tk.Canvas(list_container, bg="#F8F9FA", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#F8F9FA")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh(self):
        self._filter()

    def _filter(self):
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        query = self.search_entry.get().strip()
        category = self.cat_var.get()

        if query:
            events = db_search(query, category if category else None)
        elif category:
            events = db_search("", category)
        else:
            events = get_all_events()

        if self.sort_var.get() == "date":
            events.sort(key=lambda e: e["start_date"])
        else:
            events.sort(key=lambda e: e["title"].lower())

        if not events:
            tk.Label(
                self.scrollable_frame,
                text="Nenhum compromisso encontrado" if query else "Nenhum compromisso cadastrado",
                font=("Segoe UI", 12), bg="#F8F9FA", fg="#9CA3AF"
            ).pack(pady=40)
            return

        self.app._load_events()
        now = datetime.now()
        for ev in events:
            self._create_card(ev, now)

    def _create_card(self, ev, now):
        start = parse_datetime(ev["start_date"])
        end = parse_datetime(ev["end_date"])
        is_past = end < now

        card = tk.Frame(
            self.scrollable_frame, bg="white",
            highlightthickness=0, padx=12, pady=8
        )
        card.pack(fill="x", pady=4)

        # Color bar
        bar = tk.Frame(card, bg=ev.get("color", "#4A90D9"), width=4)
        bar.pack(side="left", fill="y")
        bar.pack_propagate(False)

        content = tk.Frame(card, bg="white")
        content.pack(side="left", fill="x", expand=True, padx=(8, 0))

        # Header row
        hdr = tk.Frame(content, bg="white")
        hdr.pack(fill="x")

        tk.Label(
            hdr, text=format_date(start),
            font=("Segoe UI", 10), bg="white", fg="#6B7280"
        ).pack(side="left")

        if is_past:
            tk.Label(
                hdr, text="Passado",
                font=("Segoe UI", 10, "italic"), bg="white", fg="#9CA3AF"
            ).pack(side="right")
        else:
            diff = (start - now).total_seconds()
            if diff < 3600:
                rel = f"Em {int(diff // 60)} min"
            elif diff < 86400:
                rel = f"Em {int(diff // 3600)}h"
            else:
                rel = f"Em {int(diff // 86400)}d"
            tk.Label(
                hdr, text=rel,
                font=("Segoe UI", 10, "bold"), bg="white", fg="#4A90D9"
            ).pack(side="right")

        tk.Label(
            content, text=ev["title"],
            font=("Segoe UI", 12, "bold"), bg="white", fg="#1A1A2E"
        ).pack(anchor="w")

        tk.Label(
            content, text=f"{format_time(start)} - {format_time(end)}",
            font=("Segoe UI", 10), bg="white", fg="#6B7280"
        ).pack(anchor="w")

        # Category badge
        for cat in CATEGORIES:
            if cat["id"] == ev.get("category"):
                badge = tk.Frame(content, bg=cat["color"] + "30")
                badge.pack(anchor="w", pady=(4, 0))
                tk.Label(
                    badge, text=cat["label"],
                    font=("Segoe UI", 9, "bold"),
                    bg=cat["color"] + "30",
                    fg=cat["color"], padx=6, pady=1
                ).pack()
                break

        ev_id = ev["id"]
        card.bind("<Button-1>", lambda e: self.app.show_event_detail(ev_id))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e: self.app.show_event_detail(ev_id))
