# src/scorer.py
# This module defines a TripScorer for DTW-based SVM scoring.

# Import pickle for loading the trained model.
import pickle

# Import numpy for numerical operations.
import numpy as np

# Import pandas for data handling.
import pandas as pd

# Import DTW distance function.
from dtaidistance import dtw

# Import Config for configuration access.
from src.config import Config

# Define a TripScorer class to score trip sequences.
class TripScorer:
    # Initialize the scorer by loading model and templates.
    def __init__(self):
        # Load configuration from YAML.
        cfg = Config.load()
        # Store config for later use.
        self.cfg = cfg
        # Load the trained SVM model from disk.
        with open(cfg.MODEL_PATH, "rb") as f:
            self.model = pickle.load(f)
        # Load the base trips data to compute templates.
        base_df = pd.read_csv(cfg.DATA_PATH)
        # Build the list of speed column names.
        speed_cols = [f"speed_t{i}" for i in range(50)]
        # Compute calm template as the mean of calm trips.
        self.calm_template = base_df.loc[base_df["label"] == "calm", speed_cols].mean().to_numpy(dtype=float)
        # Compute aggressive template as the mean of aggressive trips.
        self.aggressive_template = base_df.loc[base_df["label"] == "aggressive", speed_cols].mean().to_numpy(dtype=float)
        # Store speed column names for reuse.
        self.speed_cols = speed_cols

    # Score a single trip represented as a numpy array of speeds.
    def score_trip(self, speed_array):
        # Compute DTW distance to the calm template.
        dtw_calm = dtw.distance(speed_array, self.calm_template)
        # Compute DTW distance to the aggressive template.
        dtw_aggressive = dtw.distance(speed_array, self.aggressive_template)
        # Build the feature row for prediction.
        X = np.array([[dtw_calm, dtw_aggressive]], dtype=float)
        # Predict the class label.
        pred_label = self.model.predict(X)[0]
        # Predict class probabilities.
        pred_proba = self.model.predict_proba(X)[0]
        # Map numeric prediction to string label.
        label = "aggressive" if pred_label == 1 else "calm"
        # Compute confidence as the max probability.
        confidence = float(np.max(pred_proba) * 100.0)
        # Compute safety score using aggressive probability.
        safety_score = float(round(100.0 - (pred_proba[1] * 100.0), 1))
        # Return a dictionary of scoring results.
        return {
            "label": label,
            "confidence": confidence,
            "safety_score": safety_score,
            "dtw_calm": float(dtw_calm),
            "dtw_aggressive": float(dtw_aggressive),
        }

    # Score every row in a dataframe with speed columns.
    def score_dataframe(self, df):
        # Apply scoring to each row's speed values.
        scores = [self.score_trip(row[self.speed_cols].to_numpy(dtype=float)) for _, row in df.iterrows()]
        # Extract labels into a list.
        labels = [s["label"] for s in scores]
        # Extract confidence into a list.
        confidences = [s["confidence"] for s in scores]
        # Extract safety scores into a list.
        safety_scores = [s["safety_score"] for s in scores]
        # Add new columns to the dataframe.
        df = df.copy()
        # Assign predicted label column.
        df["label"] = labels
        # Assign confidence column.
        df["confidence"] = confidences
        # Assign safety score column.
        df["safety_score"] = safety_scores
        # Return the updated dataframe.
        return df
