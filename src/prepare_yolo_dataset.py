import os
import shutil


# ==========================================
# PATHS
# ==========================================

DATASET_ROOT = (
    "dataset/FloodNet/"
    "FloodNet-Supervised_v1.0"
)

GENERATED_LABEL_ROOT = os.path.join(
    DATASET_ROOT,
    "yolo_vehicle_labels"
)

YOLO_DATASET_ROOT = (
    "dataset/yolo_vehicle_dataset"
)


# ==========================================
# YOLO DATASET STRUCTURE
# ==========================================

SPLITS = [
    "train",
    "val",
    "test"
]


# ==========================================
# CREATE DIRECTORIES
# ==========================================

for split in SPLITS:

    os.makedirs(
        os.path.join(
            YOLO_DATASET_ROOT,
            "images",
            split
        ),
        exist_ok=True
    )

    os.makedirs(
        os.path.join(
            YOLO_DATASET_ROOT,
            "labels",
            split
        ),
        exist_ok=True
    )


# ==========================================
# COPY IMAGES AND LABELS
# ==========================================

for split in SPLITS:

    print(f"\nPreparing {split.upper()} dataset...")

    source_image_dir = os.path.join(
        DATASET_ROOT,
        split,
        f"{split}-org-img"
    )

    source_label_dir = os.path.join(
        GENERATED_LABEL_ROOT,
        split
    )

    destination_image_dir = os.path.join(
        YOLO_DATASET_ROOT,
        "images",
        split
    )

    destination_label_dir = os.path.join(
        YOLO_DATASET_ROOT,
        "labels",
        split
    )

    image_count = 0
    label_count = 0

    # --------------------------------------
    # Get images
    # --------------------------------------

    image_files = [
        filename
        for filename in os.listdir(
            source_image_dir
        )
        if filename.lower().endswith(
            (".jpg", ".jpeg", ".png")
        )
    ]

    image_files.sort()

    # --------------------------------------
    # Copy images
    # --------------------------------------

    for image_filename in image_files:

        source_image = os.path.join(
            source_image_dir,
            image_filename
        )

        destination_image = os.path.join(
            destination_image_dir,
            image_filename
        )

        shutil.copy2(
            source_image,
            destination_image
        )

        image_count += 1

        # ----------------------------------
        # Find corresponding YOLO label
        # ----------------------------------

        image_id = os.path.splitext(
            image_filename
        )[0]

        label_filename = (
            image_id + ".txt"
        )

        source_label = os.path.join(
            source_label_dir,
            label_filename
        )

        destination_label = os.path.join(
            destination_label_dir,
            label_filename
        )

        # Every image gets a label file.
        # Images without vehicles receive
        # an empty .txt file.

        if os.path.exists(source_label):

            shutil.copy2(
                source_label,
                destination_label
            )

        else:

            open(
                destination_label,
                "w"
            ).close()

        label_count += 1

    # --------------------------------------
    # Split summary
    # --------------------------------------

    print(
        f"Images copied : {image_count}"
    )

    print(
        f"Labels created: {label_count}"
    )


# ==========================================
# CREATE data.yaml
# ==========================================

yaml_path = os.path.join(
    YOLO_DATASET_ROOT,
    "data.yaml"
)


yaml_content = f"""path: {os.path.abspath(YOLO_DATASET_ROOT)}

train: images/train
val: images/val
test: images/test

nc: 1

names:
  0: Vehicle
"""


with open(
    yaml_path,
    "w",
    encoding="utf-8"
) as file:
    file.write(
        yaml_content
    )


# ==========================================
# FINAL OUTPUT
# ==========================================

print(
    "\nYOLO dataset preparation completed."
)

print(
    f"Dataset location: "
    f"{YOLO_DATASET_ROOT}"
)

print(
    f"data.yaml: {yaml_path}"
)