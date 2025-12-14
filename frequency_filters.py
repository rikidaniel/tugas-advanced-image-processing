import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import cv2
from PIL import Image, ImageTk
from base_frame import BaseFrame


class FrequencyFilterApp(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)

        content = self.create_header("Program 5 - Filter Domain Frekuensi", "Implementasi Lowpass & Highpass Filter.")

        ctrl_frame = ttk.LabelFrame(content, text="Panel Kontrol", padding=15)
        ctrl_frame.pack(fill="x", pady=(0, 20))

        row1 = ttk.Frame(ctrl_frame)
        row1.pack(fill="x", pady=5)
        ttk.Button(row1, text="📂 Buka Gambar", command=self.open_image, style="Primary.TButton").pack(side="left",
                                                                                                      padx=(0, 15))
        ttk.Button(row1, text="↺ Reset Gambar", command=self.reset_image, style="Danger.TButton").pack(side="left")

        row2 = ttk.Frame(ctrl_frame)
        row2.pack(fill="x", pady=(20, 5))

        ttk.Label(row2, text="Jenis Filter:", style="Sub.TLabel").pack(side="left")
        self.filter_type_var = tk.StringVar(value="Ideal")
        ttk.Combobox(row2, textvariable=self.filter_type_var, values=["Ideal", "Butterworth", "Gaussian", "Mean Removal"],
                     state="readonly", width=14).pack(side="left", padx=(5, 15))

        ttk.Label(row2, text="Mode:", style="Sub.TLabel").pack(side="left")
        self.pass_type_var = tk.StringVar(value="Lowpass")
        ttk.Combobox(row2, textvariable=self.pass_type_var, values=["Lowpass", "Highpass"],
                     state="readonly", width=10).pack(side="left", padx=(5, 15))

        ttk.Label(row2, text="Cutoff (D0):", style="Sub.TLabel").pack(side="left")
        self.d0_var = tk.DoubleVar(value=40.0)
        ttk.Entry(row2, textvariable=self.d0_var, width=6).pack(side="left", padx=(5, 15))

        ttk.Label(row2, text="Orde (n):", style="Sub.TLabel").pack(side="left")
        self.n_var = tk.IntVar(value=2)
        ttk.Entry(row2, textvariable=self.n_var, width=6).pack(side="left", padx=(5, 20))

        ttk.Button(row2, text="▶ Terapkan Filter", command=self.apply_filter, style="Soft.TButton").pack(side="left",
                                                                                                         padx=20)

        img_grid = ttk.Frame(content)
        img_grid.pack(fill="both", expand=True)
        img_grid.columnconfigure(0, weight=1)
        img_grid.columnconfigure(1, weight=1)

        f_left = ttk.Frame(img_grid, style="Card.TFrame")
        f_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(f_left, text="Original Image (512x512)", bg="#F1F5F9", pady=8, font=("Segoe UI", 10, "bold")).pack(
            fill="x")
        self.lbl_original = tk.Label(f_left, bg="#F1F5F9")
        self.lbl_original.pack(fill="both", expand=True)

        f_right = ttk.Frame(img_grid, style="Card.TFrame")
        f_right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        tk.Label(f_right, text="Filtered Result", bg="#F1F5F9", pady=8, font=("Segoe UI", 10, "bold")).pack(fill="x")
        self.lbl_filtered = tk.Label(f_right, bg="#F1F5F9")
        self.lbl_filtered.pack(fill="both", expand=True)

        self.gray_img = None
        self.original_img = None

    def open_image(self):
        # [Perbaikan] Tambah Support TIFF
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.tif")])
        if not path: return
        img_bgr = cv2.imread(path)
        if img_bgr is None: return

        # --- NORMALISASI UKURAN KE 512x512 ---
        # Mengubah ukuran gambar input menjadi tepat 512x512 piksel
        img_bgr = cv2.resize(img_bgr, (512, 512))

        self.gray_img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
        self.original_img = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

        # Tampilkan gambar (resize sedikit untuk tampilan UI jika perlu, tapi data tetap 512)
        self.show_img(self.lbl_original, self.original_img)
        self.lbl_filtered.config(image="")

    def reset_image(self):
        if self.original_img:
            self.show_img(self.lbl_original, self.original_img)
            self.lbl_filtered.config(image="")

    def show_img(self, lbl, pil):
        # Kita resize sedikit untuk tampilan UI agar rapi (350px),
        # namun data asli (self.gray_img) tetap 512x512 untuk pemrosesan.
        display_img = pil.resize((350, 350), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(display_img)
        lbl.config(image=tk_img)
        lbl.image = tk_img

    def apply_filter(self):
        if self.gray_img is None: return
        d0, n = self.d0_var.get(), self.n_var.get()

        # Proses FFT (Gambar input sudah pasti 512x512)
        f = np.fft.fftshift(np.fft.fft2(self.gray_img))

        rows, cols = self.gray_img.shape
        crow, ccol = rows // 2, cols // 2
        u = np.arange(rows)
        v = np.arange(cols)
        U, V = np.meshgrid(v, u)
        D = np.sqrt((U - ccol) ** 2 + (V - crow) ** 2)

        ft = self.filter_type_var.get()
        if ft == "Mean Removal":
             # EXPLICIT LOGIC: All 1s, except 0 at center.
             # This sets F(0,0) = 0 and passes everything else.
             # This overrides "Lowpass/Highpass" selection logic.
             H = np.ones((rows, cols), dtype=np.float32)
             H[crow, ccol] = 0.0
             
             # Apply directly without flipping
             pass
        else:
            # Standard Filters
            if ft == "Ideal":
                H = (D <= d0)
            elif ft == "Butterworth":
                H = 1 / (1 + (D / d0) ** (2 * n))
            elif ft == "Gaussian":
                H = np.exp(-(D ** 2) / (2 * d0 ** 2))
            
            # Apply Highpass toggle for standard filters
            if self.pass_type_var.get() == "Highpass": 
                H = 1 - H

        g = np.abs(np.fft.ifft2(np.fft.ifftshift(f * H)))
        g = np.clip(g, 0, 255).astype(np.uint8)
        self.show_img(self.lbl_filtered, Image.fromarray(g))