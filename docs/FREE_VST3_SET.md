# Free VST3 set (2026-10-20)

Installed for the whole machine, no admin required, into the per-user VST3
folder:

```
%LOCALAPPDATA%\Programs\Common\VST3
C:\Users\sandr\AppData\Local\Programs\Common\VST3
```

## What is installed

| Plugin | Type | Version | Source | Notes |
|---|---|---|---|---|
| Surge XT | Instrument | 1.4.0 (nightly 2026-10-17) | github.com/surge-synthesizer/surge | hybrid synth, huge mod matrix, built-in filters/FX |
| Surge XT Effects | Effect | 1.4.0 (same build) | same | filters, delays, distortion, chorus as an effect rack |
| Dexed | Instrument | 1.0.1 | github.com/asb2m10/dexed | DX7-style FM, loads Sysex patches |
| Dragonfly Hall Reverb | Effect | 3.2.10 | github.com/michaelwillis/dragonfly-reverb | long halls |
| Dragonfly Room Reverb | Effect | 3.2.10 | same | small/medium rooms |
| Dragonfly Plate Reverb | Effect | 3.2.10 | same | plates |
| Dragonfly Early Reflections | Effect | 3.2.10 | same | ER-only, pairs with the others |
| Valhalla Supermassive | Effect | 5.0.0 | valhalladsp.com (free) | 22 reverb/echo modes, the "massive space" one; installed to Program Files\Common Files\VST3 |
| Cardinal | Instrument + FX | 26.02 | github.com/DISTRHO/Cardinal (winget) | VCV-Rack-based modular playground, ~1.1 GB; three VST3s: Cardinal, Cardinal Synth, Cardinal FX |

All four Dragonfly plugins are separate VST3s, so they can sit on different
sends. All are open source; check each upstream repo for the exact licence
before redistributing.

## Why this set

- **One broad synth** (Surge XT) covers subtractive, wavetable, FM-ish and
  vector-ish sounds, and its effects rack covers filters, distortion and delay
  without another install.
- **One FM synth** (Dexed) because FM is a different way of thinking, and DX7
  patches are everywhere.
- **Four reverb characters** instead of one: hall, room, plate, early
  reflections. Cheap on CPU, no iLok, no account.

## Verified

- SoundCraft scans both the per-user folder and `C:\Program Files\Common
  Files\VST3`: `engine.vst3_plugins` lists 11 plugins.
- **VST3 effects process.** Valhalla Supermassive inserted on a melody track
  changes the bounce (dry vs wet), and the effect chain is audible.
- **VST3 instruments are unresolved in SoundCraft (host bug).** Surge XT and
  Dexed, set as track instruments, render silence in SoundCraft's headless
  bounce **and in the live app over its control channel**; the built-in
  subtractive synth on the same clip is audible. The same MIDI file and VST3s
  render correctly in Reaper 7.80 (Surge 3.45M, Dexed 1.13M peak samples), so
  the plugins are fine and the fault is SoundCraft's instrument path. Tracked as
  **BUG-082** (`mcp-central-docs/troubleshooting/details/`). Suite VST3 effects
  process correctly in both hosts.
- Reaper: `vstpath` and `vstpath64` in `%APPDATA%\REAPER\reaper.ini` now
  include the per-user folder. Restart Reaper, then
  Options > Preferences > Plug-ins > VST > **Re-scan**.

## Other DAWs

Add `%LOCALAPPDATA%\Programs\Common\VST3` to the plugin search path. VST3 hosts
that only scan `C:\Program Files\Common Files\VST3` will still see Valhalla and
Cardinal (machine-wide), but not Surge/Dexed/Dragonfly.

## Worth adding later (all need an installer or a big download)

| Plugin | Why | Catch |
|---|---|---|
| Vital | spectral-warp synth, free tier | installer/account |
| ChowKick / BYOD | kick synth / build-your-own distortion | installers |
| SFizz | SFZ sampler | the win64 release ships no VST3 (checked 1.2.3) |

## Notes

- Cardinal writes scan/initialisation logs to stdout, so tooling that expects
  pure JSON from SoundCraft should filter lines by prefix (`engine.vst3_plugins:`).
- Surge XT here is a nightly build (1.4.0). The stable installer needs
  elevation and replaces it in Program Files.

## Remove

Delete the `.vst3` bundles from the folder and re-scan in the DAW. Nothing was
written to the registry or to Program Files.
