import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import tempfile
import os
from datetime import datetime
from database import get_all_tasks, get_all_contacts, get_all_receipts


class PrintView(tk.Frame):
    def __init__(self, parent, app, colors):
        super().__init__(parent, bg=colors["bg"])
        self.app = app
        self.C = colors
        self._build_ui()

    def _build_ui(self):
        main = tk.Frame(self, bg=self.C["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=16)

        tk.Label(
            main, text="Impress\u00e3o de Relat\u00f3rios",
            font=("Segoe UI", 20, "bold"),
            bg=self.C["bg"], fg=self.C["text"]
        ).pack(anchor="w", pady=(0, 20))

        control_frame = tk.Frame(main, bg=self.C["bg"])
        control_frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            control_frame, text="Tipo de relat\u00f3rio:",
            font=("Segoe UI", 12, "bold"),
            bg=self.C["bg"], fg=self.C["text"]
        ).pack(side="left", padx=(0, 8))

        self.report_var = tk.StringVar(value="Tarefas")
        self.report_combo = ttk.Combobox(
            control_frame, textvariable=self.report_var,
            values=["Tarefas", "Contatos", "Recibos"],
            width=20, font=("Segoe UI", 11), state="readonly"
        )
        self.report_combo.pack(side="left", padx=(0, 12))

        tk.Button(
            control_frame, text="Gerar Visualiza\u00e7\u00e3o",
            font=("Segoe UI", 11, "bold"),
            bg=self.C["accent"], fg="white",
            relief="flat", bd=0, padx=14, pady=6,
            cursor="hand2", command=self._generate
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            control_frame, text="Salvar como...",
            font=("Segoe UI", 11),
            bg="white", fg=self.C["accent"],
            relief="flat", bd=1, highlightbackground=self.C["border"],
            padx=14, pady=6, cursor="hand2", command=self._save
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            control_frame, text="Imprimir",
            font=("Segoe UI", 11, "bold"),
            bg="#FF9500", fg="white",
            relief="flat", bd=0, padx=14, pady=6,
            cursor="hand2", command=self._print
        ).pack(side="left")

        self.text_area = scrolledtext.ScrolledText(
            main, font=("Segoe UI", 10),
            bg=self.C["surface"], fg=self.C["text"],
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=self.C["border"],
            wrap="word"
        )
        self.text_area.pack(fill="both", expand=True)

    def _generate(self):
        report_type = self.report_var.get()
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        lines = [
            "=" * 60,
            f"RELAT\u00d3RIO DE {report_type.upper()}",
            f"Gerado em: {now}",
            "=" * 60,
            "",
        ]

        if report_type == "Tarefas":
            data = get_all_tasks()
            lines += self._format_tasks(data)
        elif report_type == "Contatos":
            data = get_all_contacts()
            lines += self._format_contacts(data)
        else:
            data = get_all_receipts()
            lines += self._format_receipts(data)

        content = "\n".join(lines)
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", content)

    def _format_tasks(self, tasks):
        if not tasks:
            return ["Nenhuma tarefa encontrada."]
        lines = [
            f"{'T\u00edtulo':<40} {'Data':<12} {'Hora':<8} {'Prioridade':<10}",
            "-" * 70,
        ]
        for t in tasks:
            title = t["title"][:38]
            date = t.get("task_date", "") or ""
            time_ = t.get("task_time", "") or ""
            prio = {0: "Baixa", 1: "M\u00e9dia", 2: "Alta"}.get(
                t.get("priority", 1), "M\u00e9dia"
            )
            lines.append(f"{title:<40} {date:<12} {time_:<8} {prio:<10}")
        return lines

    def _format_contacts(self, contacts):
        if not contacts:
            return ["Nenhum contato encontrado."]
        lines = [
            f"{'Nome':<30} {'Telefone':<16} {'Email':<30}",
            "-" * 76,
        ]
        for c in contacts:
            name = c["name"][:28]
            phone = c.get("phone", "") or ""
            email = c.get("email", "") or ""
            lines.append(f"{name:<30} {phone:<16} {email:<30}")
        return lines

    def _format_receipts(self, receipts):
        if not receipts:
            return ["Nenhum recibo encontrado."]
        lines = [
            f"{'Recebedor':<30} {'Valor':<12} {'Data':<12}",
            "-" * 54,
        ]
        for r in receipts:
            name = r["recipient_name"][:28]
            value = f"R$ {r['value']:.2f}"
            date = r.get("date", "") or ""
            lines.append(f"{name:<30} {value:<12} {date:<12}")
        return lines

    def _save(self):
        content = self.text_area.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("Aviso", "Gere uma visualiza\u00e7\u00e3o primeiro.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt"), ("Todos os arquivos", "*.*")],
            title="Salvar relat\u00f3rio como..."
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Sucesso", f"Relat\u00f3rio salvo em:\n{path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar:\n{e}")

    def _print(self):
        content = self.text_area.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("Aviso", "Gere uma visualiza\u00e7\u00e3o primeiro.")
            return
        try:
            tmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False, encoding="utf-8"
            )
            tmp.write(content)
            tmp.close()
            try:
                subprocess.run(["notepad.exe", "/P", tmp.name], check=True)
            except (subprocess.SubprocessError, FileNotFoundError):
                os.startfile(tmp.name)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao imprimir:\n{e}")

    def refresh(self):
        pass
