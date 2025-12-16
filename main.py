import tkinter as tk
from tkinter import ttk, messagebox
from styles import apply_theme, COLORS, FONTS

# Import semua modul
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

        # [FINAL POLISH] Judul Aplikasi memuat Identitas Mahasiswa
        self.title("Aplikasi Pengolahan Citra Digital - Riki Daniel Tanebeth (14240032)")
        self.geometry("1400x900")
        self.state("zoomed")

        self.style = apply_theme(self)
        self.configure(bg=COLORS["sidebar_bg"])

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- DATABASE PENCARIAN (Mapping Keyword -> Menu & Instruksi) ---
        self.search_index = {
            "mach": (MachBandApp, "Buka Menu 02.\nKlik tombol 'Generate Mach Band'."),
            "bright": (MachBandApp, "Buka Menu 02.\nKlik tombol 'Brightness Adaptation'."),
            "resolu": (ResHistApp, "Buka Menu 07 (Tab 1).\nUbah dropdown 'Target Resolusi'."),
            "quantiz": (ResHistApp, "Buka Menu 07 (Tab 1).\nGeser slider 'Jumlah Level'."),
            "negat": (SinglePixelApp, "Buka Menu 03 (Tab 1).\nKlik tombol 'Image Negative'."),
            "gamma": (SinglePixelApp, "Buka Menu 03 (Tab 2).\nMainkan slider Gamma dan Constant."),
            "power": (SinglePixelApp, "Buka Menu 03 (Tab 2).\nFitur Power-Law adalah Gamma Correction."),
            "slicing": (SinglePixelApp, "Buka Menu 03 (Tab 3).\nMainkan slider Range A dan B."),
            "clahe": (ResHistApp, "Buka Menu 07 (Tab 2).\nKlik tombol 'Local Histogram Eq.'."),
            "local": (ResHistApp, "Buka Menu 07 (Tab 2).\nKlik tombol 'Local Histogram Eq.'."),
            "equal": (ResHistApp, "Buka Menu 07 (Tab 2).\nKlik tombol 'Global Histogram Eq.'."),
            "smooth": (SpatialSegmentationApp, "Buka Menu 06.\nPilih Kategori 'Smoothing'."),
            "sharp": (SpatialSegmentationApp, "Buka Menu 06.\nPilih Kategori 'Sharpening' (Laplacian)."),
            "laplac": (SpatialSegmentationApp, "Buka Menu 06.\nPilih Kategori 'Sharpening' -> Filter Laplacian."),
            "point": (SpatialSegmentationApp, "Buka Menu 06.\nPilih Kategori 'Segmentation' -> Point Detection."),
            "line": (SpatialSegmentationApp, "Buka Menu 06.\nPilih Kategori 'Segmentation' -> Line Detection."),
            "dft": (DftApp, "Buka Menu 04.\nKlik 'Apply Transform'."),
            "freq": (FrequencyFilterApp, "Buka Menu 05.\nPilih Ideal/Butterworth/Gaussian.")
        }

        # --- SIDEBAR (KIRI) ---
        self.sidebar = tk.Frame(self, bg=COLORS["sidebar_bg"], width=320)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        # Logo / Judul Sidebar
        logo_area = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        logo_area.pack(fill="x", padx=20, pady=(40, 20))

        tk.Label(logo_area, text="IMAGE", bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_fg"],
                 font=("Segoe UI", 24, "bold"), anchor="w").pack(fill="x")
        tk.Label(logo_area, text="PROCESSING", bg=COLORS["sidebar_bg"], fg=COLORS["primary"],
                 font=("Segoe UI", 24, "bold"), anchor="w").pack(fill="x")

        # --- FITUR PENCARIAN ---
        search_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        search_frame.pack(fill="x", padx=20, pady=(0, 20))

        tk.Label(search_frame, text="🔍 Cari Topik / Filter:", bg=COLORS["sidebar_bg"], fg="#A0A0A0",
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 5))

        self.search_var = tk.StringVar()
        self.entry_search = tk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 11), bg="white",
                                     relief="flat", bd=5)
        self.entry_search.pack(fill="x", side="left", expand=True)
        self.entry_search.bind("<Return>", self.perform_search)

        btn_go = tk.Button(search_frame, text="GO", command=self.perform_search, bg=COLORS["primary"], fg="white",
                           relief="flat", font=("Segoe UI", 9, "bold"))
        btn_go.pack(side="right", fill="y", padx=(5, 0))

        # Menu Container
        self.menu_container = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        self.menu_container.pack(fill="both", expand=True, padx=0)

        # Daftar Menu [SESUAI TOPIK PDF]
        self.menus = [
            ("01", "Penampil Citra (Viewer)", ImageViewerApp),
            ("02", "Mach Band Effect & Brightness", MachBandApp),
            ("03", "Image Negative, Power-Law & Slicing", SinglePixelApp),
            ("04", "2-D DFT Spectrum", DftApp),
            ("05", "Frequency Domain Filtering", FrequencyFilterApp),
            ("06", "Spatial Filtering & Segmentation", SpatialSegmentationApp),
            ("07", "Spatial Resolution, Quantization & Hist", ResHistApp),
            ("08", "Arithmetic & Logic Operations", ArithmeticApp)
        ]

        self.btn_refs = []
        self.menu_map = {}

        for code, name, frame_class in self.menus:
            btn = self.create_menu_btn(code, name, frame_class)
            self.menu_map[frame_class] = btn

        # Footer
        footer = tk.Frame(self.sidebar, bg="#2C3E32", height=100)
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)
        tk.Frame(footer, bg="#4F6D54", height=1).pack(fill="x", side="top")

        tk.Label(footer, text="Riki Daniel Tanebeth", bg="#2C3E32", fg="white",
                 font=("Segoe UI", 11, "bold")).pack(side="top", anchor="w", padx=30, pady=(20, 2))
        tk.Label(footer, text="NIM: 14240032", bg="#2C3E32", fg=COLORS["primary"],
                 font=("Segoe UI", 10)).pack(side="top", anchor="w", padx=30)

        # --- CONTENT AREA (KANAN) ---
        self.content_area = ttk.Frame(self, style="Main.TFrame")
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        self.current_frame = None

        if self.btn_refs:
            self.switch_frame(ImageViewerApp, self.btn_refs[0])

    def create_menu_btn(self, code, name, frame_class):
        btn_frame = tk.Frame(self.menu_container, bg=COLORS["sidebar_bg"], cursor="hand2", height=60)
        btn_frame.pack(fill="x", pady=1)
        btn_frame.pack_propagate(False)

        indicator = tk.Frame(btn_frame, bg=COLORS["sidebar_bg"], width=6)
        indicator.pack(side="left", fill="y")

        text_frame = tk.Frame(btn_frame, bg=COLORS["sidebar_bg"])
        text_frame.pack(side="left", fill="both", expand=True, padx=(15, 10))

        lbl_name = tk.Label(text_frame, text=f"{code}. {name}", font=("Segoe UI", 10),
                            bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_fg"], anchor="w")
        lbl_name.pack(side="left", fill="x")

        for w in (btn_frame, indicator, text_frame, lbl_name):
            w.bind("<Button-1>", lambda e: self.switch_frame(frame_class, btn_frame))

        btn_frame.indicator = indicator
        btn_frame.lbl_name = lbl_name
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
            font_weight = "bold" if is_active else "normal"

            btn.config(bg=bg)
            btn.text_frame.config(bg=bg)
            btn.indicator.config(bg=ind_bg)
            btn.lbl_name.config(bg=bg, fg=fg_name, font=("Segoe UI", 10, font_weight))

        self.current_frame = frame_class(self.content_area)

    def perform_search(self, event=None):
        query = self.search_var.get().lower().strip()
        if not query:
            return

        found = False
        for keyword, (app_class, instruction) in self.search_index.items():
            if keyword in query:
                if app_class in self.menu_map:
                    btn_target = self.menu_map[app_class]
                    self.switch_frame(app_class, btn_target)

                messagebox.showinfo("Hasil Pencarian", f"Topik ditemukan: '{query}'\n\nInstruksi:\n{instruction}")
                found = True
                self.entry_search.delete(0, tk.END)
                break

        if not found:
            messagebox.showwarning("Tidak Ditemukan",
                                   f"Maaf, topik '{query}' tidak ditemukan.\nCoba kata kunci lain.")


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()