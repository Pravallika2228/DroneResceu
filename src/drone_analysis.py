import os
import numpy as np
import tensorflow as tf
from PIL import Image
from joblib import load
from ultralytics import YOLO

from src.emergency_assessment import (
    generate_assessment,
    print_assessment
)


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CLASSIFICATION_SIZE = 224
SEGMENTATION_SIZE = 256

UNET_MODEL = os.path.join(
    PROJECT_ROOT,
    "models",
    "unet_weighted",
    "unet_best.keras"
)

XGB_MODEL = os.path.join(
    PROJECT_ROOT,
    "models",
    "efficientnet_xgb",
    "xgboost_flood_classifier.joblib"
)

YOLO_MODEL = os.path.join(
    PROJECT_ROOT,
    "yolo11n.pt"
)

YOLO_CONFIDENCE = 0.10
YOLO_IMAGE_SIZE = 1280


SEGMENTATION_OUTPUT_FOLDER = os.path.join(
    PROJECT_ROOT,
    "web",
    "static",
    "uploads",
    "segmentation"
)

os.makedirs(SEGMENTATION_OUTPUT_FOLDER, exist_ok=True)


SEGMENTATION_COLORS = {
    1: (235, 85, 95),    # Building Flooded
    3: (245, 145, 65),   # Road Flooded
    5: (65, 155, 235),   # Water
    7: (245, 200, 55)    # Vehicle
}


print("Loading EfficientNetB0...")

efficientnet = tf.keras.applications.EfficientNetB0(
    weights="imagenet",
    include_top=False,
    pooling="avg"
)

print("EfficientNetB0 loaded successfully.")

print("Loading XGBoost...")
xgb_model = load(XGB_MODEL)
print("XGBoost loaded successfully.")

print("Loading U-Net...")
unet_model = tf.keras.models.load_model(
    UNET_MODEL,
    compile=False
)
print("U-Net loaded successfully.")

print("Loading YOLO...")
yolo_model = YOLO(YOLO_MODEL)
print("YOLO loaded successfully.")


def predict_flood(image_path):
    image = Image.open(image_path).convert("RGB")

    image = image.resize(
        (CLASSIFICATION_SIZE, CLASSIFICATION_SIZE),
        Image.Resampling.BILINEAR
    )

    image = np.asarray(image, dtype=np.float32)
    image = np.expand_dims(image, axis=0)

    image = tf.keras.applications.efficientnet.preprocess_input(
        image
    )

    features = efficientnet.predict(
        image,
        verbose=0
    )

    flood_probability = float(
        xgb_model.predict_proba(features)[0][1]
    )

    prediction = int(
        xgb_model.predict(features)[0]
    )

    return prediction == 1, flood_probability


def predict_segmentation(image_path):
    image = Image.open(image_path).convert("RGB")

    image = image.resize(
        (SEGMENTATION_SIZE, SEGMENTATION_SIZE),
        Image.Resampling.BILINEAR
    )

    image = (
        np.asarray(image, dtype=np.float32) / 255.0
    )

    image = np.expand_dims(image, axis=0)

    prediction = unet_model.predict(
        image,
        verbose=0
    )

    return np.argmax(prediction[0], axis=-1)


def create_segmentation_overlay(image_path, predicted_mask):
    original = Image.open(image_path).convert("RGB")

    display_image = original.copy()
    max_dimension = 1200

    width, height = display_image.size

    if max(width, height) > max_dimension:
        scale = max_dimension / max(width, height)

        display_image = display_image.resize(
            (
                int(width * scale),
                int(height * scale)
            ),
            Image.Resampling.LANCZOS
        )

    mask_image = Image.fromarray(
        predicted_mask.astype(np.uint8),
        mode="L"
    )

    mask_image = mask_image.resize(
        display_image.size,
        Image.Resampling.NEAREST
    )

    mask_array = np.asarray(mask_image)

    color_mask = np.zeros(
        (
            display_image.height,
            display_image.width,
            3
        ),
        dtype=np.uint8
    )

    overlay_mask = np.zeros(
        (
            display_image.height,
            display_image.width
        ),
        dtype=bool
    )

    for class_id, color in SEGMENTATION_COLORS.items():
        pixels = mask_array == class_id
        color_mask[pixels] = color
        overlay_mask |= pixels

    original_array = np.asarray(display_image).copy()

    blended_array = original_array.copy()

    color_pixels = color_mask[overlay_mask].astype(np.float32)
    original_pixels = original_array[overlay_mask].astype(np.float32)

    blended_array[overlay_mask] = (
        original_pixels * 0.45
        + color_pixels * 0.55
    ).astype(np.uint8)

    overlay = Image.fromarray(
        blended_array,
        mode="RGB"
    )

    base_name = os.path.splitext(
        os.path.basename(image_path)
    )[0]

    output_filename = (
        f"{base_name}_segmentation_overlay.jpg"
    )

    output_path = os.path.join(
        SEGMENTATION_OUTPUT_FOLDER,
        output_filename
    )

    overlay.save(
        output_path,
        quality=90
    )

    return (
        "/static/uploads/segmentation/"
        + output_filename
    )


