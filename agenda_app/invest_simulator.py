import tkinter as tk
from tkinter import messagebox


class InvestSimulatorView(tk.Frame):
    def __init__(self, parent, app, colors):
        super().__init__(parent, bg=colors["bg"])
        self.app = app
        self.C = colors
        self._build_ui()

    def _build_ui(self):
        main = tk.Frame(self, bg=self.C["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=16)

        tk.Label(
            main, text="Simulador de Investimento",
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
            ("Valor Inicial (R$)", "initial"),
            ("Aporte Mensal (R$)", "monthly"),
            ("Taxa (% ao ano)", "rate"),
            ("Período (meses)", "period"),
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

        tk.Button(
            form, text="Calcular",
            font=("Segoe UI", 12, "bold"),
            bg=self.C["accent"], fg="white",
            relief="flat", bd=0, padx=20, pady=10,
            cursor="hand2", command=self._calculate
        ).pack(anchor="w", pady=(12, 0))

        # Results card
        self.result_card = tk.Frame(
            main, bg=self.C["surface"],
            highlightthickness=1, highlightbackground=self.C["border"]
        )
        self.result_card.pack(fill="x", pady=(0, 12))

        self.result_inner = tk.Frame(self.result_card, bg=self.C["surface"])
        self.result_inner.pack(fill="x", padx=24, pady=20)

        tk.Label(self.result_inner, text="Resultados",
                 font=("Segoe UI", 14, "bold"),
                 bg=self.C["surface"], fg=self.C["text"]
                 ).pack(anchor="w", pady=(0, 10))

        self.result_labels = {}
        for label in ["Valor Final", "Total Aportado", "Total de Juros"]:
            row = tk.Frame(self.result_inner, bg=self.C["surface"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{label}:", font=("Segoe UI", 11),
                     bg=self.C["surface"], fg=self.C["text_sec"], width=16, anchor="w"
                     ).pack(side="left")
            lbl = tk.Label(row, text="-", font=("Segoe UI", 11, "bold"),
                           bg=self.C["surface"], fg=self.C["accent"], anchor="w")
            lbl.pack(side="left", fill="x", expand=True)
            self.result_labels[label] = lbl

        # Table
        tk.Label(main, text="Mês a mês", font=("Segoe UI", 12, "bold"),
                 bg=self.C["bg"], fg=self.C["text"]
                 ).pack(anchor="w", pady=(0, 4))

        table_frame = tk.Frame(main, bg=self.C["border"], bd=1)
        table_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(table_frame, orient="vertical")
        self.table = tk.Listbox(table_frame, font=("Segoe UI", 9),
                                bg=self.C["surface"], fg=self.C["text"],
                                relief="flat", bd=0,
                                yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.table.yview)
        scrollbar.pack(side="right", fill="y")
        self.table.pack(side="left", fill="both", expand=True)

    def refresh(self):
        pass

    def _calculate(self):
        try:
            pv = float(self.entries["initial"].get().strip().replace(",", ".") or "0")
            pmt = float(self.entries["monthly"].get().strip().replace(",", ".") or "0")
            annual_rate = float(self.entries["rate"].get().strip().replace(",", ".") or "0")
            n = int(self.entries["period"].get().strip() or "0")
        except ValueError:
            messagebox.showwarning("Atenção", "Preencha todos os campos com valores numéricos.")
            return

        if n <= 0:
            messagebox.showwarning("Atenção", "Período deve ser maior que zero.")
            return

        r = annual_rate / 100 / 12

        fv = pv * (1 + r) ** n + pmt * ((1 + r) ** n - 1) / r if r != 0 else pv + pmt * n
        total_invested = pv + pmt * n
        total_interest = fv - total_invested

        self.result_labels["Valor Final"].config(text=f"R$ {fv:,.2f}")
        self.result_labels["Total Aportado"].config(text=f"R$ {total_invested:,.2f}")
        self.result_labels["Total de Juros"].config(text=f"R$ {total_interest:,.2f}")

        self.table.delete(0, "end")
        self.table.insert("end", f"{'Mês':<6} {'Saldo':>14} {'Juros':>14}")
        self.table.insert("end", "-" * 36)
        balance = pv
        for i in range(1, n + 1):
            interest = balance * r
            balance = balance * (1 + r) + pmt
            self.table.insert("end", f"{i:<6} R$ {balance:>10,.2f} R$ {interest:>10,.2f}")
