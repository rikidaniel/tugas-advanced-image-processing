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
        
        # --- UI Initialization ---
        content = self.create_header("Resolution & Histogram", "Simulasi Resolusi, Kuantisasi, Ekualisasi, & Matching.")
        
        # --- Control Panel (Tabbed) ---
        self.notebook = ttk.Notebook(content)
        self.notebook.pack(fill="x", pady=(0, 20))
        
        # Tab 1: Degradation (Resolution & Quantization)
        tab_degrade = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab_degrade, text="Degradasi Citra")
        
        # Resolution Controls
        res_frame = ttk.LabelFrame(tab_degrade, text="Resolusi Spasial (Pixelation)", padding=10)
        res_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(res_frame, text="Target Resolusi:", style="Sub.TLabel").pack(side="left")
        
        # [Perbaikan] Menggunakan Combobox sesuai tabel PDF Hal 1 (256, 128, 64, 32)
        self.res_var = tk.StringVar(value="256")
        self.res_combo = ttk.Combobox(res_frame, textvariable=self.res_var, 
                                      values=["512", "256", "128", "64", "32"], 
                                      state="readonly", width=10)
        self.res_combo.pack(side="left", padx=15)
        self.res_combo.bind("<<ComboboxSelected>>", self.on_param_change)
        
        # Quantization Controls
        quant_frame = ttk.LabelFrame(tab_degrade, text="Kuantisasi (Gray-Level Slicing)", padding=10)
        quant_frame.pack(fill="x")
        
        ttk.Label(quant_frame, text="Jumlah Level:", style="Sub.TLabel").pack(side="left")
        self.levels_var = tk.IntVar(value=256)
        self.levels_scale = tk.Scale(quant_frame, from_=1, to=8, orient="horizontal", 
                                     command=self.on_level_change,
                                     length=300, bg=COLORS["bg_card"], highlightthickness=0, showvalue=0)
        self.levels_scale.set(8) # 2^8 = 256
        self.levels_scale.pack(side="left", padx=15, fill="x", expand=True)
        self.lbl_levels_val = ttk.Label(quant_frame, text="256 Level", style="Sub.TLabel")
        self.lbl_levels_val.pack(side="left")

        # Tab 2: Histogram Operations
        tab_hist = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab_hist, text="Histogram Ops")
        
        btn_frame = ttk.Frame(tab_hist)
        btn_frame.pack(fill="x", pady=(0, 10))
        
        # Equalization Buttons
        ttk.Button(btn_frame, text="⚡ Equalize", command=self.apply_equalization, style="Primary.TButton").pack(side="left")
        ttk.Button(btn_frame, text="⚡ CLAHE", command=self.apply_clahe, style="Soft.TButton").pack(side="left", padx=5)
        
        # Matching Controls
        sep = ttk.Frame(btn_frame, width=2, style="Card.TFrame")
        sep.pack(side="left", padx=10, fill="y")
        
        ttk.Button(btn_frame, text="📂 Load Ref", command=self.load_reference_image, style="Soft.TButton").pack(side="left")
        ttk.Button(btn_frame, text="⚡ Match Hist", command=self.apply_matching, style="Primary.TButton").pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="📊 Chart", command=self.draw_histograms, style="Soft.TButton").pack(side="right")
        
        # Histogram Canvas
        self.hist_canvas = tk.Canvas(tab_hist, bg="white", height=150, bd=1, relief="solid")
        self.hist_canvas.pack(fill="x", pady=5)


        # --- Global Buttons (Outside Tabs) ---
        ctrl_frame = ttk.Frame(content)
        ctrl_frame.pack(fill="x", pady=(0, 10))
        ttk.Button(ctrl_frame, text="📂 Buka Gambar", command=self.open_image, style="Primary.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(ctrl_frame, text="↺ Reset Original", command=self.reset_image, style="Danger.TButton").pack(side="left")
        
        # --- Image Display Area ---
        img_grid = ttk.Frame(content)
        img_grid.pack(fill="both", expand=True)
        img_grid.columnconfigure(0, weight=1)
        img_grid.columnconfigure(1, weight=1)
        
        # Left: Original
        f_left = ttk.Frame(img_grid, style="Card.TFrame")
        f_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(f_left, text="Original / Reference", bg="#F1F5F9", pady=8, font=("Segoe UI", 10, "bold")).pack(fill="x")
        self.lbl_original = tk.Label(f_left, bg="#F1F5F9")
        self.lbl_original.pack(fill="both", expand=True)
        
        # Right: Result
        f_right = ttk.Frame(img_grid, style="Card.TFrame")
        f_right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        tk.Label(f_right, text="Processed Result", bg="#F1F5F9", pady=8, font=("Segoe UI", 10, "bold")).pack(fill="x")
        self.lbl_result = tk.Label(f_right, bg="#F1F5F9")
        self.lbl_result.pack(fill="both", expand=True)
        
        # --- Application State ---
        self.original_img_cv = None
        self.gray_img_cv = None 
        self.reference_img_cv = None 
        self.processed_img_cv = None

    def on_level_change(self, val):
        exp = int(float(val))
        levels = 2 ** exp
        self.levels_var.set(levels)
        self.lbl_levels_val.config(text=f"{levels} Level")
        self.on_param_change()

    def open_image(self):
        # [Perbaikan] Tambah Support TIFF
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
            
        self.display_image(self.reference_img_cv, self.lbl_original)
        messagebox.showinfo("Info", "Citra referensi dimuat. Klik 'Match Hist' untuk menerapkan.")

    def reset_image(self):
        if self.original_img_cv is None: return
        # Set dropdown ke resolusi asli atau terdekat (misal 256)
        self.res_combo.set("256")
        self.levels_scale.set(8)
        
        self.processed_img_cv = self.original_img_cv.copy()
        self.display_image(self.processed_img_cv, self.lbl_result)
        self.display_image(self.original_img_cv, self.lbl_original)
        if self.notebook.index(self.notebook.select()) == 1:
            self.draw_histograms()

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
            print(f"Error display: {e}")

    def on_param_change(self, event=None):
        if self.original_img_cv is None: return
        
        # [Perbaikan] Ambil nilai dari Combobox (string -> int)
        try:
            target_res = int(self.res_var.get())
        except:
            target_res = 256

        levels = self.levels_var.get()
        
        h, w = self.original_img_cv.shape[:2]
        
        # Logika Resolusi (Pixelation)
        temp = cv2.resize(self.original_img_cv, (target_res, target_res), interpolation=cv2.INTER_LINEAR)
        res_sim = cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)
        
        # Logika Kuantisasi
        if levels < 256:
            if len(res_sim.shape) == 3:
                work_img = cv2.cvtColor(res_sim, cv2.COLOR_BGR2GRAY)
                is_color = True
            else:
                work_img = res_sim
                is_color = False
                
            interval = 256 // levels
            quantized = (work_img // interval) * interval
            quantized = quantized.astype(np.uint8)
            
            if is_color:
                # Jika ingin menampilkan efek kuantisasi pada gambar berwarna,
                # kita perlu menerapkannya ke setiap channel atau hanya luminance.
                # Sederhananya, kita konversi balik ke grayscale untuk visualisasi "Gray-Level Slicing"
                self.processed_img_cv = quantized
            else:
                self.processed_img_cv = quantized
        else:
            self.processed_img_cv = res_sim
            
        self.display_image(self.processed_img_cv, self.lbl_result)

    def apply_equalization(self):
        if self.gray_img_cv is None: return
        eq_img = cv2.equalizeHist(self.gray_img_cv)
        self.processed_img_cv = eq_img
        self.display_image(self.processed_img_cv, self.lbl_result)
        self.draw_histograms()

    def apply_clahe(self):
        if self.gray_img_cv is None: return
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        res = clahe.apply(self.gray_img_cv)
        self.processed_img_cv = res
        self.display_image(self.processed_img_cv, self.lbl_result)
        self.draw_histograms()

    def apply_matching(self):
        if self.gray_img_cv is None: return
        if self.reference_img_cv is None:
            messagebox.showwarning("Warning", "Silakan muat gambar referensi terlebih dahulu (Load Ref).")
            return

        # Histogram Matching Algorithm
        src_hist, _ = np.histogram(self.gray_img_cv.flatten(), 256, [0, 256])
        src_cdf = src_hist.cumsum()
        src_cdf_norm = src_cdf / src_cdf.max()

        ref_hist, _ = np.histogram(self.reference_img_cv.flatten(), 256, [0, 256])
        ref_cdf = ref_hist.cumsum()
        ref_cdf_norm = ref_cdf / ref_cdf.max()

        lut = np.zeros(256, dtype=np.uint8)
        for g in range(256):
            idx = np.abs(ref_cdf_norm - src_cdf_norm[g]).argmin()
            lut[g] = idx

        res = cv2.LUT(self.gray_img_cv, lut)
        self.processed_img_cv = res
        
        self.display_image(self.processed_img_cv, self.lbl_result)
        self.draw_histograms()

    def draw_histograms(self):
        if self.gray_img_cv is None: return
        
        self.hist_canvas.delete("all")
        w = self.hist_canvas.winfo_width()
        h = self.hist_canvas.winfo_height()
        if w < 10: w = 400
        if h < 10: h = 150
        
        hist_orig = cv2.calcHist([self.gray_img_cv], [0], None, [256], [0, 256])
        cv2.normalize(hist_orig, hist_orig, 0, h, cv2.NORM_MINMAX)
        
        if self.processed_img_cv is None:
            comp_img = self.gray_img_cv
        elif len(self.processed_img_cv.shape) == 3:
             comp_img = cv2.cvtColor(self.processed_img_cv, cv2.COLOR_BGR2GRAY)
        else:
            comp_img = self.processed_img_cv
            
        hist_res = cv2.calcHist([comp_img], [0], None, [256], [0, 256])
        cv2.normalize(hist_res, hist_res, 0, h, cv2.NORM_MINMAX)
        
        bar_w = w / 256
        
        pts = []
        for i in range(256):
            val = int(hist_res[i])
            x = i * bar_w
            pts.append(x)
            pts.append(h - val)
        if len(pts) > 2:
            self.hist_canvas.create_line(pts, fill=COLORS["primary"], width=2)
            
        pts_orig = []
        for i in range(256):
            val = int(hist_orig[i])
            x = i * bar_w
            pts_orig.append(x)
            pts_orig.append(h - val)
        if len(pts_orig) > 2:
             self.hist_canvas.create_line(pts_orig, fill="#999999", width=1, dash=(2, 2))
             
        self.hist_canvas.create_text(10, 10, anchor="nw", text="--- Original", fill="#999999", font=("Segoe UI", 8))
        self.hist_canvas.create_text(10, 25, anchor="nw", text="___ Result", fill=COLORS["primary"], font=("Segoe UI", 8))