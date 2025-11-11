import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2


class ImageViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Program 1 - Image Viewer")
        self.root.geometry("800x600")

        header_frame = tk.Frame(root)
        header_frame.pack(fill="x", pady=5)

        btn_open = tk.Button(header_frame, text="Buka Gambar", command=self.open_image)
        btn_open.pack(side="left", padx=10, pady=5)

        nim_label = tk.Label(header_frame, text="14240032",
                             font=("Arial", 14, "bold"))
        nim_label.pack(side="left", padx=20)

        nama_label = tk.Label(header_frame, text="Riki Daniel Tanebeth",
                              font=("Arial", 14, "bold"))
        nama_label.pack(side="left", padx=20)

        self.canvas = tk.Label(root, bg="white")
        self.canvas.pack(expand=True, fill="both", padx=10, pady=10)

        frame_btn = tk.Frame(root)
        frame_btn.pack(pady=10)

        btn_gray = tk.Button(frame_btn, text="Tampilkan Grayscale", command=self.show_gray, width=18)
        btn_gray.grid(row=0, column=0, padx=5, pady=5)

        btn_color = tk.Button(frame_btn, text="Tampilkan Berwarna", command=self.show_color, width=18)
        btn_color.grid(row=0, column=1, padx=5, pady=5)

        # HAPUS tombol Keluar yang sebelumnya ada di sini

        self.img_rgb = None
        self.img_gray = None
        self.tk_img = None

    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff")]
        )
        if not path:
            return

        img = cv2.imread(path)
        if img is None:
            messagebox.showerror("Error", "Gagal membuka gambar.")
            return

        self.img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        self.show_on_canvas(self.img_rgb)

    def show_gray(self):
        if self.img_gray is None:
            messagebox.showwarning("Peringatan", "Silakan buka gambar terlebih dahulu.")
            return
        self.show_on_canvas(self.img_gray, is_gray=True)

    def show_color(self):
        if self.img_rgb is None:
            messagebox.showwarning("Peringatan", "Silakan buka gambar terlebih dahulu.")
            return
        self.show_on_canvas(self.img_rgb)

    def show_on_canvas(self, img, is_gray=False):
        # Konversi NumPy array ke PIL Image
        pil_img = Image.fromarray(img)
        pil_img = pil_img.resize((600, 400), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(pil_img)
        self.canvas.config(image=self.tk_img)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewerApp(root)
    root.mainloop()
