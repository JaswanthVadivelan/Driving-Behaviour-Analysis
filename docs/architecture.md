# Architecture

This document explains the project structure, the major modules, and how data flows through the system. It is written to be easy to follow even if you are new to Streamlit or ML projects.

## Big Picture

This project is a **Streamlit web app** that scores driving trips using a **DTW + SVM** model. It has a clean separation between:

- **App/UI**: Streamlit pages and UI components
- **Core Logic**: Scoring, alerts, profiling, report generation
- **Pipelines**: Offline data preparation and model training steps
- **Data/Outputs**: Raw datasets, processed datasets, charts, and reports

## Folder Structure (Production Layout)

```
project_root/
+-- app/                     # Streamlit application (UI)
¦   +-- main.py              # Main dashboard entrypoint
¦   +-- pages/               # Streamlit pages (Live Scoring, Reports, etc.)
¦   +-- components/          # UI cards, tables, visual widgets
¦   +-- config/              # UI theme and navigation
¦
+-- core/                    # Business logic (no Streamlit)
¦   +-- alerts/              # Alert generation + retrieval
¦   +-- scoring/             # ML scoring (DTW + SVM)
¦   +-- profiling/           # Vehicle profiling & comparisons
¦   +-- reports/             # PDF report generation
¦   +-- utils/               # Config loading, history storage
¦
+-- pipelines/               # Offline scripts: data prep, training, evaluation
+-- data/                    # Datasets (raw, processed, external)
+-- models/                  # Trained model artifacts (.pkl)
+-- outputs/                 # Generated charts + reports
+-- scripts/                 # Utility scripts (e.g. download data)
+-- configs/                 # YAML configs for paths + thresholds
+-- docs/                    # Documentation
+-- requirements.txt         # Dependencies
```

## App Layer (Streamlit UI)

### app/main.py
- The main dashboard that shows KPIs, charts, and alerts.
- Calls into `core` modules to get data (history, alerts, profiling).
- Uses shared theme utilities from `app/config/theme.py`.

### app/pages/
Each page is a separate feature of the product:

- `01_live_scoring.py` — Upload or select CSV and score trips
- `04_alerts.py` — View and manage alerts
- `05_reports.py` — Generate PDF reports
- `06_vehicle_profile.py` — Vehicle profiling analytics
- `07_fleet_map.py` — Map view
- `08_driver_leaderboard.py` — Driver ranking
- `09_risk_heatmap.py` — Risk heatmap
- `11_model_performance.py` — Model comparison and metrics

### app/components/
Reusable UI widgets:
- KPI cards
- Chart cards
- Leaderboard tables
- Map view

### app/config/theme.py
- Central place for styling, navigation, and Plotly layouts

## Core Layer (Business Logic)

This layer has no Streamlit UI code. It is pure Python logic that can be reused anywhere.

### core/utils/config.py
- Loads `configs/config.yaml`
- Provides paths (data, model, outputs)
- Provides thresholds and constants

### core/utils/history_manager.py
- Stores scored trips into `data/processed/trip_history.csv`
- Filters history by date or vehicle

### core/alerts/alert_engine.py
- Creates alerts based on aggressive driving patterns
- Stores alerts into `data/processed/alerts.csv`

### core/scoring/scorer.py
- Loads ML model (`models/svm_model.pkl`)
- Computes DTW features
- Predicts aggressive vs calm

### core/profiling/vehicle_profiler.py
- Creates per-vehicle summaries and comparisons

### core/reports/report_generator.py
- Generates PDF reports (fleet, trip, alert)
- Saves into `outputs/reports/`

## Pipelines Layer

`pipelines/` contains offline scripts for ML development:

- `step1_generate.py` — create synthetic or prepared data
- `step2_eda.py` — exploratory analysis + plots
- `step3_dtw_features.py` — feature extraction
- `step4_svm_train.py` — model training
- `step5_evaluate.py` — evaluation

## Data Flow Overview

1. **Input**: User uploads a CSV or selects a sample from `data/raw/`.
2. **Scoring**: `core/scoring/scorer.py` processes the data and predicts labels.
3. **History**: `core/utils/history_manager.py` appends results to history CSV.
4. **Alerts**: `core/alerts/alert_engine.py` checks for risky patterns.
5. **Reports**: `core/reports/report_generator.py` generates PDFs on request.
6. **UI**: Streamlit pages render everything with charts and tables.

## Configuration

`configs/config.yaml` controls:

- File paths (data, models, outputs)
- Risk thresholds
- Alert rules

Changing this file updates behavior without editing code.

## Why This Architecture Is Production-Ready

- **Clear separation of concerns**: UI vs logic vs data
- **Modular design**: easy to expand features
- **Config-driven**: paths and thresholds are centralized
- **Reusable core logic**: can be reused in APIs or batch jobs

If you want a diagram version, I can generate a simple ASCII or Mermaid flowchart as well.
