# Algorithm

This document explains the ML algorithm used in the project in simple terms, step by step.

## Goal

Classify driving trips as:

- **Calm** (safe driving)
- **Aggressive** (risky driving)

The algorithm uses **DTW (Dynamic Time Warping)** features + **SVM (Support Vector Machine)** classification.

## Data Format

Each trip is represented as a time-series of speed values:

- `speed_t0, speed_t1, ..., speed_t49`

So every row has 50 time steps. The model does **not** look at raw GPS or route data, only speed patterns.

## Step 1 — Feature Extraction with DTW

DTW compares two sequences and tells how similar their shapes are, even if one is faster/slower in time.

### In this project:

- A **calm template** is built from safe trips
- An **aggressive template** is built from risky trips

For each trip we compute:

- `dtw_calm` = distance to calm template
- `dtw_aggressive` = distance to aggressive template

Smaller distance means more similar.

So a calm trip should have:

- low `dtw_calm`
- higher `dtw_aggressive`

## Step 2 — SVM Classification

The two DTW features are fed into a **Support Vector Machine (SVM)** classifier.

Why SVM?

- Works well with small feature sets
- Creates a clear boundary between classes
- Strong performance on non-linear patterns (RBF kernel)

The output of the SVM is:

- `label`: calm or aggressive
- `confidence`: model probability

## Step 3 — Safety Score

The app converts the prediction into a **safety score** (0–100).

- Higher score = safer
- Lower score = more risky

This is used for dashboards, KPI cards, and reports.

## Step 4 — Alerts

Alerts are generated when:

- A trip is aggressive and score is below a threshold
- A vehicle has **N consecutive aggressive trips**

These rules are configurable in `configs/config.yaml`.

## Outputs

For each trip, the system produces:

- `trip_id`
- `label` (calm/aggressive)
- `confidence`
- `safety_score`
- `dtw_calm`, `dtw_aggressive`

## Summary (Simple Explanation)

1. Measure how similar a trip is to safe vs risky behavior using DTW
2. Feed those two numbers into an SVM model
3. Predict calm/aggressive and compute a safety score
4. Save results and trigger alerts if needed

If you want the mathematical formulas for DTW and SVM, I can add them as an appendix.
