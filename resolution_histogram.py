import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
from base_frame import BaseFrame
from styles import COLORS


# ==============================================================================
# KELAS 1: RESOLUSI & KUANTISASI (Sesuai PDF Halaman 1-2)
# ==============================================================================
class ResolutionApp(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)
        content = self.create_header("Spatial Resolution & Quantization (Pg 1-2)",
                                     "Simulasi efek penurunan resolusi spasial dan level warna.")

        # --- Control Panel ---
        ctrl_frame = ttk.Frame(content, padding=10)
        ctrl_frame.pack(fill="x")

        # Group 1: Spatial Resolution
        grp_res = ttk.LabelFrame(ctrl_frame, text="Effect of Spatial Resolution (Pg 2)", padding=10)
        grp_res.pack(fill="x", pady=5)

        ttk.Label(grp_res, text="Resolusi:", style="Sub.TLabel").pack(side="left")
        self.res_var = tk.StringVar(value="256")

        # [PERBAIKAN] Mengembalikan opsi 1024 dan 512
        self.res_combo = ttk.Combobox(grp_res, textvariable=self.res_var,
                                      values=["1024", "512", "256", "128", "64", "32"], state="readonly", width=8)
        self.res_combo.pack(side="left", padx=5)
        self.res_combo.bind("<<ComboboxSelected>>", self.on_param_change)

        ttk.Button(grp_res, text="⊞ Generate Comparison (Fig 3.2)",
                   command=self.generate_res_comparison, style="Soft.TButton").pack(side="right")

        # Group 2: Quantization
        grp_quant = ttk.LabelFrame(ctrl_frame, text="Effect of Quantization Levels (Pg 2)", padding=10)
        grp_quant.pack(fill="x", pady=5)

        ttk.Label(grp_quant, text="Levels:", style="Sub.TLabel").pack(side="left")
        self.quant_var = tk.StringVar(value="256")
        self.quant_combo = ttk.Combobox(grp_quant, textvariable=self.quant_var,
                                        values=["256", "128", "64", "32", "16", "8", "4", "2"], state="readonly",
                                        width=8)
        self.quant_combo.pack(side="left", padx=5)
        self.quant_combo.bind("<<ComboboxSelected>>", self.on_param_change)

        # Tombol Load
        btn_bar = ttk.Frame(content, padding=10)
        btn_bar.pack(fill="x")
        ttk.Button(btn_bar, text="📂 Buka Gambar", command=self.open_image, style="Primary.TButton").pack(side="left")
        ttk.Button(btn_bar, text="↺ Reset", command=self.reset_image, style="Danger.TButton").pack(side="left", padx=10)

        # --- Display Area ---
        self.split_view = ttk.Frame(content)
        self.split_view.pack(fill="both", expand=True, padx=10)
        self.split_view.columnconfigure(0, weight=1);
        self.split_view.columnconfigure(1, weight=1)

        self.lbl_src = self._create_card(self.split_view, 0, "Original")
        self.lbl_res = self._create_card(self.split_view, 1, "Result", save=True)

        self.original_img = None

    def _create_card(self, parent, col, title, save=False):
        f = ttk.Frame(parent, style="Card.TFrame")
        f.grid(row=0, column=col, sticky="nsew", padx=5)
        h = tk.Frame(f, bg="#F1F5F9");
        h.pack(fill="x")
        tk.Label(h, text=title, bg="#F1F5F9", font=("Segoe UI", 9, "bold")).pack(side="left", pady=5)
        if save: tk.Button(h, text="💾", bd=0, bg="#ddd",
                           command=lambda: self.save_image_cv(self.processed_img, "res_result")).pack(side="right")
        l = tk.Label(f, bg="#F1F5F9");
        l.pack(fill="both", expand=True)
        return l

    def open_image(self):
        path = filedialog.askopenfilename()
        if path:
            self.original_img = cv2.imread(path)
            self.reset_image()

    def reset_image(self):
        if self.original_img is None: return
        self.res_var.set("256");
        self.quant_var.set("256")
        self.display_image(self.original_img, self.lbl_src)
        self.on_param_change()

    def generate_res_comparison(self):
        if self.original_img is None:
            messagebox.showwarning("Peringatan", "Silakan load gambar terlebih dahulu!")
            return

        # Resolusi tetap sesuai PDF untuk Comparison
        resolutions = [256, 128, 64, 32]
        processed = []
        h, w = self.original_img.shape[:2]
        for r in resolutions:
            tmp = cv2.resize(self.original_img, (r, r))
            res = cv2.resize(tmp, (w, h), interpolation=cv2.INTER_NEAREST)
            # Tambah text label
            cv2.putText(res, f"{r}x{r}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            processed.append(res)

        top = np.hstack((processed[0], processed[1]))
        bot = np.hstack((processed[2], processed[3]))
        grid = np.vstack((top, bot))
        self.processed_img = grid
        self.display_image(grid, self.lbl_res)

    def on_param_change(self, e=None):
        if self.original_img is None: return
        img = self.original_img.copy()
        h, w = img.shape[:2]

        # 1. Res
        res = int(self.res_var.get())
        tmp = cv2.resize(img, (res, res))
        img = cv2.resize(tmp, (w, h), interpolation=cv2.INTER_NEAREST)

        # 2. Quant
        levels = int(self.quant_var.get())
        if levels < 256:
            div = 256 // levels
            img = (img // div) * div
            img = img.astype(np.uint8)

        self.processed_img = img
        self.display_image(img, self.lbl_res)

    def display_image(self, img, lbl):
        if img is None: return
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(img_rgb)
        pil.thumbnail((400, 400), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(pil)
        lbl.config(image=tk_img);
        lbl.image = tk_img


# ==============================================================================
# KELAS 2: HISTOGRAM PROCESSING (Sesuai PDF Halaman 5-7)
# ==============================================================================
class HistogramApp(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)
        content = self.create_header("Histogram Processing (Pg 5-7)",
                                     "Histogram Equalization & Matching.")

        ctrl = ttk.Frame(content, padding=10)
        ctrl.pack(fill="x")

        # Equalization
        grp_eq = ttk.LabelFrame(ctrl, text="Equalization", padding=10)
        grp_eq.pack(fill="x", pady=5)
        ttk.Button(grp_eq, text="Histogram Equalitation", command=self.do_global_he, style="Primary.TButton").pack(side="left")
        ttk.Button(grp_eq, text="Local HE (CLAHE)", command=self.do_local_he, style="Soft.TButton").pack(side="left", padx=5)

        # Matching
        grp_match = ttk.LabelFrame(ctrl, text="Matching (Specification)", padding=10)
        grp_match.pack(fill="x", pady=5)
        ttk.Button(grp_match, text="Load Ref", command=self.load_ref, style="Soft.TButton").pack(side="left")
        ttk.Label(grp_match, text="➡", font=("Arial", 12)).pack(side="left", padx=5)
        ttk.Button(grp_match, text="Match Histogram", command=self.do_match, style="Primary.TButton").pack(side="left")

        # Canvas Histogram
        self.cv_hist = tk.Canvas(ctrl, bg="white", height=100, bd=1, relief="solid")
        self.cv_hist.pack(fill="x", pady=10)

        # Load Src
        ttk.Button(ctrl, text="📂 Load Source Image", command=self.load_src, style="Primary.TButton").pack(fill="x")

        # Display
        disp = ttk.Frame(content)
        disp.pack(fill="both", expand=True)
        disp.columnconfigure(0, weight=1);
        disp.columnconfigure(1, weight=1)

        self.lbl_src = tk.Label(disp, bg="#ddd", text="Source")
        self.lbl_src.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.lbl_res = tk.Label(disp, bg="#ddd", text="Result")
        self.lbl_res.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)

        self.src_img = None
        self.ref_img = None
        self.res_img = None

    def load_src(self):
        p = filedialog.askopenfilename()
        if p:
            self.src_img = cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2GRAY)
            self.res_img = self.src_img.copy()
            self.show(self.src_img, self.lbl_src)
            self.show(self.res_img, self.lbl_res)
            self.plot_hist()

    def load_ref(self):
        p = filedialog.askopenfilename()
        if p:
            self.ref_img = cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2GRAY)
            messagebox.showinfo("Info", "Reference loaded.")

    def do_global_he(self):
        if self.src_img is None: return
        self.res_img = cv2.equalizeHist(self.src_img)
        self.show(self.res_img, self.lbl_res)
        self.plot_hist()

    def do_local_he(self):
        if self.src_img is None: return
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        self.res_img = clahe.apply(self.src_img)
        self.show(self.res_img, self.lbl_res)
        self.plot_hist()

    def do_match(self):
        if self.src_img is None or self.ref_img is None: return
        # Simple Matching Logic
        src_hist, _ = np.histogram(self.src_img.flatten(), 256, [0, 256])
        ref_hist, _ = np.histogram(self.ref_img.flatten(), 256, [0, 256])

        src_cdf = src_hist.cumsum()
        src_cdf = src_cdf / src_cdf.max()
        ref_cdf = ref_hist.cumsum()
        ref_cdf = ref_cdf / ref_cdf.max()

        lut = np.zeros(256, dtype=np.uint8)
        for g in range(256):
            idx = np.abs(ref_cdf - src_cdf[g]).argmin()
            lut[g] = idx

        self.res_img = cv2.LUT(self.src_img, lut)
        self.show(self.res_img, self.lbl_res)
        self.plot_hist()

    def show(self, img, lbl):
        pil = Image.fromarray(img)
        pil.thumbnail((300, 300))
        tk_img = ImageTk.PhotoImage(pil)
        lbl.config(image=tk_img, text="");
        lbl.image = tk_img

    def plot_hist(self):
        self.cv_hist.delete("all")
        if self.res_img is None: return
        w = self.cv_hist.winfo_width()
        h = self.cv_hist.winfo_height()
        hist = cv2.calcHist([self.res_img], [0], None, [256], [0, 256])
        cv2.normalize(hist, hist, 0, h, cv2.NORM_MINMAX)
        pts = []
        for i in range(256):
            pts.extend([i * (w / 256), h - int(hist[i])])
        self.cv_hist.create_line(pts, fill="black")