from pathlib import Path

import numpy as np
import tensorflow as tf
import joblib

from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input


# ============================================================
# Paths
# ============================================================

DATASET = Path(
    "dataset/FloodNet/FloodNet-Supervised_v1.0"
)

MODEL_PATH = Path(
    "models/efficientnet_xgb/xgboost_flood_classifier.joblib"
)


# ============================================================
# Choose an unseen test image
# ============================================================

image_path = (
    DATASET /
    "test" /
    "test-org-img" /
    "10163.jpg"
)


# ============================================================
# Load EfficientNetB0
# ============================================================

print("Loading EfficientNetB0...")

feature_model = EfficientNetB0(
    weights="imagenet",
    include_top=False,
    pooling="avg"
)

print("EfficientNetB0 loaded.")


# ============================================================
# Load XGBoost
# ============================================================

print("Loading XGBoost model...")

classifier = joblib.load(MODEL_PATH)

print("XGBoost loaded.")


# ============================================================
# Load and preprocess image
# ============================================================

print("\nImage:", image_path.name)

image = tf.keras.utils.load_img(
    image_path,
    target_size=(224, 224)
)

image = tf.keras.utils.img_to_array(image)

image = np.expand_dims(
    image,
    axis=0
)

image = preprocess_input(image)


# ============================================================
# Extract EfficientNet features
# ============================================================

features = feature_model.predict(
    image,
    verbose=0
)

print("Feature shape:", features.shape)


# ============================================================
# Predict
# ============================================================

prediction = classifier.predict(features)[0]

probability = classifier.predict_proba(features)[0]

flood_probability = probability[1] * 100


# ============================================================
# Display result
# ============================================================

if prediction == 1:
    result = "FLOODED"
else:
    result = "NON-FLOODED"


print("\n========================================")
print("       DRONERESCUE FLOOD PREDICTION")
print("========================================")

print("Image              :", image_path.name)
print("Prediction         :", result)
print(
    f"Flood probability  : {flood_probability:.2f}%"
)

print("========================================")