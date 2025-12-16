import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
from base_frame import BaseFrame
from styles import COLORS


class ArithmeticApp(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)

        content = self.create_header("Arithmetic & Logic Operations",
                                     "Subtraction, Averaging, & Logic Ops (AND/OR/XOR).")

        # --- Control Panel ---
        ctrl_frame = ttk.LabelFrame(content, text="Panel Kontrol", padding=15)
        ctrl_frame.pack(fill="x", pady=(0, 20))

        # Row 1: Load Buttons
        row1 = ttk.Frame(ctrl_frame)
        row1.pack(fill="x", pady=5)

        ttk.Button(row1, text="📂 Load Img A", command=self.load_image_a, style="Primary.TButton").pack(side="left",
                                                                                                       padx=(0, 5))
        ttk.Button(row1, text="📂 Load Img B", command=self.load_image_b, style="Soft.TButton").pack(side="left",
                                                                                                    padx=(0, 10))

        # [FITUR TAMBAHAN] Generator untuk Demo
        ttk.Button(row1, text="🧩 Logic Shapes", command=self.generate_logic_shapes, style="Soft.TButton").pack(
            side="left", padx=(0, 5))
        ttk.Button(row1, text="💉 DSA Demo (Subtr.)", command=self.generate_dsa_demo, style="Soft.TButton").pack(
            side="left", padx=(0, 10))

        ttk.Button(row1, text="↺ Reset", command=self.reset_all, style="Danger.TButton").pack(side="left")

        # Row 2: Operation Selection & Params
        row2 = ttk.Frame(ctrl_frame)
        row2.pack(fill="x", pady=(15, 5))

        ttk.Label(row2, text="Operasi:", style="Sub.TLabel").pack(side="left")
        self.op_var = tk.StringVar(value="Subtraction (A - B)")
        ops = [
            "Subtraction (A - B)",
            "Subtraction (Bit Plane Removal)",
            "Averaging Simulation (Noise)",
            "Bitwise AND",
            "Bitwise OR",
            "Bitwise XOR"
        ]
        self.cb_op = ttk.Combobox(row2, textvariable=self.op_var, values=ops, state="readonly", width=35)
        self.cb_op.pack(side="left", padx=(5, 15))
        self.cb_op.bind("<<ComboboxSelected>>", self.on_op_change)

        # Parameter K untuk Averaging
        self.k_frame = ttk.Frame(row2)
        self.k_frame.pack(side="left", padx=10)
        ttk.Label(self.k_frame, text="K (Jumlah Img):", style="Sub.TLabel").pack(side="left")
        self.k_var = tk.IntVar(value=8)
        self.k_entry = ttk.Entry(self.k_frame, textvariable=self.k_var, width=5)
        self.k_entry.pack(side="left", padx=5)
        self.k_frame.pack_forget()

        ttk.Button(row2, text="▶ Jalankan Operasi", command=self.run_operation, style="Primary.TButton").pack(
            side="left", padx=20)

        # --- Image Display Area ---
        img_grid = ttk.Frame(content)
        img_grid.pack(fill="both", expand=True)
        img_grid.columnconfigure(0, weight=1);
        img_grid.columnconfigure(1, weight=1);
        img_grid.columnconfigure(2, weight=1)

        f1 = ttk.Frame(img_grid, style="Card.TFrame")
        f1.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        tk.Label(f1, text="Image A", bg="#F1F5F9", pady=8, font=("Segoe UI", 10, "bold")).pack(fill="x")
        self.lbl_a = tk.Label(f1, bg="#F1F5F9");
        self.lbl_a.pack(fill="both", expand=True)

        f2 = ttk.Frame(img_grid, style="Card.TFrame")
        f2.grid(row=0, column=1, sticky="nsew", padx=5)
        self.lbl_title_b = tk.Label(f2, text="Image B", bg="#F1F5F9", pady=8, font=("Segoe UI", 10, "bold"))
        self.lbl_title_b.pack(fill="x")
        self.lbl_b = tk.Label(f2, bg="#F1F5F9");
        self.lbl_b.pack(fill="both", expand=True)

        f3 = ttk.Frame(img_grid, style="Card.TFrame")
        f3.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        tk.Label(f3, text="Result Image", bg="#F1F5F9", pady=8, font=("Segoe UI", 10, "bold")).pack(fill="x")
        self.lbl_res = tk.Label(f3, bg="#F1F5F9");
        self.lbl_res.pack(fill="both", expand=True)

        self.img_a_cv = None;
        self.img_b_cv = None

    def load_image_a(self):
        self.img_a_cv = self._load_img()
        if self.img_a_cv is not None: self.display_image(self.img_a_cv, self.lbl_a)

    def load_image_b(self):
        self.img_b_cv = self._load_img()
        if self.img_b_cv is not None: self.display_image(self.img_b_cv, self.lbl_b)

    def _load_img(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.tif")])
        if not path: return None
        return cv2.imread(path)

    def generate_logic_shapes(self):
        img_a = np.zeros((300, 300), dtype=np.uint8)
        cv2.rectangle(img_a, (50, 50), (250, 250), 255, -1)
        self.img_a_cv = img_a
        img_b = np.zeros((300, 300), dtype=np.uint8)
        cv2.circle(img_b, (150, 150), 120, 255, -1)
        self.img_b_cv = img_b
        self.display_image(self.img_a_cv, self.lbl_a)
        self.display_image(self.img_b_cv, self.lbl_b)
        self.cb_op.current(3)  # Auto select AND
        self.on_op_change(None)

    def generate_dsa_demo(self):
        # Simulasi DSA: Background Tulang (A) vs Background + Pembuluh (B)
        # Image A (Mask): Background Noise
        img_a = np.ones((300, 300), dtype=np.uint8) * 100
        noise = np.random.normal(0, 10, (300, 300)).astype(np.uint8)
        img_a = cv2.add(img_a, noise)  # Background bertekstur

        # Image B (Live): Background + Object
        img_b = img_a.copy()
        # Tambah "pembuluh darah" (Garis gelap)
        cv2.line(img_b, (50, 50), (150, 150), 50, 5)
        cv2.line(img_b, (150, 150), (250, 50), 50, 5)
        cv2.circle(img_b, (150, 150), 20, 40, -1)

        # Dalam DSA medis: Result = Mask - Live (atau sebaliknya)
        # Disini kita set A = Live, B = Mask agar A-B = Object
        self.img_a_cv = img_b  # Ada objek
        self.img_b_cv = img_a  # Background saja

        self.display_image(self.img_a_cv, self.lbl_a)
        self.display_image(self.img_b_cv, self.lbl_b)
        self.cb_op.current(0)  # Select Subtraction
        messagebox.showinfo("DSA Demo",
                            "Image A: Pembuluh Darah + Background\nImage B: Background Saja\n\nHasil Pengurangan akan mengisolasi pembuluh darah.")

    def reset_all(self):
        self.img_a_cv = None;
        self.img_b_cv = None
        self.lbl_a.config(image="");
        self.lbl_b.config(image="");
        self.lbl_res.config(image="")

    def on_op_change(self, event):
        op = self.op_var.get()
        if "Averaging" in op:
            self.k_frame.pack(side="left", padx=10, after=self.cb_op)
            self.lbl_title_b.config(text="Image B (Sample Noise)")
        elif "Bit Plane" in op:
            self.k_frame.pack_forget()
            self.lbl_title_b.config(text="Image B (4-Bit Zeroed)")
        else:
            self.k_frame.pack_forget()
            self.lbl_title_b.config(text="Image B (Manual/Generated)")

    def display_image(self, cv_img, label_widget):
        if cv_img is None: return
        try:
            if len(cv_img.shape) == 2:
                img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
            else:
                img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)
            pil_img.thumbnail((300, 300), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil_img)
            label_widget.config(image=tk_img);
            label_widget.image = tk_img
        except Exception as e:
            print(f"Error display: {e}")

    def run_operation(self):
        if self.img_a_cv is None:
            messagebox.showwarning("Warning", "Image A must be loaded!")
            return
        op = self.op_var.get()
        if "Averaging" in op: self._run_averaging(); return
        if "Bit Plane" in op: self._run_bit_plane_subtraction(); return
        if self.img_b_cv is None:
            messagebox.showwarning("Warning", "Image B must be loaded!")
            return

        h_a, w_a = self.img_a_cv.shape[:2]
        img_b_resized = cv2.resize(self.img_b_cv, (w_a, h_a))
        res = None
        try:
            if "Subtraction (A - B)" in op:
                # Konversi ke float untuk akurasi pengurangan (bisa negatif)
                a_f = self.img_a_cv.astype(np.float32)
                b_f = img_b_resized.astype(np.float32)
                diff = cv2.absdiff(a_f, b_f)  # Absolute difference
                res = np.clip(diff, 0, 255).astype(np.uint8)

                # Auto contrast stretching agar hasil terlihat jelas
                if len(res.shape) == 2:
                    res = cv2.equalizeHist(res)
                else:
                    ycrcb = cv2.cvtColor(res, cv2.COLOR_BGR2YCrCb)
                    ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
                    res = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

            elif "Bitwise" in op:
                gray_a = cv2.cvtColor(self.img_a_cv, cv2.COLOR_BGR2GRAY) if len(
                    self.img_a_cv.shape) == 3 else self.img_a_cv
                gray_b = cv2.cvtColor(img_b_resized, cv2.COLOR_BGR2GRAY) if len(
                    img_b_resized.shape) == 3 else img_b_resized
                _, bin_a = cv2.threshold(gray_a, 127, 255, cv2.THRESH_BINARY)
                _, bin_b = cv2.threshold(gray_b, 127, 255, cv2.THRESH_BINARY)
                if "AND" in op:
                    res = cv2.bitwise_and(bin_a, bin_b)
                elif "OR" in op:
                    res = cv2.bitwise_or(bin_a, bin_b)
                elif "XOR" in op:
                    res = cv2.bitwise_xor(bin_a, bin_b)

            if res is not None: self.display_image(res, self.lbl_res)
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {e}")

    def _run_bit_plane_subtraction(self):
        mask = 0xF0
        img_b = (self.img_a_cv & mask).astype(np.uint8)
        self.display_image(img_b, self.lbl_b)
        diff = cv2.absdiff(self.img_a_cv, img_b)
        # Contrast stretch
        if len(diff.shape) == 3:
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            res_eq = cv2.equalizeHist(diff_gray)
        else:
            res_eq = cv2.equalizeHist(diff)
        self.display_image(res_eq, self.lbl_res)

    def _run_averaging(self):
        img_clean = self.img_a_cv.astype(np.float32)
        K = self.k_var.get();
        if K < 1: K = 1
        accumulator = np.zeros_like(img_clean)
        sample_noisy = None
        for i in range(K):
            gauss = np.random.normal(0, 64, img_clean.shape).astype(np.float32)
            noisy = img_clean + gauss
            accumulator += noisy
            if i == 0: sample_noisy = np.clip(noisy, 0, 255).astype(np.uint8)
        avg_img = np.clip(accumulator / K, 0, 255).astype(np.uint8)
        self.display_image(sample_noisy, self.lbl_b)
        self.display_image(avg_img, self.lbl_res)