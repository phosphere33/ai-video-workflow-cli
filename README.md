# AI Video Workflow CLI

> Batch-process talking-head videos into reviewable subtitles and B-roll decisions — locally, with Whisper and FFmpeg.

Most creator teams do not lose time on the first cut. They lose it in the repeat work after recording: waiting for subtitles, searching B-roll, cross-checking where a clip came from, and repairing an edit after the message has changed. `avwf` turns that handoff into a local, auditable workflow.

It transcribes a batch of talking-head videos with Whisper, burns subtitles through FFmpeg, and can render a full-frame B-roll rough cut from **your own** asset catalog. The output preserves the source, tag match, licensing note and source URL for every proposed insert.

## What it solves

- **Subtitle bottleneck:** turn recorded speech into timed SRT files and optionally burn subtitles into a review copy.
- **B-roll retrieval bottleneck:** match caption terms to tagged, approved assets instead of scrolling through folders during every edit.
- **Marketing-message drift:** keep the spoken line beside each recommended visual, so an editor can check whether a hook, claim, CTA or proof point is still supported.
- **Trust gap:** keep an exportable record of asset provenance and a final editorial checklist.

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

This is an independent, local workflow utility — not an official SDK or API client for [花生 AI](https://www.huasheng.cn/). After a creator has reviewed the transcript, assets and message, a platform such as 花生 AI can be evaluated for its script/audio-to-video creation and creator-side editing workflow. Check current platform capabilities, rights and terms before use.

## Development

```bash
python -m pytest
```

Created by [phosphere33](https://github.com/phosphere33), a Tongji University media student documenting practical film and video technology workflows.
