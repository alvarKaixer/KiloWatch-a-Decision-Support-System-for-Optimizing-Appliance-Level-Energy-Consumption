# ⚡ KiloWatch
### A Decision Support System for Optimizing Appliance-Level Energy Consumption

![Python](https://img.shields.io/badge/Python-3.14-blue?style=flat-square&logo=python)
![GUI](https://img.shields.io/badge/GUI-Tkinter-informational?style=flat-square)
![License](https://img.shields.io/badge/License-See%20LICENSE-lightgrey?style=flat-square)

KiloWatch is a desktop application that helps households track, analyze, and reduce their electricity consumption at the appliance level. Log your appliances, generate ranked energy reports, compare snapshots over time, and simulate savings — all from a clean, themeable UI.

---

## 📸 Features

| Feature | Description |
|---|---|
| ⚡ **Appliance Tracker** | Add appliances by name, wattage, and daily usage hours (or minutes) |
| 📊 **Energy Reports** | Instantly ranked breakdown of daily & monthly kWh per appliance |
| 💡 **Smart Recommendations** | Per-appliance and overall energy-saving tips generated automatically |
| ⇄ **Report Comparison** | Pick any two saved reports and compare consumption changes side-by-side |
| 🎛 **What-If Simulator** | Drag a slider to simulate reducing an appliance's hours and see savings in real time |
| 🎯 **Goal Tracker** | Set a monthly kWh or bill target and track progress with a live circular gauge |
| 📋 **Export** | Save any report as `.TXT` or `.CSV`, or copy it to clipboard |
| 🌙 **Light / Dark Mode** | Full theme switching with high-contrast palettes for both modes |
| 💾 **Session Persistence** | Appliances and report history are automatically saved and restored between sessions |

---

## 🗂 Project Structure

```
KiloWatch/
│
├── main.py              # Entry point — launches the Tkinter app
├── gui.py               # All UI logic: home screen, main system, windows & widgets
├── logic.py             # Core computation: kWh calculations, appliance ranking
├── data_manager.py      # In-memory appliance store (add / get / remove)
├── persistence.py       # Load/save appliances and report history to JSON
├── utils.py             # Formatting helpers, recommendation & insight generators
│
├── kilowatch_data.json      # Auto-generated: saved appliance list
├── kilowatch_history.json   # Auto-generated: saved report history
└── data.json                # Auxiliary data file
```

---

## 🧠 How It Works

### 1. Data Entry
Users input an appliance's **name**, **wattage (W)**, and **daily usage** (in hours or minutes). The app validates all inputs with inline error messages — catching negatives, duplicates, and unrealistic values (e.g. > 15,000 W or > 24 h/day) before anything gets added.

### 2. Computation (`logic.py`)
For each appliance, daily energy consumption is calculated as:

```
kWh/day = (Watts × Hours/day) / 1000
```

All appliances are then **ranked highest to lowest** by kWh/day so the biggest energy consumers are immediately obvious.

### 3. Reports & Insights (`utils.py`)
When a report is generated, the app:
- Formats kWh values for display
- Generates a **per-appliance recommendation** based on the appliance name and its monthly consumption
- Generates an **overall household insight** based on the full ranked list
- Calculates an **estimated monthly bill** using a configurable ₱/kWh rate (defaults to Meralco's April 2026 rate of ₱14.3496/kWh)

Reports are automatically saved to history with a timestamp and can be renamed by the user.

### 4. Persistence (`persistence.py`)
Appliances and report history are serialized to JSON files (`kilowatch_data.json`, `kilowatch_history.json`) on every change and reloaded automatically when the app starts — so no data is lost between sessions.

### 5. Report Comparison
Any two saved reports can be selected from dropdowns and compared. The comparison engine:
- Diffs every appliance that appears in either report (new, removed, or changed)
- Shows percentage change per appliance with ▲/▼ indicators
- Highlights commendations (drops > 10%) and suggestions (increases > 10%)
- Generates appliance-specific tips (e.g. thermostat advice for air conditioners, cold-wash tips for washing machines)
- Gives an overall verdict with total kWh change

### 6. What-If Simulator
After generating a report, the What-If window lets users pick any appliance and drag a slider to a **new target hours/day** value. The app instantly recalculates:
- New kWh/day for that appliance
- New household daily and monthly total
- kWh saved (or added)
- Bill saved (or added), if a rate is configured

### 7. Goal Tracker
Users set a monthly kWh or peso (₱) target. A **live circular gauge** shows current consumption as a percentage of the goal, color-coded green → amber → red as you approach or exceed the limit. The gauge auto-refreshes every 2 seconds against live appliance data.

---

## 🚀 Getting Started

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

1. **Launch** the app — you'll land on the home screen.
2. Click **Open the System →** to enter the main dashboard.
3. **Add appliances** using the input fields at the top (name, watts, hours/day).
4. Click **⚡ Generate** to produce a ranked energy report.
5. Use **💡 What If** to simulate reducing usage on any appliance.
6. Generate multiple reports over time, then use **⇄ Compare A vs B** to track changes.
7. Open **More ▾ → Goal Tracker** to set a monthly consumption target.
8. Export any report via **More ▾ → Export as .TXT / .CSV**.

---

## ⚙ Configuration

The electricity rate defaults to **₱14.3496/kWh** (Meralco, April 2026) but can be changed directly in the rate field on the main dashboard. The new rate is used immediately for all bill calculations.

---

## 📄 License

See the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Kaixer Emmanuel Oscar Antonio M. Alvar**  
Developed as a Decision Support System for household energy optimization.
