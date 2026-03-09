"""
POST /analyze — accepts a photo and returns tree age estimation.
"""

import logging
import os
import time
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from ml.preprocess import preprocess_image
from ml.llm_vision import count_rings

logger = logging.getLogger(__name__)

router = APIRouter()

# Maximum upload size: 20 MB
MAX_BYTES = 20 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}

# Age margin is ±1 year per 20 rings as a rough estimate
def _age_margin(ring_count: int) -> int:
    if ring_count < 20:
        return 2
    if ring_count < 60:
        return 3
    return max(3, ring_count // 20)


class AnalysisResponse(BaseModel):
    id: str
    ring_count: int
    estimated_age: int
    age_margin: int
    confidence: float
    notes: str
    annotated_image_url: str | None
    model_used: str
    processing_time_ms: int


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(file: UploadFile = File(...)):
    # --- Validate ---
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES and not content_type.startswith("image/"):
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {content_type}. Upload a JPEG, PNG, or WEBP image.",
        )

    image_bytes = await file.read()
    if len(image_bytes) > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Image is too large. Maximum size is 20 MB.",
        )
    if len(image_bytes) < 1024:
        raise HTTPException(status_code=400, detail="Image file appears to be empty or corrupt.")

    start_ms = time.monotonic()

    # --- Preprocess ---
    try:
        processed_bytes, _meta = preprocess_image(image_bytes)
    except Exception as exc:
        logger.exception("Preprocessing failed")
        raise HTTPException(status_code=422, detail=f"Image preprocessing failed: {exc}") from exc

    # --- Inference ---
    use_yolo = os.getenv("USE_YOLO", "false").lower() == "true"

    if use_yolo:
        from ml.yolo_inference import count_rings_yolo
        try:
            result = count_rings_yolo(processed_bytes)
            model_used = result.model_used
            ring_count = result.ring_count
            confidence = result.confidence
            notes = result.notes
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
    else:
        try:
            result = await count_rings(processed_bytes)
            model_used = result.model_used
            ring_count = result.ring_count
            confidence = result.confidence
            notes = result.notes
        except EnvironmentError as exc:
            raise HTTPException(
                status_code=503,
                detail=str(exc) + " — set the API key in your .env file.",
            ) from exc
        except Exception as exc:
            logger.exception("LLM inference failed")
            raise HTTPException(
                status_code=502, detail=f"AI inference failed: {exc}"
            ) from exc

    elapsed_ms = int((time.monotonic() - start_ms) * 1000)

    return AnalysisResponse(
        id=str(uuid.uuid4()),
        ring_count=ring_count,
        estimated_age=ring_count,
        age_margin=_age_margin(ring_count),
        confidence=round(confidence, 3),
        notes=notes,
        annotated_image_url=None,
        model_used=model_used,
        processing_time_ms=elapsed_ms,
    )
