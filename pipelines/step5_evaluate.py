# step5_evaluate.py
# This script compares three modeling approaches on the trip dataset.

# Import standard library for filesystem operations.
import os

# Import numpy for numerical operations.
import numpy as np

# Import pandas for data loading and manipulation.
import pandas as pd

# Import matplotlib for plotting.
import matplotlib.pyplot as plt

# Import sklearn utilities for splitting and metrics.
from sklearn.model_selection import train_test_split

# Import classifiers from sklearn.
from sklearn.svm import SVC

# Import KNN classifier from sklearn.
from sklearn.neighbors import KNeighborsClassifier

# Import evaluation metrics from sklearn.
from sklearn.metrics import accuracy_score, f1_score

# Define the input CSV path.
input_path = os.path.join("data", "trips_features.csv")

# Load the dataset from CSV.
df = pd.read_csv(input_path)

# Build the list of speed column names.
speed_cols = [f"speed_t{i}" for i in range(50)]

# Compute speed standard deviation per trip if not already present.
if "speed_std" not in df.columns:
    # Calculate std over speed columns as a raw feature.
    df["speed_std"] = df[speed_cols].std(axis=1)

# Encode labels as 0 for calm and 1 for aggressive.
y = df["label"].map({"calm": 0, "aggressive": 1}).to_numpy(dtype=int)

# Prepare raw feature matrix using jerk and speed standard deviation.
X_raw = df[["jerk", "speed_std"]].to_numpy(dtype=float)

# Prepare DTW feature matrix using dtw_calm and dtw_aggressive.
X_dtw = df[["dtw_calm", "dtw_aggressive"]].to_numpy(dtype=float)

# Split indices once to ensure the same train/test split for all experiments.
indices = np.arange(len(df))

# Create a shared train/test split.
idx_train, idx_test = train_test_split(indices, test_size=0.2, random_state=42, stratify=y)

# Slice training and testing data for raw features.
X_raw_train, X_raw_test = X_raw[idx_train], X_raw[idx_test]

# Slice training and testing labels.
y_train, y_test = y[idx_train], y[idx_test]

# Slice training and testing data for DTW features.
X_dtw_train, X_dtw_test = X_dtw[idx_train], X_dtw[idx_test]

# Experiment 1: Raw features with SVM RBF kernel.
svm_raw = SVC(kernel="rbf", probability=True, random_state=42)

# Train the raw-feature SVM.
svm_raw.fit(X_raw_train, y_train)

# Predict on the raw-feature test set.
y_pred_raw = svm_raw.predict(X_raw_test)

# Compute accuracy and F1 for raw-feature SVM.
acc_raw = accuracy_score(y_test, y_pred_raw)

# Compute F1 for raw-feature SVM.
f1_raw = f1_score(y_test, y_pred_raw)

# Experiment 2: DTW features with KNN classifier.
knn_dtw = KNeighborsClassifier(n_neighbors=5)

# Train the DTW-feature KNN.
knn_dtw.fit(X_dtw_train, y_train)

# Predict on the DTW-feature test set.
y_pred_knn = knn_dtw.predict(X_dtw_test)

# Compute accuracy and F1 for DTW-feature KNN.
acc_knn = accuracy_score(y_test, y_pred_knn)

# Compute F1 for DTW-feature KNN.
f1_knn = f1_score(y_test, y_pred_knn)

# Experiment 3: DTW features with SVM RBF kernel (hybrid model).
svm_dtw = SVC(kernel="rbf", probability=True, random_state=42)

# DTW features capture sequence alignment, and an RBF SVM can model non-linear class boundaries well.
# This combination often performs better because it leverages temporal shape similarity plus flexible decision surfaces.

# Train the DTW-feature SVM.
svm_dtw.fit(X_dtw_train, y_train)

# Predict on the DTW-feature test set.
y_pred_dtw = svm_dtw.predict(X_dtw_test)

# Compute accuracy and F1 for DTW-feature SVM.
acc_dtw = accuracy_score(y_test, y_pred_dtw)

# Compute F1 for DTW-feature SVM.
f1_dtw = f1_score(y_test, y_pred_dtw)

# Build a comparison table of results.
results = pd.DataFrame({
    "method": [
        "Raw (jerk+std) + SVM",
        "DTW + KNN (k=5)",
        "DTW + SVM (RBF)",
    ],
    "accuracy": [acc_raw, acc_knn, acc_dtw],
    "f1_score": [f1_raw, f1_knn, f1_dtw],
})

# Print the comparison table.
print(results)

# Determine the winning method by accuracy.
best_idx = results["accuracy"].idxmax()

# Extract the best method name and accuracy.
best_method = results.loc[best_idx, "method"]

# Compute the margin over the second-best accuracy.
sorted_acc = results["accuracy"].sort_values(ascending=False).to_numpy()

# Calculate the percentage margin over the runner-up.
margin = (sorted_acc[0] - sorted_acc[1]) * 100.0

# Print the winning method and margin.
print(f"Best method: {best_method} by {margin:.2f}% accuracy")

# Ensure the charts output directory exists.
os.makedirs("charts", exist_ok=True)

# Create a bar chart for accuracy comparison.
plt.figure(figsize=(8, 5))

# Plot accuracy bars.
plt.bar(results["method"], results["accuracy"], color=["gray", "orange", "steelblue"])

# Add title and labels for the chart.
plt.title("Model Accuracy Comparison")

# Label the y-axis.
plt.ylabel("Accuracy")

# Rotate x labels for readability.
plt.xticks(rotation=20, ha="right")

# Save the accuracy comparison chart.
plt.savefig(os.path.join("charts", "model_comparison.png"), dpi=150, bbox_inches="tight")

# Close the figure to free memory.
plt.close()
