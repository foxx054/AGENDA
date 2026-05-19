import tkinter as tk
from tkinter import ttk, messagebox
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import get_setting, set_setting, get_all_contacts


class EmailSenderView(tk.Frame):
    def __init__(self, parent, app, colors):
        super().__init__(parent, bg=colors["bg"])
        self.app = app
        self.C = colors
        self._smtp_visible = False
        self._build_ui()

    def _build_ui(self):
        main = tk.Frame(self, bg=self.C["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=16)

        tk.Label(
            main, text="Envio de E-mail",
            font=("Segoe UI", 20, "bold"),
            bg=self.C["bg"], fg=self.C["text"]
        ).pack(anchor="w", pady=(0, 20))

        # SMTP config - collapsible header
        self.smtp_header = tk.Frame(main, bg=self.C["surface"], cursor="hand2")
        self.smtp_header.pack(fill="x", pady=(0, 2))
        self.smtp_header.bind("<Button-1>", lambda e: self._toggle_smtp())

        self.smtp_arrow = tk.Label(
            self.smtp_header, text="\u25b6 Configurar SMTP",
            font=("Segoe UI", 13, "bold"),
            bg=self.C["surface"], fg=self.C["text"]
        )
        self.smtp_arrow.pack(anchor="w", padx=16, pady=10)

        self.smtp_body = tk.Frame(main, bg=self.C["surface"])
        self._build_smtp_form()

        # Separator
        tk.Frame(main, bg=self.C["border"], height=1).pack(fill="x", pady=(10, 12))

        # Compose section
        tk.Label(
            main, text="Compor Mensagem",
            font=("Segoe UI", 16, "bold"),
            bg=self.C["bg"], fg=self.C["text"]
        ).pack(anchor="w", pady=(0, 12))

        # Para
        tk.Label(main, text="Para:", font=("Segoe UI", 11, "bold"),
                 bg=self.C["bg"], fg=self.C["text"]).pack(anchor="w")

        self.to_var = tk.StringVar()
        self.to_combo = ttk.Combobox(
            main, textvariable=self.to_var,
            width=50, font=("Segoe UI", 11)
        )
        self.to_combo.pack(fill="x", pady=(2, 10))
        self._populate_contacts()

        # Assunto
        tk.Label(main, text="Assunto:", font=("Segoe UI", 11, "bold"),
                 bg=self.C["bg"], fg=self.C["text"]).pack(anchor="w")
        ef = tk.Frame(main, bg=self.C["border"], bd=0)
        ef.pack(fill="x", pady=(2, 10))
        self.subject_entry = tk.Entry(
            ef, font=("Segoe UI", 12),
            bg=self.C["surface"], fg=self.C["text"],
            relief="flat", bd=0
        )
        self.subject_entry.pack(fill="x", ipady=2)

        # Mensagem
        tk.Label(main, text="Mensagem:", font=("Segoe UI", 11, "bold"),
                 bg=self.C["bg"], fg=self.C["text"]).pack(anchor="w")
        tf = tk.Frame(main, bg=self.C["border"], bd=0)
        tf.pack(fill="both", expand=True, pady=(2, 10))
        self.msg_text = tk.Text(
            tf, height=8, font=("Segoe UI", 11),
            bg=self.C["surface"], fg=self.C["text"],
            relief="flat", bd=0
        )
        self.msg_text.pack(fill="both", expand=True)

        # Send button
        self.send_btn = tk.Button(
            main, text="Enviar",
            font=("Segoe UI", 12, "bold"),
            bg=self.C["accent"], fg="white",
            relief="flat", bd=0, padx=24, pady=10,
            cursor="hand2", command=self._send
        )
        self.send_btn.pack(anchor="w")

        self.status_label = tk.Label(
            main, text="", font=("Segoe UI", 10),
            bg=self.C["bg"], fg="#34C759"
        )
        self.status_label.pack(anchor="w", pady=(6, 0))

    def _build_smtp_form(self):
        body = self.smtp_body
        form = tk.Frame(body, bg=self.C["surface"])
        form.pack(fill="x", padx=16, pady=(0, 12))

        fields = [
            ("Servidor SMTP", "smtp_server"),
            ("Porta", "smtp_port"),
            ("Usu\u00e1rio", "smtp_user"),
            ("Senha", "smtp_password"),
        ]
        self.smtp_entries = {}
        for label, key in fields:
            tk.Label(form, text=label, font=("Segoe UI", 10, "bold"),
                     bg=self.C["surface"], fg=self.C["text"]).pack(anchor="w")
            ef = tk.Frame(form, bg=self.C["border"], bd=0)
            ef.pack(fill="x", pady=(2, 8))
            entry = tk.Entry(
                ef, font=("Segoe UI", 11),
                bg=self.C["surface"], fg=self.C["text"],
                relief="flat", bd=0
            )
            entry.pack(fill="x", ipady=2)
            if key == "smtp_password":
                entry.config(show="*")
            self.smtp_entries[key] = entry

        tk.Button(
            form, text="Salvar",
            font=("Segoe UI", 11, "bold"),
            bg=self.C["accent"], fg="white",
            relief="flat", bd=0, padx=16, pady=6,
            cursor="hand2", command=self._save_smtp
        ).pack(anchor="w")

    def _toggle_smtp(self):
        self._smtp_visible = not self._smtp_visible
        if self._smtp_visible:
            self.smtp_body.pack(fill="x", pady=(0, 2))
            self.smtp_arrow.config(text="\u25bc Configurar SMTP")
            self._load_smtp()
        else:
            self.smtp_body.pack_forget()
            self.smtp_arrow.config(text="\u25b6 Configurar SMTP")

    def _load_smtp(self):
        self.smtp_entries["smtp_server"].delete(0, "end")
        self.smtp_entries["smtp_server"].insert(0, get_setting("smtp_server", ""))
        self.smtp_entries["smtp_port"].delete(0, "end")
        self.smtp_entries["smtp_port"].insert(0, get_setting("smtp_port", "587"))
        self.smtp_entries["smtp_user"].delete(0, "end")
        self.smtp_entries["smtp_user"].insert(0, get_setting("smtp_user", ""))
        self.smtp_entries["smtp_password"].delete(0, "end")
        self.smtp_entries["smtp_password"].insert(0, get_setting("smtp_password", ""))

    def _save_smtp(self):
        set_setting("smtp_server", self.smtp_entries["smtp_server"].get().strip())
        set_setting("smtp_port", self.smtp_entries["smtp_port"].get().strip())
        set_setting("smtp_user", self.smtp_entries["smtp_user"].get().strip())
        set_setting("smtp_password", self.smtp_entries["smtp_password"].get().strip())
        self.status_label.config(text="Configura\u00e7\u00f5es SMTP salvas!")
        self.after(3000, lambda: self.status_label.config(text=""))

    def _populate_contacts(self):
        contacts = get_all_contacts()
        emails = []
        for c in contacts:
            if c.get("email"):
                emails.append(f"{c['name']} <{c['email']}>")
        self.to_combo["values"] = emails

    def _send(self):
        to_raw = self.to_var.get().strip()
        if not to_raw:
            messagebox.showwarning("Aviso", "Informe o destinat\u00e1rio.")
            return
        if "<" in to_raw and ">" in to_raw:
            to_email = to_raw.split("<")[1].split(">")[0].strip()
        else:
            to_email = to_raw

        subject = self.subject_entry.get().strip()
        if not subject:
            messagebox.showwarning("Aviso", "Informe o assunto.")
            return

        body = self.msg_text.get("1.0", "end-1c").strip()
        if not body:
            messagebox.showwarning("Aviso", "Escreva uma mensagem.")
            return

        server = get_setting("smtp_server", "")
        port_str = get_setting("smtp_port", "587")
        user = get_setting("smtp_user", "")
        password = get_setting("smtp_password", "")

        if not server or not user or not password:
            messagebox.showwarning("Aviso", "Configure o SMTP primeiro.")
            return

        try:
            port = int(port_str)
        except ValueError:
            port = 587

        try:
            msg = MIMEMultipart()
            msg["From"] = user
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))

            context = ssl.create_default_context()
            with smtplib.SMTP(server, port) as smtp:
                smtp.starttls(context=context)
                smtp.login(user, password)
                smtp.send_message(msg)

            messagebox.showinfo("Sucesso", "E-mail enviado com sucesso!")
            self.subject_entry.delete(0, "end")
            self.msg_text.delete("1.0", "end")
        except smtplib.SMTPAuthenticationError:
            messagebox.showerror(
                "Erro", "Falha de autentica\u00e7\u00e3o. Verifique usu\u00e1rio/senha."
            )
        except (smtplib.SMTPConnectError, ConnectionRefusedError):
            messagebox.showerror(
                "Erro",
                "N\u00e3o foi poss\u00edvel conectar ao servidor SMTP. "
                "Verifique servidor e porta."
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao enviar e-mail:\n{e}")

    def refresh(self):
        self._populate_contacts()
