"""Deterministic helpers for turning scripts into reviewable video batches."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
import json
import re
from typing import Any


SENTENCE_END = re.compile(r"(?<=[。！？!?；;])\s*|\n+")
WHITESPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class Scene:
    """One reviewable unit in a production batch."""

    id: str
    narration: str
    estimated_seconds: float
    suggested_visual: str
    source: str


def normalise_text(value: str) -> str:
    return WHITESPACE.sub(" ", value).strip()


def split_script(script: str, max_chars: int) -> list[str]:
    """Split a script by sentence boundaries, then by character length if needed."""
    if max_chars < 20:
        raise ValueError("max_chars must be at least 20")
    text = normalise_text(script)
    if not text:
        raise ValueError("script is empty")

    sentences = [normalise_text(item) for item in SENTENCE_END.split(text) if normalise_text(item)]
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        parts = [sentence[i : i + max_chars] for i in range(0, len(sentence), max_chars)]
        for part in parts:
            candidate = f"{current} {part}".strip()
            if current and len(candidate) > max_chars:
                chunks.append(current)
                current = part
            else:
                current = candidate
    if current:
        chunks.append(current)
    return chunks


def estimate_seconds(text: str, chars_per_second: float) -> float:
    if chars_per_second <= 0:
        raise ValueError("chars_per_second must be greater than zero")
    return round(max(1.0, len(text) / chars_per_second), 1)


def visual_hint(text: str, local_assets: list[str]) -> str:
    """Provide a conservative, human-review-first visual suggestion."""
    if local_assets:
        return "Prioritize a matching local asset; otherwise review platform-suggested footage."
    if any(word in text for word in ("数据", "比例", "增长", "下降", "%")):
        return "Use a source-verified data card or a simple motion graphic."
    if any(word in text for word in ("采访", "口播", "观点", "我认为")):
        return "Use speaker footage or an attribution card; keep the claim reviewable."
    return "Use source-cleared footage or a simple explanatory motion graphic."


def build_plan(
    script_path: Path,
    *,
    title: str,
    aspect_ratio: str,
    max_chars: int,
    chars_per_second: float,
    local_assets: list[str],
) -> dict[str, Any]:
    if aspect_ratio not in {"16:9", "9:16", "1:1"}:
        raise ValueError("aspect_ratio must be one of: 16:9, 9:16, 1:1")
    script = script_path.read_text(encoding="utf-8")
    segments = split_script(script, max_chars)
    scenes = [
        Scene(
            id=f"scene-{index:03d}",
            narration=segment,
            estimated_seconds=estimate_seconds(segment, chars_per_second),
            suggested_visual=visual_hint(segment, local_assets),
            source="local_asset_preferred" if local_assets else "needs_review",
        )
        for index, segment in enumerate(segments, start=1)
    ]
    return {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "project": {
            "title": title,
            "aspect_ratio": aspect_ratio,
            "script_file": script_path.name,
            "script_sha256": sha256(script.encode("utf-8")).hexdigest(),
        },
        "review_checklist": [
            "Verify facts, quotes, and rights before export.",
            "Confirm every suggested visual is appropriate for its narration.",
            "Replace placeholder visual suggestions with approved assets.",
            "Review audio, subtitles, and final framing before publishing.",
        ],
        "local_assets": local_assets,
        "scenes": [asdict(scene) for scene in scenes],
        "estimated_total_seconds": round(sum(scene.estimated_seconds for scene in scenes), 1),
    }


def write_plan(plan: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
