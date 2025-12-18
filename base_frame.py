import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
from styles import COLORS, FONTS

class BaseFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        self.grid(row=0, column=0, sticky="nsew")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # --- SCROLLABLE CONTAINER ---
        self.main_scroll_canvas = tk.Canvas(self, bg=COLORS["bg_main"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.main_scroll_canvas.yview)

        self.main_scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.main_scroll_canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.scrollable_content = ttk.Frame(self.main_scroll_canvas, style="Main.TFrame")

        self.canvas_window = self.main_scroll_canvas.create_window(
            (0, 0), window=self.scrollable_content, anchor="nw"
        )

        self.scrollable_content.bind("<Configure>", self._on_frame_configure)
        self.main_scroll_canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind_all("<MouseWheel>", self._on_mousewheel)

        self.scrollable_content.columnconfigure(0, weight=1)
        self.scrollable_content.columnconfigure(1, weight=30)
        self.scrollable_content.columnconfigure(2, weight=1)
        self.scrollable_content.rowconfigure(0, weight=0)
        self.scrollable_content.rowconfigure(1, weight=1)

        # Container Utama (Kartu)
        self.card = ttk.Frame(self.scrollable_content, style="Card.TFrame")
        self.card.grid(row=1, column=1, sticky="nsew", pady=10, padx=5)
        self.card.columnconfigure(0, weight=1)
        self.card.rowconfigure(1, weight=1)

    def _on_frame_configure(self, event=None):
        self.main_scroll_canvas.configure(scrollregion=self.main_scroll_canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        canvas_width = event.width
        self.main_scroll_canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _on_mousewheel(self, event):
        if self.main_scroll_canvas.winfo_height() < self.scrollable_content.winfo_height():
            self.main_scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_header(self, title, subtitle):
        header_frame = ttk.Frame(self.card, style="Card.TFrame")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        lbl_title = ttk.Label(header_frame, text=title, style="H1.TLabel")
        lbl_title.pack(anchor="w")

        lbl_sub = ttk.Label(header_frame, text=subtitle, style="Body.TLabel")
        lbl_sub.pack(anchor="w", pady=(2, 0))

        accent_line = tk.Frame(header_frame, bg=COLORS["active_indicator"], height=3, width=60)
        accent_line.pack(anchor="w", pady=(10, 0))

        sep = tk.Frame(header_frame, bg=COLORS["border"], height=1)
        sep.pack(fill="x", pady=(15, 0))

        content_frame = ttk.Frame(self.card, style="Card.TFrame")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(5, 20))
        return content_frame

    # --- [BARU] FUNGSI GLOBAL UNTUK SAVE GAMBAR ---
    def save_image_cv(self, img_cv, filename_prefix="result"):
        if img_cv is None:
            messagebox.showwarning("Peringatan", "Tidak ada gambar hasil untuk disimpan.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=f"{filename_prefix}.png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("Bitmap", "*.bmp")]
        )

        if file_path:
            try:
                # OpenCV menyimpan dalam BGR, pastikan input sudah BGR atau Grayscale
                cv2.imwrite(file_path, img_cv)
                messagebox.showinfo("Berhasil", f"Gambar berhasil disimpan ke:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyimpan gambar:\n{e}")