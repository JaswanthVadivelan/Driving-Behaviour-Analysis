# step3_dtw_features.py
# This script adds Dynamic Time Warping (DTW) features to each trip and saves a scatter plot.

# Import standard library for filesystem operations.
import os

# Import numpy for numerical arrays and math.
import numpy as np

# Import pandas for data loading and manipulation.
import pandas as pd

# Import matplotlib for plotting.
import matplotlib.pyplot as plt

# Import DTW distance function from dtaidistance.
from dtaidistance import dtw

# Define the input CSV path.
input_path = os.path.join("data", "trips.csv")

# Load the dataset from CSV.
df = pd.read_csv(input_path)

# Build the list of speed column names.
speed_cols = [f"speed_t{i}" for i in range(50)]

# Extract speed values as a numpy array (rows = trips, cols = time steps).
speeds = df[speed_cols].to_numpy(dtype=float)

# Select calm trips and compute the mean speed profile as a reference template.
calm_template = df.loc[df["label"] == "calm", speed_cols].mean().to_numpy(dtype=float)

# Select aggressive trips and compute the mean speed profile as a reference template.
aggressive_template = df.loc[df["label"] == "aggressive", speed_cols].mean().to_numpy(dtype=float)

# DTW (Dynamic Time Warping) measures similarity between two sequences by non-linearly aligning them in time.
# This allows sequences with similar shapes but shifted or stretched timelines to be considered close.

# Compute DTW distance from each trip to the calm template.
dtw_calm = [dtw.distance(trip, calm_template) for trip in speeds]

# Compute DTW distance from each trip to the aggressive template.
dtw_aggressive = [dtw.distance(trip, aggressive_template) for trip in speeds]

# Add the DTW feature columns to the DataFrame.
df["dtw_calm"] = dtw_calm

# Add the DTW feature columns to the DataFrame.
df["dtw_aggressive"] = dtw_aggressive

# Ensure the charts output directory exists.
os.makedirs("charts", exist_ok=True)

# Create a scatter plot comparing DTW distances to both templates.
plt.figure(figsize=(7, 6))

# Plot calm trips in blue.
plt.scatter(df.loc[df["label"] == "calm", "dtw_calm"], df.loc[df["label"] == "calm", "dtw_aggressive"], color="steelblue", label="calm", alpha=0.7)

# Plot aggressive trips in red.
plt.scatter(df.loc[df["label"] == "aggressive", "dtw_calm"], df.loc[df["label"] == "aggressive", "dtw_aggressive"], color="firebrick", label="aggressive", alpha=0.7)

# Add title and axis labels.
plt.title("DTW Distances to Calm vs Aggressive Templates")

# Label the x-axis.
plt.xlabel("DTW Distance to Calm Template")

# Label the y-axis.
plt.ylabel("DTW Distance to Aggressive Template")

# Show legend for classes.
plt.legend()

# Save the scatter plot to disk.
plt.savefig(os.path.join("charts", "dtw_scatter.png"), dpi=150, bbox_inches="tight")

# Close the figure to free memory.
plt.close()

# Save the updated DataFrame with DTW features.
output_path = os.path.join("data", "trips_features.csv")

df.to_csv(output_path, index=False)

# Print the first five rows to confirm new features.
print(df.head(5))
