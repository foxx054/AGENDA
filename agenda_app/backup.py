import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os
from database import DB_PATH, get_setting, set_setting, get_connection


class BackupView(tk.Frame):
    def __init__(self, parent, app, colors):
        super().__init__(parent, bg=colors["bg"])
        self.app = app
        self.C = colors
        self._build_ui()

    def _build_ui(self):
        main = tk.Frame(self, bg=self.C["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=16)

        tk.Label(
            main, text="Backup e Restauração",
            font=("Segoe UI", 20, "bold"),
            bg=self.C["bg"], fg=self.C["text"]
        ).pack(anchor="w", pady=(0, 20))

        # Export card
        export_card = tk.Frame(
            main, bg=self.C["surface"],
            highlightthickness=1, highlightbackground=self.C["border"]
        )
        export_card.pack(fill="x", pady=(0, 12))

        export_body = tk.Frame(export_card, bg=self.C["surface"])
        export_body.pack(fill="x", padx=24, pady=20)

        tk.Label(
            export_body, text="Exportar Backup",
            font=("Segoe UI", 14, "bold"),
            bg=self.C["surface"], fg=self.C["text"]
        ).pack(anchor="w")

        tk.Label(
            export_body, text="Salve uma cópia do banco de dados em outro local.",
            font=("Segoe UI", 10),
            bg=self.C["surface"], fg=self.C["text_sec"]
        ).pack(anchor="w", pady=(4, 12))

        tk.Button(
            export_body, text="Exportar Backup",
            font=("Segoe UI", 11, "bold"),
            bg=self.C["accent"], fg="white",
            relief="flat", bd=0, padx=16, pady=8,
            cursor="hand2", command=self._export
        ).pack(anchor="w")

        # Import card
        import_card = tk.Frame(
            main, bg=self.C["surface"],
            highlightthickness=1, highlightbackground=self.C["border"]
        )
        import_card.pack(fill="x", pady=(0, 12))

        import_body = tk.Frame(import_card, bg=self.C["surface"])
        import_body.pack(fill="x", padx=24, pady=20)

        tk.Label(
            import_body, text="Importar Backup",
            font=("Segoe UI", 14, "bold"),
            bg=self.C["surface"], fg=self.C["text"]
        ).pack(anchor="w")

        tk.Label(
            import_body, text="Restaurar banco de dados de um arquivo anterior.",
            font=("Segoe UI", 10),
            bg=self.C["surface"], fg=self.C["text_sec"]
        ).pack(anchor="w", pady=(4, 8))

        warn_frame = tk.Frame(
            import_body, bg="#FFF3E0",
            highlightthickness=1, highlightbackground="#FFE0B2"
        )
        warn_frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            warn_frame, text="⚠️  Atenção: Isso substituirá todos os dados atuais!",
            font=("Segoe UI", 10, "bold"),
            bg="#FFF3E0", fg="#FF9500"
        ).pack(pady=8)

        tk.Button(
            import_body, text="Importar Backup",
            font=("Segoe UI", 11, "bold"),
            bg="#FF9500", fg="white",
            relief="flat", bd=0, padx=16, pady=8,
            cursor="hand2", command=self._import
        ).pack(anchor="w")

        # Status
        self.status_label = tk.Label(
            main, text="", font=("Segoe UI", 11),
            bg=self.C["bg"], fg=self.C["text_sec"]
        )
        self.status_label.pack(anchor="w", pady=(8, 0))

        self._update_status()

    def _update_status(self):
        last = get_setting("last_backup", "")
        if last:
            self.status_label.config(text=f"Último backup: {last}")
        else:
            self.status_label.config(text="Nenhum backup realizado ainda.")

    def _export(self):
        default_name = f"agenda_backup_{os.path.getmtime(DB_PATH) if os.path.exists(DB_PATH) else 0}.db"
        dest = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            title="Salvar backup como...",
            initialfile="agenda_backup.db"
        )
        if not dest:
            return

        try:
            shutil.copy2(DB_PATH, dest)
            from datetime import datetime
            now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            set_setting("last_backup", now_str)
            self._update_status()
            messagebox.showinfo("Sucesso", f"Backup salvo em:\n{dest}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar:\n{e}")

    def _import(self):
        src = filedialog.askopenfilename(
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            title="Selecionar arquivo de backup"
        )
        if not src:
            return

        if not messagebox.askyesno(
            "Confirmar",
            "Tem certeza? Todos os dados atuais serão substituídos!"
        ):
            return

        if not messagebox.askyesno(
            "Confirmação final",
            "Esta ação é irreversível. Deseja continuar?"
        ):
            return

        try:
            self.app.notif_mgr.stop()
            src_path = str(src)
            dest_path = str(DB_PATH)
            shutil.copy2(src_path, dest_path)
            from datetime import datetime
            now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            set_setting("last_backup", now_str)
            self._update_status()
            messagebox.showinfo("Sucesso", "Banco de dados restaurado com sucesso!")
            self.app.refresh_all()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao importar:\n{e}")

    def refresh(self):
        self._update_status()
