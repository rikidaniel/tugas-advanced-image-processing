import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
from base_frame import BaseFrame
from styles import COLORS


class ResHistApp(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)

        content = self.create_header("Resolution, Quantization & Histogram",
                                     "Simulasi Resolusi, Kuantisasi, & Histogram Processing.")

        # --- Control Panel (Tabbed) ---
        self.notebook = ttk.Notebook(content)
        self.notebook.pack(fill="x", pady=(0, 20))

        # Tab 1: Spatial Res & Quantization
        tab_degrade = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab_degrade, text="Spatial Res & Quantization")

        # Resolution Controls
        res_frame = ttk.LabelFrame(tab_degrade, text="Effect of Spatial Resolution", padding=10)
        res_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(res_frame, text="Target Resolusi:", style="Sub.TLabel").pack(side="left")
        self.res_var = tk.StringVar(value="256")
        self.res_combo = ttk.Combobox(res_frame, textvariable=self.res_var,
                                      values=["512", "256", "128", "64", "32"], state="readonly", width=10)
        self.res_combo.pack(side="left", padx=15)
        self.res_combo.bind("<<ComboboxSelected>>", self.on_param_change)

        # Quantization Controls
        quant_frame = ttk.LabelFrame(tab_degrade, text="Effect of Quantization Levels", padding=10)
        quant_frame.pack(fill="x")
        ttk.Label(quant_frame, text="Jumlah Level:", style="Sub.TLabel").pack(side="left")
        self.quant_var = tk.StringVar(value="256")
        self.quant_combo = ttk.Combobox(quant_frame, textvariable=self.quant_var,
                                        values=["256", "128", "64", "32", "16", "8", "4", "2"], state="readonly",
                                        width=10)
        self.quant_combo.pack(side="left", padx=15)
        self.quant_combo.bind("<<ComboboxSelected>>", self.on_param_change)

        # Tab 2: Histogram Processing
        tab_hist = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab_hist, text="Histogram Processing")

        # Area Histogram Equalization
        frame_eq = ttk.LabelFrame(tab_hist, text="Equalization", padding=10)
        frame_eq.pack(fill="x", pady=(0, 10))
        ttk.Button(frame_eq, text="Global Hist. Eq.", command=self.apply_equalization, style="Primary.TButton").pack(
            side="left")
        ttk.Button(frame_eq, text="Local Hist. Eq. (7x7)", command=self.apply_local_he, style="Soft.TButton").pack(
            side="left", padx=5)

        # Area Histogram Matching (Layout Diperbaiki)
        frame_match = ttk.LabelFrame(tab_hist, text="Matching (Specification)", padding=10)
        frame_match.pack(fill="x")

        # Preview Reference Kecil
        self.lbl_ref_thumb = tk.Label(frame_match, text="[No Ref]", bg="#eee", width=10, height=3)
        self.lbl_ref_thumb.pack(side="left", padx=(0, 10))

        ttk.Button(frame_match, text="1. Load Reference (Target)", command=self.load_reference_image,
                   style="Soft.TButton").pack(side="left")
        ttk.Label(frame_match, text="➡", style="Body.TLabel").pack(side="left", padx=5)
        ttk.Button(frame_match, text="2. Match Histogram", command=self.apply_matching, style="Primary.TButton").pack(
            side="left")

        # Histogram Chart
        self.hist_canvas = tk.Canvas(tab_hist, bg="white", height=150, bd=1, relief="solid")
        self.hist_canvas.pack(fill="x", pady=10)

        # --- Global Buttons ---
        ctrl_frame = ttk.Frame(content)
        ctrl_frame.pack(fill="x", pady=(0, 10))
        ttk.Button(ctrl_frame, text="📂 Buka Gambar (Source)", command=self.open_image, style="Primary.TButton").pack(
            side="left", padx=(0, 10))
        ttk.Button(ctrl_frame, text="竊ｺ Reset Original", command=self.reset_image, style="Danger.TButton").pack(
            side="left")

        # --- Image Display Area ---
        img_grid = ttk.Frame(content)
        img_grid.pack(fill="both", expand=True)
        img_grid.columnconfigure(0, weight=1);
        img_grid.columnconfigure(1, weight=1)

        f_left = ttk.Frame(img_grid, style="Card.TFrame")
        f_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(f_left, text="Original Image", bg="#F1F5F9", pady=8, font=("Segoe UI", 10, "bold")).pack(fill="x")
        self.lbl_original = tk.Label(f_left, bg="#F1F5F9")
        self.lbl_original.pack(fill="both", expand=True)

        f_right = ttk.Frame(img_grid, style="Card.TFrame")
        f_right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Header Result + Save
        res_header = tk.Frame(f_right, bg="#F1F5F9")
        res_header.pack(fill="x")
        self.lbl_res_title = tk.Label(res_header, text="Processed Result", bg="#F1F5F9", pady=8,
                                      font=("Segoe UI", 10, "bold"))
        self.lbl_res_title.pack(side="left", fill="x", expand=True)

        save_btn = tk.Button(res_header, text="💾 Save", font=("Segoe UI", 8), bg="#ddd", bd=0,
                             command=lambda: self.save_image_cv(self.processed_img_cv, "res_hist_result"))
        save_btn.pack(side="right", padx=5, pady=5)

        self.lbl_result = tk.Label(f_right, bg="#F1F5F9")
        self.lbl_result.pack(fill="both", expand=True)

        self.original_img_cv = None;
        self.gray_img_cv = None
        self.reference_img_cv = None;
        self.processed_img_cv = None
        self.is_matching_mode = False

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.tif")])
        if not path: return
        img = cv2.imread(path)
        if img is None: return
        self.original_img_cv = img
        if len(img.shape) == 3:
            self.gray_img_cv = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            self.gray_img_cv = img.copy()
        self.display_image(self.original_img_cv, self.lbl_original)
        self.reset_image()

    def load_reference_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.tif")])
        if not path: return
        img = cv2.imread(path)
        if img is None: return
        if len(img.shape) == 3:
            self.reference_img_cv = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            self.reference_img_cv = img.copy()

        # Tampilkan Thumbnail di tombol
        thumb_pil = Image.fromarray(self.reference_img_cv)
        thumb_pil.thumbnail((50, 30))
        tk_thumb = ImageTk.PhotoImage(thumb_pil)
        self.lbl_ref_thumb.config(image=tk_thumb, text="")
        self.lbl_ref_thumb.image = tk_thumb  # Keep ref
        messagebox.showinfo("Info", "Citra referensi dimuat. Klik 'Match Histogram' untuk proses.")

    def reset_image(self):
        if self.original_img_cv is None: return
        self.res_combo.set("256");
        self.quant_combo.set("256")
        self.is_matching_mode = False
        self.processed_img_cv = self.original_img_cv.copy()
        self.display_image(self.processed_img_cv, self.lbl_result)
        if self.notebook.index(self.notebook.select()) == 1: self.draw_histograms()

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
            label_widget.config(image=tk_img);
            label_widget.image = tk_img
        except Exception as e:
            print(f"Error display: {e}")

    def on_param_change(self, event=None):
        if self.original_img_cv is None: return
        target_res = int(self.res_var.get())
        levels = int(self.quant_var.get())
        h, w = self.original_img_cv.shape[:2]

        temp = cv2.resize(self.original_img_cv, (target_res, target_res), interpolation=cv2.INTER_LINEAR)
        res_sim = cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)

        if levels < 256:
            work_img = cv2.cvtColor(res_sim, cv2.COLOR_BGR2GRAY) if len(res_sim.shape) == 3 else res_sim
            interval = 256 // levels
            quantized = (work_img // interval) * interval
            quantized = quantized.astype(np.uint8)
            self.processed_img_cv = cv2.cvtColor(quantized, cv2.COLOR_GRAY2BGR) if len(
                res_sim.shape) == 3 else quantized
        else:
            self.processed_img_cv = res_sim

        self.lbl_res_title.config(text=f"Res: {target_res}px, Level: {levels}")
        self.display_image(self.processed_img_cv, self.lbl_result)

    def apply_equalization(self):
        if self.gray_img_cv is None: return
        self.is_matching_mode = False
        self.processed_img_cv = cv2.equalizeHist(self.gray_img_cv)
        self.lbl_res_title.config(text="Result: Global Equalization")
        self.display_image(self.processed_img_cv, self.lbl_result)
        self.draw_histograms()

    def apply_local_he(self):
        if self.gray_img_cv is None: return
        self.is_matching_mode = False
        clahe = cv2.createCLAHE(clipLimit=40.0, tileGridSize=(8, 8))
        self.processed_img_cv = clahe.apply(self.gray_img_cv)
        self.lbl_res_title.config(text="Result: Local Hist. Eq. (7x7 Sim.)")
        self.display_image(self.processed_img_cv, self.lbl_result)
        self.draw_histograms()

    def apply_matching(self):
        if self.gray_img_cv is None: return
        if self.reference_img_cv is None:
            messagebox.showwarning("Warning", "Muat gambar referensi dulu.")
            return
        self.is_matching_mode = True
        src_hist, _ = np.histogram(self.gray_img_cv.flatten(), 256, [0, 256])
        src_cdf = src_hist.cumsum();
        src_cdf_norm = src_cdf / src_cdf.max()
        ref_hist, _ = np.histogram(self.reference_img_cv.flatten(), 256, [0, 256])
        ref_cdf = ref_hist.cumsum();
        ref_cdf_norm = ref_cdf / ref_cdf.max()

        lut = np.zeros(256, dtype=np.uint8)
        for g in range(256):
            idx = np.abs(ref_cdf_norm - src_cdf_norm[g]).argmin()
            lut[g] = idx
        self.processed_img_cv = cv2.LUT(self.gray_img_cv, lut)
        self.lbl_res_title.config(text="Result: Histogram Matching")
        self.display_image(self.processed_img_cv, self.lbl_result)
        self.draw_histograms()

    def draw_histograms(self):
        if self.gray_img_cv is None: return
        self.hist_canvas.delete("all")
        w = self.hist_canvas.winfo_width();
        h = self.hist_canvas.winfo_height()
        if w < 10: w = 400; h = 150

        def get_pts(img, color):
            hist = cv2.calcHist([img], [0], None, [256], [0, 256])
            cv2.normalize(hist, hist, 0, h - 20, cv2.NORM_MINMAX)
            pts = []
            for i in range(256):
                pts.extend([i * (w / 256), h - int(hist[i])])
            return pts

        if self.is_matching_mode and self.reference_img_cv is not None:
            pts_ref = get_pts(self.reference_img_cv, "#22C55E")
            if len(pts_ref) > 2: self.hist_canvas.create_line(pts_ref, fill="#22C55E", width=2)

        target = self.processed_img_cv if self.processed_img_cv is not None else self.gray_img_cv
        if len(target.shape) == 3: target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        pts_res = get_pts(target, COLORS["primary"])
        if len(pts_res) > 2: self.hist_canvas.create_line(pts_res, fill=COLORS["primary"], width=2)