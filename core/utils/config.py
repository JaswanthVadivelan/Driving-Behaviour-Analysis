# src/config.py
# This module loads YAML configuration into a Config object.

# Import standard library for filesystem operations.
import os
from pathlib import Path

# Import PyYAML for YAML parsing.
import yaml

# Define a Config class to hold configuration values.
class Config:
    # Initialize the Config with explicit attributes.
    def __init__(
        # Accept model path value.
        self,
        # Accept data path value.
        model_path,
        # Accept features path value.
        data_path,
        # Accept history path value.
        features_path,
        # Accept alerts path value.
        history_path,
        # Accept reports path value.
        alerts_path,
        # Accept risk thresholds value.
        reports_path,
        # Accept number of clusters value.
        risk_thresholds,
        # Accept alert consecutive trips value.
        n_clusters,
        # Accept alert consecutive trips value.
        alert_consecutive_trips,
    ):
        # Store the model path.
        self.MODEL_PATH = model_path
        # Store the data path.
        self.DATA_PATH = data_path
        # Store the features path.
        self.FEATURES_PATH = features_path
        # Store the history path.
        self.HISTORY_PATH = history_path
        # Store the alerts path.
        self.ALERTS_PATH = alerts_path
        # Store the reports path.
        self.REPORTS_PATH = reports_path
        # Store the risk thresholds dictionary.
        self.RISK_THRESHOLDS = risk_thresholds
        # Store the number of clusters.
        self.N_CLUSTERS = n_clusters
        # Store the alert consecutive trips setting.
        self.ALERT_CONSECUTIVE_TRIPS = alert_consecutive_trips

    # Define a classmethod to load configuration from YAML.
    @classmethod
    def load(cls, path="configs/config.yaml"):
        # Resolve the configuration path relative to the project root.
        project_root = Path(__file__).resolve().parents[2]
        config_path = (project_root / path).resolve()
        # Backward-compatible fallback to legacy root config.yaml.
        if not config_path.exists():
            legacy_path = (project_root / "config.yaml").resolve()
            if legacy_path.exists():
                config_path = legacy_path
        # Open the YAML file for reading.
        with open(config_path, "r", encoding="utf-8") as f:
            # Parse YAML content into a dictionary.
            data = yaml.safe_load(f)
        # Create and return a Config instance from the YAML data.
        return cls(
            # Map model path from YAML.
            model_path=data["model_path"],
            # Map data path from YAML.
            data_path=data["data_path"],
            # Map features path from YAML.
            features_path=data["features_path"],
            # Map history path from YAML.
            history_path=data["history_path"],
            # Map alerts path from YAML.
            alerts_path=data["alerts_path"],
            # Map reports path from YAML.
            reports_path=data["reports_path"],
            # Map risk thresholds from YAML.
            risk_thresholds=data["risk_thresholds"],
            # Map number of clusters from YAML.
            n_clusters=data["n_clusters"],
            # Map alert consecutive trips from YAML.
            alert_consecutive_trips=data["alert_consecutive_trips"],
        )

    # Define a method to get the risk label for a given score.
    def get_risk_label(self, score):
        # Read the low threshold.
        low = self.RISK_THRESHOLDS["low"]
        # Read the medium threshold.
        medium = self.RISK_THRESHOLDS["medium"]
        # Read the high threshold.
        high = self.RISK_THRESHOLDS["high"]
        # Return Low Risk if below low threshold.
        if score < low:
            return "Low Risk"
        # Return Medium Risk if below medium threshold.
        if score < medium:
            return "Medium Risk"
        # Return High Risk if below high threshold.
        if score < high:
            return "High Risk"
        # Otherwise return Critical if above high threshold.
        return "Critical"
