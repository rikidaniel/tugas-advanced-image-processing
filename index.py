import tkinter as tk

from image_view import ImageViewerApp
from mach_and_band_effect import MachBandApp
from program3_single_pixel import SinglePixelApp
from dft_explorer import DftApp  # <-- DITAMBAHKAN


class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard - Pemilihan Program")
        self.root.geometry("500x400")

        # Header
        header = tk.Frame(root)
        header.pack(fill="x", pady=12)

        tk.Label(
            header,
            text="Pilih Program",
            font=("Arial", 16, "bold")
        ).pack()

        content = tk.Frame(root)
        content.pack(expand=True, fill="both", padx=20, pady=10)

        btn1 = tk.Button(
            content,
            text="Buka Program 1 - Image Viewer",
            width=35,
            command=self.open_program1
        )
        btn1.pack(pady=8)

        btn2 = tk.Button(
            content,
            text="Buka Program 2 - Mach Band Effect",
            width=35,
            command=self.open_program2
        )
        btn2.pack(pady=8)

        btn3 = tk.Button(
            content,
            text="Buka Program 3 - Image enhancement",
            width=35,
            command=self.open_program3
        )
        btn3.pack(pady=8)

        btn4 = tk.Button(
            content,
            text="Buka Program 4 - Transformasi Fourier 2D",
            width=35,
            command=self.open_program4  # <-- DIPERBAIKI
        )
        btn4.pack(pady=8)

        footer = tk.Frame(root)
        footer.pack(fill="x", pady=6)
        tk.Label(footer, text="14240032  •  Riki Daniel Tanebeth", font=("Arial", 10, "bold")).pack()

        btn_exit = tk.Button(root, text="Keluar", width=20, command=root.quit)
        btn_exit.pack(pady=8)

        self.center_window(self.root)

    def center_window(self, win):
        win.update_idletasks()
        w = win.winfo_width()
        h = win.winfo_height()
        ws = win.winfo_screenwidth()
        hs = win.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")

    def open_program1(self):
        top = tk.Toplevel(self.root)
        top.title("Program 1 - Image Viewer")
        top.geometry("800x600")
        ImageViewerApp(top)

    def open_program2(self):
        top = tk.Toplevel(self.root)
        top.title("Program 2 - Mach Band Effect")
        top.geometry("800x750")
        MachBandApp(top)

    def open_program3(self):
        top = tk.Toplevel(self.root)
        top.title("Program 3 - Image enhancement")
        top.geometry("1000x680")
        SinglePixelApp(top)

    # FUNGSI BARU DITAMBAHKAN
    def open_program4(self):
        top = tk.Toplevel(self.root)
        # Title dan geometry akan diatur oleh DftApp
        DftApp(top)


if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()