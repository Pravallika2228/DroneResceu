# DroneRescue AI

## AI-Based Flood Assessment and Emergency Monitoring Using Drone Imagery

DroneRescue AI is an AI-based system that analyzes aerial drone images of flood-affected areas. It combines flood classification, semantic segmentation, and object detection to provide useful information about flooded regions and visible objects.

The system uses EfficientNetB0 + XGBoost for flooded/non-flooded classification, Weighted U-Net for detailed flood-area segmentation, and pretrained YOLO11n for object detection. A Flask-based web application brings these results together and generates a project-defined emergency assessment and rescue priority.

---

## Overview

DroneRescue is designed to automate important parts of flood assessment from aerial drone imagery.

When a drone image is uploaded, the system:

- Determines whether the image is flooded or non-flooded.
- Provides the flood prediction probability.
- Segments different regions in the image.
- Calculates overall flood coverage.
- Calculates flooded building and flooded road areas.
- Detects visible people and vehicles.
- Combines the results into an emergency assessment.
- Generates a project-defined rescue priority.
- Displays the results through a web dashboard.

---

## Key Features

### Flood Classification

The classification pipeline uses:

**EfficientNetB0 → 1,280-dimensional features → XGBoost**

EfficientNetB0 extracts visual features from the input image, while XGBoost performs the final flooded/non-flooded classification.

The output includes:

- Flooded / Non-Flooded status
- Prediction probability

### Flood Area Segmentation

A Weighted U-Net performs semantic segmentation using 10 classes.

The segmentation results are used to calculate:

- Overall flood coverage
- Flooded building area
- Flooded road area

Weighted loss was used to improve the handling of important and minority classes.

### Object Detection

Pretrained YOLO11n is integrated for object detection.

The system uses detected:

- People
- Vehicles

as additional information for the emergency assessment.

### Emergency Assessment

The Emergency Assessment Engine combines:

- Flood prediction
- Flood probability
- Flood coverage
- Flooded building area
- Flooded road area
- People count
- Vehicle count

It then generates:

- Flood severity
- Rescue priority

The severity and rescue-priority rules are project-defined rules and are not official emergency authority standards.

### Web Application

The project includes a Flask-based web application with pages for:

- Home
- Dashboard
- Analyze Image
- Reports
- Analysis History
- Settings
- Help
- Login

---

## System Architecture

```text
Drone / UAV Image
        ↓
Flask Web Application
        ↓
┌──────────────────────────────────────┐
│              AI Pipeline             │
│                                      │
│  EfficientNetB0 + XGBoost            │
│  Flood Classification                │
│                                      │
│  Weighted U-Net                      │
│  Semantic Segmentation               │
│                                      │
│  YOLO11n                             │
│  Object Detection                    │
└──────────────────────────────────────┘
        ↓
Emergency Assessment Engine
        ↓
Flood Status + Flood Coverage
+ Buildings + Roads + People + Vehicles
        ↓
Severity + Rescue Priority
        ↓
Web Dashboard