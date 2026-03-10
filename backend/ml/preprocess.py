"""
Image preprocessing pipeline for tree ring analysis.

Prepares raw phone photos for LLM or YOLO inference:
1. Converts to RGB
2. Applies CLAHE (contrast-limited adaptive histogram equalisation)
   to bring out ring detail in low-contrast cuts
3. Detects the circular cut surface with Hough Circle Transform
   and crops/masks to it
4. Resizes to a fixed 1024×1024 square
"""

import io
import cv2
import numpy as np
from PIL import Image
import pillow_heif

# Register HEIF opener with PIL
pillow_heif.register_heif_opener()

TARGET_SIZE = 1024


def preprocess_image(image_bytes: bytes) -> tuple[bytes, dict]:
    """
    Preprocess raw image bytes for ring detection.

    Returns:
        processed_bytes: JPEG-encoded preprocessed image
        meta: dict with detected circle info (cx, cy, radius) or None
    """
    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = np.array(pil_img)
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    meta: dict = {"circle": None, "original_size": img.shape[:2]}

    # --- CLAHE on luminance channel ---
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l_ch, a_ch, b_ch = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l_ch = clahe.apply(l_ch)
    lab = cv2.merge([l_ch, a_ch, b_ch])
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # --- Circle detection (Hough) ---
    gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.GaussianBlur(gray, (9, 9), 2)
    h, w = gray.shape
    min_r = min(h, w) // 6
    max_r = min(h, w) // 2

    circles = cv2.HoughCircles(
        gray_blur,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=min(h, w) // 4,
        param1=60,
        param2=35,
        minRadius=min_r,
        maxRadius=max_r,
    )

    if circles is not None:
        circles = np.round(circles[0, :]).astype(int)
        # Pick the largest circle
        cx, cy, r = sorted(circles, key=lambda c: c[2], reverse=True)[0]
        meta["circle"] = {"cx": int(cx), "cy": int(cy), "radius": int(r)}

        # Crop to bounding box of detected circle with 5% padding
        pad = int(r * 0.05)
        x1 = max(0, cx - r - pad)
        y1 = max(0, cy - r - pad)
        x2 = min(w, cx + r + pad)
        y2 = min(h, cy + r + pad)
        cropped = enhanced[y1:y2, x1:x2]
    else:
        # No circle found — use centre crop
        side = min(h, w)
        y1 = (h - side) // 2
        x1 = (w - side) // 2
        cropped = enhanced[y1 : y1 + side, x1 : x1 + side]

    # --- Resize to TARGET_SIZE ---
    resized = cv2.resize(cropped, (TARGET_SIZE, TARGET_SIZE), interpolation=cv2.INTER_LANCZOS4)

    # --- Encode back to JPEG ---
    success, buf = cv2.imencode(".jpg", resized, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if not success:
        raise ValueError("Failed to encode preprocessed image")

    return bytes(buf), meta
