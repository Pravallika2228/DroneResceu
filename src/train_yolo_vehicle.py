from ultralytics import YOLO
import os


# ==========================================
# SETTINGS
# ==========================================

DATA_YAML = (
    "dataset/yolo_vehicle_dataset/data.yaml"
)

BASE_MODEL = "yolo11n.pt"

OUTPUT_DIR = "models/yolo_vehicle"

EPOCHS = 30
IMAGE_SIZE = 640
BATCH_SIZE = 4

DEVICE = "cpu"

PROJECT_NAME = "DroneRescue"


# ==========================================
# CREATE OUTPUT DIRECTORY
# ==========================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ==========================================
# LOAD PRETRAINED YOLO
# ==========================================

print("Loading pretrained YOLO11n...")

model = YOLO(
    BASE_MODEL
)

print("YOLO11n loaded successfully.")


# ==========================================
# TRAIN
# ==========================================

print("\nStarting Vehicle Detection Training")

print(
    f"Dataset : {DATA_YAML}"
)

print(
    f"Epochs  : {EPOCHS}"
)

print(
    f"Image   : {IMAGE_SIZE}"
)

print(
    f"Batch   : {BATCH_SIZE}"
)

print(
    f"Device  : {DEVICE}"
)


results = model.train(

    data=DATA_YAML,

    epochs=EPOCHS,

    imgsz=IMAGE_SIZE,

    batch=BATCH_SIZE,

    device=DEVICE,

    project=OUTPUT_DIR,

    name=PROJECT_NAME,

    pretrained=True,

    optimizer="auto",

    patience=8,

    save=True,

    plots=True,

    verbose=True
)


# ==========================================
# TRAINING COMPLETED
# ==========================================

print(
    "\nYOLO vehicle training completed."
)

print(
    "Best model should be available at:"
)

print(
    "models/yolo_vehicle/"
    "DroneRescue/weights/best.pt"
)