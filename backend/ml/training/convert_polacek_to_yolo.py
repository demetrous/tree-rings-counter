"""
Convert Poláček et al. 2023 CVAT 1.1 XML annotations to YOLO segmentation format.

The Poláček dataset stores ring boundaries as polylines in CVAT XML.
YOLO segmentation expects closed polygon masks normalised to [0, 1].

Usage
-----
1. Download the dataset from Zenodo: https://zenodo.org/record/8428752
2. Run:
   python convert_polacek_to_yolo.py \
       --cvat_xml path/to/annotations.xml \
       --images_dir path/to/images \
       --output_dir data/train
"""

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

import cv2
import numpy as np


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--cvat_xml", required=True)
    p.add_argument("--images_dir", required=True)
    p.add_argument("--output_dir", required=True)
    p.add_argument(
        "--ring_thickness",
        type=int,
        default=8,
        help="Pixel thickness for polyline-to-mask conversion",
    )
    return p.parse_args()


def polyline_to_mask(points_str: str, img_w: int, img_h: int, thickness: int) -> np.ndarray:
    """Convert CVAT polyline string 'x1,y1;x2,y2;...' to a binary mask."""
    pts = [
        (float(xy.split(",")[0]), float(xy.split(",")[1]))
        for xy in points_str.strip().split(";")
        if "," in xy
    ]
    pts_arr = np.array(pts, dtype=np.int32)
    mask = np.zeros((img_h, img_w), dtype=np.uint8)
    cv2.polylines(mask, [pts_arr], isClosed=False, color=255, thickness=thickness)
    return mask


def mask_to_yolo_polygon(mask: np.ndarray) -> list[float] | None:
    """Extract the largest contour from a binary mask and normalise to [0,1]."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    contour = max(contours, key=cv2.contourArea)
    if cv2.contourArea(contour) < 50:
        return None
    h, w = mask.shape
    pts = contour.squeeze()
    if pts.ndim != 2:
        return None
    normalized = []
    for x, y in pts:
        normalized.extend([x / w, y / h])
    return normalized


def convert(cvat_xml: str, images_dir: str, output_dir: str, thickness: int):
    out_path = Path(output_dir)
    labels_path = out_path / "labels"
    labels_path.mkdir(parents=True, exist_ok=True)

    tree = ET.parse(cvat_xml)
    root = tree.getroot()

    for image_el in root.iter("image"):
        img_name = image_el.get("name", "")
        img_w = int(image_el.get("width", 0))
        img_h = int(image_el.get("height", 0))

        if img_w == 0 or img_h == 0:
            img_path = Path(images_dir) / img_name
            if img_path.exists():
                img = cv2.imread(str(img_path))
                if img is not None:
                    img_h, img_w = img.shape[:2]

        lines = []
        for poly_el in image_el.iter("polyline"):
            label = poly_el.get("label", "")
            if label.lower() not in ("ringbndy", "ring", "ringboundary"):
                continue
            points_str = poly_el.get("points", "")
            if not points_str:
                continue
            mask = polyline_to_mask(points_str, img_w, img_h, thickness)
            polygon = mask_to_yolo_polygon(mask)
            if polygon:
                coords = " ".join(f"{v:.6f}" for v in polygon)
                lines.append(f"0 {coords}")

        if lines:
            stem = Path(img_name).stem
            label_file = labels_path / f"{stem}.txt"
            label_file.write_text("\n".join(lines))
            print(f"  {stem}: {len(lines)} rings")


def main():
    args = parse_args()
    print(f"Converting {args.cvat_xml} → {args.output_dir}")
    convert(args.cvat_xml, args.images_dir, args.output_dir, args.ring_thickness)
    print("Done.")


if __name__ == "__main__":
    main()
