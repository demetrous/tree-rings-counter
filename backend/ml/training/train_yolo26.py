"""
Phase 2: Fine-tune YOLO26n-seg on tree ring images.

Prerequisites
-------------
1. Install ultralytics:  pip install ultralytics
2. Prepare dataset in YOLO segmentation format (see dataset.yaml below)
3. Run: python train_yolo26.py

Dataset sources
---------------
- Poláček et al. 2023 annotated dataset (Zenodo):
    https://zenodo.org/record/8428752
  Convert polyline annotations to YOLO segmentation masks using
  convert_polacek_to_yolo.py in this directory.
- Your own phone-camera photos collected via the app (opt-in contributions).

Dataset structure expected
--------------------------
data/
  train/
    images/   *.jpg
    labels/   *.txt   (YOLO segmentation format)
  val/
    images/
    labels/
"""

from pathlib import Path
from ultralytics import YOLO  # type: ignore

# ── Config ──────────────────────────────────────────────────────────────────
DATASET_YAML = "ml/training/dataset.yaml"
BASE_WEIGHTS = "yolo26n-seg.pt"          # Ultralytics will download on first run
OUTPUT_DIR   = "ml/weights"
EPOCHS       = 150
IMG_SIZE     = 1024
BATCH        = 8                          # reduce to 4 if VRAM is limited
PROJECT_NAME = "tree-rings-yolo26"
# ────────────────────────────────────────────────────────────────────────────


def train():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    model = YOLO(BASE_WEIGHTS)

    results = model.train(
        data=DATASET_YAML,
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        batch=BATCH,
        project=OUTPUT_DIR,
        name=PROJECT_NAME,
        # Augmentation — important for generalising to messy phone photos
        flipud=0.3,
        fliplr=0.5,
        degrees=45,
        hsv_h=0.02,
        hsv_s=0.4,
        hsv_v=0.3,
        mosaic=0.5,
        # Freeze backbone for first 20 epochs (transfer learning)
        freeze=10,
        patience=30,
        save_period=10,
        val=True,
        plots=True,
        verbose=True,
    )

    best_path = Path(OUTPUT_DIR) / PROJECT_NAME / "weights" / "best.pt"
    print(f"\nTraining complete. Best weights: {best_path}")
    print(
        f"Set YOLO_WEIGHTS_PATH={best_path} and USE_YOLO=true in your .env "
        "to switch the backend to YOLO26 inference."
    )
    return results


if __name__ == "__main__":
    train()
