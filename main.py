import tkinter as tk
from tkinter import ttk
from styles import apply_theme, COLORS, FONTS

from image_view import ImageViewerApp
from mach_and_band_effect import MachBandApp
from program3_single_pixel import SinglePixelApp
from dft_explorer import DftApp
from frequency_filters import FrequencyFilterApp


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Aplikasi Pengolahan Citra Digital")
        self.geometry("1300x800")
        self.state("zoomed")

        self.style = apply_theme(self)
        self.configure(bg=COLORS["sidebar_bg"])

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (KIRI) ---
        self.sidebar = tk.Frame(self, bg=COLORS["sidebar_bg"], width=280)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        # Logo / Judul Sidebar
        logo_area = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        logo_area.pack(fill="x", padx=25, pady=(50, 40))

        tk.Label(logo_area, text="IMAGE", bg=COLORS["sidebar_bg"], fg="#FFFFFF",
                 font=("Segoe UI", 26, "bold"), anchor="w").pack(fill="x")
        tk.Label(logo_area, text="PROCESSING", bg=COLORS["sidebar_bg"], fg=COLORS["primary"],
                 font=("Segoe UI", 26, "bold"), anchor="w").pack(fill="x")
        tk.Label(logo_area, text="DASHBOARD v2.0", bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_fg"],
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=(5, 0))

        # Menu
        self.menu_container = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        self.menu_container.pack(fill="both", expand=True, padx=15)

        self.menus = [
            ("01", "Penampil Citra", ImageViewerApp),
            ("02", "Mach Band Effect", MachBandApp),
            ("03", "Image Enhancement", SinglePixelApp),
            ("04", "DFT Explorer", DftApp),
            ("05", "Filter Frekuensi", FrequencyFilterApp)
        ]

        self.btn_refs = []
        for code, name, frame_class in self.menus:
            self.create_menu_btn(code, name, frame_class)

        # Footer (Info Mahasiswa)
        footer = tk.Frame(self.sidebar, bg="#022C22", height=100)  # Hijau sangat gelap
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)

        tk.Label(footer, text="Riki Daniel Tanebeth", bg="#022C22", fg="white",
                 font=("Segoe UI", 11, "bold")).pack(side="top", anchor="w", padx=25, pady=(25, 2))
        tk.Label(footer, text="NIM: 14240032", bg="#022C22", fg=COLORS["primary"],
                 font=("Segoe UI", 10)).pack(side="top", anchor="w", padx=25)

        # --- CONTENT AREA (KANAN) ---
        self.content_area = ttk.Frame(self, style="Main.TFrame")
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        self.current_frame = None
        self.switch_frame(ImageViewerApp, self.btn_refs[0])

    def create_menu_btn(self, code, name, frame_class):
        btn_frame = tk.Frame(self.menu_container, bg=COLORS["sidebar_bg"], cursor="hand2", height=60)
        btn_frame.pack(fill="x", pady=4)
        btn_frame.pack_propagate(False)

        # Indikator (Garis kiri)
        indicator = tk.Frame(btn_frame, bg=COLORS["sidebar_bg"], width=5)
        indicator.pack(side="left", fill="y")

        # Teks
        lbl_code = tk.Label(btn_frame, text=code, font=("Segoe UI", 12, "bold"),
                            bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_fg"])
        lbl_code.pack(side="left", padx=(15, 10))

        lbl_name = tk.Label(btn_frame, text=name, font=("Segoe UI", 11),
                            bg=COLORS["sidebar_bg"], fg="white")
        lbl_name.pack(side="left")

        # Binding Event
        for w in (btn_frame, lbl_code, lbl_name):
            w.bind("<Button-1>", lambda e: self.switch_frame(frame_class, btn_frame))

        btn_frame.indicator = indicator
        btn_frame.lbl_code = lbl_code
        btn_frame.lbl_name = lbl_name
        self.btn_refs.append(btn_frame)

    def switch_frame(self, frame_class, active_btn):
        if self.current_frame:
            self.current_frame.destroy()

        # Update Visual Tombol
        for btn in self.btn_refs:
            is_active = (btn == active_btn)
            bg = COLORS["active_bg"] if is_active else COLORS["sidebar_bg"]
            ind_bg = COLORS["primary"] if is_active else bg

            btn.config(bg=bg)
            btn.indicator.config(bg=ind_bg)
            btn.lbl_code.config(bg=bg, fg="white" if is_active else COLORS["sidebar_fg"])
            btn.lbl_name.config(bg=bg, fg="white", font=("Segoe UI", 11, "bold" if is_active else "normal"))

        self.current_frame = frame_class(self.content_area)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()