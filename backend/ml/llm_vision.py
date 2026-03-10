"""
LLM Vision inference for tree ring counting (Phase 1).

Primary:  Gemini 2.5 Flash  (fast, cost-effective)
Fallback: GPT-4o            (higher semantic accuracy)

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
from openai import AsyncOpenAI

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


async def analyze_with_gpt4o(image_bytes: bytes) -> LLMResult:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set")

    client = AsyncOpenAI(api_key=api_key)
    b64 = base64.b64encode(image_bytes).decode()

    response = await client.chat.completions.create(
        model="gpt-4o",
        max_tokens=256,
        temperature=0.1,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": RING_COUNT_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64}",
                            "detail": "high",
                        },
                    },
                ],
            }
        ],
    )

    text = response.choices[0].message.content or ""
    data = _parse_llm_json(text)
    return LLMResult(
        ring_count=int(data["ring_count"]),
        confidence=float(data["confidence"]),
        notes=str(data.get("notes", "")),
        model_used="gpt-4o",
    )


def _openai_key_looks_valid() -> bool:
    """Return False if the OpenAI key is missing or still a placeholder."""
    key = os.getenv("OPENAI_API_KEY", "")
    return bool(key) and not key.startswith("your_") and key != "sk-..."


async def count_rings(image_bytes: bytes) -> LLMResult:
    """
    Count rings using Gemini 2.5 Flash; fall back to GPT-4o if needed.
    If the fallback also fails (e.g. no valid OpenAI key), returns the
    primary result at whatever confidence it had rather than raising.
    """
    primary = os.getenv("PRIMARY_MODEL", "gemini").lower()

    if primary == "gemini":
        best: LLMResult | None = None
        try:
            result = await analyze_with_gemini(image_bytes)
            if result.confidence >= FALLBACK_THRESHOLD:
                return result
            best = result
            logger.warning(
                "Gemini confidence %.2f below threshold %.2f, trying GPT-4o fallback",
                result.confidence,
                FALLBACK_THRESHOLD,
            )
        except Exception as exc:
            logger.warning("Gemini failed (%s), trying GPT-4o fallback", exc)

        if not _openai_key_looks_valid():
            logger.warning("OPENAI_API_KEY not configured — skipping GPT-4o fallback")
            if best is not None:
                return best
            raise EnvironmentError(
                "GEMINI_API_KEY returned low-confidence result and OPENAI_API_KEY is not set"
            )

        try:
            return await analyze_with_gpt4o(image_bytes)
        except Exception as exc:
            logger.warning("GPT-4o fallback failed (%s)", exc)
            if best is not None:
                logger.info("Returning Gemini result despite low confidence (%.2f)", best.confidence)
                return best
            raise

    # openai primary
    best = None
    try:
        result = await analyze_with_gpt4o(image_bytes)
        if result.confidence >= FALLBACK_THRESHOLD:
            return result
        best = result
        logger.warning("GPT-4o confidence low, trying Gemini fallback")
    except Exception as exc:
        logger.warning("GPT-4o failed (%s), trying Gemini fallback", exc)

    try:
        return await analyze_with_gemini(image_bytes)
    except Exception as exc:
        logger.warning("Gemini fallback also failed (%s)", exc)
        if best is not None:
            return best
        raise
