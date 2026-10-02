from pathlib import Path
from PIL import Image
import numpy as np
import pandas as pd

DATASET = Path(
    "dataset/FloodNet/FloodNet-Supervised_v1.0"
)

OUTPUT = Path("outputs")
OUTPUT.mkdir(exist_ok=True)


def create_labels(split):

    image_dir = DATASET / split / f"{split}-org-img"
    mask_dir = DATASET / split / f"{split}-label-img"

    images = sorted(image_dir.glob("*.jpg"))

    rows = []

    print(f"\nProcessing {split}: {len(images)} images")

    for i, image_path in enumerate(images, start=1):

        mask_path = (
            mask_dir /
            f"{image_path.stem}_lab.png"
        )

        if not mask_path.exists():
            print("Missing mask:", mask_path.name)
            continue

        mask = np.array(Image.open(mask_path))

        total_pixels = mask.size

        # Explicit FloodNet flood-damage classes
        building_flooded_pixels = np.count_nonzero(mask == 1)
        road_flooded_pixels = np.count_nonzero(mask == 3)

        flood_damage_pixels = (
            building_flooded_pixels +
            road_flooded_pixels
        )

        flood_damage_pct = (
            flood_damage_pixels / total_pixels
        ) * 100

        # DroneRescue derived binary label
        if flood_damage_pixels > 0:
            label = 1
            label_name = "Flooded"
        else:
            label = 0
            label_name = "Non-Flooded"

        rows.append({
            "image": image_path.name,
            "split": split,
            "building_flooded_pct":
                building_flooded_pixels / total_pixels * 100,
            "road_flooded_pct":
                road_flooded_pixels / total_pixels * 100,
            "flood_damage_pct": flood_damage_pct,
            "label": label,
            "label_name": label_name
        })

        if i % 100 == 0:
            print(f"Processed {i}/{len(images)}")

    df = pd.DataFrame(rows)

    output_file = (
        OUTPUT /
        f"{split}_classification_labels.csv"
    )

    df.to_csv(output_file, index=False)

    print("\nResults")
    print("-------------------------")
    print("Total       :", len(df))
    print(
        "Flooded     :",
        (df["label"] == 1).sum()
    )
    print(
        "Non-Flooded :",
        (df["label"] == 0).sum()
    )

    print(
        "Flooded %   :",
        round((df["label"] == 1).mean() * 100, 2)
    )

    print("Saved:", output_file)

    return df


# Keep the official FloodNet splits
train_df = create_labels("train")
val_df = create_labels("val")
test_df = create_labels("test")

print("\n================================")
print("Classification labels completed")
print("================================")