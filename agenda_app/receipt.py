import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from database import add_receipt, get_all_receipts, delete_receipt


class ReceiptView(tk.Frame):
    def __init__(self, parent, app, colors):
        super().__init__(parent, bg=colors["bg"])
        self.app = app
        self.C = colors
        self._build_ui()

    def _build_ui(self):
        main = tk.Frame(self, bg=self.C["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=16)

        tk.Label(
            main, text="Emissor de Recibos",
            font=("Segoe UI", 20, "bold"),
            bg=self.C["bg"], fg=self.C["text"]
        ).pack(anchor="w", pady=(0, 16))

        # Form card
        card = tk.Frame(
            main, bg=self.C["surface"],
            highlightthickness=1, highlightbackground=self.C["border"]
        )
        card.pack(fill="x", pady=(0, 16))

        form = tk.Frame(card, bg=self.C["surface"])
        form.pack(fill="x", padx=24, pady=20)

        tk.Label(form, text="Nome do Recebedor", font=("Segoe UI", 10, "bold"),
                 bg=self.C["surface"], fg=self.C["text"]).pack(anchor="w")
        f1 = tk.Frame(form, bg=self.C["border"], bd=0)
        f1.pack(fill="x", pady=(2, 8))
        self.name_entry = tk.Entry(f1, font=("Segoe UI", 12), bg=self.C["surface"],
                                   fg=self.C["text"], relief="flat", bd=0)
        self.name_entry.pack(fill="x", ipady=2)

        tk.Label(form, text="CPF/CNPJ", font=("Segoe UI", 10, "bold"),
                 bg=self.C["surface"], fg=self.C["text"]).pack(anchor="w")
        f2 = tk.Frame(form, bg=self.C["border"], bd=0)
        f2.pack(fill="x", pady=(2, 8))
        self.doc_entry = tk.Entry(f2, font=("Segoe UI", 12), bg=self.C["surface"],
                                  fg=self.C["text"], relief="flat", bd=0)
        self.doc_entry.pack(fill="x", ipady=2)

        tk.Label(form, text="Descrição", font=("Segoe UI", 10, "bold"),
                 bg=self.C["surface"], fg=self.C["text"]).pack(anchor="w")
        f3 = tk.Frame(form, bg=self.C["border"], bd=0)
        f3.pack(fill="x", pady=(2, 8))
        self.desc_text = tk.Text(f3, height=3, font=("Segoe UI", 11), bg=self.C["surface"],
                                 fg=self.C["text"], relief="flat", bd=0)
        self.desc_text.pack(fill="x")

        tk.Label(form, text="Valor (R$)", font=("Segoe UI", 10, "bold"),
                 bg=self.C["surface"], fg=self.C["text"]).pack(anchor="w")
        f4 = tk.Frame(form, bg=self.C["border"], bd=0)
        f4.pack(fill="x", pady=(2, 8))
        self.value_entry = tk.Entry(f4, font=("Segoe UI", 12), bg=self.C["surface"],
                                    fg=self.C["text"], relief="flat", bd=0)
        self.value_entry.pack(fill="x", ipady=2)

        tk.Label(form, text="Data", font=("Segoe UI", 10, "bold"),
                 bg=self.C["surface"], fg=self.C["text"]).pack(anchor="w")
        f5 = tk.Frame(form, bg=self.C["border"], bd=0)
        f5.pack(fill="x", pady=(2, 8))
        self.date_entry = tk.Entry(f5, font=("Segoe UI", 12), bg=self.C["surface"],
                                   fg=self.C["text"], relief="flat", bd=0)
        self.date_entry.pack(fill="x", ipady=2)
        self.date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

        tk.Button(
            form, text="Emitir Recibo",
            font=("Segoe UI", 12, "bold"),
            bg=self.C["accent"], fg="white",
            relief="flat", bd=0, padx=20, pady=10,
            cursor="hand2", command=self._emit
        ).pack(anchor="w", pady=(8, 0))

        # List
        tk.Label(main, text="Recibos emitidos", font=("Segoe UI", 14, "bold"),
                 bg=self.C["bg"], fg=self.C["text"]).pack(anchor="w", pady=(0, 8))

        container = tk.Frame(main, bg=self.C["bg"])
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, bg=self.C["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable = tk.Frame(self.canvas, bg=self.C["bg"])

        self.scrollable.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh(self):
        for w in self.scrollable.winfo_children():
            w.destroy()

        receipts = get_all_receipts()
        if not receipts:
            empty = tk.Frame(self.scrollable, bg=self.C["surface"],
                             highlightthickness=1, highlightbackground=self.C["border"])
            empty.pack(fill="x", pady=20)
            tk.Label(empty, text="Nenhum recibo emitido",
                     font=("Segoe UI", 13), bg=self.C["surface"], fg=self.C["text_sec"]
                     ).pack(pady=24)
            return

        for r in receipts:
            card = tk.Frame(self.scrollable, bg=self.C["surface"],
                            highlightthickness=1, highlightbackground=self.C["border"])
            card.pack(fill="x", pady=2)

            body = tk.Frame(card, bg=self.C["surface"])
            body.pack(fill="x", padx=14, pady=10)

            tk.Label(body, text=r["recipient_name"],
                     font=("Segoe UI", 13, "bold"),
                     bg=self.C["surface"], fg=self.C["text"]
                     ).pack(anchor="w")

            meta = tk.Frame(body, bg=self.C["surface"])
            meta.pack(anchor="w", pady=(2, 0))

            tk.Label(meta, text=f"R$ {r['value']:.2f}",
                     font=("Segoe UI", 11),
                     bg=self.C["surface"], fg=self.C["accent"]
                     ).pack(side="left", padx=(0, 12))

            tk.Label(meta, text=r.get("date", ""),
                     font=("Segoe UI", 11),
                     bg=self.C["surface"], fg=self.C["text_sec"]
                     ).pack(side="left")

            btn_frame = tk.Frame(card, bg=self.C["surface"])
            btn_frame.pack(fill="x", padx=14, pady=(0, 8))

            tk.Button(btn_frame, text="Visualizar",
                      font=("Segoe UI", 9), bg=self.C["surface"], fg=self.C["accent"],
                      relief="flat", bd=0, cursor="hand2",
                      command=lambda rid=r["id"]: self._view(rid)
                      ).pack(side="left", padx=(0, 8))

    def _emit(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Atenção", "Nome do recebedor é obrigatório.")
            return
        try:
            value = float(self.value_entry.get().strip().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Atenção", "Valor inválido.")
            return

        data = {
            "recipient_name": name,
            "recipient_doc": self.doc_entry.get().strip(),
            "description": self.desc_text.get("1.0", "end-1c").strip(),
            "value": value,
            "date": self.date_entry.get().strip(),
        }
        add_receipt(data)

        self.name_entry.delete(0, "end")
        self.doc_entry.delete(0, "end")
        self.desc_text.delete("1.0", "end")
        self.value_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

        self.refresh()
        messagebox.showinfo("Recibo", "Recibo emitido com sucesso!")

    def _view(self, receipt_id):
        receipts = get_all_receipts()
        r = None
        for rec in receipts:
            if rec["id"] == receipt_id:
                r = rec
                break
        if not r:
            return
        ReceiptDetailDialog(self, self.C, r, on_delete=lambda: self.refresh())


class ReceiptDetailDialog(tk.Toplevel):
    def __init__(self, parent, colors, receipt, on_delete=None):
        super().__init__(parent)
        self.C = colors
        self.receipt = receipt
        self.on_delete = on_delete

        self.title("Recibo")
        self.geometry("480x520")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self._build_viewer()

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 240
        y = (self.winfo_screenheight() // 2) - 260
        self.geometry(f"+{x}+{y}")

    def _build_viewer(self):
        bg = "#F5F5F7"
        surface = "#FFFFFF"
        text = "#1C1C1E"
        text_sec = "#8E8E93"
        border = "#E5E5EA"

        main = tk.Frame(self, bg=bg)
        main.pack(fill="both", expand=True, padx=24, pady=20)

        # Styled receipt
        card = tk.Frame(main, bg=surface,
                        highlightthickness=1, highlightbackground=border)
        card.pack(fill="x", pady=(0, 16))

        inner = tk.Frame(card, bg=surface)
        inner.pack(fill="x", padx=24, pady=24)

        tk.Label(inner, text="RECIBO", font=("Segoe UI", 22, "bold"),
                 bg=surface, fg=text).pack(anchor="center")
        tk.Frame(inner, bg=border, height=2).pack(fill="x", pady=(8, 16))

        fields = [
            ("Recebedor", self.receipt["recipient_name"]),
            ("CPF/CNPJ", self.receipt.get("recipient_doc", "")),
            ("Valor", f"R$ {self.receipt['value']:.2f}"),
            ("Data", self.receipt.get("date", "")),
        ]
        for label, val in fields:
            row = tk.Frame(inner, bg=surface)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"{label}:", font=("Segoe UI", 10, "bold"),
                     bg=surface, fg=text_sec, width=10, anchor="w"
                     ).pack(side="left")
            tk.Label(row, text=val, font=("Segoe UI", 12),
                     bg=surface, fg=text, anchor="w"
                     ).pack(side="left", fill="x", expand=True)

        desc = self.receipt.get("description", "")
        if desc:
            tk.Frame(inner, bg=border, height=1).pack(fill="x", pady=(8, 8))
            tk.Label(inner, text="Descrição:", font=("Segoe UI", 10, "bold"),
                     bg=surface, fg=text_sec, anchor="w"
                     ).pack(fill="x")
            tk.Label(inner, text=desc, font=("Segoe UI", 11),
                     bg=surface, fg=text, anchor="w", wraplength=380
                     ).pack(fill="x", pady=(2, 0))

        tk.Button(
            main, text="Excluir Recibo",
            font=("Segoe UI", 11, "bold"),
            bg="#FF3B30", fg="white",
            relief="flat", bd=0, padx=20, pady=8,
            cursor="hand2", command=self._delete
        ).pack(pady=(0, 8))

        tk.Button(
            main, text="Fechar",
            font=("Segoe UI", 11),
            bg="white", fg=text_sec,
            relief="flat", bd=1, highlightbackground=border,
            padx=20, pady=8, cursor="hand2", command=self.destroy
        ).pack()

    def _delete(self):
        if messagebox.askyesno("Excluir", "Excluir este recibo?"):
            delete_receipt(self.receipt["id"])
            if self.on_delete:
                self.on_delete()
            self.destroy()
