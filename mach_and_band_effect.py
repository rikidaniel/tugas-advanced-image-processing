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

        # Tombol-tombol
        ttk.Button(ctrl_frame, text="✨ Generate Mach Band",
                   command=self.show_mach_band, style="Primary.TButton").pack(side="left", padx=(0, 10), expand=True)

        ttk.Button(ctrl_frame, text="📈 Show Intensity Profile",
                   command=self.show_profile, style="Soft.TButton").pack(side="left", padx=(0, 10), expand=True)

        ttk.Button(ctrl_frame, text="👁️ Brightness Adaptation",
                   command=self.show_brightness_adaptation, style="Soft.TButton").pack(side="left", expand=True)

        # Area Tampil
        preview_frame = tk.Frame(content, bg=COLORS["bg_main"], bd=2, relief="flat")
        preview_frame.pack(fill="both", expand=True)

        self.canvas = tk.Label(preview_frame, bg=COLORS["bg_main"], text="Pilih simulasi di atas",
                               fg="#6B7280", font=("Segoe UI", 12))
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)

        self.current_img_cv = None  # Simpan gambar raw untuk profiling
        self.tk_img = None

    def show_mach_band(self):
        w = 560
        h_band = 120
        bands = np.zeros((h_band, w), dtype=np.uint8)
        block_w = w // 10

        # Membuat pola tangga (Staircase)
        for i in range(10):
            value = int(255 * i / 9)
            bands[:, i * block_w:(i + 1) * block_w] = value

        self.current_img_cv = bands

        # Visualisasi dipercantik untuk UI
        bands_disp = cv2.copyMakeBorder(bands, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)
        self._display_final(Image.fromarray(bands_disp), "Mach Band Effect (Perhatikan batas antar pita!)")

    def show_profile(self):
        if self.current_img_cv is None:
            self.show_mach_band()  # Generate dulu kalau belum ada

        # Ambil satu baris pixel dari tengah gambar
        h, w = self.current_img_cv.shape
        mid_line = self.current_img_cv[h // 2, :]

        # Buat Canvas Plot Sederhana menggunakan OpenCV
        plot_h, plot_w = 300, 560
        plot_img = np.ones((plot_h, plot_w, 3), dtype=np.uint8) * 255  # Putih

        # Gambar Grid
        cv2.line(plot_img, (50, 250), (550, 250), (0, 0, 0), 2)  # X axis
        cv2.line(plot_img, (50, 250), (50, 50), (0, 0, 0), 2)  # Y axis

        # Plot data
        # Normalisasi x ke lebar plot (50-550)
        # Normalisasi y (nilai 0-255) ke tinggi plot (250-50)
        pts = []
        for x in range(len(mid_line)):
            val = mid_line[x]
            px = int(50 + (x / w) * 500)
            py = int(250 - (val / 255) * 200)
            pts.append((px, py))

        pts = np.array(pts, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(plot_img, [pts], False, (255, 0, 0), 2)

        # Label
        cv2.putText(plot_img, "Actual Intensity Profile", (60, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(plot_img, "Mata melihat 'overshoot' di sudut, padahal data datar.", (60, 280),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 50, 50), 1)

        self._display_final(Image.fromarray(plot_img), "Bukti Ilusi (Grafik Intensitas Sebenarnya)")

    def show_brightness_adaptation(self):
        w, h = 600, 400
        img = np.zeros((h, w), dtype=np.uint8)
        img[:, :w // 2] = 50
        img[:, w // 2:] = 200

        box_size = 80
        cy, cx_l, cx_r = h // 2, w // 4, (w // 4) * 3
        img[cy - 40:cy + 40, cx_l - 40:cx_l + 40] = 125
        img[cy - 40:cy + 40, cx_r - 40:cx_r + 40] = 125

        self.current_img_cv = img
        self._display_final(Image.fromarray(img), "Brightness Adaptation (Kotak tengah bernilai SAMA)")

    def _display_final(self, pil_img, title_text):
        # ... (Kode display sama seperti sebelumnya) ...
        header_height = 40
        total_width = pil_img.width
        final_img = Image.new('RGB', (total_width, pil_img.height + header_height), 'white')
        draw = ImageDraw.Draw(final_img)
        draw.rectangle([(2, 2), (total_width - 2, header_height)], fill='white', outline='black', width=2)

        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()

        text = title_text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        text_x, text_y = (total_width - text_w) // 2, (header_height - text_h) // 2

        draw.text((text_x, text_y), text, fill='black', font=font)
        final_img.paste(pil_img.convert('RGB'), (0, header_height))

        vh = self.canvas.winfo_height()
        vw = self.canvas.winfo_width()
        if vh < 100: vh = 600
        if vw < 100: vw = 600

        scale = min(vw / total_width, vh / final_img.height) * 0.95
        final_img = final_img.resize((int(total_width * scale), int(final_img.height * scale)), Image.LANCZOS)

        self.tk_img = ImageTk.PhotoImage(final_img)
        self.canvas.config(image=self.tk_img, text="")