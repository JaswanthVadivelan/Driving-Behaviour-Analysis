# src/history_manager.py
# This module manages storage and retrieval of trip scoring history.

# Import os for filesystem checks.
import os

# Import datetime for timestamps.
from datetime import datetime

# Import pandas for data handling.
import pandas as pd

# Import Config for configuration access.
from src.config import Config

# Define a HistoryManager class for trip history operations.
class HistoryManager:
    # Initialize the manager and ensure history storage exists.
    def __init__(self):
        # Load configuration from YAML.
        self.cfg = Config.load()
        # Resolve the history path from config.
        self.history_path = self.cfg.HISTORY_PATH
        # Define the required columns for the history file.
        self.columns = [
            "trip_id",
            "vehicle_id",
            "timestamp",
            "label",
            "confidence",
            "safety_score",
            "dtw_calm",
            "dtw_aggressive",
        ]
        # Create the history CSV if it does not exist.
        if not os.path.exists(self.history_path):
            # Create an empty DataFrame with the required columns.
            empty_df = pd.DataFrame(columns=self.columns)
            # Ensure the parent directory exists.
            os.makedirs(os.path.dirname(self.history_path) or ".", exist_ok=True)
            # Write the empty CSV to disk.
            empty_df.to_csv(self.history_path, index=False)

    # Save scored trips to the history CSV.
    def save_trips(self, df, vehicle_id):
        # Copy the input DataFrame to avoid mutation.
        df = df.copy()
        # Add the vehicle_id column.
        df["vehicle_id"] = vehicle_id
        # Add the current timestamp column.
        df["timestamp"] = datetime.utcnow().isoformat()
        # Ensure all required columns exist.
        for col in self.columns:
            if col not in df.columns:
                df[col] = pd.NA
        # Reorder columns to match the history schema.
        df = df[self.columns]
        # Append to the history CSV without headers.
        df.to_csv(self.history_path, mode="a", header=False, index=False)

    # Load history with optional filters.
    def load_history(self, vehicle_id=None, start_date=None, end_date=None):
        # Load the full history CSV.
        history_df = pd.read_csv(self.history_path)
        # Filter by vehicle_id if provided.
        if vehicle_id is not None:
            history_df = history_df[history_df["vehicle_id"] == vehicle_id]
        # Convert timestamp to datetime for filtering.
        history_df["timestamp"] = pd.to_datetime(history_df["timestamp"], errors="coerce")
        # Apply start date filter if provided.
        if start_date is not None:
            history_df = history_df[history_df["timestamp"] >= pd.to_datetime(start_date)]
        # Apply end date filter if provided.
        if end_date is not None:
            history_df = history_df[history_df["timestamp"] <= pd.to_datetime(end_date)]
        # Return the filtered history DataFrame.
        return history_df

    # Compute summary statistics over history.
    def get_summary_stats(self, vehicle_id=None):
        # Load history with optional vehicle filter.
        history_df = self.load_history(vehicle_id=vehicle_id)
        # Compute total trips.
        total_trips = len(history_df)
        # Compute percent aggressive trips.
        if total_trips > 0:
            pct_aggressive = (history_df["label"] == "aggressive").mean() * 100.0
        else:
            pct_aggressive = 0.0
        # Compute average safety score.
        avg_safety_score = float(history_df["safety_score"].mean()) if total_trips > 0 else 0.0
        # Compute worst (minimum) safety score.
        worst_trip_score = float(history_df["safety_score"].min()) if total_trips > 0 else 0.0
        # Compute best (maximum) safety score.
        best_trip_score = float(history_df["safety_score"].max()) if total_trips > 0 else 0.0
        # Return a dictionary of summary statistics.
        return {
            "total_trips": total_trips,
            "pct_aggressive": pct_aggressive,
            "avg_safety_score": avg_safety_score,
            "worst_trip_score": worst_trip_score,
            "best_trip_score": best_trip_score,
        }
