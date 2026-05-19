import tkinter as tk
from tkinter import messagebox


class BMICalculatorView(tk.Frame):
    def __init__(self, parent, app, colors):
        super().__init__(parent, bg=colors["bg"])
        self.app = app
        self.C = colors
        self._build_ui()

    def _build_ui(self):
        main = tk.Frame(self, bg=self.C["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=16)

        tk.Label(
            main, text="Calculadora de IMC",
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
            ("Peso (kg)", "weight"),
            ("Altura (cm)", "height"),
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
            form, text="Calcular IMC",
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
        self.result_card.pack(fill="x")

        self.result_inner = tk.Frame(self.result_card, bg=self.C["surface"])
        self.result_inner.pack(fill="x", padx=24, pady=20)

        tk.Label(self.result_inner, text="Resultado",
                 font=("Segoe UI", 14, "bold"),
                 bg=self.C["surface"], fg=self.C["text"]
                 ).pack(anchor="w", pady=(0, 12))

        self.bmi_label = tk.Label(self.result_inner, text="IMC: --",
                                  font=("Segoe UI", 28, "bold"),
                                  bg=self.C["surface"], fg=self.C["text"]
                                  )
        self.bmi_label.pack(anchor="w")

        self.category_label = tk.Label(self.result_inner, text="",
                                       font=("Segoe UI", 16),
                                       bg=self.C["surface"]
                                       )
        self.category_label.pack(anchor="w", pady=(4, 0))

    def refresh(self):
        pass

    def _calculate(self):
        try:
            weight = float(self.entries["weight"].get().strip().replace(",", "."))
            height_cm = float(self.entries["height"].get().strip().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Atenção", "Preencha os campos com valores numéricos.")
            return

        if weight <= 0 or height_cm <= 0:
            messagebox.showwarning("Atenção", "Valores devem ser maiores que zero.")
            return

        height_m = height_cm / 100
        bmi = weight / (height_m ** 2)

        if bmi < 18.5:
            category = "Abaixo do peso"
            color = "#FF9500"
        elif bmi < 25:
            category = "Normal"
            color = "#34C759"
        elif bmi < 30:
            category = "Sobrepeso"
            color = "#FF9500"
        elif bmi < 35:
            category = "Obesidade grau I"
            color = "#FF3B30"
        elif bmi < 40:
            category = "Obesidade grau II"
            color = "#FF3B30"
        else:
            category = "Obesidade grau III"
            color = "#FF3B30"

        self.bmi_label.config(text=f"IMC: {bmi:.1f}", fg=color)
        self.category_label.config(text=category, fg=color)
