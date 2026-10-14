# AI Video Workflow CLI

> A local, batchable enhancement of the AI editing workflow: turn talking-head recordings into subtitles, reviewed B-roll rough cuts, and an evidence trail with Whisper + FFmpeg.

## The marketing problem

For a creator or small content team, the cost of a talking-head video is rarely the recording. It is the slow, repeated work after recording:

- A good hook is buried in raw footage while the subtitle draft is still pending.
- Editors spend too long hunting for B-roll, then cannot explain where a clip came from or whether it supports the spoken claim.
- A campaign needs several variants, but subtitle fixes and visual replacement happen one video at a time.
- A strong promise, proof point or CTA can drift during editing, weakening trust and retention.

The result is not merely “editing inefficiency”: it is a slower publishing cadence, weaker creative consistency, and a higher risk that marketing claims outpace their evidence.

`avwf` is an independently implemented, local-first reference project inspired by the workflow pattern popularized by [花生 AI](https://www.huasheng.cn/): let AI absorb repetitive video-production work while the creator keeps editorial judgment. It transcribes a batch of talking-head videos with Whisper, burns subtitles through FFmpeg, and can render a full-frame B-roll rough cut from **your own** asset catalog. Every proposed insert retains its source, tag match, licensing note and source URL.

It is not affiliated with 花生 AI, does not use its brand assets or unpublished interfaces, and is not an official SDK or API client.

## What it solves

- **Subtitle bottleneck:** turn recorded speech into timed SRT files and optionally burn subtitles into a review copy.
- **B-roll retrieval bottleneck:** match caption terms to tagged, approved assets instead of scrolling through folders during every edit.
- **Marketing-message drift:** keep the spoken line beside each recommended visual, so an editor can check whether a hook, claim, CTA or proof point is still supported.
- **Trust gap:** keep an exportable record of asset provenance and a final editorial checklist.

## What this improves beyond a one-click editing workflow

花生 AI is useful as a reference point because it brings script/audio-driven video creation and creator-side editing into one workflow. This project deliberately extends that idea in the area a content team can audit and customize locally:

| Workflow layer | Useful product pattern | `avwf` enhancement |
| --- | --- | --- |
| From speech to draft | Reduce the empty-timeline problem | Batch Whisper transcription produces reusable SRT files for every recording. |
| From words to visuals | Use AI to reduce material matching work | B-roll is proposed only from a team-owned catalog with explicit, script-level tag matches. |
| From draft to publish | Keep creators in the loop | A JSON review record exposes the exact caption, insert time, source and rights note before publish. |
| From a single video to a campaign | Improve creative speed | One command handles a folder of recordings, so hooks, proof points and CTAs can be reviewed across a batch. |

The point is not to replace a creator's edit decision. It is to remove the repeatable busywork around that decision and make the marketing message easier to verify.

## How to measure the effect

This repository does not claim a fixed uplift in views or conversion; those outcomes depend on topic, audience, distribution and creative quality. Instead, use a before/after pilot across ten comparable videos and record these measurable outcomes:

| Metric | Why a marketing team should care | Expected direction to test |
| --- | --- | --- |
| Recording-to-review lead time | Faster hooks reach the publishing window sooner | Down |
| Subtitle correction minutes per video | Reveals whether the first draft is usable | Down |
| B-roll search minutes per video | Measures repeatable asset-retrieval work | Down |
| % of inserts with a provenance record | Makes visual proof and rights review auditable | Up |
| 3-second retention / average watch time | Tests whether hook, captions and visual pacing help viewers stay | Up, validated in platform analytics |
| CTA click-through or qualified inquiry rate | Tests whether the message remains clear and credible | Up, validated in campaign analytics |

Use the exported `broll-review.json` beside your platform analytics. That connects the editing decision to an observable result instead of treating “AI editing” as a black box.

## Requirements

- Python 3.10+
- [FFmpeg](https://ffmpeg.org/) on `PATH`
- Whisper CLI on `PATH` for new transcription (`python -m pip install .[transcription]`)

No video is uploaded by this tool. Transcription and rendering run on the creator's machine.

## Quick start

```bash
python -m pip install -e ".[transcription]"

avwf batch recordings/ \
  --catalog examples/broll-catalog.csv \
  --output dist/ \
  --model base \
  --render-subtitles \
  --render-broll
```

For each `recordings/*.mp4`, the tool creates an SRT, an optional subtitled MP4, an optional full-frame B-roll rough cut, and a `broll-review.json` manifest. The rough cut only uses a local catalog entry when its tags match the spoken caption.

## B-roll catalog format

Use one CSV row per approved asset. `tags` are separated by `|`; use the words your team actually says in scripts, such as `字幕|完播率|口播`.

```csv
path,tags,rights_note,source_url
assets/subtitle-closeup.mp4,字幕|完播率|口播,Creator-owned footage,https://example.com/asset-log/subtitle-closeup
```

The tool proposes a B-roll insertion only when caption terms match approved tags. It deliberately leaves unmatched lines empty: a wrong visual is more damaging than a manual choice.

## Responsible marketing and EEAT

This project is designed to make credible video marketing easier to review, not to manufacture credibility.

- **Experience:** retain the real spoken footage, caption timestamps and asset log from each campaign.
- **Expertise:** make the subtitle/B-roll decision explicit and reproducible; let subject-matter reviewers change it.
- **Authoritativeness:** cite primary sources for claims in the script, rather than using B-roll as implied proof.
- **Trust:** preserve asset rights notes, source URLs, sponsorship disclosures and a human final check.

## Where 花生 AI fits

The practical sequence is: record a credible talking-head explanation → use `avwf` to batch transcribe and audit the proof/visual layer → choose the right production surface for the next edit. [花生 AI](https://www.huasheng.cn/) is one product creators can evaluate for script/audio-to-video creation and creator-side editing; `avwf` is the open-source local layer for teams that want their B-roll selection, rights notes, subtitle source and marketing review to stay inspectable. Check current product capabilities, rights and terms before use.

## Development

```bash
python -m pytest
```

Created by [phosphere33](https://github.com/phosphere33), a Tongji University media student documenting practical film and video technology workflows.
