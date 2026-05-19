import tkinter as tk
import time


class StopwatchView(tk.Frame):
    def __init__(self, parent, app, colors):
        super().__init__(parent, bg=colors["bg"])
        self.app = app
        self.C = colors
        self._running = False
        self._start_time = 0.0
        self._elapsed = 0.0
        self._build_ui()

    def _build_ui(self):
        center = tk.Frame(self, bg=self.C["bg"])
        center.place(relx=0.5, rely=0.45, anchor="center")

        self.time_label = tk.Label(
            center, text="00:00:00.000",
            font=("Segoe UI", 48, "bold"),
            bg=self.C["bg"], fg=self.C["text"]
        )
        self.time_label.pack(pady=(0, 40))

        btn_frame = tk.Frame(center, bg=self.C["bg"])
        btn_frame.pack()

        self.start_btn = tk.Button(
            btn_frame, text="Iniciar",
            font=("Segoe UI", 14, "bold"),
            bg=self.C["accent"], fg="white",
            relief="flat", bd=0, padx=24, pady=10,
            cursor="hand2", command=self._start
        )
        self.start_btn.pack(side="left", padx=(0, 10))

        self.pause_btn = tk.Button(
            btn_frame, text="Pausar",
            font=("Segoe UI", 14, "bold"),
            bg="#FF9500", fg="white",
            relief="flat", bd=0, padx=20, pady=10,
            cursor="hand2", command=self._pause
        )
        self.pause_btn.pack(side="left", padx=(0, 10))

        self.reset_btn = tk.Button(
            btn_frame, text="Resetar",
            font=("Segoe UI", 14, "bold"),
            bg="#FF3B30", fg="white",
            relief="flat", bd=0, padx=20, pady=10,
            cursor="hand2", command=self._reset
        )
        self.reset_btn.pack(side="left")

    def _start(self):
        if not self._running:
            self._start_time = time.time()
            self._running = True
            self._tick()

    def _pause(self):
        if self._running:
            self._elapsed += time.time() - self._start_time
            self._running = False

    def _reset(self):
        self._running = False
        self._elapsed = 0.0
        self._update_display()

    def _tick(self):
        if self._running:
            self._update_display()
            self.after(50, self._tick)

    def _update_display(self):
        total = self._elapsed
        if self._running:
            total += time.time() - self._start_time
        total_ms = int(total * 1000)
        hours = total_ms // 3600000
        remainder = total_ms % 3600000
        minutes = remainder // 60000
        seconds = (remainder % 60000) // 1000
        ms = remainder % 1000
        self.time_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}.{ms:03d}")

    def refresh(self):
        pass
