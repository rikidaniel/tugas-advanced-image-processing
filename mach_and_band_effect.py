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

        content = self.create_header("Mach Band & Brightness", "Simulasi ilusi optik Mach Band dan Adaptasi Kecerahan.")

        # Tombol Aksi Pusat
        ctrl_frame = tk.Frame(content, bg="white")
        ctrl_frame.pack(fill="x", pady=20)

        # [Perbaikan] Tambah tombol Brightness Adaptation
        ttk.Button(ctrl_frame, text="✨ Generate Mach Band",
                   command=self.show_mach_band, style="Primary.TButton").pack(side="left", padx=(0, 10), expand=True)
        
        ttk.Button(ctrl_frame, text="👁️ Brightness Adaptation",
                   command=self.show_brightness_adaptation, style="Soft.TButton").pack(side="left", expand=True)

        # Area Tampil
        preview_frame = tk.Frame(content, bg=COLORS["bg_main"], bd=2, relief="flat")
        preview_frame.pack(fill="both", expand=True)

        self.canvas = tk.Label(preview_frame, bg=COLORS["bg_main"], text="Pilih simulasi di atas",
                               fg="#6B7280", font=("Segoe UI", 12))
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)
        self.tk_img = None

    def show_mach_band(self):
        # ... (Logika Mach Band Tetap Sama)
        w = 560
        border = 1
        h_band = 120
        bands = np.zeros((h_band, w), dtype=np.uint8)
        block_w = w // 10
        for i in range(10):
            value = int(255 * i / 9)
            bands[:, i * block_w:(i + 1) * block_w] = value

        bands_with_border = cv2.copyMakeBorder(bands, border, border, border, border, cv2.BORDER_CONSTANT, value=0)
        white_space = np.ones((20, w + 2 * border), dtype=np.uint8) * 255

        block_size = 340
        illusion = np.zeros((block_size, block_size), dtype=np.uint8)
        half = block_size // 2
        illusion[0:half, 0:half] = 100
        illusion[0:half, half:block_size] = 60
        illusion[half:block_size, 0:half] = 150
        illusion[half:block_size, half:block_size] = 180

        small_box_w = 60
        small_box_h = 60
        offset_x = (half - small_box_w) // 2
        offset_y = (half - small_box_h) // 2
        square_color = 125

        coords = [(offset_x, offset_y), (half + offset_x, offset_y),
                  (offset_x, half + offset_y), (half + offset_x, half + offset_y)]
        for (ox, oy) in coords:
            cv2.rectangle(illusion, (ox, oy), (ox + small_box_w, oy + small_box_h), square_color, -1)

        illusion_resized = cv2.resize(illusion, (w, 340), interpolation=cv2.INTER_NEAREST)
        illusion_with_border = cv2.copyMakeBorder(illusion_resized, border, border, border, border, cv2.BORDER_CONSTANT,
                                                  value=0)
        combined = np.vstack([bands_with_border, white_space, illusion_with_border])
        combined = cv2.copyMakeBorder(combined, 15, 15, 15, 15, cv2.BORDER_CONSTANT, value=255)
        combined = cv2.copyMakeBorder(combined, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=0)

        self._display_final(Image.fromarray(combined), "Mach Band Effect")

    def show_brightness_adaptation(self):
        # [Perbaikan] Fitur Baru: Simultaneous Contrast
        w, h = 600, 400
        img = np.zeros((h, w), dtype=np.uint8)
        
        # Split Background: Kiri Gelap (50), Kanan Terang (200)
        img[:, :w//2] = 50
        img[:, w//2:] = 200
        
        # Kotak Kecil di tengah: Intensitas SAMA (125)
        box_size = 80
        center_y = h // 2
        center_x_left = w // 4
        center_x_right = (w // 4) * 3
        
        # Gambar kotak kiri
        img[center_y-box_size//2 : center_y+box_size//2, 
            center_x_left-box_size//2 : center_x_left+box_size//2] = 125
            
        # Gambar kotak kanan
        img[center_y-box_size//2 : center_y+box_size//2, 
            center_x_right-box_size//2 : center_x_right+box_size//2] = 125
            
        self._display_final(Image.fromarray(img), "Brightness Adaptation (Simultaneous Contrast)")

    def _display_final(self, pil_img, title_text):
        # Helper untuk menampilkan gambar dengan header
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

        draw.rectangle([(text_x - 5, text_y - 5), (text_x + text_w + 5, text_y + text_h + 5)], fill='yellow')
        draw.text((text_x, text_y), text, fill='black', font=font)
        final_img.paste(pil_img.convert('RGB'), (0, header_height))

        # Resize agar pas di layar
        vh = self.canvas.winfo_height()
        vw = self.canvas.winfo_width()
        if vh < 100: vh = 600
        if vw < 100: vw = 600

        scale = min(vw / total_width, vh / final_img.height) * 0.95
        final_img = final_img.resize((int(total_width * scale), int(final_img.height * scale)), Image.LANCZOS)

        self.tk_img = ImageTk.PhotoImage(final_img)
        self.canvas.config(image=self.tk_img, text="")