import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import numpy as np
import cv2


class MachBandApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Program 2 - Mach Band Effect")
        self.root.geometry("800x750")

        header_frame = tk.Frame(root)
        header_frame.pack(fill="x", pady=5)

        btn_mach = tk.Button(header_frame,
                             text="Tampilkan Mach Band Effect",
                             command=self.show_mach_band)
        btn_mach.pack(side="left", padx=10, pady=5)

        nim_label = tk.Label(header_frame,
                             text="14240032",
                             font=("Arial", 14, "bold"))
        nim_label.pack(side="left", padx=20)

        nama_label = tk.Label(header_frame,
                              text="Riki Daniel Tanebeth",
                              font=("Arial", 14, "bold"))
        nama_label.pack(side="left", padx=20)

        self.canvas = tk.Label(root, bg="white")
        self.canvas.pack(expand=True, fill="both", padx=10, pady=10)

        # HAPUS tombol Keluar yang sebelumnya ada di sini

        self.tk_img = None

    def show_mach_band(self):
        w = 560
        border = 1

        h_band = 120
        bands = np.zeros((h_band, w), dtype=np.uint8)
        block_w = w // 10
        for i in range(10):
            value = int(255 * i / 9)
            bands[:, i * block_w:(i + 1) * block_w] = value

        bands_with_border = cv2.copyMakeBorder(
            bands, border, border, border, border,
            cv2.BORDER_CONSTANT, value=0
        )

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

        cv2.rectangle(illusion, (offset_x, offset_y),
                      (offset_x + small_box_w, offset_y + small_box_h),
                      square_color, -1)
        cv2.rectangle(illusion, (half + offset_x, offset_y),
                      (half + offset_x + small_box_w, offset_y + small_box_h),
                      square_color, -1)
        cv2.rectangle(illusion, (offset_x, half + offset_y),
                      (offset_x + small_box_w, half + offset_y + small_box_h),
                      square_color, -1)
        cv2.rectangle(illusion, (half + offset_x, half + offset_y),
                      (half + offset_x + small_box_w, half + offset_y + small_box_h),
                      square_color, -1)

        illusion_resized = cv2.resize(illusion, (w, 340), interpolation=cv2.INTER_NEAREST)
        illusion_with_border = cv2.copyMakeBorder(
            illusion_resized, border, border, border, border,
            cv2.BORDER_CONSTANT, value=0
        )

        combined = np.vstack([bands_with_border, white_space, illusion_with_border])

        combined = cv2.copyMakeBorder(combined, 15, 15, 15, 15,
                                      cv2.BORDER_CONSTANT, value=255)
        combined = cv2.copyMakeBorder(combined, 2, 2, 2, 2,
                                      cv2.BORDER_CONSTANT, value=0)

        pil_img = Image.fromarray(combined)

        header_height = 40
        total_width = pil_img.width
        final_img = Image.new('RGB', (total_width, pil_img.height + header_height), 'white')

        draw = ImageDraw.Draw(final_img)
        draw.rectangle([(2, 2), (total_width - 2, header_height)],
                       fill='white', outline='black', width=2)

        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", 16)
            except:
                font = ImageFont.load_default()

        text = "mach band effect"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = (total_width - text_width) // 2
        text_y = (header_height - text_height) // 2

        padding = 5
        draw.rectangle([(text_x - padding, text_y - padding),
                        (text_x + text_width + padding, text_y + text_height + padding)],
                       fill='yellow')
        draw.text((text_x, text_y), text, fill='black', font=font)

        final_img.paste(pil_img.convert('RGB'), (0, header_height))

        final_img = final_img.resize((600, 600), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(final_img)
        self.canvas.config(image=self.tk_img)


if __name__ == "__main__":
    root = tk.Tk()
    app = MachBandApp(root)
    root.mainloop()
