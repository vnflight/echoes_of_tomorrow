## Echoes presentation audio. Ambience and weather are separate looping
## channels on the Sound mixer so room machinery can change without cutting
## the Arctic wind carried through the building.

default eot_room_ambience = None
default eot_audio_location = None
default eot_weather_audio_level = -1
default eot_weather_audio_mode = "interior"
default eot_generator_adv_ambience = False
default eot_eva_music_deck = "music"

init -20 python:
    renpy.music.register_channel("ambience", mixer="sfx", loop=True, stop_on_mute=True, tight=True)
    renpy.music.register_channel("weather", mixer="sfx", loop=True, stop_on_mute=True, tight=True)
    renpy.music.register_channel("terminal_type", mixer="sfx", loop=False, stop_on_mute=True, tight=True)
    renpy.music.register_channel("terminal_scan", mixer="sfx", loop=True, stop_on_mute=True, tight=True)
    renpy.music.register_channel("structure", mixer="sfx", loop=False, stop_on_mute=True, tight=True)
    renpy.music.register_channel("foley", mixer="sfx", loop=False, stop_on_mute=True, tight=True)
    renpy.music.register_channel(
        "eot_eva_music_alt", mixer="music", loop=True,
        stop_on_mute=True, tight=True)

    _EOT_ROOM_BEDS = {
        "corridor": "audio/sfx/corridor_room_loop.ogg",
        "lab": "audio/sfx/lab_room_loop.ogg",
        "comms": "audio/sfx/comms_room_loop.ogg",
        "generator": "audio/sfx/generator_room_loop.ogg",
        "habitat": "audio/sfx/canteen_room_loop.ogg",
        ## Storage shares the station ventilation texture, but its level is
        ## reduced below the corridor to make the small room feel enclosed.
        "storage": "audio/sfx/corridor_room_loop.ogg",
    }

    def eot_room_ambience_volume(sound):
        if (getattr(store, "eot_audio_location", None) == "storage"
                and sound == _EOT_ROOM_BEDS["storage"]):
            return 0.25
        if sound == _EOT_ROOM_BEDS["lab"]:
            return 0.30
        if sound == _EOT_ROOM_BEDS["comms"]:
            return 0.30
        if sound == _EOT_ROOM_BEDS["generator"]:
            return 0.70 if store.eot_generator_adv_ambience else 0.56
        return 1.0

    def eot_set_generator_adv_ambience(active, fade=0.45):
        """Let machinery rise for people speaking over it in Generator ADV."""
        store.eot_generator_adv_ambience = bool(active)
        if (getattr(store, "eot_audio_location", None) == "generator"
                and getattr(store, "eot_room_ambience", None)
                == _EOT_ROOM_BEDS["generator"]):
            renpy.music.set_volume(
                eot_room_ambience_volume(_EOT_ROOM_BEDS["generator"]),
                delay=fade, channel="ambience")

    def eot_set_room_ambience(sound, fadeout=0.8, fadein=0.8):
        """Remember the visible room bed; terminal presentation may mute it."""
        store.eot_room_ambience = sound
        if sound:
            renpy.music.set_volume(
                eot_room_ambience_volume(sound),
                delay=fadein,
                channel="ambience"
            )
        if renpy.get_screen("echo_terminal_live") is not None:
            return
        if sound:
            renpy.music.play(
                sound, channel="ambience", loop=True,
                fadeout=fadeout, fadein=fadein
            )
        else:
            renpy.music.stop(channel="ambience", fadeout=fadeout)

    def eot_enter_room(location, allow_creak=True):
        """Set a room identity and occasionally let the stressed shell answer."""
        store.eot_audio_location = location
        store.eot_generator_adv_ambience = False
        music_room_changed = getattr(store, "eot_hub_music_room_changed", None)
        if music_room_changed is not None:
            music_room_changed()
        eot_set_room_ambience(_EOT_ROOM_BEDS.get(location), fadeout=0.9, fadein=1.1)
        _weather_gain = 1.0
        if renpy.get_screen("echo_terminal_live") is not None:
            _weather_gain *= 0.45
        renpy.music.set_volume(_weather_gain, delay=1.0, channel="weather")
        intensity = int(getattr(store, "storm_intensity", 0))
        if store.eot_weather_audio_level >= 0:
            eot_update_storm_weather(intensity)
        if not allow_creak or intensity <= 0 or location == "habitat":
            return
        visit = int(getattr(store, "hub_visits", 0))
        location_seed = sum((index + 1) * ord(char) for index, char in enumerate(location))
        period = {1: 5, 2: 3, 3: 2}.get(intensity, 5)
        if (visit * 7 + location_seed + intensity * 11) % period:
            return
        variant = 1 + ((visit + location_seed + intensity) % 3)
        renpy.sound.play(
            "audio/sfx/structure_creak_{}.ogg".format(variant),
            channel="structure"
        )

    def eot_update_storm_weather(level):
        level = max(0, min(3, int(level)))
        if getattr(store, "eot_weather_audio_mode", "interior") != "interior":
            return
        sound = "audio/sfx/wind_interior_storm_{}.ogg".format(level)
        if level > 0 and store.eot_audio_location == "lab":
            sound = "audio/sfx/wind_lab_interior_loop.ogg"
        if (level == getattr(store, "eot_weather_audio_level", -1)
                and renpy.music.get_playing(channel="weather") == sound):
            return
        store.eot_weather_audio_level = level
        gain = 0.45 if renpy.get_screen("echo_terminal_live") is not None else 1.0
        renpy.music.set_volume(gain, delay=1.0, channel="weather")
        renpy.music.play(
            sound,
            channel="weather", loop=True, fadeout=2.5, fadein=2.5
        )

    def eot_enter_exterior(play_wind=True):
        ## Some exterior scenes own a complete wind-led music bed. Let those
        ## suppress the legacy weather loop instead of stacking two gales.
        store.eot_weather_audio_mode = (
            "exterior" if play_wind else "exterior_music")
        store.eot_audio_location = "exterior"
        eot_set_room_ambience(None, fadeout=1.0)
        if play_wind:
            renpy.music.set_volume(1.0, delay=1.0, channel="weather")
            renpy.music.play(
                "audio/sfx/wind_eva_loop.ogg",
                channel="weather", loop=True, fadeout=1.8, fadein=1.2
            )
        else:
            renpy.music.stop(channel="weather", fadeout=0.8)

    def eot_leave_exterior(location="corridor"):
        store.eot_weather_audio_mode = "interior"
        store.eot_weather_audio_level = -1
        eot_enter_room(location, allow_creak=False)
        eot_update_storm_weather(getattr(store, "storm_intensity", 0))

    def eot_eva_music_reset():
        """Make the plain music deck own the intro; retire a stale alt deck."""
        store.eot_eva_music_deck = "music"
        renpy.music.set_volume(1.0, delay=0.0, channel="music")
        renpy.music.set_volume(1.0, delay=0.0, channel="eot_eva_music_alt")
        renpy.music.stop(channel="eot_eva_music_alt", fadeout=0.3)

    def eot_eva_music_switch(sound, fade=2.6):
        """Crossfade EVA cues with explicit, overlapping channel ramps."""
        old_deck = getattr(store, "eot_eva_music_deck", "music")
        new_deck = (
            "eot_eva_music_alt" if old_deck == "music" else "music")

        ## File fadeins and channel fadeouts can be applied on different audio
        ## updates, which leaves an audible seam on some backends.  Keep both
        ## decks alive and ramp their channel volumes over the same interval.
        renpy.music.set_volume(0.0, delay=0.0, channel=new_deck)
        renpy.music.play(
            sound, channel=new_deck, loop=True, fadeout=0.0,
            fadein=0.0, tight=True)
        renpy.music.set_volume(1.0, delay=fade, channel=new_deck)
        renpy.music.set_volume(0.0, delay=fade, channel=old_deck)
        store.eot_eva_music_deck = new_deck

    def eot_enter_dawn():
        """Replace the peak-storm inheritance with calm post-front air."""
        store.eot_weather_audio_mode = "dawn"
        store.eot_audio_location = "exterior"
        eot_set_room_ambience(None, fadeout=1.5)
        renpy.music.set_volume(1.0, delay=1.0, channel="weather")
        renpy.music.play(
            "audio/sfx/wind_dawn_loop.ogg",
            channel="weather", loop=True, fadeout=4.0, fadein=4.0
        )

    # Terminal texture mix (2026-08-25): scanner motor and keystrokes
    # sit a third quieter under the louder music master.
    EOT_SCAN_GAIN = 0.67

    def eot_terminal_audio_enter():
        renpy.music.set_volume(EOT_SCAN_GAIN, delay=0.0,
                               channel="terminal_type")
        renpy.music.stop(channel="ambience", fadeout=0.8)
        # Keep the station weather present, but make acoustic room for the
        # scanner as the terminal comes forward. This is a screen-level duck,
        # so the wind does not pump up and down between individual rows.
        renpy.music.set_volume(0.45, delay=0.9, channel="weather")

    def eot_terminal_audio_exit():
        renpy.music.stop(channel="terminal_scan", fadeout=0.04)
        renpy.music.set_volume(1.0, delay=1.2, channel="weather")
        sound = getattr(store, "eot_room_ambience", None)
        if sound:
            renpy.music.set_volume(
                eot_room_ambience_volume(sound),
                delay=0.0,
                channel="ambience"
            )
            renpy.music.play(sound, channel="ambience", loop=True, fadein=0.8)

    def eot_terminal_reveal_start(row):
        """Machine-authored rows render through a low scanner-motor layer."""
        renpy.music.stop(channel="terminal_scan", fadeout=0.02)
        if row.get("who") == "elara>":
            return
        text = row.get("display_text", row.get("text", ""))
        seed = sum((index + 1) * ord(char) for index, char in enumerate(text))
        pitch = ("m20", "m10", "mid", "p10", "p20")[seed % 5]
        renpy.music.set_volume(EOT_SCAN_GAIN, delay=0.0,
                               channel="terminal_scan")
        renpy.music.play(
            "audio/sfx/scan_continuous_motor_v6_{}.ogg".format(pitch),
            channel="terminal_scan", loop=True, fadein=0.04
        )

    def eot_terminal_reveal_finish():
        renpy.music.stop(channel="terminal_scan", fadeout=0.055)

    def eot_terminal_type_tick(old_reveal, reveal):
        """Irregular, rollback-stable output texture derived from row content."""
        rows = getattr(store, "echo_terminal_rows", [])
        row = rows[-1] if rows else {}
        text = row.get("display_text", row.get("text", ""))
        seed = sum((index + 1) * ord(char) for index, char in enumerate(text))
        if row.get("who") == "elara>":
            family = "keyboard_tick"
            gaps = (2, 4, 3, 6, 2, 5, 3, 4, 7, 2, 3, 5, 2)
            variants = 10
        else:
            newly_visible = text[int(old_reveal):int(reveal)]
            # At high text speeds one timer tick reveals several characters.
            # Looking for whitespace anywhere in that whole chunk made long,
            # wrapped ECHO-7 lines spend most of their life at 14% volume.
            # Shape the motor from the reveal cursor instead: visual wrapping
            # adds no character, while a real space/newline still breathes.
            cursor_char = newly_visible[-1:] if newly_visible else ""
            punctuation = cursor_char in "/.,:;!?"
            whitespace = bool(cursor_char and cursor_char.isspace())
            micro_pause = ((int(reveal) * 17 + seed) % 43) == 0
            if punctuation:
                volume = 0.08
            elif whitespace:
                volume = 0.14
            elif micro_pause:
                volume = 0.38
            else:
                volume = 1.0
            renpy.music.set_volume(volume * EOT_SCAN_GAIN, delay=0.018,
                                   channel="terminal_scan")
            return

        position = 1 + seed % 4
        step = seed % len(gaps)
        trigger = None
        while position <= int(reveal):
            if int(old_reveal) < position:
                trigger = position
            position += gaps[step % len(gaps)]
            step += 1
        if trigger is None:
            return
        variant = 1 + ((trigger * 7 + seed) % variants)
        renpy.sound.play(
            "audio/sfx/{}_{}.ogg".format(family, variant),
            channel="terminal_type"
        )

