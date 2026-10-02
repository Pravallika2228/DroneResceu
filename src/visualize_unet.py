import os
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from PIL import Image

# ==========================================
# SETTINGS
# ==========================================
IMG_SIZE = 256
NUM_CLASSES = 10

DATASET = "dataset/FloodNet/FloodNet-Supervised_v1.0"

IMAGE_DIR = os.path.join(
    DATASET, "val", "val-org-img"
)

MASK_DIR = os.path.join(
    DATASET, "val", "val-label-img"
)

MODEL_PATH = "models/unet/unet_best.keras"

OUTPUT_DIR = "outputs/unet_predictions"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==========================================
# FLOODNET CLASS NAMES
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
print("Loading U-Net model...")

model = tf.keras.models.load_model(
    MODEL_PATH
)

print("Model loaded successfully.")


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
# VISUALIZE FIRST 5 IMAGES
# ==========================================
for image_name in image_files[:5]:

    print("\nProcessing:", image_name)

    # --------------------------------------
    # Paths
    # --------------------------------------
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
    # Load original image
    # --------------------------------------
    original = Image.open(
        image_path
    ).convert("RGB")

    # --------------------------------------
    # Prepare image for U-Net
    # --------------------------------------
    image = original.resize(
        (IMG_SIZE, IMG_SIZE),
        Image.Resampling.BILINEAR
    )

    image_array = (
        np.array(image)
        .astype(np.float32)
        / 255.0
    )

    input_image = np.expand_dims(
        image_array,
        axis=0
    )

    # --------------------------------------
    # Load ground truth mask
    # --------------------------------------
    ground_truth = Image.open(
        mask_path
    )

    ground_truth = ground_truth.resize(
        (IMG_SIZE, IMG_SIZE),
        Image.Resampling.NEAREST
    )

    ground_truth = np.array(
        ground_truth
    ).astype(np.int32)

    # --------------------------------------
    # Prediction
    # --------------------------------------
    prediction = model.predict(
        input_image,
        verbose=0
    )

    predicted_mask = np.argmax(
        prediction[0],
        axis=-1
    )

    # --------------------------------------
    # Print classes
    # --------------------------------------
    print(
        "Ground truth classes:",
        np.unique(ground_truth)
    )

    print(
        "Predicted classes    :",
        np.unique(predicted_mask)
    )

    # --------------------------------------
    # Plot
    # --------------------------------------
    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.imshow(image_array)
    plt.title("Original Image")
    plt.axis("off")

    plt.subplot(1, 3, 2)
    plt.imshow(ground_truth)
    plt.title("Ground Truth")
    plt.axis("off")

    plt.subplot(1, 3, 3)
    plt.imshow(predicted_mask)
    plt.title("U-Net Prediction")
    plt.axis("off")

    plt.tight_layout()

    # --------------------------------------
    # Save result
    # --------------------------------------
    output_path = os.path.join(
        OUTPUT_DIR,
        base_name + "_prediction.png"
    )

    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    print(
        "Saved:",
        output_path
    )


print("\n====================================")
print("U-NET VISUALIZATION COMPLETED")
print("====================================")