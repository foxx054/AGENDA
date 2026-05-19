import tkinter as tk
from tkinter import messagebox


class ROICalculatorView(tk.Frame):
    def __init__(self, parent, app, colors):
        super().__init__(parent, bg=colors["bg"])
        self.app = app
        self.C = colors
        self._build_ui()

    def _build_ui(self):
        main = tk.Frame(self, bg=self.C["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=16)

        tk.Label(
            main, text="Calculadora de ROI",
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

        fields = [
            ("Investimento Inicial (R$)", "initial"),
            ("Retorno Total (R$)", "return_val"),
        ]
        self.entries = {}
        for label, key in fields:
            tk.Label(form, text=label, font=("Segoe UI", 10, "bold"),
                     bg=self.C["surface"], fg=self.C["text"]
                     ).pack(anchor="w", pady=(6, 2))
            f = tk.Frame(form, bg=self.C["border"], bd=0)
            f.pack(fill="x")
            entry = tk.Entry(f, font=("Segoe UI", 12), bg=self.C["surface"],
                             fg=self.C["text"], relief="flat", bd=0)
            entry.pack(fill="x", ipady=2)
            self.entries[key] = entry

        tk.Label(form, text="Período (meses) - opcional", font=("Segoe UI", 10, "bold"),
                 bg=self.C["surface"], fg=self.C["text"]
                 ).pack(anchor="w", pady=(6, 2))
        f_period = tk.Frame(form, bg=self.C["border"], bd=0)
        f_period.pack(fill="x")
        self.period_entry = tk.Entry(f_period, font=("Segoe UI", 12), bg=self.C["surface"],
                                     fg=self.C["text"], relief="flat", bd=0)
        self.period_entry.pack(fill="x", ipady=2)

        tk.Button(
            form, text="Calcular ROI",
            font=("Segoe UI", 12, "bold"),
            bg=self.C["accent"], fg="white",
            relief="flat", bd=0, padx=20, pady=10,
            cursor="hand2", command=self._calculate
        ).pack(anchor="w", pady=(12, 0))

        # Result card
        self.result_card = tk.Frame(
            main, bg=self.C["surface"],
            highlightthickness=1, highlightbackground=self.C["border"]
        )
        self.result_card.pack(fill="x", pady=(0, 16))

        self.result_inner = tk.Frame(self.result_card, bg=self.C["surface"])
        self.result_inner.pack(fill="x", padx=24, pady=20)

        tk.Label(self.result_inner, text="Resultado",
                 font=("Segoe UI", 14, "bold"),
                 bg=self.C["surface"], fg=self.C["text"]
                 ).pack(anchor="w", pady=(0, 12))

        tk.Label(self.result_inner, text="Fórmula: ROI = ((Retorno - Investimento) / Investimento) × 100",
                 font=("Segoe UI", 10), bg=self.C["surface"], fg=self.C["text_sec"]
                 ).pack(anchor="w")

        tk.Frame(self.result_inner, bg=self.C["border"], height=1).pack(fill="x", pady=(10, 10))

        self.roi_label = tk.Label(self.result_inner, text="ROI: --",
                                  font=("Segoe UI", 24, "bold"),
                                  bg=self.C["surface"], fg=self.C["accent"]
                                  )
        self.roi_label.pack(anchor="w")

        self.annualized_label = tk.Label(self.result_inner, text="",
                                         font=("Segoe UI", 12),
                                         bg=self.C["surface"], fg=self.C["text_sec"]
                                         )
        self.annualized_label.pack(anchor="w", pady=(2, 0))

    def refresh(self):
        pass

    def _calculate(self):
        try:
            initial = float(self.entries["initial"].get().strip().replace(",", ".") or "0")
            return_val = float(self.entries["return_val"].get().strip().replace(",", ".") or "0")
        except ValueError:
            messagebox.showwarning("Atenção", "Preencha os campos com valores numéricos.")
            return

        if initial <= 0:
            messagebox.showwarning("Atenção", "Investimento inicial deve ser maior que zero.")
            return

        roi = ((return_val - initial) / initial) * 100
        color = "#34C759" if roi >= 0 else "#FF3B30"
        self.roi_label.config(text=f"ROI: {roi:+.2f}%", fg=color)

        period_text = self.period_entry.get().strip()
        if period_text:
            try:
                months = int(period_text)
                if months > 0:
                    annualized = ((1 + roi / 100) ** (12 / months) - 1) * 100
                    self.annualized_label.config(
                        text=f"ROI anualizado: {annualized:+.2f}%"
                    )
            except ValueError:
                self.annualized_label.config(text="")
        else:
            self.annualized_label.config(text="")
