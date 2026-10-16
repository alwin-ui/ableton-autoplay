"""
AutoPlay - a Live control surface script that automatically launches the next
scene in Session View when the current one finishes.

How a scene's end is found:
  * Unwarped audio clips (e.g. full-song backing tracks): the scene ends when
    the clip reaches its end marker. The next scene is launched immediately,
    ignoring global launch quantization, so songs follow without a gap.
  * MIDI / warped clips: the scene lasts as long as its longest clip and the
    next scene is launched on the bar line where it ends.

Tags (anywhere in the scene name, case-insensitive):

    [16]  or  [16 bars]   play this scene for exactly 16 bars, then advance
    [hold]                loop this scene forever (no auto-advance)
    [stop]                stop when this scene ends (no auto-advance)

On/off switch: a device named "AutoPlay" on the Main track. Its power button
turns auto-advance on and off. If there is no such device, AutoPlay is always
on, and (with ADD_SWITCH = True) an empty Audio Effect Rack named "AutoPlay"
is added to any set that has clips in it.
"""
from __future__ import absolute_import, division

import re

from _Framework.ControlSurface import ControlSurface

# ---- Settings ---------------------------------------------------------------
LOOP_SET = False          # after the last scene: True = jump to first scene, False = stop
SKIP_EMPTY_SCENES = True  # skip scenes that contain no clips
END_LEAD_SECONDS = 0.12   # unwarped clips: launch the next scene this long before the end
ADD_SWITCH = True         # add the on/off switch device to the Main track if missing
SWITCH_NAME = "AutoPlay"
# ----------------------------------------------------------------------------

BARS_RE = re.compile(r"\[\s*(\d+(?:\.\d+)?)\s*(?:bars?)?\s*\]", re.I)
HOLD_RE = re.compile(r"\[\s*hold\s*\]", re.I)
STOP_RE = re.compile(r"\[\s*stop\s*\]", re.I)

# Song.clip_trigger_quantization -> (amount, unit) ; unit "bar" or quarter-note "beat"
QUANTIZATION = {
    0: (0, "beat"),     # None
    1: (8, "bar"),
    2: (4, "bar"),
    3: (2, "bar"),
    4: (1, "bar"),
    5: (2.0, "beat"),   # 1/2
    6: (4 / 3.0, "beat"),
    7: (1.0, "beat"),   # 1/4
    8: (2 / 3.0, "beat"),
    9: (0.5, "beat"),   # 1/8
    10: (1 / 3.0, "beat"),
    11: (0.25, "beat"),  # 1/16
    12: (1 / 6.0, "beat"),
    13: (0.125, "beat"),  # 1/32
}


