import tkinter as tk
from tkinter import ttk
from styles import apply_theme, COLORS, FONTS

from image_view import ImageViewerApp
from mach_and_band_effect import MachBandApp
from program3_single_pixel import SinglePixelApp
from dft_explorer import DftApp
from frequency_filters import FrequencyFilterApp
from spatial_segmentation import SpatialSegmentationApp
from resolution_histogram import ResHistApp
from arithmetic_operations import ArithmeticApp


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Aplikasi Pengolahan Citra Digital")
        self.geometry("1400x900") # Start a bit larger
        self.state("zoomed")

        self.style = apply_theme(self)
        self.configure(bg=COLORS["sidebar_bg"])

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (KIRI) ---
        self.sidebar = tk.Frame(self, bg=COLORS["sidebar_bg"], width=300)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        # Logo / Judul Sidebar
        logo_area = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        logo_area.pack(fill="x", padx=30, pady=(60, 40))

        tk.Label(logo_area, text="IMAGE", bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_fg"],
                 font=("Segoe UI", 24, "bold"), anchor="w").pack(fill="x")
        tk.Label(logo_area, text="PROCESSING", bg=COLORS["sidebar_bg"], fg=COLORS["primary"],
                 font=("Segoe UI", 24, "bold"), anchor="w").pack(fill="x")
        tk.Label(logo_area, text="DASHBOARD v2.0", bg=COLORS["sidebar_bg"], fg="#CFD8CC",
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x", pady=(8, 0))

        # Menu
        self.menu_container = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        self.menu_container.pack(fill="both", expand=True, padx=0) # Full width items

        self.menus = [
            ("01", "Penampil Citra", ImageViewerApp),
            ("02", "Mach Band Effect", MachBandApp),
            ("03", "Image Enhancement", SinglePixelApp),
            ("04", "DFT Explorer", DftApp),
            ("05", "Filter Frekuensi", FrequencyFilterApp),
            ("06", "Spatial & Segmentation", SpatialSegmentationApp),
            ("07", "Resolution & Histogram", ResHistApp),
            ("08", "Arithmetic & Logic", ArithmeticApp)
        ]

        self.btn_refs = []
        for code, name, frame_class in self.menus:
            self.create_menu_btn(code, name, frame_class)

        # Footer (Info Mahasiswa)
        footer = tk.Frame(self.sidebar, bg="#2C3E32", height=120) 
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)

        # Divider
        tk.Frame(footer, bg="#4F6D54", height=1).pack(fill="x", side="top")

        tk.Label(footer, text="Riki Daniel Tanebeth", bg="#2C3E32", fg="white",
                 font=("Segoe UI", 11, "bold")).pack(side="top", anchor="w", padx=30, pady=(30, 2))
        tk.Label(footer, text="NIM: 14240032", bg="#2C3E32", fg=COLORS["primary"],
                 font=("Segoe UI", 10)).pack(side="top", anchor="w", padx=30)

        # --- CONTENT AREA (KANAN) ---
        self.content_area = ttk.Frame(self, style="Main.TFrame")
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        self.current_frame = None
        
        # Select first item by default
        if self.btn_refs:
            self.switch_frame(ImageViewerApp, self.btn_refs[0])

    def create_menu_btn(self, code, name, frame_class):
        # Increased height for better touch/click area
        btn_frame = tk.Frame(self.menu_container, bg=COLORS["sidebar_bg"], cursor="hand2", height=65)
        btn_frame.pack(fill="x", pady=1)
        btn_frame.pack_propagate(False)

        # Indikator (Garis kiri)
        indicator = tk.Frame(btn_frame, bg=COLORS["sidebar_bg"], width=6)
        indicator.pack(side="left", fill="y")

        # Container for text to center vertically
        text_frame = tk.Frame(btn_frame, bg=COLORS["sidebar_bg"])
        text_frame.pack(side="left", fill="both", expand=True, padx=(20, 10))

        # Teks
        # lbl_code = tk.Label(text_frame, text=code, font=("Segoe UI", 10, "bold"),
        #                     bg=COLORS["sidebar_bg"], fg="#64748B")
        # lbl_code.pack(side="left", padx=(0, 15))

        lbl_name = tk.Label(text_frame, text=name, font=("Segoe UI", 11),
                            bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_fg"])
        lbl_name.pack(side="left", anchor="center")

        # Binding Event
        # Bind to frame and all children
        for w in (btn_frame, indicator, text_frame, lbl_name):
            w.bind("<Button-1>", lambda e: self.switch_frame(frame_class, btn_frame))

        btn_frame.indicator = indicator
        # btn_frame.lbl_code = lbl_code
        btn_frame.lbl_name = lbl_name
        btn_frame.text_frame = text_frame
        self.btn_refs.append(btn_frame)

    def switch_frame(self, frame_class, active_btn):
        if self.current_frame:
            self.current_frame.destroy()

        # Update Visual Tombol
        for btn in self.btn_refs:
            is_active = (btn == active_btn)
            bg = COLORS["active_bg"] if is_active else COLORS["sidebar_bg"]
            ind_bg = COLORS["active_indicator"] if is_active else bg
            fg_name = "white" if is_active else COLORS["sidebar_fg"]
            font_weight = "bold" if is_active else "normal"

            btn.config(bg=bg)
            btn.text_frame.config(bg=bg)
            btn.indicator.config(bg=ind_bg)
            # btn.lbl_code.config(bg=bg)
            btn.lbl_name.config(bg=bg, fg=fg_name, font=("Segoe UI", 11, font_weight))

        self.current_frame = frame_class(self.content_area)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()