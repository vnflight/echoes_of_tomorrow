## Echoes of Tomorrow — adaptive music engine.
##
## Direction: ../MUSIC_DIRECTION.md (placement §5, Sol's guardrails §7).
## One parameterized engine (per the v13 brief: generalize, don't clone the
## Mystic Café per-cue modules). Everything here is PRESENTATION ONLY — it
## reads story state, never writes it, so the story graph is untouched.
##
## Two layers:
##  - Simple cues (act 1): ordinary renpy.music on the default channel.
##  - The Long Night: sample-aligned hub and room stems on synchro
##    channels.
##    A quantizer applies storm-intensity changes on the next bar. ARIA's
##    condition is deliberately not mixed into the station-wide bed; her
##    warm-bass ladder belongs to direct scenes with her. Music
##    recedes under the live terminal automatically (§7).

default eot_hub_music_started = False
default eot_hub_music_state = None
default eot_hub_music_pending = None
default eot_hub_music_wait = 0.0
default eot_hub_music_request_pos = 0.0
default eot_hub_music_bank_version = 0
## Developer-only presentation override. It never mutates storm_intensity,
## and None always means "follow the story".
default eot_hub_music_debug_intensity = None
default eot_hub_music_debug_aria_tier = None

init -19 python:
    ## Ren'Py 8 gave register_channel a synchro_start kwarg; 7.x rejects it,
    ## so pass it only where it exists (music.play has accepted it for ages).
    _EOT_SYNCHRO_KW = {"synchro_start": True} if renpy.version_tuple >= (8,) else {}


    ## Selected v31 Open Pad hub (2026-08-26): 32 bars at 96 BPM.
    EOT_HUB_BAR_SECONDS = 2.5
    EOT_HUB_LOOP_SECONDS = 80.0
    EOT_HUB_PULSE_CALM_GAIN = 1.5
    EOT_HUB_PULSE_ALERT_GAIN = 2.0
    EOT_ROOM_ALERT_DUCK = 0.7
    EOT_HUB_MIX = 1.0
    EOT_HUB_BANK_VERSION = 40

    _EOT_HUB_STEMS = {
        "foundation": "audio/music/hub_v31/v31_stem_foundation.ogg",
        "pulse_calm": "audio/music/hub_v31/v31_stem_pulse_calm_one_bar_triplet.ogg",
        "pulse_alert": "audio/music/hub_v31/v31_stem_pulse_alert_4_4_tine_loud.ogg",
        "open_pad": "audio/music/hub_v31/v31_stem_open_pad.ogg",
        "bloom": "audio/music/hub_v31/v31_stem_bloom.ogg",
        "lab_machine": "audio/music/lab_v33/v33_stem_lab_machine.ogg",
        "lab_field": "audio/music/lab_v33/v33_stem_lab_field.ogg",
        "lab_bloom": "audio/music/lab_v33/v33_stem_lab_bloom.ogg",
        "lab_aria_healthy": "audio/music/lab_v33/v33_stem_aria_healthy.ogg",
        "lab_aria_missing": "audio/music/lab_v33/v33_stem_aria_missing.ogg",
        "lab_aria_dyads": "audio/music/lab_v33/v33_stem_aria_dyads.ogg",
        "lab_aria_fragile": "audio/music/lab_v33/v33_stem_aria_fragile.ogg",
        "lab_aria_collapsed": "audio/music/lab_v33/v33_stem_aria_collapsed.ogg",
        "habitat_room": "audio/music/habitat_v34/v34_habitat_room.ogg",
        "habitat_human": (
            "audio/music/habitat_v34/"
            "v34_stem_habitat_human_detail_research.ogg"),
        "telescope_air": (
            "audio/music/telescope_v35/v35_stem_telescope_air.ogg"),
        "telescope_orbit": (
            "audio/music/telescope_v35/v35_stem_telescope_orbit.ogg"),
        "generator_cycle": (
            "audio/music/generator_v36/v36_stem_generator_cycle.ogg"),
        "generator_pulse_calm": (
            "audio/music/generator_v36/"
            "v36_stem_generator_pulse_calm.ogg"),
        "generator_pulse_alert": (
            "audio/music/generator_v36/"
            "v36_stem_generator_pulse_alert.ogg"),
        "comms_carrier": (
            "audio/music/comms_v37/v37_stem_carrier.ogg"),
        "comms_reply_echo": (
            "audio/music/comms_v37/v37_stem_reply_echo.ogg"),
        "comms_reply_alert": (
            "audio/music/comms_v37/v37_stem_reply_alert.ogg"),
    }

    ## Old channels may still be playing in a save made before the v31 swap.
    _EOT_LEGACY_HUB_STEMS = (
        "ground_calm", "ground_storm2", "ground_storm3",
        "aria_healthy", "aria_missing", "aria_dyads", "aria_fragile",
        "aria_collapsed", "warm_full", "warm_thin",
    )

    for _eot_stem in _EOT_HUB_STEMS:
        renpy.music.register_channel(
            "eot_m_" + _eot_stem,
            mixer="music",
            loop=True,
            tight=True,
            **_EOT_SYNCHRO_KW
        )

    ## Keep the previous channel names registered so loading a pre-v31 save
    ## can silence its already-running hub cleanly before the new bank starts.
    for _eot_stem in _EOT_LEGACY_HUB_STEMS:
        renpy.music.register_channel(
            "eot_m_" + _eot_stem,
            mixer="music",
            loop=True,
            tight=True,
            **_EOT_SYNCHRO_KW
        )

    ## A second simple-cue deck permits a genuine overlap when the ordinary
    ## terminal field becomes the signal cue. Replacing a file on one Ren'Py
    ## channel serializes its fade-out/fade-in; this deck lets both breathe
    ## during the handoff instead of inserting a musical pause.
    renpy.music.register_channel(
        "eot_music_overlap", mixer="music", loop=True, tight=True)

    def _eot_hub_intensity():
        override = getattr(
            renpy.store, "eot_hub_music_debug_intensity", None)
        if config.developer and override in ("calm", "alert"):
            return override
        storm = getattr(renpy.store, "storm_intensity", 0)
        antenna_alert = getattr(
            renpy.store, "antenna_damage_notice", False)
        return "alert" if storm >= 2 or antenna_alert else "calm"

    def _eot_aria_tier():
        override = getattr(
            renpy.store, "eot_hub_music_debug_aria_tier", None)
        if config.developer and override in ("healthy", "missing", "dyads", "fragile", "collapsed"):
            return override
        integrity = int(getattr(renpy.store, "aria_integrity", 100))
        if integrity > 75:
            return "healthy"
        if integrity > 60:
            return "missing"
        if integrity > 45:
            return "dyads"
        if integrity > 20:
            return "fragile"
        return "collapsed"

    def _eot_hub_target_state():
        """Return (state key, stem volumes) from room and story state."""
        intensity = _eot_hub_intensity()
        location = getattr(renpy.store, "eot_audio_location", None)
        in_lab = location == "lab"
        in_habitat = location == "habitat"
        in_telescope = location == "telescope"
        in_generator = location == "generator"
        in_comms = location == "comms"
        in_storage = location == "storage"
        station_notice = bool(getattr(
            renpy.store, "antenna_damage_notice", False))
        marcus_location = getattr(renpy.store, "eot_marcus_location", None)
        marcus_in_habitat = (
            in_habitat and callable(marcus_location)
            and marcus_location() == "habitat")
        tier = _eot_aria_tier() if in_lab else None
        room_gain = EOT_ROOM_ALERT_DUCK if intensity == "alert" else 1.0
        volumes = {stem: 0.0 for stem in _EOT_HUB_STEMS}
        if in_lab:
            volumes.update({
                "lab_machine": room_gain,
                "lab_field": room_gain,
                "lab_bloom": room_gain,
                "lab_aria_" + tier: room_gain,
                "pulse_alert": (
                    EOT_HUB_PULSE_ALERT_GAIN if intensity == "alert" else 0.0),
            })
            key = ("lab", tier, intensity)
        elif in_habitat:
            ## Act 1's canteen language returns during the Long Night, with
            ## the selected muted-string research motif as human detail.
            volumes.update({
                "habitat_room": room_gain,
                "habitat_human": room_gain if marcus_in_habitat else 0.0,
                ## Habitat keeps its canteen-derived beat while calm. The
                ## station-wide alert pulse joins it only when the storm state
                ## calls for the same warning rhythm heard in other rooms.
                "pulse_alert": (
                    EOT_HUB_PULSE_ALERT_GAIN if intensity == "alert" else 0.0),
            })
            key = ("habitat", intensity, marcus_in_habitat)
        elif in_telescope:
            ## The dome sheds the station's everyday rhythm. A low trace of
            ## the common foundation keeps it in the same building while the
            ## wide pad and irregular bloom give the room distance and wonder.
            volumes.update({
                "foundation": 0.35 * room_gain,
                "telescope_air": room_gain,
                "telescope_orbit": room_gain,
                "pulse_alert": (1.5 if intensity == "alert" else 0.0),
            })
            key = ("telescope", intensity)
        elif in_generator:
            ## Generator SFX remain the literal room. These stems only reveal
            ## a musical cycle inside the machinery; alert is the same relay
            ## working harder, not a separate warning theme.
            volumes.update({
                "generator_cycle": room_gain,
                "generator_pulse_calm": (
                    1.0 if intensity == "calm" else 0.0),
                "generator_pulse_alert": (
                    0.85 if intensity == "alert" else 0.0),
            })
            key = ("generator", intensity)
        elif in_comms:
            ## Comms keeps a stable listening carrier. Its calm reply is
            ## passive and spacious; under signal/antenna pressure the same
            ## ECHO-coloured voice becomes more active rather than ominous.
            ## The common station rhythm belongs only to the actual damage
            ## bulletin, not to the whole severe-storm stretch.
            volumes.update({
                "comms_carrier": 1.0,
                "comms_reply_echo": (
                    1.0 if intensity == "calm" else 0.0),
                "comms_reply_alert": (
                    1.0 if intensity == "alert" else 0.0),
                "pulse_alert": (1.5 if station_notice else 0.0),
            })
            key = ("comms", intensity, station_notice)
        elif in_storage:
            ## Storage is a small utility room, not another musical landmark.
            ## A stripped station bed leaves space for shelves, weather, and
            ## Marcus's part hunt. Only a real station bulletin adds rhythm.
            storage_gain = 0.7 if station_notice else 1.0
            volumes.update({
                "foundation": 0.35 * storage_gain,
                "open_pad": 0.55 * storage_gain,
                "pulse_alert": (1.5 if station_notice else 0.0),
            })
            key = ("storage", station_notice)
        else:
            ## The complete pad-and-bloom arrangement is the station's
            ## identity. ARIA's condition does not filter any other room.
            volumes.update({
                "foundation": 1.0,
                "pulse_calm": (
                    EOT_HUB_PULSE_CALM_GAIN if intensity == "calm" else 0.0),
                "pulse_alert": (
                    EOT_HUB_PULSE_ALERT_GAIN if intensity == "alert" else 0.0),
                "open_pad": 1.0,
                "bloom": 1.0,
            })
            key = ("hub", intensity)
        return (key, volumes)

    def _eot_terminal_duck():
        """§7: music recedes while the live terminal owns the scene."""
        return 0.35 if renpy.get_screen("echo_terminal_live") is not None else 1.0

    def _eot_hub_apply(volumes, fade=1.2):
        ## The hub has its own mix level so it can be balanced independently
        ## from the linear act-1 cues on the plain music channel.
        duck = _eot_terminal_duck()
        for stem, volume in volumes.items():
            renpy.music.set_volume(
                volume * duck * EOT_HUB_MIX, delay=fade,
                channel="eot_m_" + stem)

    def eot_hub_music_start():
        if (renpy.store.eot_hub_music_started
                and getattr(renpy.store, "eot_hub_music_bank_version", 0)
                >= EOT_HUB_BANK_VERSION):
            return
        if renpy.store.eot_hub_music_started:
            for stem in _EOT_HUB_STEMS:
                renpy.music.stop(channel="eot_m_" + stem, fadeout=1.0)
            renpy.store.eot_hub_music_started = False
        state = _eot_hub_target_state()
        renpy.music.stop(channel="music", fadeout=2.0)
        renpy.music.stop(channel="eot_music_overlap", fadeout=2.0)
        renpy.music.stop(channel="eot_eva_music_alt", fadeout=2.0)
        for legacy_stem in _EOT_LEGACY_HUB_STEMS:
            renpy.music.stop(channel="eot_m_" + legacy_stem, fadeout=1.0)
        _eot_hub_apply(state[1], fade=0.0)
        for stem, filename in _EOT_HUB_STEMS.items():
            renpy.music.play(
                filename, channel="eot_m_" + stem, loop=True,
                synchro_start=True, fadein=2.5, tight=True)
        renpy.store.eot_hub_music_started = True
        renpy.store.eot_hub_music_state = state[0]
        renpy.store.eot_hub_music_pending = None
        renpy.store.eot_hub_music_bank_version = EOT_HUB_BANK_VERSION

    def eot_hub_music_stop(fadeout=4.0):
        for stem in _EOT_HUB_STEMS:
            renpy.music.stop(channel="eot_m_" + stem, fadeout=fadeout)
        for legacy_stem in _EOT_LEGACY_HUB_STEMS:
            renpy.music.stop(channel="eot_m_" + legacy_stem, fadeout=fadeout)
        renpy.music.stop(channel="eot_eva_music_alt", fadeout=fadeout)
        renpy.store.eot_hub_music_started = False
        renpy.store.eot_hub_music_pending = None

    def _eot_hub_music_poll():
        """Slow poll: derive the target from story state; queue on change.
        Also re-applies the terminal duck so sessions breathe the mix."""
        if not renpy.store.eot_hub_music_started:
            return
        state = _eot_hub_target_state()
        if (state[0] == renpy.store.eot_hub_music_state
                and renpy.store.eot_hub_music_pending is None):
            _eot_hub_apply(state[1], fade=0.8)
            return
        if renpy.store.eot_hub_music_pending == state[0]:
            return
        pos = renpy.music.get_pos(channel="eot_m_foundation")
        if pos is None:
            _eot_hub_apply(state[1], fade=EOT_HUB_BAR_SECONDS)
            renpy.store.eot_hub_music_state = state[0]
            renpy.store.eot_hub_music_pending = None
            return
        wait = EOT_HUB_BAR_SECONDS - (pos % EOT_HUB_BAR_SECONDS)
        if wait < 0.08:
            wait = EOT_HUB_BAR_SECONDS
        renpy.store.eot_hub_music_pending = state[0]
        renpy.store.eot_hub_music_request_pos = pos % EOT_HUB_LOOP_SECONDS
        renpy.store.eot_hub_music_wait = wait

    def _eot_hub_music_tick():
        """Fast tick while a change is pending: apply on the bar."""
        if renpy.store.eot_hub_music_pending is None:
            return
        pos = renpy.music.get_pos(channel="eot_m_foundation")
        if pos is None:
            elapsed = renpy.store.eot_hub_music_wait
        else:
            elapsed = (pos % EOT_HUB_LOOP_SECONDS
                       - renpy.store.eot_hub_music_request_pos)
            if elapsed < -0.05:
                elapsed += EOT_HUB_LOOP_SECONDS
        if elapsed + 0.04 >= renpy.store.eot_hub_music_wait:
            state = _eot_hub_target_state()
            _eot_hub_apply(state[1], fade=EOT_HUB_BAR_SECONDS)
            renpy.store.eot_hub_music_state = state[0]
            renpy.store.eot_hub_music_pending = None

    _EOT_DEBUG_INTENSITIES = (None, "calm", "alert")
    _EOT_DEBUG_ARIA_TIERS = (
        None, "healthy", "missing", "dyads", "fragile", "collapsed")
    def _eot_debug_cycle(value, values):
        try:
            index = values.index(value)
        except ValueError:
            index = 0
        return values[(index + 1) % len(values)]

    def eot_hub_debug_set_intensity(value):
        if not config.developer:
            return
        if value not in _EOT_DEBUG_INTENSITIES:
            raise ValueError("unknown hub music intensity override")
        renpy.store.eot_hub_music_debug_intensity = value
        _eot_hub_music_poll()
        renpy.restart_interaction()

    def eot_hub_debug_cycle_intensity():
        current = getattr(
            renpy.store, "eot_hub_music_debug_intensity", None)
        eot_hub_debug_set_intensity(
            _eot_debug_cycle(current, _EOT_DEBUG_INTENSITIES))

    def eot_hub_debug_set_aria_tier(value):
        if not config.developer:
            return
        if value not in _EOT_DEBUG_ARIA_TIERS:
            raise ValueError("unknown Lab ARIA music override")
        renpy.store.eot_hub_music_debug_aria_tier = value
        _eot_hub_music_poll()
        renpy.restart_interaction()

    def eot_hub_debug_cycle_aria_tier():
        current = getattr(
            renpy.store, "eot_hub_music_debug_aria_tier", None)
        eot_hub_debug_set_aria_tier(
            _eot_debug_cycle(current, _EOT_DEBUG_ARIA_TIERS))

    def eot_hub_debug_reset_music():
        if not config.developer:
            return
        renpy.store.eot_hub_music_debug_intensity = None
        renpy.store.eot_hub_music_debug_aria_tier = None
        _eot_hub_music_poll()
        renpy.restart_interaction()

    def eot_hub_debug_intensity_label():
        value = getattr(
            renpy.store, "eot_hub_music_debug_intensity", None)
        return (value or "auto").upper()

    def eot_hub_debug_aria_label():
        value = getattr(
            renpy.store, "eot_hub_music_debug_aria_tier", None)
        return (value or "auto").upper()

    def eot_hub_music_room_changed():
        """Queue a synchronized bank change as soon as room audio changes."""
        if renpy.store.eot_hub_music_started:
            _eot_hub_music_poll()

    def eot_hub_music_refresh_now(fade=0.35):
        """Apply a short presentation beat without waiting for a bar boundary."""
        if not renpy.store.eot_hub_music_started:
            return
        state = _eot_hub_target_state()
        _eot_hub_apply(state[1], fade=fade)
        renpy.store.eot_hub_music_state = state[0]
        renpy.store.eot_hub_music_pending = None

    # In-game music mix (2026-08-25): the rendered files are mastered to
    # commercial loudness; the game plays them at half so dialogue, SFX
    # and ambience keep the foreground.
    EOT_MUSIC_MIX = 0.5

    def eot_music_play(filename, fadein=1.5, fadeout=1.5, level=1.0):
        """`level` scales this cue only; the next play() resets to EOT_MUSIC_MIX."""
        renpy.music.stop(channel="eot_music_overlap", fadeout=fadeout)
        gain = EOT_MUSIC_MIX * max(0.0, min(1.0, float(level)))
        renpy.music.set_volume(gain, delay=0.0, channel="music")
        renpy.music.play("audio/music/" + filename, channel="music",
                         loop=True, fadein=fadein, fadeout=fadeout)

    def eot_music_crossfade(filename, fadein=2.0, fadeout=2.0):
        """Overlap a new loop with the current simple cue during handoff."""
        renpy.music.set_volume(
            EOT_MUSIC_MIX, delay=0.0, channel="eot_music_overlap")
        renpy.music.play(
            "audio/music/" + filename, channel="eot_music_overlap",
            loop=True, fadein=fadein)
        renpy.music.stop(channel="music", fadeout=fadeout)

    def eot_music_once(filename, fadein=0.5):
        renpy.music.stop(channel="eot_music_overlap", fadeout=fadein)
        renpy.music.set_volume(EOT_MUSIC_MIX, delay=0.0, channel="music")
        renpy.music.play("audio/music/" + filename, channel="music",
                         loop=False, fadein=fadein)

    def eot_music_set_level(level=1.0, fade=1.0):
        """Scale both simple-cue channels without changing the playing cue."""
        gain = EOT_MUSIC_MIX * max(0.0, min(1.0, float(level)))
        renpy.music.set_volume(gain, delay=fade, channel="music")
        renpy.music.set_volume(gain, delay=fade, channel="eot_music_overlap")

    def eot_music_stop(fadeout=2.0):
        renpy.music.stop(channel="music", fadeout=fadeout)
        renpy.music.stop(channel="eot_music_overlap", fadeout=fadeout)

    if "eot_hub_music_quantizer" not in config.overlay_screens:
        config.overlay_screens.append("eot_hub_music_quantizer")
    if "eot_hub_music_debug_panel" not in config.overlay_screens:
        config.overlay_screens.append("eot_hub_music_debug_panel")


screen eot_hub_music_quantizer():
    if eot_hub_music_started:
        if eot_hub_music_pending is not None:
            timer 0.05 repeat True action Function(_eot_hub_music_tick)
        else:
            timer 1.0 repeat True action Function(_eot_hub_music_poll)


screen eot_hub_music_debug_panel():
    if config.developer and eot_hub_music_started:
        zorder 290
        frame:
            xalign 0.99
            yalign 0.01
            background Solid("#07131de8")
            padding (8, 6)
            hbox:
                spacing 6
                text "MUSIC TEST" color "#7bdfff" size 13 yalign 0.5
                textbutton ("INT " + eot_hub_debug_intensity_label()):
                    action Function(eot_hub_debug_cycle_intensity)
                if eot_audio_location == "lab":
                    textbutton ("ARIA " + eot_hub_debug_aria_label()):
                        action Function(eot_hub_debug_cycle_aria_tier)
                textbutton "AUTO":
                    action Function(eot_hub_debug_reset_music)
