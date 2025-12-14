import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
from base_frame import BaseFrame

class SpatialSegmentationApp(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # --- UI Initialization ---
        content = self.create_header("Spatial & Segmentation", "Smoothing, Sharpening, and Line Detection")
        
        # --- Control Panel ---
        ctrl_frame = ttk.LabelFrame(content, text="Panel Kontrol", padding=15)
        ctrl_frame.pack(fill="x", pady=(0, 20))
        
        # Row 1: Image Controls
        row1 = ttk.Frame(ctrl_frame)
        row1.pack(fill="x", pady=5)
        ttk.Button(row1, text="📂 Buka Gambar", command=self.open_image, style="Primary.TButton").pack(side="left", padx=(0, 15))
        ttk.Button(row1, text="↺ Reset", command=self.reset_image, style="Danger.TButton").pack(side="left")

        # Row 2: Filter Controls
        row2 = ttk.Frame(ctrl_frame)
        row2.pack(fill="x", pady=(20, 5))
        
        # Operation Category
        ttk.Label(row2, text="Kategori Operasi:", style="Sub.TLabel").pack(side="left")
        self.category_var = tk.StringVar(value="Smoothing")
        self.cb_category = ttk.Combobox(row2, textvariable=self.category_var, state="readonly", width=15)
        self.cb_category['values'] = ["Smoothing", "Sharpening", "Segmentation"]
        self.cb_category.pack(side="left", padx=(5, 15))
        self.cb_category.bind("<<ComboboxSelected>>", self.update_filter_types)
        
        # Filter Type
        ttk.Label(row2, text="Jenis Filter:", style="Sub.TLabel").pack(side="left")
        self.filter_var = tk.StringVar()
        self.cb_filter = ttk.Combobox(row2, textvariable=self.filter_var, state="readonly", width=25)
        self.cb_filter.pack(side="left", padx=(5, 15))
        
        # Apply Button
        ttk.Button(row2, text="▶ Apply", command=self.apply_filter, style="Soft.TButton").pack(side="left", padx=20)
        
        # --- Image Display Area ---
        img_grid = ttk.Frame(content)
        img_grid.pack(fill="both", expand=True)
        img_grid.columnconfigure(0, weight=1)
        img_grid.columnconfigure(1, weight=1)
        
        # Left: Original
        f_left = ttk.Frame(img_grid, style="Card.TFrame")
        f_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(f_left, text="Original Image", bg="#F1F5F9", pady=8, font=("Segoe UI", 10, "bold")).pack(fill="x")
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
        self.processed_img_cv = None
        
        # Initialize filter options
        self.update_filter_types()

    def update_filter_types(self, event=None):
        category = self.category_var.get()
        if category == "Smoothing":
            options = ["Averaging 3x3", "Averaging 5x5", "Averaging 7x7", "Averaging 9x9", "Averaging 15x15", "Averaging 35x35", "Median 3x3", "Median 5x5"]
        elif category == "Sharpening":
            options = ["Laplacian", "Sobel Gradient"]
        elif category == "Segmentation":
            options = ["Point Detection", "Line: Horizontal", "Line: Vertical", "Line: +45 Degree", "Line: -45 Degree"]
        else:
            options = []
            
        self.cb_filter['values'] = options
        if options:
            self.cb_filter.current(0)

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])
        if not path:
            return
            
        # Read image using OpenCV
        img = cv2.imread(path)
        if img is None:
            messagebox.showerror("Error", "Gagal memuat gambar.")
            return
            
        self.original_img_cv = img
        self.display_image(self.original_img_cv, self.lbl_original)
        self.reset_image()

    def reset_image(self):
        self.processed_img_cv = None
        self.lbl_result.config(image="")
        self.lbl_result.image = None

    def display_image(self, cv_img, label_widget):
        if cv_img is None:
            return
            
        try:
            # Convert BGR (OpenCV) to RGB (PIL)
            # Check if grayscale
            if len(cv_img.shape) == 2:
                img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
            else:
                img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                
            pil_img = Image.fromarray(img_rgb)
            
            # Resize for display (Preserve aspect ratio roughly or fixed width)
            # Using fixed size similar to frequency_filters.py logic for consistency
            display_size = (400, 400)
            pil_img.thumbnail(display_size, Image.LANCZOS)
            
            tk_img = ImageTk.PhotoImage(pil_img)
            label_widget.config(image=tk_img)
            label_widget.image = tk_img # Keep reference
        except Exception as e:
            print(f"Error displaying image: {e}")

    def apply_filter(self):
        if self.original_img_cv is None:
            messagebox.showwarning("Peringatan", "Silakan buka gambar terlebih dahulu.")
            return

        category = self.category_var.get()
        filter_type = self.filter_var.get()
        
        # Ensure we work on a copy
        img_src = self.original_img_cv.copy()
        
        # Automatic grayscale conversion for Segmentation and Laplacian
        needs_grayscale = category == "Segmentation" or (category == "Sharpening" and "Laplacian" in filter_type)
        if needs_grayscale and len(img_src.shape) == 3:
            img_src = cv2.cvtColor(img_src, cv2.COLOR_BGR2GRAY)

        result = None

        try:
            # --- SMOOTHING ---
            if category == "Smoothing":
                if "Averaging" in filter_type:
                    # Extract k from "Averaging KxK"
                    k_str = filter_type.split()[1] # "3x3"
                    k = int(k_str.split('x')[0])
                    result = cv2.blur(img_src, (k, k))
                elif "Median" in filter_type:
                    k = int(filter_type.split()[1][0]) # Extract 3 or 5
                    result = cv2.medianBlur(img_src, k)
                    
            # --- SHARPENING ---
            elif category == "Sharpening":
                if "Laplacian" in filter_type:
                    # Using cv2.Laplacian or custom kernel. 
                    result = cv2.Laplacian(img_src, cv2.CV_64F)
                    result = cv2.convertScaleAbs(result) 
                
                elif "Sobel Gradient" in filter_type:
                    grad_x = cv2.Sobel(img_src, cv2.CV_64F, 1, 0, ksize=3)
                    grad_y = cv2.Sobel(img_src, cv2.CV_64F, 0, 1, ksize=3)
                    abs_grad_x = cv2.convertScaleAbs(grad_x)
                    abs_grad_y = cv2.convertScaleAbs(grad_y)
                    # Approx Magnitude = 0.5*|dx| + 0.5*|dy|, or proper magnitude
                    # PDF usually implies magnitude = sqrt(dx^2 + dy^2) or sum of abs
                    # Using cv2.magnitude for correctness
                    mag = cv2.magnitude(grad_x, grad_y)
                    result = cv2.convertScaleAbs(mag)
                    
            # --- SEGMENTATION ---
            elif category == "Segmentation":
                kernel = None
                
                if filter_type == "Point Detection":
                    kernel = np.array([[-1, -1, -1], 
                                       [-1,  8, -1], 
                                       [-1, -1, -1]])
                
                elif filter_type == "Line: Horizontal":
                    kernel = np.array([[-1, -1, -1], 
                                       [ 2,  2,  2], 
                                       [-1, -1, -1]])
                                       
                elif filter_type == "Line: Vertical":
                    kernel = np.array([[-1,  2, -1], 
                                       [-1,  2, -1], 
                                       [-1,  2, -1]])
                                       
                elif filter_type == "Line: +45 Degree":
                    kernel = np.array([[-1, -1,  2], 
                                       [-1,  2, -1], 
                                       [ 2, -1, -1]])
                                       
                elif filter_type == "Line: -45 Degree":
                    kernel = np.array([[ 2, -1, -1], 
                                       [-1,  2, -1], 
                                       [-1, -1,  2]])
                
                if kernel is not None:
                    # Apply kernel using filter2D
                    # Use CV_64F to handle negative values, then take absolute
                    processed = cv2.filter2D(img_src, cv2.CV_64F, kernel)
                    result = cv2.convertScaleAbs(processed)

            self.processed_img_cv = result
            self.display_image(self.processed_img_cv, self.lbl_result)
            
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan saat pemrosesan: {e}")
            print(e)
