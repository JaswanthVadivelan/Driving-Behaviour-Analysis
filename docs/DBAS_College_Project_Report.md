# DBAS (Driving Behaviour Analysis System) - College Project Report

## Abstract

Driving Behaviour Analysis System (DBAS) is a data-driven application designed to analyze vehicle trip speed patterns and classify driving behaviour as calm or aggressive. The system uses a combination of Dynamic Time Warping (DTW) for feature extraction and Support Vector Machine (SVM) for classification. It is built as a Streamlit-based web application with a modular Python architecture, allowing users to upload trip data, score driving patterns, generate alerts, view trip history, and produce PDF reports.

The project demonstrates how machine learning, structured data handling, and software engineering principles can be combined to build a practical safety and monitoring solution. It focuses on efficient trip analysis, clear visualization, configurable thresholds, and persistent history management using local CSV-based storage.

---

## 1. Introduction

DBAS is an intelligent driving analytics project that helps identify risky driving behaviour from vehicle speed time-series data. In real-world fleet operations, unsafe driving can lead to accidents, high maintenance costs, fuel wastage, and poor vehicle utilization. DBAS addresses this problem by converting raw trip data into actionable insights.

The application analyzes 50 time-step speed samples per trip, extracts similarity-based features using DTW, and classifies each trip into one of two categories:

- Calm
- Aggressive

Along with the classification result, the system generates a safety score, stores historical records, raises alerts when risky behaviour is detected, and provides downloadable reports for analysis and audit purposes.

---

## 2. Project Objectives

The main objectives of this project are:

1. To design a system that can analyze vehicle driving behaviour from time-series speed data.
2. To classify trips into calm and aggressive driving categories using machine learning.
3. To compute a safety score for each trip for easy interpretation by users.
4. To store trip results in a structured and reusable format.
5. To generate alerts for repeated or highly risky behaviour.
6. To provide an interactive web interface for viewing, filtering, and exporting results.
7. To demonstrate practical use of DTW, SVM, CSV-based persistence, and dashboard design.

---

## 3. Why We Created This Project

This project was created to solve a real operational and safety problem. In many fleet or transport systems, vehicle speed data is available, but it is not always analyzed in a meaningful way. DBAS was developed to convert raw speed sequences into a measurable safety output.

### Reasons for creating DBAS:

- To detect aggressive driving patterns early
- To support fleet safety monitoring
- To provide a simple but effective ML-based classification system
- To create a reusable analytical tool for trip-level monitoring
- To produce reports that can be used for review, coaching, or documentation

The project also serves as a strong academic example because it combines:

- Data preprocessing
- Feature extraction
- Machine learning classification
- Dashboard development
- Alert generation
- File-based data persistence
- Report generation

---

## 4. Problem Statement

The problem addressed by DBAS is the lack of an automated mechanism to identify unsafe driving behaviour from speed profile data.

Traditional manual inspection of trip records is time-consuming and inefficient. It becomes difficult to analyze a large number of trips, compare drivers, and track long-term behaviour trends. DBAS solves this by automating the complete analysis pipeline:

- Input trip speed data
- Compare the trip with safe and risky templates
- Predict the driving category
- Generate a safety score
- Save the result
- Trigger alerts if needed

---

## 5. System Overview

DBAS is a multi-page Streamlit application built around a layered architecture. The project is separated into three major layers:

1. Presentation layer - Streamlit UI
2. Business logic layer - scoring, alerts, profiling, reporting
3. Data and model layer - datasets, CSV history, and trained model artifacts

This separation makes the system easier to maintain, understand, and extend.

---

## 6. Technology Stack

### Frontend / UI
- Streamlit for the web interface
- Plotly for interactive visualizations

### Machine Learning
- Pandas for data handling
- NumPy for numerical operations
- dtaidistance for DTW feature computation
- scikit-learn SVM for classification

### Storage and Output
- CSV files for trip history and alerts
- Pickle file for storing the trained model
- ReportLab for PDF generation

### Configuration
- YAML configuration file for paths, thresholds, and parameters

