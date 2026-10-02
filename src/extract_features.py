from pathlib import Path
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input

# ============================================================
# Paths
# ============================================================

DATASET = Path(
    "dataset/FloodNet/FloodNet-Supervised_v1.0"
)

OUTPUT = Path("outputs")
OUTPUT.mkdir(exist_ok=True)

# ============================================================
# Settings
# ============================================================

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 8

# ============================================================
# Load pretrained EfficientNetB0
# ============================================================

print("Loading EfficientNetB0...")

model = EfficientNetB0(
    weights="imagenet",
    include_top=False,
    pooling="avg"
)

print("EfficientNetB0 loaded successfully.")
print("Feature size:", model.output_shape[-1])


# ============================================================
# Extract features for one split
# ============================================================

def extract_features(split):

    image_dir = DATASET / split / f"{split}-org-img"

    label_file = (
        OUTPUT /
        f"{split}_classification_labels.csv"
    )

    df = pd.read_csv(label_file)

    features = []
    labels = []

    image_paths = []

    print(f"\nProcessing {split}...")
    print("Images:", len(df))

    for i in range(0, len(df), BATCH_SIZE):

        batch_df = df.iloc[i:i + BATCH_SIZE]

        batch_images = []

        for filename in batch_df["image"]:

            image_path = image_dir / filename

            image = tf.keras.utils.load_img(
                image_path,
                target_size=IMAGE_SIZE
            )

            image = tf.keras.utils.img_to_array(
                image
            )

            batch_images.append(image)

            image_paths.append(filename)

        batch_images = np.array(batch_images)

        batch_images = preprocess_input(
            batch_images
        )

        batch_features = model.predict(
            batch_images,
            verbose=0
        )

        features.append(batch_features)

        labels.extend(
            batch_df["label"].values
        )

        processed = min(
            i + BATCH_SIZE,
            len(df)
        )

        if processed % 100 == 0 or processed == len(df):
            print(
                f"Processed {processed}/{len(df)}"
            )

    features = np.vstack(features)

    labels = np.array(labels)

    # Save
    feature_file = (
        OUTPUT /
        f"{split}_efficientnet_features.npy"
    )

    label_output = (
        OUTPUT /
        f"{split}_efficientnet_labels.npy"
    )

    np.save(feature_file, features)
    np.save(label_output, labels)

    print(f"\n{split} completed")
    print("Feature shape:", features.shape)
    print("Labels shape :", labels.shape)
    print("Saved:", feature_file)
    print("Saved:", label_output)


# ============================================================
# Run
# ============================================================

extract_features("train")
extract_features("val")
extract_features("test")

print("\n======================================")
print("EfficientNet feature extraction done")
print("======================================")