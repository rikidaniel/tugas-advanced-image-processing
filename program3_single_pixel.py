import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import cv2


class SinglePixelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Program 3 - Image enhancement")
        self.root.geometry("1120x740")

        header = tk.Frame(root)
        header.pack(fill="x", pady=6)

        tk.Button(header, text="Buka Gambar", command=self.open_image).pack(side="left", padx=8)
        tk.Label(header, text="14240032", font=("Arial", 12, "bold")).pack(side="left", padx=14)
        tk.Label(header, text="Riki Daniel Tanebeth", font=("Arial", 12, "bold")).pack(side="left", padx=14)

        body = tk.Frame(root)
        body.pack(expand=True, fill="both", padx=10, pady=6)

        canvas_frame = tk.Frame(body)
        canvas_frame.pack(side="left", expand=True, fill="both")

        self.lbl_ori = tk.Label(canvas_frame, text="Before (Asli)", bg="white", width=60, height=22, relief="sunken")
        self.lbl_ori.grid(row=0, column=0, padx=6, pady=(6,3), sticky="nsew")

        self.lbl_out = tk.Label(canvas_frame, text="After (Hasil)", bg="white", width=60, height=22, relief="sunken")
        self.lbl_out.grid(row=1, column=0, padx=6, pady=(3,6), sticky="nsew")

        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.rowconfigure(1, weight=1)

        right = tk.Frame(body)
        right.pack(side="left", fill="y", padx=(10,0))

        cs = tk.LabelFrame(right, text="Pengaturan Kontras (Pencahayaan)")
        cs.pack(fill="x", padx=6, pady=6)

        self.r1 = tk.IntVar(value=50)
        self.r2 = tk.IntVar(value=200)
        self.s1 = tk.IntVar(value=30)
        self.s2 = tk.IntVar(value=220)

        def add_slider(row, label, var):
            tk.Label(cs, text=label, width=10, anchor="e").grid(row=row, column=0, padx=(6,4), pady=2)
            tk.Scale(cs, from_=0, to=255, orient="horizontal", variable=var, length=240,
                     command=lambda _=None: self._constraints_and_preview())\
                .grid(row=row, column=1, pady=2, sticky="w")

        add_slider(0, "r1", self.r1)
        add_slider(1, "r2", self.r2)
        add_slider(2, "s1", self.s1)
        add_slider(3, "s2", self.s2)

        btns = tk.Frame(cs); btns.grid(row=4, column=0, columnspan=2, pady=6, sticky="w", padx=6)
        tk.Button(btns, text="Terapkan Pengaturan", command=self.do_piecewise).pack(side="left")
        tk.Button(btns, text="Terapkan Otomatis", command=self.auto_apply).pack(side="left", padx=6)

        self.plot_label = tk.Label(cs, bg="white", width=32, height=16, relief="sunken")
        self.plot_label.grid(row=0, column=2, rowspan=5, padx=(10,6), pady=4)

        tk.Button(right, text="Reset ke Asli", command=self.reset_view)\
            .pack(fill="x", padx=12, pady=(0,10))

        self.img_bgr = None
        self.img_gray = None
        self.tk_ori = None
        self.tk_out = None
        self.tk_plot = None
        self.proc = None

        self._draw_transfer_plot()

    # ---------- utils ----------
    def _to_tk(self, img):
        pil = Image.fromarray(img)
        pil = pil.resize((510, 330), Image.LANCZOS)
        return ImageTk.PhotoImage(pil)

    def _ensure_gray(self):
        if self.img_gray is None:
            messagebox.showwarning("Peringatan", "Silakan buka gambar terlebih dahulu.")
            return False
        return True

    def _constraints_and_preview(self):
        if self.r2.get() <= self.r1.get():
            self.r2.set(min(255, self.r1.get() + 1))
        if self.s2.get() <= self.s1.get():
            self.s2.set(min(255, self.s1.get() + 1))
        self._draw_transfer_plot()

    def _draw_transfer_plot(self):
        W = H = 256
        img = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(img)

        margin = 20
        x0, y0 = margin, H - margin
        x1, y1 = W - margin, margin

        d.rectangle([x0, y1, x1, y0], outline="black", width=2)

        r1, r2, s1, s2 = self.r1.get(), self.r2.get(), self.s1.get(), self.s2.get()

        def to_xy(r, s):
            x = x0 + (x1 - x0) * (r / 255.0)
            y = y0 - (y0 - y1) * (s / 255.0)
            return (x, y)

        p0 = to_xy(0, 0)
        p1 = to_xy(r1, s1)
        p2 = to_xy(r2, s2)
        p3 = to_xy(255, 255)
        d.line([p0, p1, p2, p3], fill="black", width=3)
        for (rx, sx) in [(r1, s1), (r2, s2)]:
            px, py = to_xy(rx, sx)
            d.ellipse([px-3, py-3, px+3, py+3], fill="black")

        img = img.resize((250, 250), Image.LANCZOS)
        self.tk_plot = ImageTk.PhotoImage(img)
        self.plot_label.config(image=self.tk_plot)

    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Gambar", "*.tif;*.tiff;*.jpg;*.jpeg;*.png;*.bmp")]
        )
        if not path:
            return

        raw = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if raw is None:
            messagebox.showerror("Error", "Gagal membuka gambar.")
            return

        if raw.dtype == np.uint16:
            rmin, rmax = int(raw.min()), int(raw.max())
            if rmax > rmin:
                norm = ((raw.astype(np.float32) - rmin) / (rmax - rmin) * 255.0).clip(0, 255).astype(np.uint8)
            else:
                norm = np.zeros_like(raw, dtype=np.uint8)
            raw = norm
        elif raw.dtype in (np.float32, np.float64):
            mn, mx = float(np.nanmin(raw)), float(np.nanmax(raw))
            if mx > mn:
                raw = ((raw - mn) / (mx - mn) * 255.0).clip(0, 255).astype(np.uint8)
            else:
                raw = np.zeros_like(raw, dtype=np.uint8)
        else:
            raw = raw.astype(np.uint8)

        if raw.ndim == 2:
            gray = raw
            bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        else:
            bgr = raw[:, :, :3] if raw.shape[2] >= 3 else raw
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        self.img_bgr = bgr
        self.img_gray = gray

        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        self.tk_ori = self._to_tk(rgb)
        self.lbl_ori.config(image=self.tk_ori)

        self.proc = self.img_gray.copy()
        self.tk_out = self._to_tk(self.proc)
        self.lbl_out.config(image=self.tk_out)


    def reset_view(self):
        if self.img_bgr is None:
            return
        self.proc = self.img_gray.copy()
        self.tk_out = self._to_tk(self.proc)
        self.lbl_out.config(image=self.tk_out)

    def do_piecewise(self):
        if not self._ensure_gray(): return
        r1, r2, s1, s2 = map(int, (self.r1.get(), self.r2.get(), self.s1.get(), self.s2.get()))
        r1 = max(0, min(254, r1))
        r2 = max(r1+1, min(255, r2))
        s1 = max(0, min(254, s1))
        s2 = max(s1+1, min(255, s2))

        img = self.img_gray.astype(np.float32)

        if r1 > 0:
            a1 = s1 / r1
            seg1 = (img <= r1) * (a1 * img)
        else:
            seg1 = (img <= r1) * 0.0

        a2 = (s2 - s1) / max(1.0, (r2 - r1))
        b2 = s1 - a2 * r1
        seg2 = ((img > r1) & (img <= r2)) * (a2 * img + b2)

        a3 = (255 - s2) / max(1.0, (255 - r2))
        b3 = s2 - a3 * r2
        seg3 = (img > r2) * (a3 * img + b3)

        out = seg1 + seg2 + seg3
        out = np.clip(out, 0, 255).astype(np.uint8)

        self.proc = out
        self.tk_out = self._to_tk(self.proc)
        self.lbl_out.config(image=self.tk_out)
        self._draw_transfer_plot()

    def auto_apply(self, p_low=2, p_high=98):
        if not self._ensure_gray(): return
        img = self.img_gray
        r1 = int(np.percentile(img, p_low))
        r2 = int(np.percentile(img, p_high))
        if r2 <= r1:
            r2 = min(255, r1 + 1)
        self.r1.set(r1); self.r2.set(r2)
        self.s1.set(0);  self.s2.set(255)
        self._draw_transfer_plot()
        self.do_piecewise()


if __name__ == "__main__":
    root = tk.Tk()
    app = SinglePixelApp(root)
    root.mainloop()
