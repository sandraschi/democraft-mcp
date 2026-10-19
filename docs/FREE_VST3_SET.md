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

- SoundCraft scans the per-user folder automatically: `engine.vst3_plugins`
  lists all seven.
- Surge XT loaded on an instrument track and rendered two seconds of audio
  (`peak -17.7 dB`), so the scan is not just a file listing.
- Reaper: `vstpath` and `vstpath64` in `%APPDATA%\REAPER\reaper.ini` now
  include the per-user folder. Restart Reaper, then
  Options > Preferences > Plug-ins > VST > **Re-scan**.

## Other DAWs

Add `%LOCALAPPDATA%\Programs\Common\VST3` to the plugin search path. VST3 hosts
that only scan `C:\Program Files\Common Files\VST3` will not see these without
that path, and the machine-wide folder is not writable without elevation.

## Worth adding later (all need an installer or a big download)

| Plugin | Why | Catch |
|---|---|---|
| Cardinal | modular playground, the "crazy" one | portable zip is ~1.1 GB |
| Valhalla Supermassive | best free halls/delay, tiny CPU | installer (admin) |
| Vital | spectral-warp synth, free tier | installer/account |
| ChowKick / BYOD | kick synth / build-your-own distortion | installers |
| SFizz | SFZ sampler | the win64 release ships no VST3 (checked 1.2.3) |

## Remove

Delete the `.vst3` bundles from the folder and re-scan in the DAW. Nothing was
written to the registry or to Program Files.
