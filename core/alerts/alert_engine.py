# src/alert_engine.py
# This module defines alert generation and retrieval for risky driving events.

# Import os for filesystem checks.
import os

# Import datetime for time calculations.
from datetime import datetime, timedelta

# Import pandas for data handling.
import pandas as pd

# Import Config for configuration access.
from core.utils.config import Config

# Define an AlertEngine class for generating and managing alerts.
class AlertEngine:
    # Initialize the alert engine and ensure alert storage exists.
    def __init__(self):
        # Load configuration from YAML.
        self.cfg = Config.load()
        # Resolve the alerts path from config.
        self.alerts_path = self.cfg.ALERTS_PATH
        # Define the required columns for the alerts file.
        self.columns = [
            "alert_id",
            "vehicle_id",
            "timestamp",
            "alert_type",
            "message",
            "trip_count",
            "severity",
            "status",
        ]
        # Create the alerts CSV if it does not exist.
        if not os.path.exists(self.alerts_path):
            # Create an empty DataFrame with the required columns.
            empty_df = pd.DataFrame(columns=self.columns)
            # Ensure the parent directory exists.
            os.makedirs(os.path.dirname(self.alerts_path) or ".", exist_ok=True)
            # Write the empty CSV to disk.
            empty_df.to_csv(self.alerts_path, index=False)

    # Check a trip result and create alerts if needed.
    def check_trip(self, vehicle_id, label, safety_score):
        # Prepare a list to collect new alerts.
        new_alerts = []
        # Generate a critical alert for aggressive trips with very low safety score.
        if label == "aggressive" and safety_score < 30:
            # Build the alert dictionary.
            alert = {
                "alert_id": f"crit_{vehicle_id}_{int(datetime.utcnow().timestamp())}",
                "vehicle_id": vehicle_id,
                "timestamp": datetime.utcnow().isoformat(),
                "alert_type": "Critical Alert",
                "message": "Aggressive trip with safety score below 30.",
                "trip_count": 1,
                "severity": "High",
                "status": "Active"
            }
            # Add the alert to the list.
            new_alerts.append(alert)
        # Load history for the vehicle to check consecutive aggressive trips.
        history_path = self.cfg.HISTORY_PATH
        # Initialize history DataFrame as empty.
        history_df = pd.DataFrame()
        # Load history if the file exists.
        if os.path.exists(history_path):
            history_df = pd.read_csv(history_path)
        # Filter history to the specified vehicle.
        if not history_df.empty:
            history_df = history_df[history_df["vehicle_id"] == vehicle_id]
        # Determine how many recent trips to check.
        n = self.cfg.ALERT_CONSECUTIVE_TRIPS
        # Check if we have enough recent trips to evaluate.
        if not history_df.empty and len(history_df) >= n:
            # Sort history by timestamp descending.
            history_df["timestamp"] = pd.to_datetime(history_df["timestamp"], errors="coerce")
            history_df = history_df.sort_values("timestamp", ascending=False)
            # Get the last N trips.
            recent = history_df.head(n)
            # Determine if all recent trips are aggressive.
            if (recent["label"] == "aggressive").all():
                # Build the repeat offender alert.
                alert = {
                    "alert_id": f"repeat_{vehicle_id}_{int(datetime.utcnow().timestamp())}",
                    "vehicle_id": vehicle_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "alert_type": "Repeat Offender Alert",
                    "message": f"Last {n} trips were aggressive.",
                    "trip_count": int(n),
                    "severity": "Medium",
                    "status": "Active"
                }
                # Add the alert to the list.
                new_alerts.append(alert)
        # Append any new alerts to the alerts CSV.
        if new_alerts:
            # Convert alerts to a DataFrame.
            alerts_df = pd.DataFrame(new_alerts)
            # Ensure all required columns exist.
            for col in self.columns:
                if col not in alerts_df.columns:
                    alerts_df[col] = pd.NA
            # Reorder columns to match the schema.
            alerts_df = alerts_df[self.columns]
            # Append to CSV without header.
            alerts_df.to_csv(self.alerts_path, mode="a", header=False, index=False)
        # Return the list of generated alerts.
        return new_alerts

    # Get alerts from the last 24 hours.
    def get_active_alerts(self, vehicle_id=None):
        # Load all alerts from CSV.
        alerts_df = pd.read_csv(self.alerts_path)
        # Convert timestamp to datetime for filtering.
        alerts_df["timestamp"] = pd.to_datetime(alerts_df["timestamp"], errors="coerce")
        # Filter to last 24 hours.
        cutoff = datetime.utcnow() - timedelta(hours=24)
        alerts_df = alerts_df[alerts_df["timestamp"] >= cutoff]
        # Filter by vehicle_id if provided.
        if vehicle_id is not None:
            alerts_df = alerts_df[alerts_df["vehicle_id"] == vehicle_id]
        # Only return active alerts
        if "status" in alerts_df.columns:
            alerts_df = alerts_df[alerts_df["status"].isin(["Active", "Acknowledged"])]
        # Return the filtered alerts.
        return alerts_df

    # Update alert status
    def update_alert_status(self, alert_id, new_status):
        if not os.path.exists(self.alerts_path):
            return False
            
        alerts_df = pd.read_csv(self.alerts_path)
        if "status" not in alerts_df.columns:
            alerts_df["status"] = "Active"
            
        mask = alerts_df["alert_id"] == alert_id
        if mask.any():
            alerts_df.loc[mask, "status"] = new_status
            alerts_df.to_csv(self.alerts_path, index=False)
            return True
        return False
        
    def get_all_alerts(self, vehicle_id=None):
        if not os.path.exists(self.alerts_path):
            return pd.DataFrame(columns=self.columns)
            
        alerts_df = pd.read_csv(self.alerts_path)
        if vehicle_id is not None:
            alerts_df = alerts_df[alerts_df["vehicle_id"] == vehicle_id]
        return alerts_df

    # Return a summary count by alert type.
    def get_alert_summary(self):
        # Load all alerts from CSV.
        alerts_df = pd.read_csv(self.alerts_path)
        # Count alerts by type.
        summary = alerts_df["alert_type"].value_counts().to_dict()
        # Return the summary dictionary.
        return summary
