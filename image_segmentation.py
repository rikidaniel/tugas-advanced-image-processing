import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
from base_frame import BaseFrame
from styles import COLORS


class ImageSegmentationApp(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # --- Header ---
        content = self.create_header("Image Segmentation (Pg 17)",
                                     "Point Detection & Line Detection using Spatial Masks.")

        self.notebook = ttk.Notebook(content)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))

        # --- Variables ---
        self.point_src = None
        self.line_src = None

        # --- TAB 1: POINT DETECTION ---
        self.tab_point = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_point, text="Point Detection")
        self.setup_point_tab()

        # --- TAB 2: LINE DETECTION ---
        self.tab_line = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_line, text="Line Detection")
        self.setup_line_tab()

    # =========================================================================
    # TAB 1: POINT DETECTION (Porosity Detection)
    # =========================================================================
    def setup_point_tab(self):
        # --- Control Panel ---
        ctrl = ttk.Frame(self.tab_point)
        ctrl.pack(fill="x", pady=10)

        ttk.Button(ctrl, text="📂 Load Turbine Image", command=self.load_point_src, style="Primary.TButton").pack(
            side="left")

        # Threshold Slider
        ttk.Label(ctrl, text="|  Threshold (T):", style="Sub.TLabel").pack(side="left", padx=(20, 5))
        self.point_thresh_val = tk.IntVar(value=200)  # Nilai default tinggi untuk isolasi titik
        self.lbl_point_t = tk.Label(ctrl, text="200")
        self.lbl_point_t.pack(side="left", padx=2)
        ttk.Scale(ctrl, from_=0, to=255, variable=self.point_thresh_val,
                  command=lambda v: self.update_point_threshold(v)).pack(side="left", padx=5)

        ttk.Button(ctrl, text="▶ Run Detection", command=self.run_point_detection, style="Soft.TButton").pack(
            side="left", padx=20)

        # --- Display Grid (3 Kolom: Input -> Laplacian -> Threshold) ---
        grid = ttk.Frame(self.tab_point)
        grid.pack(fill="both", expand=True)

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(2, weight=1)

        self.lbl_point_in = self.create_img_card(grid, 0, "Input Image (X-Ray)")
        self.lbl_point_lap = self.create_img_card(grid, 1, "Laplacian Filtered (Abs)")
        self.lbl_point_out = self.create_img_card(grid, 2, "Result > T (Point)", save_btn=True)

    def create_img_card(self, parent, col, title, save_btn=False):
        f = ttk.Frame(parent, style="Card.TFrame")
        f.grid(row=0, column=col, sticky="nsew", padx=5, pady=5)
        h = tk.Frame(f, bg="#F1F5F9");
        h.pack(fill="x", pady=2, padx=5)
        tk.Label(h, text=title, bg="#F1F5F9", font=("Segoe UI", 9, "bold")).pack(side="left")
        if save_btn: tk.Button(h, text="💾", bd=0, bg="#ddd",
                               command=lambda: self.save_result(self.lbl_point_out, "point_detected")).pack(
            side="right")
        lbl = tk.Label(f, bg="#F1F5F9");
        lbl.pack(fill="both", expand=True)
        return lbl

    def load_point_src(self):
        img = self._load_img()
        if img is not None:
            self.point_src = img
            self.display_image(img, self.lbl_point_in)
            self.run_point_detection()  # Auto run preview

    def update_point_threshold(self, val):
        self.lbl_point_t.config(text=f"{float(val):.0f}")
        self.run_point_detection()

    def run_point_detection(self):
        if self.point_src is None: return

        # 1. Convert to Gray
        if len(self.point_src.shape) == 3:
            gray = cv2.cvtColor(self.point_src, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.point_src.copy()

        # 2. Laplacian Filter (Mask sesuai PDF Halaman 17: [-1 -1 -1; -1 8 -1; -1 -1 -1])
        kernel = np.array([[-1, -1, -1],
                           [-1, 8, -1],
                           [-1, -1, -1]], dtype=np.float32)

        laplacian = cv2.filter2D(gray, cv2.CV_64F, kernel)

        # Ambil nilai Absolute agar respon negatif (tepi) menjadi positif
        laplacian_abs = np.abs(laplacian)

        # Konversi ke uint8 untuk visualisasi
        laplacian_vis = cv2.normalize(laplacian_abs, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        self.display_image(laplacian_vis, self.lbl_point_lap)

        # 3. Thresholding (Isolasi Titik Terang)
        T = self.point_thresh_val.get()
        # Kita threshold pada nilai absolut asli (sebelum normalisasi visual) atau visual?
        # Biasanya threshold dilakukan pada nilai max respons.
        # Mari gunakan versi yang sudah dinormalisasi agar slider 0-255 relevan.
        _, thresh_res = cv2.threshold(laplacian_vis, T, 255, cv2.THRESH_BINARY)

        self.display_image(thresh_res, self.lbl_point_out)

    # =========================================================================
    # TAB 2: LINE DETECTION
    # =========================================================================
    def setup_line_tab(self):
        # --- Control Panel ---
        ctrl = ttk.Frame(self.tab_line)
        ctrl.pack(fill="x", pady=10)

        ttk.Button(ctrl, text="📂 Load Circuit Image", command=self.load_line_src, style="Primary.TButton").pack(
            side="left")

        # Mask Selection
        ttk.Label(ctrl, text="|  Mask Type:", style="Sub.TLabel").pack(side="left", padx=(15, 5))
        self.line_mask_var = tk.StringVar(value="Horizontal")
        masks = ["Horizontal", "+45 Degree", "Vertical", "-45 Degree"]
        cb = ttk.Combobox(ctrl, textvariable=self.line_mask_var, values=masks, state="readonly", width=15)
        cb.pack(side="left", padx=5)
        cb.bind("<<ComboboxSelected>>", lambda e: self.run_line_detection())

        # Threshold
        ttk.Label(ctrl, text="|  Threshold:", style="Sub.TLabel").pack(side="left", padx=(15, 5))
        self.line_thresh_val = tk.IntVar(value=100)  # Sesuaikan nanti
        self.lbl_line_t = tk.Label(ctrl, text="100")
        self.lbl_line_t.pack(side="left", padx=2)
        ttk.Scale(ctrl, from_=0, to=255, variable=self.line_thresh_val,
                  command=lambda v: self.update_line_threshold(v)).pack(side="left", padx=5)

        # Matrix Preview
        self.lbl_matrix_preview = tk.Label(ctrl, text="[Mask Preview]", bg="#ddd", font=("Consolas", 8), width=25)
        self.lbl_matrix_preview.pack(side="right", padx=10)

        # --- Display Grid ---
        grid = ttk.Frame(self.tab_line)
        grid.pack(fill="both", expand=True)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(2, weight=1)

        self.lbl_line_in = self.create_img_card(grid, 0, "Input Image")
        self.lbl_line_filt = self.create_img_card(grid, 1, "Filtered Response (Abs)")
        self.lbl_line_out = self.create_img_card(grid, 2, "Detected Lines", save_btn=True)

        # Init Matrix Preview
        self.update_matrix_preview()

    def update_matrix_preview(self):
        m_name = self.line_mask_var.get()
        # Definisi Mask sesuai PDF Halaman 17
        if m_name == "Horizontal":
            txt = "-1 -1 -1\n 2  2  2\n-1 -1 -1"
        elif m_name == "+45 Degree":
            txt = "-1 -1  2\n-1  2 -1\n 2 -1 -1"
        elif m_name == "Vertical":
            txt = "-1  2 -1\n-1  2 -1\n-1  2 -1"
        else:  # -45 Degree
            txt = " 2 -1 -1\n-1  2 -1\n-1 -1  2"
        self.lbl_matrix_preview.config(text=txt)

    def load_line_src(self):
        img = self._load_img()
        if img is not None:
            self.line_src = img
            self.display_image(img, self.lbl_line_in)
            self.run_line_detection()

    def update_line_threshold(self, val):
        self.lbl_line_t.config(text=f"{float(val):.0f}")
        self.run_line_detection()

    def run_line_detection(self):
        self.update_matrix_preview()
        if self.line_src is None: return

        if len(self.line_src.shape) == 3:
            gray = cv2.cvtColor(self.line_src, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.line_src.copy()

        m_name = self.line_mask_var.get()
        # Kernel Definition (Sesuai PDF Page 17 Tabel Bawah)
        if m_name == "Horizontal":
            k = np.array([[-1, -1, -1],
                          [2, 2, 2],
                          [-1, -1, -1]], dtype=np.float32)
        elif m_name == "+45 Degree":
            k = np.array([[-1, -1, 2],
                          [-1, 2, -1],
                          [2, -1, -1]], dtype=np.float32)
        elif m_name == "Vertical":
            k = np.array([[-1, 2, -1],
                          [-1, 2, -1],
                          [-1, 2, -1]], dtype=np.float32)
        else:  # -45 Degree
            k = np.array([[2, -1, -1],
                          [-1, 2, -1],
                          [-1, -1, 2]], dtype=np.float32)

        # Filter
        resp = cv2.filter2D(gray, cv2.CV_64F, k)

        # Absolute & Normalize
        resp_abs = np.abs(resp)
        resp_vis = cv2.normalize(resp_abs, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        self.display_image(resp_vis, self.lbl_line_filt)

        # Threshold
        T = self.line_thresh_val.get()
        _, res_bin = cv2.threshold(resp_vis, T, 255, cv2.THRESH_BINARY)
        self.display_image(res_bin, self.lbl_line_out)

    # --- Helpers ---
    def _load_img(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff")])
        if not path: return None
        return cv2.imread(path)

    def display_image(self, cv_img, label):
        try:
            h, w = cv_img.shape[:2]
            scale = 300 / h
            nw, nh = int(w * scale), int(h * scale)

            if len(cv_img.shape) == 2:
                img = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
            else:
                img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

            pil = Image.fromarray(img).resize((nw, nh), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil)
            label.config(image=tk_img)
            label.image = tk_img
        except Exception as e:
            print(e)

    def save_result(self, label_widget, name):
        # Fitur simpan sederhana, mengambil dari image yang ada di label (bukan raw data hires)
        # Untuk tugas ini cukup.
        pass  # Implementasi save standar sudah ada di class lain jika perlu copy paste