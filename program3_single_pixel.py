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
        content = self.create_header("Image Negative, Power-Law & Slicing",
                                     "Operasi Titik: Intensity Transformations sesuai Topik PDF.")

        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        # --- Preview Gambar ---
        img_grid = ttk.Frame(content, style="Card.TFrame")
        img_grid.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        img_grid.rowconfigure(0, weight=1)
        img_grid.rowconfigure(1, weight=1)
        img_grid.columnconfigure(0, weight=1)

        frame_top = tk.Frame(img_grid, bg=COLORS["bg_main"])
        frame_top.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        tk.Label(frame_top, text="Original Image", bg=COLORS["bg_main"], font=("Segoe UI", 10, "bold")).pack(side="top",
                                                                                                             anchor="w")
        self.lbl_ori = tk.Label(frame_top, bg=COLORS["bg_main"])
        self.lbl_ori.pack(fill="both", expand=True)

        frame_bot = tk.Frame(img_grid, bg=COLORS["bg_main"])
        frame_bot.grid(row=1, column=0, sticky="nsew")
        tk.Label(frame_bot, text="Result Image", bg=COLORS["bg_main"], font=("Segoe UI", 10, "bold")).pack(side="top",
                                                                                                           anchor="w")
        self.lbl_out = tk.Label(frame_bot, bg=COLORS["bg_main"])
        self.lbl_out.pack(fill="both", expand=True)

        # --- Kontrol ---
        ctrl_panel = tk.Frame(content, bg="white")
        ctrl_panel.grid(row=0, column=1, sticky="ns")

        self.notebook = ttk.Notebook(ctrl_panel)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        self.tab_neg = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_neg, text="Negative")
        self.tab_power = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_power, text="Power-Law")
        self.tab_slice = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_slice, text="Slicing")

        # Tab 1: Negative
        ttk.Button(self.tab_neg, text="🔄 Apply Image Negative", command=self.negative_image,
                   style="Primary.TButton").pack(fill="x", pady=20)

        # Tab 2: Power-Law (Gamma)
        self.gamma_var = tk.DoubleVar(value=1.0)
        self.const_var = tk.DoubleVar(value=1.0)

        # [FITUR BARU] Preset Gamma sesuai PDF Page 3
        preset_frame = tk.Frame(self.tab_power)
        preset_frame.pack(fill="x", pady=(0, 10))
        tk.Label(preset_frame, text="Presets (PDF Page 3):", fg="#666", font=("Segoe UI", 8)).pack(anchor="w")

        # Lambda harus pakai default value agar tidak ter-overwrite loop
        for val in [0.4, 1.0, 3.0, 4.0, 5.0]:
            btn = tk.Button(preset_frame, text=f"γ={val}", font=("Segoe UI", 8),
                            command=lambda v=val: self.set_gamma(v))
            btn.pack(side="left", padx=2)

        def create_float_slider(parent, label, var, min_val, max_val):
            f = tk.Frame(parent)
            f.pack(fill="x", pady=5)
            hdr = tk.Frame(f)
            hdr.pack(fill="x")
            tk.Label(hdr, text=label, fg="#4B5563").pack(side="left")
            lbl_val = tk.Label(hdr, text=f"{var.get():.2f}", fg=COLORS["primary"], font=("Segoe UI", 9, "bold"))
            lbl_val.pack(side="right")

            def on_change(v):
                lbl_val.config(text=f"{float(v):.2f}")
                self._update_preview()

            ttk.Scale(f, from_=min_val, to=max_val, variable=var, command=on_change).pack(fill="x")
            return lbl_val

        self.lbl_gamma_val = create_float_slider(self.tab_power, "Gamma (\u03B3)", self.gamma_var, 0.1, 5.0)
        create_float_slider(self.tab_power, "Constant (c)", self.const_var, 0.1, 5.0)

        # Tab 3: Slicing
        self.slice_a = tk.IntVar(value=100)
        self.slice_b = tk.IntVar(value=180)
        self.slice_preserve = tk.BooleanVar(value=True)

        def create_int_slider(parent, label, var):
            f = tk.Frame(parent)
            f.pack(fill="x", pady=5)
            tk.Label(f, text=label, fg="#4B5563").pack(anchor="w")
            ttk.Scale(f, from_=0, to=255, variable=var, command=lambda _: self._update_preview()).pack(fill="x")

        create_int_slider(self.tab_slice, "Range Min (A)", self.slice_a)
        create_int_slider(self.tab_slice, "Range Max (B)", self.slice_b)
        ttk.Checkbutton(self.tab_slice, text="Preserve Background", variable=self.slice_preserve,
                        command=self._update_preview).pack(fill="x", pady=10)

        # Plot & Global
        self.plot_label = tk.Label(ctrl_panel, bg="white", relief="solid", bd=1, height=140)
        self.plot_label.pack(fill="x", side="bottom", pady=20)

        btn_frame = tk.Frame(ctrl_panel, bg="white")
        btn_frame.pack(fill="x", side="top", pady=10)
        ttk.Button(btn_frame, text="📂 Buka Gambar", command=self.open_image, style="Primary.TButton").pack(fill="x",
                                                                                                           pady=5)
        ttk.Button(btn_frame, text="↺ Reset", command=self.reset_view, style="Danger.TButton").pack(fill="x", pady=5)

        self.img_bgr = None;
        self.img_gray = None
        self.tk_ori = None;
        self.tk_out = None
        self._draw_transfer_plot()

    def set_gamma(self, val):
        self.gamma_var.set(val)
        self.lbl_gamma_val.config(text=f"{val:.2f}")
        self._update_preview()

    def _on_tab_change(self, event):
        self._update_preview()

    def _to_tk(self, img):
        pil = Image.fromarray(img)
        pil.thumbnail((350, 200), Image.LANCZOS)
        return ImageTk.PhotoImage(pil)

    def _ensure_gray(self):
        return self.img_gray is not None

    def _update_preview(self):
        self._draw_transfer_plot()
        if not self._ensure_gray(): return
        tab_idx = self.notebook.index(self.notebook.select())
        if tab_idx == 0:
            self._apply_negative()
        elif tab_idx == 1:
            self._apply_gamma()
        elif tab_idx == 2:
            self._apply_slicing()

    def _draw_transfer_plot(self):
        W, H = 250, 140
        img = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(img)
        tab_idx = self.notebook.index(self.notebook.select())

        def tx(val):
            return int(val / 255 * W)

        def ty(val):
            return int(H - (val / 255 * H))

        if tab_idx == 0:
            d.line([(0, 0), (W, H)], fill=COLORS["primary"], width=3)
        elif tab_idx == 1:
            gamma = self.gamma_var.get()
            c = self.const_var.get()
            pts = []
            for i in range(0, 256, 5):
                r = i / 255.0
                s = np.clip(c * (r ** gamma) * 255, 0, 255)
                pts.append((tx(i), ty(s)))
            if len(pts) > 1: d.line(pts, fill=COLORS["primary"], width=3)
        elif tab_idx == 2:
            a, b = self.slice_a.get(), self.slice_b.get()
            if b < a: b = a
            d.line([(tx(a), ty(255)), (tx(b), ty(255))], fill=COLORS["primary"], width=3)
            if self.slice_preserve.get():
                d.line([(0, H), (tx(a), ty(a))], fill=COLORS["primary"], width=2)
                d.line([(tx(b), ty(b)), (W, 0)], fill=COLORS["primary"], width=2)
            else:
                d.line([(0, H), (tx(a), H)], fill=COLORS["primary"], width=2)
                d.line([(tx(b), H), (W, H)], fill=COLORS["primary"], width=2)

        self.tk_plot = ImageTk.PhotoImage(img)
        self.plot_label.config(image=self.tk_plot, height=H)

    def open_image(self):
        path = filedialog.askopenfilename()
        if not path: return
        raw = cv2.imread(path)
        if raw is None: return
        self.img_bgr = raw
        self.img_gray = cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY)
        self.tk_ori = self._to_tk(cv2.cvtColor(raw, cv2.COLOR_BGR2RGB))
        self.lbl_ori.config(image=self.tk_ori)
        self._update_preview()

    def reset_view(self):
        self.gamma_var.set(1.0);
        self.const_var.set(1.0)
        self.slice_a.set(100);
        self.slice_b.set(180)
        self.notebook.select(0)
        self._update_preview()

    def negative_image(self):
        self._update_preview()

    def _apply_negative(self):
        self.tk_out = self._to_tk(255 - self.img_gray)
        self.lbl_out.config(image=self.tk_out)

    def _apply_gamma(self):
        gamma = self.gamma_var.get();
        c = self.const_var.get()
        table = np.array([((i / 255.0) ** gamma) * 255 * c for i in range(256)]).astype("uint8")
        self.tk_out = self._to_tk(cv2.LUT(self.img_gray, table))
        self.lbl_out.config(image=self.tk_out)

    def _apply_slicing(self):
        a, b = self.slice_a.get(), self.slice_b.get();
        if b < a: b = a
        img = self.img_gray.copy();
        mask = (img >= a) & (img <= b)
        if self.slice_preserve.get():
            img[mask] = 255
        else:
            out = np.zeros_like(img); out[mask] = 255; img = out
        self.tk_out = self._to_tk(img)
        self.lbl_out.config(image=self.tk_out)