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
        
        # --- UI Initialization ---
        content = self.create_header("Arithmetic & Logic", "Operasi Aritmatika (Sub/Avg) dan Logika (AND/OR/XOR)")
        
        # --- Control Panel ---
        ctrl_frame = ttk.LabelFrame(content, text="Panel Kontrol", padding=15)
        ctrl_frame.pack(fill="x", pady=(0, 20))
        
        # Row 1: Load Buttons
        row1 = ttk.Frame(ctrl_frame)
        row1.pack(fill="x", pady=5)
        
        ttk.Button(row1, text="📂 Load Image A", command=self.load_image_a, style="Primary.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(row1, text="📂 Load Image B", command=self.load_image_b, style="Soft.TButton").pack(side="left", padx=(0, 20))
        ttk.Button(row1, text="↺ Reset All", command=self.reset_all, style="Danger.TButton").pack(side="left")

        # Row 2: Operation Selection
        row2 = ttk.Frame(ctrl_frame)
        row2.pack(fill="x", pady=(15, 5))
        
        ttk.Label(row2, text="Operasi:", style="Sub.TLabel").pack(side="left")
        self.op_var = tk.StringVar(value="Subtraction (A - B)")
        ops = [
            "Subtraction (A - B)",
            "Averaging Simulation (Noise)",
            "Bitwise AND",
            "Bitwise OR",
            "Bitwise XOR"
        ]
        self.cb_op = ttk.Combobox(row2, textvariable=self.op_var, values=ops, state="readonly", width=30)
        self.cb_op.pack(side="left", padx=(5, 15))
        self.cb_op.bind("<<ComboboxSelected>>", self.on_op_change)
        
        ttk.Button(row2, text="▶ Jalankan Operasi", command=self.run_operation, style="Primary.TButton").pack(side="left")
        
        # --- Image Display Area (3 Columns) ---
        img_grid = ttk.Frame(content)
        img_grid.pack(fill="both", expand=True)
        img_grid.columnconfigure(0, weight=1)
        img_grid.columnconfigure(1, weight=1)
        img_grid.columnconfigure(2, weight=1)
        
        # Col 1: Image A
        f1 = ttk.Frame(img_grid, style="Card.TFrame")
        f1.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        tk.Label(f1, text="Image A", bg="#F1F5F9", pady=8, font=("Segoe UI", 10, "bold")).pack(fill="x")
        self.lbl_a = tk.Label(f1, bg="#F1F5F9")
        self.lbl_a.pack(fill="both", expand=True)
        
        # Col 2: Image B
        f2 = ttk.Frame(img_grid, style="Card.TFrame")
        f2.grid(row=0, column=1, sticky="nsew", padx=5)
        tk.Label(f2, text="Image B (or Noise)", bg="#F1F5F9", pady=8, font=("Segoe UI", 10, "bold")).pack(fill="x")
        self.lbl_b = tk.Label(f2, bg="#F1F5F9")
        self.lbl_b.pack(fill="both", expand=True)
        
        # Col 3: Result
        f3 = ttk.Frame(img_grid, style="Card.TFrame")
        f3.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        tk.Label(f3, text="Result Image", bg="#F1F5F9", pady=8, font=("Segoe UI", 10, "bold")).pack(fill="x")
        self.lbl_res = tk.Label(f3, bg="#F1F5F9")
        self.lbl_res.pack(fill="both", expand=True)
        
        # --- State ---
        self.img_a_cv = None
        self.img_b_cv = None
        
    def load_image_a(self):
        self.img_a_cv = self._load_img()
        if self.img_a_cv is not None:
            self.display_image(self.img_a_cv, self.lbl_a)
            
    def load_image_b(self):
        self.img_b_cv = self._load_img()
        if self.img_b_cv is not None:
            self.display_image(self.img_b_cv, self.lbl_b)

    def _load_img(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])
        if not path: return None
        img = cv2.imread(path)
        # Resize to standard size for consistency if needed, but let's keep flexible.
        # However, for 3 columns, smaller preview usually needed.
        return img
        
    def reset_all(self):
        self.img_a_cv = None
        self.img_b_cv = None
        self.lbl_a.config(image="")
        self.lbl_b.config(image="")
        self.lbl_res.config(image="")
        
    def on_op_change(self, event):
        op = self.op_var.get()
        if "Averaging" in op:
            messagebox.showinfo("Info", "Mode Averaging: Image B will be automatically generated as a noisy version of Image A.")
            
    def display_image(self, cv_img, label_widget):
        if cv_img is None: return
        try:
            h, w = cv_img.shape[:2]
            # Convert
            if len(cv_img.shape) == 2:
                img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
            else:
                img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            
            pil_img = Image.fromarray(img_rgb)
            pil_img.thumbnail((300, 300), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil_img)
            label_widget.config(image=tk_img)
            label_widget.image = tk_img
        except Exception as e:
            print(f"Error display: {e}")

    def run_operation(self):
        if self.img_a_cv is None:
            messagebox.showwarning("Warning", "Image A must be loaded!")
            return

        op = self.op_var.get()
        
        # Special Logic for Averaging (Auto-generate B)
        if "Averaging" in op:
            self._run_averaging()
            return

        # For other ops, we need Image B
        if self.img_b_cv is None:
            messagebox.showwarning("Warning", "Image B must be loaded for this operation!")
            return

        # Resize B to match A
        h_a, w_a = self.img_a_cv.shape[:2]
        img_b_resized = cv2.resize(self.img_b_cv, (w_a, h_a))
        
        # Prepare inputs based on Op
        res = None
        
        try:
            if "Subtraction" in op:
                # Color subtraction is fine
                res = cv2.absdiff(self.img_a_cv, img_b_resized)
                
            elif "Bitwise" in op:
                # Convert to Grayscale -> Binary threshold 
                gray_a = cv2.cvtColor(self.img_a_cv, cv2.COLOR_BGR2GRAY) if len(self.img_a_cv.shape) == 3 else self.img_a_cv
                gray_b = cv2.cvtColor(img_b_resized, cv2.COLOR_BGR2GRAY) if len(img_b_resized.shape) == 3 else img_b_resized
                
                _, bin_a = cv2.threshold(gray_a, 127, 255, cv2.THRESH_BINARY)
                _, bin_b = cv2.threshold(gray_b, 127, 255, cv2.THRESH_BINARY)
                
                # Update displays to show the binary versions being used? 
                # Maybe better to keep original input visible, but user expects result based on logic.
                # Let's show result as binary.
                
                if "AND" in op:
                    res = cv2.bitwise_and(bin_a, bin_b)
                elif "OR" in op:
                    res = cv2.bitwise_or(bin_a, bin_b)
                elif "XOR" in op:
                    res = cv2.bitwise_xor(bin_a, bin_b)
            
            if res is not None:
                self.display_image(res, self.lbl_res)
                
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {e}")

    def _run_averaging(self):
        # 1. Create Noisy Version of A
        img_a = self.img_a_cv
        
        # Generate Gaussian noise
        mean = 0
        sigma = 50 # Amount of noise
        gauss = np.random.normal(mean, sigma, img_a.shape).astype(np.float32)
        
        noisy_float = img_a.astype(np.float32) + gauss
        noisy_img = np.clip(noisy_float, 0, 255).astype(np.uint8)
        
        # Show Noisy in Slot B
        self.display_image(noisy_img, self.lbl_b)
        
        # 2. Average (A + Noisy) / 2
        # Simulation: In real world we avg many images. 
        # Here we just show that Avg(Original, Noisy) reduces the noise compared to Noisy alone.
        # Wait, usually we average multiple *Noisy* images to get clearer image.
        # Averaging Original + Noisy is cheating :)
        # Correct Simulation: Create 2 different noisy versions of A and average them.
        
        gauss2 = np.random.normal(0, 50, img_a.shape).astype(np.float32)
        noisy2_float = img_a.astype(np.float32) + gauss2
        
        # Let's Avg 10 noisy images? Too slow?
        # Let's keep it simple: Average 2 independent noisy images.
        avg_float = (noisy_float + noisy2_float) / 2.0
        res = np.clip(avg_float, 0, 255).astype(np.uint8)
        
        self.display_image(res, self.lbl_res)
