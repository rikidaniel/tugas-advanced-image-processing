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
        content = self.create_header("Spatial Filters (Pg 10-12)",
                                     "Smoothing (Pg 10), Median (Pg 11), Sharpening & Gradient (Pg 11-12).")

        self.notebook = ttk.Notebook(content)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))

        # --- Variables ---
        self.smooth_src = None
        self.smooth_res = {}
        self.hubble_src = None
        self.hubble_res = {}
        self.median_src = None
        self.sharp_src = None

        # Gradient Variables
        self.grad_src = None
        self.grad_res_cache = {}
        self.grad_view_mode = tk.StringVar(value="Pg11")

        # --- TABS ---
        self.tab_smooth = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_smooth, text="Pg 10: Smoothing")
        self.setup_smoothing_tab()

        self.tab_hubble = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_hubble, text="Pg 10: Hubble")
        self.setup_hubble_tab()

        self.tab_median = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_median, text="Pg 11: Median")
        self.setup_median_tab()

        self.tab_sharp = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_sharp, text="Pg 11: Sharpening")
        self.setup_sharpening_tab()

        self.tab_grad = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_grad, text="Pg 11-12: Gradient")
        self.setup_gradient_tab()

    # =========================================================================
    # TAB 1: SMOOTHING
    # =========================================================================
    def setup_smoothing_tab(self):
        top = ttk.Frame(self.tab_smooth)
        top.pack(fill="x", pady=10)
        ttk.Button(top, text="📂 1. Load Source", command=self.load_smooth_src, style="Primary.TButton").pack(
            side="left")
        ttk.Button(top, text="▶ 2. Run Smoothing", command=self.run_smoothing_all, style="Soft.TButton").pack(
            side="left", padx=10)
        self.lbl_smooth_status = tk.Label(top, text="Load gambar...", fg="#666")
        self.lbl_smooth_status.pack(side="left")

        self.smooth_display = ttk.Frame(self.tab_smooth, style="Card.TFrame")
        self.smooth_display.pack(fill="both", expand=True, padx=50, pady=10)
        self.lbl_smooth_main = tk.Label(self.smooth_display, bg="#F1F5F9", text="No Image")
        self.lbl_smooth_main.pack(fill="both", expand=True)

        btn_bar = ttk.Frame(self.tab_smooth)
        btn_bar.pack(fill="x", pady=15)

        self.smooth_btns = {}
        labels = [("Orig (a)", 'a'), ("3x3 (b)", 'b'), ("5x5 (c)", 'c'),
                  ("9x9 (d)", 'd'), ("15x15 (e)", 'e'), ("35x35 (f)", 'f')]

        for text, key in labels:
            btn = ttk.Button(btn_bar, text=text, command=lambda k=key: self.show_smooth(k), state="disabled")
            btn.pack(side="left", expand=True, fill="x", padx=2)
            self.smooth_btns[key] = btn

        ttk.Button(btn_bar, text="💾 Save View", command=lambda: self.save_view(self.current_smooth_view, "smoothing"),
                   style="Soft.TButton").pack(side="right", padx=10)

    def load_smooth_src(self):
        img = self._load_img()
        if img is not None:
            self.smooth_src = img
            self.display_image_large(img, self.lbl_smooth_main)
            self.lbl_smooth_status.config(text="Gambar siap. Klik Run.")

    def run_smoothing_all(self):
        if self.smooth_src is None: return
        self.lbl_smooth_status.config(text="Processing...")
        self.update()
        src = self.smooth_src
        self.smooth_res['a'] = src
        sizes = [3, 5, 9, 15, 35]
        keys = ['b', 'c', 'd', 'e', 'f']
        for k_size, key in zip(sizes, keys):
            res = cv2.blur(src, (k_size, k_size))
            self.smooth_res[key] = res
        for k in self.smooth_btns: self.smooth_btns[k].config(state="normal")
        self.show_smooth('f')
        self.lbl_smooth_status.config(text="Selesai.")

    def show_smooth(self, key):
        if key in self.smooth_res:
            self.display_image_large(self.smooth_res[key], self.lbl_smooth_main)
            self.current_smooth_view = self.smooth_res[key]

    # =========================================================================
    # TAB 2: HUBBLE CASE
    # =========================================================================
    def setup_hubble_tab(self):
        top = ttk.Frame(self.tab_hubble)
        top.pack(fill="x", pady=10)
        ttk.Button(top, text="📂 Load Hubble Image (a)", command=self.load_hubble, style="Primary.TButton").pack(
            side="left")

        ttk.Label(top, text="Threshold:", style="Sub.TLabel").pack(side="left", padx=(20, 5))
        self.hubble_thresh = tk.IntVar(value=65)
        self.lbl_hubble_val = tk.Label(top, text="65")
        self.lbl_hubble_val.pack(side="left", padx=2)
        ttk.Scale(top, from_=0, to=255, variable=self.hubble_thresh,
                  command=lambda v: self.lbl_hubble_val.config(text=f"{float(v):.0f}")).pack(side="left", padx=5)

        ttk.Button(top, text="▶ Run (a->b->c)", command=self.run_hubble, style="Soft.TButton").pack(side="left",
                                                                                                    padx=20)

        grid = ttk.Frame(self.tab_hubble)
        grid.pack(fill="both", expand=True)
        self.lbl_hubble_a = self.create_img_frame(grid, 0, "Original (a)")
        self.lbl_hubble_b = self.create_img_frame(grid, 1, "Processed 15x15 (b)")
        self.lbl_hubble_c = self.create_img_frame(grid, 2, "Thresholded (c)", save_btn=True)

    def load_hubble(self):
        img = self._load_img()
        if img is not None:
            self.hubble_src = img
            self.display_image_fit(img, self.lbl_hubble_a)
            self.lbl_hubble_b.config(image="")
            self.lbl_hubble_c.config(image="")

    def run_hubble(self):
        if self.hubble_src is None: return
        img_a = self.hubble_src
        if len(img_a.shape) == 3:
            img_gray = cv2.cvtColor(img_a, cv2.COLOR_BGR2GRAY)
        else:
            img_gray = img_a.copy()

        img_b = cv2.blur(img_gray, (15, 15))
        self.display_image_fit(img_b, self.lbl_hubble_b)

        thresh_val = self.hubble_thresh.get()
        _, img_c = cv2.threshold(img_b, thresh_val, 255, cv2.THRESH_BINARY)
        self.display_image_fit(img_c, self.lbl_hubble_c)
        self.current_hubble_res = img_c

    # =========================================================================
    # TAB 3: MEDIAN FILTER
    # =========================================================================
    def setup_median_tab(self):
        top = ttk.Frame(self.tab_median)
        top.pack(fill="x", pady=10)
        ttk.Button(top, text="📂 Load Noisy Img", command=self.load_median_src, style="Primary.TButton").pack(
            side="left", padx=5)
        ttk.Button(top, text="🧂 Add S&P Noise", command=self.add_noise_median, style="Soft.TButton").pack(side="left",
                                                                                                          padx=5)
        ttk.Button(top, text="▶ Run Comparison", command=self.run_median_compare, style="Soft.TButton").pack(
            side="left", padx=15)

        grid = ttk.Frame(self.tab_median)
        grid.pack(fill="both", expand=True)
        self.lbl_med_a = self.create_img_frame(grid, 0, "(a) Noisy Image")
        self.lbl_med_b = self.create_img_frame(grid, 1, "(b) Mean Filter 3x3")
        self.lbl_med_c = self.create_img_frame(grid, 2, "(c) Median Filter 3x3", save_btn=True)

    def load_median_src(self):
        img = self._load_img()
        if img is not None:
            self.median_src = img
            self.display_image_fit(img, self.lbl_med_a)

    def add_noise_median(self):
        if self.median_src is None: return
        row, col = self.median_src.shape[:2]
        noisy = self.median_src.copy()
        n_px = random.randint(1000, 10000)
        for i in range(n_px):
            y, x = random.randint(0, row - 1), random.randint(0, col - 1)
            noisy[y][x] = 255
            y, x = random.randint(0, row - 1), random.randint(0, col - 1)
            noisy[y][x] = 0
        self.median_src = noisy
        self.display_image_fit(noisy, self.lbl_med_a)

    def run_median_compare(self):
        if self.median_src is None: return
        img = self.median_src
        res_mean = cv2.blur(img, (3, 3))
        self.display_image_fit(res_mean, self.lbl_med_b)
        res_median = cv2.medianBlur(img, 3)
        self.display_image_fit(res_median, self.lbl_med_c)
        self.current_med_res = res_median

    # =========================================================================
    # TAB 4: SHARPENING (Page 11)
    # =========================================================================
    def setup_sharpening_tab(self):
        ctrl = ttk.Frame(self.tab_sharp)
        ctrl.pack(fill="x", pady=10)
        ttk.Button(ctrl, text="📂 Load Image", command=self.load_sharp_src, style="Primary.TButton").pack(side="left")
        ttk.Label(ctrl, text="Filter:", style="Sub.TLabel").pack(side="left", padx=(15, 5))
        self.sharp_var = tk.StringVar()
        opts = ["Laplacian (Center -4)", "Laplacian (Center -8)", "Laplacian (Center +8)", "High-Boost (A=1.2)"]
        self.cb_sharp = ttk.Combobox(ctrl, textvariable=self.sharp_var, values=opts, state="readonly", width=25)
        self.cb_sharp.pack(side="left", padx=5)
        self.cb_sharp.current(0)
        ttk.Button(ctrl, text="▶ Apply", command=self.run_sharpening, style="Soft.TButton").pack(side="left", padx=10)

        grid = ttk.Frame(self.tab_sharp)
        grid.pack(fill="both", expand=True)
        self.lbl_sharp_src = self.create_img_frame(grid, 0, "Original")
        self.lbl_sharp_res = self.create_img_frame(grid, 1, "Result", save_btn=True)

        self.lbl_kernel_vis = tk.Label(self.tab_sharp, text="Kernel Matrix: -", bg="white", font=("Consolas", 10),
                                       relief="solid", bd=1, pady=5)
        self.lbl_kernel_vis.pack(fill="x", pady=10)

    def load_sharp_src(self):
        img = self._load_img()
        if img is not None:
            self.sharp_src = img
            self.display_image_fit(img, self.lbl_sharp_src)

    def run_sharpening(self):
        if self.sharp_src is None: return
        mode = self.sharp_var.get()
        img = self.sharp_src
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        res = None;
        kernel_txt = ""
        if "Laplacian" in mode:
            if "-4" in mode:
                k = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
                sharpen_k = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            elif "-8" in mode:
                k = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]])
                sharpen_k = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            else:
                k = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
                sharpen_k = np.array([[1, 1, 1], [1, -7, 1], [1, 1, 1]])
            kernel_txt = str(k).replace('[', ' ').replace(']', ' ')
            res = cv2.filter2D(img, -1, sharpen_k)
        elif "High-Boost" in mode:
            kernel_txt = "Formula: Img + A*(Img - Blur)"
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            mask = cv2.addWeighted(gray.astype(float), 1.0, blur.astype(float), -1.0, 0)
            res_float = gray.astype(float) + 1.2 * mask
            res = np.clip(res_float, 0, 255).astype(np.uint8)

        self.lbl_kernel_vis.config(text=f"Active Kernel ({mode}):\n{kernel_txt}")
        self.display_image_fit(res, self.lbl_sharp_res)
        self.current_sharp_res = res

    # =========================================================================
    # TAB 5: IMAGE GRADIENT (Page 11-12)
    # =========================================================================
    def setup_gradient_tab(self):
        ctrl = ttk.Frame(self.tab_grad)
        ctrl.pack(fill="x", pady=10)

        # 1. Action Buttons
        ttk.Button(ctrl, text="📂 Load Source", command=self.load_grad_src, style="Primary.TButton").pack(side="left")
        ttk.Button(ctrl, text="▶ Calculate Gradient", command=self.run_gradient, style="Soft.TButton").pack(side="left",
                                                                                                            padx=10)

        # 2. View Options
        ttk.Label(ctrl, text="|  View:", style="Sub.TLabel").pack(side="left", padx=(10, 5))

        # Pg 11: 3 Gambar (Orig + 2 Gray Output)
        ttk.Radiobutton(ctrl, text="Pg 11 (Orig + Gx + Gy)", variable=self.grad_view_mode,
                        value="Pg11", command=self.update_grad_grid).pack(side="left", padx=5)

        # Pg 12: 4 Gambar Lengkap
        ttk.Radiobutton(ctrl, text="Pg 12 (Full + Mag)", variable=self.grad_view_mode,
                        value="Pg12", command=self.update_grad_grid).pack(side="left", padx=5)

        # Container Grid
        self.grad_grid_frame = ttk.Frame(self.tab_grad)
        self.grad_grid_frame.pack(fill="both", expand=True)

        # Init View
        self.update_grad_grid()

    def update_grad_grid(self):
        # Clear
        for w in self.grad_grid_frame.winfo_children(): w.destroy()
        mode = self.grad_view_mode.get()

        if mode == "Pg11":
            # Layout Halaman 11: Top(Orig), Bottom Left(Gx), Bottom Right(Gy)
            self.grad_grid_frame.columnconfigure(0, weight=1)
            self.grad_grid_frame.columnconfigure(1, weight=1)
            self.grad_grid_frame.rowconfigure(0, weight=1)
            self.grad_grid_frame.rowconfigure(1, weight=1)

            # Row 0: Original (Span 2 kolom)
            f = ttk.Frame(self.grad_grid_frame, style="Card.TFrame")
            f.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=3, pady=3)
            h = tk.Frame(f, bg="#F1F5F9");
            h.pack(fill="x", pady=2, padx=5)
            tk.Label(h, text="Original Image", bg="#F1F5F9", font=("Segoe UI", 8, "bold")).pack(side="left")
            self.lbl_grad_src_custom = tk.Label(f, bg="#F1F5F9");
            self.lbl_grad_src_custom.pack(fill="both", expand=True)
            self.lbl_grad_src = self.lbl_grad_src_custom

            # Row 1: Gx (Kiri) dan Gy (Kanan)
            self.lbl_grad_x = self.create_img_frame_grid(self.grad_grid_frame, 1, 0, "Partial X (dP/dx) - Bright")
            self.lbl_grad_y = self.create_img_frame_grid(self.grad_grid_frame, 1, 1, "Partial Y (dP/dy) - Dark")
            self.lbl_grad_mag = None

        else:
            # Layout Halaman 12 (4 Gambar Grid 2x2)
            self.grad_grid_frame.columnconfigure(0, weight=1)
            self.grad_grid_frame.columnconfigure(1, weight=1)
            self.grad_grid_frame.rowconfigure(0, weight=1)
            self.grad_grid_frame.rowconfigure(1, weight=1)

            # Baris 1
            self.lbl_grad_src = self.create_img_frame_grid(self.grad_grid_frame, 0, 0, "(a) Original (P)")
            self.lbl_grad_x = self.create_img_frame_grid(self.grad_grid_frame, 0, 1, "(b) Partial X (dP/dx)")

            # Baris 2
            self.lbl_grad_y = self.create_img_frame_grid(self.grad_grid_frame, 1, 0, "(c) Partial Y (dP/dy)")
            self.lbl_grad_mag = self.create_img_frame_grid(self.grad_grid_frame, 1, 1, "(d) Magnitude |VP|",
                                                           save_btn=True)

        # Reload image
        if self.grad_res_cache:
            self.refresh_grad_display()
        elif self.grad_src is not None and self.lbl_grad_src:
            self.display_image_grid(self.grad_src, self.lbl_grad_src)

    def load_grad_src(self):
        img = self._load_img()
        if img is not None:
            self.grad_src = img
            self.grad_res_cache = {}
            if hasattr(self, 'lbl_grad_src') and self.lbl_grad_src:
                self.display_image_grid(img, self.lbl_grad_src)

    def run_gradient(self):
        if self.grad_src is None: return
        img = self.grad_src
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        # Hitung Gradient Sobel (CV_64F)
        gx_64 = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        gy_64 = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

        # Hitung Magnitude
        mag = cv2.magnitude(gx_64, gy_64)

        # --- PERBAIKAN VISUALISASI (REQUEST USER) ---
        # User request: "Yang kiri (Gx) di cerahin gray nya"
        # Gx (Kiri): Beta = 200 (Background Abu-abu Terang)
        # Gy (Kanan): Beta = 55 (Background Abu-abu Gelap)
        # Alpha=1.5 agar kontras garis tepi tetap kuat

        vis_gx = cv2.convertScaleAbs(gx_64, alpha=1.5, beta=160)
        vis_gy = cv2.convertScaleAbs(gy_64, alpha=1.5, beta=128)

        # Magnitude tetap normalisasi 0-255 (hitam ke putih)
        vis_mag = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # Simpan
        self.grad_res_cache = {
            "gx": vis_gx,
            "gy": vis_gy,
            "mag": vis_mag,
            "orig": gray
        }
        self.current_grad_res = vis_mag
        self.refresh_grad_display()

    def refresh_grad_display(self):
        if not self.grad_res_cache: return

        gx = self.grad_res_cache["gx"]
        gy = self.grad_res_cache["gy"]
        mag = self.grad_res_cache["mag"]
        orig = self.grad_res_cache.get("orig", None)

        if self.lbl_grad_src and orig is not None: self.display_image_grid(orig, self.lbl_grad_src)
        if self.lbl_grad_mag and mag is not None: self.display_image_grid(mag, self.lbl_grad_mag)
        if self.lbl_grad_x and gx is not None: self.display_image_grid(gx, self.lbl_grad_x)
        if self.lbl_grad_y and gy is not None: self.display_image_grid(gy, self.lbl_grad_y)

    # --- Helpers ---
    def create_img_frame(self, parent, col, title, save_btn=False):
        parent.columnconfigure(col, weight=1)
        f = ttk.Frame(parent, style="Card.TFrame")
        f.grid(row=0, column=col, sticky="nsew", padx=5, pady=5)
        h = tk.Frame(f, bg="#F1F5F9");
        h.pack(fill="x", pady=2, padx=5)
        tk.Label(h, text=title, bg="#F1F5F9", font=("Segoe UI", 8, "bold")).pack(side="left")
        if save_btn: tk.Button(h, text="💾", bd=0, bg="#ddd", command=lambda: self.save_smart(title)).pack(side="right")
        lbl = tk.Label(f, bg="#F1F5F9");
        lbl.pack(fill="both", expand=True)
        return lbl

    def create_img_frame_grid(self, parent, r, c, title, save_btn=False):
        f = ttk.Frame(parent, style="Card.TFrame")
        f.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)
        h = tk.Frame(f, bg="#F1F5F9");
        h.pack(fill="x", pady=2, padx=5)
        tk.Label(h, text=title, bg="#F1F5F9", font=("Segoe UI", 8, "bold")).pack(side="left")
        if save_btn: tk.Button(h, text="💾", bd=0, bg="#ddd", command=lambda: self.save_smart(title)).pack(side="right")
        lbl = tk.Label(f, bg="#F1F5F9");
        lbl.pack(fill="both", expand=True)
        return lbl

    def save_smart(self, title):
        target = None;
        name = "result"
        if "Sharpened" in title and hasattr(self, 'current_sharp_res'):
            target = self.current_sharp_res;
            name = "sharpening"
        elif "Thresholded" in title and hasattr(self, 'current_hubble_res'):
            target = self.current_hubble_res;
            name = "hubble_threshold"
        elif "Median" in title and hasattr(self, 'current_med_res'):
            target = self.current_med_res;
            name = "median_filter"
        elif "Magnitude" in title and hasattr(self, 'current_grad_res'):
            target = self.current_grad_res;
            name = "gradient_magnitude"
        if target is not None: self.save_image_cv(target, name)

    def save_view(self, img, prefix):
        if img is not None: self.save_image_cv(img, prefix)

    def _load_img(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff")])
        if not path: return None
        return cv2.imread(path)

    def display_image_large(self, cv_img, label_widget):
        self._display(cv_img, label_widget, 500)

    def display_image_fit(self, cv_img, label_widget):
        self._display(cv_img, label_widget, 350)

    def display_image_grid(self, cv_img, label_widget):
        self._display(cv_img, label_widget, 250)

    def _display(self, cv_img, label, max_h):
        if cv_img is None: return
        try:
            h, w = cv_img.shape[:2];
            scale = max_h / h;
            nw, nh = int(w * scale), int(h * scale)
            if len(cv_img.shape) == 2:
                img = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
            else:
                img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            pil = Image.fromarray(img).resize((nw, nh), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil)
            label.config(image=tk_img);
            label.image = tk_img
        except Exception as e:
            print(e)