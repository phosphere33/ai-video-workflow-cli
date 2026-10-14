"""Local-first subtitle and B-roll editing primitives."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
import csv
import json
import re
import shutil
import subprocess
from typing import Iterable


SRT_TIME = re.compile(r"(?P<start>\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(?P<end>\d{2}:\d{2}:\d{2},\d{3})")
WORD = re.compile(r"[\u4e00-\u9fff]{2,}|[A-Za-z]{3,}")


@dataclass(frozen=True)
class Caption:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class BrollAsset:
    path: str
    tags: tuple[str, ...]
    rights_note: str
    source_url: str


@dataclass(frozen=True)
class Insert:
    start: float
    end: float
    text: str
    asset: str | None
    match_terms: tuple[str, ...]
    rights_note: str | None
    source_url: str | None


def require_program(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"{name} was not found on PATH")
    return path


def seconds(timestamp: str) -> float:
    hours, minutes, rest = timestamp.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(rest)


def parse_srt(path: Path) -> list[Caption]:
    captions: list[Caption] = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip()):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        time_index = next((i for i, line in enumerate(lines) if SRT_TIME.fullmatch(line)), None)
        if time_index is None:
            continue
        match = SRT_TIME.fullmatch(lines[time_index])
        assert match is not None
        text = " ".join(lines[time_index + 1 :])
        if text:
            captions.append(Caption(seconds(match["start"]), seconds(match["end"]), text))
    if not captions:
        raise ValueError(f"No valid captions found in {path}")
    return captions


def load_catalog(path: Path) -> list[BrollAsset]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"path", "tags", "rights_note", "source_url"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("catalog must have path,tags,rights_note,source_url columns")
        return [BrollAsset(row["path"].strip(), tuple(tag.strip().lower() for tag in row["tags"].split("|") if tag.strip()), row["rights_note"].strip(), row["source_url"].strip()) for row in reader if row["path"].strip()]


def terms(text: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(token.lower() for token in WORD.findall(text)))


def choose_asset(caption: Caption, assets: Iterable[BrollAsset]) -> tuple[BrollAsset | None, tuple[str, ...]]:
    query = set(terms(caption.text))
    caption_text = caption.text.lower()
    candidates = [
        (len(matched), asset, matched)
        for asset in assets
        if (matched := tuple(tag for tag in asset.tags if tag in query or (any("\u4e00" <= char <= "\u9fff" for char in tag) and tag in caption_text)))
    ]
    if not candidates:
        return None, ()
    _, asset, matched = max(candidates, key=lambda item: item[0])
    return asset, matched


def build_inserts(captions: list[Caption], assets: list[BrollAsset]) -> list[Insert]:
    result: list[Insert] = []
    for caption in captions:
        asset, matched = choose_asset(caption, assets)
        result.append(Insert(caption.start, caption.end, caption.text, asset.path if asset else None, matched, asset.rights_note if asset else None, asset.source_url if asset else None))
    return result


def run_whisper(video: Path, output_dir: Path, model: str) -> Path:
    require_program("whisper")
    output_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["whisper", str(video), "--model", model, "--output_format", "srt", "--output_dir", str(output_dir)], check=True)
    srt = output_dir / f"{video.stem}.srt"
    if not srt.exists():
        raise RuntimeError(f"Whisper completed but did not produce {srt}")
    return srt


def render_subtitles(video: Path, srt: Path, output: Path) -> list[str]:
    require_program("ffmpeg")
    output.parent.mkdir(parents=True, exist_ok=True)
    subtitle_path = str(srt.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", r"\'")
    command = ["ffmpeg", "-y", "-i", str(video), "-vf", f"subtitles='{subtitle_path}'", "-c:a", "copy", str(output)]
    subprocess.run(command, check=True)
    return command


def broll_command(video: Path, inserts: list[Insert], output: Path) -> list[str]:
    """Build an FFmpeg full-frame B-roll rough-cut command from approved assets."""
    selected = [item for item in inserts if item.asset and Path(item.asset).is_file()]
    if not selected:
        raise ValueError("No matched B-roll paths exist locally; check catalog paths and tags")
    command = ["ffmpeg", "-y", "-i", str(video)]
    graph = ["[0:v]setpts=PTS-STARTPTS[v0]"]
    previous = "v0"
    for index, item in enumerate(selected, start=1):
        command.extend(["-stream_loop", "-1", "-i", str(item.asset)])
        graph.append(f"[{index}:v]setpts=PTS-STARTPTS[br{index}]")
        graph.append(f"[{previous}][br{index}]overlay=0:0:enable='between(t,{item.start:.3f},{item.end:.3f})'[v{index}]")
        previous = f"v{index}"
    command.extend(["-filter_complex", ";".join(graph), "-map", f"[{previous}]", "-map", "0:a?", "-c:v", "libx264", "-c:a", "copy", str(output)])
    return command


def render_broll(video: Path, inserts: list[Insert], output: Path) -> list[str]:
    require_program("ffmpeg")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = broll_command(video, inserts, output)
    subprocess.run(command, check=True)
    return command


def write_manifest(video: Path, srt: Path, inserts: list[Insert], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "source_video": str(video),
        "source_sha256": sha256(video.read_bytes()).hexdigest(),
        "subtitle_file": str(srt),
        "editorial_checks": ["Verify every caption against the spoken audio.", "Confirm each B-roll source is licensed and contextually accurate.", "Review claims, quotations, and call-to-action language before publishing.", "Record changes that affect factual meaning or sponsorship disclosure."],
        "inserts": [asdict(insert) for insert in inserts],
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