def detect_objects(image_path):
    """
    Detect people and common vehicle classes using YOLO only.

    Vehicle counts shown by the dashboard come from object detections,
    not from semantic-segmentation pixels. This prevents the U-Net
    vehicle class from being mistaken for an exact object count.
    """

    results = yolo_model.predict(
        source=image_path,
        conf=YOLO_CONFIDENCE,
        imgsz=YOLO_IMAGE_SIZE,
        iou=0.50,
        max_det=100,
        save=False,
        verbose=False
    )

    people_count = 0
    vehicle_count = 0

    vehicle_classes = {
        1: "Bicycle",
        2: "Car",
        3: "Motorcycle",
        5: "Bus",
        7: "Truck"
    }

    vehicle_breakdown = {
        "Bicycle": 0,
        "Car": 0,
        "Motorcycle": 0,
        "Bus": 0,
        "Truck": 0
    }

    if results and results[0].boxes is not None:
        for box in results[0].boxes:
            class_id = int(box.cls[0].item())

            if class_id == 0:
                people_count += 1

            elif class_id in vehicle_classes:
                vehicle_count += 1
                vehicle_breakdown[vehicle_classes[class_id]] += 1

    return (
        people_count,
        vehicle_count,
        vehicle_breakdown,
        {
            "yolo_vehicle_count": vehicle_count,
            "count_source": "YOLO object detections"
        }
    )


def analyze_drone_image(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    print("\nAnalyzing drone image:")
    print(image_path)

    flood_detected, flood_probability = predict_flood(
        image_path
    )
    print("\nFlood classification completed.")

    predicted_mask = predict_segmentation(
        image_path
    )
    print("Semantic segmentation completed.")

    segmentation_url = create_segmentation_overlay(
        image_path,
        predicted_mask
    )
    print("Segmentation visualization created.")

    (
        people_count,
        vehicle_count,
        vehicle_breakdown,
        vehicle_sources
    ) = detect_objects(
        image_path
    )

    print("Object detection completed.")

    report = generate_assessment(
        flood_detected=flood_detected,
        flood_probability=flood_probability,
        predicted_mask=predicted_mask,
        people_count=people_count,
        vehicle_count=vehicle_count
    )

    report["segmentation_image"] = segmentation_url

    print_assessment(report)

    print("\nVehicle Breakdown")

    for vehicle, count in vehicle_breakdown.items():
        print(f"{vehicle:12s}: {count}")

    print("\nAnalysis completed successfully.")

    # IMPORTANT:
    # Return only JSON-safe information.
    # The NumPy segmentation mask is NOT returned.
    return {
        "assessment": report,
        "vehicle_breakdown": vehicle_breakdown,
        "segmentation_image": segmentation_url,
        "pipeline": {
            "classification": "EfficientNetB0 + XGBoost",
            "segmentation": "Weighted U-Net",
            "object_detection": "YOLO11n pretrained object detection",
            "vehicle_sources": vehicle_sources,
            "status": "COMPLETED"
        }
    }


if __name__ == "__main__":
    image_path = os.path.join(
        PROJECT_ROOT,
        "dataset",
        "FloodNet",
        "FloodNet-Supervised_v1.0",
        "test",
        "test-org-img",
        "10163.jpg"
    )

    analyze_drone_image(image_path)
