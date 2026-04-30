import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, filedialog
import csv
import os
import datetime
from data_manager import add_appliance, get_all, remove_appliance
from persistence import save_appliances, load_appliances, save_history, load_history
from logic import compute_all, rank_appliances
from utils import format_kwh, generate_recommendation, generate_overall_insight


# ══════════════════════════════════════════════════════════════════════════════
#  THEME DEFINITIONS  — Refined, high-contrast palettes
# ══════════════════════════════════════════════════════════════════════════════

THEMES = {
    "light": {
        # Backgrounds
        "BG":           "#f0f4f8",   # clean off-white page bg
        "CARD":         "#ffffff",   # pure white cards
        "CARD2":        "#f5f7fa",   # input field fill — barely-grey
        "HOME_BG":      "#0f1c2e",   # deep navy for home (unchanged)
        "HOME_CARD":    "#1a2d45",   # home feature cards (unchanged)

        # Borders / dividers
        "BORDER":       "#e2e8f0",   # very subtle light grey

        # Brand accents
        "ACCENT":       "#2563eb",   # Google/Apple-style vivid blue
        "ACCENT2":      "#1e40af",   # deeper blue — headers
        "ACCENT3":      "#f59e0b",   # clean amber yellow — highlights

        # Text
        "TEXT":         "#111827",   # near-black — crisp on white
        "TEXT_ON_DARK": "#f0f4f8",
        "MUTED":        "#6b7280",   # neutral grey — secondary text
        "MUTED_DARK":   "#8bafc9",

        # Semantic
        "DANGER":       "#dc2626",
        "SUCCESS":      "#16a34a",
        "GOLD":         "#f59e0b",
        "WARNING":      "#f59e0b",

        # Buttons
        "BTN_ADD":      "#2563eb",
        "BTN_ADD_FG":   "#ffffff",
        "BTN_REP":      "#1e40af",
        "BTN_REP_FG":   "#ffffff",
        "BTN_CLR":      "#e2e8f0",
        "BTN_CLR_FG":   "#374151",
        "BTN_HIST":     "#2563eb",
        "BTN_HIST_FG":  "#ffffff",
        "BTN_CMP":      "#f59e0b",
        "BTN_CMP_FG":   "#ffffff",
        "BTN_HOME":     "#1e3a5a",
        "BTN_HOME_FG":  "#ffffff",
        "BTN_THEME":    "#f59e0b",
        "BTN_THEME_FG": "#111827",
        "BTN_REMOVE":   "#dc2626",
        "BTN_REMOVE_FG":"#ffffff",
    },

    "dark": {
        # Backgrounds — layered neutrals, not pure black
        "BG":           "#0f172a",   # deep navy-slate page bg
        "CARD":         "#1e293b",   # slightly lighter card surface
        "CARD2":        "#0f172a",   # input fill = page bg
        "HOME_BG":      "#080e1a",   # deepest dark for home
        "HOME_CARD":    "#162032",   # home feature cards

        # Borders / dividers — subtle, not harsh
        "BORDER":       "#334155",

        # Brand accents
        "ACCENT":       "#3b82f6",   # vivid blue — pops on dark
        "ACCENT2":      "#1e40af",   # deeper blue — headers
        "ACCENT3":      "#fbbf24",   # clean amber yellow

        # Text
        "TEXT":         "#f1f5f9",   # near-white — crisp on dark
        "TEXT_ON_DARK": "#f1f5f9",
        "MUTED":        "#94a3b8",   # slate-400 — readable secondary text
        "MUTED_DARK":   "#94a3b8",

        # Semantic
        "DANGER":       "#f87171",
        "SUCCESS":      "#4ade80",
        "GOLD":         "#fbbf24",
        "WARNING":      "#fbbf24",

        # Buttons — vivid enough to stand out on dark cards
        "BTN_ADD":      "#2563eb",
        "BTN_ADD_FG":   "#f1f5f9",
        "BTN_REP":      "#1d4ed8",
        "BTN_REP_FG":   "#f1f5f9",
        "BTN_CLR":      "#334155",
        "BTN_CLR_FG":   "#cbd5e1",
        "BTN_HIST":     "#2563eb",
        "BTN_HIST_FG":  "#f1f5f9",
        "BTN_CMP":      "#fbbf24",
        "BTN_CMP_FG":   "#0f172a",
        "BTN_HOME":     "#1e3a5a",
        "BTN_HOME_FG":  "#f1f5f9",
        "BTN_THEME":    "#fbbf24",
        "BTN_THEME_FG": "#0f172a",
        "BTN_REMOVE":   "#dc2626",
        "BTN_REMOVE_FG":"#f1f5f9",
    }
}
    

class Toast:
    def __init__(self, root, message, kind="info", duration=2800):
        T_COLORS = {
            "info":    ("#2563eb", "#ffffff"),
            "success": ("#16a34a", "#ffffff"),
            "error":   ("#dc2626", "#ffffff"),
            "warning": ("#f59e0b", "#111827"),
        }
        bg, fg = T_COLORS.get(kind, T_COLORS["info"])

        self.root = root
        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.0)

        icons = {"info": "ℹ", "success": "✓", "error": "✕", "warning": "⚠"}
        icon  = icons.get(kind, "ℹ")

        frame = tk.Frame(self.win, bg=bg, padx=18, pady=12)
        frame.pack()

        tk.Label(frame, text=icon, font=("Segoe UI", 13, "bold"),
                 fg=fg, bg=bg).pack(side="left", padx=(0, 10))
        tk.Label(frame, text=message, font=("Segoe UI", 10),
                 fg=fg, bg=bg, wraplength=280, justify="left").pack(side="left")

        self.win.update_idletasks()
        w = self.win.winfo_width()
        h = self.win.winfo_height()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = sw - w - 24
        self._y_shown  = sh - h - 56
        self._y_hidden = sh + 10
        self.win.geometry(f"{w}x{h}+{x}+{self._y_hidden}")

        self._alpha   = 0.0
        self._sliding = True
        self._fade_in()
        root.after(duration, self._start_fade_out)

    def _fade_in(self):
        sw = self.root.winfo_screenwidth()
        w  = self.win.winfo_width()
        h  = self.win.winfo_height()
        sh = self.root.winfo_screenheight()
        cur_y = int(self.win.geometry().split("+")[2])
        target = self._y_shown
        if cur_y > target:
            new_y = max(target, cur_y - 18)
            self.win.geometry(f"{w}x{h}+{sw - w - 24}+{new_y}")
        self._alpha = min(1.0, self._alpha + 0.08)
        self.win.attributes("-alpha", self._alpha)
        if self._alpha < 1.0 or cur_y > target:
            self.root.after(16, self._fade_in)

    def _start_fade_out(self):
        self._sliding = False
        self._fade_out()

    def _fade_out(self):
        self._alpha = max(0.0, self._alpha - 0.06)
        self.win.attributes("-alpha", self._alpha)
        if self._alpha > 0:
            self.root.after(16, self._fade_out)
        else:
            self.win.destroy()

    def show(self):
        return self
    
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text   = text
        self.tip    = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None):
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() - 30
        self.tip = tk.Toplevel(self.widget)
        self.tip.overrideredirect(True)
        self.tip.attributes("-topmost", True)
        frm = tk.Frame(self.tip, bg="#1e293b", padx=8, pady=4)
        frm.pack()
        tk.Label(frm, text=self.text, font=("Segoe UI", 8),
                 fg="#f1f5f9", bg="#1e293b").pack()
        self.tip.update_idletasks()
        w = self.tip.winfo_width()
        self.tip.geometry(f"+{x - w//2}+{y}")

    def _hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

def _darken(hex_color, amount=20):
    
    try:
        r = max(0, int(hex_color[1:3], 16) - amount)
        g = max(0, int(hex_color[3:5], 16) - amount)
        b = max(0, int(hex_color[5:7], 16) - amount)
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color


def _lighten(hex_color, amount=20):
    try:
        r = min(255, int(hex_color[1:3], 16) + amount)
        g = min(255, int(hex_color[3:5], 16) + amount)
        b = min(255, int(hex_color[5:7], 16) + amount)
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color


class KiloWatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KiloWatch — Decision Support System")

        self._mode = "light"
        self._apply_theme()

        self.root.configure(bg=self.T["HOME_BG"])
        self.root.resizable(True, True)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")
        try:
            self.root.state("zoomed")
        except Exception:
            try:
                self.root.attributes("-zoomed", True)
            except Exception:
                pass

        self.root.minsize(900, 600)
        self.report_history = []
        self._last_ranked = []
        self._goal_kwh = tk.DoubleVar(value=0.0)
        self._goal_bill = tk.DoubleVar(value=0.0)
        self._goal_mode = "kwh"  # "kwh" or "bill"
        self._load_session()
        self._load_session()
        self._build_fonts()
        self._show_homescreen()

    # ── Theme helpers ──────────────────────────────────────────────────────────
    def _apply_theme(self):
        self.T = THEMES[self._mode]

    def _toggle_theme(self):
        self._mode = "dark" if self._mode == "light" else "light"
        self._apply_theme()
        for w in self.root.winfo_children():
            w.destroy()
        self.root.configure(bg=self.T["BG"])
        self._build_ui()
        self._refresh_remove_menu()
        self._refresh_output_appliances()
        for i, rpt in enumerate(self.report_history):
            label = rpt.get("label") or f"[{i+1}]  {rpt['timestamp']}"
            self.hist_listbox.insert(tk.END, label)
        self._refresh_cmp_menus()

    def _toggle_theme_home(self):
        """Toggle theme from the home screen and rebuild home screen."""
        self._mode = "dark" if self._mode == "light" else "light"
        self._apply_theme()
        for w in self.root.winfo_children():
            w.destroy()
        self.root.configure(bg=self.T["HOME_BG"])
        self._show_homescreen()

    # ── Fonts ──────────────────────────────────────────────────────────────────
    def _build_fonts(self):
        self.f_title    = ("Segoe UI", 26, "bold")
        self.f_title2   = ("Segoe UI", 18, "bold")
        self.f_subtitle = ("Segoe UI", 11)
        self.f_label    = ("Segoe UI", 9, "bold")
        self.f_entry    = ("Segoe UI", 11)
        self.f_btn      = ("Segoe UI", 10, "bold")
        self.f_output   = ("Segoe UI", 10)
        self.f_hist     = ("Segoe UI", 9)
        self.f_small    = ("Segoe UI", 8, "bold")

    # ══════════════════════════════════════════════════════════════════════════
    #  HOME SCREEN
    # ══════════════════════════════════════════════════════════════════════════
    def _load_session(self):
        """Restore appliances and report history from disk."""
        saved = load_appliances()
        for name, info in saved.items():
            add_appliance(name, info.get("watts", 0), info.get("hours", 0))
        self.report_history = load_history()

    def _save_session(self):
        save_appliances(get_all())
        save_history(self.report_history)

    def _show_homescreen(self):
        T = self.T
        bg = T["HOME_BG"]
        card_bg = T["HOME_CARD"]
        # Text on dark bg: always use TEXT_ON_DARK for readability
        fg_main   = T["TEXT_ON_DARK"]   # bright near-white
        fg_muted  = T["MUTED_DARK"]     # medium blue-grey — secondary
        fg_accent = T["ACCENT3"]        # amber highlight

        self.root.configure(bg=bg)
        self.home_frame = tk.Frame(self.root, bg=bg)
        self.home_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Top accent bar
        tk.Frame(self.home_frame, height=3, bg=fg_accent).pack(fill="x", side="top")

        # ── Theme toggle pinned top-right ──────────────────────────────────────
        top_bar = tk.Frame(self.home_frame, bg=bg)
        top_bar.pack(fill="x", padx=20, pady=(8, 0))

        mode_icon  = "☀  Light" if self._mode == "dark" else "🌙  Dark"
        theme_home = tk.Button(
            top_bar, text=mode_icon,
            font=("Segoe UI", 9, "bold"),
            bg=T["BTN_THEME"], fg=T["BTN_THEME_FG"],
            activebackground=_lighten(T["BTN_THEME"], 15),
            activeforeground=T["BTN_THEME_FG"],
            relief="flat", bd=0, cursor="hand2", padx=12, pady=5,
            command=self._toggle_theme_home
        )
        theme_home.pack(side="right")

        # ── Centre content ─────────────────────────────────────────────────────
        centre = tk.Frame(self.home_frame, bg=bg)
        centre.place(relx=0.5, rely=0.5, anchor="center")

        # Logo / bolt icon
        icon_canvas = tk.Canvas(centre, width=76, height=76,
                                bg=bg, highlightthickness=0)
        icon_canvas.pack(pady=(0, 16))
        icon_canvas.create_oval(4, 4, 72, 72, fill=card_bg,
                                outline=fg_accent, width=2)
        bolt = [38, 12, 20, 42, 34, 42, 26, 62, 52, 32, 38, 32, 44, 12]
        icon_canvas.create_polygon(bolt, fill=fg_accent, outline="")

        # Title — always bright against dark bg
        tk.Label(centre, text="KiloWatch",
                 font=("Segoe UI", 44, "bold"),
                 fg=fg_main, bg=bg).pack()

        tk.Label(centre, text="A Decision Support System for Optimizing",
                 font=("Segoe UI", 13), fg=fg_muted, bg=bg).pack(pady=(2, 0))
        tk.Label(centre, text="Appliance-level Energy Consumption",
                 font=("Segoe UI", 13, "bold"),
                 fg=fg_accent, bg=bg).pack(pady=(0, 32))

        # Feature cards
        cards_row = tk.Frame(centre, bg=bg)
        cards_row.pack(pady=(0, 36))
        features = [
            ("⚡", "Track Usage",     "Log your appliances\nand daily watt-hours"),
            ("📊", "Generate Reports", "Ranked energy breakdown\nwith smart insights"),
            ("⇄",  "Compare Reports", "Pick any two snapshots\nand analyse changes"),
            ("💡", "Get Suggestions", "Smart tips to cut\nyour electricity bill"),
        ]
        for icon, title, desc in features:
            fc = tk.Frame(cards_row, bg=card_bg,
                          highlightthickness=1, highlightbackground=T["BORDER"])
            fc.pack(side="left", padx=10, ipadx=18, ipady=14)
            tk.Label(fc, text=icon, font=("Segoe UI", 22),
                     fg=fg_accent, bg=card_bg).pack(pady=(12, 4))
            # Card title: bright fg_main so it's visible on dark card_bg
            tk.Label(fc, text=title, font=("Segoe UI", 10, "bold"),
                     fg=fg_main, bg=card_bg).pack()
            tk.Label(fc, text=desc, font=("Segoe UI", 9),
                     fg=fg_muted, bg=card_bg, justify="center").pack(pady=(4, 12))

        # Enter button
        enter_btn = tk.Button(
            centre, text="  ⚡  Open the System  →",
            font=("Segoe UI", 13, "bold"),
            bg=fg_accent, fg=T["HOME_BG"],
            activebackground=_lighten(fg_accent, 20),
            activeforeground=T["HOME_BG"],
            relief="flat", bd=0, cursor="hand2", padx=30, pady=14,
            command=self._launch_system
        )
        enter_btn.pack()
        enter_btn.bind("<Enter>", lambda e: enter_btn.config(bg=_lighten(T["ACCENT3"], 20)))
        enter_btn.bind("<Leave>", lambda e: enter_btn.config(bg=fg_accent))

        # Footer
        tk.Label(self.home_frame,
                 text="Developed by Kaixer Alvar",
                 font=("Segoe UI", 8), fg=fg_muted, bg=bg
                 ).place(relx=0.5, rely=0.97, anchor="center")

        tk.Frame(self.home_frame, height=3, bg=T["ACCENT"]).pack(
            side="bottom", fill="x")

    def _launch_system(self):
        self.home_frame.destroy()
        self.root.configure(bg=self.T["BG"])
        self._build_ui()
        self._refresh_remove_menu()
        self._refresh_output_appliances()
        for rpt in self.report_history:
            self.hist_listbox.insert(tk.END, rpt.get("label", rpt["timestamp"]))
        self._refresh_cmp_menus()

    # ══════════════════════════════════════════════════════════════════════════
    #  MAIN SYSTEM UI
    # ══════════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        T = self.T
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        # ── Header ────────────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=T["ACCENT2"], pady=0)
        header.grid(row=0, column=0, sticky="ew")
        tk.Frame(self.root, height=3, bg=T["ACCENT3"]).grid(
            row=0, column=0, sticky="new")

        inner_header = tk.Frame(header, bg=T["ACCENT2"])
        inner_header.pack(fill="x", padx=32, pady=(14, 12))

        # Bolt icon
        left_h = tk.Frame(inner_header, bg=T["ACCENT2"])
        left_h.pack(side="left")
        bolt_c = tk.Canvas(left_h, width=32, height=32,
                           bg=T["ACCENT2"], highlightthickness=0)
        bolt_c.create_oval(2, 2, 30, 30, fill=T["ACCENT3"], outline="")
        bolt_pts = [16, 4, 8, 18, 14, 18, 10, 28, 22, 14, 16, 14, 20, 4]
        bolt_c.create_polygon(bolt_pts, fill=T["ACCENT2"], outline="")
        bolt_c.pack(side="left", padx=(0, 10))

        title_stack = tk.Frame(inner_header, bg=T["ACCENT2"])
        title_stack.pack(side="left")
        # Header text — always white against the dark-blue/navy header
        tk.Label(title_stack, text="KiloWatch",
                 font=("Segoe UI", 20, "bold"),
                 fg="#ffffff", bg=T["ACCENT2"]).pack(anchor="w")
        tk.Label(title_stack,
                 text="A Decision Support System for Optimizing Appliance-level Energy Consumption",
                 font=("Segoe UI", 8), fg="#a8c4e0",
                 bg=T["ACCENT2"]).pack(anchor="w")

        # Clock
        self.clock_label = tk.Label(inner_header, font=("Segoe UI", 9),
                                    fg="#a8c4e0", bg=T["ACCENT2"])
        self.clock_label.pack(side="right", padx=(0, 4))
        self._tick_clock()

        # ── Home button — always clearly visible ───────────────────────────────
        home_btn = tk.Button(
            inner_header, text="⌂  Home",
            font=("Segoe UI", 9, "bold"),
            bg=T["BTN_HOME"], fg=T["BTN_HOME_FG"],
            activebackground=_lighten(T["BTN_HOME"], 20),
            activeforeground=T["BTN_HOME_FG"],
            relief="flat", bd=0, cursor="hand2", padx=10, pady=4,
            command=self._go_home
        )
        home_btn.pack(side="right", padx=(0, 8))

        # ── Theme toggle ───────────────────────────────────────────────────────
        mode_icon  = "☀  Light" if self._mode == "dark" else "🌙  Dark"
        self._theme_btn = tk.Button(
            inner_header, text=mode_icon,
            font=("Segoe UI", 9, "bold"),
            bg=T["BTN_THEME"], fg=T["BTN_THEME_FG"],
            activebackground=_lighten(T["BTN_THEME"], 20),
            activeforeground=T["BTN_THEME_FG"],
            relief="flat", bd=0, cursor="hand2", padx=10, pady=4,
            command=self._toggle_theme
        )
        self._theme_btn.pack(side="right", padx=(0, 8))

        # ── Body ──────────────────────────────────────────────────────────────
        body = tk.Frame(self.root, bg=T["BG"])
        body.grid(row=1, column=0, sticky="nsew", padx=16, pady=10)
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)

        left = tk.Frame(body, bg=T["BG"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.rowconfigure(1, weight=1)   # output card gets all spare height
        left.columnconfigure(0, weight=1)

        # ── Compact top strip: inputs + rate + buttons all in one row ──────────
        top_strip = tk.Frame(left, bg=T["BG"])
        top_strip.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        top_strip.columnconfigure(0, weight=3)   # input card
        top_strip.columnconfigure(1, weight=1)   # rate + actions stacked

        self._build_input_card(top_strip, grid_col=0)

        right_strip = tk.Frame(top_strip, bg=self.T["BG"])
        right_strip.grid(row=0, column=1, sticky="nsew")
        right_strip.rowconfigure(0, weight=1)
        right_strip.rowconfigure(1, weight=1)
        right_strip.columnconfigure(0, weight=1)

        self._build_rate_card(right_strip, grid_col=0, grid_row=0)
        self._build_action_buttons(right_strip, grid_col=0, grid_row=1)

        # ── Output fills the rest ─────────────────────────────────────────────
        self._build_output_card(left)
        self._build_history_panel(body)
    
    def _build_rate_card(self, parent, grid_col=1, grid_row=0):
        T = self.T
        card = self._card(parent)
        card.grid(row=grid_row, column=grid_col, sticky="nsew", padx=(0, 0), pady=(0, 6))

        self._section_label(card, "RATE  (optional)", T["ACCENT3"])

        tk.Label(card, text="₱/kWh — Meralco Apr 2026: 14.3496",
                 font=("Segoe UI", 7), fg=T["MUTED"], bg=T["CARD"],
                 wraplength=160, justify="left"
                 ).pack(anchor="w", padx=12, pady=(0, 4))

        rate_row = tk.Frame(card, bg=T["CARD"])
        rate_row.pack(fill="x", padx=12, pady=(0, 12))

        self.rate_entry = tk.Entry(
            rate_row, font=("Segoe UI", 10),
            bg=T["CARD2"], fg=T["TEXT"],
            insertbackground=T["ACCENT"],
            relief="flat", bd=0, width=9,
            highlightthickness=1,
            highlightbackground=T["BORDER"],
            highlightcolor=T["ACCENT"],
        )
        self.rate_entry.insert(0, "14.3496")
        self.rate_entry.pack(side="left", ipady=5)

        tk.Label(rate_row, text="₱/kWh", font=("Segoe UI", 8),
                 fg=T["MUTED"], bg=T["CARD"]).pack(side="left", padx=(6, 0))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _tick_clock(self):
        now = datetime.datetime.now().strftime("%A, %b %d %Y   %H:%M:%S")
        self.clock_label.config(text=now)
        self.root.after(1000, self._tick_clock)

    def _go_home(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self._show_homescreen()

    # ── Input Card ────────────────────────────────────────────────────────────
    def _build_input_card(self, parent, grid_col=0):
        T = self.T
        card = self._card(parent)
        card.grid(row=0, column=grid_col, sticky="nsew", padx=(0, 8))

        self._section_label(card, "ADD APPLIANCE", T["ACCENT"])

        fields = tk.Frame(card, bg=T["CARD"])
        fields.pack(fill="x", padx=16, pady=(0, 10))
        fields.columnconfigure(0, weight=1)
        fields.columnconfigure(1, weight=1)
        fields.columnconfigure(2, weight=1)

        self.name_entry  = self._field(fields, "Appliance Name", col=0, hint="e.g. Air Con")
        self.watts_entry = self._field(fields, "Watts (W)",      col=1, hint="e.g. 750")
        self.hours_entry = self._field(fields, "Usage / Day",    col=2, hint="e.g. 8")

        # Unit toggle — hours or minutes
        unit_row = tk.Frame(fields, bg=T["CARD"])
        unit_row.grid(row=1, column=2, sticky="w", padx=(6, 0), pady=(4, 0))
        self.time_unit = tk.StringVar(value="Hours")
        for unit in ("Hours", "Minutes"):
            tk.Radiobutton(
                unit_row, text=unit,
                variable=self.time_unit, value=unit,
                font=("Segoe UI", 8),
                bg=T["CARD"], fg=T["MUTED"],
                selectcolor=T["CARD2"],
                activebackground=T["CARD"],
                relief="flat", bd=0
            ).pack(side="left", padx=(0, 8))


        self.name_entry.bind("<Return>", lambda e: self.add())
        self.watts_entry.bind("<Return>", lambda e: self.add())
        self.hours_entry.bind("<Return>", lambda e: self.add())

        add_btn = self._btn(card, "＋  Add Appliance",
                  T["BTN_ADD"], T["BTN_ADD_FG"],
                  self.add)
        add_btn.pack(fill="x", padx=16, pady=(0, 12))
        Tooltip(add_btn, "Add this appliance to your list")

        tk.Frame(card, height=1, bg=T["BORDER"]).pack(fill="x", padx=16)
        self._section_label(card, "REMOVE APPLIANCE", T["DANGER"])

        remove_row = tk.Frame(card, bg=T["CARD"])
        remove_row.pack(fill="x", padx=16, pady=(0, 14))
        remove_row.columnconfigure(0, weight=1)

        self.remove_var  = tk.StringVar(value="")
        self.remove_menu = tk.OptionMenu(remove_row, self.remove_var, "")
        self._style_optionmenu(self.remove_menu, T["DANGER"])
        self.remove_menu.grid(row=0, column=0, sticky="ew", ipady=4)

        self._btn(remove_row, "－  Remove",
                  T["BTN_REMOVE"], T["BTN_REMOVE_FG"],
                  self.remove).grid(row=0, column=1, sticky="ew", padx=(8, 0))

        remove_row.columnconfigure(2, weight=1)
        tk.Button(
            remove_row, text="All", width=5,
            font=("Segoe UI", 10, "bold"),
            bg=T["BTN_REMOVE"], fg=T["BTN_REMOVE_FG"],
            activebackground=_darken(T["BTN_REMOVE"], 15),
            activeforeground=T["BTN_REMOVE_FG"],
            relief="flat", bd=0, cursor="hand2",
            padx=12, pady=8, command=self._remove_all_appliances
        ).grid(row=0, column=2, padx=(8, 0))
        remove_row.columnconfigure(2, weight=0)

    # ── Action Buttons ────────────────────────────────────────────────────────
    def _build_action_buttons(self, parent, grid_col=0, grid_row=1):
        T = self.T

        outer = tk.Frame(parent, bg=T["CARD"],
                         highlightthickness=1, highlightbackground=T["BORDER"])
        outer.grid(row=grid_row, column=grid_col, sticky="nsew")

        tk.Label(outer, text="ACTIONS", font=self.f_small,
                 fg=T["ACCENT2"], bg=T["CARD"]).pack(anchor="w", padx=12, pady=(10, 6))

        # Generate — full width, tall, primary CTA
        gen_btn = self._btn(outer, "⚡  Generate",
                  T["BTN_REP"], T["BTN_REP_FG"],
                  self.report)
        gen_btn.pack(fill="x", padx=10, pady=(0, 4))
        Tooltip(gen_btn, "Compute and rank appliance energy usage")

        clr_btn = self._btn(outer, "✕  Clear",
                  T["BTN_CLR"], T["BTN_CLR_FG"],
                  self.clear_output)
        clr_btn.pack(fill="x", padx=10, pady=(0, 4))
        Tooltip(clr_btn, "Clear the output panel")

        whatif_btn = self._btn(outer, "💡  What If",
                  T["BTN_CMP"], T["BTN_CMP_FG"],
                  self._open_whatif_window)
        whatif_btn.pack(fill="x", padx=10, pady=(0, 4))
        Tooltip(whatif_btn, "Simulate reducing an appliance's daily hours")

        

        # More ▾ dropdown
        more_btn = tk.Menubutton(
            outer, text="⋯  More ▾",
            font=self.f_btn,
            bg=T["BTN_HIST"], fg=T["BTN_HIST_FG"],
            activebackground=_lighten(T["BTN_HIST"], 15),
            activeforeground=T["BTN_HIST_FG"],
            relief="flat", bd=0, cursor="hand2",
            padx=10, pady=8,
            direction="below",
        )
        more_btn.pack(fill="x", padx=10, pady=(0, 10))

        more_menu = tk.Menu(more_btn, tearoff=0,
                            bg=T["CARD"], fg=T["TEXT"],
                            activebackground=T["BTN_HIST"],
                            activeforeground="#ffffff",
                            font=("Segoe UI", 9),
                            bd=0, relief="flat")
        more_btn["menu"] = more_menu
        more_menu.add_command(label="📋  Copy to Clipboard",
                              command=self._copy_to_clipboard)
        more_menu.add_command(label="🎯  Goal Tracker",
                              command=self._open_goal_tracker)
        more_menu.add_separator()
        more_menu.add_command(label="💾  Export as .TXT",
                              command=lambda: self._export_report("txt"))
        more_menu.add_command(label="📊  Export as .CSV",
                              command=lambda: self._export_report("csv"))

    # ── Output Card ───────────────────────────────────────────────────────────
    def _build_output_card(self, parent):
        T = self.T
        out_card = self._card(parent)
        out_card.grid(row=1, column=0, sticky="nsew")
        out_card.rowconfigure(1, weight=1)
        out_card.columnconfigure(0, weight=1)

        hdr = tk.Frame(out_card, bg=T["CARD"])
        hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 0))

        tk.Label(hdr, text="OUTPUT", font=self.f_small,
                 fg=T["ACCENT2"], bg=T["CARD"]).pack(side="left")

        self.status_dot = tk.Canvas(hdr, width=9, height=9,
                                    bg=T["CARD"], highlightthickness=0)
        self.status_dot.create_oval(0, 0, 9, 9,
                                    fill=T["MUTED"], outline="", tags="dot")
        self.status_dot.pack(side="right", pady=2)

        tk.Frame(out_card, height=1, bg=T["BORDER"]).grid(
            row=0, column=0, sticky="ew", padx=16, pady=(34, 0))

        txt_frame = tk.Frame(out_card, bg=T["CARD"])
        txt_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=10)
        txt_frame.rowconfigure(0, weight=1)
        txt_frame.columnconfigure(0, weight=1)

        sb = ttk.Scrollbar(txt_frame, orient="vertical")
        sb.grid(row=0, column=1, sticky="ns")

        self.output = tk.Text(
            txt_frame, font=self.f_output,
            bg=T["CARD2"], fg=T["TEXT"],
            insertbackground=T["ACCENT"],
            selectbackground=T["BORDER"],
            relief="flat", bd=0, wrap="word",
            yscrollcommand=sb.set, padx=10, pady=8,
            state="disabled"
        )
        self.output.grid(row=0, column=0, sticky="nsew")
        sb.config(command=self.output.yview)

        # Text tags — all foregrounds chosen for legibility on CARD2 bg
        self.output.tag_configure("header",  foreground=T["ACCENT2"],  font=("Segoe UI", 13, "bold"))
        self.output.tag_configure("section", foreground=T["GOLD"],     font=("Segoe UI", 10, "bold"))
        self.output.tag_configure("name",    foreground=T["ACCENT"],   font=("Segoe UI", 10, "bold"))
        self.output.tag_configure("kwh",     foreground=T["TEXT"],     font=("Segoe UI", 10))
        self.output.tag_configure("rec",     foreground=T["MUTED"],    font=("Segoe UI", 9, "italic"))
        self.output.tag_configure("insight", foreground=T["ACCENT"],   font=("Segoe UI", 9, "italic"))
        self.output.tag_configure("divider", foreground=T["BORDER"])
        self.output.tag_configure("added",   foreground=T["ACCENT"],   font=("Segoe UI", 10))
        self.output.tag_configure("warning", foreground=T["DANGER"],   font=("Segoe UI", 9, "italic"))
        self.output.tag_configure("good",    foreground=T["SUCCESS"],  font=("Segoe UI", 9))

        # Bar chart canvas below the text output
        chart_card = self._card(parent)
        chart_card.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        tk.Label(chart_card, text="USAGE CHART", font=self.f_small,
                 fg=self.T["ACCENT2"], bg=self.T["CARD"]
                 ).pack(anchor="w", padx=16, pady=(10, 4))

        self.chart_canvas = tk.Canvas(
            chart_card, height=160,
            bg=self.T["CARD"], highlightthickness=0
        )
        self.chart_canvas.pack(fill="x", padx=16, pady=(0, 12))
        self.chart_canvas.bind("<Configure>", lambda e: self._redraw_chart())
        self._chart_data = []

        parent.rowconfigure(1, weight=1)
        self._write_placeholder()

    # ── History Panel (right) ─────────────────────────────────────────────────
    def _build_history_panel(self, parent):
        T = self.T
        panel = self._card(parent)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.rowconfigure(7, weight=1)
        panel.columnconfigure(0, weight=1)

        self._section_label(panel, "REPORT HISTORY", T["BTN_HIST"], row=0)
        tk.Frame(panel, height=1, bg=T["BORDER"]).grid(
            row=0, column=0, sticky="ew", padx=16, pady=(34, 0))

        lf = tk.Frame(panel, bg=T["CARD"])
        lf.grid(row=1, column=0, sticky="ew", padx=12, pady=(8, 4))

        self.hist_listbox = tk.Listbox(
            lf, font=self.f_hist,
            bg=T["CARD2"], fg=T["TEXT"],
            selectbackground=T["BTN_HIST"],
            selectforeground="#ffffff",     # always white on purple
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=T["BORDER"],
            activestyle="none", height=6
        )
        hist_sb = ttk.Scrollbar(lf, orient="vertical",
                                command=self.hist_listbox.yview)
        self.hist_listbox.config(yscrollcommand=hist_sb.set)
        self.hist_listbox.pack(side="left", fill="both", expand=True)
        hist_sb.pack(side="right", fill="y")
        self.hist_listbox.bind("<<ListboxSelect>>", self._preview_history_entry)
        btn_row_hist = tk.Frame(panel, bg=T["CARD"])
        btn_row_hist.grid(row=2, column=0, sticky="ew", padx=12, pady=(4, 8))
        btn_row_hist.columnconfigure(0, weight=1)
        btn_row_hist.columnconfigure(1, weight=1)

        btn_row_hist.columnconfigure(2, weight=1)

        ren_btn = self._btn(btn_row_hist, "✎  Rename",
                  T["BTN_HIST"], T["BTN_HIST_FG"],
                  self._rename_history_entry)
        ren_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        Tooltip(ren_btn, "Rename the selected report")

        del_btn = self._btn(btn_row_hist, "🗑  Delete",
                  T["BTN_REMOVE"], T["BTN_REMOVE_FG"],
                  self._delete_history_entry)
        del_btn.grid(row=0, column=1, sticky="ew", padx=(0, 4))
        Tooltip(del_btn, "Delete the selected report")

        del_all_btn = tk.Button(
            btn_row_hist, text="🗑 All", width=5,
            font=("Segoe UI", 10, "bold"),
            bg=T["BTN_REMOVE"], fg=T["BTN_REMOVE_FG"],
            activebackground=_darken(T["BTN_REMOVE"], 15),
            activeforeground=T["BTN_REMOVE_FG"],
            relief="flat", bd=0, cursor="hand2",
            padx=12, pady=8, command=self._delete_all_history
        )
        del_all_btn.grid(row=0, column=2, padx=(4, 0))
        btn_row_hist.columnconfigure(2, weight=0)
        Tooltip(del_all_btn, "Delete all reports from history")

        sel_frame = tk.Frame(panel, bg=T["CARD"])
        sel_frame.grid(row=3, column=0, sticky="ew", padx=12)
        sel_frame.columnconfigure(0, weight=1)
        sel_frame.columnconfigure(1, weight=1)

        tk.Label(sel_frame, text="REPORT A", font=self.f_small,
                 fg=T["ACCENT"], bg=T["CARD"]).grid(
            row=0, column=0, sticky="w", pady=(4, 0))
        tk.Label(sel_frame, text="REPORT B", font=self.f_small,
                 fg=T["GOLD"], bg=T["CARD"]).grid(
            row=0, column=1, sticky="w", pady=(4, 0), padx=(6, 0))

        self.cmp_a_var = tk.StringVar(value="(select)")
        self.cmp_b_var = tk.StringVar(value="(select)")

        self.cmp_a_menu = tk.OptionMenu(sel_frame, self.cmp_a_var, "(none)")
        self._style_optionmenu(self.cmp_a_menu, T["ACCENT"])
        self.cmp_a_menu.grid(row=1, column=0, sticky="ew", ipady=3)

        self.cmp_b_menu = tk.OptionMenu(sel_frame, self.cmp_b_var, "(none)")
        self._style_optionmenu(self.cmp_b_menu, T["GOLD"])
        self.cmp_b_menu.grid(row=1, column=1, sticky="ew", ipady=3, padx=(6, 0))

        self._btn(panel, "⇄  Compare A  vs  B",
                  T["BTN_CMP"], T["BTN_CMP_FG"],
                  self.compare_reports).grid(
            row=4, column=0, sticky="ew", padx=12, pady=(4, 2))

        tk.Frame(panel, height=1, bg=T["BORDER"]).grid(
            row=5, column=0, sticky="ew", padx=16, pady=(2, 0))
        tk.Label(panel, text="COMPARISON RESULTS", font=self.f_small,
                 fg=T["BTN_HIST"], bg=T["CARD"]).grid(
            row=6, column=0, sticky="w", padx=16, pady=(4, 2))

        cmp_frame = tk.Frame(panel, bg=T["CARD"])
        cmp_frame.grid(row=7, column=0, sticky="nsew", padx=12, pady=(0, 12))
        cmp_frame.rowconfigure(0, weight=1)
        cmp_frame.columnconfigure(0, weight=1)
        panel.rowconfigure(7, weight=1)

        cmp_sb = ttk.Scrollbar(cmp_frame, orient="vertical")
        cmp_sb.grid(row=0, column=1, sticky="ns")

        self.cmp_output = tk.Text(
            cmp_frame, font=("Segoe UI", 9),
            bg=T["CARD2"], fg=T["TEXT"],
            relief="flat", bd=0, wrap="word",
            highlightthickness=1, highlightbackground=T["BORDER"],
            yscrollcommand=cmp_sb.set, padx=8, pady=6,
            state="disabled"
        )
        self.cmp_output.grid(row=0, column=0, sticky="nsew")
        cmp_sb.config(command=self.cmp_output.yview)

        self.cmp_output.tag_configure("head",    foreground=T["ACCENT2"],  font=("Segoe UI", 9, "bold"))
        self.cmp_output.tag_configure("better",  foreground=T["SUCCESS"],  font=("Segoe UI", 9, "bold"))
        self.cmp_output.tag_configure("worse",   foreground=T["DANGER"],   font=("Segoe UI", 9, "bold"))
        self.cmp_output.tag_configure("same",    foreground=T["MUTED"])
        self.cmp_output.tag_configure("suggest", foreground=T["GOLD"],     font=("Segoe UI", 9, "italic"))
        self.cmp_output.tag_configure("praise",  foreground=T["SUCCESS"],  font=("Segoe UI", 9, "italic"))
        self.cmp_output.tag_configure("divider", foreground=T["BORDER"])
        self.cmp_output.tag_configure("label",   foreground=T["MUTED"],    font=("Segoe UI", 8))

        self._cmp_write("Select Report A and Report B\nthen press ⇄ Compare.\n", "same")

    # ── Card / Widget helpers ──────────────────────────────────────────────────
    def _card(self, parent):
        T = self.T
        return tk.Frame(parent, bg=T["CARD"], bd=0,
                        highlightthickness=1, highlightbackground=T["BORDER"])

    def _section_label(self, parent, text, color, row=None):
        T = self.T
        lbl = tk.Label(parent, text=text, font=self.f_small,
                       fg=color, bg=T["CARD"])
        if row is not None:
            lbl.grid(row=row, column=0, sticky="w", padx=16, pady=(14, 6))
        else:
            lbl.pack(anchor="w", padx=16, pady=(14, 6))

    def _style_optionmenu(self, menu, accent=None):
        T = self.T
        if accent is None:
            accent = T["ACCENT"]
        menu.config(
            font=("Segoe UI", 9),
            bg=T["CARD2"], fg=T["TEXT"],
            activebackground=T["BORDER"],
            activeforeground=T["TEXT"],
            highlightthickness=1, highlightbackground=accent,
            relief="flat", bd=0, anchor="w",
        )
        menu["menu"].config(
            bg=T["CARD2"], fg=T["TEXT"],
            activebackground=accent,
            activeforeground="#ffffff",
            font=("Segoe UI", 9),
        )

    def _field(self, parent, placeholder, col, hint=""):
        T = self.T
        wrapper = tk.Frame(parent, bg=T["CARD"])
        wrapper.grid(row=0, column=col, sticky="ew",
                     padx=(0 if col == 0 else 6, 0))
        tk.Label(wrapper, text=placeholder.upper(), font=("Segoe UI", 7, "bold"),
                 fg=T["MUTED"], bg=T["CARD"]).pack(anchor="w")
        entry = tk.Entry(
            wrapper, font=self.f_entry,
            bg=T["CARD2"], fg=T["MUTED"],
            insertbackground=T["ACCENT"],
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=T["BORDER"],
            highlightcolor=T["ACCENT"],
        )
        entry.pack(fill="x", ipady=6)
        # Inline error label
        err_lbl = tk.Label(wrapper, text="", font=("Segoe UI", 7),
                           fg=T["DANGER"], bg=T["CARD"])
        err_lbl.pack(anchor="w")
        entry._err_label = err_lbl

        if hint:
            entry.insert(0, hint)
            entry._placeholder = hint
            entry._has_placeholder = True
        else:
            entry._placeholder = ""
            entry._has_placeholder = False

        def _on_focus_in(e):
            if entry._has_placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=T["TEXT"])
                entry._has_placeholder = False

        def _on_focus_out(e):
            if not entry.get().strip():
                entry.delete(0, tk.END)
                entry.insert(0, entry._placeholder)
                entry.config(fg=T["MUTED"])
                entry._has_placeholder = True

        entry.bind("<FocusIn>", _on_focus_in)
        entry.bind("<FocusOut>", _on_focus_out)
        return entry

    def _btn(self, parent, text, bg, fg, cmd):
        b = tk.Button(
            parent, text=text, font=self.f_btn,
            bg=bg, fg=fg,
            activebackground=_darken(bg, 15),
            activeforeground=fg,
            relief="flat", bd=0, cursor="hand2",
            padx=12, pady=8, command=cmd
        )
        b.bind("<Enter>", lambda e, b=b, c=bg: b.config(bg=_lighten(c, 15)))
        b.bind("<Leave>", lambda e, b=b, c=bg: b.config(bg=c))
        return b

    def _set_status(self, active=True):
        T = self.T
        self.status_dot.itemconfig("dot", fill=T["ACCENT"] if active else T["MUTED"])

    def _unlock(self):
        self.output.config(state="normal")

    def _lock(self):
        self.output.config(state="disabled")

    def _redraw_chart(self):
        c = self.chart_canvas
        c.delete("all")
        data = self._chart_data
        if not data:
            c.create_text(
                c.winfo_width() // 2, 70,
                text="Generate a report to see the chart",
                font=("Segoe UI", 9), fill=self.T["MUTED"]
            )
            return

        T       = self.T
        W       = c.winfo_width() or 400
        max_kwh = max(kwh for _, kwh in data) or 1
        bar_h   = 22
        gap     = 8
        label_w = 130
        val_w   = 72
        bar_area = W - label_w - val_w - 16
        colors   = [T["ACCENT"], T["ACCENT2"], T["ACCENT3"]]
        medals   = ["🥇", "🥈", "🥉"]

        for i, (name, kwh) in enumerate(data):
            y      = i * (bar_h + gap) + 8
            ratio  = kwh / max_kwh
            bar_px = max(4, int(ratio * bar_area))
            color  = colors[i] if i < 3 else T["MUTED"]

            # Label
            display = (name[:16] + "…") if len(name) > 17 else name
            prefix  = medals[i] + "  " if i < 3 else f"  {i+1}.  "
            c.create_text(
                label_w - 6, y + bar_h // 2,
                text=prefix + display,
                anchor="e", font=("Segoe UI", 8),
                fill=T["TEXT"]
            )

            # Background track
            c.create_rectangle(
                label_w, y,
                label_w + bar_area, y + bar_h,
                fill=T["CARD2"], outline="", width=0
            )

            # Filled bar with rounded feel (two rects + oval cap)
            if bar_px > 0:
                c.create_rectangle(
                    label_w, y,
                    label_w + bar_px, y + bar_h,
                    fill=color, outline="", width=0
                )

            # Value label
            monthly = kwh * 30
            c.create_text(
                label_w + bar_area + 6, y + bar_h // 2,
                text=f"{kwh:.3f} kWh/d",
                anchor="w", font=("Segoe UI", 8),
                fill=T["MUTED"]
            )

        total_h = len(data) * (bar_h + gap) + 16
        c.config(height=max(80, total_h))

    def _write_placeholder(self):
        self._unlock()
        self.output.insert("1.0",
            "Add your appliances above, then click\n"
            "⚡  Generate Report to see the full analysis.\n",
            "rec")
        self._lock()

    # ── Remove menu / output refresh ──────────────────────────────────────────
    def _refresh_remove_menu(self):
        data = get_all()
        menu = self.remove_menu["menu"]
        menu.delete(0, "end")
        if data:
            for name in data.keys():
                menu.add_command(label=name,
                                 command=lambda n=name: self.remove_var.set(n))
            if self.remove_var.get() not in data:
                self.remove_var.set(next(iter(data)))
        else:
            menu.add_command(label="(none)", command=lambda: None)
            self.remove_var.set("")

    def _refresh_cmp_menus(self):
        for var, menu_widget in [(self.cmp_a_var, self.cmp_a_menu),
                                 (self.cmp_b_var, self.cmp_b_menu)]:
            m = menu_widget["menu"]
            m.delete(0, "end")
            for i, rpt in enumerate(self.report_history):
                label = rpt.get("label") or f"[{i+1}] {rpt['timestamp']}"
                m.add_command(label=label,
                              command=lambda lbl=label, v=var: v.set(lbl))
            n = len(self.report_history)
            if n > 0 and var.get() in ("(select)", "(none)"):
                last = self.report_history[-1]
                var.set(last.get("label") or f"[{n}] {last['timestamp']}")

    def _refresh_output_appliances(self):
        self._refresh_remove_menu()
        data = get_all()
        self._unlock()
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "📋  CURRENT APPLIANCES\n", "header")
        self.output.insert(tk.END, "─" * 48 + "\n", "divider")
        if not data:
            self.output.insert(tk.END, "  No appliances yet — add one above.\n", "rec")
        else:
            for i, (name, info) in enumerate(data.items(), 1):
                watts = info.get("watts", 0)
                hours = info.get("hours", 0)
                self.output.insert(tk.END, f"  {i}.  {name}\n", "name")
                self.output.insert(tk.END, f"       {watts} W  ×  {hours} h/day\n", "kwh")
        self.output.insert(tk.END, "\n", "rec")
        self._lock()

    # ── History helpers ───────────────────────────────────────────────────────
    def _save_report(self, ranked):
        ts = datetime.datetime.now().strftime("%b %d  %H:%M:%S")
        idx = len(self.report_history) + 1
        count = len(ranked)
        default_label = f"[{idx}]  {count} appliance{'s' if count != 1 else ''}  —  {ts}"
        self.report_history.append({
            "timestamp": ts,
            "ranked":    ranked,
            "label":     default_label,
        })
        self.hist_listbox.insert(tk.END, default_label)
        self.hist_listbox.see(tk.END)
        self._refresh_cmp_menus()
        self._save_session()

    def _preview_history_entry(self, event=None):
        sel = self.hist_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        rpt = self.report_history[idx]
        ranked = rpt["ranked"]
        label  = rpt.get("label", rpt["timestamp"])

        self._unlock()
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, f"🕘  PREVIEW — {label}\n", "header")
        self.output.insert(tk.END, "─" * 48 + "\n", "divider")
        for i, (name, kwh) in enumerate(ranked, 1):
            medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"  {i}."
            monthly_kwh = kwh * 30
            self.output.insert(tk.END, f"\n{medal}  {name}\n", "name")
            self.output.insert(tk.END,
                f"     {format_kwh(kwh, 'kWh/day')}  |  {format_kwh(monthly_kwh, 'kWh/month')}\n", "kwh")
        self.output.insert(tk.END, "\n" + "─" * 48 + "\n", "divider")
        total = sum(k for _, k in ranked)
        self.output.insert(tk.END,
            f"    Daily Total : {format_kwh(total, 'kWh/day')}\n"
            f"    Monthly Est.: {format_kwh(total * 30, 'kWh/month')}\n", "section")
        self._lock()

    def _rename_history_entry(self):
        sel = self.hist_listbox.curselection()
        if not sel:
            Toast(self.root, "Select a report from the list first.", "warning")
            return
        idx = sel[0]
        rpt = self.report_history[idx]
        current_label = rpt.get("label", "")

        new_name = simpledialog.askstring(
            "Rename Report",
            f"Enter a new name for report #{idx + 1}:",
            initialvalue=current_label,
            parent=self.root,
        )
        if new_name is None:
            return
        new_name = new_name.strip()
        if not new_name:
            Toast(self.root, "Report name cannot be blank.", "error")
            return

        rpt["label"] = new_name
        self.hist_listbox.delete(idx)
        self.hist_listbox.insert(idx, new_name)
        self.hist_listbox.selection_set(idx)
        self._refresh_cmp_menus()

    def _delete_all_history(self):
        if not self.report_history:
            Toast(self.root, "No reports in history to delete.", "warning")
            return
        if not messagebox.askyesno("Delete All", "Delete all reports from history? This cannot be undone."):
            return
        self.report_history.clear()
        self.hist_listbox.delete(0, tk.END)
        self._refresh_cmp_menus()
        self._save_session()
        Toast(self.root, "All reports deleted.", "success")

    def _delete_history_entry(self):
        sel = self.hist_listbox.curselection()
        if not sel:
            Toast(self.root, "Select a report from the list first.", "warning")
            return
        idx = sel[0]
        rpt = self.report_history[idx]
        label = rpt.get("label", f"Report #{idx + 1}")
        if not messagebox.askyesno("Delete Entry", f"Delete '{label}' from history?"):
            return
        self.report_history.pop(idx)
        self.hist_listbox.delete(idx)
        self._refresh_cmp_menus()
        self._write_placeholder()

    def _cmp_write(self, text, tag="same"):
        self.cmp_output.config(state="normal")
        self.cmp_output.delete("1.0", tk.END)
        self.cmp_output.insert(tk.END, text, tag)
        self.cmp_output.config(state="disabled")

    def _cmp_append(self, text, tag="same"):
        self.cmp_output.config(state="normal")
        self.cmp_output.insert(tk.END, text, tag)
        self.cmp_output.config(state="disabled")

    # ══════════════════════════════════════════════════════════════════════════
    #  ACTIONS
    # ══════════════════════════════════════════════════════════════════════════
    def _field_error(self, entry, msg=""):
        T = self.T
        lbl = getattr(entry, "_err_label", None)
        if msg:
            entry.config(highlightbackground=T["DANGER"], highlightcolor=T["DANGER"])
            if lbl:
                lbl.config(text=msg)
        else:
            entry.config(highlightbackground=T["BORDER"], highlightcolor=T["ACCENT"])
            if lbl:
                lbl.config(text="")

    def _get_real_value(self, entry):
        """Return entry value, ignoring placeholder text."""
        val = entry.get().strip()
        if getattr(entry, "_has_placeholder", False) or val == entry._placeholder:
            return ""
        return val

    def add(self):
        name  = self._get_real_value(self.name_entry)
        watts = self._get_real_value(self.watts_entry)
        hours = self._get_real_value(self.hours_entry)

        # Clear previous errors
        for e in (self.name_entry, self.watts_entry, self.hours_entry):
            self._field_error(e)

        ok = True
        if not name:
            self._field_error(self.name_entry, "Required")
            ok = False

        watts_f = None
        hours_f = None

        if not watts:
            self._field_error(self.watts_entry, "Required")
            ok = False
        else:
            try:
                watts_f = float(watts)
                if watts_f <= 0:
                    self._field_error(self.watts_entry, "Must be > 0")
                    ok = False
                elif watts_f > 15000:
                    self._field_error(self.watts_entry, "Unrealistic (>15 000 W)")
                    ok = False
            except ValueError:
                self._field_error(self.watts_entry, "Must be a number")
                ok = False

        if not hours:
            self._field_error(self.hours_entry, "Required")
            ok = False
        else:
            try:
                hours_f = float(hours)
                unit = self.time_unit.get()
                if unit == "Minutes":
                    hours_f = hours_f / 60
                if hours_f <= 0:
                    self._field_error(self.hours_entry, "Must be > 0")
                    ok = False
                elif hours_f > 24:
                    self._field_error(self.hours_entry, "Exceeds 24 h/day")
                    ok = False
            except ValueError:
                self._field_error(self.hours_entry, "Must be a number")
                ok = False

        if not ok:
            return

        # Duplicate check
        existing = get_all()
        if name in existing:
            self._field_error(self.name_entry, f"'{name}' already exists")
            return

        add_appliance(name, watts_f, hours_f)

        for e in (self.name_entry, self.watts_entry, self.hours_entry):
            e.delete(0, tk.END)
            # Restore placeholders
            if e._placeholder:
                e.insert(0, e._placeholder)
                e.config(fg=self.T["MUTED"])
                e._has_placeholder = True
            self._field_error(e)

        self.time_unit.set("Hours")
        self._set_status(False)
        self._refresh_output_appliances()
        self._save_session()

    def _remove_all_appliances(self):
        data = get_all()
        if not data:
            Toast(self.root, "No appliances to remove.", "warning")
            return
        if not messagebox.askyesno("Remove All", "Remove all appliances? This cannot be undone."):
            return
        for name in list(data.keys()):
            remove_appliance(name)
        self._refresh_output_appliances()
        self._set_status(False)
        self._save_session()
        Toast(self.root, "All appliances removed.", "success")

    
    def remove(self):
        name = self.remove_var.get().strip()
        if not name or name == "(none)":
            Toast(self.root, "Please select an appliance to remove.", "warning")
            return
        if not messagebox.askyesno("Confirm Remove", f"Remove '{name}' from the list?"):
            return
        remove_appliance(name)
        self._refresh_output_appliances()
        self._set_status(False)
        self._save_session()

    def report(self):
        data = get_all()
        if not data:
            Toast(self.root, "Add at least one appliance first.", "warning")
            return

        results = compute_all(data)
        ranked  = rank_appliances(results)
        self._save_report(ranked)
        self._last_ranked = ranked
        self._last_ranked = ranked

        self._unlock()
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "⚡  ENERGY REPORT\n", "header")
        self.output.insert(tk.END, "─" * 48 + "\n", "divider")

        for i, (name, kwh) in enumerate(ranked, 1):
            medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"  {i}."
            monthly_kwh = kwh * 30
            self.output.insert(tk.END, f"\n{medal}  {name}\n", "name")
            self.output.insert(tk.END, f"     {format_kwh(kwh, 'kWh/day')}  |  {format_kwh(monthly_kwh, 'kWh/month')}\n", "kwh")
            self.output.insert(tk.END,
                f"     ↳ {generate_recommendation(name, monthly_kwh)}\n", "rec")

        self.output.insert(tk.END, "\n" + "─" * 48 + "\n", "divider")
        insight = generate_overall_insight(ranked)
        self.output.insert(tk.END, f"\n💡  {insight}\n", "insight")

        total   = sum(kwh for _, kwh in ranked)
        monthly = total * 30

        self.output.insert(tk.END, f"    Daily Total   : {format_kwh(total, 'kWh/day')}\n", "section")
        self.output.insert(tk.END, f"    Monthly Est.  : {format_kwh(monthly, 'kWh/month')}\n", "section")

        rate_str = self.rate_entry.get().strip()
        if rate_str:
            try:
                rate = float(rate_str)
                if rate > 0:
                    bill = monthly * rate
                    self.output.insert(tk.END, f"    Est. Bill     : ₱{bill:,.2f}/month\n", "section")
                    self.output.insert(tk.END, f"    Rate Used     : ₱{rate:.4f}/kWh\n", "section")
                else:
                    self.output.insert(tk.END, "    Est. Bill     : (rate must be > 0)\n", "warning")
            except ValueError:
                self.output.insert(tk.END, "    Est. Bill     : (invalid rate entered)\n", "warning")

        self._lock()
        self._set_status(True)
        self._chart_data = ranked
        self._redraw_chart()

    # ── Compare ───────────────────────────────────────────────────────────────
    def compare_reports(self):
        if len(self.report_history) < 2:
            Toast(self.root, "Generate at least two reports before comparing.", "warning")
            return

        def resolve(var):
            val = var.get()
            for i, rpt in enumerate(self.report_history):
                if rpt.get("label") == val:
                    return i
            if val.startswith("["):
                try:
                    idx = int(val.split("]")[0][1:]) - 1
                    if 0 <= idx < len(self.report_history):
                        return idx
                except ValueError:
                    pass
            return None

        idx_a = resolve(self.cmp_a_var)
        idx_b = resolve(self.cmp_b_var)

        if idx_a is None or idx_b is None:
            Toast(self.root, "Please select both Report A and Report B.", "warning")
            return
        if idx_a == idx_b:
            Toast(self.root, "Please select two different reports to compare.", "warning")
            return

        rpt_a  = self.report_history[idx_a]
        rpt_b  = self.report_history[idx_b]
        dict_a = dict(rpt_a["ranked"])
        dict_b = dict(rpt_b["ranked"])
        all_names = sorted(set(dict_a) | set(dict_b))

        self.cmp_output.config(state="normal")
        self.cmp_output.delete("1.0", tk.END)

        label_a = rpt_a.get("label") or f"[{idx_a+1}] {rpt_a['timestamp']}"
        label_b = rpt_b.get("label") or f"[{idx_b+1}] {rpt_b['timestamp']}"

        self.cmp_output.insert(tk.END, "Report A\n", "head")
        self.cmp_output.insert(tk.END, f"  {label_a}\n", "label")
        self.cmp_output.insert(tk.END, "Report B\n", "head")
        self.cmp_output.insert(tk.END, f"  {label_b}\n", "label")
        self.cmp_output.insert(tk.END, "─" * 30 + "\n\n", "divider")

        suggestions   = []
        commendations = []

        for name in all_names:
            a = dict_a.get(name)
            b = dict_b.get(name)
            if a is None:
                self.cmp_output.insert(tk.END, f"＋ {name}\n", "better")
                self.cmp_output.insert(tk.END,
                    f"   NEW in B → {format_kwh(b, 'kWh/day')} ({format_kwh(b * 30, 'kWh/month')})\n\n", "better")
            elif b is None:
                self.cmp_output.insert(tk.END, f"－ {name}\n", "worse")
                self.cmp_output.insert(tk.END,
                    f"   {format_kwh(a, 'kWh/day')} ({format_kwh(a * 30, 'kWh/month')}) in A  →  Removed in B\n\n", "same")
            else:
                diff = b - a
                pct  = (diff / a * 100) if a else 0
                sign = "▲" if diff > 0 else ("▼" if diff < 0 else "=")
                tag  = "worse" if diff > 0 else ("better" if diff < 0 else "same")
                self.cmp_output.insert(tk.END, f"  {name}\n", "head")
                self.cmp_output.insert(tk.END,
                    f"   A: {format_kwh(a, 'kWh/day')} ({format_kwh(a * 30, 'kWh/month')})"
                    f"  →  B: {format_kwh(b, 'kWh/day')} ({format_kwh(b * 30, 'kWh/month')})"
                    f"  ({sign} {abs(pct):.1f}%)\n\n", tag)
                if diff > 0 and pct > 10:
                    suggestions.append((name, pct, b))
                elif diff < 0 and abs(pct) > 10:
                    commendations.append((name, abs(pct), b))

        total_a    = sum(dict_a.values())
        total_b    = sum(dict_b.values())
        total_diff = total_b - total_a
        total_pct  = (total_diff / total_a * 100) if total_a else 0
        total_tag  = "worse" if total_diff > 0 else "better"

        self.cmp_output.insert(tk.END, "─" * 30 + "\n", "divider")
        self.cmp_output.insert(tk.END, "OVERALL TOTALS\n", "head")
        self.cmp_output.insert(tk.END,
            f"   A: {format_kwh(total_a, 'kWh/day')} ({format_kwh(total_a * 30, 'kWh/month')})"
            f"  →  B: {format_kwh(total_b, 'kWh/day')} ({format_kwh(total_b * 30, 'kWh/month')})\n", total_tag)
        sign = "▲" if total_diff > 0 else "▼"
        self.cmp_output.insert(tk.END,
            f"   {sign} {abs(total_pct):.1f}% overall change\n\n", total_tag)

        if commendations:
            self.cmp_output.insert(tk.END, "🌟  COMMENDATIONS\n", "head")
            for cname, cpct, _ in commendations:
                self.cmp_output.insert(tk.END,
                    f"  ✓ {cname} dropped {cpct:.0f}% — excellent progress!\n", "praise")
            self.cmp_output.insert(tk.END, "\n", "same")

        if suggestions:
            self.cmp_output.insert(tk.END, "💡  ENERGY-SAVING SUGGESTIONS\n", "head")
            for sname, spct, skwh in suggestions:
                tip = self._generate_comparison_tip(sname, spct, skwh)
                self.cmp_output.insert(tk.END, f"  • {tip}\n", "suggest")
            self.cmp_output.insert(tk.END, "\n", "same")

        if total_diff > 0:
            verdict = (f"⚠  Energy use increased {abs(total_pct):.1f}% from A to B. "
                       "Review high-usage appliances and reduce idle hours.")
            vtag = "worse"
        elif total_diff < 0:
            verdict = (f"✅  Energy use decreased {abs(total_pct):.1f}% from A to B. "
                       "Keep up the efficient habits!")
            vtag = "better"
        else:
            verdict = "= Usage is unchanged between the two reports."
            vtag = "same"

        self.cmp_output.insert(tk.END, "─" * 30 + "\n", "divider")
        self.cmp_output.insert(tk.END, f"{verdict}\n", vtag)
        self.cmp_output.config(state="disabled")

    @staticmethod
    def _generate_comparison_tip(name, pct, kwh):
        name_l = name.lower()
        if "air con" in name_l or "aircon" in name_l or "ac" in name_l:
            return (f"{name} rose {pct:.0f}% — raise the thermostat by 1–2 °C "
                    "or reduce run-time during cooler hours.")
        if "tv" in name_l or "television" in name_l:
            return (f"{name} rose {pct:.0f}% — enable auto-sleep mode "
                    "and avoid leaving it on standby.")
        if "ref" in name_l or "fridge" in name_l or "refriger" in name_l:
            return (f"{name} rose {pct:.0f}% — check door seals and "
                    "ensure the coils are clean for optimal efficiency.")
        if "wash" in name_l:
            return (f"{name} rose {pct:.0f}% — switch to cold-water wash cycles "
                    "and run only with full loads.")
        if "light" in name_l or "lamp" in name_l or "bulb" in name_l:
            return (f"{name} rose {pct:.0f}% — replace with LED equivalents "
                    "and use motion sensors or timers.")
        if "computer" in name_l or "pc" in name_l or "laptop" in name_l:
            return (f"{name} rose {pct:.0f}% — enable hibernate/sleep after "
                    "5–10 minutes of inactivity.")
        if "heater" in name_l or "iron" in name_l:
            return (f"{name} rose {pct:.0f}% — batch tasks to minimise total "
                    "run-time and unplug when not in use.")
        return (f"{name} usage rose {pct:.0f}% — review daily runtime "
                f"(currently {format_kwh(kwh)}) and reduce where possible.")

   
    def _export_report(self, fmt):
        if not self.report_history:
            Toast(self.root, "Generate at least one report first.", "warning")
            return
        rpt = self.report_history[-1]
        ranked = rpt["ranked"]
        label  = rpt.get("label", rpt["timestamp"])

        if fmt == "txt":
            path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")],
                initialfile=f"KiloWatch_Report.txt",
                title="Export Report as TXT"
            )
            if not path:
                return
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"KiloWatch Energy Report\n")
                f.write(f"Report: {label}\n")
                f.write("=" * 48 + "\n\n")
                for i, (name, kwh) in enumerate(ranked, 1):
                    f.write(f"{i}. {name}\n")
                    f.write(f"   {kwh:.4f} kWh/day  |  {kwh * 30:.4f} kWh/month\n\n")
                total = sum(k for _, k in ranked)
                f.write("=" * 48 + "\n")
                f.write(f"Daily Total  : {total:.4f} kWh/day\n")
                f.write(f"Monthly Est. : {total * 30:.4f} kWh/month\n")
            Toast(self.root, "Report exported as TXT!", "success")

        elif fmt == "csv":
            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"KiloWatch_Report.csv",
                title="Export Report as CSV"
            )
            if not path:
                return
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Rank", "Appliance", "kWh/day", "kWh/month"])
                for i, (name, kwh) in enumerate(ranked, 1):
                    writer.writerow([i, name, f"{kwh:.4f}", f"{kwh * 30:.4f}"])
                total = sum(k for _, k in ranked)
                writer.writerow([])
                writer.writerow(["", "TOTAL", f"{total:.4f}", f"{total * 30:.4f}"])
            Toast(self.root, "Report exported as CSV!", "success")

    def _copy_to_clipboard(self):
        content = self.output.get("1.0", tk.END).strip()
        if not content or content.startswith("Add your appliances"):
            Toast(self.root, "Generate a report first.", "warning")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()
        Toast(self.root, "Report copied to clipboard!", "success")

    # ── What-If Simulator ─────────────────────────────────────────────────────
    def _show_simulator(self):
        if not self._last_ranked:
            Toast(self.root, "Generate a report first, then open the simulator.", "warning")
            return

        self._sim_active = True
        T = self.T

        self._unlock()
        self.output.delete("1.0", tk.END)
        self._lock()

        # Embed a real frame inside the output card's parent
        # We'll place the simulator as a sibling widget using the same card
        if hasattr(self, "_sim_frame") and self._sim_frame.winfo_exists():
            self._sim_frame.destroy()

        # Find the output card frame (parent of self.output)
        out_card_parent = self.output.master.master  # txt_frame → out_card

        self._sim_frame = tk.Frame(out_card_parent, bg=T["CARD"])
        self._sim_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 10))
        out_card_parent.rowconfigure(1, weight=1)

        # ── Header row ────────────────────────────────────────────────────────
        hdr = tk.Frame(self._sim_frame, bg=T["CARD"])
        hdr.pack(fill="x", pady=(4, 8))

        tk.Label(hdr, text="🎛  WHAT-IF SIMULATOR",
                 font=("Segoe UI", 11, "bold"),
                 fg=T["ACCENT2"], bg=T["CARD"]).pack(side="left")

        back_btn = self._btn(hdr, "← Back to Report",
                             T["BTN_CLR"], T["BTN_CLR_FG"],
                             self._close_simulator)
        back_btn.pack(side="right")

        tk.Frame(self._sim_frame, height=1, bg=T["BORDER"]).pack(fill="x", pady=(0, 10))

        # ── Appliance picker ──────────────────────────────────────────────────
        pick_row = tk.Frame(self._sim_frame, bg=T["CARD"])
        pick_row.pack(fill="x", pady=(0, 8))

        tk.Label(pick_row, text="Appliance:",
                 font=("Segoe UI", 9, "bold"),
                 fg=T["MUTED"], bg=T["CARD"]).pack(side="left", padx=(0, 8))

        self._sim_var = tk.StringVar(value=self._last_ranked[0][0])
        sim_menu = tk.OptionMenu(pick_row, self._sim_var,
                                 *[name for name, _ in self._last_ranked],
                                 command=lambda _: self._sim_update())
        self._style_optionmenu(sim_menu, T["ACCENT"])
        sim_menu.pack(side="left", fill="x", expand=True)

        # ── Baseline info ─────────────────────────────────────────────────────
        info_row = tk.Frame(self._sim_frame, bg=T["CARD2"],
                            highlightthickness=1, highlightbackground=T["BORDER"])
        info_row.pack(fill="x", pady=(0, 12), ipady=6)

        self._sim_base_label = tk.Label(
            info_row, text="", font=("Segoe UI", 9),
            fg=T["MUTED"], bg=T["CARD2"], justify="left")
        self._sim_base_label.pack(anchor="w", padx=12, pady=(4, 0))

        # ── Slider ────────────────────────────────────────────────────────────
        slider_hdr = tk.Frame(self._sim_frame, bg=T["CARD"])
        slider_hdr.pack(fill="x")

        tk.Label(slider_hdr, text="Reduce usage by:",
                 font=("Segoe UI", 9, "bold"),
                 fg=T["TEXT"], bg=T["CARD"]).pack(side="left")

        self._sim_pct_label = tk.Label(slider_hdr, text="0%",
                                        font=("Segoe UI", 11, "bold"),
                                        fg=T["ACCENT"], bg=T["CARD"])
        self._sim_pct_label.pack(side="right")

        self._sim_slider = tk.Scale(
            self._sim_frame,
            from_=0, to=100,
            orient="horizontal",
            showvalue=False,
            bg=T["CARD"], fg=T["TEXT"],
            troughcolor=T["CARD2"],
            activebackground=T["ACCENT"],
            highlightthickness=0,
            command=self._sim_on_drag,
            length=300,
            sliderlength=18,
        )
        self._sim_slider.pack(fill="x", pady=(2, 4))

        tick_row = tk.Frame(self._sim_frame, bg=T["CARD"])
        tick_row.pack(fill="x", pady=(0, 10))
        for lbl in ("0%", "25%", "50%", "75%", "100%"):
            tk.Label(tick_row, text=lbl, font=("Segoe UI", 7),
                     fg=T["MUTED"], bg=T["CARD"]).pack(side="left", expand=True)

        tk.Frame(self._sim_frame, height=1, bg=T["BORDER"]).pack(fill="x", pady=(0, 10))

        # ── Results grid ──────────────────────────────────────────────────────
        results_frame = tk.Frame(self._sim_frame, bg=T["CARD"])
        results_frame.pack(fill="x")
        results_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(1, weight=1)
        results_frame.columnconfigure(2, weight=1)

        def _stat_col(parent, col, title, color):
            f = tk.Frame(parent, bg=T["CARD2"],
                         highlightthickness=1, highlightbackground=T["BORDER"])
            f.grid(row=0, column=col, sticky="ew",
                   padx=(0 if col == 0 else 6, 0), ipady=10)
            tk.Label(f, text=title, font=("Segoe UI", 7, "bold"),
                     fg=T["MUTED"], bg=T["CARD2"]).pack(pady=(8, 2))
            val = tk.Label(f, text="—", font=("Segoe UI", 13, "bold"),
                           fg=color, bg=T["CARD2"])
            val.pack()
            sub = tk.Label(f, text="", font=("Segoe UI", 8),
                           fg=T["MUTED"], bg=T["CARD2"])
            sub.pack(pady=(0, 6))
            return val, sub

        self._sim_bill_val,  self._sim_bill_sub  = _stat_col(results_frame, 0, "EST. BILL SAVED",   T["SUCCESS"])
        self._sim_kwh_val,   self._sim_kwh_sub   = _stat_col(results_frame, 1, "kWh SAVED",         T["ACCENT"])
        self._sim_pct_val,   self._sim_pct_sub   = _stat_col(results_frame, 2, "TOTAL REDUCTION",   T["ACCENT3"])

        tk.Frame(self._sim_frame, height=1, bg=T["BORDER"]).pack(fill="x", pady=(12, 6))

        # ── New bill summary ──────────────────────────────────────────────────
        self._sim_summary = tk.Label(
            self._sim_frame, text="",
            font=("Segoe UI", 9), fg=T["TEXT"],
            bg=T["CARD"], justify="left", wraplength=380)
        self._sim_summary.pack(anchor="w", padx=4)

        # Trigger initial render
        self._sim_update()

    def _sim_on_drag(self, val):
        pct = int(float(val))
        self._sim_pct_label.config(text=f"{pct}%")
        self._sim_update()

    def _sim_update(self):
        if not hasattr(self, "_sim_slider"):
            return

        T        = self.T
        name     = self._sim_var.get()
        pct      = self._sim_slider.get()
        ranked   = dict(self._last_ranked)

        if name not in ranked:
            return

        # Rate from entry
        try:
            rate = float(self.rate_entry.get().strip())
            if rate <= 0:
                rate = None
        except (ValueError, AttributeError):
            rate = None

        orig_kwh_day   = ranked[name]
        saved_kwh_day  = orig_kwh_day * (pct / 100)
        new_kwh_day    = orig_kwh_day - saved_kwh_day

        saved_kwh_mon  = saved_kwh_day * 30
        new_kwh_day_total  = sum(
            (kwh - kwh * (pct / 100) if n == name else kwh)
            for n, kwh in self._last_ranked
        )
        total_orig_day = sum(kwh for _, kwh in self._last_ranked)
        total_reduction_pct = ((total_orig_day - new_kwh_day_total) / total_orig_day * 100) if total_orig_day else 0

        # Baseline label
        orig_hours_equiv = orig_kwh_day / (ranked[name] / orig_kwh_day) if orig_kwh_day else 0
        self._sim_base_label.config(
            text=f"  {name}  —  baseline: {orig_kwh_day:.4f} kWh/day  |  {orig_kwh_day * 30:.3f} kWh/month"
        )

        # kWh card
        self._sim_kwh_val.config(text=f"{saved_kwh_day:.4f}")
        self._sim_kwh_sub.config(text=f"kWh/day  |  {saved_kwh_mon:.3f}/month")

        # % reduction card
        self._sim_pct_val.config(text=f"{total_reduction_pct:.1f}%")
        self._sim_pct_sub.config(text="of total household usage")

        # Bill card
        if rate:
            bill_saved = saved_kwh_mon * rate
            new_total_bill = new_kwh_day_total * 30 * rate
            orig_total_bill = total_orig_day * 30 * rate
            self._sim_bill_val.config(text=f"₱{bill_saved:,.2f}")
            self._sim_bill_sub.config(text="saved per month")
            self._sim_summary.config(
                text=(
                    f"If you reduce {name} by {pct}%:\n"
                    f"  • This appliance: {format_kwh(new_kwh_day, 'kWh/day')}  (was {format_kwh(orig_kwh_day, 'kWh/day')})\n"
                    f"  • New household total: {format_kwh(new_kwh_day_total, 'kWh/day')}  |  "
                    f"{format_kwh(new_kwh_day_total * 30, 'kWh/month')}\n"
                    f"  • Est. monthly bill: ₱{new_total_bill:,.2f}  (was ₱{orig_total_bill:,.2f})  →  saving ₱{bill_saved:,.2f}"
                )
            )
        else:
            self._sim_bill_val.config(text="N/A")
            self._sim_bill_sub.config(text="enter ₱/kWh rate")
            self._sim_summary.config(
                text=(
                    f"If you reduce {name} by {pct}%:\n"
                    f"  • This appliance: {format_kwh(new_kwh_day, 'kWh/day')}  (was {format_kwh(orig_kwh_day, 'kWh/day')})\n"
                    f"  • New household total: {format_kwh(new_kwh_day_total, 'kWh/day')}  |  "
                    f"{format_kwh(new_kwh_day_total * 30, 'kWh/month')}\n"
                    f"  • Enter a ₱/kWh rate above to see bill savings."
                )
            )

    def _close_simulator(self):
        self._sim_active = False
        if hasattr(self, "_sim_frame") and self._sim_frame.winfo_exists():
            self._sim_frame.destroy()
        # Restore last report or placeholder
        if self._last_ranked:
            self._unlock()
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, "⚡  ENERGY REPORT\n", "header")
            self.output.insert(tk.END, "─" * 48 + "\n", "divider")
            ranked = self._last_ranked
            for i, (name, kwh) in enumerate(ranked, 1):
                medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"  {i}."
                monthly_kwh = kwh * 30
                self.output.insert(tk.END, f"\n{medal}  {name}\n", "name")
                self.output.insert(tk.END, f"     {format_kwh(kwh, 'kWh/day')}  |  {format_kwh(monthly_kwh, 'kWh/month')}\n", "kwh")
                self.output.insert(tk.END, f"     ↳ {generate_recommendation(name, monthly_kwh)}\n", "rec")
            self.output.insert(tk.END, "\n" + "─" * 48 + "\n", "divider")
            total = sum(kwh for _, kwh in ranked)
            self.output.insert(tk.END, f"    Daily Total   : {format_kwh(total, 'kWh/day')}\n", "section")
            self.output.insert(tk.END, f"    Monthly Est.  : {format_kwh(total * 30, 'kWh/month')}\n", "section")
            self._lock()
        else:
            self._unlock()
            self.output.delete("1.0", tk.END)
            self._write_placeholder()
            self._lock()
