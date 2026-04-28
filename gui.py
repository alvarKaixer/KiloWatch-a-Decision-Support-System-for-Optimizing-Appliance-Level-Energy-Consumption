import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import datetime
from data_manager import add_appliance, get_all, remove_appliance
from logic import compute_all, rank_appliances
from utils import format_kwh, generate_recommendation, generate_overall_insight

# ══════════════════════════════════════════════════════════════════════════════
#  THEME DEFINITIONS  — Refined, high-contrast palettes
# ══════════════════════════════════════════════════════════════════════════════

THEMES = {
    "light": {
        # Backgrounds
        "BG":           "#f0f4f8",   # cool slate-grey page bg
        "CARD":         "#ffffff",   # pure white cards
        "CARD2":        "#f0f4f8",   # input field fill
        "HOME_BG":      "#0f1c2e",   # deep navy for home
        "HOME_CARD":    "#1a2d45",   # slightly lighter navy card

        # Borders / dividers
        "BORDER":       "#d1dde9",

        # Brand accents
        "ACCENT":       "#1a6fc4",   # strong blue — interactive
        "ACCENT2":      "#0d4f91",   # darker blue — headers
        "ACCENT3":      "#f5a623",   # warm amber — highlight / CTA

        # Text
        "TEXT":         "#0d1b2a",   # near-black — always readable on white
        "TEXT_ON_DARK": "#f0f4f8",   # near-white — for text on dark/navy bg
        "MUTED":        "#5a7a99",   # medium slate — secondary text on cards
        "MUTED_DARK":   "#8bafc9",   # lighter muted — secondary text on dark bg

        # Semantic
        "DANGER":       "#c0392b",
        "SUCCESS":      "#1a7a3e",
        "GOLD":         "#ffa200",
        "WARNING":      "#ff9900",

        # Buttons — each has enough contrast against CARD white
        "BTN_ADD":      "#1a6fc4",   # blue
        "BTN_ADD_FG":   "#ffffff",
        "BTN_REP":      "#0d4f91",   # deep blue
        "BTN_REP_FG":   "#ffffff",
        "BTN_CLR":      "#6b7e8f",   # neutral slate
        "BTN_CLR_FG":   "#ffffff",
        "BTN_HIST":     "#6b3fa0",   # purple
        "BTN_HIST_FG":  "#ffffff",
        "BTN_CMP":      "#ffc400",   # deep amber
        "BTN_CMP_FG":   "#ffffff",
        "BTN_HOME":     "#1a2d45",   # navy — readable on any bg
        "BTN_HOME_FG":  "#f0f4f8",
        "BTN_THEME":    "#f5a623",   # amber CTA
        "BTN_THEME_FG": "#0d1b2a",
        "BTN_REMOVE":   "#c0392b",
        "BTN_REMOVE_FG":"#ffffff",
    },

    "dark": {
        # Backgrounds
        "BG":           "#0d1117",   # true near-black
        "CARD":         "#161b22",   # GitHub-dark-style card
        "CARD2":        "#0d1117",   # input fill = page bg
        "HOME_BG":      "#080c12",   # deepest dark for home
        "HOME_CARD":    "#0f1620",   # home feature cards

        # Borders / dividers
        "BORDER":       "#2a3a4e",

        # Brand accents
        "ACCENT":       "#4da3ff",   # bright sky-blue — visible on dark
        "ACCENT2":      "#7ec8ff",   # lighter blue — for secondary highlights
        "ACCENT3":      "#fbbf24",   # amber — consistent brand highlight

        # Text
        "TEXT":         "#e6edf3",   # near-white — always readable on dark
        "TEXT_ON_DARK": "#e6edf3",   # same — dark mode is already dark bg
        "MUTED":        "#7d9ab5",   # muted blue-grey — secondary on dark cards
        "MUTED_DARK":   "#7d9ab5",   # same

        # Semantic
        "DANGER":       "#f87171",   # bright red — visible on dark
        "SUCCESS":      "#4ade80",   # bright green — visible on dark
        "GOLD":         "#fbbf24",
        "WARNING":      "#fb923c",

        # Buttons — all have light fg for contrast on dark surfaces
        "BTN_ADD":      "#1d5fa8",
        "BTN_ADD_FG":   "#e6edf3",
        "BTN_REP":      "#14477d",
        "BTN_REP_FG":   "#e6edf3",
        "BTN_CLR":      "#2a3a4e",
        "BTN_CLR_FG":   "#a8c4d8",
        "BTN_HIST":     "#4a2d80",
        "BTN_HIST_FG":  "#e6edf3",
        "BTN_CMP":      "#ffe601",
        "BTN_CMP_FG":   "#e6edf3",
        "BTN_HOME":     "#1e3a5a",   # visible dark-blue, NOT black
        "BTN_HOME_FG":  "#e6edf3",
        "BTN_THEME":    "#fbbf24",
        "BTN_THEME_FG": "#0d1117",
        "BTN_REMOVE":   "#a02020",
        "BTN_REMOVE_FG":"#e6edf3",
    }
}


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
            ("💡", "Get Suggestions", "AI-powered tips to cut\nyour electricity bill"),
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
                 text="Capstone Research Project  •  Energy Monitoring System",
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
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=1)

        left = tk.Frame(body, bg=T["BG"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        left.rowconfigure(2, weight=1)
        left.columnconfigure(0, weight=1)

        self._build_input_card(left)
        self._build_action_buttons(left)
        self._build_output_card(left)
        self._build_history_panel(body)

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
    def _build_input_card(self, parent):
        T = self.T
        card = self._card(parent)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self._section_label(card, "ADD APPLIANCE", T["ACCENT"])

        fields = tk.Frame(card, bg=T["CARD"])
        fields.pack(fill="x", padx=16, pady=(0, 10))
        fields.columnconfigure(0, weight=1)
        fields.columnconfigure(1, weight=1)
        fields.columnconfigure(2, weight=1)

        self.name_entry  = self._field(fields, "Appliance Name", col=0)
        self.watts_entry = self._field(fields, "Watts (W)",      col=1)
        self.hours_entry = self._field(fields, "Hours / Day",    col=2)

        self._btn(card, "＋  Add Appliance",
                  T["BTN_ADD"], T["BTN_ADD_FG"],
                  self.add).pack(fill="x", padx=16, pady=(0, 12))

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

    # ── Action Buttons ────────────────────────────────────────────────────────
    def _build_action_buttons(self, parent):
        T = self.T
        row = tk.Frame(parent, bg=T["BG"])
        row.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)

        self._btn(row, "⚡  Generate Report",
                  T["BTN_REP"], T["BTN_REP_FG"],
                  self.report).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._btn(row, "✕  Clear Output",
                  T["BTN_CLR"], T["BTN_CLR_FG"],
                  self.clear_output).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    # ── Output Card ───────────────────────────────────────────────────────────
    def _build_output_card(self, parent):
        T = self.T
        out_card = self._card(parent)
        out_card.grid(row=2, column=0, sticky="nsew")
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

        parent.rowconfigure(2, weight=1)
        self._write_placeholder()

    # ── History Panel (right) ─────────────────────────────────────────────────
    def _build_history_panel(self, parent):
        T = self.T
        panel = self._card(parent)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.rowconfigure(5, weight=1)
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

        self._btn(panel, "✎  Rename Selected Entry",
                  T["BTN_HIST"], T["BTN_HIST_FG"],
                  self._rename_history_entry).grid(
            row=2, column=0, sticky="ew", padx=12, pady=(4, 8))

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
            row=4, column=0, sticky="ew", padx=12, pady=(8, 4))

        tk.Frame(panel, height=1, bg=T["BORDER"]).grid(
            row=5, column=0, sticky="ew", padx=16)
        tk.Label(panel, text="COMPARISON RESULTS", font=self.f_small,
                 fg=T["BTN_HIST"], bg=T["CARD"]).grid(
            row=5, column=0, sticky="w", padx=16, pady=(8, 2))

        cmp_frame = tk.Frame(panel, bg=T["CARD"])
        cmp_frame.grid(row=6, column=0, sticky="nsew", padx=12, pady=(0, 12))
        cmp_frame.rowconfigure(0, weight=1)
        cmp_frame.columnconfigure(0, weight=1)
        panel.rowconfigure(6, weight=1)

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

    def _field(self, parent, placeholder, col):
        T = self.T
        wrapper = tk.Frame(parent, bg=T["CARD"])
        wrapper.grid(row=0, column=col, sticky="ew",
                     padx=(0 if col == 0 else 6, 0))
        tk.Label(wrapper, text=placeholder.upper(), font=("Segoe UI", 7, "bold"),
                 fg=T["MUTED"], bg=T["CARD"]).pack(anchor="w")
        entry = tk.Entry(
            wrapper, font=self.f_entry,
            bg=T["CARD2"], fg=T["TEXT"],
            insertbackground=T["ACCENT"],
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=T["BORDER"],
            highlightcolor=T["ACCENT"],
        )
        entry.pack(fill="x", ipady=6)
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
        default_label = f"[{idx}]  {ts}"
        self.report_history.append({
            "timestamp": ts,
            "ranked":    ranked,
            "label":     default_label,
        })
        self.hist_listbox.insert(tk.END, default_label)
        self.hist_listbox.see(tk.END)
        self._refresh_cmp_menus()

    def _rename_history_entry(self):
        sel = self.hist_listbox.curselection()
        if not sel:
            messagebox.showinfo("No Selection",
                "Click an entry in the Report History list first, then press Rename.")
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
            messagebox.showerror("Empty Name", "Report name cannot be blank.")
            return

        rpt["label"] = new_name
        self.hist_listbox.delete(idx)
        self.hist_listbox.insert(idx, new_name)
        self.hist_listbox.selection_set(idx)
        self._refresh_cmp_menus()

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
    def add(self):
        name  = self.name_entry.get().strip()
        watts = self.watts_entry.get().strip()
        hours = self.hours_entry.get().strip()
        if not name or not watts or not hours:
            messagebox.showerror("Missing Fields", "Please fill in all three fields.")
            return
        try:
            add_appliance(name, float(watts), float(hours))
            for e in (self.name_entry, self.watts_entry, self.hours_entry):
                e.delete(0, tk.END)
            self._set_status(False)
            self._refresh_output_appliances()
        except ValueError:
            messagebox.showerror("Invalid Input", "Watts and Hours must be numbers.")

    def remove(self):
        name = self.remove_var.get().strip()
        if not name or name == "(none)":
            messagebox.showerror("No Selection", "Please select an appliance to remove.")
            return
        if not messagebox.askyesno("Confirm Remove", f"Remove '{name}' from the list?"):
            return
        remove_appliance(name)
        self._refresh_output_appliances()
        self._set_status(False)

    def report(self):
        data = get_all()
        if not data:
            messagebox.showinfo("No Data", "Add at least one appliance first.")
            return

        results = compute_all(data)
        ranked  = rank_appliances(results)
        self._save_report(ranked)

        self._unlock()
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "⚡  ENERGY REPORT\n", "header")
        self.output.insert(tk.END, "─" * 48 + "\n", "divider")

        for i, (name, kwh) in enumerate(ranked, 1):
            medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"  {i}."
            self.output.insert(tk.END, f"\n{medal}  {name}\n", "name")
            self.output.insert(tk.END, f"     {format_kwh(kwh)}\n", "kwh")
            self.output.insert(tk.END,
                f"     ↳ {generate_recommendation(name, kwh)}\n", "rec")

        self.output.insert(tk.END, "\n" + "─" * 48 + "\n", "divider")
        insight = generate_overall_insight(ranked)
        self.output.insert(tk.END, f"\n💡  {insight}\n", "insight")

        total   = sum(kwh for _, kwh in ranked)
        monthly = total * 30
        self.output.insert(tk.END, f"\n📊  Daily Total : {format_kwh(total)}\n", "section")
        self.output.insert(tk.END, f"    Monthly Est. : {format_kwh(monthly)}\n", "section")

        self._lock()
        self._set_status(True)

    # ── Compare ───────────────────────────────────────────────────────────────
    def compare_reports(self):
        if len(self.report_history) < 2:
            messagebox.showinfo("Not Enough Reports",
                "Generate at least two reports before comparing.")
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
            messagebox.showinfo("Select Reports",
                "Please select both Report A and Report B from the drop-downs.")
            return
        if idx_a == idx_b:
            messagebox.showinfo("Same Report",
                "Please select two different reports to compare.")
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
                self.cmp_output.insert(tk.END, f"   NEW in B → {format_kwh(b)}\n\n", "better")
            elif b is None:
                self.cmp_output.insert(tk.END, f"－ {name}\n", "worse")
                self.cmp_output.insert(tk.END,
                    f"   {format_kwh(a)} in A  →  Removed in B\n\n", "same")
            else:
                diff = b - a
                pct  = (diff / a * 100) if a else 0
                sign = "▲" if diff > 0 else ("▼" if diff < 0 else "=")
                tag  = "worse" if diff > 0 else ("better" if diff < 0 else "same")
                self.cmp_output.insert(tk.END, f"  {name}\n", "head")
                self.cmp_output.insert(tk.END,
                    f"   A: {format_kwh(a)}  →  B: {format_kwh(b)}  "
                    f"({sign} {abs(pct):.1f}%)\n\n", tag)
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
            f"   A: {format_kwh(total_a)}  →  B: {format_kwh(total_b)}\n", total_tag)
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

    def clear_output(self):
        self._unlock()
        self.output.delete("1.0", tk.END)
        self._write_placeholder()
        self._set_status(False)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = KiloWatchApp(root)
    root.mainloop()