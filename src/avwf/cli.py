"""Command-line interface for AVWF."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .planner import build_plan, write_plan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="avwf",
        description="Build reviewable batch plans for script-to-video production.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan", help="Create a JSON scene plan from a UTF-8 script.")
    plan.add_argument("script", type=Path, help="Path to a UTF-8 text script.")
    plan.add_argument("--title", required=True, help="Project title for the plan.")
    plan.add_argument("--output", type=Path, default=Path("dist/video-plan.json"))
    plan.add_argument("--aspect-ratio", default="9:16", choices=("16:9", "9:16", "1:1"))
    plan.add_argument("--max-chars", type=int, default=72, help="Maximum narration characters per scene.")
    plan.add_argument("--chars-per-second", type=float, default=4.2)
    plan.add_argument("--asset", action="append", default=[], help="Approved local asset path (repeatable).")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "plan":
        try:
            plan = build_plan(
                args.script,
                title=args.title,
                aspect_ratio=args.aspect_ratio,
                max_chars=args.max_chars,
                chars_per_second=args.chars_per_second,
                local_assets=args.asset,
            )
            write_plan(plan, args.output)
        except (OSError, ValueError) as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
        print(f"Wrote {len(plan['scenes'])} scenes to {args.output}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
