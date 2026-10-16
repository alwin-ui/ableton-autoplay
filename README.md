# AutoPlay for Ableton Live

A Control Surface script for Ableton Live 11/12 that automatically launches the next scene in Session View when the current one finishes — handy for playing a setlist of backing tracks hands-free.

## How it works

- **Unwarped audio clips** (e.g. full-song mp3 backing tracks): when the clip reaches its end marker, the next scene launches immediately (global launch quantization is bypassed), so songs follow without a gap. Keep **Loop** off on these clips.
- **MIDI / warped clips**: the scene lasts as long as its longest clip, and the next scene launches on the bar line where it ends. Use a global launch quantization of 1 Bar or 1/4.
- Empty scenes are skipped. After the last scene, playback stops.

### Scene-name tags

| Tag | Effect |
|---|---|
| `[16]` or `[16 bars]` | Play this scene for exactly 16 bars, then advance |
| `[hold]` | Loop this scene; no auto-advance |
| `[stop]` | Stop when this scene ends (e.g. pause between songs) |

## Install

1. Copy the `AutoPlay` folder into `Remote Scripts` inside your Live **User Library** (default: `~/Music/Ableton/User Library/Remote Scripts/` — check *Settings → Library* if you moved it).
2. Restart Live.
3. *Settings → Link, Tempo & MIDI*: pick **AutoPlay** in an empty Control Surface slot, Input/Output = None.
4. Launch a scene.

## Settings

At the top of `AutoPlay.py`:

- `LOOP_SET` — `True` jumps back to the first scene after the last one.
- `SKIP_EMPTY_SCENES` — skip scenes with no clips.
- `END_LEAD_SECONDS` — how early (in seconds) to launch the next scene before an unwarped clip ends.

Messages are written to Live's `Log.txt`, prefixed with `AutoPlay`.
