import tkinter as tk
from tkinter import ttk

# --- PALET WARNA EARTHY & NYAMAN (Restored) ---
COLORS = {
    # --- SIDEBAR & NAVIGASI (Sage Green) ---
    "sidebar_bg": "#3A4D3F",  # Hijau Sage Tua
    "sidebar_fg": "#E8EDDF",  # Putih Tulang
    "active_bg": "#4F6D54",   # Hijau Sage Sedang
    "active_fg": "#FFFFFF",   # Putih Bersih
    "active_indicator": "#73A580", # Hijau Sage Cerah (Accent)

    # --- AREA KONTEN (Cream) ---
    "bg_main": "#F5F7F0",     # Krem Sangat Muda
    "bg_card": "#FFFFFF",     # Putih Bersih

    # --- TOMBOL UTAMA ---
    "primary": "#73A580",     # Hijau Sage Cerah
    "primary_hover": "#5E8C6A",
    "primary_fg": "#FFFFFF",

    # --- TOMBOL SEKUNDER ---
    "secondary": "#E8EDDF",   # Krem Kehijauan
    "secondary_fg": "#3A4D3F",
    "secondary_hover": "#D0D6CB",

    # --- LAIN-LAIN ---
    "danger": "#D64045",
    "danger_fg": "#FFFFFF",

    "text_header": "#2C3E32", # Hijau Arang Tua
    "text_body": "#4A5552",
    "border": "#CFD8CC"
}

FONTS = {
    "h1": ("Segoe UI", 24, "bold"),
    "h2": ("Segoe UI", 18, "bold"),
    "body": ("Segoe UI", 11),
    "small": ("Segoe UI", 9),
    "btn": ("Segoe UI", 10, "bold")
}


def apply_theme(root):
    style = ttk.Style(root)
    style.theme_use('clam')

    # --- FRAME CONFIG ---
    style.configure("Main.TFrame", background=COLORS["bg_main"])
    style.configure("Card.TFrame", background=COLORS["bg_card"])
    style.configure("Sidebar.TFrame", background=COLORS["sidebar_bg"])

    # --- LABEL CONFIG ---
    style.configure("H1.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_header"], font=FONTS["h1"])
    style.configure("H2.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_header"], font=FONTS["h2"])
    style.configure("Body.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_body"], font=FONTS["body"])
    style.configure("Sub.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_body"], font=FONTS["small"])

    # --- PRIMARY BUTTON ---
    style.configure("Primary.TButton",
                    font=FONTS["btn"],
                    background=COLORS["primary"],
                    foreground=COLORS["primary_fg"],
                    borderwidth=0,
                    focuscolor="none",
                    padding=(20, 12))
    style.map("Primary.TButton",
              background=[("active", COLORS["primary_hover"]), ("pressed", COLORS["sidebar_bg"])])

    # --- SECONDARY BUTTON ---
    style.configure("Soft.TButton",
                    font=FONTS["btn"],
                    background=COLORS["secondary"],
                    foreground=COLORS["secondary_fg"],
                    borderwidth=0,
                    focuscolor="none",
                    padding=(20, 12))
    style.map("Soft.TButton",
              background=[("active", COLORS["secondary_hover"])])

    # --- DANGER BUTTON ---
    style.configure("Danger.TButton",
                    font=FONTS["btn"],
                    background=COLORS["danger"],
                    foreground=COLORS["danger_fg"],
                    borderwidth=0,
                    focuscolor="none",
                    padding=(20, 12))
    style.map("Danger.TButton",
              background=[("active", "#DC2626")])

    # --- INPUT WIDGETS ---
    style.configure("TEntry", padding=8, relief="flat", fieldbackground="#F1F5F9", borderwidth=0)
    style.configure("TCombobox", padding=8, relief="flat", fieldbackground="#F1F5F9", borderwidth=0)
    
    # --- SCROLLBAR ---
    style.configure("Vertical.TScrollbar", 
                    background=COLORS["secondary"], 
                    troughcolor=COLORS["bg_main"],
                    borderwidth=0, 
                    arrowsize=12)

    return style