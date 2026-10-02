import os
import numpy as np
import tensorflow as tf
from PIL import Image

# ==========================================
# SETTINGS
# ==========================================
IMG_SIZE = 256
NUM_CLASSES = 10

DATASET = "dataset/FloodNet/FloodNet-Supervised_v1.0"

IMAGE_DIR = os.path.join(
    DATASET,
    "val",
    "val-org-img"
)

MASK_DIR = os.path.join(
    DATASET,
    "val",
    "val-label-img"
)

# Weighted U-Net
MODEL_PATH = "models/unet_weighted/unet_best.keras"


# ==========================================
# CLASS NAMES
# ==========================================
CLASS_NAMES = [
    "Background",
    "Building Flooded",
    "Building Non-Flooded",
    "Road Flooded",
    "Road Non-Flooded",
    "Water",
    "Tree",
    "Vehicle",
    "Pool",
    "Grass"
]


# ==========================================
# LOAD MODEL
# ==========================================
print("Loading U-Net...")

# compile=False is important because the model
# was trained using a custom weighted loss.
model = tf.keras.models.load_model(
    MODEL_PATH,
    compile=False
)

print("Model loaded successfully.")
print("Model output shape:", model.output_shape)


# ==========================================
# GET VALIDATION IMAGES
# ==========================================
image_files = sorted([
    f for f in os.listdir(IMAGE_DIR)
    if f.lower().endswith(
        (".jpg", ".jpeg", ".png")
    )
])

print("Validation images:", len(image_files))


# ==========================================
# CONFUSION MATRIX
# ==========================================
confusion_matrix = np.zeros(
    (NUM_CLASSES, NUM_CLASSES),
    dtype=np.int64
)


# ==========================================
# EVALUATE
# ==========================================
for index, image_name in enumerate(image_files):

    image_path = os.path.join(
        IMAGE_DIR,
        image_name
    )

    base_name = os.path.splitext(
        image_name
    )[0]

    mask_name = base_name + "_lab.png"

    mask_path = os.path.join(
        MASK_DIR,
        mask_name
    )

    # --------------------------------------
    # Load image
    # --------------------------------------
    image = Image.open(
        image_path
    ).convert("RGB")

    image = image.resize(
        (IMG_SIZE, IMG_SIZE),
        Image.Resampling.BILINEAR
    )

    image = np.array(
        image
    ).astype(np.float32) / 255.0

    image = np.expand_dims(
        image,
        axis=0
    )

    # --------------------------------------
    # Load ground-truth mask
    # --------------------------------------
    mask = Image.open(
        mask_path
    )

    # VERY IMPORTANT:
    # NEAREST preserves class IDs.
    mask = mask.resize(
        (IMG_SIZE, IMG_SIZE),
        Image.Resampling.NEAREST
    )

    mask = np.array(
        mask
    ).astype(np.int32)

    # --------------------------------------
    # Predict
    # --------------------------------------
    prediction = model.predict(
        image,
        verbose=0
    )

    predicted_mask = np.argmax(
        prediction[0],
        axis=-1
    )

    # --------------------------------------
    # Update confusion matrix
    # --------------------------------------
    true_flat = mask.flatten()
    pred_flat = predicted_mask.flatten()

    combined = (
        true_flat * NUM_CLASSES
        + pred_flat
    )

    counts = np.bincount(
        combined,
        minlength=NUM_CLASSES * NUM_CLASSES
    )

    confusion_matrix += counts.reshape(
        NUM_CLASSES,
        NUM_CLASSES
    )

    # --------------------------------------
    # Progress
    # --------------------------------------
    if (index + 1) % 50 == 0:

        print(
            f"Processed "
            f"{index + 1}/{len(image_files)}"
        )


# ==========================================
# CALCULATE PER-CLASS METRICS
# ==========================================
print("\n========================================")
print("WEIGHTED U-NET SEGMENTATION RESULTS")
print("========================================")

all_ious = []
all_dices = []

for class_id in range(NUM_CLASSES):

    true_positive = confusion_matrix[
        class_id,
        class_id
    ]

    false_positive = (
        confusion_matrix[:, class_id].sum()
        - true_positive
    )

    false_negative = (
        confusion_matrix[class_id, :].sum()
        - true_positive
    )

    iou_denominator = (
        true_positive
        + false_positive
        + false_negative
    )

    dice_denominator = (
        2 * true_positive
        + false_positive
        + false_negative
    )

    if iou_denominator == 0:

        iou = np.nan

    else:

        iou = (
            true_positive
            / iou_denominator
        )

        all_ious.append(iou)

    if dice_denominator == 0:

        dice = np.nan

    else:

        dice = (
            2 * true_positive
            / dice_denominator
        )

        all_dices.append(dice)

    print(
        f"{class_id:2d} "
        f"{CLASS_NAMES[class_id]:22s} "
        f"IoU: {iou:.4f} "
        f"Dice: {dice:.4f}"
    )


# ==========================================
# MEAN IoU / DICE
# ==========================================
mean_iou = np.nanmean(all_ious)
mean_dice = np.nanmean(all_dices)

print("\n----------------------------------------")

print(
    f"Mean IoU  : {mean_iou:.4f}"
)

print(
    f"Mean Dice : {mean_dice:.4f}"
)

print("----------------------------------------")


# ==========================================
# FLOOD-RELATED CLASSES
# ==========================================
# DroneRescue focuses particularly on:
# 1 = Building Flooded
# 3 = Road Flooded

flood_classes = [
    1,
    3
]

flood_ious = []
flood_dices = []

print("\nFLOOD-RELATED CLASSES")
print("----------------------------------------")

for class_id in flood_classes:

    true_positive = confusion_matrix[
        class_id,
        class_id
    ]

    false_positive = (
        confusion_matrix[:, class_id].sum()
        - true_positive
    )

    false_negative = (
        confusion_matrix[class_id, :].sum()
        - true_positive
    )

    iou_denominator = (
        true_positive
        + false_positive
        + false_negative
    )

    dice_denominator = (
        2 * true_positive
        + false_positive
        + false_negative
    )

    if iou_denominator > 0:

        iou = (
            true_positive
            / iou_denominator
        )

        flood_ious.append(iou)

    else:

        iou = np.nan

    if dice_denominator > 0:

        dice = (
            2 * true_positive
            / dice_denominator
        )

        flood_dices.append(dice)

    else:

        dice = np.nan

    print(
        f"{CLASS_NAMES[class_id]:22s} "
        f"IoU: {iou:.4f} "
        f"Dice: {dice:.4f}"
    )


# ==========================================
# FLOOD CLASS AVERAGE
# ==========================================
print()

if flood_ious:

    print(
        "Flooded classes mean IoU : "
        f"{np.mean(flood_ious):.4f}"
    )

else:

    print(
        "Flooded classes mean IoU : N/A"
    )


if flood_dices:

    print(
        "Flooded classes mean Dice: "
        f"{np.mean(flood_dices):.4f}"
    )

else:

    print(
        "Flooded classes mean Dice: N/A"
    )


# ==========================================
# FINAL
# ==========================================
print("\n========================================")
print("WEIGHTED U-NET EVALUATION COMPLETED")
print("========================================")