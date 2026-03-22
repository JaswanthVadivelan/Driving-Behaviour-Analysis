# step4_svm_train.py
# This script trains an SVM on DTW features, evaluates it, and saves plots and the model.

# Import standard library for filesystem operations.
import os

# Import standard library for model serialization.
import pickle

# Import numpy for numerical operations.
import numpy as np

# Import pandas for data loading and manipulation.
import pandas as pd

# Import matplotlib for plotting.
import matplotlib.pyplot as plt

# Import sklearn utilities for splitting, modeling, and metrics.
from sklearn.model_selection import train_test_split

# Import SVC classifier from sklearn.
from sklearn.svm import SVC

# Import evaluation metrics from sklearn.
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

# Define the input CSV path.
input_path = os.path.join("data", "trips_features.csv")

# Load the dataset from CSV.
df = pd.read_csv(input_path)

# Select only the DTW feature columns as input features.
X = df[["dtw_calm", "dtw_aggressive"]].to_numpy(dtype=float)

# Encode labels as 0 for calm and 1 for aggressive.
y = df["label"].map({"calm": 0, "aggressive": 1}).to_numpy(dtype=int)

# Split the data into training and testing sets.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Initialize the SVM classifier with RBF kernel and probability estimates.
model = SVC(kernel="rbf", probability=True, random_state=42)

# Train the SVM model on the training data.
model.fit(X_train, y_train)

# Predict labels on the test set.
y_pred = model.predict(X_test)

# Compute accuracy on the test set.
acc = accuracy_score(y_test, y_pred)

# Compute F1 score on the test set.
f1 = f1_score(y_test, y_pred)

# Print the accuracy.
print(f"Accuracy: {acc:.4f}")

# Print the F1 score.
print(f"F1 Score: {f1:.4f}")

# Print the full classification report.
print("Classification Report:")

# Output classification report details.
print(classification_report(y_test, y_pred, target_names=["calm", "aggressive"]))

# Compute confusion matrix.
cm = confusion_matrix(y_test, y_pred)

# Ensure the charts output directory exists.
os.makedirs("charts", exist_ok=True)

# Create a confusion matrix plot.
plt.figure(figsize=(6, 5))

# Display the confusion matrix as an image.
plt.imshow(cm, cmap="Blues")

# Add a title to the confusion matrix plot.
plt.title("Confusion Matrix")

# Add x-axis label.
plt.xlabel("Predicted")

# Add y-axis label.
plt.ylabel("True")

# Add tick labels for classes.
plt.xticks([0, 1], ["calm", "aggressive"])

# Add tick labels for classes.
plt.yticks([0, 1], ["calm", "aggressive"])

# Annotate each cell with its count.
for i in range(cm.shape[0]):
    # Loop over columns for annotation.
    for j in range(cm.shape[1]):
        # Place text for the cell value.
        plt.text(j, i, str(cm[i, j]), ha="center", va="center", color="black")

# Save the confusion matrix plot to disk.
plt.savefig(os.path.join("charts", "confusion_matrix.png"), dpi=150, bbox_inches="tight")

# Close the figure to free memory.
plt.close()

# Build a meshgrid for decision boundary visualization.
x_min, x_max = X[:, 0].min() - 1.0, X[:, 0].max() + 1.0

# Compute y-axis bounds for the meshgrid.
y_min, y_max = X[:, 1].min() - 1.0, X[:, 1].max() + 1.0

# Create a grid of points for contour plotting.
xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300), np.linspace(y_min, y_max, 300))

# Predict class labels on the meshgrid.
Z = model.predict(np.c_[xx.ravel(), yy.ravel()])

# Reshape predictions back to grid shape.
Z = Z.reshape(xx.shape)

# Create a decision boundary plot.
plt.figure(figsize=(7, 6))

# Plot the decision regions.
plt.contourf(xx, yy, Z, alpha=0.25, cmap="coolwarm")

# Plot calm points in blue.
plt.scatter(X[y == 0, 0], X[y == 0, 1], color="steelblue", label="calm", alpha=0.7)

# Plot aggressive points in red.
plt.scatter(X[y == 1, 0], X[y == 1, 1], color="firebrick", label="aggressive", alpha=0.7)

# Add title to the decision boundary plot.
plt.title("SVM Decision Boundary on DTW Features")

# Label the x-axis.
plt.xlabel("DTW Distance to Calm Template")

# Label the y-axis.
plt.ylabel("DTW Distance to Aggressive Template")

# Add legend for classes.
plt.legend()

# Save the decision boundary plot to disk.
plt.savefig(os.path.join("charts", "decision_boundary.png"), dpi=150, bbox_inches="tight")

# Close the figure to free memory.
plt.close()

# Ensure the models output directory exists.
os.makedirs("models", exist_ok=True)

# Define the model output path.
model_path = os.path.join("models", "svm_model.pkl")

# Serialize and save the trained model.
with open(model_path, "wb") as f:
    # Write the model bytes to disk.
    pickle.dump(model, f)
