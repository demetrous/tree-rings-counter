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

import google.generativeai as genai
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

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")

    import PIL.Image
    import io
    pil_image = PIL.Image.open(io.BytesIO(image_bytes))

    response = model.generate_content(
        [RING_COUNT_PROMPT, pil_image],
        generation_config=genai.GenerationConfig(
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )

    data = _parse_llm_json(response.text)
    return LLMResult(
        ring_count=int(data["ring_count"]),
        confidence=float(data["confidence"]),
        notes=str(data.get("notes", "")),
        model_used="gemini-2.5-flash",
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


async def count_rings(image_bytes: bytes) -> LLMResult:
    """
    Count rings using Gemini 2.5 Flash; fall back to GPT-4o if needed.
    """
    primary = os.getenv("PRIMARY_MODEL", "gemini").lower()

    if primary == "gemini":
        try:
            result = await analyze_with_gemini(image_bytes)
            if result.confidence >= FALLBACK_THRESHOLD:
                return result
            logger.warning(
                "Gemini confidence %.2f below threshold %.2f, falling back to GPT-4o",
                result.confidence,
                FALLBACK_THRESHOLD,
            )
        except Exception as exc:
            logger.warning("Gemini failed (%s), falling back to GPT-4o", exc)

        return await analyze_with_gpt4o(image_bytes)

    # openai primary
    try:
        result = await analyze_with_gpt4o(image_bytes)
        if result.confidence >= FALLBACK_THRESHOLD:
            return result
        logger.warning("GPT-4o confidence low, falling back to Gemini")
    except Exception as exc:
        logger.warning("GPT-4o failed (%s), falling back to Gemini", exc)

    return await analyze_with_gemini(image_bytes)