---

## 7. Architecture

DBAS follows a modular architecture that separates user interface, business logic, and data processing.

### 7.1 High-Level Architecture

```
User
  |
  v
Streamlit UI
  |
  +--> Live Trip Upload / Scoring
  +--> Trip History
  +--> Alerts
  +--> Reports
  +--> Vehicle Profile
  |
  v
Core Logic
  |
  +--> DTW Feature Extraction
  +--> SVM Classification
  +--> Alert Rules
  +--> History Management
  +--> Report Generation
  |
  v
Data Layer
  |
  +--> CSV files
  +--> Model file
  +--> Generated reports
```

### 7.2 Architectural Design Principles

The project is designed using the following principles:

- Separation of concerns: UI and logic are kept in different modules
- Reusability: core functions can be reused in other applications
- Config-driven design: thresholds and paths are controlled centrally
- Local persistence: results are saved without requiring an external database
- Scalability by modularity: each feature is isolated into a dedicated module

### 7.3 Why This Architecture Is Effective

This architecture is effective because it keeps the system clean, easy to debug, and simple to extend. If a new page, report format, or scoring rule is needed later, it can be added without rewriting the complete application.

---

## 8. Project Structure

The repository is organized in a modular form:

```text
Project1/
|-- app/                      # Streamlit application layer
|-- core/                     # Business logic modules
|-- pipelines/                # Offline ML preparation scripts
|-- configs/                  # YAML configuration files
|-- data/                     # Raw and processed CSV datasets
|-- models/                   # Trained ML model artifacts
|-- outputs/                  # Reports and generated results
|-- datasets/                 # Sample input files
|-- docs/                     # Documentation files
|-- scripts/                  # Utility scripts
|-- README.md
|-- requirements.txt
|-- USAGE.md
```

### 8.1 App Layer

The `app/` folder contains the Streamlit user interface. It is responsible for displaying:

- Dashboard metrics
- Trip scoring page
- Alert center
- Reports page
- Vehicle profile page
- Driver leaderboard and analysis views

### 8.2 Core Layer

The `core/` folder contains the backend logic of the application:

- Scoring logic
- DTW feature extraction
- Alert generation
- Vehicle profiling
- History management
- Report generation

### 8.3 Pipeline Layer

The `pipelines/` folder contains offline scripts used to prepare and train the machine learning model:

- Data generation
- Exploratory data analysis
- Feature extraction
- Model training
- Model evaluation

### 8.4 Data Layer

The `data/` and `models/` folders store the actual working artifacts:

- Trip datasets
- Feature datasets
- Scored history
- Alerts
- Trained model file

---

## 9. Modules and Their Purpose

### 9.1 Scoring Module

The scoring module loads the trained model, extracts DTW features from trip data, and predicts whether a trip is calm or aggressive.

### 9.2 Alert Module

The alert module applies rule-based conditions to identify critical behaviour. It can raise alerts for:

- Aggressive trips
- Low safety scores
- Repeated risky driving patterns

### 9.3 History Module

The history module stores scored trips in CSV format and allows filtering by:

- Vehicle ID
- Date
- Label
- Safety score range

### 9.4 Vehicle Profiling Module

This module summarizes behaviour per vehicle and helps compare performance across multiple trips.

### 9.5 Report Generation Module

The report module creates structured PDF files for trip reports, fleet reports, and alert reports.

---

## 10. Input and Data Format

The system works with speed time-series data.

Each trip is represented by 50 sequential speed values:

```text
speed_t0, speed_t1, speed_t2, ..., speed_t49
```

This means every row in the input dataset represents one trip. The model focuses on the shape and variation of the speed pattern rather than GPS coordinates or route geometry.

### Example Data Columns

- `trip_id`
- `label`
- `speed_t0` to `speed_t49`
- `dtw_calm`
- `dtw_aggressive`
- `safety_score`
- `confidence`

---

## 11. Algorithm

DBAS uses a two-stage ML approach:

1. DTW-based feature extraction
2. SVM-based classification

### 11.1 Step 1: Feature Extraction Using DTW

