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

        content = self.create_header("Transformasi Fourier",
                                     "Eksplorasi spektrum frekuensi citra 2D (Spasial vs Frekuensi).")

        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.columnconfigure(2, weight=1)
        content.rowconfigure(0, weight=1)

        # KIRI: Spasial
        left_frame = tk.Frame(content, bg="white")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10)
        tk.Label(left_frame, text="Gambar Spasial", bg="white", fg="#4B5563", font=("Segoe UI", 11, "bold")).pack(pady=10)

        self.left_panel = tk.Label(left_frame, bg="#000000", bd=1, relief="solid")
        self.left_panel.pack(expand=True, padx=10, fill="both")

        # TENGAH: Kontrol
        mid_frame = tk.Frame(content, bg="white")
        mid_frame.grid(row=0, column=1, sticky="ns", padx=20)

        ttk.Label(mid_frame, text="Kontrol Objek", style="H2.TLabel").pack(pady=(10, 20))

        # Slider Frame
        slider_frame = tk.Frame(mid_frame, bg=COLORS["bg_main"], padx=10, pady=10)
        slider_frame.pack(fill="x", pady=10)
        
        ttk.Button(slider_frame, text="📂 Buka Gambar", command=self.open_image, style="Primary.TButton").pack(fill="x", pady=(0, 15))

        tk.Label(slider_frame, text="Rotasi (°)", bg=COLORS["bg_main"]).pack(anchor="w")
        self.angle_var = tk.DoubleVar(value=0.0)
        self.angle_lbl = tk.Label(slider_frame, text="0.0°", bg=COLORS["bg_main"], fg=COLORS["primary"],
                                  font=("Segoe UI", 10, "bold"))
        self.angle_lbl.pack(anchor="e")
        ttk.Scale(slider_frame, from_=-90, to=90, variable=self.angle_var, command=self._update_ui).pack(fill="x")

        self.invert_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(mid_frame, text="Invert Warna", variable=self.invert_var).pack(pady=15, anchor="w")

        ttk.Button(mid_frame, text="▶ Terapkan", command=self.apply_changes, style="Soft.TButton").pack(fill="x", pady=5)
        ttk.Button(mid_frame, text="↺ Reset", command=self.on_reset, style="Danger.TButton").pack(fill="x", pady=5)

        # KANAN: Frekuensi
        right_frame = tk.Frame(content, bg="white")
        right_frame.grid(row=0, column=2, sticky="nsew", padx=10)
        tk.Label(right_frame, text="Spektrum Frekuensi (DFT)", bg="white", fg="#4B5563",
                 font=("Segoe UI", 11, "bold")).pack(pady=10)

        self.right_panel = tk.Label(right_frame, bg="#000000", bd=1, relief="solid")
        self.right_panel.pack(expand=True, padx=10, fill="both")

        self.apply_changes()
    
    def open_image(self):
        # [Perbaikan] Menambahkan *.tiff dan *.tif
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.tif")])
        if not path: return
        
        img_bgr = cv2.imread(path)
        if img_bgr is None:
            messagebox.showerror("Error", "Gagal membuka gambar.")
            return

        img_bgr_resized = cv2.resize(img_bgr, (IMG_W, IMG_H))
        img_gray = cv2.cvtColor(img_bgr_resized, cv2.COLOR_BGR2GRAY)
        
        self.custom_img = img_gray.astype(np.float32) / 255.0
        self.apply_changes()

    def _update_ui(self, val):
        self.angle_lbl.config(text=f"{float(val):.1f}°")

    def on_reset(self):
        self.custom_img = None
        self.angle_var.set(0.0)
        self.invert_var.set(False)
        self._update_ui(0)
        self.apply_changes()

    def apply_changes(self):
        if self.custom_img is not None:
            img = self.custom_img.copy()
        else:
            # Default: Rectangle 20x40 (PDF Hal 13)
            img = np.zeros((IMG_H, IMG_W), dtype=np.float32)
            # Gambar kotak putih di tengah
            cv2.rectangle(img, (IMG_W//2 - 10, IMG_H//2 - 20), (IMG_W//2 + 10, IMG_H//2 + 20), 1.0, -1)

        M = cv2.getRotationMatrix2D((IMG_W // 2, IMG_H // 2), self.angle_var.get(), 1.0)
        
        img = cv2.warpAffine(img, M, (IMG_W, IMG_H), flags=cv2.INTER_LINEAR)
        if self.invert_var.get(): img = 1.0 - img
        img = np.clip(img, 0.0, 1.0)

        self.show_img(self.left_panel, img)

        F = np.fft.fftshift(np.fft.fft2(img))
        mag = np.log1p(np.abs(F))
        mag_norm = cv2.normalize(mag, None, 0, 1, cv2.NORM_MINMAX)
        self.show_img(self.right_panel, mag_norm)

    def show_img(self, panel, img_float):
        img_u8 = (img_float * 255).astype(np.uint8)
        pil = Image.fromarray(img_u8).resize((250, 250))
        tk_img = ImageTk.PhotoImage(pil)
        panel.config(image=tk_img)
        panel.image = tk_img