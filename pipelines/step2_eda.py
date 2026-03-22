# step2_eda.py
# This script performs basic EDA and saves charts for the synthetic trips dataset.

# Import standard library for filesystem operations.
import os

# Import pandas for data loading and manipulation.
import pandas as pd

# Import numpy for numerical calculations.
import numpy as np

# Import matplotlib for plotting.
import matplotlib.pyplot as plt

# Import seaborn for nicer statistical visualizations.
import seaborn as sns

# Define the input CSV path.
input_path = os.path.join("data", "trips.csv")

# Load the dataset from CSV.
df = pd.read_csv(input_path)

# Build the list of speed column names.
speed_cols = [f"speed_t{i}" for i in range(50)]

# Extract only the speed columns into a separate DataFrame.
speeds_df = df[speed_cols]

# Ensure the charts output directory exists.
os.makedirs("charts", exist_ok=True)

# Compute average speed profile for each label across all trips.
mean_profile = df.groupby("label")[speed_cols].mean()

# Create the line chart for average speed profiles.
plt.figure(figsize=(10, 5))

# Plot calm mean profile.
plt.plot(range(50), mean_profile.loc["calm"], label="calm", color="steelblue")

# Plot aggressive mean profile.
plt.plot(range(50), mean_profile.loc["aggressive"], label="aggressive", color="firebrick")

# Add title and labels to the line chart.
plt.title("Average Speed Profile by Label")

# Label the x-axis for time steps.
plt.xlabel("Time Step")

# Label the y-axis for speed.
plt.ylabel("Speed (km/h)")

# Show legend for the two classes.
plt.legend()

# Save the line chart to disk.
plt.savefig(os.path.join("charts", "avg_speed_profile.png"), dpi=150, bbox_inches="tight")

# Close the figure to free memory.
plt.close()

# Create the histogram of jerk split by label.
plt.figure(figsize=(8, 5))

# Plot histogram for jerk by label using seaborn.
sns.histplot(data=df, x="jerk", hue="label", bins=30, kde=False, element="step")

# Add title and labels for the histogram.
plt.title("Jerk Distribution by Label")

# Label the x-axis for jerk values.
plt.xlabel("Jerk (mean abs diff)")

# Label the y-axis for count.
plt.ylabel("Count")

# Save the jerk histogram to disk.
plt.savefig(os.path.join("charts", "jerk_histogram.png"), dpi=150, bbox_inches="tight")

# Close the figure to free memory.
plt.close()

# Compute maximum speed per trip.
df["max_speed"] = speeds_df.max(axis=1)

# Create the boxplot of max speed by label.
plt.figure(figsize=(8, 5))

# Plot the boxplot for max speed split by label.
sns.boxplot(data=df, x="label", y="max_speed", palette="Set2")

# Add title and labels for the max speed boxplot.
plt.title("Max Speed by Label")

# Label the x-axis for class.
plt.xlabel("Label")

# Label the y-axis for max speed.
plt.ylabel("Max Speed (km/h)")

# Save the max speed boxplot to disk.
plt.savefig(os.path.join("charts", "max_speed_boxplot.png"), dpi=150, bbox_inches="tight")

# Close the figure to free memory.
plt.close()

# Compute speed standard deviation per trip.
df["speed_std"] = speeds_df.std(axis=1)

# Create the boxplot of speed standard deviation by label.
plt.figure(figsize=(8, 5))

# Plot the boxplot for speed standard deviation split by label.
sns.boxplot(data=df, x="label", y="speed_std", palette="Set3")

# Add title and labels for the speed std boxplot.
plt.title("Speed Standard Deviation by Label")

# Label the x-axis for class.
plt.xlabel("Label")

# Label the y-axis for speed standard deviation.
plt.ylabel("Speed Std Dev (km/h)")

# Save the speed std boxplot to disk.
plt.savefig(os.path.join("charts", "speed_std_boxplot.png"), dpi=150, bbox_inches="tight")

# Close the figure to free memory.
plt.close()

# Compute mean jerk by label.
mean_jerk = df.groupby("label")["jerk"].mean()

# Compute mean max speed by label.
mean_max_speed = df.groupby("label")["max_speed"].mean()

# Print mean jerk by class.
print("Mean jerk by label:")

# Print the mean jerk values.
print(mean_jerk)

# Print mean max speed by class.
print("Mean max speed by label:")

# Print the mean max speed values.
print(mean_max_speed)
