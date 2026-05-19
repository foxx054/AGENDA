import tkinter as tk
from tkinter import messagebox, simpledialog
from database import (
    add_note, update_note, delete_note,
    get_all_notes, get_note_by_id
)


class NotesView(tk.Frame):
    def __init__(self, parent, app, colors):
        super().__init__(parent, bg=colors["bg"])
        self.app = app
        self.C = colors
        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self, bg=self.C["surface"])
        header.pack(fill="x", padx=20, pady=16)

        tk.Label(
            header, text="Anotações",
            font=("Segoe UI", 20, "bold"), bg=self.C["surface"], fg=self.C["text"]
        ).pack(anchor="w")

        btn_row = tk.Frame(header, bg=self.C["surface"])
        btn_row.pack(fill="x", pady=(8, 0))

        tk.Button(
            btn_row, text="+ Nova Anotação",
            font=("Segoe UI", 11, "bold"),
            bg=self.C["accent"], fg="white",
            relief="flat", bd=0, padx=14, pady=6,
            cursor="hand2", command=self._add
        ).pack(side="left")

        container = tk.Frame(self, bg=self.C["bg"])
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.canvas = tk.Canvas(container, bg=self.C["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable = tk.Frame(self.canvas, bg=self.C["bg"])

        self.scrollable.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh(self):
        for w in self.scrollable.winfo_children():
            w.destroy()

        notes = get_all_notes()

        if not notes:
            empty = tk.Frame(
                self.scrollable, bg=self.C["surface"],
                highlightthickness=1, highlightbackground=self.C["border"]
            )
            empty.pack(fill="x", pady=20, padx=20)
            tk.Label(
                empty, text="Nenhuma anotação encontrada",
                font=("Segoe UI", 13), bg=self.C["surface"], fg=self.C["text_sec"]
            ).pack(pady=24)
            return

        for n in notes:
            card = tk.Frame(
                self.scrollable, bg=self.C["surface"],
                highlightthickness=1, highlightbackground=self.C["border"]
            )
            card.pack(fill="x", pady=2, padx=20)

            body = tk.Frame(card, bg=self.C["surface"])
            body.pack(fill="x", padx=14, pady=10)

            title_row = tk.Frame(body, bg=self.C["surface"])
            title_row.pack(fill="x")

            secret_tag = "🔒 " if n.get("is_secret") else ""
            tk.Label(
                title_row, text=f"{secret_tag}{n['title']}",
                font=("Segoe UI", 13, "bold"),
                bg=self.C["surface"], fg=self.C["text"], anchor="w"
            ).pack(side="left", fill="x", expand=True)

            preview = n.get("content", "")[:80].replace("\n", " ")
            if preview:
                tk.Label(
                    body, text=preview,
                    font=("Segoe UI", 10), bg=self.C["surface"],
                    fg=self.C["text_sec"], anchor="w"
                ).pack(fill="x", pady=(2, 4))

            btn_frame = tk.Frame(card, bg=self.C["surface"])
            btn_frame.pack(fill="x", padx=14, pady=(0, 8))

            tk.Button(
                btn_frame, text="Abrir",
                font=("Segoe UI", 9), bg=self.C["surface"], fg=self.C["accent"],
                relief="flat", bd=0, cursor="hand2",
                command=lambda nid=n["id"]: self._open(nid)
            ).pack(side="left", padx=(0, 8))

            tk.Button(
                btn_frame, text="Editar",
                font=("Segoe UI", 9), bg=self.C["surface"], fg=self.C["accent"],
                relief="flat", bd=0, cursor="hand2",
                command=lambda nid=n["id"]: self._edit(nid)
            ).pack(side="left", padx=(0, 8))

            tk.Button(
                btn_frame, text="Excluir",
                font=("Segoe UI", 9), bg=self.C["surface"], fg="#FF3B30",
                relief="flat", bd=0, cursor="hand2",
                command=lambda nid=n["id"]: self._delete(nid)
            ).pack(side="left")

    def _add(self):
        NoteEditorDialog(self, self.C, on_save=lambda: self.refresh())

    def _edit(self, note_id):
        note = get_note_by_id(note_id)
        if not note:
            return
        if note.get("is_secret"):
            pwd = simpledialog.askstring("Senha", "Digite a senha:", show="*")
            if pwd != note.get("password"):
                messagebox.showerror("Erro", "Senha incorreta!")
                return
        NoteEditorDialog(self, self.C, note=note, on_save=lambda: self.refresh())

    def _open(self, note_id):
        note = get_note_by_id(note_id)
        if not note:
            return
        if note.get("is_secret"):
            pwd = simpledialog.askstring("Senha", "Digite a senha:", show="*")
            if pwd != note.get("password"):
                messagebox.showerror("Erro", "Senha incorreta!")
                return
        NoteViewerDialog(self, self.C, note=note, on_save=lambda: self.refresh())

    def _delete(self, note_id):
        if messagebox.askyesno("Excluir", "Excluir esta anotação?"):
            delete_note(note_id)
            self.refresh()


class NoteEditorDialog(tk.Toplevel):
    def __init__(self, parent, colors, note=None, on_save=None):
        super().__init__(parent)
        self.C = colors
        self.note = note
        self.on_save = on_save

        self.title("Editar Anotação" if note else "Nova Anotação")
        self.geometry("500x450")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self._build_form()

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 250
        y = (self.winfo_screenheight() // 2) - 225
        self.geometry(f"+{x}+{y}")

    def _build_form(self):
        bg = self.C["bg"]
        surface = self.C["surface"]
        text = self.C["text"]
        text_sec = self.C["text_sec"]
        border = self.C["border"]

        main = tk.Frame(self, bg=bg)
        main.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(main, text="Título", font=("Segoe UI", 10, "bold"),
                 bg=bg, fg=text).pack(anchor="w")
        tf = tk.Frame(main, bg=border, bd=0)
        tf.pack(fill="x", pady=(0, 10))
        self.title_entry = tk.Entry(
            tf, font=("Segoe UI", 14),
            bg=surface, fg=text, relief="flat", bd=0
        )
        self.title_entry.pack(fill="x", ipady=2)
        if self.note:
            self.title_entry.insert(0, self.note["title"])
        else:
            self.title_entry.focus_set()

        tk.Label(main, text="Conteúdo", font=("Segoe UI", 10, "bold"),
                 bg=bg, fg=text).pack(anchor="w")
        cf = tk.Frame(main, bg=border, bd=0)
        cf.pack(fill="both", expand=True, pady=(0, 10))
        self.content_text = tk.Text(
            cf, font=("Segoe UI", 11),
            bg=surface, fg=text, relief="flat", bd=0
        )
        self.content_text.pack(fill="both", expand=True)
        if self.note and self.note.get("content"):
            self.content_text.insert("1.0", self.note["content"])

        # Secret toggle
        secret_frame = tk.Frame(main, bg=bg)
        secret_frame.pack(fill="x", pady=(0, 10))

        self.is_secret_var = tk.BooleanVar(value=self.note.get("is_secret", 0) if self.note else False)
        tk.Checkbutton(
            secret_frame, text="Anotação secreta (protegida por senha)",
            variable=self.is_secret_var, font=("Segoe UI", 10),
            bg=bg, fg=text, selectcolor="#E8F0FE",
            command=self._toggle_secret
        ).pack(side="left")

        self.pwd_frame = tk.Frame(main, bg=bg)
        tk.Label(
            self.pwd_frame, text="Senha:", font=("Segoe UI", 10),
            bg=bg, fg=text
        ).pack(side="left", padx=(0, 6))
        pf = tk.Frame(self.pwd_frame, bg=border, bd=0)
        pf.pack(side="left")
        self.password_entry = tk.Entry(
            pf, font=("Segoe UI", 11), show="*",
            bg=surface, fg=text, relief="flat", bd=0
        )
        self.password_entry.pack(fill="x", ipady=2)

        if self.is_secret_var.get():
            self.pwd_frame.pack(fill="x")
            if self.note and self.note.get("password"):
                self.password_entry.insert(0, self.note["password"])

        btn_frame = tk.Frame(main, bg=bg)
        btn_frame.pack(fill="x")

        tk.Button(
            btn_frame, text="Cancelar",
            font=("Segoe UI", 11), bg="white", fg=text_sec,
            relief="flat", bd=1, highlightbackground=border,
            padx=16, pady=6, cursor="hand2", command=self.destroy
        ).pack(side="right", padx=(6, 0))

        tk.Button(
            btn_frame, text="Salvar",
            font=("Segoe UI", 11, "bold"),
            bg=self.C["accent"], fg="white",
            relief="flat", bd=0, padx=16, pady=6, cursor="hand2",
            command=self._save
        ).pack(side="right")

    def _toggle_secret(self):
        if self.is_secret_var.get():
            self.pwd_frame.pack(fill="x", pady=(0, 10))
        else:
            self.pwd_frame.pack_forget()

    def _save(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Atenção", "O título é obrigatório.")
            return

        is_secret = 1 if self.is_secret_var.get() else 0
        password = self.password_entry.get().strip()

        if is_secret and not password and not (self.note and self.note.get("password")):
            messagebox.showwarning("Atenção", "Defina uma senha para anotações secretas.")
            return

        if is_secret and not password and self.note:
            password = self.note.get("password", "")

        data = {
            "title": title,
            "content": self.content_text.get("1.0", "end-1c").strip(),
            "is_secret": is_secret,
            "password": password,
        }

        if self.note:
            data["id"] = self.note["id"]
            update_note(data)
        else:
            add_note(data)

        if self.on_save:
            self.on_save()
        self.destroy()


class NoteViewerDialog(tk.Toplevel):
    def __init__(self, parent, colors, note=None, on_save=None):
        super().__init__(parent)
        self.C = colors
        self.note = note
        self.on_save = on_save

        self.title(note["title"] if note else "Anotação")
        self.geometry("500x450")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self._build_viewer()

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 250
        y = (self.winfo_screenheight() // 2) - 225
        self.geometry(f"+{x}+{y}")

    def _build_viewer(self):
        bg = self.C["bg"]
        surface = self.C["surface"]
        text = self.C["text"]
        text_sec = self.C["text_sec"]
        border = self.C["border"]

        main = tk.Frame(self, bg=bg)
        main.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(
            main, text=self.note["title"],
            font=("Segoe UI", 16, "bold"),
            bg=bg, fg=text
        ).pack(anchor="w")

        if self.note.get("is_secret"):
            tk.Label(
                main, text="🔒 Secreto",
                font=("Segoe UI", 10), bg=bg, fg="#FF9500"
            ).pack(anchor="w", pady=(2, 0))

        cf = tk.Frame(main, bg=border, bd=0)
        cf.pack(fill="both", expand=True, pady=(10, 12))
        viewer = tk.Text(
            cf, font=("Segoe UI", 11),
            bg=surface, fg=text, relief="flat", bd=0,
            wrap="word", state="normal"
        )
        viewer.pack(fill="both", expand=True)
        viewer.insert("1.0", self.note.get("content", ""))
        viewer.config(state="disabled")

        tk.Button(
            main, text="Fechar",
            font=("Segoe UI", 11), bg=self.C["accent"], fg="white",
            relief="flat", bd=0, padx=16, pady=6, cursor="hand2",
            command=self.destroy
        ).pack(anchor="e")
