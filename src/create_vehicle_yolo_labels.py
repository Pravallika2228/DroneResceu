import os
import cv2
import numpy as np


# ==========================================
# SETTINGS
# ==========================================

DATASET_ROOT = (
    "dataset/FloodNet/"
    "FloodNet-Supervised_v1.0"
)

# FloodNet semantic segmentation class
FLOODNET_VEHICLE_CLASS = 7

# YOLO class ID for our one-class detector
YOLO_VEHICLE_CLASS = 0

# Ignore extremely tiny regions
MIN_VEHICLE_AREA = 20

# Number of visual samples per split
NUM_SAMPLES = 5

# Output directory for YOLO labels
YOLO_LABEL_ROOT = os.path.join(
    DATASET_ROOT,
    "yolo_vehicle_labels"
)

# Output directory for visual inspection
SAMPLE_ROOT = (
    "outputs/vehicle_yolo_samples"
)


# ==========================================
# CREATE OUTPUT DIRECTORIES
# ==========================================

os.makedirs(
    YOLO_LABEL_ROOT,
    exist_ok=True
)

os.makedirs(
    SAMPLE_ROOT,
    exist_ok=True
)


# ==========================================
# PROCESS ONE DATASET SPLIT
# ==========================================

def process_split(split):

    image_dir = os.path.join(
        DATASET_ROOT,
        split,
        f"{split}-org-img"
    )

    mask_dir = os.path.join(
        DATASET_ROOT,
        split,
        f"{split}-label-img"
    )

    label_dir = os.path.join(
        YOLO_LABEL_ROOT,
        split
    )

    sample_dir = os.path.join(
        SAMPLE_ROOT,
        split
    )

    os.makedirs(
        label_dir,
        exist_ok=True
    )

    os.makedirs(
        sample_dir,
        exist_ok=True
    )

    # --------------------------------------
    # Find masks
    # --------------------------------------

    mask_files = [
        filename
        for filename in os.listdir(mask_dir)
        if filename.endswith("_lab.png")
    ]

    mask_files.sort()

    print(
        f"\n{split.upper()} SPLIT"
    )

    print(
        f"Found {len(mask_files)} mask files."
    )

    processed_images = 0
    images_with_vehicles = 0
    total_boxes = 0
    sample_count = 0

    # ======================================
    # PROCESS MASKS
    # ======================================

    for mask_filename in mask_files:

        mask_path = os.path.join(
            mask_dir,
            mask_filename
        )

        # Example:
        # 10163_lab.png
        #       ↓
        # 10163.jpg

        image_id = mask_filename.replace(
            "_lab.png",
            ""
        )

        image_path = os.path.join(
            image_dir,
            image_id + ".jpg"
        )

        if not os.path.exists(image_path):

            print(
                f"Image not found: {image_id}"
            )

            continue

        # ----------------------------------
        # Read mask
        # ----------------------------------

        mask = cv2.imread(
            mask_path,
            cv2.IMREAD_GRAYSCALE
        )

        if mask is None:

            print(
                f"Could not read mask: "
                f"{mask_path}"
            )

            continue

        height, width = mask.shape

        # ----------------------------------
        # Extract FloodNet Vehicle pixels
        # ----------------------------------

        vehicle_mask = np.where(
            mask == FLOODNET_VEHICLE_CLASS,
            255,
            0
        ).astype(np.uint8)

        # ----------------------------------
        # Connected components
        # ----------------------------------

        num_labels, labels, stats, centroids = (
            cv2.connectedComponentsWithStats(
                vehicle_mask,
                connectivity=8
            )
        )

        yolo_labels = []
        bounding_boxes = []

        # ==================================
        # PROCESS VEHICLE COMPONENTS
        # ==================================

        for component_id in range(
            1,
            num_labels
        ):

            x = stats[
                component_id,
                cv2.CC_STAT_LEFT
            ]

            y = stats[
                component_id,
                cv2.CC_STAT_TOP
            ]

            box_width = stats[
                component_id,
                cv2.CC_STAT_WIDTH
            ]

            box_height = stats[
                component_id,
                cv2.CC_STAT_HEIGHT
            ]

            area = stats[
                component_id,
                cv2.CC_STAT_AREA
            ]

            # Ignore tiny regions
            if area < MIN_VEHICLE_AREA:
                continue

            # ==================================
            # CONVERT TO YOLO FORMAT
            # ==================================

            x_center = (
                x + box_width / 2
            ) / width

            y_center = (
                y + box_height / 2
            ) / height

            normalized_width = (
                box_width / width
            )

            normalized_height = (
                box_height / height
            )

            # IMPORTANT:
            # YOLO class ID is 0,
            # NOT FloodNet class ID 7.

            yolo_line = (
                f"{YOLO_VEHICLE_CLASS} "
                f"{x_center:.6f} "
                f"{y_center:.6f} "
                f"{normalized_width:.6f} "
                f"{normalized_height:.6f}"
            )

            yolo_labels.append(
                yolo_line
            )

            bounding_boxes.append(
                (
                    x,
                    y,
                    box_width,
                    box_height
                )
            )

        # ==================================
        # SAVE YOLO LABEL
        # ==================================

        label_path = os.path.join(
            label_dir,
            image_id + ".txt"
        )

        with open(
            label_path,
            "w"
        ) as file:

            for line in yolo_labels:

                file.write(
                    line + "\n"
                )

        processed_images += 1

        if len(yolo_labels) > 0:

            images_with_vehicles += 1

            total_boxes += len(
                yolo_labels
            )

        # ==================================
        # SAVE VISUAL SAMPLES
        # ==================================

        if (
            len(yolo_labels) > 0
            and sample_count < NUM_SAMPLES
        ):

            image = cv2.imread(
                image_path
            )

            if image is not None:

                for (
                    x,
                    y,
                    box_width,
                    box_height
                ) in bounding_boxes:

                    cv2.rectangle(
                        image,
                        (x, y),
                        (
                            x + box_width,
                            y + box_height
                        ),
                        (0, 255, 0),
                        3
                    )

                    cv2.putText(
                        image,
                        "Vehicle",
                        (
                            x,
                            max(y - 10, 25)
                        ),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2
                    )

                sample_path = os.path.join(
                    sample_dir,
                    f"{image_id}_vehicle_boxes.jpg"
                )

                cv2.imwrite(
                    sample_path,
                    image
                )

                sample_count += 1

                print(
                    f"Sample saved: "
                    f"{sample_path}"
                )

    # ======================================
    # SPLIT SUMMARY
    # ======================================

    print(
        f"{split.upper()} images processed "
        f"     : {processed_images}"
    )

    print(
        f"{split.upper()} images with vehicles "
        f": {images_with_vehicles}"
    )

    print(
        f"{split.upper()} vehicle boxes "
        f"      : {total_boxes}"
    )

    print(
        f"{split.upper()} labels saved "
        f"        : {label_dir}"
    )


# ==========================================
# PROCESS ALL SPLITS
# ==========================================

process_split("train")

process_split("val")

process_split("test")


# ==========================================
# FINAL MESSAGE
# ==========================================

print(
    "\nVehicle YOLO dataset labels "
    "generated successfully."
)

print(
    "FloodNet Vehicle class: 7"
)

print(
    "YOLO Vehicle class: 0"
)

print(
    f"Labels root: {YOLO_LABEL_ROOT}"
)

print(
    f"Samples root: {SAMPLE_ROOT}"
)