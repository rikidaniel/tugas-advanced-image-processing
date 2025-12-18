import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk
import cv2
from base_frame import BaseFrame
from styles import COLORS

IMG_H, IMG_W = 500, 500


class DftApp(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.custom_img = None
        self.last_spectrum_display = None
        self.last_phase_display = None
        self.last_spatial_display = None
        self.current_img_data = None

        content = self.create_header("DFT Spectrum & Reconstruction (Pg 13-14)",
                                     "Analyze Spectrum, Rotation, and Simulate DC Removal (F(0,0)=0).")

        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=0)
        content.columnconfigure(2, weight=1)
        content.rowconfigure(0, weight=1)

        # --- PANEL KIRI: INPUT IMAGE ---
        left_frame = ttk.Frame(content, style="Card.TFrame")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        tk.Label(left_frame, text="Input Image (Spatial)",
                 bg="#F1F5F9", font=("Segoe UI", 9, "bold")).pack(pady=5)

        self.left_panel = tk.Label(left_frame, bg="black", bd=1, relief="solid")
        self.left_panel.pack(expand=True, fill="both", padx=10, pady=10)

        # --- PANEL TENGAH: KONTROL ---
        mid_frame = ttk.Frame(content, padding=15)
        mid_frame.grid(row=0, column=1, sticky="ns")

        # 1. Input Source (HANYA TOMBOL LOAD)
        ttk.Label(mid_frame, text="1. Input Source:", style="Sub.TLabel").pack(anchor="w", pady=(0, 5))

        self.btn_load = ttk.Button(mid_frame, text="📂 Load Image", command=self.open_image, style="Primary.TButton")
        self.btn_load.pack(fill="x", pady=(0, 10))

        ttk.Separator(mid_frame, orient="horizontal").pack(fill="x", pady=10)

        # 2. Rotation Control
        tk.Label(mid_frame, text="2. Rotation (°):", bg=COLORS["bg_main"], font=("Segoe UI", 9)).pack(anchor="w")
        self.angle_var = tk.DoubleVar(value=0.0)
        self.angle_lbl = tk.Label(mid_frame, text="0.0°", bg=COLORS["bg_main"], fg=COLORS["primary"],
                                  font=("Segoe UI", 9, "bold"))
        self.angle_lbl.pack(anchor="e")

        ttk.Scale(mid_frame, from_=-90, to=90, variable=self.angle_var,
                  command=self._update_angle).pack(fill="x", pady=(0, 15))

        # 3. Manipulation
        ttk.Label(mid_frame, text="3. Spectrum Manipulation:", style="Sub.TLabel").pack(anchor="w", pady=(0, 5))

        self.remove_dc_var = tk.BooleanVar(value=False)
        chk_dc = ttk.Checkbutton(mid_frame, text="Set F(0,0) = 0 (Remove DC)",
                                 variable=self.remove_dc_var, command=self.apply_transform)
        chk_dc.pack(anchor="w", pady=5)

        ttk.Label(mid_frame, text="(Removes average intensity)", font=("Segoe UI", 8), foreground="#666").pack(
            anchor="w", padx=20)

        ttk.Separator(mid_frame, orient="horizontal").pack(fill="x", pady=15)

        # 4. Output View Selection
        ttk.Label(mid_frame, text="4. Output View:", style="Sub.TLabel").pack(anchor="w", pady=(0, 5))
        self.view_type = tk.StringVar(value="Magnitude")

        r1 = ttk.Radiobutton(mid_frame, text="Spectrum Magnitude (Log)", variable=self.view_type, value="Magnitude",
                             command=self.refresh_display)
        r1.pack(anchor="w")
        r2 = ttk.Radiobutton(mid_frame, text="Spectrum Phase", variable=self.view_type, value="Phase",
                             command=self.refresh_display)
        r2.pack(anchor="w")
        r3 = ttk.Radiobutton(mid_frame, text="Spatial Result (Inverse DFT)", variable=self.view_type, value="Spatial",
                             command=self.refresh_display)
        r3.pack(anchor="w", pady=(5, 0))

        ttk.Button(mid_frame, text="▶ Update / Apply", command=self.apply_transform, style="Primary.TButton").pack(
            fill="x", pady=(20, 5))
        ttk.Button(mid_frame, text="↺ Reset", command=self.on_reset, style="Danger.TButton").pack(fill="x")

        # --- PANEL KANAN: OUTPUT ---
        right_frame = ttk.Frame(content, style="Card.TFrame")
        right_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        rh = tk.Frame(right_frame, bg="#F1F5F9")
        rh.pack(fill="x", pady=5, padx=10)
        self.lbl_right_title = tk.Label(rh, text="Output View", bg="#F1F5F9", font=("Segoe UI", 10, "bold"))
        self.lbl_right_title.pack(side="left")

        tk.Button(rh, text="💾 Save", bd=0, bg="#ddd", command=self.save_current_view).pack(side="right")

        self.right_panel = tk.Label(right_frame, bg="black", bd=1, relief="solid")
        self.right_panel.pack(expand=True, fill="both", padx=10, pady=10)

        # Init (KOSONGKAN DEFAULT)
        self.on_reset()

    def _update_angle(self, val):
        self.angle_lbl.config(text=f"{float(val):.1f}°")

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.tif")])
        if not path: return
        img_bgr = cv2.imread(path)
        if img_bgr is None: return

        # Resize standard agar kalkulasi FFT tidak terlalu berat
        img_bgr = cv2.resize(img_bgr, (IMG_W, IMG_H))
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        self.custom_img = img_gray
        self.apply_transform()

    def on_reset(self):
        # Reset variable
        self.angle_var.set(0.0)
        self._update_angle(0.0)
        self.remove_dc_var.set(False)
        self.view_type.set("Magnitude")
        self.custom_img = None

        # Kosongkan Tampilan
        self.left_panel.config(image="", text="Please load an image", fg="white")
        self.right_panel.config(image="", text="No Output", fg="white")

        # Reset memori gambar
        self.last_spectrum_display = None
        self.last_phase_display = None
        self.last_spatial_display = None
        self.current_img_data = None

    def apply_transform(self):
        if self.custom_img is None:
            # Tidak ada gambar yang diproses
            self.left_panel.config(image="", text="No Image Loaded", fg="white")
            self.right_panel.config(image="", text="No Output", fg="white")
            return

        # 1. Get Base Image
        img_u8 = self.custom_img.copy()

        # 2. APPLY ROTATION
        angle = self.angle_var.get()
        if abs(angle) > 0.1:
            bg_val = int(np.mean(img_u8))
            border_mode = cv2.BORDER_CONSTANT
            M = cv2.getRotationMatrix2D((IMG_W // 2, IMG_H // 2), angle, 1.0)
            img_u8 = cv2.warpAffine(img_u8, M, (IMG_W, IMG_H),
                                    flags=cv2.INTER_LINEAR,
                                    borderMode=border_mode,
                                    borderValue=bg_val)

        self.current_img_data = img_u8
        self.show_img(self.left_panel, img_u8)

        # 3. FFT
        f_img = img_u8.astype(np.float32)
        f = np.fft.fft2(f_img)
        fshift = np.fft.fftshift(f)

        # 4. Manipulasi F(0,0) -> DC Component
        if self.remove_dc_var.get():
            rows, cols = img_u8.shape
            crow, ccol = rows // 2, cols // 2
            fshift[crow, ccol] = 0.0 + 0.0j

        # 5. Prepare Magnitude Spectrum (Log Scale)
        mag = np.abs(fshift)
        mag_log = np.log(1 + mag)
        self.last_spectrum_display = cv2.normalize(mag_log, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # 6. Prepare Phase Spectrum
        phase = np.angle(fshift)
        self.last_phase_display = cv2.normalize(phase, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # 7. Inverse FFT (Spatial Reconstruction)
        f_ishift = np.fft.ifftshift(fshift)
        img_back = np.fft.ifft2(f_ishift)

        # Ambil bagian Real
        img_back_real = np.real(img_back)

        # LOGIKA VISUALISASI "SPATIAL RESULT"
        if self.remove_dc_var.get():
            # Teknik visualisasi khusus untuk Remove DC (Negatif kontras tinggi)
            res = np.abs(img_back_real)
            res = res * 4.0  # Boost contrast
            res = np.clip(res, 0, 255).astype(np.uint8)
            self.last_spatial_display = res
        else:
            # Normal reconstruction
            res = np.clip(img_back_real, 0, 255).astype(np.uint8)
            self.last_spatial_display = res

        self.refresh_display()

    def refresh_display(self):
        # Jika belum ada hasil hitungan, jangan lakukan apa-apa
        if self.last_spectrum_display is None:
            return

        mode = self.view_type.get()
        target = None
        title = ""

        if mode == "Magnitude":
            target = self.last_spectrum_display
            title = "Magnitude Spectrum"
        elif mode == "Phase":
            target = self.last_phase_display
            title = "Phase Spectrum"
        elif mode == "Spatial":
            target = self.last_spatial_display
            title = "Reconstructed Spatial Image"
            if self.remove_dc_var.get():
                title += " (DC Removed)"

        self.lbl_right_title.config(text=title)

        if target is not None:
            interp = Image.LANCZOS if mode == "Spatial" else Image.NEAREST
            self.show_img(self.right_panel, target, interp=interp)

    def show_img(self, panel, img_u8, interp=Image.LANCZOS):
        # [FIX] Anti-Zoom Out Logic
        total_w = self.winfo_width()
        total_h = self.winfo_height()

        if total_w < 100: total_w = 900
        if total_h < 100: total_h = 700

        vw = int(total_w * 0.4)
        vh = total_h - 250

        if vw < 100: vw = 300
        if vh < 100: vh = 300

        h, w = img_u8.shape
        scale = min(vw / w, vh / h) * 0.95

        nw, nh = int(w * scale), int(h * scale)
        if nw < 1: nw = 1
        if nh < 1: nh = 1

        pil = Image.fromarray(img_u8).resize((nw, nh), interp)
        tk_img = ImageTk.PhotoImage(pil)

        panel.config(image=tk_img)
        panel.image = tk_img

    def save_current_view(self):
        mode = self.view_type.get()
        target = None
        if mode == "Magnitude":
            target = self.last_spectrum_display
        elif mode == "Phase":
            target = self.last_phase_display
        elif mode == "Spatial":
            target = self.last_spatial_display

        if target is not None:
            self.save_image_cv(target, f"dft_{mode.lower()}")