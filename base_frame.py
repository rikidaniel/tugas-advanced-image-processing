import tkinter as tk
from tkinter import ttk
from styles import COLORS, FONTS


class BaseFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        self.grid(row=0, column=0, sticky="nsew")

        # Grid layout untuk memusatkan kartu di tengah
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=30)  # Area konten utama lebih lebar
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)  # Spacer atas
        self.rowconfigure(1, weight=20)  # Konten
        self.rowconfigure(2, weight=1)  # Spacer bawah

        # Kartu Putih (Container Utama)
        self.card = ttk.Frame(self, style="Card.TFrame")
        self.card.grid(row=1, column=1, sticky="nsew", pady=20)

        # Grid di dalam kartu
        self.card.columnconfigure(0, weight=1)
        self.card.rowconfigure(1, weight=1)

    def create_header(self, title, subtitle):
        # Header Area
        header_frame = ttk.Frame(self.card, style="Card.TFrame")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 10))

        # Dekorasi garis hijau kecil di atas judul
        deco_line = tk.Frame(header_frame, bg=COLORS["primary"], height=4, width=50)
        deco_line.pack(anchor="w", pady=(0, 10))

        # Judul & Subjudul
        ttk.Label(header_frame, text=title, style="H1.TLabel").pack(anchor="w")
        ttk.Label(header_frame, text=subtitle, style="Body.TLabel").pack(anchor="w", pady=(5, 0))

        # Garis pemisah halus
        sep = tk.Frame(header_frame, bg="#E5E7EB", height=1)
        sep.pack(fill="x", pady=(20, 0))

        # Area Konten Spesifik Program
        content_frame = ttk.Frame(self.card, style="Card.TFrame")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=(10, 30))
        return content_frame