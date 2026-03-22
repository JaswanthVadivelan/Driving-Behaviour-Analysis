# download_kaggle_dataset.py
# This script downloads the driving behavior dataset via kagglehub.

# Import kagglehub for dataset downloads.
import kagglehub

# Download the latest version of the dataset.
path = kagglehub.dataset_download("outofskills/driving-behavior")

# Print the local path to the dataset files.
print("Path to dataset files:", path)
