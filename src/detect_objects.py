import os
import cv2
import numpy as np
from ultralytics import YOLO


# ==========================================
# SETTINGS
# ==========================================

MODEL_NAME = "yolo11n.pt"

TEST_IMAGE_DIR = (
    "dataset/FloodNet/"
    "FloodNet-Supervised_v1.0/"
    "test/test-org-img"
)

OUTPUT_DIR = "outputs/yolo_detections"

CONFIDENCE = 0.10
IOU = 0.50

TILE_SIZE = 1024
OVERLAP = 0.25


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ==========================================
# GET REAL DATASET IMAGES
# ==========================================

all_images = [
    os.path.join(
        TEST_IMAGE_DIR,
        filename
    )
    for filename in os.listdir(
        TEST_IMAGE_DIR
    )
    if filename.lower().endswith(
        (".jpg", ".jpeg", ".png")
    )
]

IMAGE_PATHS = all_images[:3]


# ==========================================
# COCO CLASSES
# ==========================================

PERSON_CLASS = 0

VEHICLE_CLASSES = {
    1: "Bicycle",
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}


# ==========================================
# LOAD YOLO
# ==========================================

print("Loading YOLO model...")

model = YOLO(
    MODEL_NAME
)

print("YOLO model loaded successfully.")


# ==========================================
# TILED DETECTION
# ==========================================

def detect_on_tiles(image):

    height, width = image.shape[:2]

    step = int(
        TILE_SIZE * (1 - OVERLAP)
    )

    detections = []

    y_positions = list(
        range(
            0,
            max(height - TILE_SIZE, 0) + 1,
            step
        )
    )

    x_positions = list(
        range(
            0,
            max(width - TILE_SIZE, 0) + 1,
            step
        )
    )

    # Make sure final row/column is covered
    if not y_positions or (
        y_positions[-1] + TILE_SIZE < height
    ):
        y_positions.append(
            max(height - TILE_SIZE, 0)
        )

    if not x_positions or (
        x_positions[-1] + TILE_SIZE < width
    ):
        x_positions.append(
            max(width - TILE_SIZE, 0)
        )

    total_tiles = (
        len(x_positions)
        * len(y_positions)
    )

    tile_number = 0

    for y in y_positions:

        for x in x_positions:

            tile_number += 1

            print(
                f"  Tile {tile_number}/{total_tiles}"
            )

            x2 = min(
                x + TILE_SIZE,
                width
            )

            y2 = min(
                y + TILE_SIZE,
                height
            )

            tile = image[
                y:y2,
                x:x2
            ]

            results = model.predict(
                source=tile,
                conf=CONFIDENCE,
                iou=IOU,
                imgsz=TILE_SIZE,
                save=False,
                verbose=False
            )

            if not results:
                continue

            result = results[0]

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(
                    box.cls[0].item()
                )

                confidence = float(
                    box.conf[0].item()
                )

                coords = (
                    box.xyxy[0]
                    .cpu()
                    .numpy()
                )

                bx1, by1, bx2, by2 = coords

                # Convert tile coordinates
                # back to original image
                bx1 += x
                bx2 += x
                by1 += y
                by2 += y

                detections.append({
                    "class_id": class_id,
                    "confidence": confidence,
                    "box": (
                        int(bx1),
                        int(by1),
                        int(bx2),
                        int(by2)
                    )
                })

    return detections


# ==========================================
# SIMPLE NMS
# ==========================================

def remove_duplicate_detections(
    detections
):

    if not detections:
        return []

    boxes = []
    scores = []

    for detection in detections:

        x1, y1, x2, y2 = (
            detection["box"]
        )

        boxes.append([
            x1,
            y1,
            x2 - x1,
            y2 - y1
        ])

        scores.append(
            detection["confidence"]
        )

    indices = cv2.dnn.NMSBoxes(
        boxes,
        scores,
        CONFIDENCE,
        IOU
    )

    if len(indices) == 0:
        return []

    indices = np.array(
        indices
    ).reshape(-1)

    return [
        detections[i]
        for i in indices
    ]


# ==========================================
# PROCESS IMAGES
# ==========================================

for image_path in IMAGE_PATHS:

    print("\nProcessing image:")
    print(image_path)

    image = cv2.imread(
        image_path
    )

    if image is None:

        print(
            "Could not read image."
        )

        continue

    # --------------------------------------
    # Run tiled detection
    # --------------------------------------

    detections = detect_on_tiles(
        image
    )

    # --------------------------------------
    # Remove duplicates
    # --------------------------------------

    detections = (
        remove_duplicate_detections(
            detections
        )
    )

    # --------------------------------------
    # Count objects
    # --------------------------------------

    people_count = 0
    vehicle_count = 0

    vehicle_breakdown = {
        "Bicycle": 0,
        "Car": 0,
        "Motorcycle": 0,
        "Bus": 0,
        "Truck": 0
    }

    # --------------------------------------
    # Draw detections
    # --------------------------------------

    annotated_image = image.copy()

    for detection in detections:

        class_id = (
            detection["class_id"]
        )

        confidence = (
            detection["confidence"]
        )

        x1, y1, x2, y2 = (
            detection["box"]
        )

        if class_id == PERSON_CLASS:

            people_count += 1

            label = (
                f"Person "
                f"{confidence:.2f}"
            )

        elif class_id in VEHICLE_CLASSES:

            vehicle_count += 1

            vehicle_name = (
                VEHICLE_CLASSES[class_id]
            )

            vehicle_breakdown[
                vehicle_name
            ] += 1

            label = (
                f"{vehicle_name} "
                f"{confidence:.2f}"
            )

        else:

            continue

        cv2.rectangle(
            annotated_image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            3
        )

        cv2.putText(
            annotated_image,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    # --------------------------------------
    # Save result
    # --------------------------------------

    image_name = os.path.splitext(
        os.path.basename(image_path)
    )[0]

    output_path = os.path.join(
        OUTPUT_DIR,
        f"{image_name}_tiled_yolo.jpg"
    )

    cv2.imwrite(
        output_path,
        annotated_image
    )

    # --------------------------------------
    # Display results
    # --------------------------------------

    print("\nYOLO Tiled Detection Results")

    print(
        f"People detected   : {people_count}"
    )

    print(
        f"Vehicles detected : {vehicle_count}"
    )

    print("\nVehicle breakdown:")

    for vehicle, count in (
        vehicle_breakdown.items()
    ):

        print(
            f"{vehicle:12s}: {count}"
        )

    print("\nAnnotated image saved:")
    print(output_path)


# ==========================================
# COMPLETION
# ==========================================

print(
    "\nYOLO tiled detection completed."
)