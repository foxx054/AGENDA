import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from database import (
    add_contact, update_contact, delete_contact,
    get_all_contacts, search_contacts
)


class ContactsView(tk.Frame):
    def __init__(self, parent, app, colors):
        super().__init__(parent, bg=colors["bg"])
        self.app = app
        self.C = colors
        self._build_ui()

    def _build_ui(self):
        search_frame = tk.Frame(self, bg=self.C["surface"])
        search_frame.pack(fill="x", padx=20, pady=16)

        tk.Label(
            search_frame, text="Contatos",
            font=("Segoe UI", 20, "bold"), bg=self.C["surface"], fg=self.C["text"]
        ).pack(anchor="w")

        entry_frame = tk.Frame(search_frame, bg=self.C["border"], bd=0)
        entry_frame.pack(fill="x", pady=(8, 0))

        self.search_entry = tk.Entry(
            entry_frame, font=("Segoe UI", 12),
            bg="#F5F5F7", fg=self.C["text"],
            relief="flat", bd=0
        )
        self.search_entry.pack(fill="x", ipady=4)
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter())

        btn_row = tk.Frame(search_frame, bg=self.C["surface"])
        btn_row.pack(fill="x", pady=(10, 0))

        tk.Button(
            btn_row, text="+ Novo Contato",
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
        self._filter()

    def _filter(self):
        query = self.search_entry.get().strip()
        if query:
            contacts = search_contacts(query)
        else:
            contacts = get_all_contacts()
        self._render(contacts)

    def _render(self, contacts):
        for w in self.scrollable.winfo_children():
            w.destroy()

        if not contacts:
            empty = tk.Frame(
                self.scrollable, bg=self.C["surface"],
                highlightthickness=1, highlightbackground=self.C["border"]
            )
            empty.pack(fill="x", pady=20, padx=20)
            tk.Label(
                empty, text="Nenhum contato encontrado",
                font=("Segoe UI", 13), bg=self.C["surface"], fg=self.C["text_sec"]
            ).pack(pady=24)
            return

        for c in contacts:
            card = tk.Frame(
                self.scrollable, bg=self.C["surface"],
                highlightthickness=1, highlightbackground=self.C["border"]
            )
            card.pack(fill="x", pady=2, padx=20)

            body = tk.Frame(card, bg=self.C["surface"])
            body.pack(fill="x", padx=14, pady=10)

            tk.Label(
                body, text=c["name"],
                font=("Segoe UI", 13, "bold"),
                bg=self.C["surface"], fg=self.C["text"]
            ).pack(anchor="w")

            meta = tk.Frame(body, bg=self.C["surface"])
            meta.pack(anchor="w", pady=(2, 0))

            info_parts = []
            if c.get("phone"):
                info_parts.append(f"📞 {c['phone']}")
            if c.get("email"):
                info_parts.append(f"📧 {c['email']}")
            if c.get("birthday"):
                info_parts.append(f"🎂 {c['birthday']}")
            if info_parts:
                tk.Label(
                    meta, text="  ".join(info_parts),
                    font=("Segoe UI", 10), bg=self.C["surface"], fg=self.C["text_sec"]
                ).pack(anchor="w")

            btn_frame = tk.Frame(card, bg=self.C["surface"])
            btn_frame.pack(fill="x", padx=14, pady=(0, 8))

            tk.Button(
                btn_frame, text="Editar",
                font=("Segoe UI", 9), bg=self.C["surface"], fg=self.C["accent"],
                relief="flat", bd=0, cursor="hand2",
                command=lambda cid=c["id"]: self._edit(cid)
            ).pack(side="left", padx=(0, 8))

            tk.Button(
                btn_frame, text="Excluir",
                font=("Segoe UI", 9), bg=self.C["surface"], fg="#FF3B30",
                relief="flat", bd=0, cursor="hand2",
                command=lambda cid=c["id"]: self._delete(cid)
            ).pack(side="left")

    def _add(self):
        ContactDialog(self, self.C, on_save=lambda c: self.refresh())

    def _edit(self, contact_id):
        ContactDialog(self, self.C, contact_id=contact_id, on_save=lambda c: self.refresh())

    def _delete(self, contact_id):
        if messagebox.askyesno("Excluir", "Excluir este contato?"):
            delete_contact(contact_id)
            self.refresh()


class ContactDialog(tk.Toplevel):
    def __init__(self, parent, colors, contact_id=None, on_save=None):
        super().__init__(parent)
        self.C = colors
        self.contact_id = contact_id
        self.on_save = on_save
        self.contact = None
        if contact_id:
            from database import get_all_contacts
            for c in get_all_contacts():
                if c["id"] == contact_id:
                    self.contact = c
                    break

        self.title("Editar Contato" if self.contact else "Novo Contato")
        self.geometry("420x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self._build_form()

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 210
        y = (self.winfo_screenheight() // 2) - 200
        self.geometry(f"+{x}+{y}")

    def _build_form(self):
        bg = self.C["bg"]
        surface = self.C["surface"]
        text = self.C["text"]
        text_sec = self.C["text_sec"]
        border = self.C["border"]

        main = tk.Frame(self, bg=bg)
        main.pack(fill="both", expand=True, padx=24, pady=20)

        fields = [
            ("Nome", "name", True),
            ("Telefone", "phone", False),
            ("Email", "email", False),
            ("Tags", "tags", False),
            ("Aniversário (AAAA-MM-DD)", "birthday", False),
        ]

        self.entries = {}
        for label, key, required in fields:
            tk.Label(main, text=label, font=("Segoe UI", 10, "bold"),
                     bg=bg, fg=text).pack(anchor="w", pady=(6, 2))
            ef = tk.Frame(main, bg=border, bd=0)
            ef.pack(fill="x")
            entry = tk.Entry(
                ef, font=("Segoe UI", 12),
                bg=surface, fg=text, relief="flat", bd=0
            )
            entry.pack(fill="x", ipady=2)
            if self.contact and self.contact.get(key):
                entry.insert(0, self.contact[key])
            self.entries[key] = entry

        # Notes
        tk.Label(main, text="Notas", font=("Segoe UI", 10, "bold"),
                 bg=bg, fg=text).pack(anchor="w", pady=(6, 2))
        nf = tk.Frame(main, bg=border, bd=0)
        nf.pack(fill="x")
        self.notes_text = tk.Text(
            nf, height=3, font=("Segoe UI", 11),
            bg=surface, fg=text, relief="flat", bd=0
        )
        self.notes_text.pack(fill="x")
        if self.contact and self.contact.get("notes"):
            self.notes_text.insert("1.0", self.contact["notes"])

        btn_frame = tk.Frame(main, bg=bg)
        btn_frame.pack(fill="x", pady=(14, 0))

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

    def _save(self):
        name = self.entries["name"].get().strip()
        if not name:
            messagebox.showwarning("Atenção", "Nome é obrigatório.")
            return

        data = {
            "name": name,
            "phone": self.entries["phone"].get().strip(),
            "email": self.entries["email"].get().strip(),
            "tags": self.entries["tags"].get().strip(),
            "birthday": self.entries["birthday"].get().strip(),
            "notes": self.notes_text.get("1.0", "end-1c").strip(),
        }

        if self.contact:
            data["id"] = self.contact["id"]
            update_contact(data)
        else:
            add_contact(data)

        if self.on_save:
            self.on_save(data)
        self.destroy()
