import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import cv2
from base_frame import BaseFrame
from styles import COLORS

class SinglePixelApp(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)

        content = self.create_header("Image Enhancement",
                                     "Operasi Titik: Linear, Power-Law (Gamma), & Slicing.")

        content.columnconfigure(0, weight=3)  # Gambar
        content.columnconfigure(1, weight=1)  # Panel Kanan
        content.rowconfigure(0, weight=1)

        # --- Bagian Kiri: Preview Gambar ---
        img_grid = ttk.Frame(content, style="Card.TFrame")
        img_grid.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        img_grid.rowconfigure(0, weight=1)
        img_grid.rowconfigure(1, weight=1)
        img_grid.columnconfigure(0, weight=1)

        # Before
        frame_top = tk.Frame(img_grid, bg=COLORS["bg_main"])
        frame_top.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        tk.Label(frame_top, text="Original Image", bg=COLORS["bg_main"], fg="#4B5563",
                 font=("Segoe UI", 10, "bold")).pack(side="top", anchor="w")
        self.lbl_ori = tk.Label(frame_top, bg=COLORS["bg_main"])
        self.lbl_ori.pack(fill="both", expand=True)

        # After
        frame_bot = tk.Frame(img_grid, bg=COLORS["bg_main"])
        frame_bot.grid(row=1, column=0, sticky="nsew")
        tk.Label(frame_bot, text="Enhanced Result", bg=COLORS["bg_main"], fg="#4B5563",
                 font=("Segoe UI", 10, "bold")).pack(side="top", anchor="w")
        self.lbl_out = tk.Label(frame_bot, bg=COLORS["bg_main"])
        self.lbl_out.pack(fill="both", expand=True)

        # --- Bagian Kanan: Kontrol ---
        ctrl_panel = tk.Frame(content, bg="white")
        ctrl_panel.grid(row=0, column=1, sticky="ns")

        # Tab Control
        self.notebook = ttk.Notebook(ctrl_panel)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        # Tab 1: Linear (Contrast Stretching)
        self.tab_linear = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_linear, text="Linear")

        # Tab 2: Gamma Correction
        self.tab_gamma = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_gamma, text="Gamma")
        
        # Tab 3: Gray Level Slicing
        self.tab_slicing = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_slicing, text="Slicing")

        # --- Controls for Tab 1 (Linear) ---
        self.r1 = tk.IntVar(value=50)
        self.r2 = tk.IntVar(value=200)
        self.s1 = tk.IntVar(value=30)
        self.s2 = tk.IntVar(value=220)

        def create_slider(parent, label, var, limit=255):
            f = tk.Frame(parent)
            f.pack(fill="x", pady=5)
            tk.Label(f, text=label, fg="#4B5563").pack(anchor="w")
            ttk.Scale(f, from_=0, to=limit, variable=var, command=lambda _: self._update_preview()).pack(fill="x")

        create_slider(self.tab_linear, "Input Min (r1)", self.r1)
        create_slider(self.tab_linear, "Input Max (r2)", self.r2)
        create_slider(self.tab_linear, "Output Min (s1)", self.s1)
        create_slider(self.tab_linear, "Output Max (s2)", self.s2)
        
        ttk.Button(self.tab_linear, text="✨ Auto Contrast", command=self.auto_contrast, style="Soft.TButton").pack(fill="x", pady=5)
        ttk.Button(self.tab_linear, text="🔄 Invert Image (Negative)", command=self.negative_image, style="Soft.TButton").pack(fill="x", pady=5)

        # --- Controls for Tab 2 (Gamma) ---
        self.gamma_var = tk.DoubleVar(value=1.0)
        self.const_var = tk.DoubleVar(value=1.0) # Constant c
        
        def create_float_slider(parent, label, var, min_val, max_val, res):
            f = tk.Frame(parent)
            f.pack(fill="x", pady=5)
            hdr = tk.Frame(f)
            hdr.pack(fill="x")
            lbl_title = tk.Label(hdr, text=label, fg="#4B5563")
            lbl_title.pack(side="left")
            lbl_val = tk.Label(hdr, text=f"{var.get():.2f}", fg=COLORS["primary"], font=("Segoe UI", 9, "bold"))
            lbl_val.pack(side="right")
            
            def on_change(v):
                lbl_val.config(text=f"{float(v):.2f}")
                self._update_preview()
                
            ttk.Scale(f, from_=min_val, to=max_val, variable=var, command=on_change).pack(fill="x")

        # [Perbaikan] Rentang Gamma 0.1 - 5.0 (PDF Hal 4 c=0.3, 0.4, 0.6)
        create_float_slider(self.tab_gamma, "Gamma (\u03B3)", self.gamma_var, 0.1, 5.0, 0.1)
        
        # [Perbaikan] Rentang Constant (c) dinaikkan ke 5.0 agar sesuai PDF Hal 3 (c=1, 3, 4, 5)
        create_float_slider(self.tab_gamma, "Constant (c)", self.const_var, 0.1, 5.0, 0.1)

        # --- Controls for Tab 3 (Slicing) ---
        self.slice_a = tk.IntVar(value=100) # Range Min
        self.slice_b = tk.IntVar(value=180) # Range Max
        self.slice_preserve = tk.BooleanVar(value=True)
        
        create_slider(self.tab_slicing, "Range Min (A)", self.slice_a)
        create_slider(self.tab_slicing, "Range Max (B)", self.slice_b)
        
        ttk.Checkbutton(self.tab_slicing, text="Preserve Background", variable=self.slice_preserve, 
                        command=self._update_preview).pack(fill="x", pady=10)
        
        tk.Label(self.tab_slicing, text="Pixels in [A, B] -> White (255)\nOther pixels -> check preserve", 
                 fg="#666", font=("Segoe UI", 9, "italic"), justify="left").pack(anchor="w")

        # --- Plot Area (Shared) ---
        self.plot_label = tk.Label(ctrl_panel, bg="white", relief="solid", bd=1, height=140)
        self.plot_label.pack(fill="x", side="bottom", pady=20)
        tk.Label(ctrl_panel, text="Transfer Function", bg="white", font=("Segoe UI", 9, "italic")).pack(side="bottom")

        # --- Global Buttons ---
        btn_frame = tk.Frame(ctrl_panel, bg="white")
        btn_frame.pack(fill="x", side="top", pady=10)
        
        ttk.Button(btn_frame, text="📂 Buka Gambar", command=self.open_image, style="Primary.TButton").pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="↺ Reset", command=self.reset_view, style="Danger.TButton").pack(fill="x", pady=5)

        # --- State ---
        self.img_bgr = None
        self.img_gray = None
        self.tk_ori = None
        self.tk_out = None
        self.tk_plot = None
        
        self._draw_transfer_plot()

    def _on_tab_change(self, event):
        self._update_preview()

    def _to_tk(self, img):
        pil = Image.fromarray(img)
        pil.thumbnail((350, 200), Image.LANCZOS)
        return ImageTk.PhotoImage(pil)

    def _ensure_gray(self):
        if self.img_gray is None: return False
        return True

    def _update_preview(self):
        # 1. Update Plot
        self._draw_transfer_plot()
        
        # 2. Process Image
        if not self._ensure_gray(): return
        
        tab_idx = self.notebook.index(self.notebook.select())
        
        if tab_idx == 0: # Linear
            self._apply_contrast()
        elif tab_idx == 1: # Gamma
            self._apply_gamma()
        elif tab_idx == 2: # Slicing
            self._apply_slicing()

    def _draw_transfer_plot(self):
        W, H = 250, 140
        img = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(img)
        
        tab_idx = self.notebook.index(self.notebook.select())
        
        def tx(val): return int(val / 255 * W)
        def ty(val): return int(H - (val / 255 * H))
        
        if tab_idx == 0: # Linear
            r1, r2 = self.r1.get(), self.r2.get()
            s1, s2 = self.s1.get(), self.s2.get()
            if r2 < r1: r2 = r1
            
            pts = [(0, H), (tx(r1), ty(s1)), (tx(r2), ty(s2)), (W, 0)]
            d.line(pts, fill=COLORS["primary"], width=3)
            r = 4
            for x, y in pts: d.ellipse((x - r, y - r, x + r, y + r), fill=COLORS["danger"])
            
        elif tab_idx == 1: # Gamma
            gamma = self.gamma_var.get()
            c = self.const_var.get()
            
            pts = []
            for i in range(0, 256, 5):
                r_norm = i / 255.0
                s_norm = c * (r_norm ** gamma)
                s = np.clip(s_norm * 255, 0, 255)
                pts.append((tx(i), ty(s)))
            
            if len(pts) > 1:
                d.line(pts, fill=COLORS["primary"], width=3)
                
        elif tab_idx == 2: # Slicing
            a, b = self.slice_a.get(), self.slice_b.get()
            if b < a: b = a
            preserve = self.slice_preserve.get()
            
            # Draw line segments
            # Range [A, B] is always 255
            pts_high = [(tx(a), ty(255)), (tx(b), ty(255))]
            d.line(pts_high, fill=COLORS["primary"], width=3)
            
            # Left part [0, A]
            if preserve:
                # Identity y=x
                d.line([(0, H), (tx(a), ty(a))], fill=COLORS["primary"], width=2)
            else:
                # Zero y=0
                d.line([(0, H), (tx(a), H)], fill=COLORS["primary"], width=2)
                
            # Right part [B, 255]
            if preserve:
                # Identity y=x
                d.line([(tx(b), ty(b)), (W, 0)], fill=COLORS["primary"], width=2)
            else:
                # Zero y=0
                d.line([(tx(b), H), (W, H)], fill=COLORS["primary"], width=2)
                
            # Vertical connectors for visual continuity
            if preserve:
                 d.line([(tx(a), ty(a)), (tx(a), ty(255))], fill=COLORS["primary"], width=1)
                 d.line([(tx(b), ty(b)), (tx(b), ty(255))], fill=COLORS["primary"], width=1)
            else:
                 d.line([(tx(a), H), (tx(a), ty(255))], fill=COLORS["primary"], width=1)
                 d.line([(tx(b), H), (tx(b), ty(255))], fill=COLORS["primary"], width=1)

        self.tk_plot = ImageTk.PhotoImage(img)
        self.plot_label.config(image=self.tk_plot, height=H)

    def open_image(self):
        # [Perbaikan] Tambah Support TIFF
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.tif")])
        if not path: return
        raw = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if raw is None: return

        if raw.dtype == np.uint16:
            rmin, rmax = int(raw.min()), int(raw.max())
            norm = ((raw.astype(np.float32) - rmin) / (rmax - rmin) * 255.0).clip(0, 255).astype(np.uint8) if rmax > rmin else np.zeros_like(raw, dtype=np.uint8)
            raw = norm
        elif raw.dtype in (np.float32, np.float64):
            raw = raw.astype(np.uint8)

        if raw.ndim == 2:
            gray = raw
            bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        else:
            bgr = raw[:, :, :3]
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        self.img_bgr, self.img_gray = bgr, gray
        self.tk_ori = self._to_tk(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        self.lbl_ori.config(image=self.tk_ori)
        
        self._update_preview()

    def reset_view(self):
        if self.img_bgr is None: return
        self.r1.set(50); self.r2.set(200); self.s1.set(30); self.s2.set(220)
        self.gamma_var.set(1.0); self.const_var.set(1.0)
        self.slice_a.set(100); self.slice_b.set(180); self.slice_preserve.set(True)
        self.notebook.select(0)
        self._update_preview()

    def auto_contrast(self):
        if not self._ensure_gray(): return
        self.r1.set(int(np.percentile(self.img_gray, 5)))
        self.r2.set(int(np.percentile(self.img_gray, 95)))
        self.s1.set(0)
        self.s2.set(255)
        self.notebook.select(0)
        self._update_preview()

    def negative_image(self):
        self.r1.set(0)
        self.r2.set(255)
        self.s1.set(255)
        self.s2.set(0)
        self.notebook.select(0)
        self._update_preview()

    def _apply_contrast(self):
        r1, r2, s1, s2 = self.r1.get(), self.r2.get(), self.s1.get(), self.s2.get()
        if r2 < r1: r2 = r1
        
        img = self.img_gray.astype(np.float32)
        out = img.copy()
        
        m1 = img <= r1
        m2 = (img > r1) & (img <= r2)
        m3 = img > r2

        if r1 > 0: 
            out[m1] = (s1 / r1) * img[m1]
        if r2 > r1: 
            out[m2] = ((s2 - s1) / (r2 - r1)) * (img[m2] - r1) + s1
        if 255 > r2:
            denom = 255 - r2
            if denom == 0: denom = 1
            out[m3] = ((255 - s2) / denom) * (img[m3] - r2) + s2

        res = np.clip(out, 0, 255).astype(np.uint8)
        self.tk_out = self._to_tk(res)
        self.lbl_out.config(image=self.tk_out)

    def _apply_gamma(self):
        gamma = self.gamma_var.get()
        c = self.const_var.get()
        invGamma = gamma
        table = np.array([((i / 255.0) ** invGamma) * 255 * c for i in np.arange(0, 256)]).astype("uint8")
        res = cv2.LUT(self.img_gray, table)
        self.tk_out = self._to_tk(res)
        self.lbl_out.config(image=self.tk_out)
        
    def _apply_slicing(self):
        a, b = self.slice_a.get(), self.slice_b.get()
        if b < a: b = a
        preserve = self.slice_preserve.get()
        
        img = self.img_gray.copy()
        
        # Create mask for pixels in [A, B]
        mask = (img >= a) & (img <= b)
        
        # Logic
        if preserve:
            img[mask] = 255
        else:
            out = np.zeros_like(img)
            out[mask] = 255
            img = out
            
        self.tk_out = self._to_tk(img)
        self.lbl_out.config(image=self.tk_out)