define audio.eot_wind_exterior = "audio/sfx/wind_exterior_loop.ogg"
define audio.eot_wind_interior = "audio/sfx/wind_interior_loop.ogg"
define audio.eot_lab_room = "audio/sfx/lab_room_loop.ogg"
define audio.eot_canteen_room = "audio/sfx/canteen_room_loop.ogg"
define audio.eot_terminal_alert = "audio/sfx/terminal_alert.ogg"
define audio.eot_terminal_chime = "audio/sfx/terminal_chime.ogg"
define audio.eot_echo7_first_contact = "audio/sfx/echo7_first_contact.ogg"
define audio.eot_mug_desk_impact = "audio/sfx/mug_desk_impact.ogg"
define audio.eot_keyboard_tick_1 = "audio/sfx/keyboard_tick_1.ogg"
define audio.eot_keyboard_tick_2 = "audio/sfx/keyboard_tick_2.ogg"
define audio.eot_keyboard_tick_3 = "audio/sfx/keyboard_tick_3.ogg"
define audio.eot_keyboard_tick_4 = "audio/sfx/keyboard_tick_4.ogg"
define audio.eot_keyboard_tick_5 = "audio/sfx/keyboard_tick_5.ogg"
define audio.eot_keyboard_tick_6 = "audio/sfx/keyboard_tick_6.ogg"
define audio.eot_keyboard_tick_7 = "audio/sfx/keyboard_tick_7.ogg"
define audio.eot_keyboard_tick_8 = "audio/sfx/keyboard_tick_8.ogg"
define audio.eot_keyboard_tick_9 = "audio/sfx/keyboard_tick_9.ogg"
define audio.eot_keyboard_tick_10 = "audio/sfx/keyboard_tick_10.ogg"
define audio.eot_rope_tension = "audio/sfx/rope_tension.ogg"
define audio.eot_structure_peak = "audio/sfx/structure_creak_3.ogg"
define audio.eot_eva_departure_intro = "audio/music/eva_v39/v39_eva_departure_intro.ogg"
define audio.eot_eva_traverse = "audio/music/eva_v39/v39_eva_traverse.ogg"
define audio.eot_eva_antenna = "audio/music/eva_v39/v39_eva_antenna.ogg"
define audio.eot_eva_dialogue = "audio/music/eva_v39/v39_eva_dialogue.ogg"
