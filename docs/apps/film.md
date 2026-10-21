# FilmCraft demos

[All apps](README.md) | [Repo README](../../README.md)

**What it is**: timeline editing - sequences, transitions, keyframes, audio, colour, subtitles
and proxy workflows. The app's own comparison is Adobe Premiere Pro. Driven by
`C:\Program Files\FilmCraft\filmcraft-cli.exe` (verified against 0.10.0).

## Demos

| Demo | What actually runs | Artifacts | AI step |
|---|---|---|---|
| `timeline-cut` | Imports two demo clips (`OceanSunset`, `Aurora`), builds a 24 fps 1280x720 sequence, applies a 12-frame cross dissolve as its own saved `exec` step, exports H.264 and renders two frames (poster at 1 s, the dissolve at 18 s). | `build.jsonl`, `finish.jsonl`, `cut.fcproj`, `cut.mp4`, `poster.png`, `transition.png` | none - deterministic |
| `storyboard` | Exports a real EDL; the local model boards three shots for the chosen subject. | `storyboard.edl`, `brief.md` | three-shot board (shot, lens, action) |
| `interchange-kit` | Builds the two-clip cut, then hands it off: EDL, FCP7 XML and FCPXML, each with the exporter's own report of what could not be represented. | `build.jsonl`, `cut.fcproj`, `cut.edl`, `cut.xml`, `cut.fcpxml` | none - deterministic |
| `captions-roundtrip` | Writes a two-cue SRT, imports it onto the built-in demo sequence in one process, exports SRT again and lists the resulting track (style, timing, speaker). | `subs.srt`, `subs-out.srt`, `captions.jsonl` | none - deterministic |
| `poster-strip` | Builds the cut and renders three stills at 0 s, 3 s and 6 s at half scale. | `build.jsonl`, `cut.fcproj`, `poster-0s.png`, `poster-3s.png`, `poster-6s.png` | none - deterministic |
| `capability-map` | The installed CLI's `commands` output. | `capabilities.txt` | none |

`timeline-cut` and `interchange-kit` are flagged **live**: every CLI step streams with its
return code.

## What the handoff actually costs

Verified on 0.10.0 (and 0.9.0 baseline), from the exporters' own reports rather than from documentation:

- **EDL**: one video track only, so other video tracks are dropped; synthetic demo media is
  written as reel `AX`; a `Lumetri Color` effect cannot be represented at all. Transitions
  survive as a dissolve plus an `EFFECT NAME` comment.
- **FCP7 XML**: generators are written with FilmCraft effect ids, and Lumetri curve
  parameters are unsupported. This is the richest of the three (51 KB for the demo cut
  versus 2.3 KB EDL).
- **FCPXML**: generators become gaps and transitions are kept on V1 only. Smallest and
  most lossy of the three.
- **SRT round-trip**: text, order and cue count survive; times quantise to the sequence
  timebase (1,000 ms in became 1,001 ms out at 24 fps).

A handoff demo that claimed lossless interchange would be lying. These reports are the
artifact.

`timeline-cut` is flagged **live**: five CLI steps, each streamed with its return code.

## Hands-in / Hands-out

| Direction | What |
|---|---|
| Hands-in | demo footage shipped with FilmCraft; for the storyboard, a subject |
| Hands-out | `.fcproj` project, H.264 MP4, PNG stills, SRT, EDL, FCP7 XML, FCPXML |

The dissolve is applied with `--save`, so it lives in `cut.fcproj` and in both rendered frames.
A dissolve that only exists inside the export process is invisible to the next render - the
regression test `test_film_timeline_cut_persists_transition` exists because that bug was real.

## Run it

```
/craft/film
/craft/film?demo=timeline-cut&watch=1
craft(operation="run_demo", app="film", demo="timeline-cut")
```

Artifacts: `outbox/film/timeline-cut/`.

## Observed gaps

- No hardware-accelerated proxy pipeline verified.
- No third-party plugin ecosystem.
- `storyboard` still stops at the EDL and the AI board; assembling its shots into a sequence
  is project-gated. The `video-delivery` flow is marked ready because it does not depend on
  that assembly.
- Interchange is lossy by design (see above). The export reports are the honest record.
