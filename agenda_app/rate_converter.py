import tkinter as tk
from tkinter import ttk, messagebox

PERIOD_DAYS = {"ao dia": 1, "ao mês": 30, "ao ano": 365}


class RateConverterView(tk.Frame):
    def __init__(self, parent, app, colors):
        super().__init__(parent, bg=colors["bg"])
        self.app = app
        self.C = colors
        self._build_ui()

    def _build_ui(self):
        main = tk.Frame(self, bg=self.C["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=16)

        tk.Label(
            main, text="Conversor de Taxas",
            font=("Segoe UI", 20, "bold"),
            bg=self.C["bg"], fg=self.C["text"]
        ).pack(anchor="w", pady=(0, 16))

        card = tk.Frame(
            main, bg=self.C["surface"],
            highlightthickness=1, highlightbackground=self.C["border"]
        )
        card.pack(fill="x", pady=(0, 16))

        form = tk.Frame(card, bg=self.C["surface"])
        form.pack(fill="x", padx=24, pady=20)

        tk.Label(form, text="Valor da taxa (%)", font=("Segoe UI", 10, "bold"),
                 bg=self.C["surface"], fg=self.C["text"]
                 ).pack(anchor="w", pady=(6, 2))
        f_val = tk.Frame(form, bg=self.C["border"], bd=0)
        f_val.pack(fill="x")
        self.value_entry = tk.Entry(f_val, font=("Segoe UI", 12), bg=self.C["surface"],
                                    fg=self.C["text"], relief="flat", bd=0)
        self.value_entry.pack(fill="x", ipady=2)

        row1 = tk.Frame(form, bg=self.C["surface"])
        row1.pack(fill="x", pady=(12, 4))

        tk.Label(row1, text="De:", font=("Segoe UI", 10, "bold"),
                 bg=self.C["surface"], fg=self.C["text"]
                 ).pack(side="left", padx=(0, 8))

        self.from_var = tk.StringVar(value="ao mês")
        self.from_combo = ttk.Combobox(row1, textvariable=self.from_var,
                                       values=["ao dia", "ao mês", "ao ano"],
                                       width=12, font=("Segoe UI", 10), state="readonly")
        self.from_combo.pack(side="left")

        row2 = tk.Frame(form, bg=self.C["surface"])
        row2.pack(fill="x", pady=(4, 12))

        tk.Label(row2, text="Para:", font=("Segoe UI", 10, "bold"),
                 bg=self.C["surface"], fg=self.C["text"]
                 ).pack(side="left", padx=(0, 8))

        self.to_var = tk.StringVar(value="ao ano")
        self.to_combo = ttk.Combobox(row2, textvariable=self.to_var,
                                     values=["ao dia", "ao mês", "ao ano"],
                                     width=12, font=("Segoe UI", 10), state="readonly")
        self.to_combo.pack(side="left")

        tk.Button(
            form, text="Converter",
            font=("Segoe UI", 12, "bold"),
            bg=self.C["accent"], fg="white",
            relief="flat", bd=0, padx=20, pady=10,
            cursor="hand2", command=self._convert
        ).pack(anchor="w")

        # Result
        result_card = tk.Frame(
            main, bg=self.C["surface"],
            highlightthickness=1, highlightbackground=self.C["border"]
        )
        result_card.pack(fill="x")

        result_inner = tk.Frame(result_card, bg=self.C["surface"])
        result_inner.pack(fill="x", padx=24, pady=20)

        tk.Label(result_inner, text="Resultado",
                 font=("Segoe UI", 14, "bold"),
                 bg=self.C["surface"], fg=self.C["text"]
                 ).pack(anchor="w", pady=(0, 10))

        tk.Label(result_inner, text="Fórmula: (1 + r)^n - 1",
                 font=("Segoe UI", 10),
                 bg=self.C["surface"], fg=self.C["text_sec"]
                 ).pack(anchor="w")

        tk.Frame(result_inner, bg=self.C["border"], height=1).pack(fill="x", pady=(10, 10))

        self.result_label = tk.Label(result_inner, text="--",
                                     font=("Segoe UI", 24, "bold"),
                                     bg=self.C["surface"], fg=self.C["accent"]
                                     )
        self.result_label.pack(anchor="w")

    def refresh(self):
        pass

    def _convert(self):
        try:
            rate = float(self.value_entry.get().strip().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Atenção", "Valor da taxa inválido.")
            return

        from_period = self.from_var.get()
        to_period = self.to_var.get()

        if from_period == to_period:
            self.result_label.config(text=f"{rate:.4f}%")
            return

        r = rate / 100
        from_days = PERIOD_DAYS[from_period]
        to_days = PERIOD_DAYS[to_period]

        n = to_days / from_days
        result = ((1 + r) ** n - 1) * 100

        self.result_label.config(text=f"{result:.4f}%")
