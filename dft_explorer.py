import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from PIL import Image, ImageTk
import cv2

APP_TITLE = "2-D DFT Viewer"
IMG_H, IMG_W = 512, 512
RECT_H, RECT_W = 20, 40


def generate_spatial_image(h=IMG_H, w=IMG_W, rect_h=RECT_H, rect_w=RECT_W, angle=0.0, invert=False):
    img = np.zeros((h, w), dtype=np.float32)
    cy, cx = h // 2, w // 2
    y0, y1 = cy - rect_h // 2, cy + rect_h // 2
    x0, x1 = cx - rect_w // 2, cx + rect_w // 2
    img[y0:y1, x0:x1] = 1.0

    M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
    img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR)

    if invert:
        img = 1.0 - img

    img = np.clip(img, 0.0, 1.0)
    return img


def to_u8(a):
    a = a - a.min()
    mx = a.max()
    if mx > 0:
        a = a / mx
    return (a * 255).astype(np.uint8)


def compute_spectrum(img):
    F = np.fft.fft2(img)
    F = np.fft.fftshift(F)
    mag = np.abs(F)
    mag_log = np.log1p(mag)
    return mag_log


class DftApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.configure(bg="#111")
        self.root.geometry("1300x600")
        self.root.resizable(False, False)

        self.left_imgtk = None
        self.right_imgtk = None

        self.angle_var = tk.DoubleVar(value=0.0)
        self.invert_var = tk.BooleanVar(value=False)

        wrapper = ttk.Frame(self.root, padding=10)
        wrapper.pack(fill="both", expand=True)

        left = ttk.Frame(wrapper)
        settings = ttk.Frame(wrapper)
        right = ttk.Frame(wrapper)

        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        settings.grid(row=0, column=1, sticky="ns", padx=10)
        right.grid(row=0, column=2, sticky="nsew")

        wrapper.columnconfigure(0, weight=1)
        wrapper.columnconfigure(1, weight=0)
        wrapper.columnconfigure(2, weight=1)
        wrapper.rowconfigure(0, weight=1)

        # --- Panel Kiri (Gambar Spasial) ---
        self.lbl_left_title = ttk.Label(left, text=f"Spatial Image", font=("Segoe UI", 11, "bold"))
        self.lbl_left_title.pack(pady=(0, 5))
        self.left_panel = ttk.Label(left)
        self.left_panel.pack()

        # --- Panel Pengaturan (Tengah) ---
        settings_frame = ttk.LabelFrame(settings, text="Pengaturan Spasial")
        settings_frame.pack(pady=5, fill="x")

        ttk.Label(settings_frame, text="Rotasi (Derajat):").pack(padx=10, pady=(10, 0))
        self.angle_label = ttk.Label(settings_frame, text="0.0°")
        self.angle_label.pack(padx=10)
        angle_slider = ttk.Scale(settings_frame, from_=-90, to=90, variable=self.angle_var, orient="horizontal",
                                 command=self._update_angle_label)
        angle_slider.pack(padx=10, fill="x", expand=True)

        chk_invert = ttk.Checkbutton(settings_frame, text="Tukar Warna (Invert)", variable=self.invert_var)
        chk_invert.pack(padx=10, pady=10)

        btn_apply = ttk.Button(settings_frame, text="Terapkan Pengaturan", command=self.apply_changes)
        btn_apply.pack(padx=10, pady=5, fill="x")

        # --- Tombol Reset Baru ---
        btn_reset = ttk.Button(settings_frame, text="Reset", command=self.on_reset)
        btn_reset.pack(padx=10, pady=5, fill="x")
        # -------------------------

        # --- Panel Kanan (Spektrum) ---
        self.lbl_right_title = ttk.Label(right, text="Centered 2-D DFT Magnitude (log)", font=("Segoe UI", 11, "bold"))
        self.lbl_right_title.pack(pady=(0, 5))
        self.right_panel = ttk.Label(right, text="Klik 'Terapkan Pengaturan' untuk menampilkan.", anchor="center")
        self.right_panel.pack()

        # Buat gambar & spektrum awal
        self.apply_changes()

    def _update_angle_label(self, value_str):
        val = self.angle_var.get()
        self.angle_label.configure(text=f"{val:.1f}°")

    def apply_changes(self):
        # 1. Dapatkan nilai pengaturan terbaru
        angle = self.angle_var.get()
        invert = self.invert_var.get()

        # 2. Buat gambar spasial baru
        self.img_np = generate_spatial_image(angle=angle, invert=invert)

        # 3. Tampilkan di panel kiri
        self.show_left(self.img_np)

        # 4. Hitung dan tampilkan spektrum di panel kanan
        self.on_view()

    # --- Fungsi Baru untuk Reset ---
    def on_reset(self):
        # 1. Atur ulang variabel
        self.angle_var.set(0.0)
        self.invert_var.set(False)

        # 2. Perbarui label sudut secara manual
        self.angle_label.configure(text="0.0°")

        # 3. Terapkan perubahan (ini akan memperbarui kedua gambar)
        self.apply_changes()

    # -------------------------------

    def show_left(self, img_np):
        im = Image.fromarray(to_u8(img_np), mode="L").resize((512, 512), Image.NEAREST)
        self.left_imgtk = ImageTk.PhotoImage(im)
        self.left_panel.configure(image=self.left_imgtk)

    def on_view(self):
        try:
            spec = compute_spectrum(self.img_np)
            im = Image.fromarray(to_u8(spec), mode="L").resize((512, 512), Image.NEAREST)
            self.right_imgtk = ImageTk.PhotoImage(im)
            self.right_panel.configure(image=self.right_imgtk, text="")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = tk.Tk()
    app = DftApp(root)
    root.mainloop()