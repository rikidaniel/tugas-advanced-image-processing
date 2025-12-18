import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk
import cv2
from base_frame import BaseFrame
from styles import COLORS

IMG_H, IMG_W = 512, 512


class DftApp(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.custom_img = None
        self.last_mag_display = None
        self.last_phase_display = None

        content = self.create_header("2-D DFT Spectrum (Pg 13)",
                                     "Figure 4.3: Fourier Spectrum of a 20x40 Rectangle.")

        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=0)
        content.columnconfigure(2, weight=1)
        content.rowconfigure(0, weight=1)

        # --- PANEL KIRI: INPUT IMAGE ---
        left_frame = ttk.Frame(content, style="Card.TFrame")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Label sesuai PDF Fig 4.3(a)
        tk.Label(left_frame, text="(a) Image of a 20x40 white rectangle",
                 bg="#F1F5F9", font=("Segoe UI", 9, "bold"), wraplength=250).pack(pady=5)

        self.left_panel = tk.Label(left_frame, bg="black", bd=1, relief="solid")
        self.left_panel.pack(expand=True, fill="both", padx=10, pady=10)

        # --- PANEL TENGAH: KONTROL ---
        mid_frame = ttk.Frame(content, padding=15)
        mid_frame.grid(row=0, column=1, sticky="ns")

        ttk.Label(mid_frame, text="Input Source:", style="Sub.TLabel").pack(anchor="w", pady=(0, 5))

        # Preset sesuai kasus di PDF
        self.shape_var = tk.StringVar(value="Fig 4.3 (Rect 20x40)")
        shapes = ["Fig 4.3 (Rect 20x40)", "Rect 40x20 (Horizontal)", "Square 40x40", "Circle", "Custom File"]
        cb_shape = ttk.Combobox(mid_frame, textvariable=self.shape_var, values=shapes, state="readonly", width=25)
        cb_shape.pack(anchor="w", pady=(0, 10))
        cb_shape.bind("<<ComboboxSelected>>", self.on_shape_change)

        self.btn_load = ttk.Button(mid_frame, text="📂 Load Image", command=self.open_image, state="disabled")
        self.btn_load.pack(fill="x", pady=(0, 15))

        ttk.Separator(mid_frame, orient="horizontal").pack(fill="x", pady=10)

        # Rotasi (Tambahan fitur eksplorasi)
        tk.Label(mid_frame, text="Rotation (°):", bg=COLORS["bg_main"]).pack(anchor="w")
        self.angle_var = tk.DoubleVar(value=0.0)
        self.angle_lbl = tk.Label(mid_frame, text="0.0°", bg=COLORS["bg_main"], fg=COLORS["primary"],
                                  font=("Segoe UI", 9, "bold"))
        self.angle_lbl.pack(anchor="e")
        ttk.Scale(mid_frame, from_=-90, to=90, variable=self.angle_var, command=self._update_angle).pack(fill="x",
                                                                                                         pady=(0, 15))

        # Pilihan Output
        ttk.Label(mid_frame, text="Spectrum View:", style="Sub.TLabel").pack(anchor="w", pady=(10, 5))
        self.spectrum_type = tk.StringVar(value="Magnitude")

        r1 = ttk.Radiobutton(mid_frame, text="Magnitude (Log)", variable=self.spectrum_type, value="Magnitude",
                             command=self.refresh_display)
        r1.pack(anchor="w")
        r2 = ttk.Radiobutton(mid_frame, text="Phase (Angle)", variable=self.spectrum_type, value="Phase",
                             command=self.refresh_display)
        r2.pack(anchor="w")

        # Invert Display (Jika ingin background putih seperti kertas)
        self.invert_display = tk.BooleanVar(value=False)
        ttk.Checkbutton(mid_frame, text="Invert Output (White BG)", variable=self.invert_display,
                        command=self.refresh_display).pack(anchor="w", pady=10)

        ttk.Button(mid_frame, text="▶ Apply Transform", command=self.apply_transform, style="Primary.TButton").pack(
            fill="x", pady=(20, 5))
        ttk.Button(mid_frame, text="↺ Reset", command=self.on_reset, style="Danger.TButton").pack(fill="x")

        # --- PANEL KANAN: OUTPUT SPECTRUM ---
        right_frame = ttk.Frame(content, style="Card.TFrame")
        right_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        rh = tk.Frame(right_frame, bg="#F1F5F9")
        rh.pack(fill="x", pady=5, padx=10)
        # Label sesuai PDF Fig 4.3(b)
        tk.Label(rh, text="(b) Centered Spectrum", bg="#F1F5F9", font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Button(rh, text="💾 Save", bd=0, bg="#ddd", command=self.save_spectrum).pack(side="right")

        self.right_panel = tk.Label(right_frame, bg="black", bd=1, relief="solid")
        self.right_panel.pack(expand=True, fill="both", padx=10, pady=10)

        # Jalankan default saat startup
        self.on_reset()

    def on_shape_change(self, event=None):
        mode = self.shape_var.get()
        if mode == "Custom File":
            self.btn_load.config(state="normal")
        else:
            self.btn_load.config(state="disabled")
            self.custom_img = None
            self.apply_transform()

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.tif")])
        if not path: return

        img_bgr = cv2.imread(path)
        if img_bgr is None:
            messagebox.showerror("Error", "Gagal membuka gambar.")
            return

        img_bgr = cv2.resize(img_bgr, (IMG_W, IMG_H))
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        self.custom_img = img_gray.astype(np.float32) / 255.0
        self.apply_transform()

    def _update_angle(self, val):
        self.angle_lbl.config(text=f"{float(val):.1f}°")

    def on_reset(self):
        self.shape_var.set("Fig 4.3 (Rect 20x40)")
        self.angle_var.set(0.0)
        self.angle_lbl.config(text="0.0°")
        self.custom_img = None
        self.invert_display.set(False)
        self.btn_load.config(state="disabled")
        self.spectrum_type.set("Magnitude")
        self.apply_transform()

    def get_generated_image(self):
        img = np.zeros((IMG_H, IMG_W), dtype=np.float32)
        cx, cy = IMG_W // 2, IMG_H // 2
        mode = self.shape_var.get()

        if mode == "Custom File" and self.custom_img is not None:
            return self.custom_img.copy()

        # --- GENERATE SHAPES ---
        if "Fig 4.3" in mode:
            # Figure 4.3: "20x40 white rectangle"
            # Asumsi: Lebar=20, Tinggi=40 (Vertikal)
            # Koordinat: Center +/- setengah ukuran
            w_half, h_half = 10, 20
            cv2.rectangle(img, (cx - w_half, cy - h_half), (cx + w_half, cy + h_half), 1.0, -1)

        elif "Rect 40x20" in mode:
            # Lebar=40, Tinggi=20 (Horizontal)
            w_half, h_half = 20, 10
            cv2.rectangle(img, (cx - w_half, cy - h_half), (cx + w_half, cy + h_half), 1.0, -1)

        elif "Square" in mode:
            w_half = 20
            cv2.rectangle(img, (cx - w_half, cy - w_half), (cx + w_half, cy + w_half), 1.0, -1)

        elif "Circle" in mode:
            cv2.circle(img, (cx, cy), 20, 1.0, -1)

        return img

    def apply_transform(self):
        # 1. Ambil Gambar
        img = self.get_generated_image()

        # 2. Rotasi (Opsional)
        angle = self.angle_var.get()
        if abs(angle) > 0.1:
            M = cv2.getRotationMatrix2D((IMG_W // 2, IMG_H // 2), angle, 1.0)
            img = cv2.warpAffine(img, M, (IMG_W, IMG_H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                                 borderValue=0.0)

        # Tampilkan Input
        img = np.clip(img, 0.0, 1.0)
        self.show_img(self.left_panel, img, is_spectrum=False)

        # 3. Hitung DFT 2D
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)  # Pindahkan DC ke tengah (Centered Spectrum)

        # 4. Hitung Magnitude (Log Scale) -> Sesuai Eq 3.2-2 di PDF
        mag = np.abs(fshift)
        mag_log = np.log(1 + mag)
        self.last_mag_display = cv2.normalize(mag_log, None, 0, 1, cv2.NORM_MINMAX)

        # 5. Hitung Phase
        phase = np.angle(fshift)
        self.last_phase_display = cv2.normalize(phase, None, 0, 1, cv2.NORM_MINMAX)

        self.refresh_display()

    def refresh_display(self):
        mode = self.spectrum_type.get()
        target = None

        if mode == "Magnitude" and self.last_mag_display is not None:
            target = self.last_mag_display.copy()
        elif mode == "Phase" and self.last_phase_display is not None:
            target = self.last_phase_display.copy()

        if target is not None:
            if self.invert_display.get():
                target = 1.0 - target
            self.show_img(self.right_panel, target, is_spectrum=True)

    def show_img(self, panel, img_float, is_spectrum=False):
        img_u8 = (img_float * 255).astype(np.uint8)

        # Resize untuk display GUI (perbesar agar jelas)
        # Gunakan Nearest Neighbor untuk spektrum agar pixel-nya tegas
        interp = Image.NEAREST if is_spectrum else Image.LANCZOS

        pil = Image.fromarray(img_u8).resize((300, 300), interp)
        tk_img = ImageTk.PhotoImage(pil)

        panel.config(image=tk_img)
        panel.image = tk_img

    def save_spectrum(self):
        mode = self.spectrum_type.get()
        target = None
        if mode == "Magnitude":
            target = self.last_mag_display
        elif mode == "Phase":
            target = self.last_phase_display

        if target is not None:
            if self.invert_display.get():
                target = 1.0 - target
            img_save = (target * 255).astype(np.uint8)
            self.save_image_cv(img_save, f"dft_{mode.lower()}")