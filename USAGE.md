# Driving Behaviour Analysis System (DBAS) — Usage Guide

This guide explains the purpose of the application, where it is used, how to use it step by step, and includes a sample CSV template for uploads.

## Purpose
DBAS analyzes vehicle trip speed profiles to detect aggressive driving. It uses DTW (Dynamic Time Warping) features and an SVM model to score trips, generate alerts, and produce reports.

## Where It Is Used
- Fleet monitoring dashboards for safety teams.
- Driver coaching programs to identify risky behavior.
- Operations reviews for vehicle performance and incident prevention.
- Compliance or audit reporting (PDF reports).

## How It Works (High Level)
1. You provide a trip speed profile (50 time-step speed values).
2. The system compares the trip to learned calm/aggressive templates.
3. It predicts a label and safety score.
4. It stores history and generates alerts + reports.

## Step-by-Step: Run the App
1. Install dependencies
   - `pip install -r requirements.txt`
2. Start the app
   - `streamlit run app.py`
3. Open the browser
   - The app opens at `http://localhost:8501`

## Step-by-Step: Use the App
1. **Dashboard**
   - View high-level fleet metrics and charts.
2. **Live Scoring**
   - Upload a CSV file with `speed_t0` to `speed_t49` columns.
   - Optionally save the file to `datasets/`.
   - Get predictions, safety score, and auto-logging.
3. **Trip History**
   - Filter by vehicle ID and date range.
   - Review past trips and safety scores.
4. **Alerts**
   - View auto-generated alerts for risky trips.
5. **Reports**
   - Generate Trip Report (per vehicle).
   - Generate Fleet Report (all vehicles).
   - Generate Alert Report (fleet or per vehicle).
6. **Vehicle Profile**
   - Review a single vehicle’s summary and trends.

## CSV Template for Uploads
The Live Scoring page expects **50 columns** named:

```
speed_t0,speed_t1,speed_t2,speed_t3,speed_t4,speed_t5,speed_t6,speed_t7,speed_t8,speed_t9,
speed_t10,speed_t11,speed_t12,speed_t13,speed_t14,speed_t15,speed_t16,speed_t17,speed_t18,speed_t19,
speed_t20,speed_t21,speed_t22,speed_t23,speed_t24,speed_t25,speed_t26,speed_t27,speed_t28,speed_t29,
speed_t30,speed_t31,speed_t32,speed_t33,speed_t34,speed_t35,speed_t36,speed_t37,speed_t38,speed_t39,
speed_t40,speed_t41,speed_t42,speed_t43,speed_t44,speed_t45,speed_t46,speed_t47,speed_t48,speed_t49
```

### Example (Single Trip Row)
```
speed_t0,speed_t1,speed_t2,speed_t3,speed_t4,speed_t5,speed_t6,speed_t7,speed_t8,speed_t9,speed_t10,speed_t11,speed_t12,speed_t13,speed_t14,speed_t15,speed_t16,speed_t17,speed_t18,speed_t19,speed_t20,speed_t21,speed_t22,speed_t23,speed_t24,speed_t25,speed_t26,speed_t27,speed_t28,speed_t29,speed_t30,speed_t31,speed_t32,speed_t33,speed_t34,speed_t35,speed_t36,speed_t37,speed_t38,speed_t39,speed_t40,speed_t41,speed_t42,speed_t43,speed_t44,speed_t45,speed_t46,speed_t47,speed_t48,speed_t49
12,13,15,16,18,20,22,24,23,22,21,22,24,26,28,29,31,33,35,36,35,34,33,32,31,30,29,28,27,26,25,24,24,23,22,22,21,20,19,19,18,18,17,16,16,15,14,14,13,12
```

## Tips
- Ensure all speed values are numeric.
- Multiple rows = multiple trips scored in one upload.
- For best results, keep the 50 time steps consistent per trip.