class AutoPlay(ControlSurface):

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self._tracks = []
        self._dirty = True
        self._restore_quantization = None
        self._enabled = None
        self._switch_added = False
        self._ticks = 0
        self._reset()
        self.song().add_tracks_listener(self._on_tracks_changed)
        self._on_tracks_changed()
        self.show_message("AutoPlay loaded")
        self.log_message("AutoPlay loaded")

    def disconnect(self):
        song = self.song()
        if song.tracks_has_listener(self._on_tracks_changed):
            song.remove_tracks_listener(self._on_tracks_changed)
        self._remove_track_listeners()
        ControlSurface.disconnect(self)

    # ---- listeners (no Live state may be changed in here) ------------------

    def _on_tracks_changed(self):
        self._remove_track_listeners()
        self._tracks = list(self.song().tracks)
        for track in self._tracks:
            if not track.playing_slot_index_has_listener(self._mark_dirty):
                track.add_playing_slot_index_listener(self._mark_dirty)
        self._dirty = True

    def _remove_track_listeners(self):
        for track in self._tracks:
            try:
                if track.playing_slot_index_has_listener(self._mark_dirty):
                    track.remove_playing_slot_index_listener(self._mark_dirty)
            except Exception:
                pass  # track was deleted
        self._tracks = []

    def _mark_dirty(self):
        self._dirty = True

    # ---- main loop (called by Live roughly every 100 ms) -------------------

    def update_display(self):
        ControlSurface.update_display(self)
        try:
            self._tick()
        except Exception as e:
            self.log_message("AutoPlay error: %r" % (e,))

    def _tick(self):
        song = self.song()
        if self._restore_quantization is not None:
            song.clip_trigger_quantization = self._restore_quantization
            self._restore_quantization = None

        enabled = self._check_switch()

        self._ticks += 1
        if not self._switch_added and self._ticks % 20 == 1 and self._set_has_clips():
            self._add_switch()

        if not song.is_playing:
            self._reset()
            return

        if self._dirty:
            self._dirty = False
            self._detect_scene()

        if self._scene_index is None or self._done or not enabled:
            return

        if self._ref_clip is not None:
            self._tick_clip_end()
        elif self._length > 0:
            self._tick_beats()

    def _tick_beats(self):
        remaining = self._start + self._length - self.song().current_song_time
        if remaining < 0:
            # The end went by while switched off; the scene looped, so aim for
            # the end of the current pass instead.
            passes = int(-remaining // self._length) + 1
            self._start += passes * self._length
            remaining += passes * self._length
        q = self._quantization_beats()
        # Fire inside the last quantization window so Live launches the next
        # scene exactly on the boundary where this one ends.
        window = 0.1 if q == 0 else min(q, self._length) * 0.5
        if remaining <= window:
            self._done = True
            self._advance(immediate=False)

    def _tick_clip_end(self):
        clip = self._ref_clip
        try:
            if not clip.is_playing:
                return  # handled in _detect_scene when the track stops
            # Unwarped clips report position and markers in seconds.
            remaining = clip.end_marker - clip.playing_position
        except Exception:
            self._ref_clip = None  # clip was deleted
            return
        self._last_remaining = remaining
        if remaining <= END_LEAD_SECONDS:
            self._done = True
            self._advance(immediate=True)

    # ---- helpers -----------------------------------------------------------

    def _reset(self):
        self._scene_index = None
        self._start = 0.0
        self._length = 0.0
        self._ref_clip = None
        self._last_remaining = None
        self._done = False

    def _detect_scene(self):
        """Work out which scene is playing from the tracks' playing slots."""
        counts = {}
        for track in self.song().tracks:
            idx = track.playing_slot_index
            if idx >= 0:
                counts[idx] = counts.get(idx, 0) + 1
        if not counts:
            # Everything stopped. If an unwarped clip just ran out on its own
            # (rather than the user pressing stop) and we missed the end, advance now.
            if (self._ref_clip is not None and not self._done and self._enabled
                    and self._last_remaining is not None
                    and self._last_remaining < 1.0):
                self._advance(immediate=True)
            self._reset()
            return
        idx = max(counts, key=lambda k: counts[k])
        if idx == self._scene_index:
            return

        song = self.song()
        scene = song.scenes[idx]
        self._reset()
        self._scene_index = idx
        # Launches land on the grid; snap to the nearest beat to cancel polling lag.
        self._start = float(round(song.current_song_time))
        m = BARS_RE.search(scene.name)
        if m:
            self._length = float(m.group(1)) * self._beats_per_bar()
        else:
            self._ref_clip = self._longest_unwarped_clip(idx)
            if self._ref_clip is None:
                self._length = self._longest_beat_clip(idx)
        self._done = bool(HOLD_RE.search(scene.name))

        if self._ref_clip is not None:
            c = self._ref_clip
            self.log_message("AutoPlay: scene %d '%s' started, unwarped clip '%s' "
                             "start %.3f end %.3f pos %.3f (seconds)"
                             % (idx + 1, scene.name, c.name, c.start_marker,
                                c.end_marker, c.playing_position))
        else:
            self.log_message("AutoPlay: scene %d '%s' started at %.2f, length %.2f beats"
                             % (idx + 1, scene.name, self._start, self._length))

    # ---- on/off switch -----------------------------------------------------

    def _find_switch(self):
        for device in self.song().master_track.devices:
            if device.name.strip().lower() == SWITCH_NAME.lower():
                return device
        return None

    def _check_switch(self):
        """Read the switch device's power button; no device means on."""
        device = self._find_switch()
        enabled = True
        if device is not None and len(device.parameters) > 0:
            enabled = device.parameters[0].value >= 0.5  # "Device On"
        if enabled != self._enabled:
            if self._enabled is not None:
                self.show_message("AutoPlay %s" % ("ON" if enabled else "OFF"))
            self.log_message("AutoPlay %s" % ("on" if enabled else "off"))
            self._enabled = enabled
        return enabled

    def _set_has_clips(self):
        for track in self.song().tracks:
            for slot in track.clip_slots:
                if slot.has_clip:
                    return True
        return False

    def _add_switch(self):
        if not ADD_SWITCH or self._switch_added or self._find_switch() is not None:
            return
        self._switch_added = True  # only try once per session
        master = self.song().master_track
        try:
            master.insert_device("Audio Effect Rack", len(master.devices))
            master.devices[-1].name = SWITCH_NAME
            self.show_message("AutoPlay: added on/off switch to the Main track")
            self.log_message("AutoPlay: added switch device")
        except Exception as e:
            self.log_message("AutoPlay: could not add switch device: %r" % (e,))

    def _beats_per_bar(self):
        song = self.song()
        return song.signature_numerator * 4.0 / song.signature_denominator

    def _quantization_beats(self):
        amount, unit = QUANTIZATION.get(self.song().clip_trigger_quantization, (1, "bar"))
        return amount * self._beats_per_bar() if unit == "bar" else amount

    def _scene_clips(self, idx):
        for track in self.song().tracks:
            slots = track.clip_slots
            if idx < len(slots) and slots[idx].has_clip:
                yield slots[idx].clip

    def _longest_unwarped_clip(self, idx):
        best, best_len = None, 0.0
        for clip in self._scene_clips(idx):
            if clip.is_audio_clip and not clip.warping and not clip.looping:
                length = clip.end_marker - clip.start_marker
                if length > best_len:
                    best, best_len = clip, length
        return best

    def _longest_beat_clip(self, idx):
        longest = 0.0
        for clip in self._scene_clips(idx):
            if clip.is_audio_clip and not clip.warping:
                continue  # not measured in beats
            longest = max(longest, clip.length)
        return longest

    def _scene_has_clips(self, idx):
        for _ in self._scene_clips(idx):
            return True
        return False

    def _advance(self, immediate):
        song = self.song()
        current = song.scenes[self._scene_index]
        if STOP_RE.search(current.name):
            if not immediate:
                song.stop_all_clips()
            self.show_message("AutoPlay: stopped after '%s'" % current.name)
            return

        n = len(song.scenes)
        idx = self._scene_index
        for _ in range(n):
            idx += 1
            if idx >= n:
                if not LOOP_SET:
                    if not immediate:
                        song.stop_all_clips()
                    self.show_message("AutoPlay: end of set")
                    return
                idx = 0
            if not SKIP_EMPTY_SCENES or self._scene_has_clips(idx):
                break
        else:
            return

        nxt = song.scenes[idx]
        if immediate:
            # Launch right now rather than waiting for the next bar line;
            # global quantization is put back on the next tick.
            self._restore_quantization = song.clip_trigger_quantization
            song.clip_trigger_quantization = 0
        nxt.fire()
        self.show_message("AutoPlay: next -> %s" % (nxt.name or "Scene %d" % (idx + 1)))
