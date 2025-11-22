import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import cv2
from PIL import Image, ImageTk


class FrequencyFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Program 5 - Filter Domain Frekuensi")
        self.root.geometry("1000x650")

        self.original_img = None       # gambar warna (PIL)
        self.gray_img = None           # numpy grayscale
        self.filtered_img = None       # hasil filter (PIL)
        self.original_tk = None
        self.filtered_tk = None

        self._build_ui()

    # ===================== UI =====================

    def _build_ui(self):
        # -------- Header (NIM + Nama) --------
        header = tk.Frame(self.root)
        header.pack(fill="x", pady=5)

        tk.Label(
            header,
            text="Program 5 - Filter Domain Frekuensi",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=10)

        tk.Label(
            header,
            text="14240032 - Riki Daniel Tanebeth",
            font=("Arial", 11, "bold")
        ).pack(side="right", padx=10)

        # -------- Frame atas: tombol buka/reset --------
        top = tk.Frame(self.root)
        top.pack(side="top", fill="x", padx=10, pady=5)

        btn_open = tk.Button(
            top, text="Buka Gambar",
            command=self.open_image
        )
        btn_open.pack(side="left", padx=5)

        btn_reset = tk.Button(
            top, text="Reset Gambar",
            command=self.reset_image
        )
        btn_reset.pack(side="left", padx=5)

        # Separator
        sep = ttk.Separator(self.root, orient="horizontal")
        sep.pack(fill="x", padx=10, pady=5)

        # -------- Frame kontrol filter --------
        ctrl = tk.LabelFrame(self.root, text="Pengaturan Filter", padx=10, pady=5)
        ctrl.pack(side="top", fill="x", padx=10, pady=5)

        # Jenis filter: Ideal / Butterworth / Gaussian
        tk.Label(ctrl, text="Jenis filter:").grid(row=0, column=0, sticky="w")
        self.filter_type_var = tk.StringVar(value="Ideal")
        cb_filter = ttk.Combobox(
            ctrl,
            textvariable=self.filter_type_var,
            values=["Ideal", "Butterworth", "Gaussian"],
            state="readonly",
            width=15
        )
        cb_filter.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        # Lowpass / Highpass
        tk.Label(ctrl, text="Tipe frekuensi:").grid(row=1, column=0, sticky="w")
        self.pass_type_var = tk.StringVar(value="Lowpass")
        rb_lp = tk.Radiobutton(ctrl, text="Lowpass", variable=self.pass_type_var, value="Lowpass")
        rb_hp = tk.Radiobutton(ctrl, text="Highpass", variable=self.pass_type_var, value="Highpass")
        rb_lp.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        rb_hp.grid(row=1, column=2, sticky="w", padx=5, pady=2)

        # Cutoff frekuensi (D0)
        tk.Label(ctrl, text="Cutoff (D0):").grid(row=2, column=0, sticky="w")
        self.d0_var = tk.DoubleVar(value=40.0)
        ent_d0 = tk.Entry(ctrl, textvariable=self.d0_var, width=10)
        ent_d0.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        # Orde Butterworth (n)
        tk.Label(ctrl, text="Orde Butterworth (n):").grid(row=3, column=0, sticky="w")
        self.n_var = tk.IntVar(value=2)
        ent_n = tk.Entry(ctrl, textvariable=self.n_var, width=10)
        ent_n.grid(row=3, column=1, sticky="w", padx=5, pady=2)

        # Tombol terapkan filter
        btn_apply = tk.Button(
            ctrl,
            text="Terapkan Filter",
            command=self.apply_filter
        )
        btn_apply.grid(row=0, column=3, rowspan=2, padx=20, pady=5, sticky="ns")

        # Pesan bantu
        note = tk.Label(
            ctrl,
            text=(
                "Catatan:\n"
                "- Nilai n hanya dipakai untuk Butterworth.\n"
                "- Pilih Lowpass / Highpass untuk 6 jenis filter:\n"
                "  Ideal, Butterworth, Gaussian."
            ),
            fg="gray",
            justify="left"
        )
        note.grid(row=2, column=2, columnspan=2, sticky="w", padx=5, pady=2)

        # -------- Frame gambar (kiri = asli, kanan = hasil) --------
        img_frame = tk.Frame(self.root)
        img_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left = tk.Frame(img_frame)
        left.pack(side="left", fill="both", expand=True, padx=5)

        right = tk.Frame(img_frame)
        right.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(left, text="Gambar Asli").pack()
        self.lbl_original = tk.Label(left, bg="black")
        self.lbl_original.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Label(right, text="Hasil Filter").pack()
        self.lbl_filtered = tk.Label(right, bg="black")
        self.lbl_filtered.pack(fill="both", expand=True, padx=5, pady=5)

    # ===================== Fungsi Utilitas =====================

    def open_image(self):
        path = filedialog.askopenfilename(
            title="Pilih gambar",
            filetypes=[("File gambar", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff")]
        )
        if not path:
            return

        try:
            # Baca dengan OpenCV, konversi ke RGB
            img_bgr = cv2.imread(path)
            if img_bgr is None:
                raise ValueError("Gagal membuka gambar.")

            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

            # Simpan grayscale untuk proses DFT
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)

            # Resize agar tidak terlalu besar (opsional)
            max_size = 512
            h, w = gray.shape
            scale = min(max_size / h, max_size / w, 1.0)
            if scale != 1.0:
                new_w = int(w * scale)
                new_h = int(h * scale)
                gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_AREA)
                img_rgb = cv2.resize(img_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)

            self.gray_img = gray
            self.original_img = Image.fromarray(img_rgb)
            self.filtered_img = None

            self._show_original()
            self._clear_filtered()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reset_image(self):
        if self.original_img is None:
            return
        self.filtered_img = None
        self._show_original()
        self._clear_filtered()

    def _show_original(self):
        if self.original_img is None:
            return
        img = self.original_img.copy()
        self.original_tk = ImageTk.PhotoImage(img)
        self.lbl_original.configure(image=self.original_tk)

    def _show_filtered(self):
        if self.filtered_img is None:
            return
        img = self.filtered_img.copy()
        self.filtered_tk = ImageTk.PhotoImage(img)
        self.lbl_filtered.configure(image=self.filtered_tk)

    def _clear_filtered(self):
        self.lbl_filtered.configure(image="", text="")

    # ===================== Proses Filter Frekuensi =====================

    def apply_filter(self):
        if self.gray_img is None:
            messagebox.showwarning("Peringatan", "Silakan buka gambar terlebih dahulu.")
            return

        try:
            d0 = float(self.d0_var.get())
            if d0 <= 0:
                raise ValueError("Cutoff (D0) harus > 0")
        except Exception:
            messagebox.showerror("Error", "Nilai cutoff (D0) tidak valid.")
            return

        filter_type = self.filter_type_var.get()
        pass_type = self.pass_type_var.get()
        try:
            n = int(self.n_var.get())
        except Exception:
            n = 1
        n = max(1, n)  # minimal 1

        # Normalisasi [0,1]
        img = self.gray_img.copy()
        img_norm = img / 255.0

        # DFT 2D + shift ke tengah
        F = np.fft.fft2(img_norm)
        F_shift = np.fft.fftshift(F)

        # Buat filter H(u,v)
        H = self._create_filter(img.shape, d0, filter_type, pass_type, n)

        # Terapkan filter
        G_shift = F_shift * H

        # Kembali ke ruang spasial
        G = np.fft.ifft2(np.fft.ifftshift(G_shift))
        g = np.abs(G)

        # Normalisasi hasil ke [0,255]
        g_min, g_max = g.min(), g.max()
        g_norm = (g - g_min) / (g_max - g_min + 1e-8)
        g_uint8 = (g_norm * 255).astype(np.uint8)

        # Simpan sebagai gambar PIL (grayscale -> mode "L")
        self.filtered_img = Image.fromarray(g_uint8, mode="L")
        self._show_filtered()

    def _create_filter(self, shape, d0, filter_type, pass_type, n):
        rows, cols = shape
        crow, ccol = rows // 2, cols // 2

        # Matriks jarak D(u,v) dari pusat
        u = np.arange(rows)
        v = np.arange(cols)
        V, U = np.meshgrid(v, u)
        D = np.sqrt((U - crow) ** 2 + (V - ccol) ** 2)

        filter_type = filter_type.lower()
        pass_type = pass_type.lower()

        # ---------- Lowpass dasar ----------
        if filter_type == "ideal":
            # Ideal Lowpass
            H = (D <= d0).astype(np.float32)

        elif filter_type == "butterworth":
            # Butterworth Lowpass
            H = 1.0 / (1.0 + (D / (d0 + 1e-8)) ** (2 * n))

        elif filter_type == "gaussian":
            # Gaussian Lowpass
            H = np.exp(-(D ** 2) / (2 * (d0 ** 2 + 1e-8)))
        else:
            # default Ideal kalau salah input
            H = (D <= d0).astype(np.float32)

        # ---------- Ubah ke Highpass jika diminta ----------
        if pass_type == "highpass":
            H = 1.0 - H

        return H.astype(np.float32)


if __name__ == "__main__":
    root = tk.Tk()
    app = FrequencyFilterApp(root)
    root.mainloop()
