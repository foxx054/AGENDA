import calendar
import tkinter as tk
from datetime import datetime, timedelta
from utils import (
    WEEKDAYS, MONTHS, CATEGORIES, REMINDER_OPTIONS,
    format_date, format_time, to_date_str, get_week_days, parse_datetime
)
from database import get_events_by_date, save_event, delete_event, get_event_by_id
from conflict_check import check_conflict


class CalendarWidget(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#F8F9FA")
        self.app = app
        self.view_mode = tk.StringVar(value="month")
        self.current_date = datetime.now().replace(day=1)
        self.selected_date = datetime.now()

        self._build_ui()
        self._render()

    def _build_ui(self):
        mode_frame = tk.Frame(self, bg="white", highlightthickness=0)
        mode_frame.pack(fill="x")

        for mode, label in [("month", "Mês"), ("week", "Semana"), ("day", "Dia")]:
            rb = tk.Radiobutton(
                mode_frame, text=label, variable=self.view_mode,
                value=mode, command=self._render,
                font=("Segoe UI", 11), bg="white",
                selectcolor="#E8F0FE", indicatoron=0,
                padx=12, pady=6
            )
            rb.pack(side="left", padx=2, pady=4)

        self.header_frame = tk.Frame(self, bg="white", highlightthickness=0)
        self.header_frame.pack(fill="x", pady=(0, 8))

        self.header_btn_left = tk.Button(
            self.header_frame, text="<", font=("Segoe UI", 14, "bold"),
            bg="white", fg="#4A90D9", bd=0, padx=12,
            command=self._navigate_back
        )
        self.header_btn_left.pack(side="left")

        self.header_title = tk.Label(
            self.header_frame, font=("Segoe UI", 16, "bold"),
            bg="white", fg="#1A1A2E"
        )
        self.header_title.pack(side="left", expand=True, fill="x")

        self.header_btn_right = tk.Button(
            self.header_frame, text=">", font=("Segoe UI", 14, "bold"),
            bg="white", fg="#4A90D9", bd=0, padx=12,
            command=self._navigate_forward
        )
        self.header_btn_right.pack(side="right")

        self.grid_frame = tk.Frame(self, bg="#F8F9FA")
        self.grid_frame.pack(fill="both", expand=True, padx=8)

        self.events_frame = tk.Frame(self, bg="#F8F9FA")
        self.events_frame.pack(fill="both", expand=True, padx=8, pady=(8, 0))

    def _navigate_back(self):
        mode = self.view_mode.get()
        if mode == "month":
            y, m = self.current_date.year, self.current_date.month
            m -= 1
            if m < 1:
                m = 12
                y -= 1
            self.current_date = self.current_date.replace(year=y, month=m)
        elif mode == "week":
            self.current_date -= timedelta(days=7)
        else:
            self.selected_date -= timedelta(days=1)
        self._render()

    def _navigate_forward(self):
        mode = self.view_mode.get()
        if mode == "month":
            y, m = self.current_date.year, self.current_date.month
            m += 1
            if m > 12:
                m = 1
                y += 1
            self.current_date = self.current_date.replace(year=y, month=m)
        elif mode == "week":
            self.current_date += timedelta(days=7)
        else:
            self.selected_date += timedelta(days=1)
        self._render()

    def refresh(self):
        self._render()

    def _render(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        for w in self.events_frame.winfo_children():
            w.destroy()

        mode = self.view_mode.get()
        if mode == "month":
            self._render_month()
        elif mode == "week":
            self._render_week()
        else:
            self._render_day()

        self._render_events()

    def _get_month_events(self, year, month):
        events_map = {}
        self.app._load_events()
        for ev in self.app.events:
            d = to_date_str(parse_datetime(ev["start_date"]))
            if d not in events_map:
                events_map[d] = []
            events_map[d].append(ev)
        return events_map

    def _render_month(self):
        year = self.current_date.year
        month = self.current_date.month
        self.header_title.config(text=f"{MONTHS[month-1]} {year}")

        hdr = tk.Frame(self.grid_frame, bg="white")
        hdr.pack(fill="x")
        for day in WEEKDAYS:
            tk.Label(
                hdr, text=day, font=("Segoe UI", 9, "bold"),
                bg="white", fg="#6B7280", width=10
            ).pack(side="left", expand=True)

        cal = calendar.Calendar()
        days = list(cal.itermonthdates(year, month))
        month_events = self._get_month_events(year, month)

        row_frame = tk.Frame(self.grid_frame, bg="#F8F9FA")
        row_frame.pack(fill="x")

        today = datetime.now()
        for i, d in enumerate(days):
            if i > 0 and i % 7 == 0:
                row_frame = tk.Frame(self.grid_frame, bg="#F8F9FA")
                row_frame.pack(fill="x")

            d_str = to_date_str(d)
            has_events = d_str in month_events
            is_selected = d == self.selected_date.date()
            is_today = d == today.date()
            is_current_month = d.month == month

            bg_color = "#4A90D9" if is_selected else ("#E8F0FE" if is_today else "#F8F9FA")
            fg_color = "white" if is_selected else ("#4A90D9" if is_today else ("#9CA3AF" if not is_current_month else "#1A1A2E"))

            cell = tk.Frame(
                row_frame, width=80, height=60,
                bg=bg_color, highlightthickness=1,
                highlightbackground="#E5E7EB"
            )
            cell.pack(side="left", expand=True, fill="both")
            cell.pack_propagate(False)

            tk.Label(
                cell, text=str(d.day), font=("Segoe UI", 11, "bold"),
                bg=bg_color, fg=fg_color
            ).pack(pady=(4, 0))

            if has_events:
                tk.Label(
                    cell, text="●", font=("Segoe UI", 6),
                    bg=bg_color, fg="#4A90D9"
                ).pack()

            cell.bind("<Button-1>", lambda e, date=d: self._select_date(date))

    def _render_week(self):
        days = get_week_days(self.current_date)
        self.header_title.config(
            text=f"{days[0].strftime('%d/%m')} - {days[-1].strftime('%d/%m/%Y')}"
        )

        hdr = tk.Frame(self.grid_frame, bg="white")
        hdr.pack(fill="x")
        for day in WEEKDAYS:
            tk.Label(
                hdr, text=day, font=("Segoe UI", 9, "bold"),
                bg="white", fg="#6B7280", width=10
            ).pack(side="left", expand=True)

        week_events = self._get_month_events(days[0].year, days[0].month)

        row_frame = tk.Frame(self.grid_frame, bg="#F8F9FA")
        row_frame.pack(fill="x")

        today = datetime.now()
        for d in days:
            d_str = to_date_str(d)
            has_events = d_str in week_events
            is_selected = d.date() == self.selected_date.date()
            is_today = d.date() == today.date()

            bg_color = "#4A90D9" if is_selected else ("#E8F0FE" if is_today else "#F8F9FA")
            fg_color = "white" if is_selected else ("#4A90D9" if is_today else "#1A1A2E")

            cell = tk.Frame(
                row_frame, width=80, height=60,
                bg=bg_color, highlightthickness=1,
                highlightbackground="#E5E7EB"
            )
            cell.pack(side="left", expand=True, fill="both")
            cell.pack_propagate(False)

            tk.Label(
                cell, text=str(d.day), font=("Segoe UI", 11, "bold"),
                bg=bg_color, fg=fg_color
            ).pack(pady=(4, 0))

            if has_events:
                tk.Label(
                    cell, text="●", font=("Segoe UI", 6),
                    bg=bg_color, fg="#4A90D9"
                ).pack()

            cell.bind("<Button-1>", lambda e, date=d: self._select_date(date))

    def _render_day(self):
        d = self.selected_date
        month_name = MONTHS[d.month - 1]
        is_today = d.date() == datetime.now().date()
        title = f"{d.day} de {month_name} de {d.year}"
        if is_today:
            title += " (Hoje)"
        self.header_title.config(text=title)

        day_events = get_events_by_date(to_date_str(d))
        if not day_events:
            tk.Label(
                self.grid_frame, text="Nenhum compromisso neste dia",
                font=("Segoe UI", 12), bg="#F8F9FA", fg="#9CA3AF"
            ).pack(pady=20)
        else:
            for ev in day_events:
                self._create_event_card(self.grid_frame, ev)

    def _create_event_card(self, parent, ev):
        card = tk.Frame(
            parent, bg="white", highlightthickness=0,
            padx=12, pady=8
        )
        card.pack(fill="x", pady=3)

        bar = tk.Frame(card, bg=ev.get("color", "#4A90D9"), width=4)
        bar.pack(side="left", fill="y")
        bar.pack_propagate(False)

        content = tk.Frame(card, bg="white")
        content.pack(side="left", fill="x", expand=True, padx=(8, 0))

        start = parse_datetime(ev["start_date"])
        end = parse_datetime(ev["end_date"])
        tk.Label(
            content, text=f"{format_time(start)} - {format_time(end)}",
            font=("Segoe UI", 10), bg="white", fg="#6B7280"
        ).pack(anchor="w")

        tk.Label(
            content, text=ev["title"],
            font=("Segoe UI", 12, "bold"), bg="white", fg="#1A1A2E"
        ).pack(anchor="w")

        ev_id = ev["id"]
        card.bind("<Button-1>", lambda e: self.app.show_event_detail(ev_id))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e: self.app.show_event_detail(ev_id))

    def _select_date(self, date):
        self.selected_date = datetime(date.year, date.month, date.day)
        self._render()

    def _render_events(self):
        for w in self.events_frame.winfo_children():
            w.destroy()

        date_str = to_date_str(self.selected_date)
        events = get_events_by_date(date_str)

        tk.Label(
            self.events_frame,
            text=f"Compromissos - {self.selected_date.strftime('%d/%m/%Y')}",
            font=("Segoe UI", 12, "bold"), bg="#F8F9FA", fg="#1A1A2E"
        ).pack(anchor="w", pady=(0, 6))

        if not events:
            tk.Label(
                self.events_frame, text="Nenhum compromisso",
                font=("Segoe UI", 10), bg="#F8F9FA", fg="#9CA3AF"
            ).pack(anchor="w")
        else:
            for ev in events:
                self._create_event_card(self.events_frame, ev)

    def get_selected_date(self):
        return self.selected_date
