# src/vehicle_profiler.py
# This module provides per-vehicle profiling and fleet analytics.

# Import pandas for data handling.
import pandas as pd

# Import numpy for numerical operations.
import numpy as np

# Import Config for configuration access.
from core.utils.config import Config

# Import HistoryManager for history retrieval.
from core.utils.history_manager import HistoryManager

# Define a VehicleProfiler class for profile and fleet statistics.
class VehicleProfiler:
    # Initialize the profiler with a HistoryManager.
    def __init__(self):
        # Load configuration (reserved for future use).
        self.cfg = Config.load()
        # Create a HistoryManager instance.
        self.history = HistoryManager()

    # Return a sorted list of unique vehicle IDs from history.
    def get_all_vehicle_ids(self):
        # Load all history records.
        df = self.history.load_history()
        # Return sorted unique vehicle IDs.
        return sorted(df["vehicle_id"].dropna().unique().tolist())

    # Build a profile dictionary for a single vehicle.
    def get_vehicle_profile(self, vehicle_id):
        # Load history filtered to the vehicle.
        df = self.history.load_history(vehicle_id=vehicle_id)
        # Compute total trips.
        total_trips = len(df)
        # Compute percent aggressive.
        if total_trips > 0:
            pct_aggressive = (df["label"] == "aggressive").mean() * 100.0
        else:
            pct_aggressive = 0.0
        # Compute average safety score.
        avg_safety_score = float(df["safety_score"].mean()) if total_trips > 0 else 0.0
        # Compute last 10 safety scores for trend.
        if total_trips > 0:
            df_sorted = df.copy()
            df_sorted["timestamp"] = pd.to_datetime(df_sorted["timestamp"], errors="coerce")
            df_sorted = df_sorted.sort_values("timestamp", ascending=False)
            risk_trend = df_sorted["safety_score"].head(10).tolist()
        else:
            risk_trend = []
        # Compute worst trip safety score.
        worst_trip = float(df["safety_score"].min()) if total_trips > 0 else 0.0
        # Compute best trip safety score.
        best_trip = float(df["safety_score"].max()) if total_trips > 0 else 0.0
        # Compute most common label.
        most_common_label = df["label"].mode().iloc[0] if total_trips > 0 else None
        # Return the profile dictionary.
        return {
            "vehicle_id": vehicle_id,
            "total_trips": total_trips,
            "pct_aggressive": pct_aggressive,
            "avg_safety_score": avg_safety_score,
            "risk_trend": risk_trend,
            "worst_trip": worst_trip,
            "best_trip": best_trip,
            "most_common_label": most_common_label,
        }

    # Compare multiple vehicles and return a summary DataFrame.
    def compare_vehicles(self, vehicle_id_list):
        # Build profile dictionaries for each vehicle.
        profiles = [self.get_vehicle_profile(vid) for vid in vehicle_id_list]
        # Create a DataFrame from profiles.
        df = pd.DataFrame(profiles)
        # Sort by average safety score ascending to show riskiest first.
        if not df.empty:
            df = df.sort_values("avg_safety_score", ascending=True)
        # Return the comparison DataFrame.
        return df

    # Compute overall fleet summary statistics.
    def get_fleet_summary(self):
        # Load all history records.
        df = self.history.load_history()
        # Compute total trips across fleet.
        total_trips = len(df)
        # Compute total vehicles.
        total_vehicles = df["vehicle_id"].nunique()
        # Compute percent aggressive across fleet.
        if total_trips > 0:
            pct_aggressive = (df["label"] == "aggressive").mean() * 100.0
        else:
            pct_aggressive = 0.0
        # Compute average safety score across fleet.
        avg_safety_score = float(df["safety_score"].mean()) if total_trips > 0 else 0.0
        # Compute worst trip safety score across fleet.
        worst_trip = float(df["safety_score"].min()) if total_trips > 0 else 0.0
        # Compute best trip safety score across fleet.
        best_trip = float(df["safety_score"].max()) if total_trips > 0 else 0.0
        # Return the fleet summary dictionary.
        return {
            "total_trips": total_trips,
            "total_vehicles": total_vehicles,
            "pct_aggressive": pct_aggressive,
            "avg_safety_score": avg_safety_score,
            "worst_trip": worst_trip,
            "best_trip": best_trip,
        }
