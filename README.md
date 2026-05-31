# 🌞 Specusol — Solar Energy Market Analytics (Extended Build)

> Solo deep-dive development extending the original [EnergyHack 2026](https://github.com/cindy-muniz/EnergyHack2026) hackathon project  
> Built with Python · Plotly Dash · Deployed on Render

---

## What It Does

Specusol is the extended solo build of an analytics platform originally prototyped at EnergyHack @ Georgia Tech. The concept: Texas solar farms on the ERCOT grid routinely overproduce energy relative to real-time demand. This dashboard models that surplus as a financial asset and gives users tools to analyze it from both an energy and a market perspective.

This repo focuses on the core analytics engine — specifically the supply/demand charting and ERCOT zone mapping — before the final UI and market features were merged into the hackathon submission.

### What's in this version

- **Interactive supply/demand curves** — separate residential and commercial energy supply and demand modeled across a 24-hour cycle, with automatic equilibrium detection
- **ERCOT zone map** — interactive Leaflet map showing Texas grid zones; enter any address to verify which ERCOT zone it falls in and drop a pin
- **Daylight solar model** — Gaussian irradiance curve modeling realistic solar output throughout the day (peaks ~1:15 PM at ~1000 W/m²)
- **7-hour weather forecast** — localized hourly temperature (°F) and solar irradiance estimates

---

## How This Fits Into the Larger Project

This repo represents the **R&D phase** of Specusol's development:

1. **Specusol (this repo)** — Core analytics: supply/demand curves, ERCOT mapping, solar irradiance model. Built and iterated independently.
2. **EnergyHack2026** — Final merged product combining this work with teammate Jenna's stock market and financial analytics layer. Deployed live for the hackathon.

The full combined app (with stock market tracking, options Greeks, and live geolocation) lives at [github.com/cindy-muniz/EnergyHack2026](https://github.com/cindy-muniz/EnergyHack2026) and is live at [energyhack2026.onrender.com](https://energyhack2026.onrender.com).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3 |
| Web Framework | Plotly Dash + Dash Bootstrap Components |
| Mapping | Dash Leaflet |
| Data / Math | NumPy, Pandas |
| Geolocation | Geopy / Nominatim |
| Deployment | Render |

---

## How to Run Locally

```bash
git clone https://github.com/cindy-muniz/Specusol.git
cd Specusol
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:8050` in your browser.

---

## Technical Notes

**Solar Irradiance Model**  
Output is modeled as a Gaussian function: `P(t) = 1000 · e^(-(t - 13.25)² / (2 · 2.5²))` where `t` is the hour of day. This produces a physically realistic bell curve peaking around 1:15 PM — matching real-world solar generation patterns without requiring live API data.

**ERCOT Zone Detection**  
Zone assignment uses lat/lon bounding boxes for ERCOT's four major zones (North, South, West, Houston). Implemented in pure Python — no geospatial library dependencies — for portability and Render deployment stability.

**Equilibrium Annotation**  
The chart automatically detects and annotates the supply/demand crossover point using NumPy's `sign` and `diff` to find zero-crossing indices in the net supply curve.

---

## Project Structure

```
Specusol/
├── app.py              # Dash application — layout, callbacks, solar model
└── requirements.txt    # Python dependencies
```
