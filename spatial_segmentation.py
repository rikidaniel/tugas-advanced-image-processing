import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import random
from base_frame import BaseFrame


class SpatialSegmentationApp(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)

        content = self.create_header("Spatial Filtering & Segmentation",
                                     "Smoothing, Sharpening, & Segmentation (Line/Point Detection).")

        # --- Control Panel ---
        ctrl_frame = ttk.LabelFrame(content, text="Panel Kontrol", padding=15)
        ctrl_frame.pack(fill="x", pady=(0, 20))

        # Row 1: Image Controls
        row1 = ttk.Frame(ctrl_frame)
        row1.pack(fill="x", pady=5)
        ttk.Button(row1, text="📂 Buka Gambar", command=self.open_image, style="Primary.TButton").pack(side="left",
                                                                                                      padx=(0, 15))

        ttk.Button(row1, text="🧂 Add Salt & Pepper", command=self.add_salt_pepper_noise,
                   style="Soft.TButton").pack(side="left", padx=(0, 15))

        ttk.Button(row1, text="↺ Reset", command=self.reset_image, style="Danger.TButton").pack(side="left")

        # Row 2: Filter Controls
        row2 = ttk.Frame(ctrl_frame)
        row2.pack(fill="x", pady=(20, 5))

        ttk.Label(row2, text="Kategori Operasi:", style="Sub.TLabel").pack(side="left")
        self.category_var = tk.StringVar(value="Smoothing")
        self.cb_category = ttk.Combobox(row2, textvariable=self.category_var, state="readonly", width=25)
        # Penamaan kategori disesuaikan
        self.cb_category['values'] = ["Smoothing (Lowpass)", "Sharpening (Highpass)", "Segmentation (Detection)"]
        self.cb_category.pack(side="left", padx=(5, 15))
        self.cb_category.bind("<<ComboboxSelected>>", self.update_filter_types)

        ttk.Label(row2, text="Jenis Filter:", style="Sub.TLabel").pack(side="left")
        self.filter_var = tk.StringVar()
        self.cb_filter = ttk.Combobox(row2, textvariable=self.filter_var, state="readonly", width=40)
        self.cb_filter.pack(side="left", padx=(5, 15))

        # Slider Threshold (Hanya muncul saat Segmentation)
        self.thresh_frame = tk.Frame(ctrl_frame, bg="white")
        tk.Label(self.thresh_frame, text="Threshold:", bg="white").pack(side="left")
        self.thresh_val = tk.IntVar(value=100)
        self.thresh_scale = ttk.Scale(self.thresh_frame, from_=0, to=255, variable=self.thresh_val, orient="horizontal",
                                      length=200)
        self.thresh_scale.pack(side="left", padx=5)
        self.lbl_thresh = tk.Label(self.thresh_frame, text="100", bg="white", width=3)
        self.lbl_thresh.pack(side="left")
        self.thresh_scale.configure(command=lambda v: self.lbl_thresh.config(text=f"{int(float(v))}"))

        ttk.Button(row2, text="▶ Apply", command=self.apply_filter, style="Soft.TButton").pack(side="left", padx=20)

        # --- Image Display Area ---
        img_grid = ttk.Frame(content)
        img_grid.pack(fill="both", expand=True)
        img_grid.columnconfigure(0, weight=1)
        img_grid.columnconfigure(1, weight=1)

        f_left = ttk.Frame(img_grid, style="Card.TFrame")
        f_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(f_left, text="Original Image", bg="#F1F5F9", pady=8, font=("Segoe UI", 10, "bold")).pack(fill="x")
        self.lbl_original = tk.Label(f_left, bg="#F1F5F9")
        self.lbl_original.pack(fill="both", expand=True)

        f_right = ttk.Frame(img_grid, style="Card.TFrame")
        f_right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.lbl_res_title = tk.Label(f_right, text="Processed Result", bg="#F1F5F9", pady=8,
                                      font=("Segoe UI", 10, "bold"))
        self.lbl_res_title.pack(fill="x")
        self.lbl_result = tk.Label(f_right, bg="#F1F5F9")
        self.lbl_result.pack(fill="both", expand=True)

        self.original_img_cv = None
        self.processed_img_cv = None

        self.update_filter_types()

    def update_filter_types(self, event=None):
        category = self.category_var.get()

        if "Smoothing" in category:
            options = [
                "Averaging Filter (Mean) 3x3",
                "Averaging Filter (Mean) 5x5",
                "Averaging Filter (Mean) 9x9",
                "Averaging Filter (Mean) 15x15",
                "Averaging Filter (Mean) 35x35",
                "Median Filter 3x3",
                "Median Filter 5x5"
            ]
            self.thresh_frame.pack_forget()

        elif "Sharpening" in category:
            # [PERBAIKAN] Nama Filter Sharpening lebih eksplisit
            options = [
                "Laplacian (Center -4) -> Standard",
                "Laplacian (Center -8) -> Include Diagonals",
                "Laplacian (Center +8) -> Inverted Center",
                "High-Boost Filtering (A=1.2)",
            ]
            self.thresh_frame.pack_forget()

        elif "Segmentation" in category:
            options = [
                "Point Detection (Laplacian Mask)",
                "Line Detection: Horizontal",
                "Line Detection: Vertical",
                "Line Detection: +45 Degree",
                "Line Detection: -45 Degree"
            ]
            self.thresh_frame.pack(fill="x", pady=(5, 0), after=self.cb_filter.master)
        else:
            options = []
            self.thresh_frame.pack_forget()

        self.cb_filter['values'] = options
        if options:
            self.cb_filter.current(0)

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.tif")])
        if not path: return
        img = cv2.imread(path)
        if img is None: return
        self.original_img_cv = img
        self.display_image(self.original_img_cv, self.lbl_original)
        self.reset_image()

    def reset_image(self):
        self.processed_img_cv = None
        self.lbl_result.config(image="")
        self.lbl_result.image = None
        if self.original_img_cv is not None:
            self.display_image(self.original_img_cv, self.lbl_original)

    def add_salt_pepper_noise(self):
        if self.original_img_cv is None: return
        row, col = self.original_img_cv.shape[:2]
        noisy = self.original_img_cv.copy()
        number_of_pixels = random.randint(300, 5000)

        # Salt
        for i in range(number_of_pixels):
            y = random.randint(0, row - 1)
            x = random.randint(0, col - 1)
            noisy[y][x] = 255
        # Pepper
        for i in range(number_of_pixels):
            y = random.randint(0, row - 1)
            x = random.randint(0, col - 1)
            noisy[y][x] = 0

        self.original_img_cv = noisy
        self.display_image(self.original_img_cv, self.lbl_original)
        messagebox.showinfo("Info", "Noise ditambahkan. Coba gunakan 'Median Filter'.")

    def display_image(self, cv_img, label_widget):
        if cv_img is None: return
        try:
            if len(cv_img.shape) == 2:
                img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
            else:
                img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)
            pil_img.thumbnail((400, 400), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil_img)
            label_widget.config(image=tk_img)
            label_widget.image = tk_img
        except Exception as e:
            print(f"Error: {e}")

    def apply_filter(self):
        if self.original_img_cv is None: return
        category = self.category_var.get()
        filter_type = self.filter_var.get()

        img_src = self.original_img_cv.copy()

        # Konversi ke Grayscale untuk operasi filtering yang membutuhkan 1 channel
        if len(img_src.shape) == 3:
            img_gray = cv2.cvtColor(img_src, cv2.COLOR_BGR2GRAY)
        else:
            img_gray = img_src

        result = None

        try:
            # 1. SMOOTHING
            if "Smoothing" in category:
                k = int(filter_type.split()[-1].split('x')[0])  # Ambil angka dari nama filter "3x3"
                if "Averaging" in filter_type:
                    result = cv2.blur(img_src, (k, k))
                elif "Median" in filter_type:
                    result = cv2.medianBlur(img_src, k)
                self.lbl_res_title.config(text=f"Result: {filter_type}")

            # 2. SHARPENING
            elif "Sharpening" in category:
                # Menggunakan Kernel Manual untuk kontrol penuh (sesuai Textbooks)
                kernel = None

                if "Center -4" in filter_type:
                    # Kernel Standard (Isotropic)
                    kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
                    # Composite = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]
                    sharpening_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])

                elif "Center -8" in filter_type:
                    # Termasuk Diagonal
                    sharpening_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])

                elif "Center +8" in filter_type:
                    # Varian lain
                    sharpening_kernel = np.array([[1, 1, 1], [1, -7, 1], [1, 1, 1]])

                elif "High-Boost" in filter_type:
                    # A = 1.2
                    A = 1.2
                    blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
                    mask = cv2.addWeighted(img_gray.astype(float), 1.0, blur.astype(float), -1.0, 0)
                    res_float = img_gray.astype(float) + A * mask
                    result = np.clip(res_float, 0, 255).astype(np.uint8)

                if result is None and "Laplacian" in filter_type:
                    # Terapkan kernel sharpening langsung
                    result = cv2.filter2D(img_src, -1, sharpening_kernel)

                self.lbl_res_title.config(text=f"Result: {filter_type}")

            # 3. SEGMENTATION
            elif "Segmentation" in category:
                kernel = None
                if "Point" in filter_type:
                    kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
                elif "Horizontal" in filter_type:
                    kernel = np.array([[-1, -1, -1], [2, 2, 2], [-1, -1, -1]])
                elif "Vertical" in filter_type:
                    kernel = np.array([[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]])
                elif "+45" in filter_type:
                    kernel = np.array([[-1, -1, 2], [-1, 2, -1], [2, -1, -1]])
                elif "-45" in filter_type:
                    kernel = np.array([[2, -1, -1], [-1, 2, -1], [-1, -1, 2]])

                if kernel is not None:
                    # Filtering
                    filtered = cv2.filter2D(img_gray, cv2.CV_64F, kernel)
                    abs_filtered = cv2.convertScaleAbs(filtered)

                    # Thresholding untuk segmentasi tegas (Hitam/Putih)
                    thresh_val = self.thresh_val.get()
                    _, result_bin = cv2.threshold(abs_filtered, thresh_val, 255, cv2.THRESH_BINARY)
                    result = result_bin  # Output biner

                self.lbl_res_title.config(text=f"Segmented: {filter_type} (T={self.thresh_val.get()})")

            self.processed_img_cv = result
            self.display_image(self.processed_img_cv, self.lbl_result)

        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {e}")