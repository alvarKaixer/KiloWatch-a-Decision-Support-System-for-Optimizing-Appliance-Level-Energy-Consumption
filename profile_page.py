# profile_page.py
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ImageDraw
import json, os

def _profile_file(username):
    return f"profile_{username}.json"

def load_profile(username="User"):
    path = _profile_file(username)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"name": username, "avatar_path": None}

def save_profile(data, username="User"):
    with open(_profile_file(username), "w") as f:
        json.dump(data, f)

def make_circle_image(path, size=90):
    """Crop image into a circle and return a PhotoImage."""
    img = Image.open(path).resize((size, size), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    img.putalpha(mask)
    return ImageTk.PhotoImage(img)

class ProfilePage:
    def __init__(self, parent, T, report_history, rate_entry_get, username="User"):
        self.T = T
        self.report_history = report_history
        self.rate_get = rate_entry_get
        self.profile = load_profile(username)
        self.profile["name"] = username
        self.username = username

        win = tk.Toplevel(parent)
        self.win = win
        win.title("Profile — KiloWatch")
        win.configure(bg=T["BG"])
        win.resizable(True, True)
        sw, sh = parent.winfo_screenwidth(), parent.winfo_screenheight()
        W, H = 520, 620
        win.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
        win.minsize(460, 500)
        win.attributes("-topmost", True)

        self._build(win)

    def _build(self, win):
        T = self.T

        # Header
        tk.Frame(win, bg=T["ACCENT2"]).pack(fill="x", ipady=14)
        hdr = win.winfo_children()[-1]
        tk.Label(hdr, text="👤  My Profile", font=("Segoe UI", 14, "bold"),
                 fg="#ffffff", bg=T["ACCENT2"], padx=20).pack(side="left")
        tk.Frame(win, height=2, bg=T["ACCENT3"]).pack(fill="x")

        body = tk.Frame(win, bg=T["BG"], padx=24, pady=20)
        body.pack(fill="both", expand=True)

        # ── Avatar ────────────────────────────────────────────────────────────
        avatar_frame = tk.Frame(body, bg=T["BG"])
        avatar_frame.pack(pady=(0, 16))

        self._avatar_label = tk.Label(avatar_frame, bg=T["BG"])
        self._avatar_label.pack()
        self._load_avatar()

        tk.Button(avatar_frame, text="📷  Change Photo",
                  font=("Segoe UI", 8, "bold"),
                  bg=T["BTN_CLR"], fg=T["BTN_CLR_FG"],
                  relief="flat", bd=0, cursor="hand2",
                  padx=10, pady=4,
                  command=self._pick_avatar).pack(pady=(8, 0))

        # ── Name ──────────────────────────────────────────────────────────────
        tk.Label(body, text="LOGGED IN AS", font=("Segoe UI", 7, "bold"),
                 fg=T["MUTED"], bg=T["BG"]).pack(anchor="w")

        name_card = tk.Frame(body, bg=T["CARD"],
                             highlightthickness=1,
                             highlightbackground=T["BORDER"])
        name_card.pack(fill="x", pady=(2, 16))

        tk.Label(name_card, text=self.username,
                 font=("Segoe UI", 13, "bold"),
                 fg=T["ACCENT"], bg=T["CARD"],
                 padx=14, pady=10).pack(side="left")

        tk.Label(name_card, text="(from your account)",
                 font=("Segoe UI", 8),
                 fg=T["MUTED"], bg=T["CARD"]).pack(side="left")

        # ── Energy Summary ────────────────────────────────────────────────────
        tk.Frame(body, height=1, bg=T["BORDER"]).pack(fill="x", pady=(0, 12))
        tk.Label(body, text="ENERGY SAVING HISTORY",
                 font=("Segoe UI", 7, "bold"),
                 fg=T["MUTED"], bg=T["BG"]).pack(anchor="w", pady=(0, 8))

        self._build_stats(body)

        # ── Report list ───────────────────────────────────────────────────────
        tk.Label(body, text="PAST REPORTS", font=("Segoe UI", 7, "bold"),
                 fg=T["MUTED"], bg=T["BG"]).pack(anchor="w", pady=(12, 4))

        list_frame = tk.Frame(body, bg=T["CARD"],
                              highlightthickness=1,
                              highlightbackground=T["BORDER"])
        list_frame.pack(fill="both", expand=True)

        sb = ttk.Scrollbar(list_frame, orient="vertical")
        sb.pack(side="right", fill="y")

        lb = tk.Listbox(list_frame, font=("Segoe UI", 9),
                        bg=T["CARD"], fg=T["TEXT"],
                        selectbackground=T["ACCENT"],
                        selectforeground="#ffffff",
                        relief="flat", bd=0,
                        highlightthickness=0,
                        activestyle="none",
                        yscrollcommand=sb.set)
        lb.pack(side="left", fill="both", expand=True, padx=8, pady=6)
        sb.config(command=lb.yview)

        for rpt in reversed(self.report_history):
            label = rpt.get("label", rpt.get("timestamp", "—"))
            total = sum(k for _, k in rpt.get("ranked", []))
            lb.insert(tk.END, f"  {label}   |   {total:.3f} kWh/day")

    def _build_stats(self, parent):
        T = self.T
        total_reports = len(self.report_history)

        # Find best (lowest total) vs most recent
        totals = [sum(k for _, k in r.get("ranked", [])) for r in self.report_history]
        best   = min(totals) if totals else 0
        latest = totals[-1]  if totals else 0
        trend  = latest - totals[-2] if len(totals) >= 2 else 0

        stats = [
            ("📋", "Reports\nGenerated", str(total_reports), T["ACCENT"]),
            ("⚡", "Latest\nkWh/day",    f"{latest:.3f}",    T["ACCENT3"]),
            ("🏆", "Best\nkWh/day",      f"{best:.3f}",      T["SUCCESS"]),
            ("📈", "Trend",
             ("▼ Improved" if trend < 0 else ("▲ Increased" if trend > 0 else "= Same")),
             T["SUCCESS"] if trend < 0 else (T["DANGER"] if trend > 0 else T["MUTED"])),
        ]

        row = tk.Frame(parent, bg=T["BG"])
        row.pack(fill="x")
        for i, (icon, label, val, color) in enumerate(stats):
            card = tk.Frame(row, bg=T["CARD"],
                            highlightthickness=1,
                            highlightbackground=T["BORDER"])
            card.grid(row=0, column=i, sticky="ew",
                      padx=(0 if i == 0 else 6, 0), ipady=8)
            row.columnconfigure(i, weight=1)
            tk.Label(card, text=icon, font=("Segoe UI", 16),
                     bg=T["CARD"]).pack(pady=(8, 2))
            tk.Label(card, text=val, font=("Segoe UI", 11, "bold"),
                     fg=color, bg=T["CARD"]).pack()
            tk.Label(card, text=label, font=("Segoe UI", 7),
                     fg=T["MUTED"], bg=T["CARD"],
                     justify="center").pack(pady=(0, 8))

    def _load_avatar(self):
        T = self.T
        path = self.profile.get("avatar_path")
        try:
            if path and os.path.exists(path):
                self._photo = make_circle_image(path, 90)
                self._avatar_label.config(image=self._photo, bg=T["BG"])
                return
        except Exception:
            pass
        # Default initials avatar
        name = self.profile.get("name", "U")
        initials = "".join(w[0].upper() for w in name.split()[:2])
        canvas = tk.Canvas(self._avatar_label.master, width=90, height=90,
                           bg=T["BG"], highlightthickness=0)
        canvas.pack()
        canvas.create_oval(2, 2, 88, 88, fill=T["ACCENT2"], outline=T["ACCENT3"], width=2)
        canvas.create_text(45, 45, text=initials,
                           font=("Segoe UI", 28, "bold"), fill="#ffffff")
        self._avatar_label.pack_forget()  # hide blank label, use canvas

    def _pick_avatar(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")],
            title="Choose a profile photo"
        )
        if not path:
            return
        self.profile["avatar_path"] = path
        save_profile(self.profile, self.username)
        # Reload avatar
        for w in self._avatar_label.master.winfo_children():
            w.destroy()
        self._avatar_label = tk.Label(self._avatar_label.master, bg=self.T["BG"])
        self._avatar_label.pack()
        self._load_avatar()

    def _save_name(self):
        name = self._name_entry.get().strip()
        if not name:
            return
        self.profile["name"] = name
        save_profile(self.profile, self.username)