import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
from base_frame import BaseFrame


class ArithmeticApp(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)
        content = self.create_header("Arithmetic Operations (PDF Page 7-10)",
                                     "Logic (Pg 7), Subtraction (Pg 8), Averaging (Pg 9).")

        self.notebook = ttk.Notebook(content)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))

        # --- Variables to store results for switching ---
        self.logic_imgs = {"A": None, "B": None}

        # Subtraction Results Storage (a, b, c, d)
        self.sub_res = {}

        # Averaging Results Storage (a, b, c, d, e, f)
        self.avg_res = {}
        self.avg_src_img = None  # Simpan source asli

        # --- TAB 1: LOGIC (Page 7) ---
        self.tab_logic = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_logic, text="Pg 7: Logic")
        self.setup_logic_tab()

        # --- TAB 2: SUBTRACTION (Page 8) ---
        self.tab_sub = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_sub, text="Pg 8: Subtraction")
        self.setup_subtraction_tab()

        # --- TAB 3: AVERAGING (Page 9) ---
        self.tab_avg = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_avg, text="Pg 9: Averaging")
        self.setup_averaging_tab()

    # =========================================================================
    # TAB 1: LOGIC OPERATIONS (Tetap Layout Standar karena butuh 2 Input)
    # =========================================================================
    def setup_logic_tab(self):
        ctrl = ttk.Frame(self.tab_logic)
        ctrl.pack(fill="x", pady=10)

        ttk.Button(ctrl, text="🧩 Generate Shapes", command=self.gen_logic_shapes, style="Primary.TButton").pack(
            side="left", padx=5)
        ttk.Label(ctrl, text=" | ", style="Sub.TLabel").pack(side="left", padx=5)
        ttk.Button(ctrl, text="📂 Load A", command=lambda: self.load_logic("A"), style="Soft.TButton").pack(side="left",
                                                                                                           padx=2)
        ttk.Button(ctrl, text="📂 Load B", command=lambda: self.load_logic("B"), style="Soft.TButton").pack(side="left",
                                                                                                           padx=2)

        ttk.Label(ctrl, text="Op:", style="Sub.TLabel").pack(side="left", padx=(15, 5))
        self.logic_op = tk.StringVar(value="AND")
        ttk.Combobox(ctrl, textvariable=self.logic_op, values=["AND", "OR", "XOR"], width=6, state="readonly").pack(
            side="left")
        ttk.Button(ctrl, text="▶ Run", command=self.run_logic, style="Primary.TButton").pack(side="left", padx=10)

        grid = ttk.Frame(self.tab_logic)
        grid.pack(fill="both", expand=True)
        self.lbl_log_a = self.create_img_frame(grid, 0, 0, "Image A")
        self.lbl_log_b = self.create_img_frame(grid, 0, 1, "Image B")
        self.lbl_log_res = self.create_img_frame(grid, 0, 2, "Result")

    def gen_logic_shapes(self):
        img_a = np.zeros((300, 300), dtype=np.uint8)
        cv2.rectangle(img_a, (50, 50), (250, 250), 255, -1)
        img_b = np.zeros((300, 300), dtype=np.uint8)
        cv2.circle(img_b, (150, 150), 120, 255, -1)
        self.logic_imgs["A"] = img_a
        self.logic_imgs["B"] = img_b
        self.display_image(img_a, self.lbl_log_a)
        self.display_image(img_b, self.lbl_log_b)
        self.run_logic()

    def load_logic(self, target):
        img = self._load_img()
        if img is not None:
            self.logic_imgs[target] = img
            lbl = self.lbl_log_a if target == "A" else self.lbl_log_b
            self.display_image(img, lbl)

    def run_logic(self):
        if self.logic_imgs["A"] is None or self.logic_imgs["B"] is None: return
        h, w = self.logic_imgs["A"].shape[:2]
        img_b = cv2.resize(self.logic_imgs["B"], (w, h))
        img_a = self.logic_imgs["A"]

        # Color match
        if len(img_a.shape) == 3 and len(img_b.shape) == 2:
            img_b = cv2.cvtColor(img_b, cv2.COLOR_GRAY2BGR)
        elif len(img_a.shape) == 2 and len(img_b.shape) == 3:
            img_a = cv2.cvtColor(img_a, cv2.COLOR_GRAY2BGR)

        op = self.logic_op.get()
        if op == "AND":
            res = cv2.bitwise_and(img_a, img_b)
        elif op == "OR":
            res = cv2.bitwise_or(img_a, img_b)
        else:
            res = cv2.bitwise_xor(img_a, img_b)
        self.display_image(res, self.lbl_log_res)

    # =========================================================================
    # TAB 2: SUBTRACTION (Single View + 4 Tombol)
    # =========================================================================
    def setup_subtraction_tab(self):
        # 1. Controls Top
        top_bar = ttk.Frame(self.tab_sub)
        top_bar.pack(fill="x", pady=10)
        ttk.Button(top_bar, text="📂 1. Load Source Image", command=self.load_sub_src, style="Primary.TButton").pack(
            side="left")
        self.lbl_sub_status = tk.Label(top_bar, text="Silakan load gambar...", fg="#666")
        self.lbl_sub_status.pack(side="left", padx=10)

        # 2. Main Single Image Display
        self.sub_display_frame = ttk.Frame(self.tab_sub, style="Card.TFrame")
        self.sub_display_frame.pack(fill="both", expand=True, padx=50, pady=10)

        self.lbl_sub_main = tk.Label(self.sub_display_frame, bg="#F1F5F9", text="No Image")
        self.lbl_sub_main.pack(fill="both", expand=True)

        # 3. Bottom Toggle Buttons (a, b, c, d)
        btn_bar = ttk.Frame(self.tab_sub)
        btn_bar.pack(fill="x", pady=15)

        # Tombol-tombol View
        self.btn_sub_a = ttk.Button(btn_bar, text="(a) Original", command=lambda: self.show_sub('a'), state="disabled")
        self.btn_sub_a.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_sub_b = ttk.Button(btn_bar, text="(b) Masked (Low Bit 0)", command=lambda: self.show_sub('b'),
                                    state="disabled")
        self.btn_sub_b.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_sub_c = ttk.Button(btn_bar, text="(c) Difference", command=lambda: self.show_sub('c'),
                                    state="disabled")
        self.btn_sub_c.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_sub_d = ttk.Button(btn_bar, text="(d) Hist. Equalized", command=lambda: self.show_sub('d'),
                                    state="disabled")
        self.btn_sub_d.pack(side="left", expand=True, fill="x", padx=2)

        # Save Button di pojok kanan bawah
        ttk.Button(btn_bar, text="💾 Save View", command=lambda: self.save_current_sub_view(),
                   style="Soft.TButton").pack(side="right", padx=10)

    def load_sub_src(self):
        img = self._load_img()
        if img is not None:
            if len(img.shape) == 3: img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.process_subtraction_all(img)

    def process_subtraction_all(self, img_a):
        # Hitung SEMUA 4 tahap sekaligus dan simpan di memory
        # (a) Original
        self.sub_res['a'] = img_a

        # (b) Masking (Lower 4 bits zeroed)
        mask = 0xF0
        img_b = (img_a & mask).astype(np.uint8)
        self.sub_res['b'] = img_b

        # (c) Difference
        diff = cv2.absdiff(img_a, img_b)
        self.sub_res['c'] = diff

        # (d) Equalized
        diff_eq = cv2.equalizeHist(diff)
        self.sub_res['d'] = diff_eq

        # Aktifkan tombol
        for btn in [self.btn_sub_a, self.btn_sub_b, self.btn_sub_c, self.btn_sub_d]:
            btn.config(state="normal")

        # Default tampilkan hasil akhir (d)
        self.show_sub('d')
        self.lbl_sub_status.config(text="Proses Selesai. Gunakan tombol di bawah untuk melihat tahapan.")

    def show_sub(self, key):
        if key in self.sub_res:
            self.display_image_large(self.sub_res[key], self.lbl_sub_main)
            self.current_sub_view = self.sub_res[key]  # untuk save

    def save_current_sub_view(self):
        if hasattr(self, 'current_sub_view') and self.current_sub_view is not None:
            self.save_image_cv(self.current_sub_view, "subtraction_view")

    # =========================================================================
    # TAB 3: AVERAGING (Single View + Tombol)
    # =========================================================================
    def setup_averaging_tab(self):
        # 1. Controls Top
        top_bar = ttk.Frame(self.tab_avg)
        top_bar.pack(fill="x", pady=10)
        ttk.Button(top_bar, text="📂 1. Load Source Image", command=self.load_avg_src, style="Primary.TButton").pack(
            side="left")
        ttk.Button(top_bar, text="▶ 2. Run Simulation", command=self.run_averaging_all, style="Soft.TButton").pack(
            side="left", padx=10)
        self.lbl_avg_status = tk.Label(top_bar, text="Load gambar lalu klik Run", fg="#666")
        self.lbl_avg_status.pack(side="left")

        # 2. Main Single Image Display
        self.avg_display_frame = ttk.Frame(self.tab_avg, style="Card.TFrame")
        self.avg_display_frame.pack(fill="both", expand=True, padx=50, pady=10)

        self.lbl_avg_main = tk.Label(self.avg_display_frame, bg="#F1F5F9", text="No Image")
        self.lbl_avg_main.pack(fill="both", expand=True)

        # 3. Bottom Toggle Buttons (a, b, c, d, e, f)
        btn_bar = ttk.Frame(self.tab_avg)
        btn_bar.pack(fill="x", pady=15)

        self.avg_btns = {}
        # Definisi tombol sesuai PDF Page 9 (a-f)
        labels = [("Orig (a)", 'a'), ("Noisy (b)", 'b'), ("K=8 (c)", 'c'),
                  ("K=16 (d)", 'd'), ("K=64 (e)", 'e'), ("K=128 (f)", 'f')]

        for text, key in labels:
            btn = ttk.Button(btn_bar, text=text, command=lambda k=key: self.show_avg(k), state="disabled")
            btn.pack(side="left", expand=True, fill="x", padx=1)
            self.avg_btns[key] = btn

        # Save Button
        ttk.Button(btn_bar, text="💾 Save View", command=lambda: self.save_current_avg_view(),
                   style="Soft.TButton").pack(side="right", padx=10)

    def load_avg_src(self):
        img = self._load_img()
        if img is not None:
            if len(img.shape) == 3: img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.avg_src_img = img
            self.display_image_large(img, self.lbl_avg_main)
            self.lbl_avg_status.config(text="Gambar siap. Klik 'Run Simulation'.")

    def run_averaging_all(self):
        if self.avg_src_img is None:
            messagebox.showwarning("Warning", "Load Image First")
            return

        self.lbl_avg_status.config(text="Processing simulation... (Might take a sec)")
        self.update()  # Force UI refresh

        img_clean = self.avg_src_img.astype(np.float32)
        h, w = img_clean.shape

        # (a) Original
        self.avg_res['a'] = self.avg_src_img

        # (b) Noisy Sample (Just 1 noise instance)
        sample_noise = np.random.normal(0, 64, (h, w)).astype(np.float32)
        noisy_sample = np.clip(img_clean + sample_noise, 0, 255).astype(np.uint8)
        self.avg_res['b'] = noisy_sample

        # Simulasi Averaging K=8, 16, 64, 128
        accumulator = np.zeros_like(img_clean)
        ks = [8, 16, 64, 128]
        keys = ['c', 'd', 'e', 'f']

        # Kita butuh max K=128
        for i in range(1, 129):
            noise = np.random.normal(0, 64, (h, w)).astype(np.float32)
            accumulator += (img_clean + noise)

            if i in ks:
                idx = ks.index(i)
                key = keys[idx]
                avg_img = np.clip(accumulator / i, 0, 255).astype(np.uint8)
                self.avg_res[key] = avg_img

        # Aktifkan semua tombol
        for key in self.avg_btns:
            self.avg_btns[key].config(state="normal")

        # Tampilkan hasil terbaik (K=128)
        self.show_avg('f')
        self.lbl_avg_status.config(text="Selesai. Klik tombol (a)-(f) untuk membandingkan.")

    def show_avg(self, key):
        if key in self.avg_res:
            self.display_image_large(self.avg_res[key], self.lbl_avg_main)
            self.current_avg_view = self.avg_res[key]

    def save_current_avg_view(self):
        if hasattr(self, 'current_avg_view') and self.current_avg_view is not None:
            self.save_image_cv(self.current_avg_view, "averaging_view")

    # =========================================================================
    # HELPERS
    # =========================================================================
    def create_img_frame(self, parent, row, col, title):
        parent.columnconfigure(col, weight=1)
        f = ttk.Frame(parent, style="Card.TFrame")
        f.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
        tk.Label(f, text=title, bg="#F1F5F9", font=("Segoe UI", 8, "bold")).pack(fill="x")
        lbl = tk.Label(f, bg="#F1F5F9")
        lbl.pack(fill="both", expand=True)
        return lbl

    def _load_img(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff")])
        if not path: return None
        return cv2.imread(path)

    # [PERBAIKAN] Menambahkan kembali display_image untuk Tab Logic (gambar kecil)
    def display_image(self, cv_img, label_widget):
        if cv_img is None: return
        try:
            h, w = cv_img.shape[:2]
            target_size = 250  # Ukuran untuk grid kecil logic
            scale = target_size / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)

            if len(cv_img.shape) == 2:
                img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
            else:
                img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

            pil_img = Image.fromarray(img_rgb)
            pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil_img)

            label_widget.config(image=tk_img)
            label_widget.image = tk_img
        except Exception as e:
            print(f"Error display: {e}")

    # [PERBAIKAN] Menambahkan display_image_large untuk Tab Subtraction/Averaging (gambar besar)
    def display_image_large(self, cv_img, label_widget):
        if cv_img is None: return
        try:
            h, w = cv_img.shape[:2]
            # Tampilan besar (max height 500)
            target_h = 500
            scale = target_h / h
            new_w, new_h = int(w * scale), int(h * scale)

            if len(cv_img.shape) == 2:
                img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
            else:
                img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

            pil_img = Image.fromarray(img_rgb)
            pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil_img)

            label_widget.config(image=tk_img)
            label_widget.image = tk_img
        except Exception as e:
            print(f"Error display: {e}")