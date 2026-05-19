import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from utils import CATEGORIES, REMINDER_OPTIONS, parse_datetime, to_date_str
from database import save_event, get_event_by_id
from conflict_check import check_conflict


class EventFormDialog(tk.Toplevel):
    def __init__(self, parent, app, event=None, selected_date=None):
        super().__init__(parent)
        self.app = app
        self.event = event
        self.result = None

        self.title("Editar Evento" if event else "Novo Evento")
        self.geometry("500x620")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_form(selected_date)

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 250
        y = (self.winfo_screenheight() // 2) - 310
        self.geometry(f"+{x}+{y}")

    def _build_form(self, selected_date):
        main = tk.Frame(self, padx=20, pady=20, bg="#F8F9FA")
        main.pack(fill="both", expand=True)

        # Title
        tk.Label(main, text="Título *", font=("Segoe UI", 11, "bold"),
                 bg="#F8F9FA", fg="#1A1A2E").pack(anchor="w")
        self.title_entry = tk.Entry(main, font=("Segoe UI", 12),
                                    relief="solid", bd=1)
        self.title_entry.pack(fill="x", pady=(0, 12))
        if self.event:
            self.title_entry.insert(0, self.event["title"])

        # Date/Time row
        row = tk.Frame(main, bg="#F8F9FA")
        row.pack(fill="x")

        # Start date & time
        left = tk.Frame(row, bg="#F8F9FA")
        left.pack(side="left", fill="x", expand=True, padx=(0, 6))

        tk.Label(left, text="Data início", font=("Segoe UI", 10, "bold"),
                 bg="#F8F9FA", fg="#1A1A2E").pack(anchor="w")
        start_date = self.event and parse_datetime(self.event["start_date"])
        if not start_date:
            start_date = selected_date if selected_date else datetime.now()
        self.start_date_entry = tk.Entry(left, font=("Segoe UI", 11),
                                         relief="solid", bd=1)
        self.start_date_entry.pack(fill="x", pady=(0, 6))
        self.start_date_entry.insert(0, start_date.strftime("%Y-%m-%d"))

        tk.Label(left, text="Horário início", font=("Segoe UI", 10, "bold"),
                 bg="#F8F9FA", fg="#1A1A2E").pack(anchor="w")
        self.start_time_entry = tk.Entry(left, font=("Segoe UI", 11),
                                         relief="solid", bd=1)
        self.start_time_entry.pack(fill="x", pady=(0, 6))
        self.start_time_entry.insert(0, start_date.strftime("%H:%M"))

        # End date & time
        right = tk.Frame(row, bg="#F8F9FA")
        right.pack(side="left", fill="x", expand=True, padx=(6, 0))

        tk.Label(right, text="Data fim", font=("Segoe UI", 10, "bold"),
                 bg="#F8F9FA", fg="#1A1A2E").pack(anchor="w")
        end_date = self.event and parse_datetime(self.event["end_date"])
        if not end_date:
            end_date = start_date
        self.end_date_entry = tk.Entry(right, font=("Segoe UI", 11),
                                       relief="solid", bd=1)
        self.end_date_entry.pack(fill="x", pady=(0, 6))
        self.end_date_entry.insert(0, end_date.strftime("%Y-%m-%d"))

        tk.Label(right, text="Horário fim", font=("Segoe UI", 10, "bold"),
                 bg="#F8F9FA", fg="#1A1A2E").pack(anchor="w")
        self.end_time_entry = tk.Entry(right, font=("Segoe UI", 11),
                                       relief="solid", bd=1)
        self.end_time_entry.pack(fill="x", pady=(0, 6))
        self.end_time_entry.insert(0, end_date.strftime("%H:%M"))

        # Category
        tk.Label(main, text="Categoria", font=("Segoe UI", 11, "bold"),
                 bg="#F8F9FA", fg="#1A1A2E").pack(anchor="w", pady=(8, 4))

        cat_frame = tk.Frame(main, bg="#F8F9FA")
        cat_frame.pack(fill="x")
        self.category_var = tk.StringVar(value=self.event["category"] if self.event else "work")
        for cat in CATEGORIES:
            btn = tk.Button(
                cat_frame, text=cat["label"],
                font=("Segoe UI", 10),
                bg="white", fg=cat["color"],
                relief="solid", bd=1,
                padx=10, pady=4,
                command=lambda c=cat["id"]: self.category_var.set(c)
            )
            btn.pack(side="left", padx=2)

        # Reminder
        tk.Label(main, text="Lembrete", font=("Segoe UI", 11, "bold"),
                 bg="#F8F9FA", fg="#1A1A2E").pack(anchor="w", pady=(8, 4))

        rem_frame = tk.Frame(main, bg="#F8F9FA")
        rem_frame.pack(fill="x")
        self.reminder_var = tk.IntVar(
            value=self.event["reminder"] if self.event and self.event.get("reminder") is not None else 10
        )
        for label, val in REMINDER_OPTIONS:
            rb = tk.Radiobutton(
                rem_frame, text=label, variable=self.reminder_var,
                value=val, font=("Segoe UI", 10),
                bg="#F8F9FA", selectcolor="#E8F0FE"
            )
            rb.pack(side="left", padx=2)

        # Description
        tk.Label(main, text="Descrição (opcional)", font=("Segoe UI", 11, "bold"),
                 bg="#F8F9FA", fg="#1A1A2E").pack(anchor="w", pady=(8, 4))
        self.desc_text = tk.Text(main, height=3, font=("Segoe UI", 11),
                                 relief="solid", bd=1)
        self.desc_text.pack(fill="x", pady=(0, 12))
        if self.event and self.event.get("description"):
            self.desc_text.insert("1.0", self.event["description"])

        # Buttons
        btn_frame = tk.Frame(main, bg="#F8F9FA")
        btn_frame.pack(fill="x", pady=(8, 0))

        tk.Button(
            btn_frame, text="Cancelar",
            font=("Segoe UI", 11),
            bg="white", fg="#6B7280",
            relief="solid", bd=1, padx=16, pady=6,
            command=self.destroy
        ).pack(side="right", padx=(6, 0))

        tk.Button(
            btn_frame, text="Salvar",
            font=("Segoe UI", 11, "bold"),
            bg="#4A90D9", fg="white",
            relief="solid", bd=0, padx=16, pady=6,
            command=self._save
        ).pack(side="right")

    def _save(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Atenção", "O título é obrigatório.")
            return

        try:
            start_str = f"{self.start_date_entry.get().strip()} {self.start_time_entry.get().strip()}"
            end_str = f"{self.end_date_entry.get().strip()} {self.end_time_entry.get().strip()}"
            start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showwarning("Atenção", "Formato de data/hora inválido. Use YYYY-MM-DD e HH:MM.")
            return

        if end_dt <= start_dt:
            messagebox.showwarning("Atenção", "O fim do evento deve ser após o início.")
            return

        # Conflict check
        conflicts = check_conflict(
            start_dt.isoformat(), end_dt.isoformat(),
            self.event["id"] if self.event else None
        )
        if conflicts:
            names = "\n".join([c["title"] for c in conflicts])
            if not messagebox.askyesno(
                "Conflito de horário",
                f"Já existe(m) compromisso(s) neste horário:\n{names}\n\nDeseja salvar mesmo assim?"
            ):
                return

        color = "#4A90D9"
        for cat in CATEGORIES:
            if cat["id"] == self.category_var.get():
                color = cat["color"]
                break

        event_data = {
            "title": title,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "description": self.desc_text.get("1.0", "end-1c").strip(),
            "category": self.category_var.get(),
            "color": color,
            "reminder": self.reminder_var.get(),
        }
        if self.event:
            event_data["id"] = self.event["id"]

        save_event(event_data)
        self.app.refresh_all()
        self.destroy()


class EventDetailDialog(tk.Toplevel):
    def __init__(self, parent, app, event_id):
        super().__init__(parent)
        self.app = app
        self.event_id = event_id

        self.title("Detalhes do Evento")
        self.geometry("450x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._load_and_show()

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 225
        y = (self.winfo_screenheight() // 2) - 200
        self.geometry(f"+{x}+{y}")

    def _load_and_show(self):
        event = get_event_by_id(self.event_id)
        if not event:
            messagebox.showerror("Erro", "Evento não encontrado.")
            self.destroy()
            return

        main = tk.Frame(self, bg=event.get("color", "#4A90D9"))
        main.pack(fill="both", expand=True)

        # Color bar
        content = tk.Frame(main, bg="white", padx=20, pady=20)
        content.pack(fill="both", expand=True, padx=2, pady=2)

        # Category badge
        cat_frame = tk.Frame(content, bg=event.get("color", "#4A90D9") + "30")
        cat_frame.pack(anchor="w", pady=(0, 12))
        cat_label = "Outro"
        for c in CATEGORIES:
            if c["id"] == event.get("category"):
                cat_label = c["label"]
                break
        tk.Label(
            cat_frame, text=cat_label,
            font=("Segoe UI", 10, "bold"),
            bg=event.get("color", "#4A90D9") + "30",
            fg=event.get("color", "#4A90D9"),
            padx=8, pady=2
        ).pack()

        # Title
        tk.Label(
            content, text=event["title"],
            font=("Segoe UI", 18, "bold"), bg="white", fg="#1A1A2E"
        ).pack(anchor="w")

        # Date & time
        start = parse_datetime(event["start_date"])
        end = parse_datetime(event["end_date"])

        info = tk.Frame(content, bg="white")
        info.pack(fill="x", pady=(16, 0))

        for label, value in [
            ("INÍCIO", f"{start.strftime('%d/%m/%Y')} às {start.strftime('%H:%M')}"),
            ("FIM", f"{end.strftime('%d/%m/%Y')} às {end.strftime('%H:%M')}"),
        ]:
            tk.Label(
                info, text=label,
                font=("Segoe UI", 9, "bold"), bg="white",
                fg="#6B7280"
            ).pack(anchor="w")
            tk.Label(
                info, text=value,
                font=("Segoe UI", 12), bg="white", fg="#1A1A2E"
            ).pack(anchor="w", pady=(0, 8))

        # Lembrete
        rem_val = event.get("reminder")
        rem_label = "No horário"
        for l, v in REMINDER_OPTIONS:
            if v == rem_val:
                rem_label = l
                break
        tk.Label(
            info, text="LEMBRETE",
            font=("Segoe UI", 9, "bold"), bg="white", fg="#6B7280"
        ).pack(anchor="w")
        tk.Label(
            info, text=rem_label,
            font=("Segoe UI", 12), bg="white", fg="#1A1A2E"
        ).pack(anchor="w", pady=(0, 8))

        # Description
        if event.get("description"):
            tk.Label(
                info, text="DESCRIÇÃO",
                font=("Segoe UI", 9, "bold"), bg="white", fg="#6B7280"
            ).pack(anchor="w")
            tk.Label(
                info, text=event["description"],
                font=("Segoe UI", 11), bg="white", fg="#4B5563",
                wraplength=380, justify="left"
            ).pack(anchor="w", pady=(0, 8))

        # Buttons
        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(fill="x", pady=(16, 0))

        tk.Button(
            btn_frame, text="Excluir",
            font=("Segoe UI", 11),
            bg="white", fg="#EF4444",
            relief="solid", bd=1, padx=14, pady=4,
            command=self._delete
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_frame, text="Editar",
            font=("Segoe UI", 11, "bold"),
            bg="#4A90D9", fg="white",
            relief="solid", bd=0, padx=14, pady=4,
            command=self._edit
        ).pack(side="left")

        tk.Button(
            btn_frame, text="Fechar",
            font=("Segoe UI", 11),
            bg="white", fg="#6B7280",
            relief="solid", bd=1, padx=14, pady=4,
            command=self.destroy
        ).pack(side="right")

    def _edit(self):
        event = get_event_by_id(self.event_id)
        if event:
            self.destroy()
            EventFormDialog(self.app, self.app, event=event)

    def _delete(self):
        event = get_event_by_id(self.event_id)
        if not event:
            return
        if messagebox.askyesno(
            "Excluir evento",
            f'Tem certeza que deseja excluir "{event["title"]}"?'
        ):
            from database import delete_event
            delete_event(self.event_id)
            self.app.refresh_all()
            self.destroy()
