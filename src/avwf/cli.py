"""Command-line interface for batch subtitle and B-roll preparation."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

from .editor import build_inserts, load_catalog, parse_srt, render_broll, render_subtitles, run_whisper, write_manifest


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="avwf", description="Local-first batch workflow for talking-head subtitles and B-roll review.")
    sub = root.add_subparsers(dest="command", required=True)
    batch = sub.add_parser("batch", help="Transcribe videos, burn subtitles, and create B-roll review manifests.")
    batch.add_argument("videos", type=Path, help="A video file or directory containing .mp4 files.")
    batch.add_argument("--catalog", type=Path, required=True, help="CSV: path,tags,rights_note,source_url")
    batch.add_argument("--output", type=Path, default=Path("dist"))
    batch.add_argument("--model", default="base", help="Whisper model when --srt-dir is not supplied.")
    batch.add_argument("--srt-dir", type=Path, help="Reuse existing SRTs instead of invoking Whisper.")
    batch.add_argument("--render-subtitles", action="store_true", help="Write MP4 files with burned-in subtitles.")
    batch.add_argument("--render-broll", action="store_true", help="Write a full-frame B-roll rough cut from matched approved assets.")
    return root


def videos(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    found = sorted(path.glob("*.mp4"))
    if not found:
        raise ValueError(f"No .mp4 files found in {path}")
    return found


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        catalog = load_catalog(args.catalog)
        for video in videos(args.videos):
            project_dir = args.output / video.stem
            srt = args.srt_dir / f"{video.stem}.srt" if args.srt_dir else run_whisper(video, project_dir, args.model)
            inserts = build_inserts(parse_srt(srt), catalog)
            write_manifest(video, srt, inserts, project_dir / "broll-review.json")
            review_copy = video
            if args.render_subtitles:
                review_copy = project_dir / f"{video.stem}.subtitled.mp4"
                render_subtitles(video, srt, review_copy)
            if args.render_broll:
                render_broll(review_copy, inserts, project_dir / f"{video.stem}.rough-cut.mp4")
            print(f"Prepared {video.name}: {project_dir}")
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
