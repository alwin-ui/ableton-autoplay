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

1. Download **[AutoPlay.zip](https://github.com/alwin-ui/ableton-autoplay/releases/latest/download/AutoPlay.zip)** and unzip it.
2. Run the installer:
   - **Mac:** right-click **Install AutoPlay (Mac).command** → **Open** → **Open**. (Right-click is needed the first time because the file is not from the App Store.)
   - **Windows:** double-click **Install AutoPlay (Windows).bat**. If SmartScreen appears, click *More info → Run anyway*.

   The installer finds your Live User Library automatically, even if you moved it.
3. Restart Ableton Live.
4. *Settings → Link, Tempo & MIDI*: pick **AutoPlay** in an empty Control Surface slot (Input/Output = None).
5. Launch a scene — that's it.

Mac one-liner (Terminal):

```
curl -fsSL https://raw.githubusercontent.com/alwin-ui/ableton-autoplay/main/installer/install-mac.sh | bash
```

To update, run the installer again. To uninstall, set the Control Surface slot back to None and delete the `Remote Scripts/AutoPlay` folder in your User Library.

<details><summary>Manual install</summary>

Copy `__init__.py` and `AutoPlay.py` into a folder named exactly `AutoPlay` inside `Remote Scripts` in your Live User Library (default: `~/Music/Ableton/User Library/` on Mac, `Documents\Ableton\User Library\` on Windows; see *Settings → Library*). The folder name must not contain hyphens.
</details>

## Settings

At the top of `AutoPlay.py`:

- `LOOP_SET` — `True` jumps back to the first scene after the last one.
- `SKIP_EMPTY_SCENES` — skip scenes with no clips.
- `END_LEAD_SECONDS` — how early (in seconds) to launch the next scene before an unwarped clip ends.

Messages are written to Live's `Log.txt`, prefixed with `AutoPlay`.
