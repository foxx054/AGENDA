import tkinter as tk
from tkinter import ttk, messagebox
from database import get_setting, set_setting


class SettingsView(tk.Frame):
    def __init__(self, parent, app, colors):
        super().__init__(parent, bg=colors["bg"])
        self.app = app
        self.C = colors
        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        main = tk.Frame(self, bg=self.C["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=16)

        tk.Label(
            main, text="Configurações",
            font=("Segoe UI", 20, "bold"),
            bg=self.C["bg"], fg=self.C["text"]
        ).pack(anchor="w", pady=(0, 20))

        card = tk.Frame(
            main, bg=self.C["surface"],
            highlightthickness=1, highlightbackground=self.C["border"]
        )
        card.pack(fill="x", pady=(0, 16))

        body = tk.Frame(card, bg=self.C["surface"])
        body.pack(fill="x", padx=24, pady=20)

        # Theme toggle
        tk.Label(
            body, text="Tema",
            font=("Segoe UI", 12, "bold"),
            bg=self.C["surface"], fg=self.C["text"]
        ).pack(anchor="w")

        self.theme_var = tk.StringVar(value="light")
        theme_row = tk.Frame(body, bg=self.C["surface"])
        theme_row.pack(anchor="w", pady=(4, 16))

        tk.Radiobutton(
            theme_row, text="Claro", variable=self.theme_var,
            value="light", font=("Segoe UI", 10),
            bg=self.C["surface"], selectcolor="#E8F0FE"
        ).pack(side="left", padx=2)

        tk.Radiobutton(
            theme_row, text="Escuro", variable=self.theme_var,
            value="dark", font=("Segoe UI", 10),
            bg=self.C["surface"], selectcolor="#E8F0FE",
            state="disabled"
        ).pack(side="left", padx=2)

        tk.Label(
            theme_row, text="(em breve)",
            font=("Segoe UI", 9), bg=self.C["surface"], fg=self.C["text_sec"]
        ).pack(side="left", padx=(4, 0))

        # Notification interval
        tk.Label(
            body, text="Intervalo de notificação",
            font=("Segoe UI", 12, "bold"),
            bg=self.C["surface"], fg=self.C["text"]
        ).pack(anchor="w")

        self.notif_var = tk.IntVar(value=30)
        notif_row = tk.Frame(body, bg=self.C["surface"])
        notif_row.pack(anchor="w", pady=(4, 16))

        tk.Label(
            notif_row, text="A cada",
            font=("Segoe UI", 10),
            bg=self.C["surface"], fg=self.C["text"]
        ).pack(side="left", padx=(0, 6))

        self.notif_combo = ttk.Combobox(
            notif_row, textvariable=self.notif_var,
            values=[1, 5, 10, 15, 30, 60, 120],
            width=6, font=("Segoe UI", 10), state="readonly"
        )
        self.notif_combo.pack(side="left")
        tk.Label(
            notif_row, text="minutos",
            font=("Segoe UI", 10),
            bg=self.C["surface"], fg=self.C["text"]
        ).pack(side="left", padx=(6, 0))

        # Birthday reminder toggle
        tk.Label(
            body, text="Lembretes",
            font=("Segoe UI", 12, "bold"),
            bg=self.C["surface"], fg=self.C["text"]
        ).pack(anchor="w")

        self.birthday_var = tk.BooleanVar(value=True)
        bday_row = tk.Frame(body, bg=self.C["surface"])
        bday_row.pack(anchor="w", pady=(4, 0))

        tk.Checkbutton(
            bday_row, text="Lembrar de aniversários",
            variable=self.birthday_var,
            font=("Segoe UI", 10),
            bg=self.C["surface"], fg=self.C["text"],
            selectcolor="#E8F0FE"
        ).pack(side="left")

        # Separator
        sep = tk.Frame(body, bg=self.C["border"], height=1)
        sep.pack(fill="x", pady=(16, 12))

        # Save button
        tk.Button(
            body, text="Salvar Configurações",
            font=("Segoe UI", 12, "bold"),
            bg=self.C["accent"], fg="white",
            relief="flat", bd=0, padx=20, pady=10,
            cursor="hand2", command=self._save
        ).pack(anchor="w")

        self.status_label = tk.Label(
            body, text="", font=("Segoe UI", 10),
            bg=self.C["surface"], fg="#34C759"
        )
        self.status_label.pack(anchor="w", pady=(6, 0))

    def _load_settings(self):
        theme = get_setting("theme", "light")
        notif_val = get_setting("notification_interval", "30")
        bday_val = get_setting("birthday_reminder", "1")
        self.theme_var.set(theme)
        try:
            self.notif_var.set(int(notif_val))
        except ValueError:
            self.notif_var.set(30)
        self.birthday_var.set(bday_val == "1")

    def _save(self):
        set_setting("theme", self.theme_var.get())
        set_setting("notification_interval", str(self.notif_var.get()))
        set_setting("birthday_reminder", "1" if self.birthday_var.get() else "0")
        self.status_label.config(text="Configurações salvas com sucesso!")
        self.after(3000, lambda: self.status_label.config(text=""))

    def refresh(self):
        self._load_settings()
