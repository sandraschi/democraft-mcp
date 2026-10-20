# SoundCraft demos

[All apps](README.md) | [Repo README](../../README.md)

**What it is**: session audio - MIDI, mixing, effects, recording and export. The app's own
comparison is Ableton Live / Pro Tools. Driven by
`C:\Program Files\SoundCraft\soundcraft-cli.exe`.

This is the app where "hands-in" is literal: the artifacts are audio you can play.

## Demos

| Demo | What actually runs | Artifacts | AI step |
|---|---|---|---|
| `melody-vst3` | Imports a 16-note MIDI melody, bounces it dry on the built-in synth, inserts Valhalla Supermassive (VST3) and bounces it wet. Renders waveform and piano-roll frames. | `melody.mid`, `melody_dry.wav`, `melody_surge.wav`, waveform PNG, piano-roll PNG | none - no AI writes the notes |
| `ident-jingle` | Renders the bundled "Midnight Groove" demo project to WAV (~56 s). | WAV | the model writes only the words describing the bounce |
| `capability-map` | The installed CLI's `commands` output (or `--help`). | `capabilities.txt` | none |

`melody-vst3` is flagged **live**: you hear the same notes before and after the plugin, and the
waveform frames show the tail the reverb adds.

## Hands-in / Hands-out

| Direction | What |
|---|---|
| Hands-in | a MIDI melody written by the demo (not generated); for the jingle, the bundled project |
| Hands-out | `.mid`, `.wav` (dry and wet), waveform and piano-roll PNGs |

Play `melody_dry.wav` and `melody_surge.wav` back to back. That comparison is the demo; a
screenshot of a mixer would prove nothing.

## Run it

```
/craft/sound
/craft/sound?demo=melody-vst3&watch=1
craft(operation="run_demo", app="sound", demo="melody-vst3")
```

Artifacts: `outbox/sound/melody-vst3/`.

## Observed gaps

- **VST3 instruments are silent** on this build (tracked as BUG-082 upstream); VST3 *effects*
  work, which is why the reverb demo is the one that ships.
- No cloud collaboration.
- The free plugin set the demos use is listed in [../FREE_VST3_SET.md](../FREE_VST3_SET.md).
