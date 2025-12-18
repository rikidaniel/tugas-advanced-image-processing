import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import numpy as np
import cv2
from base_frame import BaseFrame
from styles import COLORS


class MachBandApp(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)

        content = self.create_header("Mach Band Effect & Brightness Adaptation",
                                     "Simulasi ilusi optik Mach Band & Adaptasi Mata (Simultaneous Contrast).")

        # Tombol Aksi Pusat
        ctrl_frame = tk.Frame(content, bg="white")
        ctrl_frame.pack(fill="x", pady=20)

        # --- TOMBOL-TOMBOL (Intensity Profile Dihapus) ---
        ttk.Button(ctrl_frame, text="✨ Generate Mach Band",
                   command=self.show_mach_band, style="Primary.TButton").pack(side="left", padx=(0, 10), expand=True)

        ttk.Button(ctrl_frame, text="👁️ Brightness Adaptation",
                   command=self.show_brightness_adaptation, style="Soft.TButton").pack(side="left", expand=True)

        # --- AREA TAMPIL ---
        # Menggunakan Frame khusus sebagai container yang ukurannya stabil
        self.preview_frame = tk.Frame(content, bg=COLORS["bg_main"], bd=2, relief="flat")
        self.preview_frame.pack(fill="both", expand=True)

        # Header untuk Tombol Save
        header_prev = tk.Frame(self.preview_frame, bg=COLORS["bg_main"])
        header_prev.pack(fill="x", pady=(0, 5))

        self.lbl_status = tk.Label(header_prev, text="Output Preview", bg=COLORS["bg_main"], fg="#666")
        self.lbl_status.pack(side="left")

        # Tombol Save
        tk.Button(header_prev, text="💾 Save Output", font=("Segoe UI", 8), bg="#ddd", bd=0,
                  command=self.save_current_output).pack(side="right")

        self.canvas = tk.Label(self.preview_frame, bg=COLORS["bg_main"], text="Pilih simulasi di atas",
                               fg="#6B7280", font=("Segoe UI", 12))
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)

        self.current_img_cv = None
        self.tk_img = None
        self.active_mode = "none"

    def show_mach_band(self):
        w = 560
        h_band = 120
        bands = np.zeros((h_band, w), dtype=np.uint8)
        block_w = w // 10
        for i in range(10):
            value = int(255 * i / 9)
            bands[:, i * block_w:(i + 1) * block_w] = value

        self.current_img_cv = bands
        self.active_mode = "mach_band"

        # Visualisasi dipercantik
        bands_disp = cv2.copyMakeBorder(bands, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)
        self._display_final(Image.fromarray(bands_disp), "Mach Band Effect")

    def show_brightness_adaptation(self):
        # Membuat 4 Kotak (Grid 2x2)
        w, h = 600, 600
        img = np.zeros((h, w), dtype=np.uint8)

        # 1. Backgrounds
        img[0:h // 2, 0:w // 2] = 50  # Gelap
        img[0:h // 2, w // 2:w] = 100  # Agak Gelap
        img[h // 2:h, 0:w // 2] = 150  # Agak Terang
        img[h // 2:h, w // 2:w] = 200  # Terang

        # 2. Kotak Kecil (Intensitas SAMA)
        inner_val = 125
        box_size = 80
        centers = [
            (h // 4, w // 4),
            (h // 4, 3 * w // 4),
            (3 * h // 4, w // 4),
            (3 * h // 4, 3 * w // 4)
        ]

        for (cy, cx) in centers:
            img[cy - box_size // 2: cy + box_size // 2, cx - box_size // 2: cx + box_size // 2] = inner_val

        self.current_img_cv = img
        self.active_mode = "adaptation"
        self._display_final(Image.fromarray(img), "Brightness Adaptation of Human Eye")

    def save_current_output(self):
        if self.current_img_cv is None: return
        name = f"mach_effect_{self.active_mode}"
        self.save_image_cv(self.current_img_cv, name)

    def _display_final(self, pil_img, title_text):
        # 1. Tambahkan Header Putih & Judul
        header_height = 40
        total_width = pil_img.width
        final_img = Image.new('RGB', (total_width, pil_img.height + header_height), 'white')
        draw = ImageDraw.Draw(final_img)
        draw.rectangle([(2, 2), (total_width - 2, header_height)], fill='white', outline='black', width=2)

        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), title_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = (total_width - text_w) // 2
        text_y = (header_height - text_h) // 2

        draw.text((text_x, text_y), title_text, fill='black', font=font)
        final_img.paste(pil_img.convert('RGB'), (0, header_height))

        # 2. LOGIKA RESIZE ANTI-LOOPING
        # Kita ambil ukuran dari self.preview_frame (Induk) yang ukurannya stabil mengikuti jendela,
        # BUKAN mengambil dari self.canvas (Label gambar) yang ukurannya berubah-ubah mengikuti gambar.

        # Pakai update_idletasks agar ukuran frame valid jika baru pertama kali load
        self.preview_frame.update_idletasks()

        vh = self.preview_frame.winfo_height()
        vw = self.preview_frame.winfo_width()

        # Fallback safety jika window belum tampil sempurna
        if vh < 100: vh = 600
        if vw < 100: vw = 600

        # Hitung skala agar gambar pas di layar (Fit Center)
        scale = min(vw / total_width, vh / final_img.height) * 0.95

        new_w = int(total_width * scale)
        new_h = int(final_img.height * scale)

        final_img_resized = final_img.resize((new_w, new_h), Image.LANCZOS)

        self.tk_img = ImageTk.PhotoImage(final_img_resized)
        self.canvas.config(image=self.tk_img, text="")
        self.lbl_status.config(text=f"Showing: {title_text}")