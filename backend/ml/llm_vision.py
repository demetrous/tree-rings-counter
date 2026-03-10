"""
LLM Vision inference for tree ring counting (Phase 1).

Implements a tiered fallback strategy to balance accuracy, speed, and quotas:
1. Gemini 3 Flash Preview (fastest, newest)
2. Gemini 3.1 Pro Preview (most accurate, strict quotas)
3. Gemini 2.5 Pro (stable fallback, generous quotas)
4. Gemini 2.5 Flash (last resort)
"""

import json
import logging
import os
import re
from dataclasses import dataclass

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

FALLBACK_THRESHOLD = float(os.getenv("FALLBACK_CONFIDENCE_THRESHOLD", "0.5"))

RING_COUNT_PROMPT = """You are an expert dendrochronologist analyzing a tree cross-section photograph.

Count ALL visible annual growth rings in this image. Each ring represents one year of growth.

Rules:
- Count from the pith (centre) outward to the bark
- Include rings that are partially visible
- If the image shows only a partial cross-section, estimate the full count proportionally
- Do NOT count the bark itself as a ring

Return ONLY valid JSON in this exact format - no markdown, no extra text:
{
  "ring_count": <integer>,
  "confidence": <float between 0.0 and 1.0>,
  "notes": "<brief explanation of confidence or any issues observed>"
}"""


@dataclass
class LLMResult:
    ring_count: int
    confidence: float
    notes: str
    model_used: str


def _parse_llm_json(text: str) -> dict:
    """Extract JSON from model response, handling markdown fences."""
    text = text.strip()
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    return json.loads(text)


async def analyze_with_model(image_bytes: bytes, model_name: str) -> LLMResult:
    """Run inference using a specific Gemini model."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=api_key)

    response = await client.aio.models.generate_content(
        model=model_name,
        contents=[
            RING_COUNT_PROMPT,
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
        ],
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )

    data = _parse_llm_json(response.text)
    return LLMResult(
        ring_count=int(data["ring_count"]),
        confidence=float(data["confidence"]),
        notes=str(data.get("notes", "")),
        model_used=model_name,
    )


async def count_rings(image_bytes: bytes) -> LLMResult:
    """
    Count rings using a tiered fallback strategy.
    Tries models in order, falling back if confidence is low or if an error (like quota exceeded) occurs.
    """
    models_to_try = [
        "gemini-3-flash-preview",
        "gemini-3.1-pro-preview",
        "gemini-2.5-pro",
        "gemini-2.5-flash"
    ]
    
    best: LLMResult | None = None
    last_error: Exception | None = None

    for model in models_to_try:
        try:
            logger.info("Attempting inference with %s", model)
            result = await analyze_with_model(image_bytes, model)
            
            if result.confidence >= FALLBACK_THRESHOLD:
                logger.info("%s succeeded with high confidence (%.2f)", model, result.confidence)
                return result
                
            # Keep track of the best result seen so far in case all models have low confidence
            if best is None or result.confidence > best.confidence:
                best = result
                
            logger.warning(
                "%s confidence %.2f below threshold %.2f, trying next fallback",
                model, result.confidence, FALLBACK_THRESHOLD
            )
        except Exception as exc:
            last_error = exc
            logger.warning("%s failed (%s), trying next fallback", model, exc)

    # If we get here, all models either failed or had low confidence
    if best is not None:
        logger.info("All models had low confidence. Returning best result (%.2f) from %s", best.confidence, best.model_used)
        return best
        
    # If we didn't get a single successful result, raise the last error
    logger.error("All Gemini models failed.")
    if last_error:
        raise last_error
    raise RuntimeError("Failed to process image with any Gemini model.")
