import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
from base_frame import BaseFrame
from styles import COLORS

IMG_SIZE = 500  # Ukuran standar sesuai PDF biasanya


class FrequencyFilterApp(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.original_img = None
        self.processed_img = None

        # --- Header ---
        content = self.create_header("Frequency Domain Filtering (Pg 14-16)",
                                     "Ideal, Butterworth, & Gaussian Filters (Lowpass & Highpass).")

        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=0)  # Control panel fixed width
        content.columnconfigure(2, weight=1)
        content.rowconfigure(0, weight=1)

        # --- PANEL KIRI: INPUT ---
        left_frame = ttk.Frame(content, style="Card.TFrame")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        tk.Label(left_frame, text="Input Image (Spatial)", bg="#F1F5F9", font=("Segoe UI", 10, "bold")).pack(pady=5)
        self.lbl_input = tk.Label(left_frame, bg="black", bd=1, relief="solid")
        self.lbl_input.pack(expand=True, fill="both", padx=10, pady=10)

        # --- PANEL TENGAH: KONTROL ---
        ctrl_frame = ttk.Frame(content, padding=15)
        ctrl_frame.grid(row=0, column=1, sticky="ns")

        # 1. Source Selection
        ttk.Label(ctrl_frame, text="1. Input Source:", style="Sub.TLabel").pack(anchor="w", pady=(0, 5))

        # Tombol khusus untuk generate pola "a" sesuai PDF
        ttk.Button(ctrl_frame, text="📄 Generate Pattern 'a' (PDF)",
                   command=self.generate_pattern_a, style="Primary.TButton").pack(fill="x", pady=2)
        ttk.Button(ctrl_frame, text="📂 Load Custom Image",
                   command=self.load_image, style="Soft.TButton").pack(fill="x", pady=2)

        ttk.Separator(ctrl_frame, orient="horizontal").pack(fill="x", pady=15)

        # 2. Filter Parameters
        ttk.Label(ctrl_frame, text="2. Filter Settings:", style="Sub.TLabel").pack(anchor="w", pady=(0, 5))

        # Filter Type
        tk.Label(ctrl_frame, text="Filter Shape:", bg=COLORS["bg_main"]).pack(anchor="w")
        self.filter_shape = tk.StringVar(value="Ideal")
        cb_shape = ttk.Combobox(ctrl_frame, textvariable=self.filter_shape,
                                values=["Ideal", "Butterworth", "Gaussian"], state="readonly")
        cb_shape.pack(fill="x", pady=(0, 10))
        cb_shape.bind("<<ComboboxSelected>>", self.apply_filter)

        # Filter Mode (Lowpass/Highpass)
        tk.Label(ctrl_frame, text="Mode:", bg=COLORS["bg_main"]).pack(anchor="w")
        self.filter_mode = tk.StringVar(value="Lowpass")
        cb_mode = ttk.Combobox(ctrl_frame, textvariable=self.filter_mode,
                               values=["Lowpass", "Highpass"], state="readonly")
        cb_mode.pack(fill="x", pady=(0, 10))
        cb_mode.bind("<<ComboboxSelected>>", self.apply_filter)

        # Cutoff Radius (D0)
        tk.Label(ctrl_frame, text="Cutoff Radius (D0):", bg=COLORS["bg_main"]).pack(anchor="w")

        # Slider Radius
        self.d0_var = tk.IntVar(value=50)
        self.lbl_d0 = tk.Label(ctrl_frame, text="50", bg=COLORS["bg_main"], fg=COLORS["primary"],
                               font=("Segoe UI", 10, "bold"))
        self.lbl_d0.pack(anchor="e")

        scale_d0 = ttk.Scale(ctrl_frame, from_=5, to=230, variable=self.d0_var, command=self.update_d0_label)
        scale_d0.pack(fill="x", pady=(0, 5))

        # Preset Buttons untuk Radius sesuai PDF
        btn_radii = tk.Frame(ctrl_frame, bg=COLORS["bg_main"])
        btn_radii.pack(fill="x", pady=5)
        for r in [5, 15, 30, 80, 230]:
            tk.Button(btn_radii, text=str(r), font=("Segoe UI", 8), width=3,
                      command=lambda v=r: self.set_radius(v)).pack(side="left", padx=1)

        # Butterworth Order (n)
        tk.Label(ctrl_frame, text="Butterworth Order (n):", bg=COLORS["bg_main"]).pack(anchor="w", pady=(10, 0))
        self.n_var = tk.IntVar(value=2)
        ttk.Scale(ctrl_frame, from_=1, to=10, variable=self.n_var, command=lambda v: self.apply_filter()).pack(fill="x")

        ttk.Separator(ctrl_frame, orient="horizontal").pack(fill="x", pady=15)

        # Tombol Aksi
        ttk.Button(ctrl_frame, text="▶ Apply Filter", command=self.apply_filter, style="Primary.TButton").pack(fill="x",
                                                                                                               pady=5)

        # --- TOMBOL RESET (BARU) ---
        ttk.Button(ctrl_frame, text="↺ Reset", command=self.reset_app, style="Danger.TButton").pack(fill="x", pady=5)

        # --- PANEL KANAN: OUTPUT ---
        right_frame = ttk.Frame(content, style="Card.TFrame")
        right_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        # Header kanan
        rh = tk.Frame(right_frame, bg="#F1F5F9")
        rh.pack(fill="x", pady=5, padx=10)
        tk.Label(rh, text="Filtered Output", bg="#F1F5F9", font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Button(rh, text="💾 Save", bd=0, bg="#ddd", command=self.save_result).pack(side="right")

        self.lbl_output = tk.Label(right_frame, bg="black", bd=1, relief="solid")
        self.lbl_output.pack(expand=True, fill="both", padx=10, pady=10)

        # Init default image
        self.generate_pattern_a()

    def reset_app(self):
        # Reset Parameter ke Default
        self.filter_shape.set("Ideal")
        self.filter_mode.set("Lowpass")
        self.set_radius(50)
        self.n_var.set(2)

        # Reset Gambar ke Pattern 'a'
        self.generate_pattern_a()

    def generate_pattern_a(self):
        # Membuat gambar teks "a" simulasi PDF Halaman 14
        img = np.ones((IMG_SIZE, IMG_SIZE), dtype=np.uint8) * 255  # White BG

        font = cv2.FONT_HERSHEY_TRIPLEX
        text = "a"
        font_scale = 15
        thickness = 25

        # Cari ukuran text agar center
        (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_org = ((IMG_SIZE - tw) // 2, (IMG_SIZE + th) // 2)

        cv2.putText(img, text, text_org, font, font_scale, (0), thickness)

        self.original_img = img
        self.display_image(self.original_img, self.lbl_input)
        self.apply_filter()  # Auto run

    def load_image(self):
        path = filedialog.askopenfilename()
        if not path: return
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None: return
        self.original_img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
        self.display_image(self.original_img, self.lbl_input)
        self.apply_filter()

    def set_radius(self, val):
        self.d0_var.set(val)
        self.update_d0_label(val)

    def update_d0_label(self, val):
        self.lbl_d0.config(text=f"{float(val):.0f}")
        self.apply_filter()

    def apply_filter(self, event=None):
        if self.original_img is None: return

        img = self.original_img.astype(np.float32)
        rows, cols = img.shape

        # 1. FFT
        dft = np.fft.fft2(img)
        dft_shift = np.fft.fftshift(dft)

        # 2. Buat Mask Filter H(u,v)
        shape = self.filter_shape.get()
        mode = self.filter_mode.get()
        D0 = self.d0_var.get()
        n = self.n_var.get()  # Order Butterworth

        H = np.zeros((rows, cols), dtype=np.float32)
        crow, ccol = rows // 2, cols // 2  # Pusat

        # Grid jarak Euclidean dari pusat
        u, v = np.meshgrid(np.arange(cols), np.arange(rows))
        D = np.sqrt((u - ccol) ** 2 + (v - crow) ** 2)
        D = np.maximum(D, 1e-5)

        # --- LOGIKA FILTER ---
        if shape == "Ideal":
            if mode == "Lowpass":
                H[D <= D0] = 1
            else:  # Highpass
                H[D > D0] = 1

        elif shape == "Butterworth":
            # H_lp = 1 / (1 + (D/D0)^(2n))
            H_lp = 1 / (1 + (D / D0) ** (2 * n))
            if mode == "Lowpass":
                H = H_lp
            else:
                H = 1 - H_lp

        elif shape == "Gaussian":
            # H_lp = exp(-D^2 / (2*D0^2))
            H_lp = np.exp(-(D ** 2) / (2 * (D0 ** 2)))
            if mode == "Lowpass":
                H = H_lp
            else:
                H = 1 - H_lp

        # 3. Filtering
        fshift_filtered = dft_shift * H

        # 4. Inverse FFT
        f_ishift = np.fft.ifftshift(fshift_filtered)
        img_back = np.fft.ifft2(f_ishift)
        img_back = np.abs(img_back)

        # Normalize 0-255
        res = cv2.normalize(img_back, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        self.processed_img = res
        self.display_image(res, self.lbl_output)

    def display_image(self, cv_img, label):
        h, w = cv_img.shape
        img_pil = Image.fromarray(cv_img).resize((300, 300), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(img_pil)
        label.config(image=tk_img)
        label.image = tk_img

    def save_result(self):
        if self.processed_img is not None:
            self.save_image_cv(self.processed_img, "freq_filter_result")