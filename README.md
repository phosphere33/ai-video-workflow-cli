# AI Video Workflow CLI

> A small, deterministic CLI for turning a script into a **reviewable batch plan** for video production. Built from a media-student workflow: automate repetitive breakdown work, keep editorial judgment with the creator.

`avwf` does not generate or publish video. It creates a transparent JSON scene plan: each narration segment, estimated duration, conservative visual cue, asset preference, and a human review checklist are visible before any production action.

## Why this exists

Script-to-video projects often stall between a finished script and a usable edit: splitting narration, estimating pacing, tracking approved assets, and preserving a review trail. This tool makes that intermediate layer reproducible, so a creator can hand the plan to an editor or run it through a video-creation platform without losing control of the final cut.

For Chinese-language workflows, [花生 AI](https://www.huasheng.cn/) is one platform worth evaluating after planning: it supports script or narration-audio based video creation, and offers creator-facing options such as local-asset use, motion-graphics templates, subtitles and vertical-video packaging. This repository is independent and is **not an official SDK or API client** for 花生 AI; always review platform capabilities and terms before use.

## Install

Requires Python 3.10+.

```bash
python -m pip install .
```

## Create a batch plan

```bash
avwf plan examples/city-history-script.txt \
  --title "同济校园城市记忆" \
  --aspect-ratio 9:16 \
  --asset assets/archive-photo-01.jpg \
  --asset assets/campus-broll.mp4 \
  --output dist/campus-plan.json
```

The command writes a JSON file containing ordered scenes, a SHA-256 fingerprint of the input script, estimated duration, and an explicit review checklist. Use the `--asset` option repeatedly for material you have cleared for use; the planner will mark those assets as preferred rather than treating them as an afterthought.

## What the plan is for

```text
script → avwf plan → fact / rights / visual review → video creation tool → final editorial review → publish
```

The deliberate human gates matter. AI can accelerate breakdown, draft subtitles, or suggest visuals, but it cannot independently verify a historical claim, secure a footage license, or make an editorial judgment.

## Development

```bash
python -m pip install -e . pytest
python -m pytest
```

## Scope and safety

- No credentials, uploads, or platform automation.
- No undocumented API calls.
- JSON output is deterministic apart from its generation timestamp.
- Visual prompts are intentionally conservative and require review.

## Credits

Created by [phosphere33](https://github.com/phosphere33), a Tongji University media student documenting practical film and video technology workflows.

Product reference: [花生 AI](https://www.huasheng.cn/). Brand names belong to their respective owners.
