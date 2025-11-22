import tkinter as tk
from tkinter import ttk

# --- PALET WARNA EARTHY & NYAMAN ---
COLORS = {
    # --- SIDEBAR & NAVIGASI (Sage Green Gelap) ---
    "sidebar_bg": "#3A4D3F",  # Hijau Sage Tua (Lebih kalem dari sebelumnya)
    "sidebar_fg": "#E8EDDF",  # Putih Tulang (Teks Sidebar)
    "active_bg": "#4F6D54",  # Hijau Sage Sedang (Menu Aktif - Soft)
    "active_fg": "#FFFFFF",  # Putih Bersih (Teks Menu Aktif)

    # --- AREA KONTEN (Cream & Putih Hangat) ---
    "bg_main": "#F5F7F0",  # Krem Sangat Muda (Background Utama - Hangat)
    "bg_card": "#FFFFFF",  # Putih Bersih (Area Kartu)

    # --- TOMBOL UTAMA (Accent Sage Cerah) ---
    "primary": "#73A580",  # Hijau Sage Cerah (Tombol Utama - Menenangkan)
    "primary_hover": "#5E8C6A",  # Hijau Sage Sedikit Gelap (Hover)
    "primary_fg": "#FFFFFF",  # Teks Putih

    # --- TOMBOL SEKUNDER (Soft Cream) ---
    "secondary": "#E8EDDF",  # Krem Kehijauan (Tombol Soft)
    "secondary_fg": "#3A4D3F",  # Teks Hijau Tua

    # --- LAIN-LAIN ---
    "danger": "#D64045",  # Merah Bata (Tombol Reset - Tidak terlalu mencolok)
    "danger_fg": "#FFFFFF",

    "text_header": "#2C3E32",  # Hijau Arang Tua (Judul - Kontras tapi lembut)
    "text_body": "#4A5552",  # Abu-abu Kehijauan (Isi Teks - Mudah dibaca)
    "border": "#CFD8CC"  # Hijau Abu Muda (Garis Batas Halus)
}

FONTS = {
    "h1": ("Segoe UI", 22, "bold"),
    "h2": ("Segoe UI", 16, "bold"),
    "body": ("Segoe UI", 11),
    "small": ("Segoe UI", 9),
    "btn": ("Segoe UI", 10, "bold")
}


def apply_theme(root):
    style = ttk.Style(root)
    style.theme_use('clam')

    # --- KONFIGURASI FRAME ---
    style.configure("Main.TFrame", background=COLORS["bg_main"])
    style.configure("Card.TFrame", background=COLORS["bg_card"])
    style.configure("Sidebar.TFrame", background=COLORS["sidebar_bg"])

    # --- KONFIGURASI LABEL ---
    style.configure("H1.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_header"], font=FONTS["h1"])
    style.configure("H2.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_header"], font=FONTS["h2"])
    style.configure("Body.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_body"], font=FONTS["body"])
    style.configure("Sub.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_body"], font=FONTS["small"])

    # --- TOMBOL UTAMA (Accent) ---
    style.configure("Primary.TButton",
                    font=FONTS["btn"],
                    background=COLORS["primary"],
                    foreground=COLORS["primary_fg"],
                    borderwidth=0,
                    focuscolor="none",
                    padding=(15, 10))
    style.map("Primary.TButton",
              background=[("active", COLORS["primary_hover"]), ("pressed", COLORS["sidebar_bg"])])

    # --- TOMBOL SEKUNDER (Soft) ---
    style.configure("Soft.TButton",
                    font=FONTS["btn"],
                    background=COLORS["secondary"],
                    foreground=COLORS["secondary_fg"],
                    borderwidth=0,
                    focuscolor="none",
                    padding=(15, 10))
    style.map("Soft.TButton",
              background=[("active", "#D0D6CB")])  # Hover slightly darker cream

    # --- TOMBOL DANGER ---
    style.configure("Danger.TButton",
                    font=FONTS["btn"],
                    background=COLORS["danger"],
                    foreground=COLORS["danger_fg"],
                    borderwidth=0,
                    focuscolor="none",
                    padding=(15, 10))
    style.map("Danger.TButton",
              background=[("active", "#B53337")])  # Hover darker red

    # --- INPUT WIDGETS ---
    # Memberikan sedikit warna latar belakang pada input agar menyatu
    style.configure("TEntry", padding=5, relief="flat", fieldbackground="#F0F2EB")
    style.configure("TCombobox", padding=5, relief="flat", fieldbackground="#F0F2EB")

    return style