import tkinter as tk
from auth import login, register


# ══════════════════════════════════════════════════════════════════════════════
#  THEMES
# ══════════════════════════════════════════════════════════════════════════════
THEMES = {
    "light": {
        "BG":           "#f0f4f8",
        "CARD":         "#ffffff",
        "CARD2":        "#f5f7fa",
        "HOME_BG":      "#0f1c2e",
        "BORDER":       "#e2e8f0",
        "ACCENT":       "#2563eb",
        "ACCENT2":      "#1e40af",
        "ACCENT3":      "#f59e0b",
        "TEXT":         "#111827",
        "TEXT_ON_DARK": "#f0f4f8",
        "MUTED":        "#6b7280",
        "MUTED_DARK":   "#8bafc9",
        "DANGER":       "#dc2626",
        "SUCCESS":      "#16a34a",
        "BTN_ADD":      "#2563eb",
        "BTN_ADD_FG":   "#ffffff",
        "BTN_THEME":    "#f59e0b",
        "BTN_THEME_FG": "#111827",
    },
    "dark": {
        "BG":           "#0f172a",
        "CARD":         "#1e293b",
        "CARD2":        "#0f172a",
        "HOME_BG":      "#080e1a",
        "BORDER":       "#334155",
        "ACCENT":       "#3b82f6",
        "ACCENT2":      "#1e40af",
        "ACCENT3":      "#fbbf24",
        "TEXT":         "#f1f5f9",
        "TEXT_ON_DARK": "#f1f5f9",
        "MUTED":        "#94a3b8",
        "MUTED_DARK":   "#94a3b8",
        "DANGER":       "#f87171",
        "SUCCESS":      "#4ade80",
        "BTN_ADD":      "#2563eb",
        "BTN_ADD_FG":   "#f1f5f9",
        "BTN_THEME":    "#fbbf24",
        "BTN_THEME_FG": "#0f172a",
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


# ══════════════════════════════════════════════════════════════════════════════
#  TOAST
# ══════════════════════════════════════════════════════════════════════════════
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
        icon = icons.get(kind, "ℹ")

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

        self._alpha = 0.0
        self._fade_in()
        root.after(duration, self._start_fade_out)

    def _fade_in(self):
        sw = self.root.winfo_screenwidth()
        w = self.win.winfo_width()
        h = self.win.winfo_height()
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
        self._fade_out()

    def _fade_out(self):
        self._alpha = max(0.0, self._alpha - 0.06)
        self.win.attributes("-alpha", self._alpha)
        if self._alpha > 0:
            self.root.after(16, self._fade_out)
        else:
            try:
                self.win.destroy()
            except tk.TclError:
                pass


# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class LoginWindow:
    """
    KiloWatch-styled login / register screen.
    Calls on_success(username) only when login succeeds.
    Closing the window WITHOUT logging in does NOT call on_success.
    """

    def __init__(self, on_success, initial_mode="dark"):
        self.on_success   = on_success
        self._mode        = initial_mode
        self.T            = THEMES[self._mode]
        self._active_tab  = "login"
        self._show_pw     = False
        self._show_pw_reg = False
        self._logged_in   = False   # ← guard: only True after successful login

        self.root = tk.Tk()
        self.root.title("KiloWatch — Login")

        # ── FIX 1: resizable + minimum size ──────────────────────────────────
        self.root.resizable(True, True)
        self.root.minsize(400, 560)

        # Open maximized by default
        try:
            self.root.state("zoomed")        # Windows & some Linux WMs
        except tk.TclError:
            self.root.attributes("-zoomed", True)  # Linux/macOS fallback

        self._center(440, 620)
        self.root.configure(bg=self.T["HOME_BG"])

        # ── FIX 2: closing the window must NOT launch the main app ────────────
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build()
        self.root.mainloop()

    # ── Close handler ─────────────────────────────────────────────────────────
    def _on_close(self):
        """User clicked X — destroy window, do NOT call on_success."""
        self.root.destroy()
        # on_success is intentionally NOT called here

    # ── Geometry ──────────────────────────────────────────────────────────────
    def _center(self, w, h):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw - w)//2}+{(sh - h)//2}")

    # ── Full rebuild (used by theme toggle) ───────────────────────────────────
    def _build(self):
        for w in self.root.winfo_children():
            w.destroy()

        T  = self.T
        bg = T["HOME_BG"]
        self.root.configure(bg=bg)

        # ── Top accent bar ────────────────────────────────────────────────────
        tk.Frame(self.root, height=3, bg=T["ACCENT3"]).pack(fill="x")

        # ── Theme toggle ──────────────────────────────────────────────────────
        top_bar = tk.Frame(self.root, bg=bg)
        top_bar.pack(fill="x", padx=16, pady=(8, 0))
        mode_icon = "☀  Light" if self._mode == "dark" else "🌙  Dark"
        theme_btn = tk.Button(
            top_bar, text=mode_icon,
            font=("Segoe UI", 9, "bold"),
            bg=T["BTN_THEME"], fg=T["BTN_THEME_FG"],
            activebackground=_lighten(T["BTN_THEME"], 15),
            activeforeground=T["BTN_THEME_FG"],
            relief="flat", bd=0, cursor="hand2", padx=10, pady=4,
            command=self._toggle_theme
        )
        theme_btn.pack(side="right")

        # ── Logo ──────────────────────────────────────────────────────────────
        logo_frame = tk.Frame(self.root, bg=bg)
        logo_frame.pack(pady=(40, 12))

        ic = tk.Canvas(logo_frame, width=56, height=56,
                       bg=bg, highlightthickness=0)
        ic.pack()
        card_bg = "#1a2d45" if self._mode == "dark" else "#1e3a5a"
        ic.create_oval(3, 3, 53, 53, fill=card_bg, outline=T["ACCENT3"], width=2)
        bolt = [28, 8, 15, 30, 25, 30, 19, 48, 40, 26, 30, 26, 34, 8]
        ic.create_polygon(bolt, fill=T["ACCENT3"], outline="")

        tk.Label(logo_frame, text="KiloWatch",
                 font=("Segoe UI", 22, "bold"),
                 fg=T["TEXT_ON_DARK"], bg=bg).pack(pady=(6, 0))
        tk.Label(logo_frame, text="A Decision Support System for Optimizing Appliance-level Energy Consumption",
                 font=("Segoe UI", 9), fg=T["MUTED_DARK"], bg=bg).pack()

        # ── Main card ─────────────────────────────────────────────────────────
        card = tk.Frame(self.root, bg=T["CARD"],
                        highlightthickness=1, highlightbackground=T["BORDER"])
        card.pack(padx=500, pady=18, fill="x")
        

        # ── Tab bar ───────────────────────────────────────────────────────────
        tab_bg = T["CARD2"]
        tab_bar = tk.Frame(card, bg=tab_bg)
        tab_bar.pack(fill="x")

        self._tab_login_btn = tk.Button(
            tab_bar, text="Login",
            font=("Segoe UI", 10, "bold"),
            relief="flat", bd=0, cursor="hand2",
            padx=0, pady=10,
            command=lambda: self._switch_tab("login")
        )
        self._tab_login_btn.pack(side="left", expand=True, fill="x")

        self._tab_reg_btn = tk.Button(
            tab_bar, text="Register",
            font=("Segoe UI", 10, "bold"),
            relief="flat", bd=0, cursor="hand2",
            padx=0, pady=10,
            command=lambda: self._switch_tab("register")
        )
        self._tab_reg_btn.pack(side="left", expand=True, fill="x")

        self._tab_indicator = tk.Frame(card, height=2)
        self._tab_indicator.pack(fill="x")

        # ── Login panel ───────────────────────────────────────────────────────
        self._login_panel = tk.Frame(card, bg=T["CARD"])

        self._login_user_entry = self._field(
            self._login_panel, "USERNAME", "Enter your username")
        self._login_pw_entry = self._pw_field(
            self._login_panel, "PASSWORD", "Enter your password", "_show_pw")

        hint_row = tk.Frame(self._login_panel, bg=T["CARD"])
        hint_row.pack(fill="x", padx=20, pady=(2, 10))
        tk.Label(hint_row, text="No account? Switch to the Register tab above.",
                 font=("Segoe UI", 7), fg=T["MUTED"], bg=T["CARD"]).pack(side="left")

        self._action_btn(
            self._login_panel, "⚡  Login",
            T["BTN_ADD"], T["BTN_ADD_FG"],
            self._handle_login
        ).pack(fill="x", padx=20, pady=(0, 20))

        # ── Register panel ────────────────────────────────────────────────────
        self._reg_panel = tk.Frame(card, bg=T["CARD"])

        self._reg_user_entry = self._field(
            self._reg_panel, "USERNAME", "Choose a username")
        self._reg_pw_entry = self._pw_field(
            self._reg_panel, "PASSWORD", "Choose a password (min 4 chars)", "_show_pw_reg")
        self._reg_pw2_entry = self._field(
            self._reg_panel, "CONFIRM PASSWORD", "Re-enter your password", show="*")

        self._action_btn(
            self._reg_panel, "＋  Create Account",
            T["BTN_ADD"], T["BTN_ADD_FG"],
            self._handle_register
        ).pack(fill="x", padx=20, pady=(4, 20))

        # Activate the current tab
        self._switch_tab(self._active_tab)

        # Enter key
        self.root.bind("<Return>", lambda e: self._handle_active())

        # ── Footer ────────────────────────────────────────────────────────────
        tk.Label(self.root, text="Developed by Kaixer Alvar",
                 font=("Segoe UI", 7), fg=T["MUTED_DARK"], bg=bg
                 ).pack(side="bottom", pady=(0, 6))
        tk.Frame(self.root, height=3, bg=T["ACCENT"]).pack(side="bottom", fill="x")

    # ── Theme ─────────────────────────────────────────────────────────────────
    def _toggle_theme(self):
        self._mode = "light" if self._mode == "dark" else "dark"
        self.T = THEMES[self._mode]
        self._build()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    def _switch_tab(self, tab):
        T = self.T
        self._active_tab = tab
        if tab == "login":
            self._tab_login_btn.config(bg=T["CARD"],  fg=T["ACCENT"])
            self._tab_reg_btn.config(  bg=T["CARD2"], fg=T["MUTED"])
            self._reg_panel.pack_forget()
            self._login_panel.pack(fill="x")
            self._tab_indicator.config(bg=T["ACCENT"])
        else:
            self._tab_login_btn.config(bg=T["CARD2"], fg=T["MUTED"])
            self._tab_reg_btn.config(  bg=T["CARD"],  fg=T["ACCENT"])
            self._login_panel.pack_forget()
            self._reg_panel.pack(fill="x")
            self._tab_indicator.config(bg=T["ACCENT3"])

    def _handle_active(self):
        if self._active_tab == "login":
            self._handle_login()
        else:
            self._handle_register()

    # ── Field builders ────────────────────────────────────────────────────────
    def _field(self, parent, label_text, placeholder, show=""):
        T = self.T
        wrapper = tk.Frame(parent, bg=T["CARD"])
        wrapper.pack(fill="x", padx=20, pady=(14, 0))

        tk.Label(wrapper, text=label_text,
                 font=("Segoe UI", 7, "bold"),
                 fg=T["MUTED"], bg=T["CARD"]).pack(anchor="w")

        entry = tk.Entry(
            wrapper, font=("Segoe UI", 11),
            bg=T["CARD2"], fg=T["MUTED"],
            insertbackground=T["ACCENT"],
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=T["BORDER"],
            highlightcolor=T["ACCENT"],
            show=show,
        )
        entry.pack(fill="x", ipady=8)

        err = tk.Label(wrapper, text="",
                       font=("Segoe UI", 7), fg=T["DANGER"], bg=T["CARD"])
        err.pack(anchor="w")
        entry._err_label       = err
        entry._placeholder     = placeholder
        entry._has_placeholder = True
        entry._show_char       = show
        entry.insert(0, placeholder)

        def _focus_in(e):
            if entry._has_placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=T["TEXT"], show=entry._show_char)
                entry._has_placeholder = False

        def _focus_out(e):
            if not entry.get().strip():
                entry.delete(0, tk.END)
                entry.config(fg=T["MUTED"], show="")
                entry.insert(0, entry._placeholder)
                entry._has_placeholder = True

        entry.bind("<FocusIn>",  _focus_in)
        entry.bind("<FocusOut>", _focus_out)
        return entry

    def _pw_field(self, parent, label_text, placeholder, pw_attr):
        T = self.T
        wrapper = tk.Frame(parent, bg=T["CARD"])
        wrapper.pack(fill="x", padx=20, pady=(14, 0))

        tk.Label(wrapper, text=label_text,
                 font=("Segoe UI", 7, "bold"),
                 fg=T["MUTED"], bg=T["CARD"]).pack(anchor="w")

        row = tk.Frame(wrapper, bg=T["CARD2"],
                       highlightthickness=1,
                       highlightbackground=T["BORDER"])
        row.pack(fill="x")

        entry = tk.Entry(
            row, font=("Segoe UI", 11),
            bg=T["CARD2"], fg=T["MUTED"],
            insertbackground=T["ACCENT"],
            relief="flat", bd=0,
            highlightthickness=0,
        )
        entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(8, 0))

        eye_btn = tk.Button(
            row, text="👁",
            font=("Segoe UI", 9),
            bg=T["CARD2"], fg=T["MUTED"],
            activebackground=T["CARD2"],
            activeforeground=T["ACCENT"],
            relief="flat", bd=0, cursor="hand2", padx=8,
        )
        eye_btn.pack(side="right", padx=(0, 4))

        err = tk.Label(wrapper, text="",
                       font=("Segoe UI", 7), fg=T["DANGER"], bg=T["CARD"])
        err.pack(anchor="w")

        entry._err_label       = err
        entry._placeholder     = placeholder
        entry._has_placeholder = True
        entry._show_char       = "*"
        entry.insert(0, placeholder)

        def _toggle():
            current = getattr(self, pw_attr)
            setattr(self, pw_attr, not current)
            if not entry._has_placeholder:
                entry.config(show="" if not current else "*")
            eye_btn.config(fg=T["ACCENT"] if not current else T["MUTED"])

        eye_btn.config(command=_toggle)

        def _focus_in(e):
            if entry._has_placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=T["TEXT"], show="*")
                entry._has_placeholder = False

        def _focus_out(e):
            if not entry.get().strip():
                entry.delete(0, tk.END)
                entry.config(fg=T["MUTED"], show="")
                entry.insert(0, entry._placeholder)
                entry._has_placeholder = True

        entry.bind("<FocusIn>",  _focus_in)
        entry.bind("<FocusOut>", _focus_out)
        return entry

    def _action_btn(self, parent, text, bg, fg, cmd):
        btn = tk.Button(
            parent, text=text,
            font=("Segoe UI", 10, "bold"),
            bg=bg, fg=fg,
            activebackground=_darken(bg, 15),
            activeforeground=fg,
            relief="flat", bd=0, cursor="hand2",
            padx=12, pady=10,
            command=cmd
        )
        btn.bind("<Enter>", lambda e, b=btn, c=bg: b.config(bg=_lighten(c, 15)))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))
        return btn

    # ── Value / error helpers ─────────────────────────────────────────────────
    def _get_val(self, entry):
        if getattr(entry, "_has_placeholder", False):
            return ""
        return entry.get().strip()

    def _set_err(self, entry, msg=""):
        T = self.T
        lbl = getattr(entry, "_err_label", None)
        color = T["DANGER"] if msg else T["BORDER"]
        entry.config(highlightbackground=color, highlightcolor=color if msg else T["ACCENT"])
        if lbl:
            lbl.config(text=msg)

    # ── Login / Register handlers ─────────────────────────────────────────────
    def _handle_login(self):
        username = self._get_val(self._login_user_entry)
        password = self._get_val(self._login_pw_entry)

        self._set_err(self._login_user_entry)
        self._set_err(self._login_pw_entry)

        ok = True
        if not username:
            self._set_err(self._login_user_entry, "Required")
            ok = False
        if not password:
            self._set_err(self._login_pw_entry, "Required")
            ok = False
        if not ok:
            return

        success, msg = login(username, password)
        if success:
            self._logged_in = True   # ← mark success before destroy
            Toast(self.root, msg, "success")
            self.root.after(900, lambda: self._launch(username))
        else:
            self._set_err(self._login_pw_entry, msg)
            Toast(self.root, msg, "error")

    def _handle_register(self):
        username  = self._get_val(self._reg_user_entry)
        password  = self._get_val(self._reg_pw_entry)
        password2 = self._get_val(self._reg_pw2_entry)

        for e in (self._reg_user_entry, self._reg_pw_entry, self._reg_pw2_entry):
            self._set_err(e)

        ok = True
        if not username:
            self._set_err(self._reg_user_entry, "Required")
            ok = False
        if not password:
            self._set_err(self._reg_pw_entry, "Required")
            ok = False
        if not password2:
            self._set_err(self._reg_pw2_entry, "Required")
            ok = False
        if password and password2 and password != password2:
            self._set_err(self._reg_pw2_entry, "Passwords do not match")
            ok = False
        if not ok:
            return

        success, msg = register(username, password)
        if success:
            Toast(self.root, msg + " You can now log in.", "success")
            self._switch_tab("login")
        else:
            Toast(self.root, msg, "error")
            if "already" in msg.lower():
                self._set_err(self._reg_user_entry, msg)
            elif "password" in msg.lower():
                self._set_err(self._reg_pw_entry, msg)

    def _launch(self, username):
        self.root.destroy()
        self.on_success(username)   # only called from here, never from _on_close


# ── Standalone test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    def on_login(username):
        print(f"Logged in as: {username}")

    LoginWindow(on_success=on_login)