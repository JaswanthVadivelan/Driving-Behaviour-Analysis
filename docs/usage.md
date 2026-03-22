# Usage Guide (Run + Use the App)

This guide explains how to run and use the application step by step.

## 1. Install and Run

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate it

**Windows**
```bash
.venv\Scripts\activate
```

**macOS/Linux**
```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start the app

```bash
streamlit run app/main.py
```

The app will open in your browser (default: `http://localhost:8501`).

## 2. Sample Data Setup

All sample datasets should be placed here:

```
data/raw/
```

The Live Scoring page loads dropdown options from this folder.

## 3. Live Scoring (Main Feature)

### Steps

1. Open **Live Scoring** page from the top navigation.
2. Enter **Vehicle ID** (example: `TN 14 AK 3524`).
3. Choose **one** input method:
   - Upload a CSV file
   - OR select a sample dataset from the dropdown
4. Click **Score Trips**.

### Output you will see

- Trip summary KPIs (Total, Calm, Aggressive, Avg Safety Score)
- Bar chart of safety scores
- Pie chart of calm vs aggressive
- Detailed scored table
- Alerts (if triggered)
- Download button for scored CSV

## 4. Reports Page

You can generate:

- **Trip Report** (per vehicle)
- **Fleet Report** (all vehicles)
- **Alert Report** (fleet or vehicle)

The reports are saved in:

```
outputs/reports/
```

You can download them directly from the UI.

## 5. Alerts Page

- Shows recent alerts (last 24 hours)
- Lets you see severity and alert type

Alerts are stored at:

```
data/processed/alerts.csv
```

## 6. Vehicle Profile

Displays driving behavior patterns for each vehicle using history data.

History data is stored at:

```
data/processed/trip_history.csv
```

## 7. Model Performance

Shows model benchmarking results using processed features:

```
data/processed/trips_features.csv
```

## 8. How to Add New Data

If you get a new dataset:

1. Place it in `data/raw/`
2. Select it in Live Scoring
3. Score trips to generate history + alerts

## 9. Troubleshooting

### “Module not found” errors
Run the app only with:

```bash
streamlit run app/main.py
```

### CSV errors
Your CSV must contain these columns:

```
speed_t0, speed_t1, ... speed_t49
```

### Model file missing
Ensure:

```
models/svm_model.pkl
```

## 10. Useful Paths Reference

- Config: `configs/config.yaml`
- Raw datasets: `data/raw/`
- Processed datasets: `data/processed/`
- Reports: `outputs/reports/`
- Charts: `outputs/charts/`

If you want a shorter quick-start version, I can generate that too.
