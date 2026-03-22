# step1_generate.py
# This script generates synthetic vehicle trip speed sequences and saves them to CSV.

# Import standard libraries for file paths and directories.
import os

# Import third-party libraries for numerical operations and tabular data.
import numpy as np
import pandas as pd

# Set a fixed random seed for reproducibility.
rng = np.random.default_rng(42)

# Define configuration values for the synthetic dataset.
num_trips_per_class = 150
num_steps = 50

# Prepare a list to collect per-trip dictionaries for DataFrame creation.
records = []

# Generate calm trips with smooth speed changes.
for i in range(num_trips_per_class):
    # Sample a starting speed in the calm range.
    speed = rng.uniform(20, 40)
    # Initialize a list to hold the speed values for each time step.
    speeds = [speed]
    # Create subsequent speeds by adding small random deltas.
    for _ in range(1, num_steps):
        speed = speed + rng.uniform(-3, 3)
        speed = np.clip(speed, 10, 60)
        speeds.append(speed)
    # Compute jerk as the mean absolute difference between consecutive speeds.
    diffs = np.abs(np.diff(speeds))
    jerk = float(diffs.mean())
    # Build the row record with identifiers, label, and speed columns.
    row = {
        "trip_id": f"calm_{i}",
        "label": "calm",
        "jerk": jerk,
    }
    # Add each time step speed with the required column names.
    for t in range(num_steps):
        row[f"speed_t{t}"] = speeds[t]
    # Append the row to the collection.
    records.append(row)

# Generate aggressive trips with larger speed changes.
for i in range(num_trips_per_class):
    # Sample a starting speed in the aggressive range.
    speed = rng.uniform(20, 60)
    # Initialize a list to hold the speed values for each time step.
    speeds = [speed]
    # Create subsequent speeds by adding larger random deltas.
    for _ in range(1, num_steps):
        speed = speed + rng.uniform(-15, 15)
        speed = np.clip(speed, 0, 120)
        speeds.append(speed)
    # Compute jerk as the mean absolute difference between consecutive speeds.
    diffs = np.abs(np.diff(speeds))
    jerk = float(diffs.mean())
    # Build the row record with identifiers, label, and speed columns.
    row = {
        "trip_id": f"aggressive_{i}",
        "label": "aggressive",
        "jerk": jerk,
    }
    # Add each time step speed with the required column names.
    for t in range(num_steps):
        row[f"speed_t{t}"] = speeds[t]
    # Append the row to the collection.
    records.append(row)

# Create a DataFrame from the list of records.
df = pd.DataFrame.from_records(records)

# Ensure the output directory exists before saving.
os.makedirs("data", exist_ok=True)

# Save the DataFrame to a CSV file.
output_path = os.path.join("data", "trips.csv")
df.to_csv(output_path, index=False)

# Print the shape of the generated dataset.
print(df.shape)

# Print the first three rows for a quick sanity check.
print(df.head(3))
