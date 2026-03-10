"""
LLM Vision inference for tree ring counting (Phase 1).

Primary:  Gemini 3 Flash       (fast, cost-effective)
Fallback: Gemini 3.1 Pro       (higher semantic accuracy)

Falls back when:
- Primary model returns confidence below threshold
- Primary model raises an exception
"""

import base64
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

Return ONLY valid JSON in this exact format — no markdown, no extra text:
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


async def analyze_with_gemini(image_bytes: bytes) -> LLMResult:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=api_key)

    response = await client.aio.models.generate_content(
        model="gemini-3-flash-preview",
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
        model_used="gemini-3-flash",
    )


async def analyze_with_gemini_pro(image_bytes: bytes) -> LLMResult:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=api_key)

    response = await client.aio.models.generate_content(
        model="gemini-3.1-pro-preview",
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
        model_used="gemini-3.1-pro",
    )


async def count_rings(image_bytes: bytes) -> LLMResult:
    """
    Count rings using Gemini 3 Flash; fall back to Gemini 3.1 Pro if needed.
    If the fallback also fails, returns the primary result at whatever
    confidence it had rather than raising.
    """
    best: LLMResult | None = None
    try:
        result = await analyze_with_gemini(image_bytes)
        if result.confidence >= FALLBACK_THRESHOLD:
            return result
        best = result
        logger.warning(
            "Gemini Flash confidence %.2f below threshold %.2f, trying Gemini 3.1 Pro fallback",
            result.confidence,
            FALLBACK_THRESHOLD,
        )
    except Exception as exc:
        logger.warning("Gemini Flash failed (%s), trying Gemini 3.1 Pro fallback", exc)

    try:
        return await analyze_with_gemini_pro(image_bytes)
    except Exception as exc:
        logger.warning("Gemini 3.1 Pro fallback failed (%s)", exc)
        if best is not None:
            logger.info("Returning Gemini Flash result despite low confidence (%.2f)", best.confidence)
            return best
        raise