# ── What If Window ────────────────────────────────────────────────────────
    def _open_whatif_window(self):
        if not self._last_ranked:
            Toast(self.root, "Generate a report first, then open What If.", "warning")
            return

        T = self.T

        # Prevent duplicate windows
        if hasattr(self, "_whatif_win") and self._whatif_win.winfo_exists():
            self._whatif_win.lift()
            return

        win = tk.Toplevel(self.root)
        self._whatif_win = win
        win.title("💡 What If — KiloWatch")
        win.resizable(True, True)
        win.configure(bg=T["BG"])
        win.attributes("-topmost", True)

        # Center on screen
        win.update_idletasks()
        W, H = 560, 520
        sx = self.root.winfo_screenwidth()
        sy = self.root.winfo_screenheight()
        win.geometry(f"{W}x{H}+{(sx - W)//2}+{(sy - H)//2}")
        win.minsize(480, 420)

        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(win, bg=T["ACCENT2"], pady=0)
        hdr.pack(fill="x")
        tk.Frame(win, height=2, bg=T["ACCENT3"]).pack(fill="x")

        tk.Label(hdr, text="💡  What If…",
                 font=("Segoe UI", 14, "bold"),
                 fg="#ffffff", bg=T["ACCENT2"],
                 pady=12, padx=20).pack(side="left")
        tk.Label(hdr, text="Simulate changing an appliance's daily hours",
                 font=("Segoe UI", 8),
                 fg="#a8c4e0", bg=T["ACCENT2"],
                 padx=20).pack(side="left", anchor="s", pady=(0, 13))

        body = tk.Frame(win, bg=T["BG"], padx=20, pady=16)
        body.pack(fill="both", expand=True)

        # ── Appliance picker ──────────────────────────────────────────────────
        tk.Label(body, text="APPLIANCE", font=("Segoe UI", 7, "bold"),
                 fg=T["MUTED"], bg=T["BG"]).pack(anchor="w")

        self._wi_var = tk.StringVar(value=self._last_ranked[0][0])
        pick_frame = tk.Frame(body, bg=T["BG"])
        pick_frame.pack(fill="x", pady=(2, 14))

        wi_menu = tk.OptionMenu(pick_frame, self._wi_var,
                                *[name for name, _ in self._last_ranked],
                                command=lambda _: self._wi_on_appliance_change())
        self._style_optionmenu(wi_menu, T["ACCENT"])
        wi_menu.pack(fill="x", ipady=4)

        # ── Baseline info bar ─────────────────────────────────────────────────
        info_card = tk.Frame(body, bg=T["CARD"],
                             highlightthickness=1,
                             highlightbackground=T["BORDER"])
        info_card.pack(fill="x", pady=(0, 14))

        self._wi_info = tk.Label(
            info_card, text="",
            font=("Segoe UI", 9), fg=T["MUTED"],
            bg=T["CARD"], justify="left", padx=14, pady=8)
        self._wi_info.pack(anchor="w")

        # ── Slider ────────────────────────────────────────────────────────────
        slider_hdr = tk.Frame(body, bg=T["BG"])
        slider_hdr.pack(fill="x")

        tk.Label(slider_hdr, text="HOURS PER DAY",
                 font=("Segoe UI", 7, "bold"),
                 fg=T["MUTED"], bg=T["BG"]).pack(side="left")

        self._wi_hr_label = tk.Label(slider_hdr, text="0 h/day",
                                     font=("Segoe UI", 12, "bold"),
                                     fg=T["ACCENT"], bg=T["BG"])
        self._wi_hr_label.pack(side="right")

        self._wi_slider = tk.Scale(
            body,
            from_=0.5, to=24,
            resolution=0.5,
            orient="horizontal",
            showvalue=False,
            bg=T["BG"], fg=T["TEXT"],
            troughcolor=T["CARD2"],
            activebackground=T["ACCENT"],
            highlightthickness=0,
            command=self._wi_on_drag,
            length=440,
            sliderlength=20,
        )
        self._wi_slider.pack(fill="x", pady=(4, 2))

        # Min / max tick labels
        tick_row = tk.Frame(body, bg=T["BG"])
        tick_row.pack(fill="x", pady=(0, 14))
        tk.Label(tick_row, text="0.5 h", font=("Segoe UI", 7),
                 fg=T["MUTED"], bg=T["BG"]).pack(side="left")
        tk.Label(tick_row, text="Max", font=("Segoe UI", 7),
                 fg=T["MUTED"], bg=T["BG"]).pack(side="right")

        tk.Frame(body, height=1, bg=T["BORDER"]).pack(fill="x", pady=(0, 14))

        # ── Results row ───────────────────────────────────────────────────────
        res = tk.Frame(body, bg=T["BG"])
        res.pack(fill="x", pady=(0, 14))
        res.columnconfigure(0, weight=1)
        res.columnconfigure(1, weight=1)
        res.columnconfigure(2, weight=1)

        def _stat(parent, col, title, color):
            f = tk.Frame(parent, bg=T["CARD"],
                         highlightthickness=1,
                         highlightbackground=T["BORDER"])
            f.grid(row=0, column=col, sticky="ew",
                   padx=(0 if col == 0 else 8, 0), ipady=8)
            tk.Label(f, text=title, font=("Segoe UI", 7, "bold"),
                     fg=T["MUTED"], bg=T["CARD"]).pack(pady=(8, 2))
            val = tk.Label(f, text="—", font=("Segoe UI", 12, "bold"),
                           fg=color, bg=T["CARD"])
            val.pack()
            sub = tk.Label(f, text="", font=("Segoe UI", 8),
                           fg=T["MUTED"], bg=T["CARD"])
            sub.pack(pady=(0, 6))
            return val, sub

        self._wi_kwh_val, self._wi_kwh_sub   = _stat(res, 0, "kWh SAVED",       T["ACCENT"])
        self._wi_bill_val, self._wi_bill_sub  = _stat(res, 1, "BILL SAVED",      T["SUCCESS"])
        self._wi_new_val, self._wi_new_sub    = _stat(res, 2, "NEW DAILY TOTAL", T["ACCENT3"])

        # ── Summary line ──────────────────────────────────────────────────────
        self._wi_summary = tk.Label(
            body, text="", font=("Segoe UI", 9),
            fg=T["TEXT"], bg=T["BG"],
            justify="left", wraplength=440)
        self._wi_summary.pack(anchor="w")

        # Trigger first render with current appliance's actual hours
        self._wi_on_appliance_change()

    def _wi_on_appliance_change(self):
        """Called when user picks a different appliance — resets slider to current hours."""
        name = self._wi_var.get()
        data = get_all()
        info = data.get(name, {})
        current_hours = info.get("hours", 1.0)
        current_hours = max(0.5, min(24.0, round(current_hours * 2) / 2))  # snap to 0.5 grid

        # Update baseline info
        ranked_dict = dict(self._last_ranked)
        kwh_day = ranked_dict.get(name, 0)
        self._wi_info.config(
            text=f"Current: {current_hours} h/day  ·  "
                 f"{kwh_day:.4f} kWh/day  ·  {kwh_day * 30:.3f} kWh/month"
        )

        # Reset slider to their actual current hours
        self._wi_slider.config(to=max(current_hours, 0.5))
        self._wi_slider.set(current_hours)
        self._wi_hr_label.config(text=f"{current_hours} h/day")
        self._wi_update(current_hours)

    def _wi_on_drag(self, val):
        hrs = float(val)
        self._wi_hr_label.config(text=f"{hrs:.1f} h/day")
        self._wi_update(hrs)

    def _wi_update(self, new_hours):
        T           = self.T
        name        = self._wi_var.get()
        data        = get_all()
        info        = data.get(name, {})
        watts       = info.get("watts", 0)
        orig_hours  = info.get("hours", 1.0)
        ranked_dict = dict(self._last_ranked)

        orig_kwh_day = ranked_dict.get(name, 0)
        new_kwh_day  = (watts * new_hours) / 1000
        saved_kwh_day = orig_kwh_day - new_kwh_day
        saved_kwh_mon = saved_kwh_day * 30

        total_orig  = sum(kwh for _, kwh in self._last_ranked)
        total_new   = total_orig - orig_kwh_day + new_kwh_day

        # Rate
        try:
            rate = float(self.rate_entry.get().strip())
            rate = rate if rate > 0 else None
        except (ValueError, AttributeError):
            rate = None

        # kWh card
        if saved_kwh_day >= 0:
            self._wi_kwh_val.config(text=f"{saved_kwh_day:.4f}",
                                    fg=T["SUCCESS"] if saved_kwh_day > 0 else T["MUTED"])
            self._wi_kwh_sub.config(text=f"kWh/day  ·  {saved_kwh_mon:.3f}/month")
        else:
            # new_hours > orig → using MORE
            self._wi_kwh_val.config(text=f"+{abs(saved_kwh_day):.4f}",
                                    fg=T["DANGER"])
            self._wi_kwh_sub.config(text=f"kWh/day extra  ·  {abs(saved_kwh_mon):.3f}/month")

        # New daily total card
        self._wi_new_val.config(text=f"{total_new:.4f}")
        self._wi_new_sub.config(text="kWh/day total")

        # Bill card
        if rate:
            bill_saved = saved_kwh_mon * rate
            new_bill   = total_new * 30 * rate
            orig_bill  = total_orig * 30 * rate
            if bill_saved >= 0:
                self._wi_bill_val.config(
                    text=f"₱{bill_saved:,.2f}",
                    fg=T["SUCCESS"])
                self._wi_bill_sub.config(text="saved per month")
            else:
                self._wi_bill_val.config(
                    text=f"−₱{abs(bill_saved):,.2f}",
                    fg=T["DANGER"])
                self._wi_bill_sub.config(text="extra per month")

            hrs_diff = orig_hours - new_hours
            dir_word = "Reducing" if hrs_diff > 0 else "Increasing"
            hrs_abs  = abs(hrs_diff)
            self._wi_summary.config(
                text=(
                    f"{dir_word} {name} by {hrs_abs:.1f} h/day:\n"
                    f"  New usage: {new_kwh_day:.4f} kWh/day  "
                    f"(was {orig_kwh_day:.4f})  ·  "
                    f"New bill: ₱{new_bill:,.2f}/month  (was ₱{orig_bill:,.2f})"
                )
            )
        else:
            self._wi_bill_val.config(text="N/A", fg=T["MUTED"])
            self._wi_bill_sub.config(text="enter ₱/kWh rate")
            hrs_diff = orig_hours - new_hours
            dir_word = "Reducing" if hrs_diff >= 0 else "Increasing"
            hrs_abs  = abs(hrs_diff)
            self._wi_summary.config(
                text=(
                    f"{dir_word} {name} by {hrs_abs:.1f} h/day:\n"
                    f"  New usage: {new_kwh_day:.4f} kWh/day  "
                    f"(was {orig_kwh_day:.4f})  ·  "
                    f"Enter a ₱/kWh rate to see bill savings."
                )
            )


    def _open_goal_tracker(self):
        T = self.T
        if hasattr(self, "_goal_win") and self._goal_win.winfo_exists():
            self._goal_win.lift()
            return

        win = tk.Toplevel(self.root)
        self._goal_win = win
        win.title("🎯 Goal Tracker — KiloWatch")
        win.resizable(True, True)
        win.configure(bg=T["BG"])
        win.attributes("-topmost", True)

        W, H = 420, 540
        sx = self.root.winfo_screenwidth()
        sy = self.root.winfo_screenheight()
        win.geometry(f"{W}x{H}+{(sx - W)//2}+{(sy - H)//2}")
        win.minsize(380, 480)

        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(win, bg=T["ACCENT2"])
        hdr.pack(fill="x")
        tk.Frame(win, height=2, bg=T["ACCENT3"]).pack(fill="x")
        tk.Label(hdr, text="🎯  Goal Tracker",
                 font=("Segoe UI", 14, "bold"),
                 fg="#ffffff", bg=T["ACCENT2"],
                 pady=12, padx=20).pack(side="left")
        tk.Label(hdr, text="Set a monthly target and track your progress",
                 font=("Segoe UI", 8),
                 fg="#a8c4e0", bg=T["ACCENT2"],
                 padx=20).pack(side="left", anchor="s", pady=(0, 13))

        body = tk.Frame(win, bg=T["BG"], padx=24, pady=20)
        body.pack(fill="both", expand=True)

        # ── Mode toggle ───────────────────────────────────────────────────────
        tk.Label(body, text="TRACK BY", font=("Segoe UI", 7, "bold"),
                 fg=T["MUTED"], bg=T["BG"]).pack(anchor="w")

        mode_row = tk.Frame(body, bg=T["BG"])
        mode_row.pack(fill="x", pady=(4, 16))

        self._goal_mode_var = tk.StringVar(value=self._goal_mode)

        def _set_mode(m):
            self._goal_mode = m
            self._goal_mode_var.set(m)
            self._goal_refresh_gauge()

        for val, lbl in (("kwh", "Monthly kWh"), ("bill", "Monthly Bill (₱)")):
            rb = tk.Radiobutton(
                mode_row, text=lbl,
                variable=self._goal_mode_var, value=val,
                font=("Segoe UI", 10, "bold"),
                bg=T["BG"], fg=T["TEXT"],
                selectcolor=T["CARD2"],
                activebackground=T["BG"],
                relief="flat", bd=0,
                command=lambda m=val: _set_mode(m)
            )
            rb.pack(side="left", padx=(0, 20))

        # ── Target input ──────────────────────────────────────────────────────
        tk.Label(body, text="SET TARGET", font=("Segoe UI", 7, "bold"),
                 fg=T["MUTED"], bg=T["BG"]).pack(anchor="w")

        input_row = tk.Frame(body, bg=T["BG"])
        input_row.pack(fill="x", pady=(4, 20))

        self._goal_entry = tk.Entry(
            input_row, font=("Segoe UI", 12),
            bg=T["CARD"], fg=T["TEXT"],
            insertbackground=T["ACCENT"],
            relief="flat", bd=0, width=12,
            highlightthickness=1,
            highlightbackground=T["BORDER"],
            highlightcolor=T["ACCENT"],
        )
        self._goal_entry.pack(side="left", ipady=8, padx=(0, 10))

        cur_val = self._goal_kwh.get() if self._goal_mode == "kwh" else self._goal_bill.get()
        if cur_val > 0:
            self._goal_entry.insert(0, str(cur_val))

        set_btn = self._btn(input_row, "Set Goal",
                            T["BTN_ADD"], T["BTN_ADD_FG"],
                            self._goal_apply)
        set_btn.pack(side="left")

        # ── Circular gauge canvas ─────────────────────────────────────────────
        gauge_frame = tk.Frame(body, bg=T["BG"])
        gauge_frame.pack(pady=(0, 16))

        self._gauge_canvas = tk.Canvas(
            gauge_frame, width=240, height=240,
            bg=T["BG"], highlightthickness=0
        )
        self._gauge_canvas.pack()
        self._gauge_canvas.update_idletasks()

        # ── Status text below gauge ───────────────────────────────────────────
        self._goal_status = tk.Label(
            body, text="", font=("Segoe UI", 10),
            fg=T["MUTED"], bg=T["BG"], justify="center"
        )
        self._goal_status.pack()

        self._goal_tip = tk.Label(
            body, text="", font=("Segoe UI", 9, "italic"),
            fg=T["ACCENT3"], bg=T["BG"],
            wraplength=360, justify="center"
        )
        self._goal_tip.pack(pady=(6, 0))

        self._goal_refresh_gauge()

    def _goal_apply(self):
        try:
            val = float(self._goal_entry.get().strip())
            if val <= 0:
                Toast(self.root, "Target must be greater than 0.", "warning")
                return
        except ValueError:
            Toast(self.root, "Please enter a valid number.", "error")
            return

        if self._goal_mode == "kwh":
            self._goal_kwh.set(val)
        else:
            self._goal_bill.set(val)

        self._goal_refresh_gauge()
        Toast(self.root, "Goal updated!", "success")

    def _goal_get_current(self):
        """Return (current_kwh_month, current_bill_month) from live appliance data."""
        data = get_all()
        if not data:
            return 0.0, 0.0
        results = compute_all(data)
        total_day = sum(v for v in results.values())
        total_month = total_day * 30
        try:
            rate = float(self.rate_entry.get().strip())
            rate = rate if rate > 0 else 0.0
        except (ValueError, AttributeError):
            rate = 0.0
        return total_month, total_month * rate

    def _goal_refresh_gauge(self):
        if not hasattr(self, "_gauge_canvas") or not self._gauge_canvas.winfo_exists():
            return

        T = self.T
        c = self._gauge_canvas
        c.update_idletasks()
        c.delete("all")

        W      = 240
        H      = 240
        cx     = 120
        cy     = 120
        r_out  = 95
        r_in   = 63
        start  = 220
        total  = 280

        current_kwh, current_bill = self._goal_get_current()

        if self._goal_mode == "kwh":
            target  = self._goal_kwh.get()
            current = current_kwh
            unit    = "kWh"
            fmt     = f"{current:.2f} / {target:.1f} kWh"
        else:
            target  = self._goal_bill.get()
            current = current_bill
            unit    = "₱"
            fmt     = f"₱{current:,.2f} / ₱{target:,.2f}"

        pct = min((current / target) if target > 0 else 0, 1.0)

        # Color based on % used
        if pct < 0.6:
            bar_color = T["SUCCESS"]
        elif pct < 0.85:
            bar_color = T["ACCENT3"]
        else:
            bar_color = T["DANGER"]

        # Background track arc
        c.create_arc(
            cx - r_out, cy - r_out, cx + r_out, cy + r_out,
            start=-(start - total + 360), extent=total,
            style="arc", outline=T["BORDER"], width=20
        )

        # Filled arc
        if pct > 0:
            sweep = total * pct
            c.create_arc(
                cx - r_out, cy - r_out, cx + r_out, cy + r_out,
                start=-start, extent=sweep,
                style="arc", outline=bar_color, width=20
            )

        # Inner circle fill
        c.create_oval(
            cx - r_in, cy - r_in, cx + r_in, cy + r_in,
            fill=T["CARD"], outline=T["BORDER"]
        )

        # Centre % text
        pct_text = f"{int(pct * 100)}%"
        c.create_text(cx, cy - 14, text=pct_text,
                      font=("Segoe UI", 28, "bold"),
                      fill=bar_color)
        c.create_text(cx, cy + 16, text="used",
                      font=("Segoe UI", 9),
                      fill=T["MUTED"])
        c.create_text(cx, cy + 34, text=fmt,
                      font=("Segoe UI", 8),
                      fill=T["MUTED"])

        # Status label
        if target <= 0:
            status = "Set a target above to begin tracking."
            tip    = ""
        elif pct >= 1.0:
            status = "⚠  You've exceeded your monthly target!"
            tip    = "Consider reducing high-usage appliances or raising your target."
        elif pct >= 0.85:
            status = "⚡  Approaching your limit — use wisely."
            tip    = "You're close to your goal. Check the What If tool to simulate reductions."
        elif pct >= 0.6:
            status = "📊  On track — moderate usage."
            tip    = "Good progress. Keep an eye on high-ranked appliances."
        else:
            status = "✅  Well within your target!"
            tip    = "Great efficiency! You have plenty of headroom this month."

        self._goal_status.config(text=status, fg=bar_color if target > 0 else T["MUTED"])
        self._goal_tip.config(text=tip)

        # Schedule live refresh every 2 seconds
        if self._gauge_canvas.winfo_exists():
            self._gauge_canvas.after(2000, self._goal_refresh_gauge)

    def clear_output(self):
        self._unlock()
        self.output.delete("1.0", tk.END)
        self._write_placeholder()
        self._set_status(False)
        self._chart_data = []
        self._redraw_chart()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = KiloWatchApp(root)
    root.mainloop()