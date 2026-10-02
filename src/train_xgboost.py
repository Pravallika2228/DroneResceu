from pathlib import Path

import numpy as np
import joblib

from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# Paths
# ============================================================

OUTPUT = Path("outputs")
MODEL_DIR = Path("models") / "efficientnet_xgb"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Load EfficientNet features
# ============================================================

print("Loading features...")

X_train = np.load(
    OUTPUT / "train_efficientnet_features.npy"
)
y_train = np.load(
    OUTPUT / "train_efficientnet_labels.npy"
)

X_val = np.load(
    OUTPUT / "val_efficientnet_features.npy"
)
y_val = np.load(
    OUTPUT / "val_efficientnet_labels.npy"
)

X_test = np.load(
    OUTPUT / "test_efficientnet_features.npy"
)
y_test = np.load(
    OUTPUT / "test_efficientnet_labels.npy"
)


print("\nFeature shapes:")
print("Train:", X_train.shape)
print("Val  :", X_val.shape)
print("Test :", X_test.shape)

print("\nClass distribution:")
print("Train - Flooded:", np.sum(y_train == 1))
print("Train - Non-Flooded:", np.sum(y_train == 0))

print("Val   - Flooded:", np.sum(y_val == 1))
print("Val   - Non-Flooded:", np.sum(y_val == 0))

print("Test  - Flooded:", np.sum(y_test == 1))
print("Test  - Non-Flooded:", np.sum(y_test == 0))


# ============================================================
# Calculate class imbalance
# ============================================================

flooded = np.sum(y_train == 1)
non_flooded = np.sum(y_train == 0)

scale_pos_weight = non_flooded / flooded

print("\nScale position weight:", scale_pos_weight)


# ============================================================
# Create XGBoost classifier
# ============================================================

print("\nCreating XGBoost model...")

model = XGBClassifier(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="binary:logistic",
    eval_metric="logloss",
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    n_jobs=-1
)


# ============================================================
# Train
# ============================================================

print("\nTraining XGBoost...")

model.fit(
    X_train,
    y_train,
    eval_set=[(X_val, y_val)],
    verbose=False
)

print("Training completed.")


# ============================================================
# Validation evaluation
# ============================================================

print("\n========================================")
print("VALIDATION RESULTS")
print("========================================")

val_predictions = model.predict(X_val)

val_accuracy = accuracy_score(
    y_val,
    val_predictions
)

val_precision = precision_score(
    y_val,
    val_predictions,
    zero_division=0
)

val_recall = recall_score(
    y_val,
    val_predictions,
    zero_division=0
)

val_f1 = f1_score(
    y_val,
    val_predictions,
    zero_division=0
)

print(f"Accuracy : {val_accuracy:.4f}")
print(f"Precision: {val_precision:.4f}")
print(f"Recall   : {val_recall:.4f}")
print(f"F1-score : {val_f1:.4f}")

print("\nConfusion Matrix:")
print(confusion_matrix(y_val, val_predictions))

print("\nClassification Report:")
print(
    classification_report(
        y_val,
        val_predictions,
        target_names=[
            "Non-Flooded",
            "Flooded"
        ],
        zero_division=0
    )
)


# ============================================================
# Test evaluation
# ============================================================

print("\n========================================")
print("TEST RESULTS")
print("========================================")

test_predictions = model.predict(X_test)

test_accuracy = accuracy_score(
    y_test,
    test_predictions
)

test_precision = precision_score(
    y_test,
    test_predictions,
    zero_division=0
)

test_recall = recall_score(
    y_test,
    test_predictions,
    zero_division=0
)

test_f1 = f1_score(
    y_test,
    test_predictions,
    zero_division=0
)

print(f"Accuracy : {test_accuracy:.4f}")
print(f"Precision: {test_precision:.4f}")
print(f"Recall   : {test_recall:.4f}")
print(f"F1-score : {test_f1:.4f}")

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, test_predictions))

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        test_predictions,
        target_names=[
            "Non-Flooded",
            "Flooded"
        ],
        zero_division=0
    )
)


# ============================================================
# Save model
# ============================================================

model_file = MODEL_DIR / "xgboost_flood_classifier.joblib"

joblib.dump(
    model,
    model_file
)

print("\n========================================")
print("XGBoost model saved")
print("========================================")

print("Model:", model_file)