# Dataset Setup

## FloodNet-Supervised v1.0

DroneRescue uses the FloodNet-Supervised v1.0 dataset for training and evaluating the flood classification and semantic segmentation models.

The dataset contains 2,343 UAV images collected using a DJI Mavic Pro after Hurricane Harvey.

---

## Dataset Split

| Split | Images |
|---|---:|
| Train | 1,445 |
| Validation | 450 |
| Test | 448 |
| Total | 2,343 |

---

## Required Folder Structure

After downloading the dataset, place it in the following structure:

```text
dataset/
└── FloodNet/
    └── FloodNet-Supervised_v1.0/
        ├── train/
        │   ├── train-org-img/
        │   └── train-label-img/
        │
        ├── val/
        │   ├── val-org-img/
        │   └── val-label-img/
        │
        ├── test/
        │   ├── test-org-img/
        │   └── test-label-img/
        │
        └── DATASET-VERSION-NOTE-v1.0.txt