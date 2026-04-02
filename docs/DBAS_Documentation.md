# DBAS — Driving Behaviour Analysis System
## Comprehensive Project Documentation

> **Version:** 1.0 | **Last Updated:** March 2026 | **Stack:** Python · Streamlit · DTW · SVM

---

## Table of Contents

1. [Purpose & Overview](#1-purpose--overview)
2. [Technology Stack](#2-technology-stack)
3. [Architecture](#3-architecture)
4. [File Structure](#4-file-structure)
5. [ML Pipeline — Coding Logic](#5-ml-pipeline--coding-logic)
6. [Core Modules — Coding Logic](#6-core-modules--coding-logic)
7. [Application Pages](#7-application-pages)
8. [Configuration System](#8-configuration-system)
9. [Data Flow](#9-data-flow)
10. [UI/UX Design System](#10-uiux-design-system)
11. [Project Guidelines](#11-project-guidelines)
12. [How to Run](#12-how-to-run)

---

## 1. Purpose & Overview

**DBAS (Driving Behaviour Analysis System)** is a professional-grade, enterprise fleet intelligence platform. Its core objective is to detect and classify **aggressive driving behaviour** from raw vehicle speed-profile data, using a combination of **Dynamic Time Warping (DTW) distance features** and a **Support Vector Machine (SVM) classifier**.

### Problem Statement
Fleet operators and road-safety authorities need an automated, data-driven way to:
- Identify vehicles exhibiting aggressive driving patterns (hard braking, rapid acceleration, high-speed fluctuations).
- Track driver safety trends over time.
- Generate actionable alerts before accidents or incidents occur.
- Export formal safety reports in PDF format.

### Solution
DBAS ingests raw trip speed sequences, extracts DTW-based features against reference templates, classifies each trip as **calm** or **aggressive**, assigns a 0–100 **Safety Score**, and presents results through a beautifully designed multi-page Streamlit dashboard. It also manages alerts, vehicle profiles, a driver leaderboard, and generates PDF reports — all from a single local application.

---

## 2. Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Frontend/UI** | Streamlit | 1.55.0 | Multi-page web app framework |
| **UI Navigation** | streamlit-option-menu | 0.4.0 | Horizontal top navigation bar |
| **Charts** | Plotly | 6.6.0 | Interactive charts & gauges |
| **Charts (PDF)** | Matplotlib / Seaborn | 3.10.8 / 0.13.2 | Charts for PDF exports |
| **PDF Generation** | ReportLab | 4.4.10 | PDF report output |
| **ML — Classifier** | scikit-learn SVC | 1.8.0 | SVM with RBF kernel |
| **ML — Feature Extraction** | dtaidistance | 2.4.0 | DTW distance computation |
| **Data Handling** | Pandas | 2.3.3 | DataFrames/CSV I/O |
| **Numerics** | NumPy | 2.4.3 | Array math |
| **Config** | PyYAML | 6.0.3 | YAML configuration parsing |
| **Map** | pydeck | ≥0.9.1 | Fleet map visualisation |
| **Auto-Refresh** | streamlit-autorefresh | ≥1.0.1 | Live-dashboard periodic reloads |
| **Model Storage** | Pickle (stdlib) | — | SVM model serialisation |

---

## 3. Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                        DBAS Application                            │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Streamlit Multi-Page Frontend  (app/)                       │  │
│  │                                                              │  │
│  │  main.py  ──►  Dashboard (KPIs, Charts, Alerts, Gauge)      │  │
│  │  pages/    ──►  Live Scoring, Alerts, Reports,              │  │
│  │                 Vehicle Profile, Leaderboard,               │  │
│  │                 Model Performance, Tutorial                  │  │
│  │                                                              │  │
│  │  config/theme.py  ──►  Design System (CSS, Nav, Layout)     │  │
│  │  components/       ──►  Reusable UI Widgets (KPI, Charts)   │  │
│  └─────────────────────────────────────┬────────────────────────┘  │
│                                        │                           │
│                                        ▼                           │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Core Business Logic  (core/)                                │  │
│  │                                                              │  │
│  │  scoring/scorer.py     ──►  TripScorer (DTW + SVM)          │  │
│  │  alerts/alert_engine.py ──►  AlertEngine (rules + CSV)      │  │
│  │  profiling/vehicle_profiler.py ──► VehicleProfiler          │  │
│  │  reports/report_generator.py   ──► ReportGenerator (PDF)    │  │
│  │  utils/history_manager.py      ──► HistoryManager (CSV)     │  │
│  │  utils/config.py               ──► Config (YAML loader)     │  │
│  └─────────────────────────────────────┬────────────────────────┘  │
│                                        │                           │
│                                        ▼                           │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Data Layer  (data/ + models/)                               │  │
│  │                                                              │  │
│  │  data/processed/trips.csv          ─ Training data          │  │
│  │  data/processed/trips_features.csv ─ DTW features           │  │
│  │  data/processed/trip_history.csv   ─ Scored trip history    │  │
│  │  data/processed/alerts.csv         ─ Generated alerts       │  │
│  │  data/raw/                         ─ User-uploaded CSVs     │  │
│  │  models/svm_model.pkl              ─ Trained SVM model      │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌───────────────────────────────────┐                            │
│  │  Offline ML Pipeline (pipelines/) │                            │
│  │  step1 → step2 → step3 → step4 → step5                        │
│  └───────────────────────────────────┘                            │
└────────────────────────────────────────────────────────────────────┘
```

### Architectural Principles

- **Separation of Concerns**: The front-end (`app/`) never contains business logic. All ML, alerting, and reporting live in `core/`.
- **CSV-based Persistence**: No external database is required. All history, alerts, and data are stored as CSV files locally in `data/processed/`.
- **Configuration-Driven**: All file paths, thresholds, and parameters live in `configs/config.yaml`. The `Config` class resolves them at runtime.
- **Model-as-Artifact**: The trained SVM model is serialised to `models/svm_model.pkl` by the pipeline and loaded by the app at runtime.
- **Reusable Bootstrap**: `app/bootstrap.py` ensures the project root is on `sys.path` for all pages/modules.

---

## 4. File Structure

```
Project1/
│
├── .streamlit/
│   └── config.toml              # Streamlit theme overrides (primary colour, fonts)
│
├── app/                         # Front-end application layer
│   ├── bootstrap.py             # sys.path bootstrap — all pages import this first
│   ├── main.py                  # Dashboard (Entry Point / Home Page)
│   ├── __init__.py
│   │
│   ├── config/
│   │   └── theme.py             # Global CSS, design tokens, nav, layout functions
│   │
│   ├── components/
│   │   ├── kpi_card.py          # Animated KPI card component
│   │   ├── chart_card.py        # Reusable chart wrapper card
│   │   └── leaderboard_table.py # Driver leaderboard table component
│   │
│   └── pages/
│       ├── 01_live_scoring.py   # Upload CSV → real-time DTW+SVM scoring
│       ├── 02_alerts.py         # View, acknowledge, and manage alerts
│       ├── 03_reports.py        # Generate & download PDF reports
│       ├── 04_vehicle_profile.py# Per-vehicle trip analytics & drill-down
│       ├── 05_driver_leaderboard.py # Driver safety ranking
│       ├── 06_model_performance.py  # SVM model metrics & visualisations
│       └── 07_tutorial.py       # In-app usage guide
│
├── core/                        # Business logic layer (no Streamlit imports)
│   ├── scoring/
│   │   └── scorer.py            # TripScorer — DTW extraction + SVM inference
│   ├── alerts/
│   │   └── alert_engine.py      # AlertEngine — rule-based alert generation
│   ├── profiling/
│   │   └── vehicle_profiler.py  # VehicleProfiler — per-vehicle & fleet stats
│   ├── reports/
│   │   └── report_generator.py  # ReportGenerator — PDF via ReportLab
│   └── utils/
│       ├── config.py            # Config — YAML loader & path resolver
│       └── history_manager.py   # HistoryManager — trip history CSV CRUD
│
├── pipelines/                   # Offline ML pipeline scripts (run once)
│   ├── step1_generate.py        # Generate synthetic trip data
│   ├── step2_eda.py             # Exploratory data analysis & plots
│   ├── step3_dtw_features.py    # Compute DTW features (calm/aggressive distances)
│   ├── step4_svm_train.py       # Train & evaluate SVM, save model
│   └── step5_evaluate.py        # Deep evaluation & additional metrics
│
├── configs/
│   └── config.yaml              # Master configuration (paths, thresholds, params)
│
├── data/
│   ├── raw/                     # User-uploaded trip CSVs
│   └── processed/
│       ├── trips.csv            # Training dataset (speed_t0 … speed_t49 + label)
│       ├── trips_features.csv   # DTW-extracted features dataset
│       ├── trip_history.csv     # Scored trip history (persistent)
│       └── alerts.csv           # Generated alerts (persistent)
│
├── models/
│   └── svm_model.pkl            # Serialised trained SVM model
│
├── outputs/
│   └── reports/                 # Generated PDF reports (fleet & vehicle)
│
├── datasets/                    # Sample/demo trip CSV datasets
├── docs/                        # Project documentation
│   ├── architecture.md          # High-level architecture notes
│   ├── algorithm.md             # Algorithm detail notes
│   ├── usage.md                 # Quick-start guide
│   └── DBAS_Documentation.md   # ← This file
│
├── scripts/                     # Utility/maintenance scripts
│   ├── apply_ui_upgrade.py      # One-time UI migration script
│   ├── apply_reports_fix.py     # One-time reports fix script
│   └── download_kaggle_dataset.py # Dataset download helper
│
├── requirements.txt             # Python dependency list
├── README.md                    # Project readme
└── USAGE.md                     # Usage instructions
```

---

## 5. ML Pipeline — Coding Logic

The machine-learning pipeline is a **5-step sequential script suite** found in `pipelines/`. These are executed **once offline** to prepare the model and training data.

### Step 1 — `step1_generate.py` · Synthetic Data Generation

**What it does:** Generates a balanced synthetic dataset of 300 vehicle trips (150 calm, 150 aggressive), each with 50 time-step speed values.

**Coding Logic:**
```
Calm trips:   start at 20–40 km/h, add small random delta ±3 km/h per step, clip to [10, 60]
Aggressive:   start at 20–60 km/h, add large random delta ±15 km/h per step, clip to [0, 120]
```
- Each trip is stored as columns: `trip_id`, `label`, `jerk`, `speed_t0` … `speed_t49`
- `jerk` = mean absolute difference between consecutive speeds (measure of smoothness)
- Output saved to `data/trips.csv`

### Step 2 — `step2_eda.py` · Exploratory Data Analysis

**What it does:** Produces visual plots (jerk histogram, speed std box plot, avg speed profile, DTW scatter) to understand the dataset's structure before modelling.

### Step 3 — `step3_dtw_features.py` · DTW Feature Extraction

**What it does:** Computes the DTW distance from each trip to two **class templates** and saves these as 2 new features.

**Coding Logic:**
```
calm_template      = mean of all calm trip speed sequences
aggressive_template= mean of all aggressive trip speed sequences

For each trip:
  dtw_calm       = dtw.distance(trip_speeds, calm_template)
  dtw_aggressive = dtw.distance(trip_speeds, aggressive_template)
```
- Output: `data/trips_features.csv` with columns `[label, dtw_calm, dtw_aggressive]`
- DTW is used because speed sequences have variable temporal dynamics. DTW aligns sequences non-linearly before computing distance, making it more robust than Euclidean distance for time-series.

### Step 4 — `step4_svm_train.py` · SVM Training

**What it does:** Trains an SVM classifier on the DTW features, evaluates it, generates diagnostic plots, and serialises the model.

**Coding Logic:**
```
X = [dtw_calm, dtw_aggressive]  (2 features per trip)
y = 0 (calm) or 1 (aggressive)

Model: SVC(kernel='rbf', probability=True, random_state=42)
Split: 80% train / 20% test (stratified)

Metrics: Accuracy, F1 Score, Confusion Matrix
Plots:   confusion_matrix.png, decision_boundary.png
Output:  models/svm_model.pkl
```
- The **RBF kernel** is chosen for its ability to learn non-linear decision boundaries in the 2D DTW feature space.
- `probability=True` enables `.predict_proba()` which powers the Safety Score.

### Step 5 — `step5_evaluate.py` · Deep Evaluation

**What it does:** Runs additional evaluation metrics, model comparisons, and generates extra diagnostic charts used by the Model Performance page.

---

## 6. Core Modules — Coding Logic

### `core/utils/config.py` — Config

Loads `configs/config.yaml` into a typed Python object using PyYAML.

- **`Config.load(path)`**: Resolves the YAML path relative to the project root using `Path(__file__).resolve().parents[2]`, with a fallback to a legacy root `config.yaml`. Returns a `Config` instance.
- **`Config.get_risk_label(score)`**: Maps a numeric score to a risk label string using the configured low/medium/high thresholds.
- Every core module calls `Config.load()` in its `__init__` to get file paths and parameters.

---

### `core/scoring/scorer.py` — TripScorer

The heart of the ML inference pipeline.

**Initialisation:**
```python
1. Load config → get MODEL_PATH, DATA_PATH
2. Load svm_model.pkl via pickle
3. Load trips.csv, compute:
   - calm_template = mean(calm trip speed vectors)
   - aggressive_template = mean(aggressive trip speed vectors)
```

**`score_trip(speed_array)` method:**
```
1. dtw_calm       = dtw.distance(speed_array, calm_template)
2. dtw_aggressive = dtw.distance(speed_array, aggressive_template)
3. X = [[dtw_calm, dtw_aggressive]]
4. label      = model.predict(X)         → "calm" or "aggressive"
5. proba      = model.predict_proba(X)   → [p_calm, p_aggressive]
6. confidence = max(proba) * 100
7. safety_score = 100 - (p_aggressive * 100)  ← key metric
```

**Safety Score Formula:**
`safety_score = 100 − (probability_of_aggressive × 100)`
- Score of 100 → model is 100% confident the trip is calm.
- Score of 0 → model is 100% confident the trip is aggressive.
- Score of 70 is the "safe threshold" used across the UI.

**`score_dataframe(df)` method:** Applies `score_trip` to every row in a DataFrame containing `speed_t0` … `speed_t49`, adding `label`, `confidence`, `safety_score` columns.

---

### `core/alerts/alert_engine.py` — AlertEngine

Rule-based alert generation system. Alerts are persisted in `data/processed/alerts.csv`.

**Alert Schema:** `alert_id, vehicle_id, timestamp, alert_type, message, trip_count, severity, status`

**`check_trip(vehicle_id, label, safety_score)` logic:**
```
Rule 1 — Critical Alert:
  IF label == "aggressive" AND safety_score < 30:
    → Create "Critical Alert" with severity "High"

Rule 2 — Repeat Offender Alert:
  Load last N trips from history for this vehicle (N = config.ALERT_CONSECUTIVE_TRIPS, default 3)
  IF all N most recent trips were "aggressive":
    → Create "Repeat Offender Alert" with severity "Medium"

All new alerts are appended to alerts.csv.
```

**Other Methods:**
- `get_active_alerts(vehicle_id=None)`: Returns alerts from the last 24h with status Active or Acknowledged.
- `update_alert_status(alert_id, new_status)`: Updates a single alert's status in-place in the CSV.
- `get_alert_summary()`: Returns a count by alert type.

---

### `core/utils/history_manager.py` — HistoryManager

Manages the persistent log of all scored trips.

**History Schema:** `trip_id, vehicle_id, timestamp, label, confidence, safety_score, dtw_calm, dtw_aggressive`

**`save_trips(df, vehicle_id)`:** Appends a batch of scored rows (from the Live Scoring page) to `trip_history.csv`, stamping each with `vehicle_id` and current UTC timestamp.

**`load_history(vehicle_id, start_date, end_date)`:** Loads the full history CSV and applies optional filters. Returns a DataFrame.

**`get_summary_stats(vehicle_id)`:** Computes aggregate stats: `total_trips`, `pct_aggressive`, `avg_safety_score`, `worst_trip_score`, `best_trip_score`.

---

### `core/profiling/vehicle_profiler.py` — VehicleProfiler

Provides per-vehicle and fleet-level aggregations built on top of `HistoryManager`.

**`get_vehicle_profile(vehicle_id)`:** Returns a dictionary with:
- `total_trips`, `pct_aggressive`, `avg_safety_score`
- `risk_trend`: list of the 10 most recent safety scores (for spark-line charts)
- `worst_trip`, `best_trip`, `most_common_label`

**`compare_vehicles(vehicle_id_list)`:** Builds a DataFrame of profiles for a list of vehicles, sorted by `avg_safety_score` ascending (riskiest first).

**`get_fleet_summary()`:** Fleet-wide aggregates: total vehicles, total trips, avg safety score, % aggressive.

---

### `core/reports/report_generator.py` — ReportGenerator

Generates three types of PDF reports using ReportLab. Charts embedded via Matplotlib.

| Method | Report Type | Contents |
|---|---|---|
| `generate_trip_report(vehicle_id, scored_df)` | Per-vehicle | Summary table, safety-score bar chart, risk level text |
| `generate_fleet_report(comparison_df)` | Fleet-wide | AI insights, vehicle rankings table, fleet safety chart |
| `generate_alert_report(alerts_df, vehicle_id)` | Alert | Alert summary table, alert-type bar chart, recent alert list |

**PDF Build Pattern (ReportLab Story):**
```python
story = []
story.append(Paragraph(...))   # Title
story.append(Table(...))       # Data tables
story.append(Image(...))       # Matplotlib chart embedded as PNG
doc.build(story)               # Render to PDF
# Cleanup temp PNG after build
```

All reports are saved to `outputs/reports/` with timestamped filenames.

---

## 7. Application Pages

### `app/main.py` — Fleet Dashboard (Home)

The home page and entry point. Displays fleet-level KPIs, AI insights, analytics charts, alert summary, and a fleet health gauge.

| Section | Description |
|---|---|
| **KPI Cards** | Total Trips, Fleet Safety Score, Active Alerts, Aggressive % |
| **AI Insights** | Auto-generated text insights: worst vehicle, weekly trend delta, best vehicle |
| **Trip Classification Chart** | Donut chart of calm vs aggressive trip share |
| **Safety Score Trend** | Line chart with spline smoothing and safe-threshold line |
| **Recent Alerts** | Table of last 24h active alerts |
| **Fleet Health Gauge** | Plotly gauge indicator showing fleet avg safety score |

---

### `pages/01_live_scoring.py` — Live Trip Scorer

**Purpose:** Core scoring interface. Users upload a trip CSV or select a pre-loaded dataset, enter a Vehicle ID, and trigger real-time classification.

**Flow:**
```
1. User selects/uploads CSV (must have speed_t0 … speed_t49 columns)
2. Click "Score Trips" button
3. TripScorer.score_dataframe() runs DTW+SVM inference
4. Results shown: KPI cards, safety-score bar chart, classification donut, detail table
5. HistoryManager.save_trips() persists the results
6. AlertEngine.check_trip() fires for each trip → warnings displayed inline
7. Download button for the scored CSV
```

---

### `pages/02_alerts.py` — Alert Management

**Purpose:** Full alert management interface. Allows operators to view, filter, acknowledge, and dismiss alerts.

**Features:**
- Filter by vehicle, severity, status
- One-click status updates (Active → Acknowledged → Dismissed)
- Alert statistics summary cards
- Generate alert PDF report button

---

### `pages/03_reports.py` — Reports

**Purpose:** PDF report generation hub.

**Report Types Available:**
1. **Vehicle Trip Report** — Select a vehicle, generate a personalised PDF
2. **Fleet Intelligence Report** — Fleet-wide comparison report with AI insights
3. **Alert Report** — Export alert log to PDF

Past generated reports are listed with download links.

---

### `pages/04_vehicle_profile.py` — Vehicle Profile

**Purpose:** Deep per-vehicle analytics. Select any vehicle ID from history to view a full profile.

**Displays:**
- Profile at-a-glance: total trips, avg score, % aggressive, best/worst trip
- Risk trend spark line (last 10 trips)
- Detailed trip history table with filters
- Comparison table across vehicles

---

### `pages/05_driver_leaderboard.py` — Driver Leaderboard

**Purpose:** Ranks all vehicles/drivers by average safety score. Highlights top performers and flagged risk vehicles.

- Sortable leaderboard table
- Colour-coded safety tiers (Green ≥70, Amber 40–70, Red <40)

---

### `pages/06_model_performance.py` — Model Performance

**Purpose:** Transparency into the underlying ML model's accuracy and decision logic.

**Displays:**
- Classification metrics (accuracy, F1 score, precision, recall)
- Confusion matrix heatmap
- SVM decision boundary scatter plot in DTW feature space
- Feature importance / DTW distance distributions
- Model comparison across alternative algorithms

---

### `pages/07_tutorial.py` — Tutorial

**Purpose:** In-app user guide explaining how to use the application, including data format requirements, workflow steps, and scoring interpretation.

---

## 8. Configuration System

All configuration lives in **`configs/config.yaml`**:

```yaml
model_path:    models/svm_model.pkl      # Trained SVM model location
data_path:     data/processed/trips.csv  # Training/template dataset
features_path: data/processed/trips_features.csv
history_path:  data/processed/trip_history.csv
alerts_path:   data/processed/alerts.csv
reports_path:  outputs/reports/

risk_thresholds:
  low:    0.3   # Score < 30  → Low Risk
  medium: 0.6   # Score < 60  → Medium Risk
  high:   0.8   # Score < 80  → High Risk
                # Score ≥ 80  → Critical

n_clusters:             4   # (reserved for future clustering features)
alert_consecutive_trips: 3  # Trips in a row before "Repeat Offender" alert fires
```

The `Config` class resolves all paths **relative to the project root**, making the project portable across machines without path edits.

---

## 9. Data Flow

```
CSV Upload (user)
       │
       ▼
 Live Scoring Page
       │
       ├──► TripScorer.score_dataframe()
       │         │
       │         ├── dtw.distance(trip, calm_template)    ──┐
       │         ├── dtw.distance(trip, aggressive_template) ┤ → SVM.predict_proba()
       │         └── safety_score = 100 - p_aggressive * 100 ┘
       │
       ├──► HistoryManager.save_trips()  →  trip_history.csv
       │
       └──► AlertEngine.check_trip()    →  alerts.csv
                    │
                    └──► Dashboard  ←  HistoryManager.load_history()
                                   ←  AlertEngine.get_active_alerts()
                                   ←  VehicleProfiler.get_fleet_summary()
                                            │
                                            └──► ReportGenerator → PDF Output
```

---

## 10. UI/UX Design System

The design system lives entirely in `app/config/theme.py`.

### Design Language
- **Glassmorphism**: All cards/surfaces use `backdrop-filter: blur(24px)` with semi-transparent backgrounds.
- **Gradient Accents**: Primary brand gradient `#2563eb → #7c3aed` (blue to purple).
- **Light/Dark Mode**: Full dark-mode support via a toggle button. Dark overrides are injected as a secondary `<style>` block.
- **Micro-animations**: Cards float up on load (`@keyframes floatUp`), KPI icons rotate/scale on hover, logo rotates on hover.

### Design Tokens (CSS Variables)
```
--blue, --green, --amber, --red     ← Semantic colours
--surface, --surface2, --surface3   ← Glass surface layers
--border, --border-med              ← Border opacity variants
--font-d (Outfit), --font-b (Inter), --font-m (Space Grotesk)
--radius, --radius-lg, --radius-xl  ← Border radius scale
--shadow-sm, --shadow, --shadow-lg  ← Box shadow scale
--glass-blur, --glass-border        ← Glassmorphism tokens
```

### Key UI Components

| Component | Class | Description |
|---|---|---|
| Top Bar | `.dbas-topbar` | Sticky, glassmorphic header with brand, live indicator, clock |
| Navigation | `option_menu` | Horizontal icon+text nav bar, highlights active page |
| KPI Card | `.kpi` | Animated stat card with icon, value, delta badge |
| Section Header | `.dbas-section` | All-caps label with trailing gradient rule |
| Content Card | `.content-card` | Glass panel wrapping chart or content blocks |
| Alert Card | `.dbas-alert-card` | Colour-coded alert row with left border accent |
| Page Footer | `page_footer()` | Version info, sync time, Tutorial shortcut button |

### Navigation System
```python
NAV_PAGE_MAP = {
    "Dashboard":          "main.py",
    "Live Scoring":       "pages/01_live_scoring.py",
    "Driver Leaderboard": "pages/05_driver_leaderboard.py",
    "Model Performance":  "pages/06_model_performance.py",
    "Vehicle Profile":    "pages/04_vehicle_profile.py",
    "Alerts":             "pages/02_alerts.py",
    "Reports":            "pages/03_reports.py",
}
```
Navigation is handled by `render_nav(current_page)` which uses `st.switch_page()` on selection change.

---

## 11. Project Guidelines

### Input Data Format
Trip CSV files uploaded to Live Scoring **must** contain these columns:

| Column | Type | Description |
|---|---|---|
| `speed_t0` … `speed_t49` | float | Speed values (km/h) at 50 time steps |
| `trip_id` *(optional)* | string | Trip identifier (auto-generated if absent) |
| Any other columns are ignored. | | |

### Safety Score Interpretation

| Score Range | Colour | Meaning |
|---|---|---|
| 70 – 100 | 🟢 Green | Safe — calm, smooth driving |
| 40 – 69 | 🟡 Amber | Moderate — occasional risky events |
| 0 – 39 | 🔴 Red | High Risk / Critical — aggressive driving |

### Alert Severity Levels

| Severity | Trigger Condition |
|---|---|
| **High** (Critical Alert) | A single trip with safety_score < 30 |
| **Medium** (Repeat Offender) | Last 3 consecutive trips all classified as aggressive |

### Adding a New Page
1. Create `app/pages/NN_page_name.py` with the correct sequential number.
2. Add `import bootstrap` as the **first line**.
3. Call `apply_theme()`, `render_topbar()`, `render_nav("Page Name")` at the top.
4. Add the page to `NAV_OPTIONS`, `NAV_ICONS`, and `NAV_PAGE_MAP` in `app/config/theme.py`.

### Adding a New Core Module
1. Create a new directory under `core/` with an `__init__.py`.
2. Import `Config` via `from core.utils.config import Config`.
3. Never import Streamlit into `core/` — keep it UI-agnostic.
4. If the module needs new config values, add them to `configs/config.yaml` and update the `Config` class.

### Code Style Guidelines
- **Naming**: Classes use PascalCase. Functions and variables use snake_case.
- **Docstrings**: Every method should have a single-line comment above it explaining intent.
- **No magic numbers**: All thresholds and paths come from `Config`.
- **CSV-first persistence**: Use append mode (`mode='a'`) for history and alert writes to avoid full rewrites.
- **Defensive loading**: Always check `if not df.empty` before operating on DataFrames loaded from CSV.

### Re-training the Model
If the underlying data changes, re-run the pipeline in order:
```bash
python pipelines/step1_generate.py   # Re-generate data
python pipelines/step2_eda.py        # (optional) EDA
python pipelines/step3_dtw_features.py  # Re-extract DTW features
python pipelines/step4_svm_train.py  # Retrain SVM, saves new model
python pipelines/step5_evaluate.py   # Evaluate
```
The app picks up the new `models/svm_model.pkl` automatically on next run.

---

## 12. How to Run

### Prerequisites
- Python 3.10+
- All dependencies installed:
```bash
pip install -r requirements.txt
```

### First-Time Setup (if model doesn't exist)
```bash
python pipelines/step1_generate.py
python pipelines/step3_dtw_features.py
python pipelines/step4_svm_train.py
```

### Start the Application
```bash
# From the project root:
python -m streamlit run app/main.py
```
The app opens at `http://localhost:8501`.

### Directory for User Datasets
Place pre-loaded trip CSVs in:
```
data/raw/
```
These appear in the dropdown on the Live Scoring page.

---

*DBAS v1.0 — Developed for Fleet Safety Intelligence | DTW + SVM Classification Engine*
