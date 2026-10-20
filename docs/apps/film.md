# FilmCraft demos

[All apps](README.md) | [Repo README](../../README.md)

**What it is**: timeline editing - sequences, transitions, keyframes, audio, colour, subtitles
and proxy workflows. The app's own comparison is Adobe Premiere Pro. Driven by
`C:\Program Files\FilmCraft\filmcraft-cli.exe` (verified against 0.9.0).

## Demos

| Demo | What actually runs | Artifacts | AI step |
|---|---|---|---|
| `timeline-cut` | Imports two demo clips (`OceanSunset`, `Aurora`), builds a 24 fps 1280x720 sequence, applies a 12-frame cross dissolve as its own saved `exec` step, exports H.264 and renders two frames (poster at 1 s, the dissolve at 18 s). | `build.jsonl`, `finish.jsonl`, `cut.fcproj`, `cut.mp4`, `poster.png`, `transition.png` | none - deterministic |
| `storyboard` | Exports a real EDL; the local model boards three shots for the chosen subject. | `storyboard.edl`, `brief.md` | three-shot board (shot, lens, action) |
| `capability-map` | The installed CLI's `commands` output. | `capabilities.txt` | none |

`timeline-cut` is flagged **live**: five CLI steps, each streamed with its return code.

## Hands-in / Hands-out

| Direction | What |
|---|---|
| Hands-in | demo footage shipped with FilmCraft; for the storyboard, a subject |
| Hands-out | `.fcproj` project, H.264 MP4, PNG stills, EDL |

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
- `storyboard` stops at the EDL and the AI board; assembling shots into a sequence is
  project-gated, which is why the film flows are marked exploratory.
