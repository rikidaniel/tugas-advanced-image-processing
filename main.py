import tkinter as tk
from tkinter import ttk, messagebox
from styles import apply_theme, COLORS, FONTS

# Import semua modul
from image_view import ImageViewerApp
from mach_and_band_effect import MachBandApp
# from resolution_histogram import ResHistApp
from resolution_histogram import ResolutionApp, HistogramApp  # Ganti import lama (ResHistApp)
from program3_single_pixel import SinglePixelApp
from arithmetic_operations import ArithmeticApp
from spatial_segmentation import SpatialSegmentationApp
from dft_explorer import DftApp
from frequency_filters import FrequencyFilterApp
# [BARU] Import modul Segmentation
from image_segmentation import ImageSegmentationApp


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("TUGAS PENGOLAHAN CITRA DIGITAL - UTS")
        self.geometry("1300x850")
        self.state("zoomed")

        self.style = apply_theme(self)
        self.configure(bg=COLORS["sidebar_bg"])

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (KIRI) ---
        self.sidebar = tk.Frame(self, bg=COLORS["sidebar_bg"], width=300)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        # Logo / Header Sidebar
        logo_area = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        logo_area.pack(fill="x", padx=20, pady=(30, 20))

        tk.Label(logo_area, text="DIGITAL IMAGE", bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_fg"],
                 font=("Segoe UI", 20, "bold"), anchor="w").pack(fill="x")
        tk.Label(logo_area, text="PROCESSING", bg=COLORS["sidebar_bg"], fg=COLORS["primary"],
                 font=("Segoe UI", 20, "bold"), anchor="w").pack(fill="x")

        tk.Frame(self.sidebar, bg=COLORS["active_bg"], height=2).pack(fill="x", padx=20, pady=(0, 20))

        # Menu Container
        self.menu_container = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        self.menu_container.pack(fill="both", expand=True, padx=0)

        # [UPDATE] Daftar Menu
        # Import class baru (pastikan import ini ada di atas file main.py)
        # from resolution_histogram import ResolutionApp, HistogramApp

        # [REVISI URUTAN MENU SESUAI PDF]
        self.menus = [
            ("01", "Image Viewer", ImageViewerApp),
            ("02", "Visual Perception (Pg 1)", MachBandApp),
            ("03", "Spatial Res & Quant (Pg 1-2)", ResolutionApp),  # Class baru 1
            ("04", "Intensity Trans. (Pg 3-4)", SinglePixelApp),  # Sesuai PDF halaman 3-4
            ("05", "Histogram Proc. (Pg 5-7)", HistogramApp),  # Class baru 2
            ("06", "Arithmetic/Logic (Pg 7-10)", ArithmeticApp),
            ("07", "Spatial Filters (Pg 10-12)", SpatialSegmentationApp),
            ("08", "DFT Spectrum (Pg 13)", DftApp),
            ("09", "Freq Filtering (Pg 14-16)", FrequencyFilterApp),
            ("10", "Image Segmentation (Pg 17)", ImageSegmentationApp)
        ]
        self.btn_refs = []
        self.menu_map = {}

        for code, name, frame_class in self.menus:
            btn = self.create_menu_btn(code, name, frame_class)
            self.menu_map[frame_class] = btn

        # Footer Identitas
        footer = tk.Frame(self.sidebar, bg="#2C3E32", height=120)
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)
        tk.Frame(footer, bg="#4F6D54", height=1).pack(fill="x", side="top")

        tk.Label(footer, text="Created by:", bg="#2C3E32", fg="#aaa",
                 font=("Segoe UI", 9)).pack(side="top", anchor="w", padx=25, pady=(15, 0))
        tk.Label(footer, text="Riki Daniel Tanebeth", bg="#2C3E32", fg="white",
                 font=("Segoe UI", 12, "bold")).pack(side="top", anchor="w", padx=25)
        tk.Label(footer, text="NIM: 14240032", bg="#2C3E32", fg=COLORS["primary"],
                 font=("Segoe UI", 11)).pack(side="top", anchor="w", padx=25)

        # --- CONTENT AREA (KANAN) ---
        self.content_area = ttk.Frame(self, style="Main.TFrame")
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        self.current_frame = None

        if self.btn_refs:
            self.switch_frame(ImageViewerApp, self.btn_refs[0])

    def create_menu_btn(self, code, name, frame_class):
        btn_frame = tk.Frame(self.menu_container, bg=COLORS["sidebar_bg"], cursor="hand2", height=55)
        btn_frame.pack(fill="x", pady=1)
        btn_frame.pack_propagate(False)

        indicator = tk.Frame(btn_frame, bg=COLORS["sidebar_bg"], width=5)
        indicator.pack(side="left", fill="y")

        text_frame = tk.Frame(btn_frame, bg=COLORS["sidebar_bg"])
        text_frame.pack(side="left", fill="both", expand=True, padx=(15, 10))

        lbl_code = tk.Label(text_frame, text=code, font=("Segoe UI", 9),
                            bg=COLORS["sidebar_bg"], fg="#888", anchor="w")
        lbl_code.pack(side="top", fill="x", pady=(8, 0))

        lbl_name = tk.Label(text_frame, text=name, font=("Segoe UI", 10),
                            bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_fg"], anchor="w")
        lbl_name.pack(side="top", fill="x")

        for w in (btn_frame, indicator, text_frame, lbl_name, lbl_code):
            w.bind("<Button-1>", lambda e: self.switch_frame(frame_class, btn_frame))

        btn_frame.indicator = indicator
        btn_frame.lbl_name = lbl_name
        btn_frame.lbl_code = lbl_code
        btn_frame.text_frame = text_frame

        self.btn_refs.append(btn_frame)
        return btn_frame

    def switch_frame(self, frame_class, active_btn):
        if self.current_frame:
            self.current_frame.destroy()

        for btn in self.btn_refs:
            is_active = (btn == active_btn)
            bg = COLORS["active_bg"] if is_active else COLORS["sidebar_bg"]
            ind_bg = COLORS["active_indicator"] if is_active else bg
            fg_name = "white" if is_active else COLORS["sidebar_fg"]
            fg_code = COLORS["primary"] if is_active else "#888"
            font_weight = "bold" if is_active else "normal"

            btn.config(bg=bg)
            btn.text_frame.config(bg=bg)
            btn.indicator.config(bg=ind_bg)
            btn.lbl_name.config(bg=bg, fg=fg_name, font=("Segoe UI", 10, font_weight))
            btn.lbl_code.config(bg=bg, fg=fg_code)

        self.current_frame = frame_class(self.content_area)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()