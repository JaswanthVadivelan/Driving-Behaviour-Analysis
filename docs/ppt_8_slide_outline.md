# 8-Slide PPT Content: Driving Behaviour Data

Slide 1 - Title & Objective
- Title: Driving Behaviour Analysis System - Data Overview
- Objective: classify trips as calm vs aggressive using speed time-series
- Data unit: one trip = 50 time-step speed sequence (speed_t0 to speed_t49)
- Current dataset: 300 trips, 150 calm and 150 aggressive
- Data status: synthetic dataset generated for model prototyping

Slide 2 - Data Assets & File Map
- Raw samples: data/raw/sample_trips.csv and per-vehicle trip files in data/raw/
- Processed trips: data/processed/trips.csv (300 rows, 53 columns)
- Feature set: data/processed/trips_features.csv (300 rows, 55 columns)
- Operational logs: data/processed/trip_history.csv (220 rows, 8 columns)
- Alerts log: data/processed/alerts.csv (195 rows, 8 columns)

Slide 3 - Core Trip Dataset Schema (trips.csv)
- Primary keys: trip_id, label
- Numeric features: jerk, speed_t0 to speed_t49 (50 time steps)
- Units: speed in km/h, jerk = mean absolute speed change per step
- Class balance: calm 150, aggressive 150
- Recommended visuals: sample trip line plot, schema table

Slide 4 - Synthetic Data Generation Logic
- Calm trips: start speed 20-40 km/h, step change +/-3, clipped to 10-60
- Aggressive trips: start speed 20-60 km/h, step change +/-15, clipped to 0-120
- Jerk definition: mean(|speed_t(i) - speed_t(i-1)|) across 49 steps
- Trips per class: 150 calm, 150 aggressive
- Random seed: 42 for reproducibility

Slide 5 - Feature Engineering (trips_features.csv)
- Adds DTW distances to two templates
- dtw_calm = DTW distance to mean calm speed profile
- dtw_aggressive = DTW distance to mean aggressive speed profile
- Mean DTW values
- Calm trips: dtw_calm 60.44 | dtw_aggressive 129.09
- Aggressive trips: dtw_calm 223.88 | dtw_aggressive 188.52
- Recommended visual: DTW scatter (calm vs aggressive separation)

Slide 6 - EDA Highlights (from trips.csv)
- Mean jerk by label: calm 1.47 vs aggressive 7.04
- Mean max speed by label: calm 37.88 km/h vs aggressive 83.67 km/h
- Mean speed std dev: calm 4.56 km/h vs aggressive 19.38 km/h
- Recommended visuals: average speed profile line chart, jerk histogram, max speed boxplot, speed std boxplot

Slide 7 - Operational Data (Trip History & Alerts)
- trip_history.csv columns: trip_id, vehicle_id, timestamp, label, confidence, safety_score, dtw_calm, dtw_aggressive
- Trip history time span: 2026-03-15 04:35:33.263187 to 2026-03-22 03:17:00.172176
- alerts.csv columns: alert_id, vehicle_id, timestamp, alert_type, message, trip_count, severity, status
- Alert counts by type: {'Critical Alert': 105, 'Repeat Offender Alert': 90}
- Alert severity breakdown: {'Medium': 127, 'High': 68}, status: {'Active': 195}

Slide 8 - Data Usage in the App & Model
- Pipeline: trips.csv -> DTW features -> SVM classifier -> safety_score and alerts
- Risk thresholds from config.yaml: low 0.3, medium 0.6, high 0.8
- Data quality notes
- Trip history DTW fields are currently NaN in stored history
- Synthetic data is ideal for demos; replace with real telematics for deployment
- Suggested next step: run EDA pipelines to generate charts for slides
