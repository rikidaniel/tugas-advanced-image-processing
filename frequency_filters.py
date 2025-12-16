import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import cv2
from PIL import Image, ImageTk
from base_frame import BaseFrame


class FrequencyFilterApp(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)
        content = self.create_header("Frequency Domain Filtering",
                                     "Implementasi Ideal, Butterworth, & Gaussian Filters.")

        ctrl_frame = ttk.LabelFrame(content, text="Panel Kontrol", padding=15)
        ctrl_frame.pack(fill="x", pady=(0, 20))

        # Row 1
        row1 = ttk.Frame(ctrl_frame)
        row1.pack(fill="x", pady=5)
        ttk.Button(row1, text="📂 Buka Gambar", command=self.open_image, style="Primary.TButton").pack(side="left",
                                                                                                      padx=(0, 15))
        ttk.Button(row1, text="↺ Reset", command=self.reset_image, style="Danger.TButton").pack(side="left")

        # [FITUR BARU] Toggle View Filter Mask
        self.view_mode = tk.StringVar(value="Result")
        ttk.Checkbutton(row1, text="Show Filter Mask (Spectrum)", variable=self.view_mode,
                        onvalue="Mask", offvalue="Result", command=self.toggle_view).pack(side="right")

        # Row 2
        row2 = ttk.Frame(ctrl_frame)
        row2.pack(fill="x", pady=(20, 5))
        ttk.Label(row2, text="Jenis:", style="Sub.TLabel").pack(side="left")
        self.filter_type_var = tk.StringVar(value="Ideal")
        ttk.Combobox(row2, textvariable=self.filter_type_var, values=["Ideal", "Butterworth", "Gaussian"],
                     state="readonly", width=12).pack(side="left", padx=5)

        ttk.Label(row2, text="Mode:", style="Sub.TLabel").pack(side="left", padx=(10, 0))
        self.pass_type_var = tk.StringVar(value="Lowpass")
        ttk.Combobox(row2, textvariable=self.pass_type_var, values=["Lowpass", "Highpass"], state="readonly",
                     width=10).pack(side="left", padx=5)

        ttk.Label(row2, text="D0:", style="Sub.TLabel").pack(side="left", padx=(10, 0))
        self.d0_var = tk.StringVar(value="30")
        ttk.Combobox(row2, textvariable=self.d0_var, values=["5", "15", "30", "80", "230"], width=5).pack(side="left",
                                                                                                          padx=5)

        ttk.Label(row2, text="Orde(n):", style="Sub.TLabel").pack(side="left", padx=(10, 0))
        self.n_var = tk.IntVar(value=2)
        ttk.Entry(row2, textvariable=self.n_var, width=5).pack(side="left", padx=5)

        ttk.Button(row2, text="▶ Apply", command=self.apply_filter, style="Soft.TButton").pack(side="left", padx=20)

        # Image Grid
        img_grid = ttk.Frame(content)
        img_grid.pack(fill="both", expand=True)
        img_grid.columnconfigure(0, weight=1);
        img_grid.columnconfigure(1, weight=1)

        f_left = ttk.Frame(img_grid, style="Card.TFrame")
        f_left.grid(row=0, column=0, sticky="nsew", padx=5)
        tk.Label(f_left, text="Original Image", bg="#F1F5F9", font=("Segoe UI", 10, "bold")).pack(fill="x")
        self.lbl_original = tk.Label(f_left, bg="#F1F5F9")
        self.lbl_original.pack(fill="both", expand=True)

        f_right = ttk.Frame(img_grid, style="Card.TFrame")
        f_right.grid(row=0, column=1, sticky="nsew", padx=5)
        self.lbl_res_title = tk.Label(f_right, text="Filtered Result", bg="#F1F5F9", font=("Segoe UI", 10, "bold"))
        self.lbl_res_title.pack(fill="x")
        self.lbl_filtered = tk.Label(f_right, bg="#F1F5F9")
        self.lbl_filtered.pack(fill="both", expand=True)

        self.gray_img = None;
        self.original_img = None
        self.current_mask = None;
        self.current_result = None

    def open_image(self):
        path = filedialog.askopenfilename()
        if not path: return
        img = cv2.imread(path)
        if img is None: return
        img = cv2.resize(img, (512, 512))
        self.gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        self.original_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        self.show_img(self.lbl_original, self.original_img)
        self.lbl_filtered.config(image="")

    def reset_image(self):
        if self.original_img: self.show_img(self.lbl_original, self.original_img); self.lbl_filtered.config(image="")

    def show_img(self, lbl, pil):
        display = pil.resize((350, 350), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(display)
        lbl.config(image=tk_img);
        lbl.image = tk_img

    def toggle_view(self):
        if self.view_mode.get() == "Mask" and self.current_mask is not None:
            # Tampilkan Mask (0-1) sebagai gambar (0-255)
            mask_disp = (self.current_mask * 255).astype(np.uint8)
            self.lbl_res_title.config(text="Filter Frequency Spectrum (H)")
            self.show_img(self.lbl_filtered, Image.fromarray(mask_disp))
        elif self.current_result is not None:
            self.lbl_res_title.config(text="Spatial Result")
            self.show_img(self.lbl_filtered, Image.fromarray(self.current_result))

    def apply_filter(self):
        if self.gray_img is None: return
        try:
            d0 = float(self.d0_var.get())
        except:
            d0 = 30.0
        n = self.n_var.get()

        rows, cols = self.gray_img.shape
        crow, ccol = rows // 2, cols // 2
        u = np.arange(rows);
        v = np.arange(cols)
        U, V = np.meshgrid(v, u)
        D = np.sqrt((U - ccol) ** 2 + (V - crow) ** 2)

        ft = self.filter_type_var.get();
        mode = self.pass_type_var.get()
        if ft == "Ideal":
            H = (D <= d0) if mode == "Lowpass" else (D > d0)
        elif ft == "Butterworth":
            H = 1 / (1 + (D / d0) ** (2 * n)) if mode == "Lowpass" else 1 / (1 + (d0 / (D + 1e-5)) ** (2 * n))
        elif ft == "Gaussian":
            H = np.exp(-(D ** 2) / (2 * d0 ** 2))
            if mode == "Highpass": H = 1 - H

        self.current_mask = H

        f = np.fft.fftshift(np.fft.fft2(self.gray_img))
        G = f * H
        g = np.abs(np.fft.ifft2(np.fft.ifftshift(G)))
        self.current_result = np.clip(g, 0, 255).astype(np.uint8)

        self.toggle_view()  # Update display sesuai mode toggle