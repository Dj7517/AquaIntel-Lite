# 💧 AquaIntel Lite — Apartment Water Intelligence Dashboard

> **i2I Challenge 3.0 | Wipro Earthian x IIT Madras**  
> Theme: Water | Hydrology | Waste Management

---

## 🏗️ Project Structure

```
aquaintel_lite/
│
├── app.py                  ← Main Streamlit application
├── requirements.txt        ← Python dependencies
├── .env                    ← Environment configuration
│
├── data/
│   └── sample_data.csv     ← Demo dataset (15 flats)
│
├── models/
│   ├── __init__.py
│   └── ml_model.py         ← K-Means clustering + tank prediction
│
└── utils/
    ├── __init__.py
    ├── config.py            ← Env-based config loader
    ├── data_utils.py        ← Metrics computation helpers
    └── charts.py            ← Plotly chart builders
```

---

## ⚙️ Setup & Run

### 1. Clone / Download the project

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure `.env` (optional)
```env
TANK_CAPACITY_LITERS=10000
IDEAL_LITERS_PER_PERSON_PER_DAY=135
```

### 5. Run the app
```bash
streamlit run app.py
```

---

## 📊 CSV Format (for upload)

```csv
Flat,Residents,Shower_Min,Kitchen_Use_L,Laundry_Use_L,Total_Liters
A101,3,22,140,120,500
A102,5,40,210,280,890
```

---

## 🧠 AI Features

| Feature | Method |
|---|---|
| Usage clustering | K-Means (k=3) |
| Efficiency labels | Centroid-ordered: Efficient / Moderate / High |
| Tank prediction | Daily rate extrapolation |
| Smart alerts | Deviation % from building average |

---

## 🌍 Problem Statement

Apartments lack visibility into per-flat water consumption. Without data:
- Some flats overuse, others face shortages
- Managers make decisions blindly
- No early warning for tank depletion

**AquaIntel Lite** solves this with a zero-IoT, data-driven dashboard.

---

## 📬 Contact

info@ideastoimpact.co.in | https://ideastoimpact.co.in
