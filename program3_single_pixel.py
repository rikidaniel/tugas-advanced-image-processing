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
                                     "Perbaikan kualitas citra dengan operasi titik (Contrast Stretching).")

        content.columnconfigure(0, weight=3)  # Gambar
        content.columnconfigure(1, weight=1)  # Panel Kanan
        content.rowconfigure(0, weight=1)

        # Bagian Kiri: Preview Gambar
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

        # Bagian Kanan: Kontrol
        ctrl_panel = tk.Frame(content, bg="white")
        ctrl_panel.grid(row=0, column=1, sticky="ns")

        ttk.Label(ctrl_panel, text="Pengaturan Kontras", style="H2.TLabel").pack(anchor="w", pady=(0, 15))

        self.r1 = tk.IntVar(value=50);
        self.r2 = tk.IntVar(value=200)
        self.s1 = tk.IntVar(value=30);
        self.s2 = tk.IntVar(value=220)

        def create_slider(label, var):
            f = tk.Frame(ctrl_panel, bg="white")
            f.pack(fill="x", pady=5)
            tk.Label(f, text=label, bg="white", fg="#4B5563").pack(anchor="w")
            ttk.Scale(f, from_=0, to=255, variable=var, command=lambda _: self._constraints_and_preview()).pack(
                fill="x")

        create_slider("Input Min (r1)", self.r1)
        create_slider("Input Max (r2)", self.r2)
        create_slider("Output Min (s1)", self.s1)
        create_slider("Output Max (s2)", self.s2)

        # Grafik
        self.plot_label = tk.Label(ctrl_panel, bg="white", relief="solid", bd=1, height=140)
        self.plot_label.pack(fill="x", pady=20)

        # Tombol
        ttk.Button(ctrl_panel, text="📂 Buka Gambar", command=self.open_image, style="Primary.TButton").pack(fill="x",
                                                                                                            pady=5)
        ttk.Button(ctrl_panel, text="⚙️ Proses Manual", command=self.do_piecewise, style="Soft.TButton").pack(fill="x",
                                                                                                              pady=5)
        ttk.Button(ctrl_panel, text="✨ Auto Contrast", command=self.auto_apply, style="Soft.TButton").pack(fill="x",
                                                                                                           pady=5)
        ttk.Button(ctrl_panel, text="↺ Reset", command=self.reset_view, style="Danger.TButton").pack(fill="x",
                                                                                                     pady=(20, 0))

        self.img_bgr = None;
        self.img_gray = None
        self.tk_ori = None;
        self.tk_out = None;
        self.tk_plot = None;
        self.proc = None
        self._draw_transfer_plot()

    def _to_tk(self, img):
        pil = Image.fromarray(img)
        # Resize small preview
        pil = pil.resize((350, 200), Image.LANCZOS)
        return ImageTk.PhotoImage(pil)

    def _ensure_gray(self):
        if self.img_gray is None:
            messagebox.showwarning("Info", "Silakan buka gambar terlebih dahulu.")
            return False
        return True

    def _constraints_and_preview(self):
        if self.r2.get() <= self.r1.get(): self.r2.set(min(255, self.r1.get() + 1))
        if self.s2.get() <= self.s1.get(): self.s2.set(min(255, self.s1.get() + 1))
        self._draw_transfer_plot()

    def _draw_transfer_plot(self):
        W, H = 250, 140
        img = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(img)
        r1, r2, s1, s2 = self.r1.get(), self.r2.get(), self.s1.get(), self.s2.get()

        def tx(val): return int(val / 255 * W)

        def ty(val): return int(H - (val / 255 * H))

        pts = [(0, H), (tx(r1), ty(s1)), (tx(r2), ty(s2)), (W, 0)]
        d.line(pts, fill=COLORS["primary"], width=3)
        r = 4
        for x, y in pts: d.ellipse((x - r, y - r, x + r, y + r), fill=COLORS["danger"])

        self.tk_plot = ImageTk.PhotoImage(img)
        self.plot_label.config(image=self.tk_plot, height=H)

    def open_image(self):
        path = filedialog.askopenfilename()
        if not path: return
        raw = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if raw is None: return

        if raw.dtype == np.uint16:
            rmin, rmax = int(raw.min()), int(raw.max())
            norm = ((raw.astype(np.float32) - rmin) / (rmax - rmin) * 255.0).clip(0, 255).astype(
                np.uint8) if rmax > rmin else np.zeros_like(raw, dtype=np.uint8)
            raw = norm
        elif raw.dtype in (np.float32, np.float64):
            raw = raw.astype(np.uint8)

        if raw.ndim == 2:
            gray = raw;
            bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        else:
            bgr = raw[:, :, :3];
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        self.img_bgr, self.img_gray = bgr, gray
        self.tk_ori = self._to_tk(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        self.lbl_ori.config(image=self.tk_ori)
        self.reset_view()

    def reset_view(self):
        if self.img_bgr is None: return
        self.proc = self.img_gray.copy()
        self.tk_out = self._to_tk(self.proc)
        self.lbl_out.config(image=self.tk_out)

    def do_piecewise(self):
        if not self._ensure_gray(): return
        r1, r2, s1, s2 = self.r1.get(), self.r2.get(), self.s1.get(), self.s2.get()
        img = self.img_gray.astype(np.float32)

        out = img.copy()
        m1 = img <= r1
        m2 = (img > r1) & (img <= r2)
        m3 = img > r2

        if r1 > 0: out[m1] = (s1 / r1) * img[m1]
        if r2 > r1: out[m2] = ((s2 - s1) / (r2 - r1)) * (img[m2] - r1) + s1
        if 255 > r2: out[m3] = ((255 - s2) / (255 - r2)) * (img[m3] - r2) + s2

        self.proc = np.clip(out, 0, 255).astype(np.uint8)
        self.tk_out = self._to_tk(self.proc)
        self.lbl_out.config(image=self.tk_out)

    def auto_apply(self):
        if not self._ensure_gray(): return
        self.r1.set(int(np.percentile(self.img_gray, 5)))
        self.r2.set(int(np.percentile(self.img_gray, 95)))
        self.s1.set(0);
        self.s2.set(255)
        self._constraints_and_preview()
        self.do_piecewise()