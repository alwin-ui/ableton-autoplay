# AutoPlay for Ableton Live

I play live with backing tracks in Session View and got tired of launching every song by hand, so I wrote this. It's a small Control Surface script for Ableton Live 11/12 that launches the next scene as soon as the current one finishes.

## What it does

- **Unwarped audio clips** (e.g. full-song mp3 backing tracks): when the clip reaches its end marker, the next scene launches immediately (global launch quantization is bypassed), so songs run back to back with no gap. Just keep **Loop** off on those clips.
- **MIDI / warped clips**: the scene lasts as long as its longest clip, and the next scene launches on the bar line where it ends. Works best with global launch quantization at 1 Bar or 1/4.
- Empty scenes get skipped, and it stops after the last scene.

### Scene name tags

You can put these anywhere in a scene's name:

| Tag | Effect |
|---|---|
| `[16]` or `[16 bars]` | Play this scene for exactly 16 bars, then advance |
| `[hold]` | Loop this scene; no auto-advance |
| `[stop]` | Stop when this scene ends (e.g. pause between songs) |

## Install

1. Download **[AutoPlay.zip](https://github.com/alwin-ui/ableton-autoplay/releases/latest/download/AutoPlay.zip)** and unzip it.
2. Run the installer:
   - **Mac:** right-click **Install AutoPlay (Mac).command** → **Open** → **Open**. (macOS only lets you open it with right-click the first time.)
   - **Windows:** double-click **Install AutoPlay (Windows).bat**. If SmartScreen appears, click *More info → Run anyway*.

   It finds your User Library on its own, even if you moved it somewhere else.
3. Restart Ableton Live.
4. *Settings → Link, Tempo & MIDI*: pick **AutoPlay** in an empty Control Surface slot (Input/Output = None).
5. Launch a scene and let it go.

Or on a Mac, from Terminal:

```
curl -fsSL https://raw.githubusercontent.com/alwin-ui/ableton-autoplay/main/installer/install-mac.sh | bash
```

To update, run the installer again. To uninstall, set the Control Surface slot back to None and delete the `Remote Scripts/AutoPlay` folder in your User Library.

<details><summary>Manual install</summary>

Copy `__init__.py` and `AutoPlay.py` into a folder named exactly `AutoPlay` inside `Remote Scripts` in your Live User Library (default: `~/Music/Ableton/User Library/` on Mac, `Documents\Ableton\User Library\` on Windows; see *Settings → Library*). Don't use hyphens in the folder name or Live won't load it.
</details>

## Settings

At the top of `AutoPlay.py`:

- `LOOP_SET`: set to `True` to jump back to the first scene after the last one.
- `SKIP_EMPTY_SCENES`: skip scenes with no clips.
- `END_LEAD_SECONDS`: how early (in seconds) to launch the next scene before an unwarped clip ends.

If something's off, check Live's `Log.txt` for lines starting with `AutoPlay`.

Issues and PRs welcome.
