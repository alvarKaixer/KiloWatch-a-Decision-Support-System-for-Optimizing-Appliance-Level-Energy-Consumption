#  KiloWatch
### A Decision Support System for Optimizing Appliance-Level Energy Consumption

![Python](https://img.shields.io/badge/Python-3.14-blue?style=flat-square&logo=python)
![GUI](https://img.shields.io/badge/GUI-Tkinter-informational?style=flat-square)
![License](https://img.shields.io/badge/License-See%20LICENSE-lightgrey?style=flat-square)

KiloWatch is a desktop application that helps households track, analyze, and reduce their electricity consumption at the appliance level. Log your appliances, generate ranked energy reports, compare snapshots over time, and simulate savings — all from a clean, themeable UI with per-user accounts.

---

##  Features

| Feature | Description |
|---|---|
|  **User Accounts** | Register and log in with hashed credentials — each user's data is fully isolated |
|  **Appliance Tracker** | Add appliances by name, wattage, and daily usage hours (or minutes) |
|  **Energy Reports** | Instantly ranked breakdown of daily & monthly kWh per appliance |
|  **Smart Recommendations** | Per-appliance and overall energy-saving tips generated automatically |
|  **Report Comparison** | Pick any two saved reports and compare consumption changes side-by-side |
|  **What-If Simulator** | Drag a slider to simulate reducing an appliance's hours and see savings in real time |
|  **Export** | Save any report as `.TXT` or `.CSV`, or copy it to clipboard |
|  **Light / Dark Mode** | Full theme switching with high-contrast palettes for both modes |
|  **Session Persistence** | Appliances and report history are automatically saved and restored per user |

---

##  Project Structure

```
KiloWatch/
│
├── main.py              # Entry point — launches login, then the main app
├── gui.py               # All UI logic: home screen, main system, windows & widgets
├── login_window.py      # Login and registration screen
├── auth.py              # User authentication: register, login, SHA-256 password hashing
├── profile_page.py      # Profile page UI
│
├── logic.py             # Core computation: kWh calculations, appliance ranking
├── data_manager.py      # In-memory appliance store (add / get / remove / clear)
├── persistence.py       # Load/save appliances and report history to JSON
├── utils.py             # Formatting helpers, recommendation & insight generators
│
│   # ── Runtime-generated files (gitignored) ──
├── users.json                        # Registered user credentials (hashed)
├── profile_<username>.json           # Per-user profile data
├── kilowatch_data_<username>.json    # Per-user saved appliance list
└── kilowatch_history_<username>.json # Per-user saved report history
```

> **Note:** All `*.json` data files are excluded from version control via `.gitignore` and are created automatically at runtime.

---

##  How It Works

### 1. Authentication (`auth.py`, `login_window.py`)
Users register with a username and password. Passwords are hashed with SHA-256 before being stored in `users.json` — plaintext passwords are never saved. On login, the entered password is hashed and compared. A successful login passes the username through to the main app, where it scopes all data loading and saving.

### 2. Data Entry
Users input an appliance's **name**, **wattage (W)**, and **daily usage** (in hours or minutes). The app validates all inputs with inline error messages — catching negatives, duplicates, and unrealistic values (e.g. > 15,000 W or > 24 h/day) before anything gets added.

### 3. Computation (`logic.py`)
For each appliance, daily energy consumption is calculated as:

```
kWh/day = (Watts × Hours/day) / 1000
```

All appliances are then **ranked highest to lowest** by kWh/day so the biggest energy consumers are immediately obvious.

###  Computation Reference

#### Core energy calculations (`logic.py` — `compute_all`)

| Formula | Expression |
|---|---|
| Daily energy | `kWh/day = (watts × hours) / 1000` |
| Monthly energy | `kWh/month = kWh/day × 30` |
| Estimated bill | `Est. Bill = kWh/month × rate` |

#### What-If Simulator

Given a target reduction percentage (`pct`) on a selected appliance:

| Formula | Expression |
|---|---|
| Energy saved (daily) | `saved_kWh/day = orig_kWh/day × (pct / 100)` |
| New appliance consumption | `new_kWh/day = orig_kWh/day − saved_kWh/day` |
| New household daily total | `Σ kWh/day` for all appliances, with the selected one replaced by `new_kWh/day` |
| Total reduction | `reduction% = (orig_total − new_total) / orig_total × 100` |
| Monthly bill saved | `bill_saved = saved_kWh/month × rate` |

**Hours window** — when specifying a new usage duration directly:

| Formula | Expression |
|---|---|
| New appliance consumption | `new_kWh/day = (watts × new_hours) / 1000` |
| Daily energy saved | `hours_saved_kWh = orig_kWh/day − new_kWh/day` |

#### Report Comparison

| Formula | Expression |
|---|---|
| Per-appliance change | `change% = (b − a) / a × 100` |
| Report total | `Σ kWh/day` for all appliances present in that report |

Where `a` = consumption in Report A, `b` = consumption in Report B. Appliances unique to one report are flagged as **added** or **removed** rather than computed.

---

### 4. Reports & Insights (`utils.py`)
When a report is generated, the app:
- Formats kWh values for display
- Generates a **per-appliance recommendation** based on the appliance name and its monthly consumption
- Generates an **overall household insight** based on the full ranked list
- Calculates an **estimated monthly bill** using a configurable ₱/kWh rate (defaults to Meralco's April 2026 rate of ₱14.3496/kWh)

Reports are automatically saved to history with a timestamp and can be renamed by the user.

### 5. Persistence (`persistence.py`)
Appliances and report history are serialized to per-user JSON files on every change and reloaded automatically when the app starts — so no data is lost between sessions, and each user's data stays separate.

### 6. Report Comparison
Any two saved reports can be selected from dropdowns and compared. The comparison engine:
- Diffs every appliance that appears in either report (new, removed, or changed)
- Shows percentage change per appliance with ▲/▼ indicators
- Highlights commendations (drops > 10%) and suggestions (increases > 10%)
- Generates appliance-specific tips (e.g. thermostat advice for air conditioners, cold-wash tips for washing machines)
- Gives an overall verdict with total kWh change

### 7. What-If Simulator
After generating a report, the What-If window lets users pick any appliance and drag a slider to a **new target hours/day** value. The app instantly recalculates:
- New kWh/day for that appliance
- New household daily and monthly total
- kWh saved (or added)
- Bill saved (or added), if a rate is configured

---

##  Getting Started

### Prerequisites
- Python 3.8 or higher
- Tkinter (included with most standard Python installations)

No third-party packages required — KiloWatch runs entirely on the Python standard library.

### Installation

```bash
# Clone the repository
git clone https://github.com/alvarKaixer/KiloWatch---a-Decision-Support-System-for-Optimizing-Appliance-Level-Energy-Consumption.git

cd KiloWatch---a-Decision-Support-System-for-Optimizing-Appliance-Level-Energy-Consumption
```

### Running the App

```bash
python main.py
```

That's it. No virtual environment or dependency installation needed.

---

## 🖥 Usage Guide

1. **Launch** the app — you'll land on the login screen.
2. **Register** a new account or **log in** with existing credentials.
3. You'll arrive at the home screen. Click **Open the System →** to enter the main dashboard.
4. **Add appliances** using the input fields at the top (name, watts, hours/day).
5. Click ** Generate** to produce a ranked energy report.
6. Use ** What If** to simulate reducing usage on any appliance.
7. Generate multiple reports over time, then use **⇄ Compare A vs B** to track changes.
8. Export any report via **More ▾ → Export as .TXT / .CSV**.
9. Click **⏻ Logout** in the header to return to the login screen.

---

##  Configuration

The electricity rate defaults to **₱14.3496/kWh** (Meralco, April 2026) but can be changed directly in the rate field on the main dashboard. The new rate is used immediately for all bill calculations.

---

##  Data & Privacy

All user data files (`users.json`, `profile_*.json`, `kilowatch_data_*.json`, `kilowatch_history_*.json`) are generated locally at runtime and are excluded from this repository via `.gitignore`. Passwords are never stored in plaintext — only their SHA-256 hashes are saved.

---

##  License

See the [LICENSE](LICENSE) file for details.

---

##  Author

**Kaixer Emmanuel Oscar Antonio M. Alvar**  
Developed as a Decision Support System for household energy optimization.
