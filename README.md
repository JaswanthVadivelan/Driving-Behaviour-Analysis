# Driving Behaviour Analysis System

A Streamlit dashboard to detect aggressive driving from speed time-series using DTW features and an SVM model. It supports live scoring, trip history, vehicle comparison, alerts, and PDF reports.

---

## What This App Is For (Simple Explanation)

This app helps you:
- Score driving trips as **calm** or **aggressive**
- See safety scores and trends over time
- Compare vehicles in a fleet
- Get alerts for risky driving
- Generate PDF reports

---

## Step-by-Step: How to Use the App

### Step 1: Install the requirements

```powershell
python -m pip install -r requirements.txt
```

### Step 2: Generate sample data (first time only)

If you don’t already have data, run:

```powershell
python step1_generate.py
python step2_eda.py
python step3_dtw_features.py
python step4_svm_train.py
```

This creates:
- `data/trips.csv` (synthetic trips)
- `data/trips_features.csv` (DTW features)
- `models/svm_model.pkl` (trained model)
- `charts/*.png` (EDA plots)

### Step 3: Start the app

```powershell
streamlit run app.py
```

Open the local URL shown in the terminal (usually `http://localhost:8501`).

---

## How to Use Each Page (Simple Steps)

### Home (Dashboard)
- See total trips, average safety score, and recent alerts
- Use the left sidebar to go to other pages

### Live Trip Scorer
1. Enter a **Vehicle ID** (any text or number, e.g., `V001`)
2. Upload a CSV **or** pick one from the `datasets/` folder
3. Click **Score Trips**
4. View results, charts, and download the scored file
5. Alerts will show if risky patterns are found

**Required CSV columns:** `speed_t0` to `speed_t49`

### Trip History
- Filter by vehicle, date range, and label
- See safety score trends and history table
- Download filtered data

### Vehicle Comparison
- Select 2 or more vehicles
- Compare average safety, risk trends, and worst trips

### Alert Centre
- See critical and repeat offender alerts
- Filter alert history
- Clear alerts older than 7 days

### Reports
- Generate **Trip Report** (for one vehicle)
- Generate **Fleet Report** (all vehicles)
- Download existing reports from `reports/`

---

## Sample Dataset

A sample file is included at:

```
datasets/sample_trips.csv
```

You can select it directly from the **Live Trip Scorer** page without uploading anything.

---

## Optional: Download External Dataset (Kaggle)

```powershell
python download_kaggle_dataset.py
```

Copy any CSVs you want into the `datasets/` folder to use them in the app.

---

## Common Errors (Quick Fixes)

**Plotly not found**
```powershell
python -m pip install plotly
```

**dtaidistance not found**
```powershell
python -m pip install dtaidistance
```

---

## Project Structure

```
app.py
pages/
  1_Live_Scoring.py
  2_Trip_History.py
  3_Vehicle_Comparison.py
  4_Alerts.py
  5_Reports.py
src/
  config.py
  scorer.py
  history_manager.py
  alert_engine.py
  vehicle_profiler.py
  report_generator.py
config.yaml
requirements.txt
data/
models/
charts/
reports/
datasets/
```

---

## Configuration

All paths and thresholds are stored in `config.yaml` (you can change without editing code).

---

## Need Changes?

If you want UI changes, extra metrics, new models, or more charts, just ask.