Dynamic Time Warping measures similarity between two time-series sequences even if they are stretched or compressed in time.

DBAS uses two reference patterns:

- Calm template
- Aggressive template

For each trip, the system calculates:

- Distance from calm template
- Distance from aggressive template

These distances become the input features for the classifier.

### 11.2 Step 2: Classification Using SVM

The extracted DTW features are passed into a Support Vector Machine classifier. SVM is suitable here because:

- It works well with small feature vectors
- It separates two classes effectively
- It can model non-linear boundaries using an RBF kernel

The model predicts whether the trip is calm or aggressive.

### 11.3 Step 3: Safety Score Calculation

The classification output is converted into a safety score from 0 to 100.

- Higher score means safer driving
- Lower score means riskier driving

This makes the output more understandable for users who may not be familiar with ML labels.

### 11.4 Step 4: Alert Logic

After scoring, the system evaluates alert conditions such as:

- Safety score below threshold
- Aggressive label
- Consecutive risky trips from the same vehicle

If conditions are satisfied, an alert is recorded.

---

## 12. Detailed Workflow

### 12.1 Data Preparation

Before deployment, the offline pipeline prepares the training data. The data is cleaned, transformed, and converted into a format suitable for DTW feature extraction and SVM training.

### 12.2 Model Training

The model training stage uses the computed features to train an SVM classifier. The trained model is saved as a reusable artifact.

### 12.3 Live Scoring

When a user uploads a new trip CSV file:

1. The system validates the input format.
2. It extracts the 50 speed values.
3. It computes DTW distances.
4. It predicts the class label.
5. It calculates the safety score.
6. It stores the result in history.
7. It checks whether an alert must be raised.

### 12.4 Reporting

The reporting module uses stored results to build structured PDF documents. These reports help in performance review, coaching, and documentation.

---

## 13. User Interface Features

DBAS provides a dashboard-style interface with multiple pages.

### Main Features

- Overview dashboard with KPIs
- Live trip scoring
- Trip history analysis
- Vehicle comparison
- Alert management
- Report generation
- Model performance view

### Benefits of the UI

- Easy to use for non-technical users
- Interactive charts for better understanding
- Separate pages for different tasks
- Clean layout for quick analysis

---

## 14. Data Flow

The data flow in DBAS is as follows:

1. User uploads trip data
2. The app validates the file format
3. DTW features are extracted
4. SVM predicts the driving category
5. Safety score is computed
6. Result is stored in history
7. Alert rules are checked
8. Report can be generated if needed

This flow ensures that every trip is processed in a consistent and traceable way.

---

## 15. Advantages of the System

- Automated analysis of driving behaviour
- Reduced manual effort
- Clear and interpretable score output
- Modular and maintainable codebase
- Reusable reports and history logs
- Configurable thresholds and rules
- Suitable for academic and demo purposes

---

## 16. Limitations

Like any analytical system, DBAS also has limitations:

- It depends on the quality of input speed data
- It uses a fixed-length time-series format
- It is primarily designed for binary classification
- Results are limited to the feature engineering strategy used

These limitations can be addressed in future versions with GPS integration, larger datasets, or advanced sequence models.

---

## 17. Future Enhancements

The project can be extended in several ways:

- Add GPS route analysis
- Use deep learning models for sequence classification
- Add real-time streaming input support
- Store data in a relational database instead of CSV
- Include driver-wise performance trends
- Add authentication and role-based access
- Export reports in more formats

---

## 18. Conclusion

DBAS is a complete driving behaviour analytics project that demonstrates the practical use of machine learning, structured data management, and dashboard design. It successfully classifies driving trips, generates safety scores, stores historical records, and produces alerts and reports.

The project is useful both as a college academic submission and as a practical demonstration of how ML and software engineering can be combined to solve a real-world safety monitoring problem.

---

## 19. Short Summary

DBAS analyzes vehicle speed time-series data, extracts DTW features, classifies trips using an SVM model, calculates a safety score, stores the results, and generates alerts and reports through a Streamlit web application.

