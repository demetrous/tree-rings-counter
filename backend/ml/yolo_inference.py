"""
YOLO26-seg inference for tree ring counting (Phase 2).

Drop-in replacement for llm_vision.count_rings().
Loaded lazily on first call so the backend starts fast even without
the model weights present.
"""

from __future__ import annotations

import io
import logging
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

_model = None
_MODEL_PATH = Path(os.getenv("YOLO_WEIGHTS_PATH", "ml/weights/yolo26n-seg-tree-rings.pt"))


def _load_model():
    global _model
    if _model is None:
        try:
            from ultralytics import YOLO  # type: ignore
            _model = YOLO(str(_MODEL_PATH))
            logger.info("YOLO26 model loaded from %s", _MODEL_PATH)
        except Exception as exc:
            raise RuntimeError(
                f"Could not load YOLO26 weights from {_MODEL_PATH}: {exc}\n"
                "Fine-tune a YOLO26n-seg model on tree ring data and place the "
                "weights at the path specified by YOLO_WEIGHTS_PATH."
            ) from exc
    return _model


@dataclass
class YOLOResult:
    ring_count: int
    confidence: float
    notes: str
    model_used: str = "yolo26"


def count_rings_yolo(image_bytes: bytes) -> YOLOResult:
    """
    Run YOLO26-seg inference and count detected ring instances.
    """
    model = _load_model()
    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_array = np.array(pil_img)

    results = model.predict(
        source=img_array,
        conf=0.35,
        iou=0.45,
        verbose=False,
    )

    if not results or results[0].masks is None:
        return YOLOResult(
            ring_count=0,
            confidence=0.0,
            notes="No rings detected by YOLO26. Image quality may be insufficient.",
        )

    masks = results[0].masks
    ring_count = len(masks)
    scores = results[0].boxes.conf.cpu().numpy() if results[0].boxes is not None else []
    avg_confidence = float(np.mean(scores)) if len(scores) > 0 else 0.5

    return YOLOResult(
        ring_count=ring_count,
        confidence=avg_confidence,
        notes=f"YOLO26 detected {ring_count} ring boundaries with average confidence {avg_confidence:.2f}.",
    )
