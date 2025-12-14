import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
from base_frame import BaseFrame
from styles import COLORS


class ImageViewerApp(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)

        content = self.create_header("Penampil Citra", "Membuka dan menampilkan citra dalam mode Warna atau Grayscale.")

        # Toolbar di atas
        toolbar = tk.Frame(content, bg="white")
        toolbar.pack(fill="x", pady=(0, 20))

        ttk.Button(toolbar, text="📂 Buka Gambar", command=self.open_image, style="Primary.TButton").pack(side="left",
                                                                                                         padx=(0, 10))
        ttk.Button(toolbar, text="Mode Grayscale", command=self.show_gray, style="Soft.TButton").pack(side="left",
                                                                                                      padx=5)
        ttk.Button(toolbar, text="Mode Warna", command=self.show_color, style="Soft.TButton").pack(side="left", padx=5)

        # Area Canvas (Dengan Border Hijau Tipis)
        canvas_frame = tk.Frame(content, bg=COLORS["bg_main"], bd=2, relief="flat")
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Label(canvas_frame, bg=COLORS["bg_main"], text="Belum ada gambar yang dipilih",
                               fg="#6B7280", font=("Segoe UI", 12))
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)

        self.img_rgb = None
        self.img_gray = None
        self.tk_img = None

    def open_image(self):
        # [Perbaikan] Menambahkan *.tiff dan *.tif agar konsisten dengan modul lain
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.tif")])
        if not path: return

        img = cv2.imread(path)
        if img is None:
            messagebox.showerror("Error", "Gagal membuka gambar.")
            return

        self.img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.show_on_canvas(self.img_rgb)

    def show_gray(self):
        if self.img_gray is None:
            messagebox.showwarning("Info", "Silakan buka gambar terlebih dahulu.")
            return
        self.show_on_canvas(self.img_gray, is_gray=True)

    def show_color(self):
        if self.img_rgb is None:
            messagebox.showwarning("Info", "Silakan buka gambar terlebih dahulu.")
            return
        self.show_on_canvas(self.img_rgb)

    def show_on_canvas(self, img, is_gray=False):
        vh = self.canvas.winfo_height()
        vw = self.canvas.winfo_width()
        if vh < 100: vh = 500
        if vw < 100: vw = 800

        h, w = img.shape[:2]
        scale = min(vw / w, vh / h) * 0.95
        new_w, new_h = int(w * scale), int(h * scale)

        pil_img = Image.fromarray(img).resize((new_w, new_h), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(pil_img)
        self.canvas.config(image=self.tk_img, text="")