"""
MLOps: Synthetic Chart Pattern Dataset Creation
"""
import numpy as np
import cv2
import os
import pandas as pd
from tqdm import tqdm

# --- Configuration ---
DATASET_DIR = "chart_dataset"
IMG_SIZE = (128, 128)
NUM_SAMPLES_PER_CLASS = 1000
CLASSES = ["head_and_shoulders", "double_top", "rising_wedge", "no_pattern"]


def generate_price_series(pattern_type):
    """Generates a numpy array of prices representing a chart pattern."""
    length = 200
    base_price = 100
    noise = np.random.randn(length) * 0.5

    if pattern_type == "head_and_shoulders":
        p = np.array([0, 10, 5, 15, 5, 10, 0])
        x = np.linspace(0, length, len(p))
        y = np.interp(np.arange(length), x, p)
        return base_price + y + noise

    elif pattern_type == "double_top":
        p = np.array([0, 10, 5, 10, 0])
        x = np.linspace(0, length, len(p))
        y = np.interp(np.arange(length), x, p)
        return base_price + y + noise

    elif pattern_type == "rising_wedge":
        x = np.arange(length)
        y = 0.1 * x + np.sin(x / 10) * 2
        return base_price + y + noise

    else:  # no_pattern (random walk)
        return base_price + np.cumsum(np.random.randn(length) * 0.7)


def series_to_image(series, width, height):
    """Converts a price series to a grayscale image."""
    min_val, max_val = np.min(series), np.max(series)
    range_val = max_val - min_val if max_val > min_val else 1
    normalized = (series - min_val) / range_val * (height - 1)

    image = np.zeros((height, width), dtype=np.uint8)
    for i in range(len(normalized) - 1):
        x1 = int((i / len(normalized)) * width)
        y1 = height - 1 - int(normalized[i])
        x2 = int(((i + 1) / len(normalized)) * width)
        y2 = height - 1 - int(normalized[i + 1])
        cv2.line(image, (x1, y1), (x2, y2), 255, 1)
    return image


def create_dataset():
    """Main function to generate and save the dataset."""
    print("Generating synthetic chart pattern dataset...")
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)

    for class_name in CLASSES:
        class_path = os.path.join(DATASET_DIR, class_name)
        if not os.path.exists(class_path):
            os.makedirs(class_path)

        print(f"Generating samples for class: {class_name}")
        for i in tqdm(range(NUM_SAMPLES_PER_CLASS)):
            price_series = generate_price_series(class_name)
            image = series_to_image(price_series, IMG_SIZE[0], IMG_SIZE[1])
            cv2.imwrite(os.path.join(class_path, f"{i}.png"), image)

    print("Dataset generation complete.")


if __name__ == "__main__":
    create_dataset()