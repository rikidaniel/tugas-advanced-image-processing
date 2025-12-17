import tkinter as tk
from tkinter import ttk
from styles import COLORS, FONTS


class BaseFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        self.grid(row=0, column=0, sticky="nsew")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # --- SCROLLABLE CONTAINER ---
        self.main_scroll_canvas = tk.Canvas(self, bg=COLORS["bg_main"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.main_scroll_canvas.yview)

        # Link scrollbar to canvas
        self.main_scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Place widgets
        self.main_scroll_canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Container Frame INSIDE Canvas
        self.scrollable_content = ttk.Frame(self.main_scroll_canvas, style="Main.TFrame")

        # Window in canvas
        self.canvas_window = self.main_scroll_canvas.create_window(
            (0, 0), window=self.scrollable_content, anchor="nw"
        )

        # Bind events
        self.scrollable_content.bind("<Configure>", self._on_frame_configure)
        self.main_scroll_canvas.bind("<Configure>", self._on_canvas_configure)

        # Enable mousewheel scrolling
        self.bind_all("<MouseWheel>", self._on_mousewheel)

        # --- GRID LAYOUT FOR THE INNER CONTENT ---
        self.scrollable_content.columnconfigure(0, weight=1)
        self.scrollable_content.columnconfigure(1, weight=30)  # Main Content Wider
        self.scrollable_content.columnconfigure(2, weight=1)
        self.scrollable_content.rowconfigure(0, weight=0)  # Top Spacer
        self.scrollable_content.rowconfigure(1, weight=1)  # Content

        # Kartu Putih (Container Utama)
        # [UBAH] Padding dikurangi drastis (pady=30 -> 10, padx=10 -> 5)
        self.card = ttk.Frame(self.scrollable_content, style="Card.TFrame")
        self.card.grid(row=1, column=1, sticky="nsew", pady=10, padx=5)

        # Grid di dalam kartu
        self.card.columnconfigure(0, weight=1)
        self.card.rowconfigure(1, weight=1)

    def _on_frame_configure(self, event=None):
        """Update scroll region to match content size"""
        self.main_scroll_canvas.configure(scrollregion=self.main_scroll_canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        """Ensure inner frame matches canvas width"""
        canvas_width = event.width
        self.main_scroll_canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _on_mousewheel(self, event):
        """Scroll with mousewheel"""
        if self.main_scroll_canvas.winfo_height() < self.scrollable_content.winfo_height():
            self.main_scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_header(self, title, subtitle):
        # Header Area
        # [UBAH] Padding Header dikurangi (padx=40->20, pady=(40,20)->(20,10))
        header_frame = ttk.Frame(self.card, style="Card.TFrame")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        # Judul & Subjudul
        lbl_title = ttk.Label(header_frame, text=title, style="H1.TLabel")
        lbl_title.pack(anchor="w")

        lbl_sub = ttk.Label(header_frame, text=subtitle, style="Body.TLabel")
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # Accent Line under text
        accent_line = tk.Frame(header_frame, bg=COLORS["active_indicator"], height=3, width=60)
        accent_line.pack(anchor="w", pady=(10, 0))

        # Garis pemisah halus
        sep = tk.Frame(header_frame, bg=COLORS["border"], height=1)
        sep.pack(fill="x", pady=(15, 0))

        # Area Konten Spesifik Program
        # [UBAH] Padding Content dikurangi (padx=40->20, pady=(10,40)->(5,20))
        content_frame = ttk.Frame(self.card, style="Card.TFrame")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(5, 20))
        return content_frame