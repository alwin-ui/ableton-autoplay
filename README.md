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
| `[hold]` | Repeat this scene until you launch another one (handy for stretching an intro) |
| `[stop]` | Stop when this scene ends (e.g. pause between songs) |

### On/off switch

When you open a set with clips in it, AutoPlay drops an empty Audio Effect Rack called **AutoPlay** on the Main track. Click the Main track to see it. Its power button turns AutoPlay on and off, and the status bar shows "AutoPlay ON" / "AutoPlay OFF". Turning it off lets the current song keep playing without moving on.

The rack is empty, so it doesn't touch your sound. You can also use any device you like as the switch, just put it on Main and rename it "AutoPlay" (Cmd+R / Ctrl+R). Adding devices from a script needs Live 12.3 or newer; on older versions, add the switch yourself. No switch at all means AutoPlay is always on.

#### Map it to a button on your controller

The switch's power button is a normal Live control, so you can map it like anything else:

1. Click the Main track so the AutoPlay rack shows in the device view.
2. Press **Cmd+M** (Ctrl+M on Windows) to enter MIDI Map mode.
3. Click the rack's power button, then press a pad or button on your controller.
4. Press **Cmd+M** again to leave MIDI Map mode.

Each press now toggles AutoPlay. For a computer key instead, do the same with **Cmd+K** / **Ctrl+K**. If nothing happens, check that **Remote** is ticked for your controller's input in *Settings → Link, Tempo & MIDI*.

Mappings are saved with the set. To have the mapped switch in every new set, set it up once in an empty set and save it as your default (*Settings → File & Folder → Save Current Set as Default*).

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
- `ADD_SWITCH`: set to `False` if you don't want the on/off rack added to your sets.

If something's off, check Live's `Log.txt` for lines starting with `AutoPlay`.

Issues and PRs welcome.
