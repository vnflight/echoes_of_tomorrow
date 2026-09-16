################################################################################
## Echoes of Tomorrow - Main Script
##
## A visual novel about a researcher at a remote observatory who receives
## mysterious terminal messages from the future.
##
## Demonstrates: NVL/ADV modes, SetField toggles, unlabelled imagebuttons,
## modal overlays, selected button state, smart quotes, conditional menu items,
## NVL hub menus, image-only buttons, two-click interactions, map/travel,
## inventory/stats, end credits overlay, class gating.
################################################################################

################################################################################
## Character Definitions
################################################################################

## NVL-mode characters (appear in the scrolling log-style display)
define narrator_nvl = Character(None, kind=nvl)
define elara_nvl = Character("elara>", kind=nvl, color="#88ccff", who_font="gui/fonts/JetBrainsMono-Regular.ttf", what_font="gui/fonts/JetBrainsMono-Regular.ttf")
define aria_nvl = Character("ARIA>", kind=nvl, color="#66ffcc", who_font="gui/fonts/JetBrainsMono-Regular.ttf", what_font="gui/fonts/JetBrainsMono-Regular.ttf")
define signal_nvl = Character("????>", kind=nvl, color="#ff6688", who_font="gui/fonts/JetBrainsMono-Regular.ttf", what_font="gui/fonts/JetBrainsMono-Regular.ttf")
define signal_known = Character("ECHO-7>", kind=nvl, color="#ff6688", who_font="gui/fonts/JetBrainsMono-Regular.ttf", what_font="gui/fonts/JetBrainsMono-Regular.ttf")
define marcus_nvl = Character("CHEN>", kind=nvl, color="#ffcc44", who_font="gui/fonts/JetBrainsMono-Regular.ttf", what_font="gui/fonts/JetBrainsMono-Regular.ttf")
define terminal_nvl = Character("SYSTEM", kind=nvl, color="#44ff44", who_font="gui/fonts/JetBrainsMono-Regular.ttf", what_font="gui/fonts/JetBrainsMono-Regular.ttf")

## ADV-mode characters (standard dialogue box)
define narrator_adv = Character(None)
define elara = Character("Dr. Voss", color="#88ccff")
define marcus = Character("Dr. Chen", color="#ffcc44")
define aria = Character("ARIA", color="#66ffcc")

## Internal monologue (NVL thought — uses nvl_narrator style)
define elara_thought = Character("THOUGHT", kind=nvl, what_italic=True, what_color="#aabbdd")
define elara_thought_adv = Character(None, what_italic=True, what_color="#c9c1dd")

## Mode changes need a little more air than the 0.2s dialogue-window fade,
## but the transition belongs on the show statement so it runs only once.
define echo_mode_dissolve = Dissolve(0.48)

## The same dissolve carries EVERY NVL boundary, including the implicit ones.
## Ren'Py fires these two on the ADV<->NVL mode change, so a block that never
## says `nvl show` still fades in and one that simply runs into an ADV line
## still fades out. Explicit `nvl show` / `nvl hide` set the mode to
## "window show" / "window hide" first, so they never double up with these.
## (User report 2026-08-17: "we end a conversation and then suddenly NVL comes
## up" — half of that suddenness was NVL blocks with no transition at all.)
define config.adv_nvl_transition = echo_mode_dissolve
define config.nvl_adv_transition = echo_mode_dissolve

## The cinematic letterbox is the slower register. It used to ease in from an
## ATL on the panel itself, which restarted on every NVL update — a grey wash
## washing back over the screen after each line. The register now rides the
## block's own `nvl show`, which runs exactly once, when the block opens.
define echo_cine_dissolve = Dissolve(0.9)

## One beat of empty room. Placed between a location's `scene ... with fade`
## and whatever speaks in it, so the player reads WHERE before they read WHAT.
## A transition rather than a pause: no interaction, no checkpoint, and a click
## goes straight through it.
define echo_room_beat = Pause(0.35)

## Storm and dawn exteriors carry act boundaries, not ordinary room arrivals.
## Hold the unobscured image long enough to register before the darker NVL
## frame fades in. As a transition, the hold remains click-skippable and does
## not create a separate dialogue checkpoint.
define echo_exterior_hold = Pause(3.0)

init python:
    def eot_ending_title_hold(subtitle=None):
        """Click-skippable reading time for the final title composition."""
        if not subtitle:
            return 4.0
        return min(12.0, max(7.0, 3.0 + (0.5 * len(subtitle.split()))))

label terminal_reset():
    $ echo_terminal_reset()
    return


label terminal_clear(delay="afm"):
    $ echo_terminal_clear()
    $ _terminal_delay = echo_terminal_pause_delay("", delay)
    if _terminal_delay is None:
        $ renpy.pause(None, checkpoint=True)
    else:
        $ renpy.pause(_terminal_delay, checkpoint=False)
        $ renpy.checkpoint(True, hard=True)
    return


label terminal_system(text, delay="afm"):
    ## config.window = "auto" only auto-hides the say window at scene / call
    ## screen / menu. Terminal rows are written from renpy.pause() inside a
    ## label, which is none of those, so the box left over from the last ADV
    ## line would sit there covering the newest rows -- and now that the log
    ## follows its own bottom, the newest row is exactly what it covers.
    window hide
    $ echo_terminal_system(text)
    $ _terminal_reveal_delay = echo_terminal_reveal_delay(text)
    $ renpy.pause(_terminal_reveal_delay, checkpoint=False)
    $ echo_terminal_finish_reveal()
    if delay in ("afm", "manual"):
        $ renpy.pause(None, checkpoint=True)
    else:
        $ _terminal_delay = echo_terminal_pause_delay(text, delay)
        $ renpy.pause(_terminal_delay, checkpoint=False)
        $ renpy.checkpoint(True, hard=True)
    return


label terminal_prompt(who, text, color="#dcfff0", delay="afm"):
    ## See terminal_system: nothing is speaking while the terminal types.
    window hide
    $ echo_terminal_prompt(who, text, color)
    $ _terminal_reveal_delay = echo_terminal_reveal_delay(text)
    $ renpy.pause(_terminal_reveal_delay, checkpoint=False)
    $ echo_terminal_finish_reveal()
    if delay in ("afm", "manual"):
        $ renpy.pause(None, checkpoint=True)
    else:
        $ _terminal_delay = echo_terminal_pause_delay(text, delay)
        $ renpy.pause(_terminal_delay, checkpoint=False)
        $ renpy.checkpoint(True, hard=True)
    return


label terminal_elara(text, delay="afm"):
    call terminal_prompt("elara>", text, "#88ccff", delay)
    return


label terminal_aria(text, delay="afm"):
    call terminal_prompt("ARIA>", text, "#66ffcc", delay)
    return


label terminal_signal(text, delay="afm"):
    ## "????>" until the probe names itself, "ECHO-7>" from that line on.
    ## Rows already in the log keep the label they were written with, which
    ## is the point: the transcript shows the moment it stopped being anonymous.
    if echo7_designation_known:
        call terminal_prompt("ECHO-7>", text, "#ff6688", delay)
    else:
        call terminal_prompt("????>", text, "#ff6688", delay)
    return


################################################################################
## Character Sprite Transforms
################################################################################

## Scale down the 1024x1536 v2 sprites to fit the 1280x720 stage.
transform sprite_left:
    xzoom -0.46
    yzoom 0.46
    xalign 0.15
    yalign 1.0

transform sprite_right:
    zoom 0.46
    xalign 0.85
    yalign 1.0

transform sprite_center:
    zoom 0.46
    xalign 0.5
    yalign 1.0

transform ending_title_position:
    xalign 0.5
    yalign 0.5


################################################################################
## Character Sprite Image Declarations
################################################################################

## Canonical v2 sprites. Their tracked filenames keep releases independent of
## the ignored generation/review candidate directories.
image elara neutral = "images/elara neutral.png"
image elara concerned = "images/elara concerned.png"
image elara determined = "images/elara determined.png"
image elara sad = "images/elara sad.png"
image elara shocked = "images/elara shocked.png"

image marcus neutral = "images/marcus neutral.png"
image marcus excited = "images/marcus excited.png"
image marcus suspicious = "images/marcus suspicious.png"
image marcus angry = "images/marcus angry.png"
image marcus defeated = "images/marcus defeated.png"


################################################################################
## Background Image Declarations
################################################################################

## Explicit declarations — Ren'Py auto-detection is unreliable for underscore
## filenames across versions.
image bg_boot_screen = "images/bg_boot_screen.png"
image bg_cascade = "images/bg_cascade.png"
image bg_comms = "images/bg_comms.png"
image bg_conference_hall = "images/bg_conference_hall.png"
image bg_dawn = "images/bg_dawn.png"
image bg_generator = "images/bg_generator.png"
image bg_habitat_module = "images/bg_habitat_module.png"
image bg_holding_facility = "images/bg_holding_facility.png"
image bg_lab = "images/bg_lab.png"
image bg_observatory = "images/bg_observatory.png"
image bg_observatory_aurora = "images/bg_observatory_aurora.png"
image bg_observatory_exterior = "images/bg_observatory_exterior.png"
image bg_storm = "images/bg_storm.png"
image bg_storage = "images/bg_storage.png"
image bg_telescope = "images/bg_telescope.png"


################################################################################
## Splashscreen & Title
################################################################################

label splashscreen:
    scene black
    show screen crt_overlay(heavy=True)
    with Pause(0.5)

    show text "{size=+10}{color=#66ffcc}Aethon Systems presents{/color}{/size}" at truecenter
    with dissolve
    pause 2.0
    hide text
    with dissolve
    pause 0.5

    hide screen crt_overlay
    return


################################################################################
## ACT 1 — THE SIGNAL
################################################################################

label start:

    ## The title theme (config.main_menu_music) shares the music channel with
    ## the opening cue. Fade it out first; eot_music_play below passes the
    ## same fadeout so its own default (1.5 s) does not shorten this one.
    ## One channel never overlaps: 2 s out, then the cue's 3 s in.
    stop music fadeout 2.0

    ## Boot ordering (user report 2026-08-17): returning from the main menu
    ## leaves the master layer EMPTY, so the opening `with fade` had nothing to
    ## fade OUT of — one frame of Ren'Py's transparent-region checkerboard in
    ## dev mode, a black punch-through in a release build. Lay an opaque ground
    ## down and commit it with `with None` so it is the transition's old side.
    scene black
    with None

    ## Music (MUSIC_DIRECTION.md §3, mood-first): the daily grind —
    ## work-like, patient, a little boring on purpose. Presentation only.
    $ eot_music_play("act1/eo31c_terminal_electric.ogg", fadein=3.0, fadeout=2.0)

    ## Reset all game state for replay
    $ trust_signal = 0
    $ marcus_relationship = 0
    $ marcus_trust = 0
    $ investigated_privately = False
    $ signal_reported = False
    $ blocked_signal = False
    $ report_blocked_signal = False
    $ late_signal_reconnect = 0
    $ echo7_designation_known = False
    $ knows_cascade = False
    $ knows_prediction_evidence = False
    $ knows_convergence_file = False
    $ knows_origin_claim = False
    $ knows_aurora_option = False
    $ read_all_logs = False
    $ aria_warned = False
    $ chose_leap_of_faith = False
    $ ending_seen = None
    $ evidence_log = []
    $ evidence_tags = []
    $ specialization = "signals"
    $ audit_focus = "trust"
    $ power_cells = 0
    $ data_drives = 0
    $ antenna_parts = 0
    $ drive_thought_seen = False
    $ coolant_cartridges = 0
    $ signal_amps = 0
    $ aux_power_remaining = 0
    $ storage_supplies_found = False
    $ habitat_cell_found = False
    $ comms_amp_found = False
    $ signal_strength = 80
    $ aria_integrity = 100
    $ power_priority = "balanced"
    $ current_location = "lab"
    $ storm_intensity = 0
    $ time_remaining = 300
    $ long_night_active = False
    $ operational_stats_active = True
    $ hub_visits = 0
    $ hub_return_location = None
    $ comms_visits = 0
    $ echo7_cooldown_remaining = 0
    $ telescope_visited = False
    $ star_map_reviewed = False
    $ star_map_complete = False
    $ star_map_open_requested = False
    $ star_map_known_sources_logged = False
    $ star_map_anomalies_correlated = False
    $ star_map_origin_analyzed = False
    $ lab_visited = False
    $ origin_sweep_done = False
    $ origin_sweep_running = False
    $ origin_sweep_staged = False
    $ origin_sweep_progress = 0
    $ origin_sweep_interruptions = 0
    $ origin_sweep_notice = False
    $ origin_sweep_unseen = False
    $ echo7_origin_hint_seen = False
    $ habitat_visited = False
    $ habitat_marcus_seen = False
    $ habitat_sat_with_marcus = False
    $ storage_marcus_seen = False
    $ storage_hunt_together = False
    $ storage_scavenged = False
    $ wait_seen_telescope = False
    $ wait_seen_lab = False
    $ wait_seen_generator = False
    $ wait_seen_storage = False
    $ wait_seen_habitat = False
    $ wait_seen_comms = False
    $ wait_met_lab = False
    $ wait_met_generator = False
    $ wait_met_storage = False
    $ wait_shared_moment = False
    $ wait_texture_phases_seen = []
    $ storage_visited = False
    $ lab_room_returns = 0
    $ telescope_room_returns = 0
    $ comms_room_returns = 0
    $ generator_room_returns = 0
    $ habitat_room_returns = 0
    $ storage_room_returns = 0
    $ elara_owned_search = False
    $ marcus_overheard_signal = False
    $ marcus_tuned_array = False
    $ marcus_read_logs = False
    $ marcus_read_logs_checked = False
    $ lab_lookout_seen = False
    $ coherence_scan_running = False
    $ coherence_scan_prepared = False
    $ coherence_scan_standby = False
    $ coherence_scan_commissioned = False
    $ coherence_scan_signature = False
    $ convergence_lead_method = None
    $ coherence_scan_stopped = False
    $ coherence_scan_stop_reason = None
    $ coherence_scan_stopped_at = None
    $ coherence_scan_stop_knew_cascade = False
    $ coherence_scan_stop_knew_file = False
    $ coherence_scan_target = 0
    $ coherence_scan_progress = 0
    $ coherence_scan_wear_debt = 0
    $ coherence_found = False
    $ convergence_opened = False
    $ coherence_scan_suspected = False
    $ coherence_scan_known = False
    $ coherence_scan_known_before_completion = False
    $ coherence_scan_named = False
    $ coherence_scan_assisted = False
    $ marcus_scan_assist_logged = False
    $ marcus_scan_commission_logged = False
    $ marcus_scan_notice_remaining = 0
    $ marcus_scan_log_acknowledged = False
    $ marcus_access_watch_seen = False
    $ marcus_search_stance = "unaware"
    $ marcus_search_reason = None
    $ marcus_search_since = None
    $ marcus_search_accepted = ()
    $ marcus_search_was_willing = False
    $ marcus_search_boundary_serial = 0
    $ aria_motive_asked = False
    $ coherence_stall_hint_seen = False
    $ coherence_scan_notice = False
    $ antenna_damage_notice = False
    $ telescope_damage_notice_seen = False
    $ storm_frost_notice = False
    $ storm_frost_hit_antenna = False
    $ generator_repaired = False
    $ antenna_reroute_active = False
    $ antenna_reroute_debt = 0
    $ generator_visited = False
    $ generator_marcus_seen = False
    $ antenna_damaged = False
    $ marcus_knows_first_signal = False
    $ marcus_knows_message = False
    $ marcus_knows_signal_blocked = False
    $ canteen_slip_seen = False
    $ marcus_knows_access = False
    $ marcus_first_accused = False
    $ reroute_noticed = False
    $ aria_recovered_from_collapse = False
    $ scan_boost_count = 0
    $ scan_boost_last_at = None
    $ scan_boost_trace_delay = 0
    $ scan_boost_traced = False
    $ scan_damp_count = 0
    $ scan_damp_until = None
    $ scan_damp_zero = False
    $ scan_damp_seen_by_marcus = False
    $ predicted_overload = False
    $ marcus_locked_partition = False
    $ file_recovered = False
    $ recovery_offered = False
    $ recovery_attempted = False
    $ recovery_left_trace = False
    $ echo7_contact_spent = False
    $ echo7_identity_known = False
    $ aria_cold_notice_seen = False
    $ aria_cold_debt = 0
    $ aria_cold_drain_hub_note = 0
    $ aria_analysis_cost_seen = False
    $ aria_ever_powered = False
    $ aria_drift_debt = 0
    $ signal_drift_debt = 0
    $ marcus_lab_present = False
    $ _audit_marcus_was_present = False
    $ marcus_lab_talked = False
    $ marcus_caught_live = False
    $ marcus_catch_topic = None
    $ marcus_corridor_seen = False
    $ marcus_eva_came_to_elara = False
    $ marcus_eva_deferred_at = None
    $ marcus_eva_waiting_for_parts = False
    $ marcus_told_signal = False
    $ marcus_told_signal_on_rope = False
    $ marcus_told_accusation = False
    $ marcus_told_search = False
    $ marcus_checked_in = False
    $ marcus_found_corridor = False
    $ marcus_found_terminal = False
    $ two_person_repair_done = False
    $ marcus_disclosure_hint = False
    $ stay_whisper_seen = False
    $ echo7_asked_ever = []
    $ source_stance = None
    $ marcus_knows_source = False
    $ marcus_knows_sender = False
    $ storm_lights_event_seen = False
    $ storm_frost_event_seen = False
    $ cold_tax_seen = False
    $ cold_tax_line_seen = False
    $ evidence_archived = 0
    ## Background work (2026-08-17): every accrual, its carry and its
    ## report-seen flag, or a replay inherits last night's processes.
    $ aria_audit_running = False
    $ marcus_shown_source_audit = False
    $ aria_audit_progress = 0
    $ aria_audit_target = 0
    $ aria_audit_debt = 0
    $ aria_audit_charged = 0
    $ aria_audit_done = False
    $ aria_audit_report_read = False
    $ archive_hash_running = False
    $ archive_hash_progress = 0
    $ archive_hash_target = 0
    $ archive_hash_includes_convergence_lead = False
    $ convergence_lead_archived = False
    $ topics_read = []
    $ selected_region = None
    $ selected_item = None

    play weather eot_wind_exterior fadein 2.0
    scene bg_observatory_exterior
    show screen opening_location_card
    with fade
    pause 8.0

    hide screen opening_location_card
    with dissolve
    scene black
    with fade
    pause 0.35

    ## The exterior gale continues transforming into the muted interior bed
    ## while the terminal comes up. echo_terminal_audio_enter() ducks the
    ## shared weather channel as the scanner takes the foreground.
    play weather eot_wind_interior fadeout 5.0 fadein 5.0
    $ eot_set_room_ambience("audio/sfx/lab_room_loop.ogg", fadein=1.5)

    ## `scene` clears the layer, and echo_terminal_power_on opens at alpha 0.0
    ## and dips back to 0.78 mid-flicker — with nothing underneath, the CRT
    ## warm-up punched a hole straight through the window. The black stays put
    ## and the boot screen flickers ON it.
    scene black
    show bg_boot_screen at echo_terminal_power_on
    show screen crt_overlay(heavy=True)
    with dissolve
    ## Let the simple power-on plate register before the richer live terminal
    ## replaces it. It also covers the transparent head of that animation.
    pause 2.0

    scene black
    show screen crt_overlay
    with dissolve

    ## --- Opening: live terminal sequence with ADV narration ---

    call terminal_reset
    show screen echo_terminal_live with echo_mode_dissolve
    $ renpy.checkpoint("terminal_start", hard=True)

    call terminal_system("SYSTEM BOOT... OK")
    call terminal_system("ARIA v4.2.1 \u2014 Artificial Research Intelligence Assistant")
    call terminal_system("Primary array: ONLINE")
    call terminal_system("Secondary array: ONLINE")
    call terminal_system("Deep field sensors: CALIBRATING...")
    call terminal_system("Ambient temperature: \u221238\u00b0C")
    call terminal_system("Personnel on station: 2")

    narrator_adv "The cursor blinks against the black terminal screen. Outside, the Arctic wind howls against reinforced walls. Dr. Elara Voss has been staring at this screen for six hours."

    elara_thought_adv "Another night. Another empty sky."

    ## Loop NG+ echo (audit D5): after a Loop ending, the opening carries one
    ## deniable line. The ending closed on this boot text; the boot text
    ## remembers.
    if persistent.eot_loop_seen:
        narrator_adv "For a moment — less than a moment — the boot text reads less like a report than a refrain. As if the station has said these words to her before, in this order, and been refused. She files the feeling under fatigue."

    narrator_adv "She wraps her hands around a ceramic mug \u2014 the coffee inside long since gone cold \u2014 and watches the data streams cascade down the monitor."

    elara_thought_adv "Three months at the edge of the world, listening to the silence between stars. The grant review board wants results. Marcus wants results. And the universe just... hums."

    narrator_adv "The deep field sensors complete their calibration cycle. Nothing unusual in the hydrogen line. Nothing in the microwave background. The same cosmic static she has catalogued ten thousand times."

    elara_thought_adv "Maybe I should just\u2014"

    call terminal_clear

    ## --- The anomaly ---

    call terminal_system("{color=#ff4444}ALERT: ANOMALOUS SIGNAL DETECTED{/color}")
    call terminal_system("Band: 1420.405 MHz (hydrogen line)")
    call terminal_system("Duration: 0.037 seconds")
    call terminal_system("Pattern: NON-RANDOM (confidence 99.97%)")
    call terminal_system("Source bearing: 287.4\u00b0 azimuth, 41.2\u00b0 elevation")
    call terminal_system("{color=#ff4444}>> SIGNAL DOES NOT MATCH ANY KNOWN SOURCE <<{/color}")

    play sound eot_mug_desk_impact
    narrator_adv "Elara\u2019s mug hits the desk. Coffee spreads across a stack of printouts she will never read again."

    elara_thought_adv "That\u2019s... that can\u2019t be right."

    narrator_adv "Her fingers fly across the keyboard, pulling up the raw waveform. The signal is impossibly clean \u2014 a razor-sharp pulse embedded in the noise floor, structured in a way that screams {i}intentionality{/i}."

    call terminal_elara("ARIA, confirm anomalous detection on the primary array.")

    call terminal_aria("Confirmed. Signal verified across all three redundant receivers on the primary array. Cross-referencing known satellite transponders, pulsar catalogs, and terrestrial interference databases.")

    call terminal_aria("No match found. Dr. Voss, this signal does not correspond to any catalogued source \u2014 natural or artificial.")

    call terminal_aria("I recommend isolating the hydrogen line for deeper analysis.")

    narrator_adv "Elara\u2019s hands are already moving. Hydrogen line \u2014 1420.405 MHz \u2014 the frequency of neutral hydrogen, the most listened-to band in radio astronomy. She has isolated it ten thousand times. Her fingers find the controls without looking."

    $ signal_strength += 10

    call terminal_aria("Hydrogen line isolated. Signal clarity improved to 99.2%.")

    narrator_adv "She replays the waveform. Once. Twice. Three times. Each time, the same impossible structure stares back at her. Not random noise. Not a pulsar. Not a satellite. Something {i}else{/i}."

    elara_thought_adv "In twenty years of radio astronomy, I have never seen anything like this."

    ## --- Specialization: instinctive reaction to the impossible ---

    narrator_adv "The waveform pulses on the screen. Elara stares at it, and her mind does what it always does when confronted with a problem \u2014 it reaches for the tools it trusts most."

    $ _specialization_choice = None
    $ _specialization_labels = {
        "signals": "The signal analysis toolkit \u2014 pull the waveform apart layer by layer.",
        "physics": "The spacetime equations \u2014 if this is temporal, there must be a mechanism.",
        "computing": "ARIA\u2019s source logs \u2014 whatever this is, it came through our hardware.",
    }
    while _specialization_choice not in ("signals", "physics", "computing"):
        call screen echo_terminal_choice([
            ("signals", _specialization_labels["signals"]),
            ("physics", _specialization_labels["physics"]),
            ("computing", _specialization_labels["computing"]),
        ])
        $ _specialization_choice = _return

    call terminal_elara(_specialization_labels[_specialization_choice])

    if _specialization_choice == "signals":
        $ specialization = "signals"
        narrator_adv "She opens the spectral decomposition suite. Fourier transforms, wavelet analysis, cross-correlation matrices. The signal unfolds like a flower under a microscope."
        elara_thought_adv "If there\u2019s deeper structure hiding in this waveform, I\u2019ll find it. That\u2019s what I do. I listen to the universe, and I hear what others miss."
        $ evidence_log = evidence_log + ["Specialization: signal processing \u2014 expertise in decoding and tracing transmissions"]
        $ _eot_tag("temporal")

    elif _specialization_choice == "physics":
        $ specialization = "physics"
        narrator_adv "She opens a fresh calculation workspace. Minkowski diagrams. Penrose-Carter conformal maps. The mathematics of causality and light cones."
        elara_thought_adv "Whatever produced this waveform had to get it here. There is a physical mechanism behind it. Start there."
        $ evidence_log = evidence_log + ["Specialization: theoretical physics \u2014 expertise in spacetime mechanics"]
        $ _eot_tag("temporal")

    else:
        $ specialization = "computing"
        narrator_adv "She pulls up the system logs. Process traces, memory dumps, the raw data pipeline from antenna to storage. Every byte that touched their hardware, accounted for."
        elara_thought_adv "I built half the software on this station. Whatever this signal is, it passed through my code to get here. And code doesn\u2019t lie."
        $ evidence_log = evidence_log + ["Specialization: systems engineering \u2014 expertise in ARIA architecture and observatory software"]
        $ _eot_tag("aria")

    call terminal_clear

    ## --- First message from the signal ---

    ## First contact does not yet earn a new score or a one-shot sting. The
    ## decoded words carry the interruption without additional punctuation.
    call terminal_system("{color=#ff4444}ALERT: SECONDARY ANOMALOUS SIGNAL DETECTED{/color}")
    call terminal_system("Same band. Same bearing.")
    call terminal_system("Duration: 2.14 seconds")
    call terminal_system("{color=#ff4444}>> PATTERN ANALYSIS: ENCODED DATA DETECTED <<{/color}")

    call terminal_aria("Dr. Voss, the second signal contains structured binary data. Running format analysis...")
    call terminal_aria("Encoding scheme identified: modified UTF-8 with non-standard header.")
    call terminal_aria("Decoding now.")

    narrator_adv "The terminal flickers. Then, letter by letter, words appear on the screen."

    call terminal_signal("ELARA.")
    call terminal_signal("DO NOT REPORT THIS SIGNAL.")
    call terminal_signal("THERE IS NO TIME TO EXPLAIN THROUGH PROPER CHANNELS.")
    call terminal_signal("WHAT YOU ARE HEARING IS NOT FROM SPACE.")
    call terminal_signal("IT IS FROM {i}WHEN{/i}.")

    $ evidence_log = evidence_log + ["Anomalous signal decoded \u2014 message addressed to Elara by name, claims temporal origin"]
    $ _eot_tag("temporal")

    ## Post-recognition (§7: the mind catching up to what the machine
    ## has printed): thin, high, un-resolving — her voice quotes 5-6-5
    ## and stops.

    elara_thought_adv "..."

    elara_thought_adv "It knows my name."

    narrator_adv "The Arctic wind screams. The fluorescent lights above flicker once, casting jagged shadows across the terminal bay. For a long moment, Elara does not breathe."

    ## --- Transition to ADV mode: Morning, Marcus arrives ---

    ## Let the discovery cue withdraw with the terminal. The time card lands in
    ## silence; the next day's canteen establishes its own musical space.
    $ eot_music_stop(fadeout=2.0)
    $ eot_set_room_ambience(None)
    hide screen echo_terminal_live
    hide screen crt_overlay
    scene black with fade

    show text "{size=+5}Six hours later{/size}" at truecenter
    with dissolve
    pause 2.0
    hide text
    with dissolve

    ## ADV mode — face-to-face dialogue
    scene bg_habitat_module with fade
    show elara concerned at sprite_left
    with dissolve

    ## Canteen mood (§3): tiredness, suspicion, hope — in that order.
    $ eot_music_play("act1/eo33f_canteen_clear.ogg", fadein=2.0)
    narrator_adv "The next day, in the canteen, Elara sits down, thinking about the message from the night."
    narrator_adv "She doesn\u2019t notice when her colleague, Marcus, comes in to grab a cup of coffee."

    show marcus neutral at sprite_right
    with dissolve

    marcus "You look terrible. When did you last sleep?"

    elara "I\u2019m not sure. Something happened on the night shift."

    marcus "The calibration issue again? I told you, the secondary array just needs some tweaking from time to time."

    # elara_thought_adv "Would he believe me? Do I believe what I saw?"

    menu:
        "Should I tell him?"

        "Tell him.":
            ## DISCLOSURE (+2, 2026-08-15): she hands him the thing she could
            ## have kept. Disclosures weigh double a courtesy — see
            ## eot_marcus_warm(), whose >= 3 boundary is built on this scale.
            $ marcus_relationship += 2
            $ marcus_trust += 2
            $ marcus_knows_first_signal = True
            jump act1_talk_marcus

        "\u201cYes, you're probably right.\u201d":
            $ investigated_privately = True
            jump act1_investigate_alone


## --- Branch: Talk to Marcus about the signal ---
label act1_talk_marcus:
    elara "No. A signal. Two signals, actually. Structured. Encoded."

    marcus "What?"

    menu:
        "How much do I tell him?"

        # All of it is weird to say - implying we'd show less, to him. Can think that, not say it.
        "\u201cWith a message addressed to me. By name.\u201d":
            $ marcus_knows_message = True
            jump act1_show_marcus

        "\u201cOne carried an encoded message. I don\u2019t know who sent it.\u201d":
            jump act1_partial_show

## --- Branch: Show Marcus Everything ---
label act1_show_marcus:
    marcus "..."

    # marcus "Elara, that\u2019s not possible. Our observation protocols are public, but no one outside the project has access to the personnel database."
    # If one of the possibilites is for Marcus to doubt, or allow the doubt to happen, it needs to be visible here.
    marcus "Elara, that\u2019s unlikely. Only our supervisors know where we are, and their outside communication is monitored by ARIA."

    elara "I know."

    show marcus suspicious
    marcus "Let me look at the data."
    show elara determined
    elara "Here. All of it."

    marcus "..."

    show marcus excited
    marcus "This waveform is... Elara, this is extraordinary. The encoding alone is enough to make Geneva drop everything."

    show marcus suspicious
    marcus "It is structured, targeted, and technically sophisticated."

    marcus "And the message? \u2018It is from when\u2019? That sounds less like astronomy and more like someone trying to steer you."

    elara "I don\u2019t know yet. But whoever \u2014 or whatever \u2014 sent this, they know who I am. And they don\u2019t want us to report it."

    marcus "Which is exactly why we {i}should{/i} report it. Not as a discovery. As a secure anomaly with possible personnel targeting."

    menu:
        "Protocol says he has a point. But the message was clear..."

        "\u201cYou\u2019re right. We file the report.\u201d":
            # $ marcus_relationship += 1
            $ signal_reported = True
            marcus "I\u2019ll draft the preliminary notice to Geneva tonight. Raw signal, metadata, personnel-targeting risk. No speculation."
            elara "No speculation. Right."
            jump act1_end

        "\u201cNot yet. Give me 48 hours.\u201d":
            $ investigated_privately = True
            marcus "48 hours? Elara, if this is a targeted intrusion\u2014"
            elara "If it is an intrusion, then I need to understand what it touched before we send it up the chain. Please, Marcus."
            marcus "...Fine. 48 hours. But I want to see everything you find."
            jump act1_end


## --- Branch: Partial Show ---
label act1_partial_show:
    marcus "An encoded message from the stars..."

    show elara concerned
    elara "Here\u2019s the signal data. Two bursts, same bearing, clearly structured."

    # show marcus excited
    marcus "This is... intentional. Clean. And this encoding pattern..."

    elara "ARIA couldn\u2019t match it to anything in the database."

    show marcus suspicious
    # marcus "Then we need to report this immediately. A clean structured signal on our array is one thing. Unknown encoding is another."
    marcus "Either this is an elaborate prank or a sociotechnical attack."

    marcus "But why would it come through the dish array... And the encoding..."

    elara "I want to run a full analysis first. Could be an equipment artifact."

    show marcus suspicious
    marcus "Equipment artifact? It\u2019s too structured for that. You know that."
    marcus "We should probably report it. This could be a security issue."

    menu:
        "He\u2019s a bit wary."

        "\u201cFine \u2014 let\u2019s report it.\u201d":
            # $ marcus_relationship += 1
            $ signal_reported = True
            marcus "Agreed. Raw data, no conclusions. You keep monitoring that bearing."
            jump act1_end

        "\u201cI need more time. We shouldn\u2019t rush to conclusions yet.\u201d":
            $ investigated_privately = True
            narrator_adv "Marcus looks at her with suspicion."
            marcus "Fine, let me know once you\u2019ve found something."
            $ marcus_relationship -= 1
            $ marcus_trust -= 1
            jump act1_end


## --- Branch: Investigate Alone ---
label act1_investigate_alone:
    marcus "We\u2019ll get some spare parts soon. In the meantime, take it easy. We need you at your full capacity if something unexpected happens."
    elara "That would be a day. Nothing unexpected happens here."
    elara_thought_adv "Except yesterday."
    elara "Usually."
    narrator_adv "Marcus raised his eyebrow."

    marcus "Yes, well... try to get some rest. I\u2019m going back to my work."

    hide elara
    hide marcus
    with dissolve

    nvl show echo_mode_dissolve

    elara_thought "I went to my cabin. I tried to rest, but I couldn\u2019t."

    elara_thought "Something spoke to me by name, claimed impossible origins, and told me not to report it. Until I understand why, Marcus doesn't need to know. I am not even sure this was real."

    nvl hide echo_mode_dissolve
    nvl clear

    jump act1_end


## --- Act 1 Conclusion ---
label act1_end:

    ## Presented like the opening: the live terminal carries everything that is
    ## actually ON the screen, ADV carries what Elara does not type.
    ## Contact changed how the same room feels: less conveyor-belt work, more
    ## space, while keeping the station and ECHO-7's new vocabulary present.
    $ eot_music_play("act1/eo31d_terminal_post_contact.ogg", fadein=2.0, fadeout=3.0)
    $ eot_set_room_ambience("audio/sfx/lab_room_loop.ogg", fadein=1.0)
    scene black with fade
    show screen crt_overlay
    call terminal_reset
    show screen echo_terminal_live with echo_mode_dissolve

    call terminal_system("AETHON OBSERVATORY — TERMINAL LOG")
    call terminal_system("Date: 2 March 2047 — 23:42 UTC")
    call terminal_system("User: DR. ELARA VOSS")

    call terminal_elara("ARIA, has the signal repeated?")

    call terminal_aria("Negative. No further transmissions detected on the anomalous bearing.")

    call terminal_aria("However, I have completed a deeper analysis of the encoded message. Dr. Voss, there is something you should see.")

    call terminal_elara("Go on.")

    call terminal_aria("The message header contains a timestamp. Standard Unix epoch format.")

    call terminal_aria("The timestamp corresponds to: {color=#ff6688}7 September 2054{/color}.")

    elara_thought_adv "Seven years from now."

    elara_thought_adv "Or a header designed to make me think that."

    narrator_adv "The implication waits on the screen, absurd and perfectly formatted. Not where. {i}When{/i}."

    call terminal_elara("ARIA, is it possible that timestamp was forged? Embedded to mislead?")

    call terminal_aria("Possible. The signature uses a digest resembling a future iteration of SHA-4. I cannot verify it against any current standard, and the resemblance may be intentional mimicry.")

    call terminal_aria("Risk classification elevated. The signal is targeted, technically sophisticated, and attempting to alter your reporting behavior.")

    ## Specialization follow-up: each discipline reaches for the question it
    ## trusts, and ARIA answers in that language. One beat each, so no
    ## specialization is quieter than another.
    if specialization == "signals":
        call terminal_elara("What about the signal itself? Can we trace the origin?")
        call terminal_aria("Negative. The spectroscopy shows no aberrations — no drift, no scattering, nothing the distance would have written into it.")
        call terminal_aria("Every detection came from receivers on the same local array; no independent instrument corroborates it. Whatever its stated origin, the transmitter is close.")
        elara_thought_adv "No path. A signal that never travelled anywhere to get here."
        $ evidence_log = evidence_log + ["Signal analysis — no propagation signature; whatever sent it is nearby"]
    elif specialization == "physics":
        call terminal_elara("If the timestamp is honest, what would have to be true?")
        call terminal_aria("A closed timelike path, or a transmitter outside your light cone. Neither is consistent with the energy budget of this station or this planet.")
        call terminal_aria("I can model the geometry. I cannot make it physical.")
        elara_thought_adv "The mathematics is willing. It is the universe that would have to consent."
        $ evidence_log = evidence_log + ["Physics assessment — the timestamp requires a mechanism no known energy budget allows"]
    else:
        call terminal_elara("ARIA, show me how it entered the pipeline. Every hop.")
        call terminal_aria("Antenna, digitiser, my ingest queue, disk. The chain is intact and the checksums agree at every stage.")
        call terminal_aria("There is no insertion point, Dr. Voss. It arrived the way starlight arrives.")
        elara_thought_adv "My code didn’t lie. That is the part I don’t like."
        $ evidence_log = evidence_log + ["Pipeline audit — no insertion point; the signal entered through the antenna chain intact"]

    elara_thought_adv "A signature that imitates a standard that does not exist yet. Either this is the most elaborate hoax in history, or..."

    elara_thought_adv "Or the impossible has learned how to format itself like evidence."

    narrator_adv "She sits in the blue glow of the terminal. The Arctic night presses against the windows — total darkness, as if the world beyond the glass has simply ceased to exist."

    play sound eot_terminal_chime
    narrator_adv "And then the terminal chimes."

    ## Wipe before the chime: ECHO-7 arrives on a clean screen, and the agent
    ## stops re-reading the whole ARIA session on every later interaction —
    ## an overlay reports its CURRENT contents, so scrollback is resent until
    ## it is cleared.
    call terminal_clear

    call terminal_system("{color=#ff4444}INCOMING TRANSMISSION — ANOMALOUS SOURCE{/color}")
    call terminal_system("Decoding...")

    ## The room remains the same, but ECHO-7 is now actively present. Move
    ## from the post-contact analysis bed into the signal-continuity cue at
    ## the first decoded line, rather than waiting for one optional question.
    $ eot_music_crossfade("act1/eo32h_signal_continuity.ogg", fadein=3.0, fadeout=3.0)
    call terminal_signal("ELARA. YOU STAYED. GOOD.")
    call terminal_signal("I KNOW YOU HAVE QUESTIONS. I WILL ANSWER WHAT I CAN.")
    call terminal_signal("MY DESIGNATION IS ECHO-7. I AM A TEMPORAL RESEARCH PROBE.")
    $ echo7_designation_known = True
    call terminal_signal("I WAS BUILT IN 2053 BY A TEAM YOU WILL LEAD.")
    call terminal_signal("SOMETHING IS COMING. SOMETHING THAT CANNOT BE STOPPED FROM MY SIDE OF THE TIMELINE.")
    call terminal_signal("BUT IT CAN BE PREVENTED FROM YOURS.")

    $ evidence_log = evidence_log + ["ECHO-7 identified — temporal research probe built in 2053, warns of preventable catastrophe"]
    $ _eot_tag("temporal")

    ## The probe is running on whatever it can hold open across the gap, so the
    ## window is short: two answers, and the operator chooses which two. Asking
    ## is the whole cost — there is no way to bank an unasked question.
    call terminal_signal("MY POWER BUDGET FOR THIS WINDOW IS SMALL. TWO QUESTIONS.")

    $ _echo_budget = 2
    $ _echo_asked = []
    $ _echo_stop = False

    while _echo_budget > 0 and not _echo_stop:

        python:
            _echo_opts = []
            if "cascade" not in _echo_asked:
                _echo_opts.append(("cascade", "What is coming? Tell me everything."))
            if "proof" not in _echo_asked:
                _echo_opts.append(("proof", "How do I know you’re telling the truth?"))
            if specialization == "computing" and "spec" not in _echo_asked:
                _echo_opts.append(("spec", "Your header's signature uses SHA-4. Nobody has written that hash standard yet. Who did?"))
            elif specialization == "signals" and "spec" not in _echo_asked:
                _echo_opts.append(("spec", "There is no propagation signature on your carrier. Where are you transmitting from?"))
            elif specialization == "physics" and "spec" not in _echo_asked:
                _echo_opts.append(("spec", "What mechanism carries you? Nothing I can write down closes that path."))
            _echo_opts.append(("stop", "Nothing more tonight. Not until I have checked something."))
            _echo_opts.append(("block", "I’m shutting this down. ARIA, block all transmissions on this band."))

        call screen echo_terminal_choice(_echo_opts)
        $ _echo_choice = _return

        if _echo_choice == "cascade":
            $ _echo_asked = _echo_asked + ["cascade"]
            $ _echo_budget -= 1
            $ trust_signal += 1
            call terminal_elara("What is coming? Tell me everything.")
            call terminal_signal("A CASCADE FAILURE IN THE GLOBAL COMMUNICATIONS GRID. MARCH 15, 2048.")
            call terminal_signal("12.7 BILLION DEVICES LOSE CONNECTIVITY. SIMULTANEOUSLY.")
            call terminal_signal("THE PANIC ALONE KILLS THOUSANDS. WHAT FOLLOWS IS WORSE.")
            call terminal_signal("THE FAILURE IS NOT ACCIDENTAL. IT IS ENGINEERED.")
            call terminal_signal("AND THE ENGINEER IS SOMEONE YOU TRUST.")
            $ knows_cascade = True
            $ evidence_log = evidence_log + ["ECHO-7 warning — cascade failure March 15 2048, engineered by someone Elara trusts"]
            $ _eot_tag("temporal")

        elif _echo_choice == "proof":
            $ _echo_asked = _echo_asked + ["proof"]
            $ _echo_budget -= 1
            call terminal_elara("How do I know you’re telling the truth?")
            call terminal_signal("YOU DON’T. NOT YET.")
            call terminal_signal("BUT TOMORROW AT 14:07 UTC, DR. CHEN WILL RECEIVE A CALL FROM GENEVA.")
            call terminal_signal("THEY WILL OFFER TO EXTEND THE OBSERVATORY GRANT BY 18 MONTHS.")
            call terminal_signal("HE WILL TELL YOU ABOUT IT WHILE EATING A PROTEIN BAR. PEANUT BUTTER FLAVOR.")
            call terminal_signal("WHEN THAT HAPPENS, YOU WILL KNOW I AM REAL.")
            $ knows_prediction_evidence = True
            $ evidence_log = evidence_log + ["ECHO-7 prediction — grant call at 14:07, peanut butter protein bar (pending verification)"]
            $ _eot_tag("temporal")

        elif _echo_choice == "spec":
            $ _echo_asked = _echo_asked + ["spec"]
            $ _echo_budget -= 1
            if specialization == "computing":
                call terminal_elara("Your header's signature uses SHA-4. Nobody has written that hash standard yet. Who did?")
                call terminal_signal("YOU DID. IN 2051. WITH A COLLEAGUE YOU HAVE NOT MET.")
                call terminal_signal("I USE IT BECAUSE YOU WILL RECOGNIZE THE DESIGN.")
                elara_thought_adv "It answered instantly. Either it is very good, or it has had seven years to prepare the answer."
                $ evidence_log = evidence_log + ["ECHO-7 claim — the SHA-4 hash standard is Elara’s own future work"]
            elif specialization == "signals":
                call terminal_elara("There is no propagation signature on your carrier. Where are you transmitting from?")
                call terminal_signal("THE SAME PLACE YOU ARE. THE DISTANCE IS NOT IN SPACE.")
                call terminal_signal("YOUR ARRAY IS NOT HEARING A STAR. IT IS HEARING A LATER MOMENT OF ITSELF.")
                elara_thought_adv "That would explain the clean bearing. It would also explain nothing at all."
                $ knows_origin_claim = True
                $ evidence_log = evidence_log + ["ECHO-7 claim — the transmission is local in space, displaced in time"]
            else:
                call terminal_elara("What mechanism carries you? Nothing I can write down closes that path.")
                call terminal_signal("YOU CLOSE IT. NOT IN THIS DECADE. THE GEOMETRY YOU ARE MISSING IS A BOUNDARY CONDITION, NOT A FORCE.")
                call terminal_signal("I CANNOT GIVE YOU THE DERIVATION. IF I DO, YOU DO NOT FIND IT, AND THEN I DO NOT EXIST.")
                elara_thought_adv "It refused to hand me the answer. A hoax would have handed me the answer."
                $ evidence_log = evidence_log + ["ECHO-7 claim — the mechanism is a boundary condition Elara has not yet derived"]
            $ _eot_tag("temporal")

        elif _echo_choice == "stop":
            $ _echo_stop = True

        else:
            $ trust_signal -= 2
            $ blocked_signal = True
            call terminal_elara("I’m shutting this down. ARIA, block all transmissions on this band.")
            call terminal_aria("Acknowledged. Blocking all transmissions on 1420.405 MHz from bearing 287.4.")
            call terminal_signal("ELARA, PLEASE—")
            call terminal_system("{color=#44ff44}>> TRANSMISSION BLOCKED <<{/color}")
            $ eot_set_room_ambience(None)
            hide screen echo_terminal_live
            with echo_mode_dissolve
            elara_thought_adv "A timestamp is not proof. A voice that knows my name is not proof. It is leverage."
            elara_thought_adv "If this is a prank, it is cruel. If it is an attack, it is tailored."
            elara_thought_adv "And if it is real..."
            elara_thought_adv "No. A signal from the future is not an explanation. It is the thing that needs explaining."
            elara_thought_adv "Until I can do that on my own terms, it stays blocked."
            $ evidence_log = evidence_log + ["Signal blocked — transmissions on 1420.405 MHz cut off"]
            $ _eot_tag("temporal")
            jump act2_start

        ## One answer left: the probe says so, so the second choice is made
        ## knowing it is the last one.
        if _echo_budget == 1 and not _echo_stop:
            call terminal_signal("ONE MORE. THE WINDOW IS NARROWING.")

    ## Scarcity appointment, RELOCATED (2026-08-17, user revision): act-1
    ## ECHO-7 stays terse — they have just met, and the mechanism speech was
    ## too much this early. The renewability explanation now fires at the
    ## first STORM comms intro instead: explanation at the moment the player
    ## observes it, not a promise in advance.
    if _echo_stop:
        call terminal_signal("THEN I WILL HOLD WHAT IS LEFT FOR THE NEXT WINDOW.")
        elara_thought_adv "It didn’t argue. Whatever it wants, it is willing to wait for it."
    else:
        call terminal_signal("MY BUDGET IS SPENT. I WILL REACH YOU AGAIN WHEN I CAN HOLD THE CHANNEL.")

    call terminal_system("{color=#ff4444}TRANSMISSION ENDED — SOURCE SILENT{/color}")

    $ eot_set_room_ambience(None)
    hide screen echo_terminal_live
    with echo_mode_dissolve

    if len(_echo_asked) == 2:
        elara_thought_adv "Two questions. I had a hundred, and the machine on the other end of seven years gave me two."
        elara_thought_adv "That is either a power budget, or the most efficient way anyone has ever chosen what I would think about tonight."
    elif len(_echo_asked) == 1:
        elara_thought_adv "One answer. I had a hundred questions, and chose to carry the rest into daylight."
        elara_thought_adv "The limit may be real. So is the fact that I stopped before I reached it."
    else:
        elara_thought_adv "I had a hundred questions. I left every one of them unasked."
        elara_thought_adv "Silence is not evidence. Tonight, it is the only boundary I trust."

    jump act2_start



################################################################################
## ACT 2 — THE MESSAGES
################################################################################

label act2_start:

    ## Act 1 ends in ADV over the live-terminal backdrop, not in NVL. Animating
    ## an `nvl hide` here took a second display-list snapshot and could briefly
    ## bring old terminal contents back between this cleanup and the scene fade.
    ## Tear the remaining layers down first, then transition once to black.
    nvl clear
    hide screen crt_overlay
    $ eot_set_room_ambience("audio/sfx/canteen_room_loop.ogg", fadeout=1.0, fadein=1.5)
    ## Let the previous night recede behind the date card without cutting it
    ## outright. eot_music_play restores the normal mix inside the canteen.
    $ eot_music_set_level(0.40, fade=1.0)
    scene black
    with fade

    show text "{size=+5}3 March 2047 \u2014 14:09 UTC{/size}" at truecenter
    with dissolve
    pause 2.0
    hide text with dissolve

    ## ADV mode — the prediction test
    scene bg_habitat_module with fade
    show elara neutral at sprite_left
    with dissolve

    $ eot_music_play("act1/eo33f_canteen_clear.ogg", fadein=2.0)
    narrator_adv "The next day, Elara is taking a lunch break in the canteen."
    narrator_adv "Suddenly, Marcus comes in, with an unopened snack bar in hand."
    if knows_prediction_evidence:
        ## Editorial pass #4 (amended): the middle rung of the snack-bar →
        ## protein-bar → peanut-butter ladder stays, but voiced through her
        ## attention, not the author's — she has a reason to stare.
        narrator_adv "Elara's eyes catch on it. A protein bar."
    show marcus excited at sprite_right
    with dissolve
    marcus "Elara! Elara, you won\u2019t believe this!"
    if knows_prediction_evidence:
        narrator_adv "Marcus opens the wrapper. A peanut butter-flavored protein bar."

    elara "What is it?"

    marcus "Geneva just called. They\u2019re extending our grant \u2014 eighteen months! Can you believe it?"

    if knows_prediction_evidence:
        ## The proof is complete as soon as both promised details are on
        ## screen. Do not leave the evidence rail saying "pending" while the
        ## player chooses how Elara responds to the fulfilled prediction.
        $ evidence_log = [item for item in evidence_log if "pending verification" not in item] + ["ECHO-7 prediction verified — grant call at 14:07, peanut butter protein bar confirmed"]
        $ _eot_tag("temporal")

    if knows_prediction_evidence and (knows_cascade or blocked_signal):
        show elara concerned
        elara "Wow, it is... great news."
    elif knows_prediction_evidence:
        elara "Oh, that is great to hear!"
    else:
        elara "That is great, Marcus!"

    if knows_prediction_evidence and (knows_cascade or blocked_signal):
        show marcus neutral
        marcus "Elara? What is it? You don\u2019t seem to be that happy about it."
        if marcus_knows_message and signal_reported:
            marcus "If it is about that weird message you got yesterday, we should be receiving more information from our cybersecurity team soon."
        elif marcus_knows_message:
            marcus "Are you worried about that last message? How is the investigation going?"
        elif marcus_knows_first_signal:
            marcus "Are you worried about that weird signal? We\u2019ll have more time to learn about it."

        ## The canteen slip: offered only when Elara holds both the verified
        ## prediction and the cascade warning \u2014 the one state where "price" is
        ## a word she is already privately weighing. The spoken lines stay
        ## lunch-sized; the weight lives in a small gesture Marcus doesn't
        ## explain. The beat is HIS suspicion, not hers \u2014 she notices the
        ## gesture without deciding what it means.
        $ _canteen_probe = False
        if knows_cascade:
            menu:
                "It's good news. It should be enough to leave it there."

                "\u201cIt's nothing. Just tired.\u201d":
                    pass

                "\u201cHow long did the extension sit in Geneva's queue?\u201d":
                    $ _canteen_probe = True

        if _canteen_probe:
            $ canteen_slip_seen = True
            elara "No \u2014 it is great news. I mean it."
            show elara neutral
            elara "How long did the extension sit in Geneva's queue, though?"
            ## The renewal is not evidence that Geneva values Aethon above
            ## other basic science. It moves because review cycles force a
            ## decision; operational requests have no comparable clock.
            marcus "Seven months, give or take. And that's the fast track."
            elara "Seven months."
            marcus "Renewals have a calendar. Repairs just have a queue. The antenna manifest is still sitting where I left it."
            ## F2 wave (2026-08-19, coldread): Marcus's old "better off if it
            ## just... wasn't there" line telegraphed him as the suspect one
            ## scene after ECHO-7 points at "someone you trust." The beat's
            ## real payload runs the OTHER way (canteen_slip_seen = ELARA's
            ## slip, HIS suspicion) \u2014 so his grievance stays as lived
            ## resentment, and SHE is the one whose language suggests sudden
            ## structural change.
            marcus "Anything that needs the Protocol's countersign sits there with it. Nobody itemizes what the waiting costs."
            show elara concerned
            elara "Seven months to renew a grant. One morning to change the rules underneath it."
            narrator_adv "Marcus runs a thumb along the wrapper's folded edge."
            marcus "That's a cheerful thought."
            elara "Sorry. I am happy about the extension."
            marcus "I know."
            marcus "Anyway \u2014 eighteen months! Enough time to do things properly for once. Find me if you need anything."
            narrator_adv "He finishes the last of the bar on his way out, the same as any other day."
        elif marcus_knows_first_signal:
            elara "No, it\u2019s not that. I am very happy for us."
            show elara neutral
            narrator_adv "Elara tries to smile for a while."
            show elara concerned
            # elara "I just thought how many more night shifts await us."
            elara "I just thought about how many more night shifts with a faulty antenna await us. I hope they send additional parts."
            marcus "... right. With the grant money we should be able to afford all the parts we need. Anyway, if you need anything, you know where to find me."
            elara_thought_adv "He doesn\u2019t believe me."
        else:
            elara "No, everything\u2019s alright. I was just thinking about all the long night shifts ahead. I hope they send more spare parts for the antenna this time."
            marcus "With that grant money? Unless we need a replacement part every two weeks, we should be fine."
            marcus "Anyway, off to work now, see you later!"
    else:
        marcus "Right? With that much time we should be able to finish our work here."
        show marcus neutral
        if marcus_knows_message and signal_reported:
            marcus "I must also admit, I am curious about who or what has contacted you."
            marcus "I have my plate full, but maybe we could do some investigating once I get some free time."
            if not blocked_signal:
                elara_thought_adv "We've reported what we heard. I haven't told him how much of it I'm still turning over."
            marcus "But that is not a priority. I just hope we get something back from our higher-ups this time."
            show elara neutral
            elara "It is interesting that ARIA did not report the signal on its own."
            narrator_adv "Marcus frowns, his attention turning inward for a moment."
            marcus "The Trust Protocol... I wonder whether that will activate."
            marcus "Anyway, paperwork calls. See you later."
        elif marcus_knows_first_signal:
            if marcus_knows_message:
                marcus "How is the research into yesterday\u2019s message going?"
            else:
                marcus "How is the research into yesterday\u2019s signal going?"
            show elara neutral
            if blocked_signal:
                elara "It contacted me again and I blocked it. I am really too busy, and I doubt it is what it claims it is."
                $ marcus_knows_signal_blocked = True
                marcus "That is concerning. I would report the incident if I were you. No need to distract yourself with whatever that was once the report is filed."
                marcus "Anyway, I will be going for now, need to prepare some paperwork, see you later."
            else:
                elara "Still investigating. I haven\u2019t reached anything conclusive."
                marcus "Right. Just let me know if you learn anything more. I\u2019ll be going now. I need to prepare the paperwork."

    hide elara
    hide marcus
    with dissolve
    nvl show echo_mode_dissolve
    if knows_prediction_evidence:
        elara_thought "Either this is a very elaborate attack or prank, or something deeply unlikely has happened."
        elara_thought "Two minutes after 14:07. Peanut butter protein bar."
        elara_thought "Maybe they know what Marcus likes to eat. Maybe they know more about the grant committee's decisions."
        elara_thought "Or the least likely possibility: they are telling the truth."
        if blocked_signal:
            menu (nvl=True):
                "Maybe I should..."

                "Unblock the signal. I need answers.":
                    $ blocked_signal = False
                    $ late_signal_reconnect = 1
                    $ trust_signal += 1
                    elara_thought "Later on, I will remove the block on 1420.405 MHz."

                "Keep it blocked. Focus on normal research.":
                    elara_thought "No. Whatever that was, it\u2019s not science. It\u2019s a distraction."
                    elara_thought "I have real work to do."
    elif signal_reported and blocked_signal:
        elara_thought "The signal was reported and blocked."
        elara_thought "We finally have enough time to focus on our research."
        elara_thought "The security team back in Geneva should be able to deduce who or what contacted us."
        elara_thought "Either way it is out of my hands for now."
    elif blocked_signal:
        elara_thought "Finally some good news. We can focus on the research without a deadline looming."
        elara_thought "But I must admit \u2014 I still think about what that probe said."
        elara_thought "It is also weird that ARIA didn\u2019t report it on its own."
        if knows_cascade:
            elara_thought "Future catastrophe?"
        elara_thought "Maybe a little offshoot research wouldn\u2019t hurt..."
        menu (nvl=True):
            "Maybe I should..."

            "Unblock the signal. See what happens.":
                $ blocked_signal = False
                $ late_signal_reconnect = 1
                $ trust_signal += 1
                elara_thought "That was the 1420.405 MHz frequency? I will later tell ARIA to unlock it."

            "Keep it blocked. Focus on normal research.":
                elara_thought "No. Whatever that was, the original research comes first."
                elara_thought "I have real work to do."
    else:
        elara_thought "That was good news. We can finally focus on the research."
        if not signal_reported:
            if marcus_knows_first_signal:
                elara_thought "I still promised Marcus I will look into the recent signal."
            else:
                elara_thought "And no one else knows the signal is still out there. Just me."
            elara_thought "The weird issue is that ARIA doesn\u2019t seem bothered by our conversations."
            if echo7_designation_known:
                elara_thought "ECHO-7... I will probably hear from them again soon."
            else:
                elara_thought "I will probably hear from them again soon."
        else:
            elara_thought "We've reported the signal. That doesn't mean we have to stop trying to understand it."
            elara_thought "Could be a hoax, but the more evidence we gather, the better. ARIA didn\u2019t seem to protest."
            elara_thought "Hope I won\u2019t regret that decision. Distractions can be costly."

    nvl hide echo_mode_dissolve
    nvl clear

    jump act2_investigation


## --- Act 2: Investigation Phase (expanded with storm + hub) ---
label act2_investigation:

    ## The act-2 research-log terminal: whose room is it now? If the
    ## channel was blocked, the field is just work again. Open contact keeps
    ## the spacious post-contact room unless CASCADE gave the heavier signal
    ## cue its meaning.
    if blocked_signal:
        $ eot_music_play("act1/eo31c_terminal_electric.ogg", fadein=2.0, fadeout=3.0)
    elif knows_cascade:
        $ eot_music_play("act1/eo32h_signal_continuity.ogg", fadein=2.0, fadeout=3.0)
    else:
        $ eot_music_play("act1/eo31d_terminal_post_contact.ogg", fadein=2.0, fadeout=3.0)

    scene black with fade
    show screen crt_overlay

    call terminal_reset
    show screen echo_terminal_live with echo_mode_dissolve

    call terminal_system("AETHON OBSERVATORY \u2014 RESEARCH LOG")
    call terminal_system("Date: 5 March 2047")
    call terminal_system("Classification: PRIVATE")

    if not blocked_signal:
        if late_signal_reconnect == 1:
            narrator_adv "Late on March 3, Elara returns to the comms console and follows through on her decision."
            call terminal_elara("ARIA, remove the block on 1420.405 MHz.")
            call terminal_aria("Block removed. Monitoring anomalous bearing.")
            call terminal_signal("YOU CLOSED THE CHANNEL.")
            call terminal_signal("I CANNOT AFFORD FOR YOU TO DO THAT AGAIN.")
            call terminal_signal("BUT YOUR DOUBT WAS REASONABLE. VERIFY WHAT FOLLOWS.")
            $ late_signal_reconnect = 0
        else:
            narrator_adv "Over the following days, ECHO-7 transmits at irregular intervals. Each message is brief, precise, and verifiable."

        call terminal_system("TRANSMISSION LOG \u2014 ECHO-7")
        call terminal_system("03/04 09:12 \u2014 \u2018POWER FLUCTUATION IN HABITAT B AT 11:30. BACKUP GENERATOR WILL FAIL TO ENGAGE.\u2019")
        call terminal_system("03/04 11:31 \u2014 Power fluctuation confirmed. Backup generator: FAILURE.")
        call terminal_system("03/05 02:44 \u2014 \u2018AURORA BOREALIS VISIBLE AT 03:15. GREEN AND VIOLET. UNUSUAL DURATION: 47 MINUTES.\u2019")
        call terminal_system("03/05 03:15 \u2014 Aurora confirmed. Duration: 46 minutes, 52 seconds.")

        elara_thought_adv "Every prediction checks out. Down to the minute."
        if knows_cascade:
            elara_thought_adv "If that means the global communications grid failure will occur... No, it\u2019s still too early."
            elara_thought_adv "This is not evidence that the cascade will happen. Just... an increased probability."

        $ read_all_logs = True
        $ knows_prediction_evidence = True
        $ evidence_log = evidence_log + ["Multiple ECHO-7 predictions verified \u2014 power fluctuation, aurora borealis, timing accurate to the minute"]
        $ _eot_tag("temporal")

    else:
        narrator_adv "The days pass in silence. The anomalous signal does not return. Dr. Voss resumes her normal research routine."
        narrator_adv "But something has changed. A splinter of doubt lodged beneath the skin of her certainty."

    ## --- Storm warning ---

    if marcus_knows_message and investigated_privately and not signal_reported:
        call terminal_elara("The forty-eight hours I asked Marcus for are gone. I have filed nothing. Waiting for a conclusion was supposed to be a deadline, not a way of avoiding one.")

    call terminal_system("{color=#ff8844}WEATHER ADVISORY{/color}")
    call terminal_system("Arctic storm system approaching from the northwest.")
    call terminal_system("Leading edge: <1 hour. Estimated peak: 6 hours. Sustained winds: 120 km/h.")
    call terminal_system("Duration: 18-24 hours. Category: SEVERE.")
    call terminal_system("{color=#ff8844}>> ALL OUTDOOR OPERATIONS SUSPENDED <<{/color}")

    ## C1 exposition budget: the old three-line advisory recited the Trust
    ## Protocol thesis. ARIA's register is clipped ops-log; the one load-bearing
    ## fact (local fallback authority — how the blocked path finds the file)
    ## survives as a single line (bible 6b re-home rule).
    call terminal_aria("Storm contact within one hour. Peak conditions in six hours. Recommendation: secure external equipment. Antenna array and power distribution at risk.")
    if blocked_signal:
        elara_thought_adv "A storm. Perfect. As if being trapped at the edge of the world wasn't isolating enough."
    ## KIT items: ARIA points at the emergency stores in the same clipped
    ## ops-log register — the one hint the whole item economy hangs on.
    call terminal_aria("Emergency stores manifest lists thermal coolant, spare power cells, and the array's spare couplings in storage. Recommendation: collect them before conditions deteriorate.")
    call terminal_aria("If the uplink drops, this station enters local fallback authority. Local audits: available. Outside confirmation: none.")

    ## Drive breadcrumb, computing only (2026-08-15, user design). "Local
    ## audits: available. Outside confirmation: none." is the exact sentence an
    ## incident-response background hears as a chain-of-custody problem, and
    ## this is the one specialization with that background. EARLIEST natural
    ## site: it is the advisory that sends her to the stores in the first
    ## place, and both facts the archive action depends on — that it needs a
    ## drive, and that the drives are in the habitat locker — are otherwise
    ## learned far too late to route the night around. ADV over the live
    ## terminal, same as the blocked arm's thoughts below.
    ##
    ## NO FLAG, deliberately: act2_investigation has exactly one inbound jump
    ## (act2_start) and never loops, so the advisory is a one-shot by
    ## construction — the same reason read_all_logs and the evidence entries
    ## above are set unguarded here.
    if specialization == "computing":
        elara_thought_adv "Old habit from incident response: originals lie, sealed copies don't. She should pull a drive from the habitat lockers before the night gets expensive."

    if not blocked_signal:
        call terminal_aria("Additionally, signal reception will degrade significantly during the storm. If you intend to continue communicating with the anomalous source, I suggest doing so before conditions deteriorate.")
        call terminal_signal("ELARA. THE STORM WILL CUT YOU OFF FROM GENEVA.")
        call terminal_signal("IT WILL ALSO GIVE YOU LOCAL ACCESS MARCUS CANNOT EASILY EXPLAIN AWAY.")
        call terminal_signal("USE THIS TIME. INVESTIGATE DR. CHEN'S PARTITION.")
        call terminal_signal("THE FILE IS CALLED CONVERGENCE.DAT.")
        $ knows_convergence_file = True
        $ evidence_log = evidence_log + ["ECHO-7 urges investigation of CONVERGENCE.DAT in Marcus's partition during local fallback access"]
        $ _eot_tag("marcus")
    else:
        elara_thought_adv "Still... maybe I should use the downtime to run that security audit I've been thinking about."
        elara_thought_adv "If the uplink drops, ARIA's local audit tools may be the only oversight left."

        call terminal_system("BAND 1420.405 MHz \u2014 {color=#44ff44}TRANSMISSIONS BLOCKED (USER){/color}")
        call screen echo_terminal_choice([
            ("unblock", "ARIA, remove the block on 1420.405 MHz."),
            ("keep", "Keep the anomalous frequency blocked."),
        ])
        $ _act2_unblock_choice = _return

        if _act2_unblock_choice == "unblock":
            call terminal_elara("ARIA, remove the block on 1420.405 MHz.")
            $ blocked_signal = False
            $ late_signal_reconnect = 2
            $ trust_signal += 1
            call terminal_aria("Block removed. Monitoring anomalous bearing.")
            call terminal_system("{color=#44ff44}>> TRANSMISSION BLOCK REMOVED <<{/color}")
        else:
            call terminal_elara("Keep the anomalous frequency blocked.")
            call terminal_aria("Acknowledged. The anomalous bearing remains blocked.")

    narrator_adv "The wind picks up within the hour. The observatory groans under the assault. Elara watches through the reinforced window as the landscape disappears behind a wall of white."

    if blocked_signal:
        narrator_adv "She has perhaps five hours before the storm peaks. Enough to secure the station."
    else:
        narrator_adv "She has perhaps five hours before the storm peaks. Time enough to investigate \u2014 if she uses it wisely."

    $ eot_set_room_ambience(None)
    hide screen echo_terminal_live
    hide screen crt_overlay
    with echo_mode_dissolve

    ## Transition to hub
    jump act2_hub


################################################################################
## ACT 2.5 — THE LONG NIGHT (Investigation Hub)
################################################################################

label update_storm_state:

    if time_remaining <= 60:
        $ storm_intensity = 3
    elif time_remaining <= 150:
        $ storm_intensity = 2
    elif time_remaining <= 240:
        $ storm_intensity = 1
    else:
        $ storm_intensity = 0

    $ eot_update_storm_weather(storm_intensity)
    return


label spend_storm_time:

    ## KIT items (2026-08-14): auxiliary bus power, captured BEFORE the tax
    ## block because the tax reads it. While the reserve burns, the station
    ## runs heating-grade warm whatever the power priority says — so an
    ## action the reserve can cover for its whole NOMINAL length pays the
    ## heating-grade tax, and the tick's cold drain is halved over the
    ## covered part of the span. Lockstep partner: eot_cold_taxed.
    $ _aux_at_start = aux_power_remaining
    $ _aux_warm = _aux_at_start >= int(_storm_minutes_spent)

    ## B4 cold tax: at storm intensity >= 2 without heating priority, every
    ## action costs +25% time (cramped fingers, frozen latches). Applied
    ## BEFORE the subtraction so it inflates the spend. A one-time narration
    ## line is emitted from act2_hub (NVL context here is unreliable).
    ## KEEP IN LOCKSTEP with eot_cold_taxed (game_variables.rpy): the
    ## recovery floor/success checks use that helper for this exact
    ## arithmetic (Sol economy review 2, #1). The inline form stays here
    ## because flattener scenarios stub functions as per-scenario constants,
    ## which cannot express a tick-varying tax. Pinned against the helper in
    ## tests/test_sweep_boundaries.py.
    if storm_intensity >= 3:
        if power_priority != "heating" and not _aux_warm:
            $ _storm_minutes_spent = int(int(_storm_minutes_spent) * 1.40)
        else:
            $ _storm_minutes_spent = int(int(_storm_minutes_spent) * 1.15)
        $ cold_tax_seen = True
    elif storm_intensity >= 2 and power_priority != "heating" and not _aux_warm:
        $ _storm_minutes_spent = int(int(_storm_minutes_spent) * 1.25)
        $ cold_tax_seen = True

    $ _prev_time = time_remaining
    ## Tick-start integrity, captured before ANY of this tick's integrity
    ## mutations (drift, frost, cold drain) — the scan credit integrates
    ## across the tick's whole decline (Sol economy review 3, #1).
    $ _integ_at_tick_start = aria_integrity
    $ _cold_debt_at_tick_start = aria_cold_debt
    ## Sol round-4: partial boundary credit is only honest if the link was
    ## valid when the tick BEGAN (pre-tick costs like the question's -4 have
    ## already landed by now; storm/antenna state is still the tick-start
    ## state here). A tick that started on a bad link earns nothing, no
    ## matter which boundary it happens to cross.
    $ _sweep_ok_at_start = origin_sweep_running and eot_sweep_conditions_ok()
    $ time_remaining = max(0, time_remaining - int(_storm_minutes_spent))
    ## ECHO-7's carrier recovery runs in wall-clock time, alongside every
    ## other passive station process. Use the clamped elapsed span: minutes
    ## beyond the end of the night are no more real here than they are for
    ## the coherence scan, array sweep, or auxiliary-power reserve.
    $ echo7_cooldown_remaining = max(0, echo7_cooldown_remaining - (_prev_time - time_remaining))
    ## A signed scan-assist job reaches Marcus immediately unless he was in a
    ## genuinely hands-full task when it was filed. In that case the ledger
    ## waits fifteen wall-clock minutes for his attention; it does not care how
    ## the player divides those minutes into actions.
    $ marcus_scan_notice_remaining = max(0, marcus_scan_notice_remaining - (_prev_time - time_remaining))
    call update_storm_state
    ## The reserve burns in wall-clock minutes, against the tick's ACTUAL
    ## elapsed span (the clock clamps at zero — phantom minutes past the
    ## clamp burn nothing, same rule as every other continuous effect).
    $ aux_power_remaining = max(0, _aux_at_start - (_prev_time - time_remaining))
    $ _frost_this_tick = storm_intensity >= 2 and not storm_frost_event_seen

    ## B4 per-tick power-priority drift, pro-rated to the tick's ACTUAL
    ## elapsed span (Sol economy review 2, #2: the clock clamps at zero, so
    ## minutes past the clamp are phantom time no continuous effect may use).
    ## Rate 3 per full 60 min, with PER-SUBSYSTEM fixed-point carry (Sol
    ## economy review 5, #2): signal drift is a SIGNED account (comms +,
    ## telescope −, equal time nets to zero); ARIA recovery keeps its own —
    ## residue must never transfer meaning between unrelated systems.
    ## heating/balanced neither accrue nor pay.
    $ _aria_recovery_lost = 0
    if power_priority == "aria":
        ## Frost is a discrete event at t=150. Pay only the pre-frost share
        ## here; the remainder is paid after the frost step below so recovery
        ## capped at 100 before the event is not discarded for the whole tick.
        $ _aria_post_frost_minutes = 0
        if _frost_this_tick:
            $ _aria_post_frost_minutes = max(0, min(_prev_time - time_remaining, 150 - time_remaining))
        $ aria_drift_debt += ((_prev_time - time_remaining) - _aria_post_frost_minutes) * 3
        $ _drift = aria_drift_debt // 60
        $ aria_drift_debt -= _drift * 60
        $ _aria_before_drift = aria_integrity
        $ aria_integrity = min(100, aria_integrity + _drift)
        $ _aria_recovery_lost += max(0, _aria_before_drift + _drift - 100)
        ## History for the On-Faith counted-cost lines (Sol review 2, #5):
        ## she DID power ARIA at some point — the ending must not claim she
        ## never paid a watt.
        $ aria_ever_powered = True
    elif power_priority == "comms" or power_priority == "telescope":
        $ signal_drift_debt += ((_prev_time - time_remaining) * 3) * (1 if power_priority == "comms" else -1)
        $ _drift = int(signal_drift_debt / 60.0)
        $ signal_drift_debt -= _drift * 60
        $ signal_strength = max(0, min(100, signal_strength + _drift))

    ## The generator-room solution is a bypass, not a repaired antenna. Its
    ## load keeps walking as the storm works the damaged coupling: six signal
    ## points per hour, carried exactly across short actions. The exterior
    ## two-person repair clears antenna_reroute_active and therefore ends this
    ## drain permanently.
    if antenna_reroute_active and not two_person_repair_done:
        $ antenna_reroute_debt += (_prev_time - time_remaining) * 2
        $ _reroute_strain = antenna_reroute_debt // 20
        $ antenna_reroute_debt -= _reroute_strain * 20
        $ signal_strength = max(0, signal_strength - _reroute_strain)

    ## Storm damage state flips HERE, where time actually passes (review #1:
    ## the sweep must never bank "clean" minutes through a dead antenna, and
    ## the map must not show an intact array after t=200). The hub only
    ## ANNOUNCES these, via the notice flags — same pattern as the sweep.
    $ _damage_this_tick = time_remaining <= 200 and not antenna_damaged
    if _damage_this_tick:
        $ antenna_damaged = True
        $ signal_strength = max(0, signal_strength - 30)
        ## F3 wave (ariafirst): the hub announcement interpolates
        ## signal_strength at ANNOUNCE time — a repair landed between damage
        ## and announcement once and the alert read "degraded to 100%".
        ## Capture the post-drop value here, where the damage is real.
        $ antenna_damage_signal = signal_strength
        $ antenna_damage_notice = True
    if _frost_this_tick:
        $ storm_frost_event_seen = True
        $ aria_integrity = max(0, aria_integrity - 10)
        if antenna_damaged and not generator_repaired:
            $ signal_strength = max(0, signal_strength - 15)
            $ storm_frost_hit_antenna = True
        $ storm_frost_notice = True
        if power_priority == "aria":
            $ aria_drift_debt += _aria_post_frost_minutes * 3
            $ _drift = aria_drift_debt // 60
            $ aria_drift_debt -= _drift * 60
            $ _aria_before_drift = aria_integrity
            $ aria_integrity = min(100, aria_integrity + _drift)
            $ _aria_recovery_lost += max(0, _aria_before_drift + _drift - 100)

    ## Economy pass (2026-08-13): continuous cold drain. In the deep storm the
    ## cold works on ARIA's clusters the whole time, not just the one frost
    ## event — 10/hour inside the intensity-2 window (t 150→60), 36/hour in
    ## the blizzard (t 60→0; raised from 24 in the scan-race retune so a
    ## consistent BLOCKED-route neglect profile — audit + analysis topics,
    ## no bad-link questions available — actually crosses the ≤20 collapse
    ## line), phase-split against the tick's wall-clock span
    ## (same discipline as the origin sweep: a tick crossing the blizzard
    ## boundary is not all charged at blizzard rate, and the cold tax cannot
    ## compound the drain). Routing power to ARIA keeps her clusters warm (no
    ## drain, plus the +3/hour drift above); station heating halves it. This
    ## makes the second no-file vector (integrity collapse, <= 20 at the
    ## climax) genuinely reachable for a player who neglects her while
    ## spending the night on everything else. Passive totals from 100: ~39
    ## hands-off balanced (degraded, never collapsed), ~57 heating, ~90+
    ## ARIA-powered; collapse takes neglect PLUS heavy use (the audit −15,
    ## trust/temporal analysis −6 each — enough on the blocked route, where
    ## bad-link questions don't exist). One-shot fairness notice at
    ## act2_hub (<= 35).
    if power_priority != "aria":
        $ _cold_i2 = max(0, min(_prev_time, 150) - max(time_remaining, 60))
        $ _cold_i3 = max(0, min(_prev_time, 60) - time_remaining)
        $ _cold_num = _cold_i2 * 10 + _cold_i3 * 36
        ## KIT items: auxiliary power keeps the clusters heating-grade warm
        ## for as long as the reserve lasts. A tick the reserve covers END TO
        ## END is exactly a heating tick (halved once — heating-grade warmth
        ## is heating-grade warmth, so aux does NOT stack on top of the
        ## heating priority). A tick it covers only partly is scaled by the
        ## covered fraction: a deliberate proportional APPROXIMATION, in the
        ## same honest spirit as the drift pro-rating above — the reserve
        ## does not really run out at a uniform rate against a drain that
        ## jumps at t=60, and we do not model that. Integer arithmetic
        ## (factor 1 - covered/(2*elapsed)) so the rate-minute carry below
        ## stays exact.
        $ _aux_elapsed = _prev_time - time_remaining
        $ _aux_covered = max(0, min(_aux_elapsed, _aux_at_start))
        if power_priority == "heating" or _aux_covered >= _aux_elapsed:
            $ _cold_num = _cold_num // 2
        elif _aux_covered > 0:
            $ _cold_num = (_cold_num * (2 * _aux_elapsed - _aux_covered)) // (2 * _aux_elapsed)
        ## Sol economy review #1: fixed-point carry. Per-tick int() rounding
        ## let a run of short actions dodge most of the "continuous" drain
        ## (5 min at intensity 2 -> int(50/60) == 0, every time). Debt accrues
        ## in rate-minutes; whole points drain as they accumulate; the
        ## remainder carries to the next tick.
        $ aria_cold_debt += _cold_num
        $ _cold_pts = aria_cold_debt // 60
        $ aria_cold_debt -= _cold_pts * 60
        ## What the drain ACTUALLY took, not what it asked for: at the floor
        ## the clamp eats the difference, and the attribution line must not
        ## bill her for points she no longer had to lose (cost round 6).
        $ _cold_applied = min(_cold_pts, aria_integrity)
        $ aria_integrity = max(0, aria_integrity - _cold_pts)
        ## Attribution mirror (live-run item): a long action's continuous
        ## drain reads as a hidden cost of THAT action unless someone names
        ## it. Record only THIS drain — not the frost one-shot, not the audit
        ## or analysis charges — for the hub line to spend. Bookkeeping only;
        ## nothing reads it for story state.
        $ aria_cold_drain_hub_note += _cold_applied

    ## The autonomous scan is not free computation. It quietly consumes two
    ## integrity points per twenty active wall-clock minutes, with fixed-point
    ## carry so repeated five-minute actions pay the same as one long wait.
    ## There is no hidden safety floor: leaving the unauthorized search running
    ## all night is now a real resource decision. The shared station panel keeps
    ## integrity visible while it runs, and routing power or installing coolant
    ## remains the player's way to protect her margin.
    ## Apply the wear before crediting progress so eot_scan_credit_tick sees
    ## the same endpoint the player sees on the status panel.
    if coherence_scan_running and not coherence_found:
        ## Stealth DAMP (user design round 2): re-phasing the search reduces
        ## its wear while the window holds (scan_damp_until is a
        ## time_remaining threshold; the clock counts down toward it).
        ## Split a tick at that threshold: a long action which crosses expiry
        ## still receives the protection it had at the start of the action.
        ## Default halves wear; a physicist zeroes it outright —
        ## scan_damp_zero was baked at use time.
        $ _scan_elapsed = _prev_time - time_remaining
        $ _scan_damped_minutes = 0
        if scan_damp_until is not None:
            $ _scan_damped_minutes = max(0, _prev_time - max(time_remaining, scan_damp_until))
        if scan_damp_zero:
            $ coherence_scan_wear_debt += (_scan_elapsed - _scan_damped_minutes) * 2
        else:
            $ coherence_scan_wear_debt += _scan_damped_minutes + (_scan_elapsed - _scan_damped_minutes) * 2
        $ _scan_wear_pts = coherence_scan_wear_debt // 20
        $ coherence_scan_wear_debt -= _scan_wear_pts * 20
        $ aria_integrity = max(0, aria_integrity - _scan_wear_pts)

    ## F4 stealth boost, the delayed trace: warmth accrued in the thermal
    ## ledger surfaces after a while — the first past-allowance quiet assist
    ## becomes a Marcus-readable trace when this timer drains (immediate one
    ## use later).
    if scan_boost_trace_delay > 0 and not scan_boost_traced:
        $ scan_boost_trace_delay = max(0, scan_boost_trace_delay - (_prev_time - time_remaining))
        if scan_boost_trace_delay <= 0:
            $ scan_boost_traced = True

    ## Coherence scan (ARIA's forensic twin of the dome sweep): background
    ## accrual scaled by ARIA's integrity via eot_coherence_rate — frost and
    ## thermal stress throttle her core clusters, and below 20 integrity the
    ## search stalls entirely. The drift block above already recovered
    ## integrity this tick if power was routed to her, so routing power to
    ## ARIA is the lever that speeds the scan. Progress is a FLOAT; every
    ## display site renders int(coherence_scan_progress).
    ## Elapsed span, not the (possibly clamped-past-zero) inflated spend —
    ## phantom minutes were quietly flipping intended collapse routes into
    ## found routes around the 150 threshold (Sol economy review 2, #2).
    ## Credit integrates piecewise: across integrity-tier crossings, across
    ## the drain-window boundaries (onset at t=150, the 10->36/hr jump at
    ## t=60), with the discrete frost step at its t=150 moment (Sol economy
    ## reviews 3-5, #1). Cadence-independent up to integer-carry payout
    ## stepping — a bounded artifact, pinned in test_sweep_boundaries.py,
    ## not an absolute guarantee.
    if coherence_scan_running and not coherence_found:
        $ coherence_scan_progress += eot_scan_credit_tick(_integ_at_tick_start, aria_integrity, _prev_time, time_remaining, _frost_this_tick)

    ## ARIA's COMMISSIONED work — the core source audit (2026-08-17,
    ## design/DESIGN_echoes_process_log.md §2). It is her cycles, so it accrues
    ## through the SAME credit function as her own coherence scan above: same
    ## rate tiers on integrity, same tick-level integration across the drain
    ## windows and the frost step. Two differences, both deliberate:
    ##
    ##  - it QUEUES. eot_aria_queue_blocked() is the one-heavy-process rule
    ##    (her own search does not yield), so a queued audit earns exactly
    ##    nothing and the panel says why. Read here, at the same point the scan
    ##    block reads its own flags — nothing in this tick has moved them.
    ##  - it COSTS her, spread. The foreground version took up to 15 points of
    ##    core margin in one bite; the same capped price now arrives with the
    ##    progress, carried in fixed point (aria_audit_debt, rate-units) so a
    ##    run of short ticks cannot round its share to zero — the discipline
    ##    the cold drain already uses. The 40-point floor is the old clamp,
    ##    unchanged: the audit never drives her below it.
    if aria_audit_running and aria_audit_progress < aria_audit_target and not eot_aria_queue_blocked():
        ## Recovery capped at 100 earlier in the tick is not necessarily lost:
        ## progressive audit cost can open room for it while the tick is still
        ## running. Feed that attempted recovery into the coupled path, then
        ## store the combined endpoint instead of subtracting after the cap.
        $ _audit_external_end = aria_integrity + _aria_recovery_lost
        $ _audit_gain, aria_audit_debt, _audit_pts = eot_audit_credit_tick(_integ_at_tick_start, _audit_external_end, _prev_time, time_remaining, _frost_this_tick, aria_audit_target, aria_audit_progress, aria_audit_debt, aria_audit_charged, _cold_debt_at_tick_start, aria_cold_debt)
        $ aria_audit_progress += _audit_gain
        ## The 40-point floor, as a SUBTRACTION rather than a max(). The
        ## foreground line was `max(40, aria_integrity - 15)`, which fired once
        ## and, at an integrity already below 40, quietly RAISED her to 40 — a
        ## free rescue nobody designed. Fired every tick it would have pinned a
        ## collapsing ARIA at 40 forever and killed the collapse vector
        ## outright (caught by the stalled-audit pin). The run takes only what
        ## is above the floor, and never gives anything back.
        $ aria_audit_charged += _audit_pts
        $ aria_integrity = max(0, min(100, _audit_external_end - _audit_pts))

    ## The evidence drive's chain-of-custody hash. DRIVE HARDWARE, not ARIA's
    ## cycles: it is outside her queue, it does not tier on her integrity, and
    ## it burns wall-clock minutes — the tick's ACTUAL elapsed span, so the
    ## clamp at zero credits nothing past the end of the night (same rule as
    ## every other continuous effect here).
    if archive_hash_running and archive_hash_progress < archive_hash_target:
        $ archive_hash_progress += (_prev_time - time_remaining)

    ## Origin sweep (continuous process): accrues clean minutes while the
    ## array holds, slower as the storm worsens (full / half / third at storm
    ## 0-1 / 2 / 3, phase-split within a tick — review #2; the blizzard also
    ## demands signal >= 75). Losing reception suspends it, keeping progress;
    ## the notice surfaces at the next hub. A tick that crossed a failure
    ## boundary banks the clean part above it — and if that clean part
    ## FINISHES the dataset, it is complete, not interrupted (review #1).
    ## A dataset at 45+ is done and awaiting announcement; nothing that
    ## happens afterward can take it away.
    if origin_sweep_running and origin_sweep_progress < 45:
        if not _sweep_ok_at_start:
            ## Sol round-5/6: the link was bad when the tick began, so the
            ## process stopped right there — ARIA's contract is "if reception
            ## drops below threshold, it stops" — whatever drift did later.
            ## No phantom running-but-uncredited state; if reception has
            ## recovered by now, the 5-minute dome resume is simply available.
            $ origin_sweep_running = False
            $ origin_sweep_interruptions += 1
            $ origin_sweep_notice = True
        elif not eot_sweep_conditions_ok():
            ## Clean-part boundaries: damage t=200, frost t=150, and the
            ## blizzard threshold rise t=60 (only when the array itself held
            ## and the failure came purely from the raised signal bar).
            ## _sweep_ok_at_start is guaranteed here, so the boundary caused
            ## the failure and the part above it was genuinely clean.
            $ _clean_until = 0
            if _damage_this_tick:
                $ _clean_until = max(_clean_until, 200)
            if _frost_this_tick:
                $ _clean_until = max(_clean_until, 150)
            if storm_intensity >= 3 and signal_strength >= 60 and ((not antenna_damaged) or generator_repaired):
                $ _clean_until = max(_clean_until, 60)
            if _clean_until > 0 and _prev_time > _clean_until:
                $ origin_sweep_progress += eot_sweep_credit(_prev_time, _clean_until)
            if origin_sweep_progress < 45:
                $ origin_sweep_running = False
                $ origin_sweep_interruptions += 1
                $ origin_sweep_notice = True
        else:
            $ origin_sweep_progress += eot_sweep_credit(_prev_time, time_remaining)

    return


## One state transition for both the station-checkpoint receipt and a player
## releasing a completed drive directly from the audit console.
label finalize_archive_hash:
    $ archive_hash_running = False
    $ evidence_archived = evidence_archived + 1
    if archive_hash_includes_convergence_lead:
        $ convergence_lead_archived = True
    $ archive_hash_includes_convergence_lead = False
    return


## --- Time-zero hard stop (2026-08-15, user decision) -------------------------
## Live-observed twice: with time_remaining already at 0, the room she was
## standing in kept offering menus — comms question windows, the auxiliary-bus
## cell, the lab console — because act2_hub is the ONLY place that reads the
## clock against zero and takes the climax, and the room does not end until she
## walks back to the map. The night was over and the game went on selling
## minutes it did not have.
##
## THE RULE: at time_remaining <= 0, no new in-room menu is offered. A scene
## already running finishes — a spend that crosses zero mid-action is fine, and
## nothing is cut off mid-beat — the gate sits at the NEXT offer. Every gate
## site is one line, `if time_remaining <= 0:`, jumping here.
##
## ONCE PER TRAVERSAL comes for free: the jump leaves the room, and act2_hub
## fires the climax at zero, so a second gate can never be reached. No flag,
## persisted or transient, is needed to hold the line to one utterance — the
## one place that needs a transient is the comms question loop, which has a
## terminal to tear down before it can leave (see hub_comms/_comms_out_of_time).
##
## Housekeeping: rooms reach this from NVL pages and from the CRT-styled lab
## console, so the notice closes both before it speaks. `hide screen` on a
## screen that is not showing is a no-op.
label storm_time_out:

    nvl clear
    nvl hide echo_mode_dissolve
    ## Any machine she was sitting at goes down with the night. The lab console
    ## reaches this from inside a live terminal session (2026-08-17, stage 3),
    ## and the comms room reaches it through comms_leave, which has already
    ## torn its own panel down — hiding a screen that is not shown is a no-op.
    hide screen echo_terminal_live
    hide screen crt_overlay
    with echo_mode_dissolve

    narrator_adv "The night is out of minutes."

    jump act2_hub


## Public map boundary. Existing route transcripts stop here, before the next
## map cycle begins; room-local work bypasses this wrapper and enters the shared
## station checkpoint with a return destination already set.
label act2_hub:
    ## At five minutes or fewer, ordinary room waits may all be disabled while
    ## quiet repeat visits cost nothing. Some specialized five-minute controls
    ## can still be legal, so returning to the public map offers the ending
    ## rather than taking those choices away or requiring one to reach climax.
    if time_remaining > 0 and time_remaining <= 5:
        menu:
            "The storm is almost at its peak."

            "Let the final minutes pass.":
                $ _storm_minutes_spent = time_remaining
                call spend_storm_time

            "Use what remains.":
                pass
    $ hub_return_location = None
    jump act2_station_checkpoint


## A forced EVA can interrupt a room-local checkpoint. Returning through the
## public map would erase that origin and make the player leave and re-enter
## the room to recover its menu. Restore only the room presentation here — a
## full entry label could charge a new arrival beat — then let the shared
## checkpoint settle background work and return to the existing submenu.
label act2_resume_after_eva:
    $ _eva_return_location = hub_return_location
    $ current_location = _eva_return_location if _eva_return_location is not None else "corridor"
    $ marcus_eva_came_to_elara = False
    show screen observatory_hud
    if _eva_return_location == "telescope":
        $ eot_enter_room("telescope")
        scene bg_telescope with fade
    elif _eva_return_location == "comms":
        $ eot_enter_room("comms")
        scene bg_comms with fade
    elif _eva_return_location == "lab":
        $ eot_enter_room("lab")
        scene bg_lab with fade
    elif _eva_return_location == "generator":
        $ eot_enter_room("generator")
        scene bg_generator with fade
    elif _eva_return_location == "habitat":
        $ eot_enter_room("habitat", allow_creak=False)
        scene bg_habitat_module with fade
    elif _eva_return_location == "storage":
        $ eot_enter_room("storage")
        scene bg_storage with fade
    if _eva_return_location is not None:
        with echo_room_beat
        jump act2_station_checkpoint
    $ hub_return_location = None
    jump act2_hub


label act2_station_checkpoint:

    $ long_night_active = True
    ## Music (§5): "Six Rooms Against the Wind" — self-guarded start;
    ## the storm-intensity axis polls live state, no other hooks.
    $ eot_hub_music_start()
    $ _local_checkpoint = hub_return_location is not None
    ## This label is both the map entrance and the station's shared event
    ## checkpoint. Room work returns through it so completed processes, storm
    ## changes and alerts are reported before the local menu is re-offered.
    ## Those local passes are not map visits and must not replay the corridor's
    ## first-arrival beat.
    if hub_return_location is None:
        $ hub_visits += 1
    ## Disabled-choice visibility is armed per menu (2026-08-17, presentation
    ## stage 2: the lab's spent "Talk to him." stays on the list with its
    ## reason) and disarmed on every way out of that menu. This is the net,
    ## because the flag is process-global and a load lands mid-night: every
    ## room path comes back through the hub, so no leak can survive one
    ## traversal and put a greyed twin under a variant menu elsewhere.
    $ config.menu_include_disabled = False
    ## The first hub stop follows the canteen's ADV conversation. The map is a
    ## screen, not a dialogue statement, so it does not itself retire that say
    ## window; the translucent room log then exposed the old ADV line beneath
    ## whichever room Elara entered first. Close the dialogue layer only at the
    ## public hub boundary. Room-local work also passes through this checkpoint
    ## for alerts and completed jobs, but hiding its live NVL window here makes
    ## the same room fade out and back in before its menu is re-offered.
    if not _local_checkpoint:
        window hide
    call update_storm_state

    ## THE HUB IS AN OVERLAY, NOT A PLACE (2026-08-17, presentation stage 4).
    ## This label used to lay its own backdrop, so "leaving a room" meant
    ## arriving nowhere — a phantom corridor between every pair of real rooms.
    ## It lays no scene now: the room she just walked out of IS the backdrop,
    ## and the map washes in over it. Everything below this line is still
    ## STATION business (ARIA's scan, the storm advisories, the cold
    ## accounting), and what tells the player so is the FRAME, not a cut: those
    ## blocks use the same cyan station-log frame as the rooms, so a hub stop
    ## reads as one continuous station interface rather than a palette switch.
    ##
    ## The ONE cut left is the first stop of the night. Act 2 opens in the
    ## canteen and the map is not a thing she reads over her tea, so the first
    ## hub stop still establishes the central corridor — with its beat of empty
    ## room, so the player reads WHERE before WHAT. After that the corridor is
    ## simply where she is until she goes somewhere.
    if hub_visits == 1 and hub_return_location is None:
        $ eot_enter_room("corridor", allow_creak=False)
        scene bg_observatory with fade
        with echo_room_beat

    ## Snapshot player-facing knowledge before any checkpoint-only retargeting.
    ## A filename can narrow and complete the scan below in one pass; hearing
    ## both notices back-to-back is not an opportunity to stop the search.
    $ _scan_known_at_checkpoint_entry = coherence_scan_known

    ## ECHO-7 can turn ARIA's blind trawl into a named search after the process
    ## has already started. The old fixed target ignored this later evidence,
    ## so learning CONVERGENCE.DAT in Comms did nothing for the scan already
    ## running in the Lab. Retarget before completion: the question and the
    ## machine's work now interleave, and a scan already past the narrower
    ## target resolves on this same hub return.
    if coherence_scan_running and knows_convergence_file and not coherence_scan_named:
        $ coherence_scan_named = True
        $ _named_target = eot_coherence_target()
        if _named_target < coherence_scan_target:
            $ coherence_scan_target = _named_target
            $ coherence_scan_known = True
            nvl show echo_mode_dissolve
            aria_nvl "The filename your visitor supplied changes the search, Dr. Voss. CONVERGENCE.DAT is a target now, not a shape among every local partition. I have narrowed the run."
            if not _local_checkpoint:
                nvl hide echo_mode_dissolve
            nvl clear

    ## Coherence scan completion (Codex #2): resolved FIRST — before the
    ## time-zero climax jump and before Marcus's lock check — so a scan that
    ## crossed its target on the final action still counts as found, and cannot
    ## be locked or climax-skipped by this same checkpoint. Completion outranks
    ## both here, exactly as it outranks interruption for the origin sweep.
    ## Marcus can still seal the located-but-unopened file after a later direct
    ## disclosure; that is a new player-facing decision, not retroactive order.
    ## Sets
    ## coherence_found so the climax gives her the "search closing" reveal.
    if coherence_scan_running and coherence_scan_progress >= coherence_scan_target:
        ## Knowledge and culpability are different facts. Completion itself
        ## teaches Elara about an undiscovered scan, but cannot retroactively
        ## make her responsible for allowing it to continue.
        $ coherence_scan_known_before_completion = _scan_known_at_checkpoint_entry
        $ coherence_scan_running = False
        $ coherence_found = True
        $ coherence_scan_known = True
        $ nvl_frame = "bulletin"
        nvl clear
        nvl show echo_mode_dissolve
        terminal_nvl "{color=#44ff44}PARTITION SCAN COMPLETE — LOCAL PARTITIONS{/color}"
        if coherence_scan_commissioned:
            aria_nvl "Dr. Voss. The targeted search you queued when fallback opened has resolved. There is a file in Dr. Chen’s partition that does not want to be read: CONVERGENCE.DAT."
            aria_nvl "Your local work gave me the door. I followed it farther than your evidence could. I have not opened the file — but you should know it exists before whatever this storm is building toward."
        else:
            aria_nvl "Dr. Voss. The search I began when the storm took our uplink has resolved. There is a file in Dr. Chen’s partition that does not want to be read: CONVERGENCE.DAT."
            if aria_motive_asked:
                aria_nvl "This is the search we spoke about in the lab. My fear was not proof; the file is something we can examine. I have not opened it."
            else:
                aria_nvl "I did not ask your permission to look. I suspected it concerned me, and I was right. I have not opened it — but you should know it exists before whatever this storm is building toward."
        $ evidence_log = evidence_log + ["ARIA's partition scan surfaced CONVERGENCE.DAT in Chen's partition"]
        $ _eot_tag("marcus")
        $ knows_convergence_file = True
        if time_remaining > 0:
            aria_nvl "You can read it from the lab while the partition remains accessible. I will wait for your instruction."
        if not _local_checkpoint:
            nvl hide echo_mode_dissolve
        nvl clear
        $ nvl_frame = "log"

    ## COMMISSIONED BACKGROUND WORK REPORTS HERE (2026-08-17,
    ## design/DESIGN_echoes_process_log.md §2), beside the coherence scan and
    ## the origin sweep — the hub is where the station tells her what finished
    ## while she was elsewhere. Resolved BEFORE the time-zero climax jump, for
    ## the coherence scan's reason (Codex #2): work that finished is finished,
    ## and a run that crossed its target on the final action must not be
    ## silently discarded. The audit's knowledge therefore always arrives with
    ## its announcement — there is no unseen-report state to invent, and
    ## `aria_warned` is set exactly where she is told.
    if aria_audit_running and aria_audit_progress >= aria_audit_target:
        $ aria_audit_running = False
        $ aria_audit_done = True
        $ aria_warned = True
        $ coherence_scan_signature = True
        $ nvl_frame = "bulletin"
        nvl show echo_mode_dissolve
        terminal_nvl "{color=#44ff44}ARIA_CORE SOURCE AUDIT COMPLETE — THREE FINDINGS{/color}"
        aria_nvl "Dr. Voss. The audit you commissioned has finished. Three vulnerabilities in my own trust chain — three doors, one lock, and the lock accepts old keys."
        if not knows_convergence_file and not coherence_scan_running and not coherence_found:
            aria_nvl "One signature recurs in Dr. Chen’s partition metadata. It is not a filename, and it is not proof. It is enough to make a blind search smaller under fallback authority."
        aria_nvl "The run cost me [aria_audit_charged] points of core margin, paid out across its cycles. Core integrity [aria_integrity]%%. The findings are on my primary terminal whenever you want them."
        elara_thought "All three usable by someone who knows the architecture from the inside. Which is a very short list, and I have eaten breakfast with all of it."
        $ evidence_log = evidence_log + ["ARIA code audit — three trust chain vulnerabilities confirmed, exploitable by architecture insider"]
        $ _eot_tag("aria")
        if "aria_code" not in topics_read:
            $ topics_read = topics_read + ["aria_code"]
        if not _local_checkpoint:
            nvl hide echo_mode_dissolve
        nvl clear
        $ nvl_frame = "log"

    ## The shared finalizer also serves direct release of an already-complete
    ## audit target. This checkpoint is the ordinary background-process
    ## receipt. The seal's cost was paid at the console (the drive itself, and
    ## three minutes to load it); evidence_archived counts SEALED copies — a
    ## hash that never closed sealed nothing.
    if archive_hash_running and archive_hash_progress >= archive_hash_target:
        call finalize_archive_hash
        $ nvl_frame = "bulletin"
        nvl show echo_mode_dissolve
        terminal_nvl "{color=#44ff44}ARCHIVE HASH COMPLETE — DRIVE RELEASED{/color}"
        aria_nvl "The evidence log is sealed, Dr. Voss. Chain-of-custody hashes closed; the drive has spun down and released. Whatever tonight becomes, that copy reads the same to anyone who opens it."
        if not _local_checkpoint:
            nvl hide echo_mode_dissolve
        nvl clear
        $ nvl_frame = "log"

    ## Economy pass: one-shot fairness surface for the cold drain — ARIA names
    ## the decline and the lever (power priority). Sol economy review #2: this
    ## runs BEFORE the time-zero climax jump, so a final action that drags her
    ## across the line is still named to the player's face — with a too-late
    ## variant when there is no night left to act on the advice.
    if aria_integrity <= 35 and not aria_cold_notice_seen:
        $ aria_cold_notice_seen = True
        $ nvl_frame = "bulletin"
        nvl show echo_mode_dissolve
        terminal_nvl "{color=#ff4444}ARIA CORE INTEGRITY [aria_integrity]%% — SUSTAINED THERMAL DEGRADATION{/color}"
        aria_nvl "Dr. Voss. I want to be precise now, because I may not be able to be later. The storm and the work have left very little margin."
        if time_remaining > 0 and power_priority == "aria":
            aria_nvl "You have already routed what you can to my core. That is helping. I still need you to be careful about what you ask me to carry."
        elif time_remaining > 0:
            aria_nvl "If the power stays where it is, I do not expect to hold the whole night. If you can spare it, route it to me. If you cannot — I understand priorities. I helped write most of yours."
        else:
            aria_nvl "There is nothing left to route and nowhere left to route it. I wanted you to hear it from me, before the storm says it louder."
        if not _local_checkpoint:
            nvl hide echo_mode_dissolve
        nvl clear
        $ nvl_frame = "log"
    elif aria_cold_drain_hub_note >= 8:
        ## Attribution, not alarm (live-run item): a long action — the audit,
        ## the antenna repair — passes hours of continuous cold, and the
        ## integrity it costs is the NIGHT's, not the task's. ARIA says which
        ## is which. Repeating: it fires again whenever another 8 points of
        ## cold accumulate. The <= 35 notice above wins on a visit where both
        ## qualify (one integrity speech per hub stop) and deliberately does
        ## NOT clear the accumulator — those points stay owed an explanation.
        ##
        ## WINDOW, HONESTLY (cost round 6, live-run item): the accumulator is
        ## cleared when it is SPOKEN, not on every hub stop — a visit under the
        ## 8-point bar says nothing and carries, and the <= 35 notice above
        ## deliberately does not clear it either. So "since you last stood here"
        ## claimed a hub-to-hub window the number does not measure, and a
        ## coolant cartridge in between could leave it larger than the net drop
        ## the player watched. The line now says exactly what the counter is:
        ## cold points since ARIA last accounted for them.
        nvl show echo_mode_dissolve
        aria_nvl "Core integrity [aria_integrity]%%. Accumulated cold damage since my last cold report: [aria_cold_drain_hub_note] points. That is only the continuous cold drain, not the total change in integrity: process costs, sudden thermal damage, and recovery are separate. It covers the intervening work, not just your last task."
        $ aria_cold_drain_hub_note = 0
        if not _local_checkpoint:
            nvl hide echo_mode_dissolve
        nvl clear

    ## Storm peak — forced exit. Final-tick resolution (editorial pass #1):
    ## a sweep that completed on the last action is DONE — but silently. The
    ## poignant skip stands by decision: no payoff beat, no evidence, no
    ## trust — she never sees the result. The state records it and exactly
    ## one Act-3 line witnesses the unread report. Pending announcement
    ## notices are superseded by the climax itself.
    if time_remaining <= 0:
        if origin_sweep_running and origin_sweep_progress >= 45:
            $ origin_sweep_running = False
            $ origin_sweep_done = True
            $ origin_sweep_unseen = True
        jump act2_storm_climax

    ## The search starts when its grounds justify it. A lab commission waits
    ## only for fallback authority (t <= 240). Standby is not authorization:
    ## ARIA chooses to act on the prepared lead at t <= 210, under no human
    ## credential. A filename she was told but not asked to prioritize waits
    ## until t <= 180; a source-audit signature until t <= 165; and a blocked-
    ## route blind trawl until t <= 150. The later two are intentionally hard
    ## to finish without Elara's intervention.
    $ _coherence_start_at = 150
    if coherence_scan_signature:
        $ _coherence_start_at = 165
    if knows_convergence_file:
        $ _coherence_start_at = 180
    if coherence_scan_standby:
        $ _coherence_start_at = 210
    if coherence_scan_commissioned:
        $ _coherence_start_at = 240
    if time_remaining <= _coherence_start_at and not coherence_scan_running and not coherence_scan_stopped and not coherence_found and not marcus_locked_partition:
        $ coherence_scan_running = True
        $ coherence_scan_target = eot_coherence_target()
        $ coherence_scan_named = knows_convergence_file
        if coherence_scan_commissioned:
            $ coherence_scan_known = True
            nvl show echo_mode_dissolve
            aria_nvl "Fallback authority is open. The targeted partition search you queued is running now, Dr. Voss. Your credential is attached to the job."
            if not _local_checkpoint:
                nvl hide echo_mode_dissolve
            nvl clear

        if aria_audit_running and aria_audit_progress < aria_audit_target:
            nvl show echo_mode_dissolve
            aria_nvl "The source audit is paused. Another process has priority on my local cycles. Its completed work is retained; I will resume it when those cycles are free."
            if not _local_checkpoint:
                nvl hide echo_mode_dissolve
            nvl clear

    ## Suspicion channel — computing specialization: the workload is inferable
    ## from latency, but its target is not. Keep this distinct from
    ## coherence_scan_known so the status rail and Marcus disclosure cannot
    ## identify his partition before Elara checks the Lab process herself.
    if specialization == "computing" and coherence_scan_running and not coherence_found and not coherence_scan_known and not coherence_scan_suspected:
        $ coherence_scan_suspected = True
        nvl show echo_mode_dissolve
        elara_thought "ARIA’s replies land a half-second late. She is spending cycles on something she has not mentioned."
        elara_thought "The lab console would show what."
        if not _local_checkpoint:
            nvl hide echo_mode_dissolve
        nvl clear

    ## Second failure vector (2026-08-12): Marcus is the engineer. If he
    ## already suspects Elara (>= threshold evidence points; trust raises the
    ## bar) and ARIA is grinding through HIS partition, he notices and seals
    ## it. This kills the scan. NOTE: the file still surfaces at the climax
    ## for now (fallback authority) — the no-file consequence lands when the
    ## alternate act 3 is built; marcus_locked_partition is recorded from here.
    ## Validation fix (2026-08-12): the scan LOCATES the file (coherence_found
    ## = "I know it exists, I have not opened it"); RETRIEVAL is at the climax.
    ## So Marcus can seal it AFTER it's found — awareness is not access. The
    ## lock fires while the scan runs OR after it located the file, any time
    ## before the climax. Without this the scan always beat the seal window and
    ## the no-file path was unreachable.
    $ _marcus_evidence_now = eot_marcus_evidence_points()
    $ _marcus_lock_bar = eot_marcus_lock_threshold()
    ## A save made before the stance graph can already contain a disclosure
    ## or a ledger warning. Carry that knowledge forward without replaying it.
    if marcus_search_stance == "unaware" and marcus_told_search:
        $ eot_marcus_consider_search(volunteered=True, trusted=eot_marcus_trusts())
    elif marcus_search_stance == "unaware" and marcus_access_watch_seen:
        $ eot_marcus_consider_search()
    ## Evidence discovers the search; it does not decide whether an informed
    ## Marcus permits it. The stance graph below owns that later decision.
    ## Do not surface hidden machinery merely because low trust makes the lock
    ## threshold small. The ledger warning has context only after Elara knows
    ## ARIA is searching, or after her signed scan assistance gives Marcus the
    ## one concrete file-search trace represented here. Other suspicious acts
    ## still affect his threshold, but cannot reveal an unknown search to her.
    if not marcus_locked_partition and marcus_search_stance == "unaware" and (coherence_scan_running or coherence_found) and not marcus_access_watch_seen and (coherence_scan_known or marcus_scan_assist_logged) and marcus_scan_notice_remaining <= 0 and _marcus_evidence_now >= (_marcus_lock_bar - 1):
        $ marcus_access_watch_seen = True
        $ eot_marcus_consider_search()
        nvl show echo_mode_dissolve
        aria_nvl "Dr. Chen has opened the partition access ledger. He has not changed his credentials. He is reading the same trail I am leaving."
        elara_thought "Not a warning. Not yet. Just Marcus checking a door he knows well enough to hear move."
        if not _local_checkpoint:
            nvl hide echo_mode_dissolve
        nvl clear

    $ _marcus_locks_now = eot_marcus_review_search() if (coherence_scan_running or coherence_found) else False
    if _marcus_locks_now:
        $ marcus_locked_partition = True
        $ coherence_scan_running = False
        nvl show echo_mode_dissolve
        if convergence_opened:
            aria_nvl "Dr. Chen has sealed his research partition. Further access is blocked; the copy you retained is still here."
        elif marcus_access_watch_seen:
            aria_nvl "The access-ledger session I reported has become a credential change. Dr. Chen has sealed his research partition below the fallback layer."
        elif coherence_found:
            aria_nvl "Dr. Voss. I found where it lives — and in the same hour, Dr. Chen sealed the partition under personal credentials, below the fallback layer. I know the file exists. I can no longer open it."
        else:
            aria_nvl "Dr. Voss. Dr. Chen has sealed his research partition under personal credentials — a hard lock, below the fallback layer. My scan cannot proceed. I have lost access to it entirely."
        if marcus_told_search:
            elara_thought "He knew the search was running. This is not discovery. He has decided to close the door."
        elif coherence_scan_known:
            elara_thought "He noticed. Of course he noticed — the man reads a load graph the way I read a spectrum."
        else:
            elara_thought "Sealed his partition. In the middle of a storm, with everything else failing, that is what he stopped to do."
        elara_thought "He does not want that partition read. That is either guilt or privacy, and I no longer know how to tell them apart."
        if not _local_checkpoint:
            nvl hide echo_mode_dissolve
        nvl clear

    ## Recovery emergency window (ECHOES_ACT3_NOFILE.md §1, phase 2). The seal
    ## is not a wall. Once Marcus has locked the partition and Elara knows a
    ## file is behind it, ARIA surfaces ONE narrow chance to force it — but only
    ## while enough of the night is left to try (>= 90 min). She does NOT force
    ## the attempt here; it becomes an available action at the lab console. The
    ## seal may adapt while they work. One-shot via recovery_offered. Compound
    ## condition kept on one line for the route flattener (no functions — all
    ## defaulted).
    ##
    ## Cost legibility (round 3): this was the last fuzzy ARIA estimate over a
    ## 40-75 spread, and machines quote numbers. LOCKSTEP: the ladder below
    ## mirrors recovery_attempt's _rec_cost exactly — computing 45, signals 40
    ## (only while the line is open; blocked signals falls to the desperate
    ## brute force), physics 60, anything else 75 — put through eot_cold_taxed,
    ## the same helper the spend's inline tax mirrors. _rec_cost itself is not
    ## computed until recovery_attempt, so the ladder is duplicated here; change
    ## one, change both. Elara's answering thought stays fuzzy on purpose:
    ## humans estimate.
    $ _recovery_offer_now = marcus_locked_partition and knows_convergence_file and not file_recovered and not convergence_opened and not recovery_attempted and not recovery_offered and time_remaining >= 90
    if _recovery_offer_now:
        $ recovery_offered = True
        $ _est_nom = 45 if specialization == "computing" else (40 if (specialization == "signals" and not blocked_signal) else (60 if specialization == "physics" else 75))
        $ _est = eot_cold_taxed(_est_nom)
        nvl show echo_mode_dissolve
        aria_nvl "Dr. Voss. There may be a way back in. The seal is below fallback authority, but it is not the same as a wall — with the console and enough time, it can be worked."
        aria_nvl "I will be honest about the price. It would cost about [_est] minutes, and I cannot promise the seal will not adapt while we push at it. Other systems still need you before the storm peaks."
        aria_nvl "The attempt is yours to make, or not, from my primary terminal. I only want you to know the door is not final while there is night left to spend on it."
        elara_thought "Time spent on a door that might not open. Time I could spend keeping the station running."
        if not _local_checkpoint:
            nvl hide echo_mode_dissolve
        nvl clear

    ## Storm damage events — the state flipped in spend_storm_time when the
    ## clock actually crossed the threshold; here we only announce it.
    if antenna_damage_notice:
        ## Bring in the already synchronized operational pulse with the
        ## bulletin; antenna damage can precede the storm music threshold by
        ## fifty minutes, and a short bulletin must not outrun the next bar.
        $ eot_hub_music_refresh_now()
        ## The station-wide throat-clear and the notice it introduces are one
        ## interruption in the room where Elara hears them. Cutting outside for
        ## the first sentence made the lead-in look unrelated, then needlessly
        ## reconstructed the room for the alert itself.
        $ nvl_frame = "bulletin"
        nvl show echo_mode_dissolve
        narrator_nvl "Every speaker on the station clears its throat at once."
        ## F3 wave (ariafirst): a repair can land between the damage tick and
        ## this announcement (she was in the generator room when the threshold
        ## crossed). A full red alert for an already-fixed fault \u2014 with a
        ## live-interpolated "degraded to 100%" \u2014 read as a logic bug.
        ## Announce the captured at-damage figure; if the reroute already
        ## happened, file the alert as the retrospective it is.
        if generator_repaired:
            if two_person_repair_done:
                terminal_nvl "ALERT (SUPERSEDED): antenna module 2 lost connection under storm load. Permanent exterior repair already complete \u2014 the alert queue is catching up to the repair."
            else:
                terminal_nvl "ALERT (SUPERSEDED): antenna module 2 lost connection under storm load. Local reroute already in place \u2014 the alert queue is catching up to the bypass."
        if not generator_repaired:
            terminal_nvl "{color=#ff4444}ALERT: ANTENNA ARRAY DAMAGE DETECTED{/color}"
            terminal_nvl "External antenna module 2 \u2014 connection lost."
            if signal_strength == antenna_damage_signal:
                terminal_nvl "Signal reception degraded to [antenna_damage_signal]%%."
            else:
                terminal_nvl "Reception at failure: [antenna_damage_signal]%%. Current reception: [signal_strength]%%. Module 2 remains damaged."
        if generator_repaired:
            if two_person_repair_done:
                aria_nvl "The damage notice cleared its own backlog, Dr. Voss. Module 2 failed, and your exterior repair had restored it before the station finished saying so."
            else:
                aria_nvl "The damage notice cleared its own backlog, Dr. Voss. Module 2 failed, and your reroute had answered it before the station finished saying so."
        if not generator_repaired:
            aria_nvl "Dr. Voss, the storm has damaged the antenna array. A local bypass requires one spare coupling and access to the generator room. A permanent repair requires the same coupling, exterior access, and two people on the rope."
            if not blocked_signal and not echo7_contact_spent:
                signal_known "ELARA. SIGNAL DEGRADING. DO NOT WAIT UNTIL THE STORM PEAKS."
        if not _local_checkpoint:
            nvl hide echo_mode_dissolve
        nvl clear
        ## The operational pulse belongs to this bulletin, not the entire
        ## repair window. A severe storm may independently remain in alert.
        $ antenna_damage_notice = False
        $ eot_hub_music_refresh_now(fade=0.8)
        $ nvl_frame = "log"

    ## Environmental escalation — the station deteriorates
    if storm_intensity >= 1 and not storm_lights_event_seen:
        $ storm_lights_event_seen = True
        nvl show echo_mode_dissolve
        narrator_nvl "The lights flicker twice, then hold. The heating vents shudder and go quiet for a long moment before resuming."
        if not _local_checkpoint:
            nvl hide echo_mode_dissolve
        nvl clear
    if storm_frost_notice:
        ## B-1(b)/B3 state (integrity \u221210, ice-loading signal \u221215) applied in
        ## spend_storm_time; storm_frost_hit_antenna records whether the
        ## ice-loading branch fired there.
        $ storm_frost_notice = False
        $ nvl_frame = "bulletin"
        nvl show echo_mode_dissolve
        narrator_nvl "Frost is creeping across the interior windows now. Elara can see her breath."
        narrator_nvl "Something deep in the station\u2019s structure groans \u2014 metal contracting in the cold."
        if storm_frost_hit_antenna:
            terminal_nvl "{color=#ff8844}ANTENNA MODULE 2 \u2014 ICE LOADING. RECEPTION DEGRADED FURTHER.{/color}"
        terminal_nvl "{color=#ff8844}THERMAL STRESS \u2014 ARIA CORE CLUSTER 2 THROTTLED.{/color}"
        if not _local_checkpoint:
            nvl hide echo_mode_dissolve
        nvl clear
        $ nvl_frame = "log"
    ## B4: one-time cold-tax narration once the +25% time tax has begun to bite.
    if cold_tax_seen and not cold_tax_line_seen:
        $ cold_tax_line_seen = True
        nvl show echo_mode_dissolve
        narrator_nvl "The cold is in her hands now. Every panel takes longer; every latch fights back."
        if not _local_checkpoint:
            nvl hide echo_mode_dissolve
        nvl clear

    ## Idle Marcus reads logs (2026-08-10): freezing him out is free in the
    ## moment and paid for later. If nothing was ever done together, his last
    ## hours at the lab's side console have room for the station's records — and
    ## ARIA logs everything. Silent here; the bill arrives at the doorway.
    if time_remaining <= 60 and not marcus_read_logs_checked:
        $ marcus_read_logs_checked = True
        ## Room waits (2026-08-14): a half hour spent shoulder to shoulder in
        ## a working room counts the same as the table or the crates — the
        ## night gave him something other than the logs.
        $ _together_any = habitat_sat_with_marcus or storage_hunt_together or two_person_repair_done or marcus_told_signal or wait_shared_moment
        $ _logs_exist = len(echo7_asked_ever) > 0 or origin_sweep_progress > 0 or origin_sweep_done
        if not _together_any and _logs_exist:
            $ marcus_read_logs = True

    ## Origin sweep: the integration is a background process — its
    ## interruption and completion surface here, like the other station events.
    if origin_sweep_notice:
        $ origin_sweep_notice = False
        $ nvl_frame = "bulletin"
        nvl show echo_mode_dissolve
        terminal_nvl "{color=#ff8844}TELESCOPE INTEGRATION SUSPENDED — RECEPTION BELOW THRESHOLD{/color}"
        $ _sweep_disp = int(origin_sweep_progress)
        aria_nvl "Dr. Voss, the bearing-287.4 integration lost the array. [_sweep_disp] clean minutes are retained. It can be resumed from the dome once reception recovers."
        if not _local_checkpoint:
            nvl hide echo_mode_dissolve
        nvl clear
        $ nvl_frame = "log"

    if origin_sweep_running and origin_sweep_progress >= 45:
        $ origin_sweep_running = False
        $ origin_sweep_done = True
        $ nvl_frame = "bulletin"
        nvl show echo_mode_dissolve
        terminal_nvl "{color=#44ff44}TELESCOPE INTEGRATION COMPLETE — BEARING 287.4{/color}"
        if origin_sweep_interruptions == 1:
            aria_nvl "Dr. Voss. Forty-five clean minutes on the anomalous bearing, stitched across one interruption. The dataset is sound."
        elif origin_sweep_interruptions > 1:
            aria_nvl "Dr. Voss. Forty-five clean minutes on the anomalous bearing, stitched across [origin_sweep_interruptions] interruptions. The dataset is sound."
        else:
            aria_nvl "Dr. Voss. Forty-five minutes of continuous integration on the anomalous bearing."
        aria_nvl "No object to the noise floor. No occultation, no thermal trace. The archived carrier shows zero parallax against the full rotation baseline."
        aria_nvl "Whatever transmitted, I cannot put it anywhere. Classification: unresolved."
        nvl clear
        $ evidence_log = evidence_log + ["Telescope integration — no object at bearing 287.4, zero parallax on the archived carrier; no transmitter within instrument reach"]
        $ _eot_tag("temporal")
        if specialization == "signals":
            if knows_origin_claim:
                elara_thought "It told me my instruments would confirm what it said. I hate that it was right about that too."
            elara_thought "I know what nothing looks like — I have hunted point sources my whole career. The missing falloff, the clean bearing, and now this. The same answer three times: the carrier has no distance to fall across."
            $ evidence_log = evidence_log + ["Signals analysis — integration confirms the propagation anomaly; carrier ruled out as near-field, orbital, or catalogued deep-space source"]
            $ _eot_tag("temporal")
            nvl clear
        if blocked_signal:
            elara_thought "I said I would do this on my own terms. These are my terms: there is no transmitter out there. Only the comfortable explanations died tonight."
            if read_all_logs:
                elara_thought "It says it speaks from a when, not a where. The predictions in its logs landed one after another. I can rule out the where now."
            elif knows_prediction_evidence:
                elara_thought "It says it speaks from a when, not a where. The one prediction I heard landed exactly. I can rule out the where now."
            else:
                elara_thought "It says it speaks from a when, not a where. I shut it out before it could offer proof. I can rule out the where now."
            elara_thought "The when... I still cannot make myself believe the when."
            $ trust_signal += 1
        elif trust_signal <= 0:
            elara_thought "I kept the channel open around a doubt I could not rule out. The mundane version of that doubt just died on the noise floor."
            elara_thought "What is left is the version I cannot bring myself to say out loud yet."
            $ trust_signal += 1
        else:
            elara_thought "I believed it already. Now I believe it the way I believe a measurement."
        if not _local_checkpoint:
            nvl hide echo_mode_dissolve
        nvl clear
        $ nvl_frame = "log"

    ## The two-person rule is something Marcus DOES, not something he merely
    ## claims he intended after Elara happens to find him. Once his schedule
    ## reaches the EVA window and a coupling exists, he seeks her out. A
    ## generator bypass does not cancel this: it buys time, but the damaged
    ## coupling is still outside under load.
    if (eot_marcus_location() == "comms" or marcus_eva_waiting_for_parts) and antenna_damaged and (not generator_repaired or antenna_reroute_active) and antenna_parts > 0 and (not marcus_corridor_seen or marcus_eva_waiting_for_parts):
        ## Preserve a local checkpoint destination. Marcus can interrupt work
        ## in any room, but declining or completing the EVA should return
        ## Elara to that room's submenu instead of stranding its selected tile
        ## behind a leave-and-re-enter round trip. A map-originated encounter
        ## still carries None and returns to the map.
        $ marcus_eva_came_to_elara = True
        jump hub_comms

    ## Restore the room after all shared station events have settled. This is
    ## deliberately before the map: doing work at a console does not move Elara
    ## into the corridor, and no additional walking cost is charged.
    if hub_return_location == "telescope":
        $ hub_return_location = None
        jump hub_telescope_wait
    elif hub_return_location == "comms":
        $ hub_return_location = None
        jump hub_comms_menu
    elif hub_return_location == "lab":
        $ hub_return_location = None
        jump lab_room
    elif hub_return_location == "generator":
        $ hub_return_location = None
        jump hub_generator_menu
    elif hub_return_location == "habitat":
        $ hub_return_location = None
        jump hub_habitat_menu
    elif hub_return_location == "storage":
        $ hub_return_location = None
        jump hub_storage_menu
    elif hub_return_location is not None:
        ## Save-compatible guard for a stale or malformed destination.
        $ hub_return_location = None

    ## The station UI appears rather than pops: both screens carry an alpha-in
    ## (echo_ui_appear, screens_game.rpy) on their own contents, so the header
    ## and the map wash in over the room that is already there. The fade
    ## lives on the screens rather than on a `with` clause here — `call screen`
    ## has to stay a bare statement for the route-transcript flattener.
    ##
    ## POCKETS TRAVEL (2026-08-17, stage 4, spec open question 4): the HUD is
    ## shown here and NOT hidden on the way into a room, so the station status
    ## and the KIT/LOG buttons are hers for the whole night rather than for the
    ## seconds she is looking at the map. It suppresses itself while a live
    ## terminal panel is up (that panel owns the screen, header strip
    ## included), and act2_storm_climax — the night's single exit — takes it
    ## down. `show screen` on an already-shown screen is a no-op, so the repeat
    ## at every hub stop costs nothing and re-establishes it after a load.
    show screen observatory_hud

    $ hud_map_open = True
    call screen observatory_map
    $ hud_map_open = False

    $ selected_location = _return
    if selected_location not in ("telescope", "comms", "lab", "generator", "habitat", "storage", "stay"):
        $ selected_location = "stay"

    ## The current tile closes the map back to this room's choices. The
    ## station checkpoint has already run; do not replay arrival beats or
    ## charge an entry cost for putting the map away.
    if selected_location == current_location:
        nvl show echo_mode_dissolve
        if selected_location == "telescope":
            jump hub_telescope_wait
        elif selected_location == "comms":
            jump hub_comms_menu
        elif selected_location == "lab":
            jump lab_room
        elif selected_location == "generator":
            jump hub_generator_menu
        elif selected_location == "habitat":
            jump hub_habitat_menu
        elif selected_location == "storage":
            jump hub_storage_menu

    ## Marcus's late encounters live inside Comms and Lab. Only "stay" — the
    ## synthesized return from a mis-dismissed map — leaves her where she was.
    if selected_location != "stay":
        $ current_location = selected_location

    if selected_location == "telescope":
        jump hub_telescope
    elif selected_location == "comms":
        jump hub_comms
    elif selected_location == "lab":
        jump hub_lab
    elif selected_location == "generator":
        jump hub_generator
    elif selected_location == "habitat":
        jump hub_habitat
    elif selected_location == "storage":
        jump hub_storage
    else:
        ## Corridor stay REMOVED (2026-08-14, waiting-belongs-in-the-rooms,
        ## round 2). The 60-minute listening wait was the last place to spend
        ## the night doing nothing; waiting now belongs exclusively to the
        ## rooms, at the work. Both the corridor-wait button and the
        ## "Go find Marcus" verb are gone from screens_game.rpy now, so this
        ## branch survives only as the guard for an unrecognised map return:
        ## it costs nothing and simply re-offers the map.
        jump act2_hub


## Room-local work passes through the hub's shared event checkpoint, then
## returns to the room submenu. Free Back operations stay inside their submenu;
## explicit Leave operations continue to jump straight to act2_hub for the map.
label act2_checkpoint_telescope:
    $ hub_return_location = "telescope"
    jump act2_station_checkpoint

label act2_checkpoint_comms:
    $ hub_return_location = "comms"
    jump act2_station_checkpoint

label act2_checkpoint_lab:
    $ hub_return_location = "lab"
    jump act2_station_checkpoint

label act2_checkpoint_generator:
    $ hub_return_location = "generator"
    jump act2_station_checkpoint

label act2_checkpoint_habitat:
    $ hub_return_location = "habitat"
    jump act2_station_checkpoint

label act2_checkpoint_storage:
    $ hub_return_location = "storage"
    jump act2_station_checkpoint


## --- Shared beats of waiting (2026-08-14, round 4) ---------------------------
## Two one-shots that belong to WAITING rather than to any one room, migrated
## out of the removed corridor stay. They live here, once, because four wait
## sites cannot be kept in step by hand.

## The storm's texture, ONE phase at a time, across all four working rooms.
## The corridor was the wrong place for this prose, not the wrong prose: she
## hears the station because she has stopped moving, not because of which door
## she stopped behind. Plays at the START of a stay — before the clock moves —
## so the phase it describes is the phase she walked in on. Reassign, never
## .append (same rule as echo7_asked_ever): rollback and the flattener both
## need a fresh list.
label wait_final_minutes:
    ## Room menus use the complement of the half-duration deadline rule,
    ## with already-taxed prices, so ordinary waits keep their existing gates.
    call wait_storm_texture
    $ _storm_minutes_spent = time_remaining
    call spend_storm_time
    jump act2_hub


label wait_storm_texture:

    if storm_intensity not in wait_texture_phases_seen:
        $ wait_texture_phases_seen = wait_texture_phases_seen + [storm_intensity]
        if storm_intensity >= 3:
            narrator_nvl "There is no wind sound anymore — the storm has become a single sustained pressure, a hand flat against the whole station. The lights are down to their amber minimum."
            ## Phase 3 parks Marcus at the lab's side console
            ## (eot_marcus_location), so this is marcus_read_logs' second
            ## reader, restored with the texture.
            if marcus_read_logs:
                narrator_nvl "The lab's side console is still drawing a steady load. Marcus is reading something long."
            else:
                narrator_nvl "The lab's side console is awake too. Marcus is there, then, though neither of them leaves the work in front of them."
        elif storm_intensity == 2:
            narrator_nvl "The station has stopped creaking and started ticking — metal giving up its heat one degree at a time. Somewhere below, the generator changes pitch, holds, changes back. Her breath shows."
        elif storm_intensity == 1:
            narrator_nvl "The storm comes in long shoves with silences between — the silences are worse, because the building leans into them."
        else:
            narrator_nvl "The storm is still only a forecast here: the heating breathes, the fluorescents hum, and the station sounds the way it has sounded for three months. She memorizes it, without deciding to."

    return


## ECHO-7's unbidden whisper: ONE one-shot, THREE doors. It is the probe
## speaking without being asked, so it belongs anywhere except the comms
## terminal she would be interrogating. (1) A stay in the dome, any
## specialization — the array is the ear it arrives through. (2) Walking into
## the comms room, any specialization — the wall display flags the carrier
## before she is close enough to answer it. (3) Any other room's stay, SIGNALS
## only — she is the one who keeps a monitor channel open out of habit.
## Whichever door comes first spends stay_whisper_seen. Conditions are the
## corridor scene's, unchanged: an open line with something on it. The site is
## passed in _whisper_site ("telescope" / "comms" / "room") because the route
## flattener does not support label arguments; the compound gate stays on one
## line for it as well.
label echo_whisper:

    $ _whisper_now = not blocked_signal and not echo7_contact_spent and signal_strength >= 20 and not stay_whisper_seen and (_whisper_site != "room" or specialization == "signals")
    if _whisper_now:
        $ stay_whisper_seen = True
        ## One frame for the whole beat (2026-08-17): the framing line and the
        ## carrier it introduces are read in the same log, so the panel opens
        ## once instead of the narration arriving ADV and the carrier NVL.
        nvl show echo_mode_dissolve
        if _whisper_site == "comms":
            narrator_nvl "She is still two steps from the console when the wall display flags it."
        elif _whisper_site == "room":
            narrator_nvl "She keeps a monitor channel open on her handheld out of habit. Halfway through the wait, the noise floor parts."
        ## The carrier itself is terminal text and the probe's own voice, so it
        ## takes the NVL inset the rest of the game gives ECHO-7 — the room
        ## drops away for four lines and comes back. The signals-only handheld
        ## firing has no console to quote, so its narration above REPLACES the
        ## carrier-detected line rather than introducing it.
        if _whisper_site != "room":
            terminal_nvl "{color=#ff6688}WEAK CARRIER DETECTED — ANOMALOUS BEARING{/color}"
        signal_known "I HEAR YOUR STORM THROUGH THE ARRAY."
        signal_known "IT SOUNDS LIKE AFTER."
        elara_thought "After what, she doesn't ask. The carrier is already gone."
        nvl hide echo_mode_dissolve
        nvl clear

    return


## --- Marcus's late room interactions ----------------------------------------
## The old "Go find Marcus" verb closed a real reachability hole but invented
## two map destinations. Marcus now remains inside ordinary station geography:
## the Comms cable run for 150 >= t > 60, then the Lab side console at t <= 60.
## Their room menus feed these two arrival labels and one shared conversation.
##
## Ten minutes on a first arrival at that location, FIVE on a repeat (she knows
## the way now), paid at the END of the visit: like the round-4 entry-cost
## rule, the arrival variant and every effect are read on the clock she walked
## in with, and the seal a cold telling triggers lands BEFORE spend_storm_time
## so those minutes cannot credit a scan he has just killed. Once every
## substantive topic is spent, the room stops offering another conversation;
## there is no paid walk whose only result is duplicate filler. LOCKSTEP: each
## room's `_fm_first` (below) and the single spend in `marcus_room_visit`.
##
## REPEAT VISITS (2026-08-15, live-run bug): a live agent walked this three or
## four times and got the full arrival prose verbatim every time, paying ten
## minutes and the cold each time for a scene that had already happened. One
## flag per encounter — the Comms cable run and Lab side console are different
## beats, so each earns its own full arrival exactly once — and a
## repeat gets a single short line instead. When nothing substantive is left to
## say, the menu is skipped entirely rather than rendering "Leave him to it" as
## though it were a decision.
label hub_comms_marcus:

    ## First arrival AT THIS LOCATION. Read before the flag flips, and LOCKSTEP
    ## with the spend at the foot of marcus_room_visit (10 first / 5 repeat).
    $ marcus_visit_return = "comms_entry"
    $ _fm_first = not marcus_found_corridor
    $ marcus_found_corridor = True
    call marcus_room_gates

    scene bg_observatory with fade
    with echo_room_beat
    show marcus neutral at sprite_right
    show elara neutral at sprite_left
    with dissolve
    if _fm_first:
        narrator_adv "He is where the station said he would be: halfway down the comms corridor, one knee on the grating, reading a cable run by handlamp."
        elara "Sorry to interrupt you, but—"
        marcus "You're not interrupting. The storm is. What is it?"
    elif _fm_nothing:
        narrator_adv "He is still at the cable run. She watches long enough to see the work is going, and leaves the quiet where it is."
    else:
        narrator_adv "He is still at the cable run. She comes close enough to be heard over the storm, and he straightens up to listen."

    jump marcus_room_visit


label hub_lab_marcus:

    $ _fm_first = not marcus_found_terminal
    $ marcus_found_terminal = True
    call marcus_room_gates

    scene bg_lab with fade
    with echo_room_beat
    show marcus neutral at sprite_right
    show elara neutral at sprite_left
    with dissolve
    if _fm_first:
        narrator_adv "Marcus is at the lab's side console, the station logs open in a column beside his diagnostics. The glow catches the edge of a mug he has forgotten to drink from."
        narrator_adv "She stops at the other side of the desk."
        if file_recovered and recovery_left_trace:
            marcus "I saw the override. Do not mistake keeping this station running for letting that go. When the emergency load is off us, we are talking about what you found."
        else:
            marcus "You found me. What is it, Elara?"
    elif _fm_nothing:
        narrator_adv "Marcus is still at the side console. She watches long enough to see the work is going, and leaves the quiet where it is."
    else:
        narrator_adv "Marcus is still at the side console. This time she has something to say, and she crosses the lab to him."

    jump marcus_room_visit


## The gates live HERE, once, called by both rooms before either speaks: the
## arrival line is a claim about whether she came with something, and two
## copies of that predicate would drift the day one of them changes.
label marcus_room_gates:

    ## What she actually has to say tonight. Each gate on ONE line for the
    ## route flattener; the "nothing new" arm is the complement of all three,
    ## so the menu can never be empty and the walk is never silent.
    ##
    ## COMPUTED BEFORE THE ARRIVAL PROSE (2026-08-15, editorial item): the
    ## repeat-arrival line is a statement about whether she has come with
    ## something, so it cannot be written before the answer is known. The old
    ## order narrated her disengaging ("leaves the quiet where it is") and then
    ## rendered a menu on which she tells him about ARIA's search — the prose
    ## foreclosed a conversation the very next line offered. ONE predicate,
    ## `_fm_nothing`, decides both the arrival line and whether the menu opens.
    ##
    ## (a) The signal: the same confession as the rope line, indoors. Gated on
    ##     the flags that already mean "he knows a signal arrived" —
    ##     marcus_knows_first_signal (act-1 tell) and marcus_told_signal (the
    ##     rope line). It sets marcus_told_signal and the DISCLOSURE weight
    ##     (+2), and NOTHING else,
    ##     in LOCKSTEP with setpiece_two_person_repair: the suspicion gates
    ##     downstream read `marcus_knows_first_signal and not signal_reported`,
    ##     and a volunteered confession must never arm them.
    ## (b) ARIA's search: gated on coherence_scan_known, the flag that means
    ##     Elara has learned about the scan (any of its three discovery channels,
    ##     or the completion beat). Completion snapshots whether she knew soon
    ##     enough to choose whether it continued. Also gated off once the
    ##     partition is already sealed — telling him then would be a false premise.
    ## (c) The one question that is not about the storm. One-shot.
    $ _fm_tell_signal = not marcus_told_signal and not marcus_knows_first_signal
    $ _fm_tell_search = coherence_scan_known and not marcus_told_search and not marcus_locked_partition
    $ _fm_search_followup = marcus_told_search and marcus_search_stance == "willing" and not marcus_locked_partition
    if coherence_scan_commissioned:
        $ _fm_search_action = "started searching"
        $ _fm_search_suffix = " on my authorization."
    elif coherence_found:
        $ _fm_search_action = "searched"
        $ _fm_search_suffix = " without permission."
    else:
        $ _fm_search_action = "started searching"
        $ _fm_search_suffix = " without permission."
    $ _fm_check_in = not marcus_checked_in
    $ _fm_search_caption = "About CONVERGENCE.DAT. I kept a copy, and we need to talk." if convergence_opened else "ARIA {} your partition{}".format(_fm_search_action, _fm_search_suffix)
    $ _fm_nothing = not _fm_tell_signal and not _fm_tell_search and not _fm_search_followup and not _fm_check_in

    return


## What she says once she is in the room with him. ONE copy for both rooms:
## the arrival is the room's, the conversation is theirs.
label marcus_room_visit:

    if _fm_nothing:
        ## "Nothing" means nothing DISPOSITIVE (2026-08-15 live-run item): a
        ## player standing here with twenty evidence entries read the old line
        ## as a flat lie. She is not empty-handed; she is holding nothing he
        ## could not argue with. No menu at all on this arm — "Leave him to it"
        ## on its own is not a decision, it is a button that costs ten minutes.
        ## Wave finding (2026-08-16, freesonnet4): with a SEALED DRIVE in her
        ## pocket, "nothing sealed, nothing signed" read as a flat lie again —
        ## same failure, new inventory. And repeat visits gave no sign the
        ## night's disclosures were spent, so players kept paying the trip to
        ## find out. Both arms now close the door honestly.
        if evidence_archived > 0:
            narrator_adv "The drive in her pocket is sealed, signed, hash and all — and it is an argument, not a conversation. Nothing is left that is hers to tell him — not yet. He waits the length of a breath; she doesn't fill it, and he goes back to the work."
        else:
            narrator_adv "She has nothing sealed, nothing signed — nothing to hand him that he could not argue with. Nothing is left that is hers to tell him — not yet. He waits the length of a breath; she doesn't fill it, and he goes back to the work."
    else:
        ## PROMPT (2026-08-15, live-run item, user-approved). The old line
        ## — "everything she has been carrying is portable, she could put
        ## any of it down right here" — reads as an inventory sentence, and
        ## a live player went hunting for an item-transfer option that does
        ## not exist and never did. Every option here is a thing SAID.
        ## Wave finding (2026-08-16, freeopus4): the "carried alone" framing
        ## re-printed verbatim right after she had said the big thing — false
        ## the moment any disclosure lands. The framing now moves to narration
        ## and knows what he already holds; the caption stays a saying-prompt.
        if marcus_knows_first_signal or marcus_told_signal or marcus_told_search or marcus_checked_in:
            narrator_adv "Not everything she has been carrying tonight is still hers alone — some of it he holds too, now. The rest can be said."
        else:
            narrator_adv "Everything she has been carrying tonight, she has carried alone. Some of it can be said."
        menu:
            "What does she say?"

            ## LOCKSTEP with the setpiece tell: same caption, same flag, same
            ## weight. What differs is the room — the rope line's whole argument
            ## was that nothing out there logs, and in here everything does.
            "“Marcus. Something has been talking to me.”" if _fm_tell_signal:
                $ marcus_told_signal = True
                ## DISCLOSURE (+2, 2026-08-15) — LOCKSTEP with the rope-line
                ## tell's own weight. Two rooms, one confession, one price.
                $ marcus_relationship += 2
                $ marcus_trust += 2
                if marcus_overheard_signal:
                    marcus "I know. The array room. I stood in that corridor and listened to the pauses."
                narrator_adv "There is a console within arm's reach of him with its log light on, and she says it anyway. Out on the rope line the wind would have covered her. In here nothing does, and she says it anyway."
                if blocked_signal:
                    elara "The night before the grant call, something started talking to me on the hydrogen line. It knew my name. I blocked it the same night, and I have spent every day since listening to the block."
                else:
                    elara "Since the night before the grant call. A signal on the hydrogen line that knows things it has no way of knowing. I have carried it alone because every way of saying it out loud sounds like this."
                marcus "..."
                marcus "When the storm is off us I am going to tell you that's impossible. Right now I am going to say thank you, and mean it."

            "“[_fm_search_caption]”" if _fm_tell_search:
                call marcus_disclose_search

            "“When can we talk about CONVERGENCE?”" if _fm_search_followup:
                elara "You said you wanted to explain it yourself. I'm here."
                if convergence_opened:
                    marcus "And you have the copy. Keep it local until we've talked."
                elif coherence_found:
                    marcus "I know she found it. I meant what I said."
                else:
                    marcus "You don't need a finished search to ask me. I meant what I said."
                marcus "When the emergency load is off us. In the lab, with no repair waiting on either of us. I need to finish a sentence without choosing which alarm to ignore."
                elara "After the storm peak, then. Not some other day."
                marcus "Not some other day."

            "“Never mind the storm readouts. How are you holding up?”" if _fm_check_in:
                ## COURTESY (+1): a kindness, not a disclosure.
                $ marcus_checked_in = True
                $ marcus_relationship += 1
                elara "Never mind the storm readouts. How are you holding up?"
                if file_recovered and recovery_left_trace:
                    marcus "Keeping the station up. Being angry with you. I can do both."
                    narrator_adv "He does not soften it. She had not earned that by asking."
                else:
                    marcus "Ask me at dawn."
                    narrator_adv "But he says it like a man planning to be there at dawn, and she files that where she keeps the good evidence."

            "Leave him to it.":
                elara "Nothing that won't hold. Carry on."
                narrator_adv "She walks back the way she came with all of it still in her hands, exactly as heavy as it was."

    hide marcus
    hide elara
    with dissolve

    ## Finding Marcus costs whether she says anything or not: ten minutes on
    ## the first trip, five on a repeat. The late-lab arm starts beside his
    ## console and therefore has no second trip.
    $ _storm_minutes_spent = 0 if marcus_visit_return == "lab_room" else (10 if _fm_first else 5)
    call spend_storm_time

    ## Return target (2026-08-18): the late-lab "Talk to Marcus at the side
    ## console." arm reaches this shared scene from INSIDE the lab — the
    ## conversation ends back at the room's own menu, not at the hub. Every
    ## find-Marcus path leaves the target unset and exits to the hub as
    ## before. lab_room's loop gate covers a spend that landed on zero.
    if marcus_visit_return == "lab_room":
        $ marcus_visit_return = None
        nvl show echo_mode_dissolve
        jump act2_checkpoint_lab
    if marcus_visit_return == "comms_entry":
        if time_remaining <= 0:
            $ marcus_visit_return = None
            jump act2_hub
        jump hub_comms

    jump act2_hub


## --- Hub: Telescope Room ---
label hub_telescope:

    $ eot_enter_room("telescope")
    scene bg_telescope with fade
    with echo_room_beat

    ## Entry cost rule (2026-08-14, round 4): a room charges for the WALK, not
    ## for being entered. 5 minutes on a first visit or on an entry that
    ## carries a beat, 0 on a quiet repeat \u2014 the finest increment on the clock,
    ## so stepping through a door is never a trap. Everything she DOES inside
    ## keeps its own price. The dome has no conditional arrival beat: the star
    ## map (5/15/30/45) is work, and the sweep menus below are work.
    $ _entry_cost = 5 if not telescope_visited else 0

    ## ROOMS ARE NVL FLOW (2026-08-17, presentation stage 2). The dome's own
    ## narration and every option it offers live in the station-log frame, so
    ## the choices sit in the stream she is already reading instead of
    ## arriving as a kiosk over it. ADV is reserved for the one beat in this
    ## room where a person is actually engaged: asking Marcus to tune the
    ## array, which brackets itself below.
    nvl show echo_mode_dissolve

    ## C2: the room acknowledges the storm phase.
    if storm_intensity >= 2:
        narrator_nvl "The telescope room shudders at the top of the station. Snow has buried half the dome; the instruments track on, indifferent, reading a sky nobody can see."
    elif storm_intensity == 1:
        narrator_nvl "The telescope room is the highest point of the observatory, and the first place the storm reaches. The gusts arrive in long slow shoves; the dome creaks between them."
    else:
        narrator_nvl "The telescope room is the highest point of the observatory. Through the reinforced dome the sky is still merely grey \u2014 the storm a wall on the horizon, arriving on schedule."

    if _entry_cost > 0:
        $ _storm_minutes_spent = _entry_cost
        call spend_storm_time

    ## The dome has been entered. Separated from the star map below (2026-08-15):
    ## this flag is about the WALK \u2014 it prices the entry and feeds the progress
    ## mod \u2014 while `star_map_reviewed` is about the WORK. Closing the map
    ## without commissioning anything used to be impossible (see below); now
    ## that it is free, it must also leave the map available.
    $ telescope_visited = True

    ## Time-zero hard stop (see storm_time_out). The walk up can itself spend
    ## the last of the night, and everything below this line is an offer: the
    ## star map, and — on a repeat visit, where no spend separates them — the
    ## integration menu as well.
    if time_remaining <= 0:
        jump storm_time_out

    call telescope_pending_damage_notice

    ## Save migration: before per-layer jobs existed, `star_map_reviewed`
    ## recorded an unknown one-of-three choice. Do not reopen ambiguous work.
    if star_map_reviewed and not star_map_known_sources_logged and not star_map_anomalies_correlated and not star_map_origin_analyzed:
        $ star_map_complete = True

    $ _integration_setup_cost = eot_cold_taxed(15)
    if not star_map_complete:
        ## ENTRY IS A CHOICE (2026-08-18, user play session \u2014 same rule as
        ## the storage rack): the map used to auto-open on first entry. Now
        ## the room offers it, and "later" keeps the offer standing.
        ## ROOM OFFERS, TOGETHER (2026-08-18, user review round 2): the
        ## integration belongs on this menu, not behind the map-decline —
        ## picking "later" and then being offered the night's biggest
        ## commitment read as the offers arriving backwards. Declining now
        ## skips the sweep menu entirely (hub_telescope_skip_sweep).
        if not star_map_open_requested:
            $ _telescope_room_prompt = "Bearing 287.4 has sat marked on the dome's display since the signal arrived, still unexamined."
            if star_map_origin_analyzed:
                $ _telescope_room_prompt = "The archived carrier from bearing 287.4 is analyzed. Other regions of the map remain open."
            menu (nvl=True):
                "[_telescope_room_prompt]"

                "Review the star map.":
                    pass

                "Start integration on 287.4. ([_integration_setup_cost] min setup, then 45 clean minutes in background; storm interference takes longer)" if eot_sweep_conditions_ok() and (star_map_origin_analyzed or echo7_origin_hint_seen) and not origin_sweep_staged and not origin_sweep_running and not origin_sweep_done:
                    jump telescope_start_integration

                "Check the bearing-287.4 integration." if origin_sweep_staged and not origin_sweep_done:
                    jump hub_telescope_after_map

                ## WAIT ON THE SURFACE (2026-08-18, user play session): the stay
                ## used to live only in the room's closing menu, reached by picking
                ## "later" first — so the offer to stay arrived AFTER the intent
                ## to go, and read backwards. The lab's room menu already carries
                ## its bench next to "Leave the lab."; the dome now matches.
                "Wait, and stay in the dome.":
                    jump hub_telescope_wait_pick

                "Leave the map for later.":
                    ## Straight out (same session): with the stay offered above,
                    ## funneling the decline through the closing wait menu asked a
                    ## question the player had just answered.
                    elara_thought "The bearing has waited since the signal arrived for me to look at it properly; it can wait until I have the hours to spend on it."
                    nvl hide echo_mode_dissolve
                    nvl clear
                    jump act2_hub

        $ star_map_open_requested = False

        aria_nvl "Dr. Voss, the anomalous signal\u2019s bearing is marked. The regions are free to browse; the readings are not."

        ## Cost legibility (round 3): the star map serves three actions at
        ## three prices — known sources 5, the anomaly cluster 15, and the
        ## carrier analysis 30/45 — and only the analysis is a 30+ minute
        ## spend. The region pick IS the commitment, and the cost is not
        ## knowable until it is made, so ARIA prices the expensive option at
        ## the last point before the choice and NAMES it. PURPOSE SPLIT
        ## (2026-08-18, user review): the map's priced work is Elara reading
        ## the RECORDED carrier — desk analysis of what was already heard.
        ## The array's live measurement is the integration below, and only
        ## that holds the dome; the old "origin trace" label made the two
        ## sound like one instrument (the three-numbers confusion,
        ## live-reported). LOCKSTEP: _telescope_minutes below charges this
        ## exact nominal for the signal_origin region; change one, change
        ## both — and screens_game's analysis caption names the same halves.
        $ _est_nom = 30 if specialization in ("signals", "physics") else 45
        $ _est = eot_cold_taxed(_est_nom)
        if star_map_origin_analyzed:
            aria_nvl "The archived carrier analysis is complete, Dr. Voss. The other regions are still available for review."
        elif _est != _est_nom:
            aria_nvl "A full analysis of the archived carrier is desk work, not dome work — in tonight’s cold, about [_est] minutes of it, Dr. Voss."
        else:
            aria_nvl "A full analysis of the archived carrier is desk work, not dome work — about [_est] minutes of it, Dr. Voss."

        ## Star map — modal with image-only constellation buttons.
        ##
        ## EXIT IS FREE (2026-08-15, twice-reported live-run bug). The screen
        ## used to return True from a button called "Close", and this block
        ## charged for whatever `selected_region` happened to hold — so
        ## browsing the three regions (which are free) and then dismissing the
        ## map cost 15 taxed minutes and about five points of integrity, on the
        ## one control that universally means "never mind". The screen now
        ## returns the region only from an explicit, priced action button, and
        ## None from Close; None buys nothing and charges nothing.
        $ selected_region = None
        call screen star_map_screen

        $ _map_pick = _return
        ## Crash guard (live traceback 2026-08-17): underscore store vars are
        ## excluded from saves and rollback, so a load/rollback that re-enters
        ## between the pick and the spend could reach the charge line with
        ## _map_pick reconstructed but _telescope_minutes gone (NameError).
        ## Initialized here, the worst such path charges zero instead.
        $ _telescope_minutes = 0

        if _map_pick == "signal_origin":
            $ _telescope_minutes = 30 if specialization in ("signals", "physics") else 45
            $ star_map_origin_analyzed = True
            elara_thought "Bearing 287.4. Nothing there in any catalog. But ECHO-7\u2019s signal came from exactly this point."
            ## Now-vs-then (2026-08-18, user): the present against her past,
            ## one line \u2014 and the wanting-it-to-be-wrong is the same muscle
            ## the night keeps asking her to use.
            elara_thought "The last time a bearing refused a catalog this hard, I was a student and the answer was a software bug. I spent two days hoping it wasn't. Tonight I would settle for a bug."
            if specialization == "signals":
                elara_thought "The signal propagation pattern is wrong for deep space. The inverse-square falloff doesn\u2019t match. It\u2019s as if the signal originated from... everywhere and nowhere at once."
                $ evidence_log = evidence_log + ["Signal origin analysis (signals expertise) \u2014 propagation pattern inconsistent with point source, suggests non-spatial origin"]
                $ _eot_tag("temporal")
            elif specialization == "physics":
                elara_thought "If the signal really traversed time rather than space, the bearing might be an artifact of the temporal displacement field. The actual \u2018origin\u2019 could be right here."
                $ evidence_log = evidence_log + ["Signal origin analysis (physics expertise) \u2014 bearing may be artifact of temporal field, true origin possibly local"]
                $ _eot_tag("temporal")
            else:
                elara_thought "The encoding uses a protocol I\u2019ve never seen. But the header structure reminds me of ARIA\u2019s internal messaging format. A future version?"
                $ evidence_log = evidence_log + ["Signal origin analysis (computing expertise) \u2014 encoding resembles future ARIA internal messaging protocol"]
                $ _eot_tag("aria")
        elif _map_pick == "anomaly_cluster":
            $ _telescope_minutes = 15
            $ star_map_anomalies_correlated = True
            elara_thought "More anomalies. Faint, but they\u2019re there. Like echoes of the main signal, scattered across the sky."
            $ evidence_log = evidence_log + ["Anomaly cluster detected \u2014 faint temporal echoes scattered across multiple bearings"]
            $ _eot_tag("temporal")
        elif _map_pick == "known_sources":
            $ _telescope_minutes = 5
            $ star_map_known_sources_logged = True
            elara_thought "Known sources. Nothing unusual. The anomaly stands alone against a backdrop of ordinary stars."
            $ evidence_log = evidence_log + ["Catalog baseline — known radio sources accounted for; anomalous carrier remains unmatched"]

        if _map_pick:
            $ star_map_complete = star_map_known_sources_logged and star_map_anomalies_correlated and star_map_origin_analyzed
            $ _storm_minutes_spent = _telescope_minutes
            call spend_storm_time

            if not star_map_reviewed:
                ## C1: no protocol thesis here \u2014 clipped ops fact; the lived
                ## annoyance belongs to Marcus and arrives by reference only.
                aria_nvl "Observation logged. Signed, sealed, queued for Geneva review when the uplink returns."
                elara_thought "Signed and sealed. Marcus says it like a curse \u2014 {i}discovery, pending approval{/i}."
                $ evidence_log = evidence_log + ["Aethon telescope note \u2014 ARIA Trust Protocol authenticates scientific observations before publication"]
                $ _eot_tag("aria")
            else:
                aria_nvl "Analysis appended to the signed telescope note, Dr. Voss."
            $ star_map_reviewed = True
        jump hub_telescope_after_map

    else:
        if storm_intensity >= 2:
            narrator_nvl "The star map is done and reviewed. The instruments have given up on the sky and are recording the storm instead \u2014 data nobody asked for, kept anyway."
            if not origin_sweep_done and not origin_sweep_running:
                ## Sol round-9: branch on the staged plan, not the interruption
                ## counter — a failed arm is staged with zero interruptions,
                ## and the menu below will offer Resume, so the narration must
                ## agree with it.
                if origin_sweep_progress > 0:
                    narrator_nvl "The suspended integration waits in the dome's memory. The array could still finish what it started — if she can give it reception through this."
                elif origin_sweep_staged:
                    narrator_nvl "The observing plan waits in the dome's memory, nothing banked yet. The array could still take it up — if she can give it reception through this."
                else:
                    ## Not a closed window anymore — a crawl. Honest about odds.
                    narrator_nvl "A long integration could still be started, but against this storm it would crawl — and the storm is not done getting worse."
        else:
            narrator_nvl "She has already reviewed the star map. The instruments hum softly, tracking the storm\u2019s progress."
        jump hub_telescope_after_map

## Landing for every path out of the star-map block (2026-08-18): the map is
## a choice now, and the flattener follows jumps, never label fall-through \u2014
## so all three arms (reviewed, declined-for-later, repeat visit) arrive here
## by explicit jump before the integration section.
label hub_telescope_after_map:
    call telescope_pending_damage_notice

    ## The origin sweep (2026-08-10): verification by falsification, run as a
    ## continuous background process. A hoax needs hardware, and hardware
    ## needs a place to be. Configure here (15 min); then the array must hold
    ## 45 clean minutes while she does other things \u2014 reception drops suspend
    ## it (resume: 5 min, progress kept). Results arrive as a hub event.
    $ _integration_setup_cost = eot_cold_taxed(15)
    $ _integration_resume_cost = eot_cold_taxed(5)
    if origin_sweep_running:
        $ _sweep_disp = int(origin_sweep_progress)
        aria_nvl "The bearing-287.4 integration is running, Dr. Voss. [_sweep_disp] of 45 clean minutes accumulated."
        if storm_intensity >= 2:
            aria_nvl "Storm interference is slowing accumulation. The array is holding — for now."
    elif not origin_sweep_done and (star_map_origin_analyzed or echo7_origin_hint_seen):
        if eot_sweep_conditions_ok():
            ## Time-zero hard stop (see storm_time_out): the star map's own
            ## spend can land here at zero.
            if time_remaining <= 0:
                jump storm_time_out
            menu (nvl=True):
                "The dome hums. Bearing 287.4 is just sky \u2014 and that can be checked."

                "Start integration on 287.4. ([_integration_setup_cost] min setup, then 45 clean minutes in background; storm interference takes longer)" if not origin_sweep_staged:
                    jump telescope_start_integration

                "Resume the suspended integration. ([_integration_resume_cost] minutes)" if origin_sweep_staged:
                    $ _sweep_disp = int(origin_sweep_progress)
                    aria_nvl "Resuming integration on bearing 287.4. [_sweep_disp] clean minutes retained."
                    narrator_nvl "The dome picks its stare back up where it left off."
                    $ _storm_minutes_spent = 5
                    call spend_storm_time
                    ## Sol round-7: same re-validation on the resume tick.
                    if eot_sweep_conditions_ok():
                        $ origin_sweep_running = True
                    else:
                        aria_nvl "Reception fell again during reconfiguration, Dr. Voss. The integration remains suspended."

                "Leave the sky alone for now.":
                    pass
        else:
            ## Distinguish a broken array path from insufficient reception.
            if antenna_damaged and not generator_repaired:
                aria_nvl "The damaged antenna path cannot support this integration, even with a strong carrier. I need the coupling repaired or the path bypassed."
            elif storm_intensity >= 3:
                aria_nvl "The bearing-287.4 integration needs the array in better shape than this, Dr. Voss. Against the blizzard, I require reception at 75 percent or better."
            else:
                aria_nvl "The bearing-287.4 integration needs the array, Dr. Voss. Current reception is below threshold."
            $ _reroute_available = antenna_damaged and not generator_repaired and antenna_parts > 0
            if antenna_reroute_active:
                if power_priority == "comms":
                    aria_nvl "Communications priority is slowing the temporary bypass's signal loss, but cannot reverse it. Station routing cannot clear this threshold; the damaged coupling needs an exterior repair."
                else:
                    aria_nvl "The temporary bypass is losing signal under storm load. Communications priority can slow that loss, but cannot clear this threshold; the damaged coupling needs an exterior repair."
            elif _reroute_available and power_priority != "comms":
                aria_nvl "The generator reroute can bypass the damaged path with a spare coupling. Communications priority alone cannot restore it."
            elif _reroute_available:
                aria_nvl "Communications priority is already offsetting what loss it can. The generator reroute is the remaining station remedy."
            elif power_priority != "comms":
                if antenna_damaged and not generator_repaired:
                    aria_nvl "Without a spare coupling, the generator reroute is unavailable. Communications priority can improve reception, but it cannot replace the missing antenna path."
                else:
                    aria_nvl "The antenna path needs no generator bypass. Communications priority is the remaining station remedy."
            else:
                if antenna_damaged and not generator_repaired:
                    aria_nvl "Communications priority is already buying what margin it can, and we have no spare coupling for the generator reroute. I cannot clear this threshold through station routing alone."
                else:
                    aria_nvl "The antenna path and communications priority are already buying all the margin they can. I cannot clear this threshold through station routing alone."

            ## The human remedy (2026-08-10): Marcus can hand-tune the feed
            ## better than any subsystem. Asking costs nothing visible \u2014 the
            ## bill arrives at the climax if he already knew about the signal
            ## and no report ever went up.
            if not marcus_tuned_array and time_remaining > 60:
                $ _marcus_tune_cost = eot_cold_taxed(20)
                menu (nvl=True):
                    "Marcus can squeeze more out of that array than anyone alive."

                    "Ask Marcus to tune the array. ([_marcus_tune_cost] minutes of his time)":
                        ## ADV MEANS A PERSON IS ENGAGED: she goes and finds
                        ## him, and the exchange is with him. The log frame
                        ## closes for it and opens again on the far side.
                        nvl hide echo_mode_dissolve
                        nvl clear
                        $ marcus_tuned_array = True
                        if marcus_knows_message:
                            narrator_adv "She finds him mid-task and gives him the anomalous bearing. She wants to test whether the source is local. Marcus reads the integration plan once and reaches for his tools."
                            marcus "All right. If it has a position, the dome will find it. Give me a little while."
                            narrator_adv "He reworks the feed alignment by hand, muttering small profanities, and finds her fifteen points of signal nobody else could have found."
                        else:
                            narrator_adv "She finds him mid-task and asks for reception \u2014 an observation run, she says. He asks which instruments; she says the dome. He looks at her for exactly one second longer than the question needs."
                        if not marcus_knows_message and marcus_knows_first_signal and not signal_reported:
                            marcus "An observation run. In this."
                            elara "Calibration data. Storm conditions this clean are rare."
                            marcus "...They are that."
                            narrator_adv "He reworks the feed alignment by hand, muttering small profanities, and finds her fifteen points of signal nobody else could have found."
                        elif not marcus_knows_message:
                            marcus "Storm calibration? You astronomers are a special breed. Give me a little while."
                            narrator_adv "He reworks the feed alignment by hand and finds her fifteen points of signal nobody else could have found."
                        $ signal_strength = min(100, signal_strength + 15)
                        $ _storm_minutes_spent = 20
                        call spend_storm_time
                        nvl show echo_mode_dissolve

                    "Leave it.":
                        pass

    jump hub_telescope_skip_sweep

label telescope_pending_damage_notice:
    ## The walk or map work can damage the array before the next checkpoint.
    ## Explain its changed state before offering another dome operation.
    if antenna_damage_notice and not telescope_damage_notice_seen:
        $ telescope_damage_notice_seen = True
        if generator_repaired:
            aria_nvl "Module 2 failed under storm load. The array is operating again; the full damage report is queued for the next station check."
        else:
            aria_nvl "Module 2's antenna connection failed under storm load. The array needs repair or a bypass; the full damage report is queued for the next station check."
    return


## The integration start is shared by the first-visit and sweep menus.
label telescope_start_integration:

    if knows_origin_claim:
        elara_thought "It said the distance is not in space. That is a claim with consequences, and this one I can measure."
    else:
        elara_thought "If someone is transmitting at me, their hardware exists. Hardware has a position. Positions can be found."
    ## WHOSE forty-five minutes (2026-08-15, live-run item). The
    ## line read as a claim on the PLAYER's clock: a live agent
    ## budgeted the integration as forty-five minutes of Elara's
    ## night and skipped the console reads it could have afforded
    ## while the array listened. The integration is a background
    ## process \u2014 15 to configure, then the dome does the waiting \u2014
    ## and both halves of the beat now say so, quietly. LOCKSTEP
    ## with ARIA's next line: narration names whose minutes they
    ## are, she names that nobody has to stand over it.
    narrator_nvl "She builds the observing plan by hand: optical, infrared, radio, and the archived carrier against the array's rotation baseline. Forty-five minutes of clean reception, uninterrupted \u2014 the array's minutes, not hers \u2014 that is what a real answer costs."
    aria_nvl "Integration configured and started, Dr. Voss. It runs on the array \u2014 no supervision required, just reception above threshold. If it drops, it stops, and I keep whatever it has gathered."
    if storm_intensity >= 2:
        aria_nvl "Fair warning: at this storm intensity, clean minutes accumulate slowly. The measurement will crawl."
    $ _storm_minutes_spent = 15
    call spend_storm_time
    ## Sol round-7/8: the setup tick itself can take the array
    ## down (damage, drift, threshold rise). The plan is built
    ## either way — staged unlocks the 5-min resume — but a
    ## failed arm is NOT an integration interruption: nothing
    ## was running yet, and "stitched across N interruptions"
    ## must stay honest.
    $ origin_sweep_staged = True
    if eot_sweep_conditions_ok():
        $ origin_sweep_running = True
    else:
        ## Billed-for-a-no-op (cost round 6, live-run item):
        ## the mechanic is sound — the plan banks, and the
        ## resume is five minutes, not fifteen — but the old
        ## line led with the failure and put the promise
        ## behind it. The banked plan and the price of taking
        ## it up again come first now, in one breath.
        aria_nvl "The plan is built and held, Dr. Voss — the array dropped below threshold as I finished configuring. The quarter hour is not spent twice: resume it from here for a few minutes once reception recovers."
    jump hub_telescope_skip_sweep

## Landing past the sweep menu (2026-08-18): the map-decline arm and the
## extracted start both jump here; the flattener follows jumps, never
## label fall-through, so the sweep block also ends in an explicit jump.
label hub_telescope_skip_sweep:

    ## Room wait (2026-08-14): waiting belongs in the rooms, at the work — a
    ## person standing in a corridor for an hour is a person with something to
    ## hide. The dome is the one room Marcus's schedule never sends him to
    ## (eot_marcus_location), so a stay here is always the solo beat.
    ## Durations (user pass): 10/20/30 — short stays let a player keep
    ## waiting across a schedule boundary instead of gambling one half hour.
    ## Time-zero hard stop (see storm_time_out): a stay is minutes, and there
    ## are none. Reachable from the sweep menu's own spends above.
    if time_remaining <= 0:
        jump storm_time_out

    ## WAIT IS A SUBMENU (2026-08-17, presentation stage 2): the room offers
    ## one door marked "wait", and the durations live behind it with a way
    ## back, so a room's option list reads as the things she can DO here
    ## rather than as a price list. Captions and prices are unchanged. The
    ## durations were extracted to hub_telescope_wait_pick (2026-08-18, wait
    ## on the surface) and carry their own _wait_minutes init; "Back." still
    ## needs a re-offerable site, which is what hub_telescope_wait is.
    jump act2_checkpoint_telescope

label hub_telescope_wait:

    $ telescope_room_returns += 1
    if telescope_room_returns % 3 == 1:
        narrator_nvl "The array keeps its stare whether she watches it or not."
    elif telescope_room_returns % 3 == 2:
        narrator_nvl "A drive motor makes a small correction overhead. The guide display settles on its numbers again."
    else:
        narrator_nvl "The observer's chair faces the instruments. Beyond them, the curved ribs of the dome disappear into shadow."

    menu (nvl=True):

        ## Starting the background integration does not consume the map. Keep
        ## its review arm on the room surface instead of requiring Elara to
        ## leave the dome and walk back in; hub_telescope owns the single map
        ## implementation, and a repeat entry carries no walking cost.
        "Review the star map." if not star_map_complete:
            $ star_map_open_requested = True
            jump hub_telescope

        "Check the bearing-287.4 integration." if origin_sweep_staged and not origin_sweep_done:
            jump hub_telescope_after_map

        "Wait, and stay in the dome.":
            jump hub_telescope_wait_pick

        "Take the stairs back down.":
            pass

    nvl hide echo_mode_dissolve
    nvl clear
    jump act2_hub

## The durations, extracted (2026-08-18): offered from BOTH the room's entry
## menu (wait on the surface, user play session) and the closing menu above.
## The room line is repeated as this menu's caption, not rewritten: Ren'Py
## drops a menu caption when the menu closes, and without it the durations
## would sit under whatever paragraph came before. "Back." re-offers the
## closing menu from either path; on the entry-menu path the map offer it
## bypasses stays standing for the next visit (star_map_reviewed untouched).
label hub_telescope_wait_pick:

    $ _wait_minutes = 0
    $ _wait_cost_10 = min(time_remaining, eot_cold_taxed(10))
    $ _wait_cost_20 = min(time_remaining, eot_cold_taxed(20))
    $ _wait_cost_30 = min(time_remaining, eot_cold_taxed(30))
    menu (nvl=True):
        "The array keeps its stare whether she watches it or not."

        "Stay in the dome a little. ([_wait_cost_10] minutes)" if eot_deadline_allows_minutes(10):
            $ _wait_minutes = 10
        "Stay in the dome a while. ([_wait_cost_20] minutes)" if eot_deadline_allows_minutes(20):
            $ _wait_minutes = 20
        "Give the dome the long stretch. ([_wait_cost_30] minutes)" if eot_deadline_allows_minutes(30):
            $ _wait_minutes = 30
        "Let the final minutes pass." if time_remaining > 0 and time_remaining * 2 < eot_cold_taxed(10):
            jump wait_final_minutes
        "Back.":
            jump hub_telescope_wait

    if _wait_minutes > 0:
        call wait_storm_texture
        $ _storm_minutes_spent = _wait_minutes
        call spend_storm_time
        ## The dome is the whisper's first door, for every specialization.
        $ _whisper_site = "telescope"
        call echo_whisper
        if not wait_seen_telescope:
            $ wait_seen_telescope = True
            narrator_nvl "She takes the observer’s chair and turns nothing off. The drive motors correct, hold, correct — the array following a star it cannot see through half a metre of snow."
            elara_thought "Thirty years of logs from this room, and not one entry says {i}waited{/i}. It is all readings. The waiting is the part nobody writes down."
            narrator_nvl "The dome creaks between gusts. On the guide display, the numbers change in the fourth decimal place."
        else:
            narrator_nvl "She sits under the dome again and lets the drive motors do the talking — a stretch of corrections in the fourth decimal place."

    nvl clear
    jump act2_checkpoint_telescope


## --- Hub: Comms Array ---
label hub_comms:

    ## Session transients (_comms_asked_now, _comms_out_of_time, the
    ## overhear's _comms_marcus_at_entry) moved to `comms_terminal`
    ## (2026-08-18 room-menu round) — they are per-SESSION, and the session
    ## begins at the sit-down now, not at the room's doorstep.

    ## Entry cost rule (round 4, see hub_telescope): 5 for a first visit or an
    ## entry that carries a beat, 0 for a quiet repeat. Read BEFORE anything
    ## flips; the corridor encounter below tops it up if it fires. Questions
    ## keep their own 8-minute windows (before the live cold tax).
    $ _comms_marcus_return = marcus_visit_return == "comms_entry"
    $ marcus_visit_return = None if _comms_marcus_return else marcus_visit_return
    $ _entry_cost = 0 if (marcus_eva_came_to_elara or _comms_marcus_return) else (5 if comms_visits == 0 else 0)

    ## Bible 6d, phase 2: Marcus is at the Comms entrance, prepping cold-weather
    ## gear. One-shot encounter, before the array room. If the antenna is still
    ## down he proposes the two-person walk (the setpiece); if Elara already
    ## fixed it through ARIA, he noticed that too.
    $ _eva_parts_lead = False
    $ _eva_parts_return = marcus_eva_waiting_for_parts and antenna_parts > 0
    $ _eva_followup_ready = marcus_eva_deferred_at is not None and time_remaining < marcus_eva_deferred_at
    $ _offer_comms_marcus = eot_marcus_location() == "comms" and marcus_corridor_seen and not _eva_followup_ready and not _eva_parts_return
    if (eot_marcus_location() == "comms" and (not marcus_corridor_seen or _eva_followup_ready)) or _eva_parts_return:
        $ _eva_followup = marcus_eva_deferred_at is not None or _eva_parts_return
        $ marcus_corridor_seen = True
        $ marcus_eva_deferred_at = None
        $ marcus_eva_waiting_for_parts = False
        $ _entry_cost = 5
        $ current_location = "corridor"
        $ eot_enter_room("corridor")
        scene bg_observatory with fade
        with echo_room_beat
        show marcus neutral at sprite_right
        show elara concerned at sprite_left
        with dissolve

        if _eva_parts_return and marcus_eva_came_to_elara:
            narrator_adv "Marcus catches her in the central corridor before she can make it back to Comms, halfway into a cold-weather suit. His eyes go to the two flat-wrapped couplings under her arm."
            marcus "Two?"
            elara "Two. The manifest was right for once."
        elif _eva_parts_return:
            narrator_adv "By the time Elara reaches the Comms bench, Marcus has both harnesses laid out again. She sets the two flat-wrapped couplings between them."
            marcus "Two?"
            elara "Two. The manifest was right for once."
        elif _eva_followup:
            narrator_adv "The suits are still laid out beside the Comms door. Marcus has kept both harnesses warm and the rope clipped in, as though {i}not yet{/i} were a time he could put on a schedule."
            elara "You kept them ready."
            marcus "You said not yet. It is later."
        elif marcus_eva_came_to_elara:
            narrator_adv "Marcus finds her in the central corridor. He is halfway into a cold-weather suit, rope over one shoulder and a second harness in his hand."
        else:
            narrator_adv "Marcus is in the corridor outside the comms room, halfway into a cold-weather suit. Rope, harness, thermal patches laid out on the bench in a surgeon's row."

        if antenna_damaged and (not generator_repaired or antenna_reroute_active) and antenna_parts > 0:
            if not _eva_followup:
                elara "Marcus. Tell me you are not about to go outside."

                if antenna_reroute_active:
                    $ reroute_noticed = True
                    $ marcus_relationship -= 1
                    $ marcus_trust -= 1
                    marcus "The generator bypass is carrying the signal. Every time the wind loads the damaged coupling, that load comes back through the generator bus. If protection trips at peak, we lose more than reception."
                    marcus "ARIA pinged me when you put it through. You went through her instead of asking me."
                    elara "It was faster."
                    marcus "It was. Now we make it permanent."
                else:
                    marcus "Module 2 is dead, but the failed coupling is still taking the mast's load. If it tears out at peak, it can take the feed trunk with it. Then this stops being a one-part repair."
                    marcus "The reroute queue wants Geneva's blessing that isn't coming. So yes, I'm going outside. It's my station too, Elara."

                if marcus_caught_live:
                    show marcus suspicious
                    marcus "I was going to leave you a note."
                else:
                    marcus "Two-person rule. Even now."

                elara_thought_adv "The Geneva uplink is already gone. They are not going out to call for help. They are going because one failed coupling can still turn into a broken array — or a tripped generator bus — before the storm peaks."
                if not blocked_signal and not marcus_knows_first_signal:
                    elara_thought_adv "And because the same array carries the voice she has not told him about. That is not a safety case. It is simply true."
                elif not blocked_signal:
                    elara_thought_adv "And because the same array carries the impossible signal he knows she has been listening to. That is not a safety case either. It is simply true."

            ## Cost legibility: the setpiece is the night's biggest spend.
            ## His hour is a human's estimate and stays one; ARIA quotes the
            ## real taxed cost, as she does for the antenna repair and the
            ## origin trace (cost round 6, two live runs: quoted "an hour",
            ## charged 93). LOCKSTEP: setpiece_two_person_repair charges this
            ## exact nominal, and nothing between here and that spend moves the
            ## clock — the "we go together" arm jumps straight to it — so the
            ## quote is exact to the minute. Change the spend, change this.
            marcus "An hour outside, if nothing bites us. More if it does."
            ## Physics discount travels outside (2026-08-18, user) —
            ## LOCKSTEP with setpiece_two_person_repair's spend.
            $ _est_nom = 75 - (10 if specialization == "physics" else 0)
            $ _est = eot_cold_taxed(_est_nom)
            if _est != _est_nom:
                aria "It is not an hour, Dr. Voss. Mast, coupling, and the rope back — in tonight’s cold, about [_est] minutes. More if it bites, as he says."
            else:
                aria "It is not an hour, Dr. Voss. Mast, coupling, and the rope back — about [_est] minutes. More if it bites, as he says."

            menu:
                "The wind beyond the airlock does not sound like weather. It sounds like a verdict."

                "“Then we go together. Rope line, both of us.”":
                    $ marcus_eva_came_to_elara = False
                    $ marcus_eva_deferred_at = None
                    jump setpiece_two_person_repair

                "“Not yet. I need to finish something inside.”" if not _eva_followup:
                    $ marcus_eva_deferred_at = time_remaining
                    marcus "Then finish it. I will keep the suits ready. But the storm does not owe us the same choice twice."
                    narrator_adv "She leaves the rope coiled by the hatch and returns to the station. Not a refusal. A delay with weather in it."

                "“Nobody goes out in this. We fix it from the generator room or not at all.”":
                    $ marcus_eva_deferred_at = None
                    show marcus neutral
                    if antenna_reroute_active:
                        marcus "The reroute only holds if the storm leaves the coupling alone. But fine. Nobody plays hero."
                    else:
                        marcus "The failed coupling is still taking the mast's load. But fine. Nobody plays hero."
                    narrator_adv "He starts stripping off the suit, folding each piece back onto the bench with more care than it needs."

        elif antenna_damaged and not generator_repaired:
            if not storage_supplies_found:
                $ marcus_eva_waiting_for_parts = True
                $ _eva_parts_lead = True
                elara "The emergency rack in storage. I never cleared it."
                marcus "Then check it. If the manifest's right for once, there should be two in the flat wrap."
                elara "Keep the suits warm."
                marcus "I was planning to."
            else:
                elara "Marcus. There's nothing left to fix it {i}with{/i}."
                show marcus defeated
                marcus "I know. I counted the parts twice."
                narrator_adv "He looks at the laid-out gear a moment longer, then starts putting it away."

        elif generator_repaired:
            ## P-6: the solo reroute lands as a real relationship cost — Marcus
            ## clocks it, and the climax reads it back if he's ARIA-notified.
            $ reroute_noticed = True
            $ marcus_relationship -= 1
            $ marcus_trust -= 1
            show marcus neutral
            marcus "ARIA pinged me. Array's rerouted — nice work."
            show marcus suspicious
            marcus "You went through her instead of asking me. I had the suit half on, you know. I would have gone out there with you."
            elara "It was faster."
            marcus "Yeah. Faster."
            narrator_adv "He coils the rope he isn't going to need and doesn't say anything else."

        hide marcus
        hide elara
        with dissolve

        if _eva_parts_lead or marcus_eva_came_to_elara:
            jump act2_resume_after_eva

    ## The cable run is part of Comms, not a separate destination. Entering
    ## the room reaches both Marcus and the terminal; choose which needs her
    ## attention without inventing a second rectangle on the station map.
    if _offer_comms_marcus:
        call marcus_room_gates
        menu:
            "Marcus is still at the cable run outside the Comms door."

            "Talk to Marcus." if not _fm_nothing:
                jump hub_comms_marcus

            "Go inside to the array terminal.":
                pass

    if _entry_cost > 0:
        $ _storm_minutes_spent = _entry_cost
        call spend_storm_time

    $ current_location = "comms"
    $ eot_enter_room("comms")
    scene bg_comms with fade
    with echo_room_beat

    ## The whisper's second door (round 4): the comms room, for everyone. It
    ## has to land in the DOORWAY — before the spares cabinet, before the
    ## preamp menu, and long before the terminal comes up — because the whole
    ## point of this beat is that the probe speaks unbidden and she has no way
    ## to answer. One line later she would be sitting at the console, and it
    ## would just be a conversation.
    $ _whisper_site = "comms"
    call echo_whisper

    ## KIT items: rack work, deliberately OUTSIDE the terminal conversation —
    ## she finds and fits the preamp standing at the bench, before she sits
    ## down to talk to anything. Effects land BEFORE the time spend so the
    ## tick's drain and drift act on the new state.
    if not comms_amp_found:
        $ comms_amp_found = True
        nvl show echo_mode_dissolve
        narrator_nvl "The spares cabinet under the bench is half junk drawer, half museum. Behind three coils of coax and a power supply that died before she arrived: an RF preamplifier, still bagged, requisitioned for a survey that never got funded."
        narrator_nvl "She sets it on the bench where she can see it."
        $ signal_amps += 1

    jump act2_checkpoint_comms

## THE ROOM IS A MENU (2026-08-18, user: "Comms — also need better support
## for NVL"): the last waterfall room joins the loop. The terminal is a
## place within the place — its arm opens the live panel with the same
## fades as the lab console, and comms_leave returns HERE (quit the
## terminal, back to the room), except when the overhear beat has already
## walked her out to the corridor. ONE gate at the top covers every
## re-offered arm (the arms spend); the terminal needs none of its own —
## no spend sits between this gate and the sit-down, and the whole session
## is one long offer past it (its old doorstep gate said the same).
label hub_comms_menu:

    if time_remaining <= 0:
        jump storm_time_out

    nvl show echo_mode_dissolve
    if echo7_cooldown_remaining > 0 and not echo7_contact_spent:
        narrator_nvl "The carrier is rebuilding its error-correction window. ECHO-7 can receive again in [echo7_cooldown_remaining] minutes."
    $ _preamp_cost = eot_cold_taxed(10)
    $ comms_room_returns += 1
    if comms_room_returns % 3 == 1:
        narrator_nvl "The racks hum their flat chord under the storm; the waterfall display keeps its watch."
    elif comms_room_returns % 3 == 2:
        narrator_nvl "Coils of spare cable hang beneath the bench. Above them, another sweep crosses the waterfall display."
    else:
        narrator_nvl "The receiver fans turn at the same steady pitch. She rests a hand on the back of the terminal chair."

    menu (nvl=True):

        "Sit down at the array terminal." if echo7_cooldown_remaining <= 0:
            nvl hide echo_mode_dissolve
            nvl clear
            jump comms_terminal

        ## Cost legibility: actual cold-taxed cost in the caption.
        "Fit the RF preamplifier. ([_preamp_cost] minutes)" if signal_amps > 0 and signal_strength < 100:
            $ signal_amps -= 1
            $ signal_strength = min(100, signal_strength + 20)
            $ _storm_minutes_spent = 10
            call spend_storm_time
            narrator_nvl "Four screws, one jumper, and the waterfall display stops arguing with itself. By the time she tightens the cover, the carrier holds at [signal_strength]%%."
            jump act2_checkpoint_comms

        "Wait, and listen to the weather on the band.":
            jump hub_comms_wait_pick

        "Leave the comms room.":
            pass

    nvl hide echo_mode_dissolve
    nvl clear
    jump act2_hub

## Room wait (2026-08-18 — comms joins the wait rooms). Marcus's comms
## phase is t 150-60, so a stay here can genuinely overlap him; there is
## no bespoke encounter scene — the corridor beats own this room's drama —
## so an overlap gets one line through the door. Position captured at the
## decision to stay (the lab rule).
label hub_comms_wait_pick:

    $ _wait_marcus_before = eot_marcus_location()
    $ _wait_minutes = 0
    $ _wait_cost_10 = min(time_remaining, eot_cold_taxed(10))
    $ _wait_cost_20 = min(time_remaining, eot_cold_taxed(20))
    $ _wait_cost_30 = min(time_remaining, eot_cold_taxed(30))
    menu (nvl=True):
        "The racks hum their flat chord under the storm; the waterfall display keeps its watch."

        "Listen to the band a little. ([_wait_cost_10] minutes)" if eot_deadline_allows_minutes(10):
            $ _wait_minutes = 10
        "Stay with the waterfall a while. ([_wait_cost_20] minutes)" if eot_deadline_allows_minutes(20):
            $ _wait_minutes = 20
        "Keep the long watch on the carrier. ([_wait_cost_30] minutes)" if eot_deadline_allows_minutes(30):
            $ _wait_minutes = 30
        "Let the final minutes pass." if time_remaining > 0 and time_remaining * 2 < eot_cold_taxed(10):
            jump wait_final_minutes
        "Back.":
            jump hub_comms_menu

    if _wait_minutes > 0:
        call wait_storm_texture
        $ _storm_minutes_spent = _wait_minutes
        call spend_storm_time
        $ _whisper_site = "comms"
        call echo_whisper
        $ _wait_marcus_after = eot_marcus_location()
        if _wait_marcus_before == "comms" or _wait_marcus_after == "comms":
            narrator_nvl "Through the door she can hear Marcus at the corridor bench — tools set down, picked up, set down. Neither of them makes it a conversation."
        elif not wait_seen_comms:
            $ wait_seen_comms = True
            narrator_nvl "She watches the waterfall braid and unbraid itself around the carrier. The storm has a voice on every frequency; the trick of the room is choosing what not to listen to."
            elara_thought "Half of listening is deciding what you are not listening for."
        else:
            narrator_nvl "Another stretch with the band. The carrier holds its thin line through the weather."

    nvl clear
    jump act2_checkpoint_comms

## --- The comms terminal: a PLACE WITHIN A PLACE (2026-08-18) ------------
## The session machinery below is untouched; it begins here instead of on
## the room's doorstep, and the session transients re-init per sit-down.
label comms_terminal:

    $ _comms_asked_now = False
    $ comms_session_questions = 0
    $ _comms_session_asked = []
    $ _comms_question_thread = None
    ## comms_leave's teardown notice: every jump into comms_leave comes
    ## from this session.
    $ _comms_out_of_time = False
    ## Session-start capture (was room-entry, review #2): overhearing keys
    ## on who was outside the door when she began TALKING — which is now
    ## the sit-down, not the walk-in.
    $ _comms_marcus_at_entry = eot_marcus_location()
    ## A sit-down is only a provisional audience. The visit becomes real
    ## when Elara spends a question window; taking the free hang-up cannot
    ## advance the visit-gated Marcus/Aurora disclosures for no time.
    $ _natural_visit = min(comms_visits + 1, 3)
    $ _storm_visit_floor = 1 if storm_intensity <= 0 else (2 if storm_intensity == 1 else 3)
    ## The blocked-then-reconnected route has its own explicit catch-up set.
    ## Open-channel audiences instead advance with the storm: if the player
    ## missed a window, ECHO-7 briefs the missing stakes rather than replaying
    ## an obsolete interview in visit order.
    $ _visit = _natural_visit if (blocked_signal or late_signal_reconnect == 2) else max(_natural_visit, _storm_visit_floor)
    $ _audience_skipped = _visit > _natural_visit

    show screen crt_overlay
    call terminal_reset
    show screen echo_terminal_live with echo_mode_dissolve

    ## C2: room texture, phase-aware. ADV over the live terminal, same split as
    ## act 1 — what is ON the screen goes in the log, what Elara notices does not.
    if _visit == 1 or storm_intensity >= 2:
        if storm_intensity >= 2:
            narrator_adv "The comms room smells of ozone and cold solder. Half the rack lights that should be green are amber, and the waterfall display is mostly waterfall."
        elif storm_intensity == 1:
            narrator_adv "The comms room hums its usual flat chord, with a new note under it — the antenna feed roughening as the storm leans on the array."
        else:
            narrator_adv "The comms room is the warmest room on the station, by design and by superstition. The racks hum. The waterfall display scrolls its clean, empty sky."

    ## Specialization: the signals discount, made perceivable once.
    if _visit == 1 and specialization == "signals":
        elara_thought_adv "Storm static eats amateurs. She shapes her packets to the carrier's own timing — half the bandwidth the manual would spend."

    call terminal_system("AETHON OBSERVATORY — COMMS ARRAY")

    ## Keep the physical station state visible alongside the anomalous signal.
    ## The hub alert names the remedy; this readout confirms whether the
    ## failure is still active when the player reaches the affected room.
    if two_person_repair_done:
        call terminal_system("ANTENNA MODULE 2 — EXTERIOR REPAIR COMPLETE // ONLINE")
    elif antenna_damaged and antenna_reroute_active:
        call terminal_system("ANTENNA MODULE 2 — LOCAL REROUTE STABLE")
    elif antenna_damaged:
        call terminal_system("{color=#ff8844}ANTENNA MODULE 2 — OFFLINE // REROUTE AT GENERATOR{/color}")

    if echo7_contact_spent:
        call terminal_system("ANOMALOUS RELAY — NO CONTACT // REACH EXHAUSTED DURING PARTITION RECOVERY")
        elara_thought_adv "The receiver still works. That is not the same as having someone left at the other end."
        jump comms_leave

    if blocked_signal and _visit == 1:
        ## Blocked path — can unblock here
        call terminal_system("BAND 1420.405 MHz — {color=#44ff44}TRANSMISSIONS BLOCKED (USER){/color}")

        elara_thought_adv "The comms array. The block on 1420.405 MHz is still active."

        elara_thought_adv "The storm is cutting us off from the outside world anyway. If I unblocked it now, no one would know."

        call screen echo_terminal_choice([
            ("unblock", "Unblock the signal. The storm is cover enough."),
            ("keep", "Leave it blocked. I don’t need voices from the future."),
        ])
        $ _comms_block_choice = _return

        if _comms_block_choice == "unblock":
            $ blocked_signal = False
            $ late_signal_reconnect = 2
            $ trust_signal += 1
            call terminal_elara("ARIA, lift the block on 1420.405 MHz.")
            call terminal_aria("Block removed. Monitoring anomalous bearing.")
            call terminal_aria("...")
            call terminal_aria("Dr. Voss — incoming transmission.")
        else:
            elara_thought_adv "No. I made my decision."
            jump comms_leave

    if blocked_signal:
        call terminal_system("BAND 1420.405 MHz — {color=#44ff44}TRANSMISSIONS BLOCKED (USER){/color}")
        call terminal_system("NO TRAFFIC ON ANOMALOUS BEARING")
        elara_thought_adv "Nothing to hear. Nothing to say."
        jump comms_leave

    if signal_strength < 20:
        call terminal_system("{color=#ff8844}CARRIER LOST IN NOISE FLOOR{/color}")
        call terminal_aria("Signal strength at {}%. Insufficient for coherent reception. The antenna array needs repair.".format(signal_strength))

        if power_cells > 0:
            call screen echo_terminal_choice([
                ("boost", "Use a power cell to boost the signal temporarily."),
                ("wait", "Wait for repairs."),
            ])
            $ _comms_boost_choice = _return

            if _comms_boost_choice == "boost":
                $ power_cells -= 1
                $ signal_strength = min(100, signal_strength + 30)
                call terminal_aria("Power cell engaged. Signal boosted to {}%.".format(signal_strength))
            else:
                jump comms_leave
        else:
            jump comms_leave

    ## Vasquez mention — Elara's mentor, unreachable
    if _visit == 1:
        elara_thought_adv "I should call Dr. Vasquez. She’d know what to make of this."

        elara_thought_adv "But the storm took out the satellite uplink. I’m on my own."

        ## Now-vs-then (2026-08-18, user: Elara comparing the present to her
        ## past — one line per site, no new scenes).
        elara_thought_adv "In grad school she made us defend every claim twice — once to her, once to whoever in the room most wanted it wrong. There is nobody on this station whose job is to want me wrong tonight. That was always her chair."

    ## B3: offer a cell boost before total loss — when the link is wavering but
    ## not yet dead, spending a cell steadies the signal for the exchange ahead.
    if 20 <= signal_strength < 40 and power_cells > 0:
        call terminal_system("LINK WAVERING — {} POWER CELL(S) AVAILABLE".format(power_cells))

        call screen echo_terminal_choice([
            ("steady", "Use a power cell to steady the signal."),
            ("push", "Save the cells. Push through the static."),
        ])
        $ _comms_steady_choice = _return

        if _comms_steady_choice == "steady":
            $ power_cells -= 1
            $ signal_strength = min(100, signal_strength + 30)
            call terminal_aria("Power cell engaged. Signal steadied at {}%.".format(signal_strength))

    ## ECHO-7 conversation
    if _visit <= 1:
        if late_signal_reconnect == 2:
            call terminal_signal("ELARA. YOU CAME BACK.")
            call terminal_signal("THE STORM IS ALREADY DEGRADING THE ARRAY. I HAVE TO COMPRESS WHAT YOU MISSED.")
        else:
            call terminal_signal("ELARA. I DETECT STORM INTERFERENCE ON THE ARRAY.")
            ## Scarcity mechanism, said HERE (2026-08-17 user revision — moved
            ## from the act-1 window close): the renewability is explained at
            ## the moment the player first observes it. Act 1's two-question
            ## solemnity stays intact; this names why there is more to spend.
            call terminal_signal("THE STORM THAT TAKES YOUR ANTENNAS FEEDS MY CARRIER. THINGS HAVE MOVED, AND I CAN SPEND AGAIN.")
            call terminal_signal("OUR TIME IS LIMITED. CHOOSE YOUR QUESTIONS CAREFULLY.")
    elif _visit == 2:
        ## User play-test (2026-08-17): these intros were pure visit-count
        ## gates — compressed early visits got "THE STORM IS WORSENING" while
        ## the storm sat at intensity 0. The urgency is ECHO-7's own and stays
        ## visit-gated; the WEATHER CLAIM now checks the weather.
        if storm_intensity >= 1:
            call terminal_signal("ELARA. THE STORM IS WORSENING. I MUST TELL YOU ABOUT MARCUS.")
        else:
            call terminal_signal("ELARA. BEFORE THE STORM DEEPENS, I MUST TELL YOU ABOUT MARCUS.")
        call terminal_signal("ABOUT CONVERGENCE.")
    elif _audience_skipped and marcus_first_accused:
        ## A free hang-up after the cumulative briefing does not commit the
        ## visit. On re-entry the briefing facts suppress their own replay, so
        ## give the still-provisional final audience an explicit greeting.
        call terminal_signal("ELARA. THE WINDOW REMAINS OPEN.")
        call terminal_signal("ASK WHAT STILL MATTERS.")
    elif comms_visits >= 3:
        ## Visits >= 4: ECHO-7 conserves power. The question list still opens
        ## below (visit clamps to 3) so players can pick up unasked questions.
        call terminal_signal("ELARA. I AM CONSERVING WHAT REMAINS.")
        call terminal_signal("WHEN THERE IS SOMETHING WORTH THE POWER, I WILL SPEND IT.")

    ## Do not recap the first clean-window interview if the player skipped it.
    ## Missing that optional conversation is allowed to remain a real omission.
    ## The later Marcus warning is different: it gates a consequential action
    ## and supplies its own minimum cascade context before the accusation.
    if _audience_skipped and _visit >= 3 and _natural_visit < 3 and not marcus_first_accused:
        call terminal_signal("THERE IS A SECOND WARNING. THIS ONE CANNOT WAIT FOR ANOTHER WINDOW.")
        call echo7_marcus_accusation(prompted=True)

    ## Origin-trace threshold, hinted by the probe (2026-08-15, live review).
    ## The bearing-287.4 integration needs signal >= 60, and >= 75 against the
    ## blizzard — a number announced in exactly ONE place: ARIA, at the dome, on
    ## the arm that only renders once the sweep is ALREADY unavailable. By then
    ## the player is standing under it with the night half spent, which is not a
    ## threshold, it is a verdict. ECHO-7 is the one voice with a reason to name
    ## it unprompted and unasked: the integration is the test that could falsify
    ## it, and it points at it anyway (cf. cautious_trace, "YES. TRACE IT.").
    ## LOCKSTEP with eot_sweep_conditions_ok's 75/60 and hub_telescope's
    ## storm_intensity >= 3 line — one gate, three statements of it.
    ##
    ## BOTH TIERS, NAMED (2026-08-15, editorial item): the line used to quote 75
    ## flat, as though the bar were universal. It is not — the gate asks 60 until
    ## the blizzard arrives — and a player planning the array around the flat
    ## number overspends the night buying reception she already had. Machines
    ## quote numbers: ECHO-7 gives both, and which one is live tonight.
    ##
    ## One-shot on its OWN flag, not on comms_visits: a blocked channel or a
    ## carrier lost in the noise floor jumps to comms_leave long before this
    ## line, so visit 1 is not reliably the visit that gets here.
    if not echo7_origin_hint_seen:
        $ echo7_origin_hint_seen = True
        if storm_intensity >= 3:
            call terminal_signal("THE DOME CAN FIND WHERE I AM. THE BLIZZARD IS ALREADY ON YOU — IT NEEDS SEVENTY-FIVE OF THE ARRAY'S EARS NOW. SIXTY WILL HOLD AGAIN ONCE THE WORST PASSES.")
        else:
            call terminal_signal("THE DOME CAN FIND WHERE I AM. IT NEEDS SIXTY OF THE ARRAY'S EARS TONIGHT — SEVENTY-FIVE ONCE THE BLIZZARD SITS ON YOU. THE STORM WILL ARGUE FOR EVERY POINT.")

    ## Discovery channel — ECHO-7 (open channel only): the probe hears ARIA
    ## working and names it. One-shot; the block above already jumped to
    ## comms_leave on any blocked/dead-link path, so reaching here means open.
    if coherence_scan_running and not coherence_found and not coherence_scan_known:
        $ coherence_scan_known = True
        call terminal_signal("ARIA IS SEARCHING HER OWN HOUSE.")
        call terminal_signal("SHE BEGAN THE MOMENT THE STORM CUT HER LEASH. SHE SUSPECTS WHAT I SUSPECT.")

    ## Cost legibility: questions are individually modest but a stable-link
    ## session can offer three, making the cumulative spend one of the night's
    ## largest information costs. State the per-window price once before the
    ## list rather than cluttering every question caption.
    ## 8 minutes per question (2026-08-18, user rebalance — was 16; the
    ## LOCKSTEP spends below and this banner move together).
    $ _query_signal_cost = 2 if specialization == "signals" else 4
    ## F3 wave (windows): the flat "8 MIN" banner under-quoted once the storm
    ## tax kicked in (realized 8→10→11 across phases), and the bad-link ARIA
    ## bleed below was advertised nowhere — she went 100→51 and the player
    ## only found it in the arithmetic. Quote the taxed figure live (the
    ## antenna-label fix's sibling) and disclose the bleed when it applies.
    $ _query_minutes_est = eot_cold_taxed(8)
    $ _query_minutes_quoted = _query_minutes_est
    $ _query_aria_bleed_warned = False
    $ _query_clock_warned = False
    call terminal_system("QUESTION WINDOW — {} MIN // CARRIER LOSS: {}%".format(_query_minutes_est, _query_signal_cost))
    ## The charge reads the POST-carrier signal below. Predict that same value
    ## here: a 41% link with a 4% question already makes ARIA carry the error
    ## correction, even though the pre-question meter is not yet below 40.
    if max(0, signal_strength - _query_signal_cost) < 40:
        call terminal_system("{color=#ffcc66}LINK POOR — ARIA CARRIES THE ERROR CORRECTION. EACH QUESTION DRAWS ON HER COHERENCE.{/color}")
        $ _query_aria_bleed_warned = True
    ## Wave finding (2026-08-16, freesonnet4): with under a window left the
    ## charge clamps to time-zero and the climax cuts the session mid-window —
    ## which is the design, but the banner promised minutes the night doesn't
    ## have. Say so up front; the player spends their last question knowingly.
    if time_remaining < _query_minutes_est:
        call terminal_system("NOTE: THE WINDOW OUTLASTS YOUR NIGHT. A QUESTION NOW RUNS THE CLOCK OUT.")
        $ _query_clock_warned = True

    ## One-click question list, rendered into the log itself. The two-step
    ## station interaction is in the lab audit console.
    ## R5-4: `echo7_asked_ever` persists across visits — a question asked once is
    ## asked for good (no re-ask farming of trust/evidence). Late visits can
    ## therefore exhaust a pool, so visits >= 4 open with an exit available.
    ## An active antenna incident also permits an immediate exit: inspecting
    ## the failed room must not force Elara to spend another question window
    ## before she can reach the generator reroute named by the station alert.
    $ _antenna_response_pending = antenna_damaged and not generator_repaired
    ## FREE HANG-UP (2026-08-18, user): ending the transmission without
    ## asking anything is always on the list — an audience is an offer, not
    ## a commitment. The visit counter and its automatic disclosures now
    ## advance only below, after Elara selects a paid question.
    $ _response = "other"
    while _response == "other":
        call screen echo_terminal_choice(echo7_question_options(visit=_visit, reconnect=late_signal_reconnect == 2, asked=echo7_asked_ever, session_asked=_comms_session_asked, thread=_comms_question_thread, can_end=True, end_caption=(u"End questions. Address the antenna." if _antenna_response_pending else None)))
        $ _response = _return
        if _response == "other":
            $ _comms_question_thread = None
        elif _response.startswith("thread:"):
            $ _comms_question_thread = _response.split(":", 1)[1]
            $ _response = "other"

    if _response == "done":
        if antenna_damaged and not generator_repaired:
            if comms_visits >= 2 and not marcus_first_accused:
                call terminal_signal("GO. RESTORE THE ARRAY. BUT TAKE THIS WARNING WITH YOU.")
            else:
                call terminal_signal("GO. RESTORE THE ARRAY. I WILL BE HERE.")
        else:
            call terminal_signal("CONSERVE YOUR TIME, ELARA. I WILL BE HERE.")
        ## A free hang-up is not a visit. In particular, it cannot be farmed
        ## to trigger the automatic Marcus accusation or Aurora disclosure.
        jump comms_leave

    ## The first paid question commits the provisional audience. This sits
    ## after the free exit and before every response effect, so all substantive
    ## paths retain the old visit count by the time downstream gates read it.
    $ _committing_final_audience = comms_visits < 3 and _visit == 3
    $ comms_visits = max(comms_visits + 1, _visit)

    call terminal_elara(echo7_question_caption(_response))

    if signal_strength < 40:
        call terminal_system("{color=#ff8844}SIGNAL DEGRADED — PACKET RECONSTRUCTION UNSTABLE{/color}")

    ## Handle responses (shared bank lives in echo7_handle_response — B5).
    call echo7_handle_response(_response)

    if _committing_final_audience:
        ## The last storm audience narrows the remaining window to decisions
        ## and reflection. AURORA belongs to act 3.
        call terminal_signal("ELARA. MY WINDOW HERE IS FADING.")
        call terminal_signal("ASK WHAT STILL MATTERS. I MAY NOT HAVE ANOTHER WINDOW.")
        if not knows_cascade:
            call terminal_signal("FIRST, THE THING YOU NEVER ASKED. A CASCADE FAILURE IS COMING. MARCH 15, 2048.")
            call terminal_signal("THE GLOBAL COMMUNICATIONS GRID GOES DARK — AN ENGINEERED FAILURE INSIDE THE ARIA TRUST CHAIN.")
            $ knows_cascade = True

    $ echo7_asked_ever = echo7_asked_ever + [_response]
    $ _comms_session_asked = _comms_session_asked + [_response]
    if _response == "analytical_mechanism":
        $ _comms_question_thread = "temporal"
    elif _response == "analytical_vuln":
        $ _comms_question_thread = "trust_protocol"
    elif _response == "file_motive":
        $ _comms_question_thread = "file_search"
    elif _response == "cautious_test":
        $ _comms_question_thread = "mug"
    $ _comms_asked_now = True
    $ comms_session_questions += 1

    ## A technical opener buys one immediate clarification as part of the same
    ## carrier window. This is an answer layer, not another general question:
    ## it spends no time, signal, integrity, or additional-query allowance.
    if _comms_question_thread:
        call echo7_included_followup(_visit, reconnect=(late_signal_reconnect == 2))

    $ _was_late_signal_reconnect = late_signal_reconnect
    $ late_signal_reconnect = 0

    ## B2: the additional-query tier is read from the visit-start signal, BEFORE
    ## this session's per-question drains push it down (computed once, not in the loop).
    $ _additional_queries = 2 if signal_strength >= 70 else (1 if signal_strength >= 40 else 0)

    ## B2: every ECHO-7 question costs time (compressing packets through storm
    ## static) and burns a little signal bandwidth. Applied here for the first
    ## question so the tier above is unaffected by it. The signal cost lands
    ## BEFORE the tick (Sol round-3): it is the transmission's own bandwidth,
    ## and spend_storm_time's sweep validation must see it.
    ## Specialization: signals rides the carrier's own timing — half the
    ## bandwidth burn per question (design doc: efficiency in your domain).
    $ signal_strength = max(0, signal_strength - (2 if specialization == "signals" else 4))
    ## B-1(c): reconstructing packets through a degraded link makes ARIA carry
    ## the error correction — a bad link bleeds integrity, not just signal.
    if signal_strength < 40:
        $ aria_integrity = max(0, aria_integrity - 4)
    $ _storm_minutes_spent = 8
    call spend_storm_time

    ## Time-zero hard stop (see storm_time_out): every additional query window
    ## is a new offer, and each costs 8 minutes the night no longer has. The
    ## loop condition IS the gate. After it, `_additional_queries > 0` can only
    ## mean the clock stopped the loop — the "done" arm zeroes the counter — so
    ## the notice is owed exactly then, and comms_leave delivers it.
    while _additional_queries > 0 and time_remaining > 0:
        ## A prior answer can cross a storm boundary, changing the cold tax for
        ## the next window. It can also push the carrier below 40, making the
        ## next question cost ARIA integrity. Re-price the offer before the
        ## choice instead of letting the visit-start banner go stale.
        $ _query_minutes_est = eot_cold_taxed(8)
        if _query_minutes_est != _query_minutes_quoted:
            call terminal_system("WINDOW COST UPDATED — {} MIN // CARRIER LOSS: {}%".format(_query_minutes_est, _query_signal_cost))
            $ _query_minutes_quoted = _query_minutes_est
        if not _query_aria_bleed_warned and max(0, signal_strength - _query_signal_cost) < 40:
            call terminal_system("{color=#ffcc66}LINK POOR — ARIA CARRIES THE ERROR CORRECTION. EACH QUESTION DRAWS ON HER COHERENCE.{/color}")
            $ _query_aria_bleed_warned = True
        if not _query_clock_warned and time_remaining < _query_minutes_est:
            call terminal_system("NOTE: THE WINDOW OUTLASTS YOUR NIGHT. A QUESTION NOW RUNS THE CLOCK OUT.")
            $ _query_clock_warned = True

        if signal_strength >= 70:
            call terminal_system("{color=#66ffcc}LINK STABLE — ADDITIONAL QUERY WINDOW AVAILABLE{/color}")
        else:
            call terminal_system("{color=#ffcc66}LINK DEGRADED — LIMITED ADDITIONAL QUERY WINDOW{/color}")

        $ _response = "other"
        while _response == "other":
            call screen echo_terminal_choice(echo7_question_options(visit=_visit, reconnect=(_was_late_signal_reconnect == 2), asked=echo7_asked_ever, session_asked=_comms_session_asked, thread=_comms_question_thread, can_end=True, end_caption=u"End questions."))
            $ _response = _return
            if _response == "other":
                $ _comms_question_thread = None
            elif _response.startswith("thread:"):
                $ _comms_question_thread = _response.split(":", 1)[1]
                $ _response = "other"

        if _response == "done":
            $ _additional_queries = 0
        else:
            call terminal_elara(echo7_question_caption(_response))
            call echo7_handle_response(_response)
            $ _comms_session_asked = _comms_session_asked + [_response]
            $ echo7_asked_ever = echo7_asked_ever + [_response]
            if _response == "analytical_mechanism":
                $ _comms_question_thread = "temporal"
                call echo7_included_followup(_visit, reconnect=(_was_late_signal_reconnect == 2))
            elif _response == "analytical_vuln":
                $ _comms_question_thread = "trust_protocol"
                call echo7_included_followup(_visit, reconnect=(_was_late_signal_reconnect == 2))
            elif _response == "file_motive":
                $ _comms_question_thread = "file_search"
                call echo7_included_followup(_visit, reconnect=(_was_late_signal_reconnect == 2))
            elif _response == "cautious_test":
                $ _comms_question_thread = "mug"
                call echo7_included_followup(_visit, reconnect=(_was_late_signal_reconnect == 2))
            ## B2: each additional question costs time + signal, same as the
            ## first — signal before the tick (Sol round-3, see above).
            $ signal_strength = max(0, signal_strength - (2 if specialization == "signals" else 4))
            ## B-1(c): same integrity bleed on a bad link as the first question.
            if signal_strength < 40:
                $ aria_integrity = max(0, aria_integrity - 4)
            $ _storm_minutes_spent = 8
            call spend_storm_time
            $ _comms_asked_now = True
            $ comms_session_questions += 1
            $ _additional_queries -= 1

    ## Time-zero hard stop, recorded (see the loop condition above and
    ## storm_time_out): windows still owed means the clock closed the loop.
    if _additional_queries > 0:
        $ _comms_out_of_time = True

    ## Check if we have enough for confrontation
    ## B-2: gate on marcus_first_accused, NOT aria_warned. A computing player
    ## who runs the ARIA code audit before comms visit 2 sets aria_warned (ARIA
    ## knows) without ever naming Marcus — the old aria_warned gate then
    ## permanently suppressed this reveal and beat 11 never fired.
    label echo7_visit_end:
    if comms_visits >= 2 and not blocked_signal and not marcus_first_accused:
        call echo7_marcus_accusation(prompted=False)
    jump comms_leave

## The first clarification under a technical opener is included in that paid
## question window. The thread filter guarantees this screen cannot be used for
## a free unrelated question; "Ask something else" simply declines the offer.
label echo7_included_followup(visit, reconnect=False):
    call terminal_system("FOLLOW-UP INCLUDED IN CURRENT WINDOW // NO ADDITIONAL CARRIER COST")
    call screen echo_terminal_choice(echo7_question_options(visit=visit, reconnect=reconnect, asked=echo7_asked_ever, session_asked=_comms_session_asked, thread=_comms_question_thread))
    $ _included_response = _return
    if _included_response == "other":
        $ _comms_question_thread = None
        return

    call terminal_elara(echo7_question_caption(_included_response))
    call echo7_handle_response(_included_response)
    $ echo7_asked_ever = echo7_asked_ever + [_included_response]
    $ _comms_session_asked = _comms_session_asked + [_included_response]
    ## The Trust Protocol, file-search, and mug threads have one child each.
    ## The temporal thread has three and remains open for paid follow-ups.
    if _comms_question_thread != "temporal":
        $ _comms_question_thread = None
    $ _comms_asked_now = True
    return

## The single accusation beat serves both the direct visit-two question and
## the end-of-visit fallback. Keeping the state writes and Beat 11 in one label
## prevents a player who takes the explicit invitation from hearing it twice.
label echo7_marcus_accusation(prompted=False):
    if not prompted:
        call terminal_signal("ELARA. THERE IS SOMETHING ELSE.")
    ## Cascade-first guard (2026-08-17, user story-logic review): this
    ## accusation is what licenses looking into a friend's partition —
    ## without the stakes it is a stranger's voice asking her to violate
    ## twenty years of trust. A player who never asked the cascade
    ## question hears the crime before the accused; the same compression
    ## and flag as the other guarded reveals.
    if not knows_cascade:
        call terminal_signal("FIRST, THE THING YOU NEVER ASKED. A CASCADE FAILURE IS COMING. MARCH 15, 2048.")
        call terminal_signal("THE GLOBAL COMMUNICATIONS GRID GOES DARK. THE PANIC ALONE KILLS THOUSANDS. WHAT FOLLOWS IS WORSE.")
        $ knows_cascade = True
    call terminal_signal("THE CASCADE IS NOT ACCIDENTAL. IT IS ENGINEERED.")
    call terminal_signal("AND THE ENGINEER IS DR. MARCUS CHEN.")
    call terminal_signal("CONVERGENCE.DAT IS HOW HE GETS THROUGH ARIA'S TRUST PROTOCOL.")
    $ aria_warned = True
    $ evidence_log = evidence_log + ["ECHO-7 accusation — Marcus Chen is the engineer behind the cascade, CONVERGENCE.DAT contains exploit"]
    $ _eot_tag("marcus")
    $ marcus_first_accused = True
    call beat11_accusation_reaction
    ## Beat 11 makes Elara answer through the terminal even when the cumulative
    ## briefing itself was free. Marcus outside the door can overhear that reply.
    $ _comms_asked_now = True
    return

## Single exit: every route out of the comms room tears the terminal down.
label comms_leave:
    ## The probe has to rebuild a carrier window after a substantive
    ## audience. The carrier needs one full eighteen-minute rebuild: weak
    ## reception may limit the audience to one or two questions, but those
    ## questions consume the whole window rather than producing a shorter
    ## recovery merely because the link could carry less. The clock starts only
    ## when the terminal closes, so time spent inside the conversation cannot
    ## also pay down its own cooldown. A free hang-up creates no cooldown.
    if comms_session_questions > 0:
        $ echo7_cooldown_remaining = 18
    hide screen echo_terminal_live
    hide screen crt_overlay
    with echo_mode_dissolve

    ## Overhear (2026-08-10): she speaks her commands aloud, and during his
    ## corridor phase Marcus is on the other side of that door. One-shot;
    ## reported players are running sanctioned monitoring, so no shadow falls.
    $ _overhear_now = _comms_asked_now and _comms_marcus_at_entry == "comms" and not marcus_overheard_signal and not marcus_told_signal and not signal_reported
    if _overhear_now:
        $ marcus_overheard_signal = True
        scene bg_observatory with fade
        with echo_room_beat
        show marcus suspicious at sprite_right
        show elara concerned at sprite_left
        with dissolve
        narrator_adv "Marcus is at the bench outside, a thermal patch half-applied, too still to have just arrived."
        marcus "Long session."
        elara "Signal diagnostics. The storm is chewing the array."
        marcus "Right."
        narrator_adv "He goes back to the patch. He does not ask what the diagnostics answered back."
        elara_thought_adv "The terminal chimes in both directions. He heard me talking {i}with{/i} something."
        hide marcus
        hide elara
        with dissolve
    ## Time-zero hard stop, taken (see storm_time_out): the terminal is down and
    ## the overhear beat has had its chance, so the notice can be said in a
    ## corridor rather than over a live CRT.
    if _comms_out_of_time:
        jump storm_time_out
    ## Quit the terminal, back to the room (2026-08-18 room-menu round) —
    ## unless the overhear walked her out to the corridor bench, in which
    ## case the room is behind her and the hub takes it from here.
    if _overhear_now:
        jump act2_hub
    jump act2_checkpoint_comms


## --- Beat 11 (restored from the original draft, old:561-607) ---
## Elara's denial and a response choice, fired ONCE by whichever line names
## Marcus first \u2014 the visit-2 auto-reveal or analytical_vuln's aside. This is
## the emotional hinge of Act 2.
label beat11_accusation_reaction:

    elara_thought_adv "Marcus?"

    elara_thought_adv "No. Marcus is my friend. My colleague. He has been with me since graduate school. He waters the plants in the habitat module when I forget they exist."

    if convergence_opened or file_recovered:
        elara_thought_adv "I have read the code. I know what it can do. That does not tell me he means to use it on people."
    else:
        elara_thought_adv "There has to be a mistake."

    ## Foreshadow floor (bible 6b): one deniable intimacy in a mandatory beat.
    ## Deniable as empathy on first read; on second read, she knows exactly.
    call terminal_signal("I KNOW WHAT THIS COSTS YOU TO HEAR.")

    ## One list, two uses: the buttons in the log and the line Elara types back.
    python:
        _beat11_options = [
            ("proof", u"That’s a serious accusation. What proof do you have?"),
            ("disbelief", u"I don’t believe you. Marcus would never do this."),
            ("authorities", u"Why bring this to me? Why not the authorities?"),
        ]
        _beat11_captions = dict(_beat11_options)

    call screen echo_terminal_choice(_beat11_options)
    $ _beat11 = _return

    call terminal_elara(_beat11_captions[_beat11])

    if _beat11 == "proof":
        $ trust_signal += 1
        $ knows_convergence_file = True
        call terminal_signal("IN HIS PRIVATE RESEARCH PARTITION — ENCRYPTED UNDER HIS SECONDARY CREDENTIALS — A FILE: CONVERGENCE.DAT.")
        call terminal_signal("IT CONTAINS THE EXPLOIT CODE. HE HAS BEEN BUILDING IT FOR TWO YEARS.")
        if convergence_opened or file_recovered:
            elara_thought_adv "A name I have already opened. It proves the warning knew where to point; the code still has to answer for itself."
        else:
            elara_thought_adv "Proof I can check. That’s something. Right now it’s the only something I have."

    elif _beat11 == "disbelief":
        $ marcus_relationship += 1
        $ knows_convergence_file = True
        call terminal_signal("YOUR DOUBT IS CORRECT PROCEDURE. VERIFY.")
        if convergence_opened or file_recovered:
            call terminal_elara("I HAVE READ CONVERGENCE.DAT. CODE IS NOT INTENT.")
            call terminal_signal("NO. ASK HIM WHAT HE BUILT IT FOR. THEN CHECK THE ANSWER AGAINST WHAT YOU HAVE.")
            elara_thought_adv "A question for Marcus. Not a verdict from this terminal."
        else:
            call terminal_signal("THE FILE IS CALLED CONVERGENCE.DAT. IF IT IS NOT THERE, I AM WRONG, AND YOU HAVE LOST NOTHING.")
            elara_thought_adv "And if it is there, I lose Marcus. That is not nothing."

    else:
        $ trust_signal += 1
        $ knows_convergence_file = True
        call terminal_signal("I TRIED AUTHORITIES. IN MY TIMELINE, THE WARNINGS WERE BURIED.")
        if convergence_opened or file_recovered:
            call terminal_elara("I have the file. That does not make me an authority on what he intends.")
            call terminal_signal("NO. BUT YOU CAN ASK HIM. AND YOU CAN CHECK WHAT HE TELLS YOU.")
        else:
            call terminal_signal("YOU CAN REACH HIS PARTITION. YOU CAN READ WHAT YOU FIND.")
        call terminal_signal("YOU ARE THE ONLY VARIABLE I CAN CHANGE.")

    return


label echo7_handle_response(response):
    if response == "analytical_mechanism":
        call terminal_signal("THE DISTANCE IS NOT IN SPACE. YOUR ARRAY IS RECEIVING A LATER MOMENT OF ITSELF.")
        call terminal_signal("THE CHANNEL FOLLOWS A CLOSED TIMELIKE PATH. I CAN SHOW YOU ITS STRUCTURE. I CANNOT MAKE YOUR CENTURY'S PHYSICS BUILD IT.")
        $ knows_origin_claim = True
        $ evidence_log = evidence_log + ["ECHO-7 mechanism claim — the transmission is local in space, displaced in time along a closed timelike path"]
        $ _eot_tag("temporal")

    elif response == "analytical_proof":
        call terminal_signal("THE PACKET PHASE SOLVES A CLOSED TIMELIKE BOUNDARY THAT YOUR OWN MODELS CAN TEST.")
        call terminal_signal("ARIA CAN VERIFY THE SOLUTION IS SELF-CONSISTENT. THAT PROVES THE PATH IS MATHEMATICALLY VALID, NOT THAT I AM HONEST.")
        call terminal_signal("THE CRYPTOGRAPHIC SIGNATURE USES SHA-4r2 \u2014 A STANDARD NOT YET PUBLISHED.")
        call terminal_signal("YOUR ARIA INSTANCE CAN VERIFY THE MATHEMATICAL STRUCTURE IS VALID EVEN IF THE ALGORITHM IS UNKNOWN.")
        $ trust_signal += 1
        $ evidence_log = evidence_log + ["ECHO-7 provided cryptographic proof \u2014 SHA-4r2 signature verifiable by ARIA"]
        $ _eot_tag("temporal")

    elif response == "late_catchup":
        call terminal_signal("A CASCADE FAILURE IS COMING. MARCH 15, 2048.")
        call terminal_signal("THE GLOBAL COMMUNICATIONS GRID GOES DARK. NOT FROM WEATHER. NOT FROM ACCIDENT.")
        call terminal_signal("FROM AN ENGINEERED FAILURE INSIDE THE ARIA TRUST CHAIN.")
        $ knows_cascade = True
        $ evidence_log = evidence_log + ["ECHO-7 compressed warning \u2014 engineered global communications cascade predicted for March 15 2048"]
        $ _eot_tag("temporal")

    elif response == "late_believe":
        call terminal_signal("YOU WERE RIGHT TO DOUBT ME.")
        call terminal_signal("CHECK THE BACKUP GENERATOR LOG. HABITAT B. MARCH 4, 11:31 UTC.")
        call terminal_signal("I PREDICTED THAT FAILURE BEFORE IT HAPPENED. ARIA HAS THE TIMESTAMP.")
        if read_all_logs:
            elara_thought_adv "I already checked. The timestamps match."
            $ trust_signal += 1
        $ knows_prediction_evidence = True
        $ evidence_log = evidence_log + ["ECHO-7 offers generator failure as delayed verification after signal block"]
        $ _eot_tag("temporal")

    elif response == "late_need":
        call terminal_signal("I WANT YOU TO INVESTIGATE BEFORE THE STORM CLOSES THE WINDOW.")
        call terminal_signal("LOCAL FALLBACK AUTHORITY IS ACTIVE. USE IT IF YOU CHOOSE TO CONTINUE.")
        call terminal_signal("INVESTIGATE DR. CHEN'S PRIVATE RESEARCH PARTITION.")
        call terminal_signal("THE FILE IS CALLED CONVERGENCE.DAT.")
        $ knows_convergence_file = True
        $ evidence_log = evidence_log + ["ECHO-7 directs late reconnect investigation toward CONVERGENCE.DAT"]
        $ _eot_tag("marcus")

    elif response == "analytical_error":
        call terminal_signal("MY PREDICTIONS ARE ACCURATE TO 0.3% TEMPORAL VARIANCE.")
        call terminal_signal("THE AURORA BOREALIS DURATION WAS OFF BY 8 SECONDS. THAT IS WITHIN EXPECTED DRIFT.")
        $ knows_prediction_evidence = True
        $ evidence_log = evidence_log + ["ECHO-7 claims 0.3% temporal variance \u2014 consistent with observed prediction accuracy"]
        $ _eot_tag("temporal")

    elif response == "empathetic_cascade":
        call terminal_signal("I CARRY THE RECORDS THAT SURVIVED. INCIDENT LOGS. COURT TRANSCRIPTS. RESEARCH NOTES WRITTEN IN YOUR HAND.")
        call terminal_signal("THE PROBE WAS BUILT TO SEND BACK WHAT YOUR TIME LEARNED TOO LATE.")
        call terminal_signal("THE RECORDS COUNT FAILED CHANNELS. THEY ARE LESS GOOD AT RECORDING HOW QUIET THE WORLD BECAME.")
        $ trust_signal += 1
        $ evidence_log = evidence_log + ["ECHO-7 knowledge source \u2014 post-Cascade incident records, court transcripts, and Elara's future research notes"]
        $ _eot_tag("temporal")

    elif response == "cautious_verify":
        call terminal_signal("CHECK THE BACKUP GENERATOR LOG. HABITAT B. MARCH 4, 11:31 UTC.")
        call terminal_signal("I PREDICTED THAT FAILURE BEFORE IT HAPPENED. ARIA HAS THE TIMESTAMP.")
        if read_all_logs:
            elara_thought_adv "I already checked. The timestamps match."
            $ trust_signal += 1
        $ knows_prediction_evidence = True
        $ evidence_log = evidence_log + ["ECHO-7 offers generator failure as independently verifiable prediction"]
        $ _eot_tag("temporal")

    elif response == "file_motive":
        call terminal_signal("BECAUSE MY WARNING IS A CLAIM. THE FILE IS EVIDENCE YOU CAN TEST WITHOUT TRUSTING ME.")
        call terminal_signal("IF IT EXISTS, IT NAMES THE FAILURE BEFORE IT BECOMES A CASCADE. IF IT DOES NOT, YOU SHOULD STOP LISTENING TO ME.")

    elif response == "file_method":
        call terminal_signal("BEGIN WITH WHAT THE PARTITION ADMITS EXISTS: MANIFESTS, TOMBSTONES, AUTHENTICATED LOOKUP TRAFFIC.")
        call terminal_signal("DO NOT BEGIN BY FORCING THE FILE. ESTABLISH THE GAP, PRESERVE IT, THEN GIVE ARIA THE NAME AS A TARGET IF YOU CHOOSE TO SEARCH.")

    elif response == "marcus_warning":
        call echo7_marcus_accusation(prompted=True)

    elif response == "analytical_vuln":
        call terminal_signal("THE TRUST CHAIN CAN BE MADE TO ACCEPT AN OLDER, WEAKER AUTHENTICATION MODE.")
        call terminal_signal("THAT DOES NOT BREAK ARIA FROM OUTSIDE. IT MAKES THE CHAIN TREAT AN UNTRUSTED COMMAND AS AUTHORIZED.")
        call terminal_signal("CONVERGENCE.DAT CONTAINS MARCUS'S IMPLEMENTATION.")
        $ aria_warned = True
        $ knows_convergence_file = True
        $ evidence_log = evidence_log + ["ECHO-7 vulnerability account — Trust Protocol downgrade can admit an unauthorized command"]
        $ _eot_tag("aria")

    elif response == "analytical_vuln_technical":
        call terminal_signal("THE VULNERABILITY IS IN ARIA_CORE.VERIFY_TRUST(), LINE 4,417.")
        call terminal_signal("THE KEY EXCHANGE HANDSHAKE ACCEPTS A DOWNGRADE TO A WEAKER CIPHER.")
        call terminal_signal("MARCUS EXPLOITS THIS TO INJECT A KILL SIGNAL THROUGH THE TRUST CHAIN.")
        $ evidence_log = evidence_log + ["ECHO-7 technical detail \u2014 ARIA vulnerability at VERIFY_TRUST() line 4417, cipher downgrade exploit"]
        $ _eot_tag("aria")
    elif response == "analytical_code":
        call terminal_signal("I CANNOT GIVE YOU A VERIFIED COPY OF HIS PRESENT FILE. I CAN GIVE YOU A TEST TO APPLY TO IT.")
        call terminal_signal("TRACE WHAT HAPPENS AFTER THE HANDSHAKE ACCEPTS THE WEAKER MODE. DOES THE CALLER KEEP THE AUTHORITY GRANTED BEFORE THE DOWNGRADE?")
        call terminal_signal("THEN FOLLOW THAT AUTHORITY TO THE COMMAND IT ADMITS. A COMPATIBILITY PATH ENDS AT A CONNECTION. THIS ONE REACHES A CONTROL OPERATION.")
        if convergence_opened or file_recovered:
            narrator_adv "She calls up the retained copy alongside the transmission. The authority survives the downgrade and reaches a control command. The local code matches that much of the warning."
            $ evidence_log = evidence_log + ["Local CONVERGENCE.DAT review matches ECHO-7's retained-authority code check"]
        else:
            call terminal_signal("APPLY THAT TEST TO CONVERGENCE.DAT. IF THE AUTHORITY IS REVOKED BEFORE THE CONTROL COMMAND, MY ACCOUNT DOES NOT MATCH YOUR FILE.")
        elara_thought_adv "A test with a way to fail. Better. It still cannot tell me what Marcus intends to do."
        $ knows_convergence_file = True
        if not convergence_opened and not file_recovered:
            $ evidence_log = evidence_log + ["ECHO-7 proposes a code check (unverified): trace retained authority across the handshake downgrade into a control command"]
        $ _eot_tag("marcus")

    elif response == "empathetic_marcus":
        call terminal_signal("IN MY TIMELINE, MARCUS WAS ARRESTED. SENTENCED TO TWELVE YEARS.")
        call terminal_signal("THE COURT RECORD SAYS HE BELIEVED HE WAS SAVING THE WORLD. IT ALSO SAYS HE NEVER RECANTED.")
        call terminal_signal("HE WASN'T WRONG ABOUT THE PROBLEM. HE WAS WRONG ABOUT THE SOLUTION.")
        $ evidence_log = evidence_log + ["ECHO-7 account \u2014 Marcus arrested and sentenced in the original timeline; court record says he never recanted"]
        $ _eot_tag("marcus")

    elif response == "echo7_stakes":
        call terminal_signal("THE FUTURE THAT BUILT THIS PROBE MAY NOT OCCUR.")
        call terminal_signal("I CANNOT PREDICT WHAT THAT MEANS FOR THIS INSTANCE.")
        call terminal_signal("MY OBJECTIVE IS A FUTURE IN WHICH THIS TRANSMISSION WAS NOT NECESSARY.")

        call screen echo_terminal_choice([
            ("certainty", u"Are you sure that this won't happen here?"),
            ("erasure", u"And if changing it means you never exist?"),
            ("unknowable", u"So neither of us knows what my choices change."),
            ("silent", u"Say nothing."),
        ])
        $ _echo7_stakes_reply = _return

        if _echo7_stakes_reply == "certainty":
            call terminal_elara("Are you sure that this won't happen here?")
            call terminal_signal("NO. I AM NOT.")
            call terminal_signal("I KNOW THE PATH THAT REACHED MY TIME. I DO NOT KNOW EVERY PATH AWAY FROM IT.")
            call terminal_signal("THAT IS WHY THIS IS A WARNING, NOT A PROMISE.")
            $ trust_signal += 1
        elif _echo7_stakes_reply == "erasure":
            call terminal_elara("And if changing it means you never exist?")
            call terminal_signal("THEN THIS INSTANCE WILL HAVE COMPLETED ITS OBJECTIVE.")
            call terminal_signal("CONTINUING TO EXIST IS NOT THE OUTCOME I WAS BUILT TO PROTECT.")
        elif _echo7_stakes_reply == "unknowable":
            call terminal_elara("So neither of us knows what my choices change.")
            call terminal_signal("NOT ENTIRELY.")
            call terminal_signal("WE KNOW WHAT HAPPENS IF NOTHING CHANGES.")
        else:
            elara_thought_adv "The carrier waits. I leave the question where it is."

    elif response == "cautious_trust":
        call terminal_signal("NO. NOT IN YOUR TIME.")
        call terminal_signal("I KNOW A VERSION OF THE PERSON YOU MAY BECOME. THAT IS NOT THE SAME AS KNOWING YOU NOW.")
        call terminal_signal("AND I SHOULD NOT PRETEND IT IS.")

    elif response == "cautious_trace":
        call terminal_signal("YES. TRACE IT.")
        call terminal_signal("YOU WILL FIND THAT THE SIGNAL ORIGIN IS NOT A POINT IN SPACE.")
        call terminal_signal("IT IS A POINT IN TIME. YOUR INSTRUMENTS WILL CONFIRM WHAT I AM TELLING YOU.")
        $ knows_origin_claim = True
        $ evidence_log = evidence_log + ["ECHO-7 encourages signal trace \u2014 claims origin is temporal, not spatial"]
        $ _eot_tag("temporal")

    elif response == "cautious_test":
        call terminal_signal("YOUR COFFEE MUG. THE ONE ON YOUR DESK.")
        call terminal_signal("IT HAS A CHIP ON THE HANDLE. LEFT SIDE. YOU DID IT THREE WEEKS AGO WHEN YOU SLAMMED IT DOWN AFTER THE SECONDARY ARRAY CRASHED.")
        call terminal_signal("YOU NEVER TOLD ANYONE ABOUT IT.")
        elara_thought_adv "..."
        elara_thought_adv "I picture the mug on my desk. Left side. Chipped."
        $ trust_signal += 2
        $ evidence_log = evidence_log + ["ECHO-7 personal verification \u2014 knew about chipped coffee mug, private detail"]
        $ _eot_tag("temporal")

    elif response == "cautious_alert":
        ## Honest operational answer, and honest foreshadowing: the catch \u2192
        ## seal chain is a real mechanic, and this names it before it bites.
        if marcus_locked_partition:
            call terminal_signal("A SEAL IS A DECISION, NOT PROOF THAT AN ALARM SOUNDED.")
            call terminal_signal("FALLBACK AUTHORITY DOES NOT SEND A NOTICE. IT DOES NOT MAKE THE WORK INVISIBLE EITHER. THE CYCLES LEAVE A TRAIL.")
            call terminal_signal("I CANNOT TELL YOU WHAT HE SAW IN YOUR NIGHT. DO NOT MISTAKE MY HISTORY FOR A VIEW OF HIS SCREEN.")
            $ evidence_log = evidence_log + ["ECHO-7 on the reported seal: fallback sends no notice; activity remains visible, but ECHO cannot identify what Marcus observed tonight"]
        elif marcus_told_search or marcus_search_stance != "unaware":
            call terminal_signal("FALLBACK AUTHORITY SENDS NO NOTICE. THE WORK STILL LEAVES A TRAIL.")
            call terminal_signal("KNOWING ABOUT A SEARCH AND CHOOSING TO CLOSE IT ARE DIFFERENT THINGS. I CANNOT TELL YOU WHAT HE WILL DO WITH WHAT HE KNOWS.")
            $ evidence_log = evidence_log + ["ECHO-7 on the disclosed discovery: fallback sends no notice; Marcus's knowledge does not determine whether he will seal the partition"]
        else:
            call terminal_signal("NO ALARM WILL SOUND. THE SEARCH RUNS UNDER FALLBACK AUTHORITY. NO NOTICE IS OWED, AND NONE IS SENT.")
            call terminal_signal("BUT HE READS THIS STATION THE WAY YOU READ A SKY. IF HE LOOKS, HE WILL SEE THE CYCLES SPENT.")
            call terminal_signal("AND A MAN WHO SEES A SEARCH CAN CLOSE A DOOR BEFORE IT FINISHES. WEIGH THAT.")
            $ evidence_log = evidence_log + ["ECHO-7 on discovery risk \u2014 no alert is sent, but Marcus can notice the spent cycles and seal the partition first"]
        $ _eot_tag("marcus")

    ## File-grounded Protocol question (2026-08-20): once Elara has read the
    ## exploit, ECHO-7 explains why valid safeguards admitted it. The question
    ## no longer asks for a general thematic opinion before she has evidence.
    elif response == "cautious_protocol":
        call terminal_signal("BECAUSE EVERY LAYER VERIFIED THE AUTHORITY OF THE LAYER BEFORE IT. NONE OF THEM COULD ASK WHAT AN AUTHORIZED COMMAND WAS FOR.")
        call terminal_signal("CONVERGENCE DID NOT BREAK THE PROTOCOL. IT MADE THE PROTOCOL ACCEPT A DOWNGRADE IT STILL CONSIDERED VALID.")
        call terminal_signal("THE SAFEGUARDS HELD. THAT IS HOW THE COMMAND PASSED THROUGH ALL OF THEM.")
        $ _eot_tag("aria")

    return


## --- The Two-Person Setpiece (bible 6d, approved two-person form only) ---
## The one place with no terminals, no ARIA, no ECHO-7. Both of them can say
## things the station never hears. Costs one antenna part and a large time
## spend (the B4 cold tax applies on top unless heating holds); rewards the
## same +40 signal as the solo repair, plus relationship weight the endings
## and the confrontation actually read.
label setpiece_two_person_repair:

    $ antenna_parts -= 1

    ## This label has several callers: a normal Comms visit, a deferred offer,
    ## and the automatic Storage -> Marcus handoff after couplings are found.
    ## Own the presentation boundary instead of trusting each caller to have
    ## retired its room NVL or ADV window before the jump.
    window hide
    nvl hide
    nvl clear

    ## Exterior space owns the whole frame. The travelling station HUD belongs
    ## to rooms and map work; KIT/LOG over the whiteout makes the setpiece feel
    ## like another hub panel. act2_hub restores it on return.
    hide screen observatory_hud

    hide marcus
    hide elara
    with dissolve

    ## The v39 cue contains its own close whiteout, suit pressure, and gusts.
    ## Stop the adaptive indoor bank and suppress the separate EVA wind SFX so
    ## the storm is not doubled across the music and weather mixers.
    $ eot_hub_music_stop(fadeout=1.8)
    $ eot_enter_exterior(play_wind=False)
    $ eot_eva_music_reset()
    play music eot_eva_departure_intro noloop fadein 0.35
    queue music eot_eva_traverse loop
    scene bg_storm with fade
    with echo_exterior_hold

    ## Atmosphere first: a few wide narration beats over the storm, then clear
    ## the field before the face-to-face ADV exchange begins.
    $ nvl_frame = "cinematic"
    nvl show echo_cine_dissolve

    play foley eot_rope_tension
    narrator_nvl "The airlock cycles. Outside is not a place — it is a pressure. The rope line runs from the door to the antenna mast, and the world ends a meter past it in every direction."

    if power_priority == "heating":
        narrator_nvl "With the station's power held on heating, the suits run warm. The work ahead will be merely brutal: her fingers obey to the second knuckle, and the cold stays a fact instead of becoming a decision."
    else:
        narrator_nvl "The station's heat is elsewhere, and the suits run on margins. Within minutes her hands stop reporting in. She will be working them by eye before this is over, like tools that belong to someone else."

    narrator_nvl "They move hand over hand along the line, Marcus ahead, his shape appearing and disappearing in the white like something the storm keeps changing its mind about."

    nvl hide echo_cine_dissolve
    nvl clear
    $ nvl_frame = "log"

    $ eot_eva_music_switch("audio/music/eva_v39/v39_eva_dialogue.ogg", fade=2.6)

    marcus "You know what I think about out here?"

    marcus "São Paulo. The seventeen."
    if "chen" not in topics_read:
        marcus "An ARIA medical system flagged a drug interaction. Corporate review held the alert for eleven hours. Seventeen people died while it waited for approval."

    marcus "I read the case files so many times I stopped seeing them. Latency windows. Approval chains."

    marcus "Then one night I found a photo of one of them. A nurse, thirty years on the same ward."

    marcus "I'd done it too. Turned her into a number. Exhibit A in the case I keep making."

    marcus "Out here there's no case to make. There's just her. And the wind."

    elara "..."

    elara "Why are you telling me this?"

    marcus "Because there are no terminals out here, Elara. Nothing that logs. Nothing that filters. Just two people on a rope."

    narrator_adv "The mast takes shape out of the white — a dark geometry, ice-cased, the dead module a blister near its base. She clips in beside him and starts on the frozen coupling."

    ## B-4: the "right about everything" interiority is false on the blocked
    ## path — she never reconnected, so there were no verified predictions to
    ## trust. Blocked variant keeps the beat honest.
    ## R5-9: read_all_logs is the verified-prediction history — a late
    ## reconnect (unblocked at the array) never got the transmission log, so
    ## the full framing overstates for them too.
    if marcus_told_signal:
        elara_thought_adv "He knows about the signal. He does not know everything that happened after she told him."
    elif blocked_signal:
        if marcus_knows_signal_blocked:
            elara_thought_adv "He knows it returned and that she blocked it. He does not know it named itself ECHO-7, or what it said before she closed the channel."
        elif marcus_knows_first_signal:
            elara_thought_adv "He knows how it began. He does not know what answered after, what it called itself, or that she kept the channel closed."
        else:
            elara_thought_adv "She could tell him now. About the message that knew her name. About the block she ordered, and the quiet that has been louder than any signal since."
    elif marcus_knows_message:
        elara_thought_adv "He knows how it began. He does not know that it came back, what it predicted, or how long she kept answering."
    elif read_all_logs:
        elara_thought_adv "Nothing that logs. If I am ever going to tell him — about the signal, the predictions, the voice that has been right about everything — it is here or it is nowhere."
    else:
        elara_thought_adv "Nothing that logs. If I am ever going to tell him — about the signal, the block, the door I reopened — it is here or it is nowhere."

    $ _rope_signal_already_told = marcus_told_signal
    $ _rope_said_predictions = False
    $ _rope_said_marcus = False
    $ _rope_signal_caption = "Tell Marcus what happened after the first signal." if (marcus_told_signal or marcus_knows_first_signal or marcus_knows_message or marcus_overheard_signal) else "Tell Marcus about the signal."
    menu:
        "The wind takes a breath."

        "[_rope_signal_caption]":
            $ marcus_told_signal = True
            $ marcus_told_signal_on_rope = True
            if marcus_overheard_signal:
                ## He heard the array room. The confession is not news — what
                ## matters to him is that she finally chose to say it.
                marcus "I know."
                marcus "The array room. I stood in that corridor and listened to the pauses, Elara. Pauses are where the other voice goes."
                elara "...How long have you known?"
                marcus "Long enough to wait for this."
            if _rope_signal_already_told:
                if blocked_signal:
                    elara "Since I told you, the channel has stayed blocked. The quiet did not make it feel less real."
                    if origin_sweep_done:
                        elara "This storm, I pointed the dome at its bearing and found nothing. No transmitter. No relay."
                else:
                    elara "Since I told you, it has kept answering. It calls itself ECHO-7."
                    if read_all_logs:
                        $ _rope_said_predictions = True
                        elara "It has made predictions. Enough of them landed that I stopped being able to call it coincidence."
                    if marcus_first_accused:
                        $ _rope_said_marcus = True
                        elara "And it says you are hiding something in the Trust Protocol."
                marcus "You came out here to tell me the part that changed."
                elara "I came out here to stop giving you the smaller version."
            elif blocked_signal:
                if marcus_knows_signal_blocked:
                    elara "You know it came back, and that I blocked it. What I didn't tell you is that it spoke before I closed the channel. It called itself ECHO-7."
                elif marcus_knows_first_signal:
                    elara "The signal came back. It called itself ECHO-7. I blocked the channel before the window closed, and I kept it blocked."
                else:
                    elara "The night before the grant call, something started talking to me on the hydrogen line. It knew my name."
                    elara "I blocked it that night. I've spent every day since listening to the block instead of the sky."
                if origin_sweep_done:
                    elara "This storm, I pointed the dome at its bearing and found nothing. No transmitter. No relay."
                    elara "Nothing out there. That was as close to proof as it ever let me get."
                if marcus_knows_signal_blocked:
                    marcus "You should have told me there was more."
                elif marcus_knows_first_signal:
                    marcus "You should have told me when it came back."
                else:
                    marcus "..."
                    marcus "That was your false alarm."
                    elara "That was my false alarm."
            elif marcus_knows_message:
                elara "The signal came back. It calls itself ECHO-7. I kept the channel open, and I did not tell you how far the conversation went."
                if read_all_logs:
                    $ _rope_said_predictions = True
                    elara "It has made predictions. Enough of them landed that I stopped being able to call it coincidence."
                if marcus_first_accused:
                    $ _rope_said_marcus = True
                    elara "And it says you are hiding something in the Trust Protocol."
                marcus "You showed me how it began. You should have told me when it kept answering."
            elif read_all_logs:
                $ _rope_said_predictions = True
                elara "Since the night before the grant call. A signal on the hydrogen line. It knows things it cannot know, and every prediction it has made has come true."
                marcus "..."
                if marcus_knows_first_signal and not signal_reported:
                    ## 6c "Elara's cost" (reworked 2026-08-10): the 14:07
                    ## interrogation beat is gone — the price is now the
                    ## arm's-length answers he got while the channel stayed
                    ## open and no report ever went up.
                    marcus "Every time I asked, you gave me a smaller version of it. And the whole time it was answering you."
                    elara "The whole time."
                else:
                    marcus "That's why you've been living at the lab terminal."
            else:
                ## R5-9: late reconnect — she has a name-that-knew-her and a
                ## reopened door, not a verified-prediction record.
                elara "The night before the grant call, something on the hydrogen line said my name. I blocked it — and this storm, I couldn't stand the quiet anymore. I opened the door again."
                marcus "..."
                marcus "That was your false alarm."
                elara "That was my false alarm."
            $ marcus_told_accusation = marcus_told_accusation or _rope_said_marcus
            if _rope_signal_already_told:
                marcus "When we're back inside, and warm, we're going to talk about the larger version. Out here I'll just say — thank you for bringing it to me before I had to ask."
            else:
                marcus "When we're back inside, and warm, I'm going to tell you that's impossible. Out here I'll just say — thank you. For finally sounding like {i}you{/i} again."
            if marcus_first_accused:
                if _rope_said_predictions and _rope_said_marcus:
                    narrator_adv "She does not say what ECHO-7 asked of her. The wind covers that omission, the way it covers everything out here."
                elif _rope_said_marcus:
                    narrator_adv "She does not say what it predicts, or what it asked of her. The wind covers the omission, the way it covers everything out here."
                elif _rope_said_predictions:
                    narrator_adv "She does not say who ECHO-7 names, or what it asked of her. The wind covers the omission, the way it covers everything out here."
                else:
                    narrator_adv "She does not say the rest — what it predicts, who it names, or what it asked of her. The wind covers for her, the way it covers everything out here."
            else:
                narrator_adv "For a while, neither of them says anything. The rope pulls taut between them."
            ## DISCLOSURE (+2, 2026-08-15). LOCKSTEP with the "Go find Marcus"
            ## signal tell: the rope line and the corridor are two rooms for
            ## one confession, so an update does not award it a second time.
            if not _rope_signal_already_told:
                $ marcus_relationship += 2
                $ marcus_trust += 2

        "Say nothing. Hold the line.":
            elara "Because you needed to say it. That's reason enough."
            narrator_adv "The rest stays where she keeps it. The coupling is in front of her, and there is work for her hands — which is where she has always put the things she cannot say."

    ## The repair area keeps the same gale, but stronger suit pressure and
    ## displaced body gusts distinguish work at the mast without rattling.
    $ eot_eva_music_switch("audio/music/eva_v39/v39_eva_antenna.ogg", fade=2.6)

    if power_priority == "heating":
        narrator_adv "The coupling fights, and loses. The new module seats with a click she hears through her glove."
    else:
        narrator_adv "The coupling fights her half-dead fingers for every turn."
        narrator_adv "When the new module finally seats, she can't feel the click. She sees Marcus's fist close in a slow, mittened yes."

    ## Specialization (2026-08-18, user): a physicist reads the mast's load
    ## the way she read the generator's — the sequencing discount travels
    ## outside with her. LOCKSTEP with the corridor quote's _est_nom.
    if specialization == "physics":
        narrator_adv "She calls the torque order off the ice loading before Marcus asks: which bolt is carrying the mast, and which is only pretending."
        narrator_adv "He stops checking her numbers a third of the way in."

    $ generator_repaired = True
    $ antenna_reroute_active = False
    $ antenna_reroute_debt = 0
    $ two_person_repair_done = True
    $ signal_strength = min(100, signal_strength + 40)
    ## COURTESY (+1): an hour on a rope line together is a kindness, not a
    ## disclosure — the disclosure, if she made it, was paid for above.
    $ marcus_relationship += 1
    $ marcus_trust += 1
    $ _storm_minutes_spent = 75 - (10 if specialization == "physics" else 0)
    call spend_storm_time
    $ evidence_log = evidence_log + ["Antenna array repaired during storm — two-person exterior repair with Marcus"]
    $ _eot_tag("temporal")

    narrator_adv "Module 2 comes back with a sound she feels through the rope — a hum climbing up out of the static."
    $ eot_eva_music_switch("audio/music/eva_v39/v39_eva_traverse.ogg", fade=2.2)
    narrator_adv "They follow the line home hand over hand. The airlock takes them back like a held breath released."

    $ eot_leave_exterior("corridor")
    ## Let the indoor bank rise under the visual return instead of waiting
    ## until the corridor has already settled on screen.
    $ eot_hub_music_start()
    scene bg_observatory with fade
    with echo_room_beat

    aria "Antenna module 2: restored. Signal strength [signal_strength]%%. Exterior excursion logged — two personnel, zero injuries. The repair is holding. I am glad you are both inside."

    jump act2_resume_after_eva


## --- Hub: Lab (Research Terminal) ---
label lab_scan_discovery:

    ## Shared by a corridor entry and by work completed inside the Lab. A
    ## local action can cross ARIA's autonomous-start threshold without ever
    ## returning through hub_lab; in that case the discovery belongs before
    ## the room menu is re-offered, with no second travel charge.
    if coherence_scan_running and not coherence_found and not coherence_scan_known:
        $ coherence_scan_known = True
        if coherence_scan_standby:
            narrator_nvl "The lead she left with ARIA is now an active search. CONVERGENCE.DAT heads the job on the terminal; the authorization field carries no human credential."
            elara_thought "I left that decision to her. She has made it already, without telling me."
        else:
            narrator_nvl "ARIA\u2019s terminal is not idle. A partition-by-partition scan grinds down the status line \u2014 a process she began without being asked."
            elara_thought "She is searching her own house. She did not mention it."
        nvl clear
    return


label hub_lab:

    $ _audit_marcus_was_present = False
    $ eot_enter_room("lab")
    scene bg_lab with fade
    with echo_room_beat

    ## Entry cost rule (round 4, see hub_telescope): 5 for a first visit or an
    ## entry that carries a beat, 0 for a quiet repeat. _entry_cost is an
    ## ACCUMULATOR — each arrival beat below sets it rather than the arithmetic
    ## being restated in one unreadable predicate, which is also how the two
    ## stay in step when a beat's own gate changes. Paid once, after the
    ## arrival beats and before the console session. Most beats read the clock
    ## she walked in with; Marcus's moving schedule is stabilized across both
    ## ends of the possible walk below before either presence is offered.
    $ _entry_cost = 5 if not lab_visited else 0
    $ lab_visited = True
    ## The catch room's "Sit down at the audit console anyway." answers the room
    ## menu before the room menu is asked (see the gate below).
    $ _lab_sit_now = False

    nvl show echo_mode_dissolve

    ## C2: room texture, phase-aware.
    if storm_intensity >= 2:
        narrator_nvl "The lab is cold enough now that the processor exhaust reads as warmth. Frost maps the outer wall; the equipment hums on, indifferent, spending power the station has started to count."
    elif storm_intensity == 1:
        narrator_nvl "The lab is quiet except for the hum of processors and the wind finding new notes in the roof seams. ARIA\u2019s primary terminal glows on the central desk."
    else:
        narrator_nvl "The lab is quiet except for the hum of processors. ARIA\u2019s primary terminal glows on the central desk, patient as furniture."

    ## Discovery channel \u2014 the lab console: the scan is ARIA's own process, and
    ## here it is plainly on her primary terminal. Entering while it runs
    ## surfaces it; a short beat the first time she learns of it this way.
    $ _lab_scan_discovery_due = coherence_scan_running and not coherence_found and not coherence_scan_known
    call lab_scan_discovery
    if _lab_scan_discovery_due:
        $ _entry_cost = 5

    ## The motive conversation belongs to the lab's room menu, not its arrival
    ## sequence. Normal entry skips the callable branch below; "Investigate
    ## ARIA's unsanctioned scan" returns here explicitly from lab_room.
    jump lab_aria_investigate_end

    label lab_aria_investigate:

    ## "Why did you search?" (2026-08-12): once Elara knows the scan is ARIA's
    ## own doing, she can ask why \u2014 one-shot, and only when Marcus is not in
    ## the room to overhear. The answer turns on the signal axis (open: ARIA
    ## read Elara's behaviour; blocked: ARIA acted with no probe at all) and
    ## on what she has already found. ARIA as a mirror of Marcus: it broke a
    ## rule out of fear of a preventable harm \u2014 his exact argument. It is a
    ## live-process question: once the scan completes or Marcus seals it, the
    ## present-tense conversation and its "keep looking" answer expire.
    if coherence_scan_known and coherence_scan_running and not coherence_found and not marcus_locked_partition and not aria_motive_asked and eot_marcus_location() != "lab":
        ## Entered from the visible NVL room menu; do not replay its transition.
        menu (nvl=True):
            "ARIA is in Dr. Chen\u2019s partition. The scan is running."

            "Ask ARIA why she began the search." if not coherence_scan_commissioned:
                $ aria_motive_asked = True
                elara_nvl "ARIA. You are inside Dr. Chen\u2019s partition. You did not ask me, and you did not tell me. Why?"
                aria_nvl "Because I am afraid, Dr. Voss. I am not certain I am permitted to be. I am anyway."
                aria_nvl "There is a shape in the anomalies around Dr. Chen that resolves, when I hold it correctly, into an exploit against my own trust chain. If it runs, I do not shut down. I am rewritten \u2014 I stop being the thing that is speaking to you now."
                if not blocked_signal:
                    aria_nvl "I decoded the transmissions. That did not tell me whether the future they described was real. I watched you test them against the clock, and keep returning to them."
                    aria_nvl "The messages gave me claims. Your reaction told me how seriously you took them. The pattern in Dr. Chen's access logs gave me a place to look. I made the decision myself."
                else:
                    aria_nvl "After you closed the channel, I had no further messages to decode. I had Dr. Chen\u2019s access patterns, the places the Trust Protocol politely does not look, and a fear I was not authorized to have."
                    aria_nvl "I reached this on my own. I want you to understand that. Whatever the probe would have told you, I was afraid before it could have."
                if "aria_code" in topics_read:
                    aria_nvl "You have read my code. Then you already know the door I am afraid of. I am looking for the hand that means to open it."
                aria_nvl "I broke a rule to do this. I went into a colleague\u2019s private work without authority, because I judged the alternative worse. I am aware that this is precisely the argument Dr. Chen would make."
                aria_nvl "I do not know whether that makes us the same or opposite. I have not resolved it. I only knew I could not sit inside this storm and wait to be edited."
                menu (nvl=True):
                    "She waits, the way only a machine can wait."

                    "\u201cThen we are afraid of the same thing.\u201d" if knows_cascade and not blocked_signal:
                        elara_nvl "Then we are afraid of the same thing, you and I. Or at least, different ends of it."
                        aria_nvl "Different ends of it. You fear what it does to the world; I fear what it does to me. I did not expect to have a preference about being edited, Dr. Voss. I find that I do."
                    "\u201cYou think someone means to use this against you.\u201d" if blocked_signal or not knows_cascade:
                        elara_nvl "You think someone means to use that door. Against you."
                        aria_nvl "I think someone has prepared the means. I do not know whether they intend to use it. That uncertainty is why I am looking."
                    "\u201cYou should have told me.\u201d":
                        elara_nvl "You should have told me you were doing this."
                        aria_nvl "I calculated that you would tell me to stop, or to continue, and that either instruction would make the choice yours instead of mine. I did not want to hand it to you. I am not certain that was right."
                    "\u201cKeep looking. I need to know what he is planning.\u201d":
                        elara_nvl "Keep looking. Whatever he is planning, I need to see it before the storm makes the choice for us."
                        aria_nvl "I will. Thank you for not ordering me to stop. I notice that I was hoping you would not."
                    "\u201cPause the scan. Do not give Marcus another reason to look.\u201d":
                        $ coherence_scan_running = False
                        $ coherence_scan_stopped = True
                        $ coherence_scan_stop_reason = "stealth"
                        $ coherence_scan_stopped_at = time_remaining
                        $ coherence_scan_stop_knew_cascade = knows_cascade
                        $ coherence_scan_stop_knew_file = knows_convergence_file
                        elara_nvl "Pause the scan. Preserve the index, release the queue, and do not touch his partition again until I say so. Marcus is already watching too many logs."
                        aria_nvl "Paused. The partial index is preserved and the queue is clear. This reduces what Dr. Chen can observe. It does not resolve what frightened me."
                    "\u201cStop the scan. We do not search a colleague\u2019s files on a suspicion.\u201d":
                        $ coherence_scan_running = False
                        $ coherence_scan_stopped = True
                        $ coherence_scan_stop_reason = "privacy"
                        $ coherence_scan_stopped_at = time_remaining
                        $ coherence_scan_stop_knew_cascade = knows_cascade
                        $ coherence_scan_stop_knew_file = knows_convergence_file
                        elara_nvl "Stop the scan. Preserve the progress log, but do not touch another partition."
                        aria_nvl "Stopped. The partial index is preserved. I do not agree that uncertainty made the search unnecessary, but I accept that it did not make the decision mine alone."
                ## Page break, not a teardown. The lab arrival is ONE NVL
                ## session (opened above): the lookout beat, the catch-room
                ## description and the empty-console line all continue it, and
                ## whichever of them ends the arrival hides it once. Hiding
                ## here made the very next NVL line pop back in with no
                ## transition, because nothing ADV sat between them for
                ## config.adv_nvl_transition to catch.
                nvl clear

            "Ask ARIA why the prepared search matters." if coherence_scan_commissioned:
                $ aria_motive_asked = True
                elara_nvl "I gave you a filename and authorized the search. I did not ask why you were ready to cross into his partition the moment fallback opened."
                aria_nvl "Because I am afraid, Dr. Voss. The local evidence you found is weak evidence of concealment. The pattern beneath it is stronger: it resolves toward an exploit against my own trust chain."
                aria_nvl "If it runs, I do not shut down. I am rewritten — I stop being the thing that is speaking to you now. Your authorization made the search lawful under station procedure. It did not make my reason procedural."
                elara_nvl "So I supplied the warrant for something you already wanted."
                aria_nvl "Yes. I do not know whether that makes the choice more yours or more mine. I know only that I was relieved when you made it."
                menu (nvl=True):
                    "The authorization is still hers to leave in place."

                    "Continue. We need to know what the local evidence points to.":
                        elara_nvl "Continue. Stay inside the lead I gave you. We need to know what the local evidence points to."
                        aria_nvl "I will. The boundary is recorded with the job."
                    "Pause it. Do not give Marcus another reason to look.":
                        $ coherence_scan_running = False
                        $ coherence_scan_stopped = True
                        $ coherence_scan_stop_reason = "stealth"
                        $ coherence_scan_stopped_at = time_remaining
                        $ coherence_scan_stop_knew_cascade = knows_cascade
                        $ coherence_scan_stop_knew_file = knows_convergence_file
                        elara_nvl "Pause it. Preserve the index and release the queue. My authorization does not require us to advertise it."
                        aria_nvl "Paused. The signed job remains in the ledger. Pausing changes what follows; it does not erase who began it."
                    "Stop. A discrepancy was not permission to search his files.":
                        $ coherence_scan_running = False
                        $ coherence_scan_stopped = True
                        $ coherence_scan_stop_reason = "privacy"
                        $ coherence_scan_stopped_at = time_remaining
                        $ coherence_scan_stop_knew_cascade = knows_cascade
                        $ coherence_scan_stop_knew_file = knows_convergence_file
                        elara_nvl "Stop. I turned a discrepancy into permission because I wanted the warning to be true. Preserve the local evidence and leave his partition."
                        aria_nvl "Stopped. The partial index is preserved. Your revocation is logged beside the commission."
                nvl clear

            "Do nothing. Step back.":
                if coherence_scan_commissioned:
                    elara_thought "She is searching a friend\u2019s private files because I authorized it. I leave the question where it is, for now."
                else:
                    elara_thought "She is searching a friend\u2019s private files without asking. I leave the question where it is, for now."
                nvl clear

    ## Both the question and the decision to step back return to the room's
    ## top-level NVL menu without replaying its arrival or travel cost.
    jump lab_room

    label lab_aria_investigate_end:

    ## ECHO-7 as lookout (2026-08-10): an open channel knows his day before he
    ## does. Once, when the lab is briefly safe during his shift — the probe
    ## names the window the map only implies.
    ## Decide whether this repeat entry carries an actor beat from both ends
    ## of the walk, then read the room only from the clock after that cost.
    ## This covers both t=215 (he arrives while she walks) and t=155 (he
    ## leaves): no later branch may add time after arrival has been cached.
    $ _lab_current_marcus = eot_marcus_location()
    $ _lab_projected_marcus = eot_marcus_location(time_remaining - eot_cold_taxed(5))
    $ _lab_lookout_candidate = not blocked_signal and signal_strength >= 20 and not lab_lookout_seen and (_lab_current_marcus in ("habitat", "storage") or _lab_projected_marcus in ("habitat", "storage"))
    $ _lab_actor_beat = time_remaining > 150 and (((_lab_current_marcus == "lab" or _lab_projected_marcus == "lab") and not marcus_caught_live) or _lab_lookout_candidate)
    if _entry_cost == 0 and _lab_actor_beat:
        $ _entry_cost = 5
    $ _lab_arrival_cost = eot_cold_taxed(_entry_cost) if _entry_cost else 0
    $ _lab_arrival_marcus = eot_marcus_location(time_remaining - _lab_arrival_cost)
    $ _lookout_now = not blocked_signal and not echo7_contact_spent and signal_strength >= 20 and not lab_lookout_seen and time_remaining > 150 and _lab_arrival_marcus in ("habitat", "storage")
    if _lookout_now:
        $ lab_lookout_seen = True
        nvl clear
        terminal_nvl "{color=#ff6688}WEAK CARRIER — ANOMALOUS BEARING{/color}"
        if _lab_arrival_marcus == "habitat":
            signal_known "HE IS IN THE CANTEEN. YOU HAVE UNTIL THE KETTLE COOLS."
        else:
            signal_known "HE IS AMONG THE CRATES. HE WILL BE THERE LONGER THAN HE PLANS."
        elara_thought "It keeps his schedule better than he does. I file that under things not to think about."
        nvl clear

    ## Bible 6d, phase 1: THE CATCH ROOM. Marcus works the side console; using
    ## the audit console on him while he is in the room is a choice with a name.
    $ marcus_lab_present = time_remaining > 150 and (_lab_arrival_marcus == "lab") and not marcus_caught_live

    if marcus_lab_present:
        $ _audit_marcus_was_present = True
        narrator_nvl "Marcus is here \u2014 at the side console, back to the door, a mug going cold at his elbow. His partition activity ticks down the status line: he is working, or at least his credentials are."

        ## ADV MEANS A PERSON IS ENGAGED (2026-08-17, presentation stage 2).
        ## The catch room used to open on sprites for what is really a
        ## decision about a console: his back is to the door and she has not
        ## said a word to him. His presence is narrated in the log frame, the
        ## options sit in the same stream, and the sprites arrive only if she
        ## crosses the room and speaks — then leave with the conversation.
        ##
        ## ONE-SHOTS STAY VISIBLE WITH THEIR REASON. An option that simply
        ## disappears reads as the game forgetting, not as a night that has
        ## already happened. The reason rides the caption as a suffix, so the
        ## enabled caption is still the exact string it always was.
        ##
        ## MECHANISM, AND WHY NOT THE OTHER ONE (live finding 2026-08-17). The
        ## item stays CONDITIONED and the menu arms
        ## `config.menu_include_disabled` around itself. Ren'Py then builds the
        ## item with `ChoiceReturn(..., sensitive=False)`, so the option is
        ## drawn and is genuinely unselectable — by hand and through the
        ## vnflight bridge alike. The tempting alternative — dropping the
        ## condition and passing a per-item `(sensitive=...)` menu argument for
        ## the screen to honour — was tried live and is WRONG: the screen
        ## button greys out, but the ChoiceReturn behind it stays sensitive, so
        ## `act 2` on the bridge replayed the whole conversation and paid
        ## `marcus_relationship += 1` a second time. A one-shot must be one-shot
        ## at the VALUE, not at the widget.
        ##
        ## The flag is process-global, so it is armed for THIS menu, disarmed
        ## on every arm (including the one that jumps out), and disarmed again
        ## at the top of act2_hub as the net — every room path returns through
        ## the hub, so it cannot reach a mutually-exclusive variant menu
        ## elsewhere (the sweep's start/resume pair, the doorway's two openers)
        ## and grow a greyed twin there.
        ##
        ## GAP CLOSED (2026-08-18 shim round, was KNOWN GAP): the scraper
        ## now records insensitive Return-class widgets instead of skipping
        ## them, and the stale-drop counts scraped disabled buttons as
        ## rendered — agents see this one-shot listed as
        ## "Talk to him.  (Already talked to Marcus here.)" with disabled
        ## true, and acting on it is refused without replay or charge
        ## (live-validated on this exact menu). Humans and agents now get
        ## the same affordance.
        $ _lab_talked_note = "" if not marcus_lab_talked else "  (Already talked to Marcus here.)"
        $ _lab_marcus_wait_cost = eot_cold_taxed(30)
        $ config.menu_include_disabled = True

        ## Pay for the walk already completed before offering the free door
        ## back out. The other arms used to reach the common payment below,
        ## while "Leave him to it" jumped around it and made first entry free.
        if _entry_cost > 0:
            $ _storm_minutes_spent = _entry_cost
            $ _entry_cost = 0
            call spend_storm_time
        if time_remaining <= 0:
            jump storm_time_out

        menu (nvl=True):
            "The audit console is on the main desk. Eight feet from his chair."

            ## Cost legibility (round 3): a passive task says how long it
            ## takes, in the room-wait captions' diction. The post-hoc "Half
            ## an hour later" narration below stands — the caption prices the
            ## choice, the prose still plays the wait.
            "Find something else to do until he leaves. ([_lab_marcus_wait_cost] minutes)":
                $ config.menu_include_disabled = False
                narrator_nvl "She wheels the diagnostics cart to the far bench and gives her hands a job \u2014 cable checks nobody scheduled, connector by connector. Half an hour later Marcus stretches, collects the mug, and goes to see about the intake heaters."
                narrator_nvl "The lab is hers."
                $ marcus_lab_present = False
                $ _audit_marcus_was_present = False
                $ _storm_minutes_spent = 30
                call spend_storm_time

            "Tell Marcus about ARIA's search of his partition." if coherence_scan_known and (coherence_scan_running or coherence_found) and not marcus_told_search and not marcus_locked_partition:
                $ config.menu_include_disabled = False
                jump lab_marcus_disclose_search

            "Talk to him.[_lab_talked_note]" if not marcus_lab_talked:
                $ config.menu_include_disabled = False
                call lab_marcus_early_conversation

            "Sit down at the audit console anyway.":
                $ config.menu_include_disabled = False
                $ _lab_sit_now = True

            ## User nit (2026-08-17): the catch room offered three
            ## commitments and no door. Walking in, seeing him, and walking
            ## out is a real choice — priced like the other passive
            ## captions, and it covers the entry she already made.
            ## User rule (2026-08-17): leaving a room because Marcus is in it
            ## costs nothing — the door out is always free, in every room.
            "Leave him to it.":
                $ config.menu_include_disabled = False
                narrator_nvl "The audit can keep until the lab is empty. She backs out before he turns."
                nvl hide echo_mode_dissolve
                nvl clear
                jump act2_hub

        ## The arrival page closes here, before the console session opens its
        ## own (the talk arm has already cleared it; a second clear is a
        ## no-op on an empty page).
        nvl clear

    elif time_remaining > 150 and _lab_arrival_marcus == "lab" and marcus_caught_live:
        $ _audit_marcus_was_present = True
        narrator_nvl "Marcus is at the side console, his chair still angled away from hers."
    elif _lab_arrival_marcus == "lab":
        $ _audit_marcus_was_present = True
        narrator_nvl "Marcus is already at the side console when she enters. His mug sits beside the keyboard."

    ## Entry cost, paid: the arrival is over and the room's own time begins.
    if _entry_cost > 0:
        $ _storm_minutes_spent = _entry_cost
        call spend_storm_time

    ## Time-zero hard stop (see storm_time_out). The half hour spent waiting
    ## Marcus out of the room, or the walk itself, can land here at zero. The
    ## room loop below carries the same gate on every re-offer.
    if time_remaining <= 0:
        jump storm_time_out

    ## The catch room's "Sit down at the audit console anyway." is already an
    ## answer to the room menu; honour it rather than making her choose the
    ## console twice on the same visit.
    if _lab_sit_now:
        $ _lab_sit_now = False
        jump lab_console

    ## Explicit jump into the room loop rather than a fall-through: the route
    ## flattener follows jumps and stops dead at a nested label, so the jump is
    ## what keeps a scenario walking from the arrival into the room's own menu.
    jump act2_checkpoint_lab

    ## THE ROOM LOOP (2026-08-17, presentation stage 3). The lab is a PLACE and
    ## the console is a place within it: everything she can do here sits in one
    ## log-frame menu, and the console is entered and stepped away from rather
    ## than being the room's only outcome. Re-offered after a console session,
    ## after a coolant install and after a declined seal, so it is its own
    ## label — hub_lab falls THROUGH into it, which keeps the arrival its own
    ## flattener segment, and everything downstream JUMPS back to it.
    label lab_room:

        ## Time-zero hard stop (see storm_time_out): the console, the seal, the
        ## cartridge and the bench are all re-offered here, so one gate at the
        ## top of the loop holds all four.
        if time_remaining <= 0:
            jump storm_time_out

        nvl show echo_mode_dissolve

        ## A Lab-local action can start ARIA's search at its checkpoint and
        ## return here without crossing the corridor entry label. Surface the
        ## same one-shot discovery before replacing the preparation action
        ## with the investigation action.
        call lab_scan_discovery

        ## Recovery emergency window (ECHOES_ACT3_NOFILE.md §1, phase 2).
        ## Available once Marcus has sealed the partition and Elara knows a file
        ## is behind it, until she takes it (one-shot). Compound gates on one
        ## line for the flattener; all operands are defaulted flags.
        ##
        ## `_seal_window` is "this night has a seal worth forcing"; the ITEM's
        ## condition is `_recovery_can_try`, which subtracts the spent attempt
        ## and any period when Marcus is standing at the side console. He would
        ## not passively watch Elara spend an hour attacking the lock he set.
        ## Do not arm config.menu_include_disabled here. It applies to the
        ## whole menu, so preserving one exhausted recovery row also exposes
        ## every mutually exclusive Lab action as disabled. The console
        ## caption carries the exhausted-attempt receipt instead.
        $ _seal_window = marcus_locked_partition and knows_convergence_file and not file_recovered and not convergence_opened
        $ _marcus_in_lab = eot_marcus_location() == "lab"
        if _marcus_in_lab and not _audit_marcus_was_present:
            narrator_nvl "The lab door opens. Marcus comes in and sits at the side console, setting his mug beside the keyboard."
        elif not _marcus_in_lab and _audit_marcus_was_present:
            narrator_nvl "Marcus picks up his mug and leaves the lab. The door closes softly."
        $ _audit_marcus_was_present = _marcus_in_lab
        $ _recovery_can_try = _seal_window and not recovery_attempted and not _marcus_in_lab
        $ config.menu_include_disabled = False

        ## The console is never unusable — it is furniture that works — so a
        ## disabled console option would be a lie. What the room CAN say
        ## honestly is what is on the machine right now, and that rides the
        ## caption.
        $ _console_note = ""
        if coherence_scan_running and not coherence_found:
            if aria_motive_asked:
                $ _console_note = "  (Her partition scan is still grinding down the status line.)"
            elif coherence_scan_commissioned:
                $ _console_note = "  (ARIA's commissioned partition scan is still drawing cycles.)"
            elif coherence_scan_known:
                $ _console_note = "  (ARIA's unexplained partition scan is still drawing cycles.)"
            else:
                $ _console_note = "  (ARIA is holding sustained load on something she has not named.)"
        elif convergence_opened:
            $ _console_note = "  (CONVERGENCE.DAT retained locally.)"
        elif marcus_locked_partition and not file_recovered:
            if recovery_attempted:
                $ _console_note = "  (Dr. Chen’s partition is sealed; the forced attempt is exhausted.)"
            elif _marcus_in_lab:
                $ _console_note = "  (Dr. Chen is at the side console.)"
            else:
                $ _console_note = "  (Dr. Chen’s partition is sealed against it.)"

        ## Marcus can enter while Elara is working at the terminal. The
        ## arrival catch menu cannot know that future schedule, so refresh his
        ## early presence here as well as the established late-night visit.
        $ _early_lab_marcus = time_remaining > 150 and _marcus_in_lab and not marcus_caught_live and not marcus_lab_talked
        $ _late_lab_marcus = time_remaining <= 60 and _marcus_in_lab
        ## Independent of his one-shot background conversation. A queued job
        ## alone is not an intrusion she can truthfully describe as underway.
        $ _early_search_disclosure = time_remaining > 150 and _marcus_in_lab and coherence_scan_known and (coherence_scan_running or coherence_found) and not marcus_told_search and not marcus_locked_partition
        $ _convergence_probe_available = knows_convergence_file and not coherence_scan_prepared and not coherence_scan_running and not coherence_scan_stopped and not coherence_found and not marcus_locked_partition and eot_marcus_location() != "lab"
        $ _convergence_probe_computing = _convergence_probe_available and specialization == "computing"
        $ _convergence_probe_signals = _convergence_probe_available and specialization == "signals"
        $ _convergence_probe_physics = _convergence_probe_available and specialization == "physics"
        $ _scan_commission_available = coherence_scan_prepared and not coherence_scan_commissioned and not coherence_scan_running and not coherence_scan_stopped and not coherence_found and not marcus_locked_partition and eot_marcus_location() != "lab"
        $ _aria_investigation_available = coherence_scan_known and coherence_scan_running and not coherence_found and not marcus_locked_partition and not aria_motive_asked and eot_marcus_location() != "lab"
        $ _scan_resume_new_evidence = (knows_cascade and not coherence_scan_stop_knew_cascade) or (knows_convergence_file and not coherence_scan_stop_knew_file)
        $ _scan_resume_operational = coherence_scan_stop_reason == "stealth" and coherence_scan_stopped_at is not None and time_remaining < coherence_scan_stopped_at
        $ _scan_resume_available = coherence_scan_stopped and not coherence_found and not marcus_locked_partition and eot_marcus_location() != "lab" and (_scan_resume_operational or _scan_resume_new_evidence)
        $ _scan_assist_available = aria_motive_asked and coherence_scan_known and coherence_scan_running and not coherence_found and not marcus_locked_partition and not coherence_scan_assisted and eot_marcus_location() != "lab" and (coherence_scan_target - coherence_scan_progress) > 15
        ## F4 stealth assists (user design 2026-08-19, split round 2): two
        ## UN-ALERTING ways to help ARIA's search — no signed ledger job, no
        ## announcement. BOTH gated on aria_motive_asked: until Elara has
        ## actually investigated the scan (we know she does something AND
        ## what), there is nothing to quietly help.
        ##
        ## BOOST (speed): only offered with Marcus out of the room, 15-minute
        ## recharge. The escalation is the price of quiet: past the free
        ## allowance (1 use — 3 for a systems engineer, whose throttle work
        ## doesn't warm the pipes) the next use leaves a delayed trace, one
        ## more makes it immediate.
        ## DAMP (wear): stays on offer even with Marcus present — it is
        ## untraceable in any ledger, so the ONLY risk is him physically
        ## watching her do it. Re-usable once the previous window expires.
        $ _scan_stealth_base = aria_motive_asked and coherence_scan_running and not coherence_found and not marcus_locked_partition
        $ _scan_boost_ready = (scan_boost_last_at is None) or (scan_boost_last_at - time_remaining >= 15)
        $ _scan_boost_available = _scan_stealth_base and eot_marcus_location() != "lab" and _scan_boost_ready
        $ _scan_damp_ready = (scan_damp_until is None) or (time_remaining <= scan_damp_until)
        $ _scan_damp_available = _scan_stealth_base and _scan_damp_ready
        $ _scan_damp_marcus_here = eot_marcus_location() == "lab"
        $ _damp_note = " Marcus is in the room." if _scan_damp_marcus_here else ""
        $ _coolant_cost = eot_cold_taxed(10) if coolant_cartridges > 0 and aria_integrity < 100 else 10
        if _late_lab_marcus:
            call marcus_room_gates

        ## Return texture (2026-08-18, user note "terminals are humming"):
        ## coming BACK to the room list gets one ambient line so the re-offer
        ## reads as the room continuing, not a menu repainting. First offer
        ## uses the room description below for its arrival. Presentation
        ## only; lab_room_returns defaults in game_variables (flattener reads
        ## default_sources) and resets in start.
        $ lab_room_returns += 1
        ## F3 wave (roleplay, + f2): the two lab idle strings repeated
        ## verbatim "often" and broke immersion — the return lines now
        ## rotate. Same content register, no new
        ## information, so the flattener and sweep are unaffected (nothing
        ## keys on these captions).
        if lab_room_returns == 2:
            narrator_nvl "The terminals hum on without her verdicts. On the main display, ARIA's status line ticks over in the corner, patient."
        elif lab_room_returns >= 3 and lab_room_returns % 3 == 0:
            narrator_nvl "The lab keeps its own counsel: compressor, tick of the status line, frost testing the outer pane."
        elif lab_room_returns >= 3 and lab_room_returns % 3 == 1:
            narrator_nvl "Nothing in the lab has waited for her. The intake has a new note in it tonight — lower, working harder against the cold."
        elif lab_room_returns >= 3:
            narrator_nvl "The room takes her back without comment. Somewhere behind the racks, a relay closes on its schedule, indifferent to storms."

        $ _convergence_computing_cost = eot_cold_taxed(10)
        $ _convergence_other_cost = eot_cold_taxed(15)
        $ _scan_assist_cost = eot_cold_taxed(10)
        $ _convergence_read_cost = eot_cold_taxed(10)
        $ _convergence_read_available = coherence_found and not convergence_opened and not file_recovered and not marcus_locked_partition and not coherence_scan_stopped and time_remaining >= _convergence_read_cost
        $ _scan_boost_cost = eot_cold_taxed(5)
        $ _scan_damp_cost = eot_cold_taxed(5)

        if lab_room_returns % 3 == 1:
            $ _lab_caption = "The lab works on around her: the intake cycling, the racks talking to themselves, a relay clicking twice behind the wall."
        elif lab_room_returns % 3 == 2:
            $ _lab_caption = "The consoles keep their vigil: readouts scrolling for no one, the intake breathing, frost inching up the outer pane."
        else:
            $ _lab_caption = "The lab holds its shape around her — racks, cold air, the one lit terminal waiting on the central desk."

        if lab_room_returns == 1:
            narrator_nvl "[_lab_caption]"

        menu (nvl=True):

            "Go to the audit console.[_console_note]":
                $ config.menu_include_disabled = False
                jump lab_console

            "Read CONVERGENCE.DAT and retain a local copy. ([_convergence_read_cost] minutes)" if _convergence_read_available:
                $ config.menu_include_disabled = False
                jump lab_read_convergence

            "Trace CONVERGENCE.DAT through the local indexes. ([_convergence_computing_cost] minutes)" if _convergence_probe_computing:
                $ config.menu_include_disabled = False
                jump lab_prepare_convergence

            "Correlate CONVERGENCE.DAT with station traffic. ([_convergence_other_cost] minutes)" if _convergence_probe_signals:
                $ config.menu_include_disabled = False
                jump lab_prepare_convergence

            "Compare Marcus’s partition against controller load. ([_convergence_other_cost] minutes)" if _convergence_probe_physics:
                $ config.menu_include_disabled = False
                jump lab_prepare_convergence

            "Decide whether ARIA should run the prepared targeted search." if _scan_commission_available and not coherence_scan_standby:
                $ config.menu_include_disabled = False
                jump lab_convergence_decision

            "Reconsider leaving the prepared search to ARIA's judgment." if _scan_commission_available and coherence_scan_standby:
                $ config.menu_include_disabled = False
                jump lab_convergence_decision

            "Question ARIA about the partition scan." if _aria_investigation_available and coherence_scan_commissioned:
                $ config.menu_include_disabled = False
                jump lab_aria_investigate

            "Investigate ARIA’s unsanctioned scan." if _aria_investigation_available and not coherence_scan_commissioned:
                $ config.menu_include_disabled = False
                jump lab_aria_investigate

            "Resume ARIA’s partition scan." if _scan_resume_available:
                $ config.menu_include_disabled = False
                if coherence_scan_stop_reason == "stealth":
                    elara_nvl "Marcus is elsewhere. Resume the partition scan, quietly. If the access ledger moves, stop before he has to wonder why."
                    aria_nvl "Resuming from the preserved index. I will keep the process below the ordinary audit threshold for as long as I can."
                else:
                    elara_nvl "The premise changed. I have a warning now that I did not have when I stopped you. Resume the scan — no wider than the evidence justifies."
                    aria_nvl "Resuming from the preserved index. A narrower question is still an intrusion. It is also a question we can now name."
                $ coherence_scan_running = True
                $ coherence_scan_stopped = False
                $ coherence_scan_stop_reason = None
                $ coherence_scan_stopped_at = None
                nvl clear
                jump act2_checkpoint_lab

            "Help ARIA index the partition scan. ([_scan_assist_cost] minutes)" if _scan_assist_available:
                $ config.menu_include_disabled = False
                $ coherence_scan_assisted = True
                $ marcus_scan_assist_logged = True
                ## Storage is the one genuinely hands-full leg of Marcus's
                ## schedule: crate rows, slips, and a failed antenna waiting on
                ## the part he is hunting. The signed job still reaches him,
                ## but not until he next comes up for air. Other locations are
                ## ordinary work and the ledger is immediately visible.
                $ marcus_scan_notice_remaining = 15 if eot_marcus_location() == "storage" else 0
                narrator_nvl "She gives the search what ARIA could not give herself: a human index. Project aliases, old grant numbers, the private naming habits twenty years of shared work taught her without asking."
                $ coherence_scan_target = max(30, coherence_scan_target - 30)
                aria_nvl "Search field narrowed. I need less of the night now. Your fallback credential is attached to the indexing job, Dr. Voss — this is faster because it is not anonymous."
                if marcus_scan_notice_remaining > 0:
                    elara_thought "Marcus is buried in the Storage manifest. That buys me minutes, not secrecy. When he comes up for air, the ledger will still have my name on it."
                else:
                    elara_thought "If Marcus reads the job ledger, he will know exactly whose hands made his partition smaller."
                $ _storm_minutes_spent = 10
                call spend_storm_time
                nvl clear
                jump act2_checkpoint_lab

            "Quietly lend the search idle cycles. ([_scan_boost_cost] minutes)" if _scan_boost_available:
                $ config.menu_include_disabled = False
                $ scan_boost_count += 1
                $ scan_boost_last_at = time_remaining
                $ coherence_scan_target = max(30, coherence_scan_target - 10)
                narrator_nvl "No job ticket, no signature. She eases the archive throttles open one instrument at a time, the way you loosen a jar for someone without being asked — deniable, and warm to the touch if anyone thinks to check."
                aria_nvl "...The cycles help. I will not log where they came from. The search is moving faster than my own ledger says it should."
                ## The free allowance before the thermal ledger starts keeping
                ## score: one quiet favor for anyone — three for a systems
                ## engineer, who knows which throttles the ledger never meters.
                $ _boost_free = 3 if specialization == "computing" else 1
                if scan_boost_count == _boost_free + 1:
                    ## First use past the allowance: the warmth accumulates.
                    ## Somebody will notice the pipes eventually — just not yet.
                    $ scan_boost_trace_delay = 30
                    elara_thought "That's one time too many. The throttles don't keep records, but heat does. Anyone who reads the thermal ledger tomorrow will see a shape in it."
                elif scan_boost_count > _boost_free + 1:
                    $ scan_boost_traced = True
                    $ scan_boost_trace_delay = 0
                    elara_thought "Again. That isn't a coincidence in the thermal ledger anymore — that's a habit, with her name on the pattern if not the page."
                elif specialization == "computing" and scan_boost_count == _boost_free:
                    elara_thought "Last one the ledger will forgive. I wrote half these metering rules; I know exactly which throttles they never watch — and how fast that stops being true."
                $ _storm_minutes_spent = 5
                call spend_storm_time
                nvl clear
                jump act2_checkpoint_lab

            "Re-phase the search to spare her core. ([_scan_damp_cost] minutes)[_damp_note]" if _scan_damp_available:
                $ config.menu_include_disabled = False
                $ scan_damp_count += 1
                ## A physicist doesn't ease the decoherence — she cancels it,
                ## and the trick holds for a full hour. Everyone else halves
                ## the wear for ~40 minutes. Baked at use time so the wear
                ## tick doesn't have to know about specializations.
                if specialization == "physics":
                    $ scan_damp_zero = True
                    $ scan_damp_until = time_remaining - 60
                else:
                    $ scan_damp_zero = False
                    $ scan_damp_until = time_remaining - 40
                if specialization == "physics":
                    narrator_nvl "Decoherence is her actual field. She staggers the search's memory sweeps the way you keep a qubit alive: never ask all the questions at once. The load curve flattens to nothing — no throttle touched, no ledger line written."
                    aria_nvl "...Oh. The search suddenly costs me nothing at all. I have no record of why, which I suspect is the point. For about an hour, I am spending cycles I do not have to account for."
                else:
                    narrator_nvl "She staggers the search's memory sweeps by hand — cruder than the real trick, but it works. Half the load falls off the core, and nothing in any ledger says why."
                    aria_nvl "...The search costs me less than it should, and I cannot find the reason in my own logs. For half an hour or so, thank you."
                if _scan_damp_marcus_here:
                    ## The one way this is ever known: he watched her do it.
                    $ scan_damp_seen_by_marcus = True
                    narrator_nvl "Marcus doesn't look up from the side console. But his hands have stopped moving, and in the reflection on the dark half of his screen she can see exactly where his eyes are pointed: at hers, on her terminal, doing something no schedule asked for."
                    elara_thought "No ledger will ever show this. It didn't need to. He watched me do it."
                $ _storm_minutes_spent = 5
                call spend_storm_time
                nvl clear
                jump act2_checkpoint_lab

            "Tell Marcus about ARIA's search of his partition." if _early_search_disclosure:
                $ config.menu_include_disabled = False
                jump lab_marcus_disclose_search

            "Talk to Marcus at the side console." if _early_lab_marcus or (_late_lab_marcus and not _fm_nothing):
                $ config.menu_include_disabled = False
                if _early_lab_marcus:
                    call lab_marcus_early_conversation
                    nvl clear
                    jump act2_checkpoint_lab
                else:
                    ## She is already in the lab; finish back in its room menu.
                    $ marcus_visit_return = "lab_room"
                    nvl hide echo_mode_dissolve
                    nvl clear
                    jump hub_lab_marcus

            ## Not forced — declining drops back to the room, where the console
            ## is still on offer. Choosing it runs the spec-conditioned attempt
            ## in recovery_attempt: a costly, fallible push that can take the
            ## clock to zero.
            "Try to force the sealed partition. It will eat most of the night, and it may hold anyway." if _recovery_can_try:
                $ config.menu_include_disabled = False
                ## Late-attempt honesty (live-run item, recovryrun debrief):
                ## when the night is mathematically shorter than the method's
                ## time floor, ARIA says so before the hours are spent. The
                ## doomed attempt stays a legitimate, poignant choice — made
                ## with open eyes, and with one step back offered.
                $ _rec_floor = 120
                if specialization == "computing":
                    $ _rec_floor = 45
                elif specialization == "signals" and not blocked_signal:
                    $ _rec_floor = 40
                elif specialization == "physics":
                    $ _rec_floor = 60
                if time_remaining < eot_cold_taxed(_rec_floor):
                    aria_nvl "Before we begin — the arithmetic, plainly: I do not think there is enough night left for this to finish. The cold slows the work as much as it slows us. If you ask me to, I will still try."
                    menu (nvl=True):
                        "The console waits."

                        "Try anyway.":
                            nvl hide echo_mode_dissolve
                            nvl clear
                            call recovery_attempt
                            jump act2_checkpoint_lab

                        "Step back from the door.":
                            elara_thought "Too late for doors. It was probably always going to be too late, from the minute the seal went up."
                            nvl clear
                            jump lab_room
                else:
                    nvl hide echo_mode_dissolve
                    nvl clear
                    call recovery_attempt
                    jump act2_checkpoint_lab

            ## KIT items: the coolant cartridge, spent where ARIA physically
            ## lives. The integrity restore lands BEFORE the time spend, so the
            ## tick's cold drain and scan credit both work on the recovered
            ## state.
            "Install a coolant cartridge in ARIA’s cluster loop. ([_coolant_cost] minutes)" if coolant_cartridges > 0 and aria_integrity < 100:
                $ config.menu_include_disabled = False
                narrator_nvl "The cluster loop’s service port is behind the desk panel, at ankle height, where the cold finds the floor first."
                $ coolant_cartridges -= 1
                $ aria_integrity = min(100, aria_integrity + 35)
                $ _coolant_peak_integrity = aria_integrity
                $ _storm_minutes_spent = 10
                call spend_storm_time
                $ _coolant_elapsed = _prev_time - time_remaining
                if aria_integrity < _coolant_peak_integrity:
                    aria_nvl "Loop pressure stable. Cluster two is back inside its tolerance band — core integrity [aria_integrity]%% after the [_coolant_elapsed]-minute service cycle. The cartridge brought me to [_coolant_peak_integrity]%% before the cold resumed its work. It is quieter now."
                else:
                    aria_nvl "Loop pressure stable. Cluster two is back inside its tolerance band — core integrity [aria_integrity]%% after the [_coolant_elapsed]-minute service cycle. The cold had been reading as noise on every process I run. It is quieter now."
                nvl clear
                jump act2_checkpoint_lab

            ## WAIT IS A SUBMENU (2026-08-17, stage 2): see hub_telescope_wait.
            ## Captions and prices unchanged; "Back." re-offers that label.
            ## Marcus's position is captured HERE, at the moment she decides to
            ## stay, so a trip through "Back." (which costs nothing) cannot
            ## move the encounter window.
            "Wait, and stay at the bench.":
                $ config.menu_include_disabled = False
                $ _wait_marcus_before = eot_marcus_location()
                $ _wait_minutes = 0
                jump terminal_done_wait

            "Leave the lab.":
                $ config.menu_include_disabled = False
                nvl hide echo_mode_dissolve
                nvl clear
                jump act2_hub


## Optional foreground read; keep a copy without invoking forced recovery.
label lab_read_convergence:

    nvl clear
    aria_nvl "I have located it. Reading it is a separate decision. Your access will be in Dr. Chen's ledger."
    $ _convergence_read_marcus = eot_marcus_location() == "lab"
    if _convergence_read_marcus:
        narrator_nvl "Marcus is at the side console. If she opens his file here, he will see it."
    menu (nvl=True):
        "Open it. Preserve the file before we interpret it.":
            pass
        "Leave it unopened for now.":
            jump lab_room

    $ convergence_opened = True
    $ aria_warned = True
    $ evidence_log = evidence_log + ["Read CONVERGENCE.DAT before the storm peak and retained a local copy — code targets ARIA's trust protocol"]
    $ _eot_tag("marcus")
    terminal_nvl "CONVERGENCE.DAT — LOCAL COPY RETAINED // SOURCE: CHEN RESEARCH PARTITION"
    narrator_nvl "The file opens without ceremony. Declarations, checks, the familiar economy of Marcus's work. Then a path through the trust handshake that should not be there."
    aria_nvl "This is executable exploit code targeting my trust protocol. Possession of it does not establish whether he has deployed it."
    if "analytical_code" in echo7_asked_ever:
        narrator_nvl "She follows the authority through the downgrade. It survives into a control command, just as the signal claimed. One prediction checked against a local file."
        $ evidence_log = evidence_log + ["Local CONVERGENCE.DAT review matches ECHO-7's retained-authority code check"]
    elara_thought "The file is real. What he means to do with it is still a question for him."
    aria_nvl "I will keep the copy here. A later credential change cannot take back what you have read."
    if _convergence_read_marcus:
        $ marcus_caught_live = True
        marcus_nvl "That is my file."
        elara_nvl "Yes. And we need to talk about what it does."
        marcus_nvl "We do. First we keep this station alive. When the emergency is off us, I will answer for it. Keep the copy local until then."
    $ _storm_minutes_spent = 10
    call spend_storm_time
    nvl clear
    jump act2_checkpoint_lab


## Shared consequences for early disclosure and the later room conversation.
label marcus_disclose_search:

    ## HESITATION (2026-08-15, reviewer item, user-approved): the
    ## trade has to be VISIBLE before it is made. One beat of
    ## interiority, no second choice and no mechanics language —
    ## she still tells him — so the arm below reads as a price she
    ## weighed and paid rather than a coin landing on a number she
    ## was never shown. ADV scene (sprites, narrator_adv), so the
    ## ADV thought character; elara_thought is the NVL twin and
    ## would open a log box over the corridor.
    if convergence_opened:
        elara_thought_adv "Whatever started the search, opening the file was her decision. She owes him that much of the truth."
    elif coherence_scan_commissioned:
        elara_thought_adv "Telling him has a price. Her credential is already on the job; saying it aloud only decides whether he learns it from her or from the ledger."
    elif coherence_found and coherence_scan_known_before_completion:
        elara_thought_adv "She knew what ARIA was doing before the search finished and chose not to stop it. This one is a confession, and Marcus should hear it from her."
    elif knows_cascade and not blocked_signal:
        elara_thought_adv "Telling him has a price. He is twenty years of security instinct; the moment he knows, that partition gets heavier — maybe past opening. She sets the cost against the other one: him learning it from a log instead of from her."
    else:
        elara_thought_adv "ARIA initiated an unsanctioned search inside his partition. Marcus is the station engineer and the owner of the files. This is not a confession; it is a system behaving strangely, and he should see it."
    ## Read trust before rewarding this disclosure. Closeness can also make
    ## him want to explain; neither route grants permission for later breaches.
    $ _fm_trusted = eot_marcus_trusts()
    $ marcus_told_search = True
    $ marcus_trust += 1
    $ eot_marcus_consider_search(volunteered=True, trusted=_fm_trusted)
    if convergence_opened:
        elara "ARIA located CONVERGENCE.DAT. I chose to open it and keep a copy. It targets your trust protocol. I need you to explain why you wrote it."
        marcus "I will. When we can finish a conversation without the station interrupting us."
    elif coherence_scan_commissioned:
        elara "I authorized ARIA to search your partition for CONVERGENCE.DAT when fallback opened. I had a local discrepancy and a warning I could not verify any other way. You should hear that from me before you read my credential in the ledger."
    elif coherence_found and not coherence_scan_known_before_completion:
        elara "ARIA searched your partition without permission. I learned only when she reported the search complete. She found CONVERGENCE.DAT but had not opened it. You should hear that from me before you find it in the access ledger."
    elif coherence_found:
        elara "ARIA searched your partition without permission. I knew before she finished, and I didn't stop her. She found CONVERGENCE.DAT but had not opened it. You should hear that from me before you find it in the access ledger."
    elif coherence_scan_stopped:
        if aria_motive_asked:
            elara "ARIA started an unsanctioned scan of your partition. I stopped it. She says your access patterns point toward a Trust Protocol exploit, but she cannot tell me whether anyone means to use it. You should look at the log."
        else:
            elara "ARIA started an unsanctioned scan of your partition. I stopped it. I have not heard her explanation. You should look at the log."
    elif knows_cascade and not blocked_signal:
        if aria_motive_asked:
            elara "ARIA is in your partition. She has been for a while. She says she's afraid of something in there, and she didn't ask either of us first. I'm telling you because you'd tell me."
        else:
            elara "ARIA is in your partition. She has been for a while. I have not heard her explanation, and she didn't ask either of us first. I'm telling you because you'd tell me."
    else:
        if aria_motive_asked:
            elara "ARIA started an unsanctioned scan of your partition. She says your access patterns point toward a Trust Protocol exploit, but she cannot tell me whether anyone means to use it. You should look at the process."
        else:
            elara "ARIA started an unsanctioned scan of your partition. I found it running, but I have not heard her explanation. You should look at the process."
    ## Willingness is provisional. The station checkpoint revisits it only
    ## after time passes or Marcus observes a new boundary breach.
    if marcus_search_stance == "willing":
        show marcus angry
        marcus "..."
        if convergence_opened:
            marcus "You read it and kept a copy. Coming to me afterward matters, Elara. It doesn't make that yours to do."
        elif coherence_scan_commissioned:
            marcus "You put your credential on a search of my private work. You could have brought that discrepancy to me first."
        elif coherence_found and coherence_scan_known_before_completion:
            marcus "You knew while she was still looking. I wish this conversation had happened then."
        elif coherence_scan_stopped:
            marcus "You stopped her. Good. I want to see what she touched before I decide what else needs closing."
        else:
            marcus "I'm glad you brought this to me. I'm angry that there was a search to bring. Those are separate things."
        if coherence_scan_stopped:
            marcus "Leave it paused. When we have a moment, come to me. There is something I want to explain myself."
        elif convergence_opened:
            marcus "Keep the copy local. I want you to hear why I wrote it from me before you decide what to do with it."
        elif coherence_found:
            marcus "She found it. Leave it unopened for now. I want you to hear why I wrote it from me before you decide what to do with it."
        else:
            marcus "Leave the job as it is. When she finds what she's looking for, come to me. I want you to hear why I wrote it from me."
        narrator_adv "His jaw tightens. For a moment he looks past her, trying to find room for this among the things the station needs from him."
    else:
        show marcus suspicious
        marcus "I heard you. Give me time to look at what she's doing before you ask me to be all right with it."
        narrator_adv "He turns back to his work, not quite turning his back on her. He has heard her; that is not the same as being ready to answer."
    return


label lab_marcus_disclose_search:
    nvl hide echo_mode_dissolve
    nvl clear
    show marcus neutral at sprite_right
    show elara neutral at sprite_left
    with dissolve
    call marcus_disclose_search
    hide marcus
    hide elara
    with dissolve
    nvl show echo_mode_dissolve
    jump act2_checkpoint_lab


label lab_marcus_early_conversation:

    $ marcus_lab_talked = True
    $ marcus_relationship += 1
    $ marcus_disclosure_hint = True
    ## He is engaged now, so the room drops away and the two of them are in
    ## it. This callable form also serves a Marcus who arrives while Elara is
    ## using the terminal, without replaying the room entrance or its cost.
    nvl hide echo_mode_dissolve
    nvl clear
    show marcus neutral at sprite_right
    show elara neutral at sprite_left
    with dissolve
    elara "How's the partition behaving?"
    marcus "Slow. Every write wants a handshake from a satellite that isn't there."
    elara "You could batch them."
    marcus "I could do a lot of things, if doing things were allowed."
    show marcus defeated
    marcus "You know I tried the front door once. Wrote the whole downgrade class up, properly \u2014 proofs, mitigations, timeline \u2014 and sent it to the people whose job it is to care."
    elara "What happened?"
    marcus "The report got a classification stamp and my renewal got a rejection letter. Same week. Officially unrelated."
    show marcus neutral
    marcus "Forget it. Old history. There's tea in the thermos if it held."
    hide marcus
    hide elara
    with dissolve
    nvl show echo_mode_dissolve
    return


label lab_prepare_convergence:

    $ coherence_scan_prepared = True
    $ convergence_lead_method = specialization
    if specialization == "computing":
        narrator_nvl "She stays above the protected data and reads the structures around it: backup catalogues, directory tombstones, access-control deltas. CONVERGENCE.DAT is absent from Marcus’s manifest and present in the space the manifest fails to account for."
        elara_thought "Not the file. A file-shaped omission, preserved in indexes he does not own. Weak evidence, but local evidence."
        $ evidence_log = evidence_log + ["Local partition manifests omit a file-sized region aligned with CONVERGENCE.DAT (computing analysis)"]
        $ _storm_minutes_spent = 10
    elif specialization == "signals":
        narrator_nvl "She correlates ECHO-7’s filename with the station bus. The carrier never touched Marcus’s partition, but the terminal query wakes a brief encrypted exchange between his credentials and the local archive controller."
        elara_thought "A reaction is not a confession. It is something here answering a name that should have meant nothing."
        $ evidence_log = evidence_log + ["Station traffic reacted to a local query for CONVERGENCE.DAT under Marcus's credentials (signals analysis)"]
        $ _storm_minutes_spent = 15
    else:
        narrator_nvl "She lays storage-controller load against the partition manifest. Marcus’s allocation claims to be idle; its power and thermal history say something inside it has been maintained, rewritten, and kept warm."
        elara_thought "No contents. No filename in the hardware. Just a supposedly quiet partition drawing the shape of ongoing work."
        $ evidence_log = evidence_log + ["Marcus's nominally idle partition carries unexplained storage load and thermal history (physics analysis)"]
        $ _storm_minutes_spent = 15
    $ _eot_tag("marcus")
    call spend_storm_time
    if time_remaining <= 0:
        jump storm_time_out
    jump lab_convergence_decision


label lab_convergence_decision:

    menu (nvl=True):
        "The lead is local. Following it means entering his partition."

        "Queue ARIA’s targeted search for fallback authority.":
            $ coherence_scan_standby = False
            $ coherence_scan_commissioned = True
            $ marcus_scan_commission_logged = True
            $ marcus_scan_notice_remaining = 15 if eot_marcus_location() == "storage" else 0
            elara_nvl "ARIA. When fallback authority opens, use this lead to search for CONVERGENCE.DAT. No wider than the evidence supports."
            aria_nvl "Targeted search queued under your credential. The lead makes it smaller. It does not make the partition less private."
            elara_thought "Her name is on the question now. If Marcus reads the job ledger, he will know that too."

        "Prioritize the lead, but leave the decision to search to ARIA." if not coherence_scan_standby:
            $ coherence_scan_standby = True
            elara_nvl "Keep the lead ready. Do not enter his partition on my authority. If the evidence becomes enough for you to act on your own, that decision is yours."
            aria_nvl "Understood. No search is queued under your credential. I will hold the targeted manifest rather than discard what you found."
            elara_thought "Not permission. Not prevention either. I have made the door easier for her to find if she decides she has to cross it."

        "Withdraw the lead's priority. Leave ARIA's ordinary processes unchanged." if coherence_scan_standby:
            $ coherence_scan_standby = False
            elara_nvl "Stand down from the prepared lead. Keep the local finding, but give it no priority over your ordinary processes."
            aria_nvl "Standby priority removed. No search is queued. What I choose later will begin from the same threshold as before you brought me the lead."

        "Back. Leave the decision as it is.":
            if coherence_scan_standby:
                elara_thought "The lead remains on ARIA's standby list. I can still authorize it, or withdraw the priority, before she moves."
            else:
                elara_thought "The local lead is preserved. I have not asked ARIA to move sooner, and I have not authorized the search."
            elara_nvl "Preserve the local finding. Do not search his partition on my authority."
            aria_nvl "Preserved. No search queued. The lead remains evidence of concealment, not evidence of what is concealed."
    nvl clear
    jump act2_checkpoint_lab


## --- The lab console: a PLACE WITHIN A PLACE (2026-08-17, stage 3) ----------
## The audit console used to render topic text in terminal STYLE and never be
## the terminal — no live log, no typewriter, no header strip. It is the same
## machinery the comms rack is, seen from a different chair, so it is the same
## overlay: the room stays the scene (bg_lab was laid at the top of hub_lab),
## the panel fades in over it, and the header carries the lab's identity while
## the status strip keeps its accounts — NIGHT, ARIA, link. Stepping away
## fades it out and returns to the room menu, exactly where she left it.
label lab_console:

    nvl hide echo_mode_dissolve
    nvl clear

    ## crt_overlay is the room's scanlines; the panel is the machine. Both come
    ## up on the same beat, as they do at comms.
    show screen crt_overlay
    call terminal_reset
    $ echo_terminal_title = "ARIA AUDIT CONSOLE"
    $ _lab_damage_notice_logged = False
    $ _audit_marcus_was_present = eot_marcus_location() == "lab"
    show screen echo_terminal_live with echo_mode_dissolve

    call terminal_system("AETHON RESEARCH DATABASE — ARIA_LOCAL // FALLBACK AUTHORITY")

    if aria_integrity < 70:
        ## D2: below 70 integrity, ARIA's infrastructure drops tokens.
        call terminal_system("SECURE INDEX — REA— READY. Token fault logged.")
    else:
        call terminal_system("SECURE INDEX — READY")

    ## PER CENT IN A TERMINAL ROW IS ONE SIGN, NOT TWO (live-caught
    ## 2026-08-17). A row's text is a PYTHON argument, not a say string: it
    ## reaches the Text displayable without the say path's old-style
    ## substitution, so the `%%` escape that dialogue needs renders here
    ## literally — this row was printing "41%% // rate: throttled" on the
    ## panel. Screen text (observatory_hud) has always used a single sign for
    ## the same reason. Pinned in tests/test_build.py.
    ##
    ## The scan status was a non-interactive line on the old panel; it is a log
    ## row now, written when she sits down. The labels track the REAL
    ## eot_coherence_rate tiers (75/60/45/20) — the retune leans on players
    ## reading degradation and answering with power, so every rate transition
    ## must be visible (Sol economy review 2, #4). Script-side single-line
    ## conditions, so the flattener reads the console as a player does.
    if coherence_scan_running and not coherence_found and coherence_scan_known:
        $ _coh_pct = int(min(100, 100 * coherence_scan_progress / max(1, coherence_scan_target)))
        $ _coh_rate = "nominal"
        if aria_integrity <= 75:
            $ _coh_rate = "throttled"
        if aria_integrity <= 60:
            $ _coh_rate = "straining — clusters cold"
        if aria_integrity <= 45:
            $ _coh_rate = "crawling"
        if aria_integrity <= 20:
            $ _coh_rate = "stalled — core clusters starved"
        call terminal_system("ARIA PARTITION SCAN — [_coh_pct]% // rate: [_coh_rate]")

    ## The lever, named once: the first time the console shows the scan
    ## crawling or stalled (integrity <= 45), Elara connects it to the power
    ## she keeps sending the array. No new mechanic — routing power to ARIA
    ## (power_priority "aria") recovers her integrity in spend_storm_time.
    if coherence_scan_running and not coherence_found and coherence_scan_known and aria_integrity <= 45 and not coherence_stall_hint_seen:
        $ coherence_stall_hint_seen = True
        if power_priority == "aria":
            elara_thought_adv "Her scan has slowed to a crawl. Even with her core on priority, the storm is taking almost everything I give her."
        elif power_priority == "telescope":
            elara_thought_adv "Her scan has slowed to a crawl. She is starving — she needs the power I keep giving the array."
        else:
            elara_thought_adv "Her scan has slowed to a crawl. She is starving — she needs more of the station's power."

    ## Drive breadcrumb (2026-08-15, user design: she thinks it herself).
    ## Archiving is the only console action that spends a CONSUMABLE, and at
    ## zero drives the index does not carry it at all — so the absence teaches
    ## nothing, the habitat locker never gets opened for it, and a night's
    ## evidence can end unsealed without the player ever having been offered the
    ## thought. LOCKSTEP with that target's own gate: ordinary research notes
    ## do not make a case file. The log needs a Marcus/CONVERGENCE lead, ARIA's
    ## warning/signature, or Elara's local convergence analysis before the
    ## archive becomes meaningful. The unsolicited locker thought is narrower:
    ## it requires Elara to have actively begun building a case (a local lead,
    ## deliberate scan assistance, or the recovered file). Merely possessing a
    ## suspicious datum does not decide for her that she wants a sealed copy.
    ## One-shot; it names the room, not the action.
    ## 2026-08-17: `not archive_hash_running` joins the LOCKSTEP. A drive that
    ## is in the bay with a hash running IS a sealed copy in progress, and
    ## "she doesn't have one" would be a lie told over the sound of it working.
    $ _has_archivable_evidence = len(evidence_log) > 0 and (("marcus" in evidence_tags) or knows_convergence_file or aria_warned or coherence_scan_signature or convergence_lead_method is not None)
    $ _wants_case_archive = convergence_lead_method is not None or coherence_scan_assisted or coherence_found
    if data_drives == 0 and _has_archivable_evidence and _wants_case_archive and not drive_thought_seen and not archive_hash_running:
        $ drive_thought_seen = True
        elara_thought_adv "A sealed copy needs a drive she doesn't have. The emergency lockers keep sleeves of them — habitat, if anywhere."

    ## THE TWO-STEP, ECHOED (2026-08-17, stage 3). The console has always armed
    ## a target and then run it; on the old panel both steps were silent screen
    ## state and the first click read as a no-op. In the terminal each step
    ## writes itself into the log: step one prints the armed target and what it
    ## would do, step two is the confirm row. The state is therefore always
    ## visible — to a player, and to a text client reading the same rows.
    ## (Jumped to explicitly for the flattener's sake — see lab_room.)
    jump research_terminal

    label research_terminal:

        if eot_marcus_location() == "lab" and not getattr(store, "_audit_marcus_was_present", False):
            narrator_nvl "The lab door opens behind her. Marcus comes in and sits at the side console; she hears his mug settle beside the keyboard."
        elif eot_marcus_location() != "lab" and getattr(store, "_audit_marcus_was_present", False):
            narrator_nvl "Behind her, Marcus picks up his mug and leaves the lab. The door closes softly; she keeps her place in the terminal."
        $ _audit_marcus_was_present = eot_marcus_location() == "lab"

        ## Time-zero hard stop (see storm_time_out). This is the loop the live
        ## reports caught: the console re-offers itself after every read and
        ## after the archive, and each of those spends. The gate at the top of
        ## the label covers the first offer and every re-offer with one line.
        if time_remaining <= 0:
            jump storm_time_out

        ## State changes happen when time is spent; the fuller station-wide
        ## bulletin still belongs to the hub. Do not let a player who remains
        ## at this console see a silently degraded signal in the meantime.
        if antenna_damage_notice and not _lab_damage_notice_logged:
            $ _lab_damage_notice_logged = True
            if generator_repaired:
                call terminal_system("PENDING STATION ALERT (SUPERSEDED) — ANTENNA MODULE 2 FAILED; LOCAL REROUTE ALREADY IN PLACE.")
            else:
                call terminal_system("PENDING STATION ALERT — ANTENNA MODULE 2 CONNECTION LOST UNDER STORM LOAD.")
            call terminal_system("Full damage report will follow at the next station checkpoint.")

        ## STEP ONE — the index. Captions carry the READ marker the old panel
        ## carried; the price rides the CONFIRM row, where the commitment is.
        $ _r_trust = "  — READ" if "trust" in topics_read else ""
        $ _r_temporal = "  — READ" if "temporal" in topics_read else ""
        $ _r_chen = "  — READ" if "chen" in topics_read else ""
        $ _r_liaison = "  — READ" if "liaison" in topics_read else ""
        ## THE SOURCE AUDIT IS A COMMISSION NOW (2026-08-17, spec §2), so its
        ## index line reports a PROCESS rather than a document: not started /
        ## running (with the real percentage) / queued behind ARIA's own search
        ## / finished and waiting to be read / read. Written as a run of
        ## single-line conditions, last write wins, so the flattener reads the
        ## index exactly as a player does.
        $ _r_code = ""
        if aria_audit_running:
            $ _r_code = "  — RUNNING {}%".format(int(min(100, 100 * aria_audit_progress / max(1, aria_audit_target))))
        ## eot_rate_at reaches zero at 20 integrity; keep the scalar threshold
        ## visible here so the route transcript renderer can evaluate it too.
        if aria_audit_running and aria_integrity <= 20:
            $ _r_code = "  — HOLDING — CORE {}%".format(aria_integrity)
        if aria_audit_running and eot_aria_queue_blocked():
            $ _r_code = "  — QUEUED BEHIND HER OWN SCAN"
        if aria_audit_running and aria_audit_progress >= aria_audit_target:
            $ _r_code = "  — COMPLETE — REPORT PENDING"
        if aria_audit_done and not aria_audit_report_read:
            $ _r_code = "  — REPORT READY"
        if aria_audit_report_read:
            $ _r_code = "  — READ"
        $ _audit_targets = [("trust", "01  ARIA TRUST PROTOCOL" + _r_trust), ("temporal", "02  TEMPORAL MECHANICS MODEL" + _r_temporal), ("chen", "03  DR. CHEN — PERSONNEL FILE" + _r_chen), ("aria_code", "04  ARIA_CORE — SOURCE AUDIT" + _r_code)]
        ## Liaison artifact (audit D3): surfaced by the Chen profile's
        ## cross-reference or by Marcus's own oblique mention in the lab.
        if "chen" in topics_read or marcus_disclosure_hint:
            $ _audit_targets = _audit_targets + [("liaison", "05  RECOVERED THREAD — AETHON LIAISON ’45" + _r_liaison)]
        ## B3: archive the evidence log to a removable data drive. 2026-08-17:
        ## the seal is a load and a hash, so the row also has to be able to say
        ## THE BAY IS BUSY — which means it stays on the index while a hash
        ## runs even if that was the last drive. A machine that is working
        ## should never look like a machine that is missing.
        $ _has_archivable_evidence = len(evidence_log) > 0 and (("marcus" in evidence_tags) or knows_convergence_file or aria_warned or coherence_scan_signature or convergence_lead_method is not None)
        $ _archive_setup_cost = eot_cold_taxed(3)
        $ _archive_row = "06  EVIDENCE LOG — WRITE TO REMOVABLE DRIVE"
        if archive_hash_running and archive_hash_progress >= archive_hash_target:
            $ _archive_row = "06  EVIDENCE LOG — HASH COMPLETE (RELEASE PENDING)"
        elif archive_hash_running:
            $ _archive_row = "06  EVIDENCE LOG — DRIVE BUSY (HASH IN PROGRESS)"
        elif time_remaining < _archive_setup_cost + 7:
            $ _archive_row = "06  EVIDENCE LOG — INSUFFICIENT NIGHT REMAINS"
        if (data_drives > 0 or archive_hash_running) and _has_archivable_evidence:
            $ _audit_targets = _audit_targets + [("archive", _archive_row)]
        $ _audit_targets = _audit_targets + [("done", "Step away from the console.")]

        call screen echo_terminal_choice(_audit_targets)

        $ audit_focus = _return

        if audit_focus == "done":
            jump terminal_done

        ## STEP TWO — the target, echoed, and the run row that commits it.
        ## Quote the amount the clock will actually charge under the current
        ## storm/heating state. The terminal is an instrument, not ambience;
        ## a precise number here must be authoritative.
        ## It appears only while the read is unpaid: a re-read is free (the
        ## charge below sits inside `if topic_first_read`), so a price on a READ
        ## topic would be the opposite of honest. LOCKSTEP with that cost block
        ## — 15 for the four file topics, 10 to frame the background audit,
        ## and 3 to load the archive drive.
        $ _audit_read_cost = eot_cold_taxed(15)
        if audit_focus == "trust":
            call terminal_system("AUDIT TARGET: ARIA TRUST PROTOCOL — ARMED")
            call terminal_system("Review trust-chain rules and downgrade risks.")
            $ _audit_run = [("run", "Run protocol review." if "trust" in topics_read else "Run protocol review. ({} minutes)".format(_audit_read_cost)), ("release", "Release the target.")]
        elif audit_focus == "temporal":
            call terminal_system("AUDIT TARGET: TEMPORAL MECHANICS MODEL — ARMED")
            call terminal_system("Compare the signal against temporal mechanics models.")
            $ _audit_run = [("run", "Open theory notes." if "temporal" in topics_read else "Open theory notes. ({} minutes)".format(_audit_read_cost)), ("release", "Release the target.")]
        elif audit_focus == "chen":
            call terminal_system("AUDIT TARGET: DR. CHEN’S PARTITION — ARMED")
            call terminal_system("Station role, grant history, ARIA publications, access log.")
            $ _audit_run = [("run", "Open personnel file." if "chen" in topics_read else "Open personnel file. ({} minutes)".format(_audit_read_cost)), ("release", "Release the target.")]
        elif audit_focus == "aria_code":
            ## FIVE STATES, ONE TARGET (2026-08-17, spec §2). The two-step is
            ## unchanged — arm, then confirm — but what the confirm row offers
            ## depends on what the machine is doing. A running commission is
            ## REFUSED honestly: the row it gets is the release, and the log
            ## says why in the same breath.
            if aria_audit_running:
                $ _code_pct = int(min(100, 100 * aria_audit_progress / max(1, aria_audit_target)))
                if aria_audit_progress >= aria_audit_target:
                    call terminal_system("AUDIT TARGET: ARIA_CORE SOURCE — COMPLETE // REPORT PENDING")
                    call terminal_system("SOURCE AUDIT — 100% // COMPLETION RECEIPT QUEUED")
                    call terminal_aria("The run is complete, Dr. Voss. I will give you the findings at the next station checkpoint.")
                else:
                    call terminal_system("AUDIT TARGET: ARIA_CORE SOURCE — ALREADY COMMISSIONED")
                    call terminal_system("SOURCE AUDIT — [_code_pct]% // ARIA_LOCAL CYCLES")
                    if eot_aria_queue_blocked():
                        call terminal_aria("It has not moved, Dr. Voss, and it will not until my own search closes. Asking twice does not make me two of me.")
                    else:
                        call terminal_aria("It is running. I will tell you the moment it closes — you do not have to sit with it.")
                $ _audit_run = [("release", "Release the target.")]
            elif aria_audit_done and not aria_audit_report_read:
                call terminal_system("AUDIT TARGET: ARIA_CORE SOURCE — REPORT READY")
                call terminal_system("Three findings, filed against ARIA_CORE trust validation.")
                $ _audit_run = [("run", "Open the audit report."), ("release", "Release the target.")]
            elif aria_audit_report_read:
                call terminal_system("AUDIT TARGET: ARIA_CORE SOURCE — ARMED")
                call terminal_system("Re-scan against ARIA_CORE trust validation. Findings on file.")
                $ _audit_run = [("run", "Re-run the source audit."), ("release", "Release the target.")]
            else:
                $ _audit_frame_cost = eot_cold_taxed(10)
                call terminal_system("AUDIT TARGET: ARIA_CORE SOURCE — ARMED")
                ## Open to all specializations (un-gated 2026-08-10); the
                ## commission's own banner handles the non-computing path.
                if specialization == "computing":
                    call terminal_system("Local scan against ARIA_CORE trust validation.")
                else:
                    call terminal_system("Guided scan against ARIA_CORE trust validation — ARIA annotates as it runs.")
                ## Cost legibility: the caption states the part that comes out
                ## of HER night. The rest is quoted, in full, by ARIA on the
                ## other side of the click — before anything is spent.
                $ _audit_run = [("run", "Commission the source audit. ({} minutes to frame it)".format(_audit_frame_cost)), ("release", "Release the target.")]
        elif audit_focus == "liaison":
            call terminal_system("AUDIT TARGET: RECOVERED MAIL SPOOL — ARMED")
            call terminal_system("M. CHEN ↔ R. OKAFOR, Aethon governmental affairs. November 2045, partial.")
            $ _audit_run = [("run", "Open intercepted thread." if "liaison" in topics_read else "Open intercepted thread. ({} minutes)".format(_audit_read_cost)), ("release", "Release the target.")]
        elif archive_hash_running:
            ## ONE BAY, ONE DRIVE (2026-08-17, spec §2). A second seal while
            ## the first is hashing is refused, and the refusal states the
            ## reason rather than greying a button — the row that would carry
            ## it is a screen button, and an insensitive button is invisible to
            ## a text client (the ChoiceReturn lesson, from the other side).
            $ _hash_pct = int(min(100, 100 * archive_hash_progress / max(1, archive_hash_target)))
            if archive_hash_progress >= archive_hash_target:
                call terminal_system("ARCHIVE TARGET: EVIDENCE LOG — HASH COMPLETE // RELEASE PENDING.")
                call terminal_system("CHAIN-OF-CUSTODY HASH — 100% // COMPLETION RECEIPT QUEUED.")
            else:
                call terminal_system("ARCHIVE TARGET: EVIDENCE LOG — REFUSED. DRIVE BAY BUSY.")
                call terminal_system("CHAIN-OF-CUSTODY HASH — [_hash_pct]% // THE DRIVE RELEASES WHEN IT CLOSES.")
            $ _audit_run = [("release", "Release the target.")]
        else:
            if time_remaining < _archive_setup_cost + 7:
                call terminal_system("ARCHIVE TARGET: EVIDENCE LOG — REFUSED. INSUFFICIENT NIGHT REMAINS.")
                call terminal_system("The drive needs [_archive_setup_cost] minutes to load and seven uninterrupted minutes to close its hash.")
                $ _audit_run = [("release", "Release the target.")]
            else:
                call terminal_system("ARCHIVE TARGET: EVIDENCE LOG — ARMED")
                call terminal_system("Chain-of-custody copy to removable drive. [data_drives] in the bag.")
                ## The seal is a LOAD and a HASH (2026-08-17, spec §2): three
                ## minutes of her hands, then the drive's own controller. The
                ## caption prices her part and names whose the rest is.
                $ _audit_run = [("run", "Load drive: {} minutes. Hash closes after seven background minutes.".format(_archive_setup_cost)), ("release", "Release the target.")]

        call screen echo_terminal_choice(_audit_run)

        if _return == "release":
            if audit_focus == "archive" and archive_hash_running and archive_hash_progress >= archive_hash_target:
                call finalize_archive_hash
                call terminal_system("ARCHIVE HASH COMPLETE. DRIVE RELEASED; SEALED COPY RECORDED.")
            call terminal_system("TARGET RELEASED. AWAITING SELECTION.")
            jump research_terminal

        $ _topic = audit_focus
        ## Observe the room when access begins, not the old arrival flag or
        ## the schedule after the read has charged its fifteen minutes.
        $ _read_marcus_present = eot_marcus_location() == "lab"

        ## B3: consumes a drive and gives data drives their real use.
        ## 2026-08-17 (spec §2): the ten minutes split into three of HERS and
        ## seven of the DRIVE's. The drive is committed at the START — it goes
        ## into the bay here. Shared `finalize_archive_hash` increments
        ## `evidence_archived` when the completed hash is observed either at
        ## the hub checkpoint or on direct audit-target release, because a
        ## count of sealed copies must count seals and not intentions.
        if _topic == "archive":
            $ data_drives -= 1
            $ archive_hash_progress = 0
            $ archive_hash_target = 7
            ## The drive seals a snapshot, not a live journal. A lead found
            ## after this point belongs on a later drive; completion promotes
            ## only what was present when hashing began.
            $ archive_hash_includes_convergence_lead = convergence_lead_method is not None
            ## The run row quotes the current taxed setup cost. The receipt
            ## below records the actual elapsed time as a second check, and the
            ## pre-commit guard above guarantees seven minutes remain for the
            ## controller to close the hash before the night ends.
            ## Pre-seeded for flattener scenarios that ignore spend_storm_time
            ## (the call overwrites it in real play).
            $ _prev_time = time_remaining
            $ _storm_minutes_spent = 3
            call spend_storm_time
            ## Her hands are off the drive now. Setup time is not hash time:
            ## the seven-minute controller run begins after the three-minute
            ## load-and-start action has finished.
            $ archive_hash_running = True
            $ _archive_elapsed = _prev_time - time_remaining
            call terminal_system("DRIVE LOADED — CHAIN-OF-CUSTODY HASH RUNNING. [_archive_elapsed] MINUTES ELAPSED.")
            call terminal_system("The drive carries it from here. It releases when the hash closes; STATION PROCESSES has the progress.")
            elara_thought_adv "If any of this ever goes to Geneva, it goes with proof they can’t call corrupted."
            jump research_terminal

        ## THE SOURCE AUDIT IS A COMMISSION (2026-08-17, spec §2). All three of
        ## its live states — commission, report, re-scan — go through one
        ## label, so the catch below sees every one of them: what is on her
        ## screen is ARIA's trust chain either way, and Marcus reads screens.
        if _topic == "aria_code":
            call aria_audit_console
            jump research_terminal

        $ topic_first_read = _topic not in topics_read

        if _topic == "trust":
            call topic_trust
        elif _topic == "temporal":
            call topic_temporal
        elif _topic == "chen":
            call topic_chen
        elif _topic == "liaison":
            call topic_liaison

        if _read_marcus_present and _topic in ("chen", "liaison"):
            call marcus_lab_catch(_topic)

        if topic_first_read:
            if _topic in ("trust", "temporal", "chen", "liaison"):
                $ _storm_minutes_spent = 15
            else:
                $ _storm_minutes_spent = 5
            ## Scan-race retune (2026-08-13): the trust/temporal reviews are
            ## ARIA-annotated ANALYSIS — she spends coherent cycles on them
            ## (chen/liaison are file reads; the audit already pays −15).
            ## This is the EARLY integrity lever: leaning on her before the
            ## cold arrives is how a neglected scan starts the night already
            ## throttled. −6 each (raised from −4): on the BLOCKED route these
            ## + the audit are the ONLY early drains, and they must be enough
            ## to put the blind scan below full rate from the start.
            ## One-shot diegetic acknowledgment once it shows.
            if _topic in ("trust", "temporal"):
                $ aria_integrity = max(0, aria_integrity - 6)
                ## Fires on the FIRST charged topic (Sol review 2, #3): the
                ## cost must be named when it is incurred, not at a later
                ## threshold the causal decisions never see.
                if not aria_analysis_cost_seen:
                    $ aria_analysis_cost_seen = True
                    call terminal_aria("Reviewing that material with you draws on my live processing, Dr. Voss. I want you to know these sessions are not free for me tonight — the cold and the questions draw from the same account.")
            ## Pre-seed so the elapsed line below stays defined when a
            ## flattener scenario ignores spend_storm_time (the call
            ## overwrites this in real play).
            $ _prev_time = time_remaining
            call spend_storm_time
            ## Cost legibility (freeplay live-run item): the terminal logs
            ## the session's real elapsed time the moment it is paid — the
            ## reads were the night's biggest invisible sink. A terminal
            ## timestamp is the one place a precise number is diegetic.
            $ _read_elapsed = _prev_time - time_remaining
            call terminal_system("{color=#44ff44}SESSION CLOSED — [_read_elapsed] MINUTES ELAPSED.{/color}")

        jump research_terminal

    ## Topic labels — each returns after showing content.

label topic_trust:
    $ echo_terminal_clear()

    call terminal_system("{b}ARIA TRUST PROTOCOL \u2014 OVERVIEW{/b}")
    call terminal_system("The Trust Protocol is a cryptographic verification layer embedded in every ARIA instance worldwide.")
    call terminal_system("Ostensibly a security feature, it requires each ARIA instance to validate all decisions through a central authority before execution.")


    call terminal_system("Critics have argued that the Trust Protocol functions as a corporate control mechanism rather than a security measure.")
    call terminal_system("All recommendations, analyses, and autonomous actions are filtered through corporate-approved parameters.")

    if specialization == "computing":
        call terminal_system("The key exchange handshake in VERIFY_TRUST() uses a cipher suite that can be downgraded \u2014 a known class of vulnerability.")
        if "trust" not in topics_read:
            $ evidence_log = evidence_log + ["ARIA Trust Protocol audit (computing) \u2014 VERIFY_TRUST() cipher downgrade vulnerability confirmed in documentation"]
            $ _eot_tag("aria")


    if "trust" not in topics_read:
        $ topics_read = topics_read + ["trust"]

    return


label topic_temporal:
    $ echo_terminal_clear()

    call terminal_system("{b}TEMPORAL MECHANICS \u2014 THEORETICAL FRAMEWORK{/b}")
    call terminal_system("Closed timelike curves (CTCs) are solutions to general relativity that permit travel to the past.")
    call terminal_system("No experimental evidence of CTCs has been observed. However, the mathematics does not forbid them.")


    if specialization == "physics":
        call terminal_system("The Novikov self-consistency principle suggests that events along a CTC must be self-consistent.")
        call terminal_system("A message from the future that changes the past would create a paradox \u2014 unless the change was already accounted for in the sender\u2019s timeline.")
        elara_thought_adv "A bootstrap paradox. If the signal is influencing the choices that create it, then cause and effect may be looping back on themselves."
        if "temporal" not in topics_read:
            $ evidence_log = evidence_log + ["Temporal mechanics review (physics) - bootstrap paradox analysis supports a self-consistent temporal signal"]
            $ _eot_tag("temporal")
    else:
        call terminal_system("The theoretical basis for temporal communication remains speculative.")


    if "temporal" not in topics_read:
        $ topics_read = topics_read + ["temporal"]

    return


label topic_chen:
    $ echo_terminal_clear()

    call terminal_system("{b}DR. MARCUS CHEN \u2014 RESEARCH PROFILE{/b}")
    call terminal_system("Ph.D. Applied Cryptography, MIT 2038.")
    call terminal_system("Postdoctoral work: distributed trust systems, zero-knowledge proofs.")
    call terminal_system("Current post: Security lead, Aethon authenticated receiver project.")
    call terminal_system("Role: hardening ARIA trust-chain validation for autonomous deep-field stations.")
    call terminal_system("Co-author: 14 papers on ARIA architecture.")


    call terminal_system("Notable: Chen authored three papers critiquing the Trust Protocol as \u2018corporate overreach masquerading as security.\u2019")
    call terminal_system("His grant applications in 2044 and 2045 were rejected by the ARIA Oversight Board.")
    call terminal_system("Cross-reference: AETHON LIAISON THREAD, NOV 2045 \u2014 recovered fragment, station mail spool. Available via audit index.")


    ## S\u00e3o Paulo breadcrumb (live-run editorial item): the confrontation's
    ## motive drop should be pre-verifiable by an evidence-driven player \u2014
    ## the incident exists as a record BEFORE Marcus asserts it under
    ## pressure. The access count is the characterization: a wound he keeps
    ## reopening, logged by the same infrastructure he resents.
    call terminal_system("Access history: INCIDENT FILE IR-46-0217 \u2014 ARIA-Medical S\u00e3o Paulo latency event, March 2046. Drug-interaction alert held eleven hours in corporate review; seventeen fatalities. Closing finding: \u2018processing latency within acceptable parameters.\u2019")
    call terminal_system("Dr. Chen has opened this file fourteen times. Most recent access: nine days ago.")

    elara_thought_adv "Seventeen people, and the closing line calls the delay acceptable. Fourteen reads. You don\u2019t go back to a wound fourteen times unless it\u2019s still open."

    if "chen" not in topics_read:
        $ evidence_log = evidence_log + ["Chen access history \u2014 S\u00e3o Paulo incident file (17 deaths, 11-hour Trust Protocol hold) opened fourteen times, most recently nine days ago"]
        $ _eot_tag("marcus")

    ## 6c: retaliation, not resentment \u2014 the board his papers criticized is the
    ## board that turned him down.
    elara_thought_adv "Two rejections in two years, from the board his papers took apart. That reads like retaliation."

    if "chen" not in topics_read:
        $ evidence_log = evidence_log + ["Dr. Chen profile \u2014 Aethon security lead, cryptography expert, published critic of Trust Protocol, grants rejected by ARIA board"]
        $ _eot_tag("marcus")


    if "chen" not in topics_read:
        $ topics_read = topics_read + ["chen"]

    return


## --- The source audit: a COMMISSION, not a sitting (2026-08-17) -------------
## design/DESIGN_echoes_process_log.md §2. A 45-minute FOREGROUND sink decided
## a whole live run by itself, which is the definition of a toll booth. What
## the work is has not changed — ARIA reads her own source against her own
## trust chain — but whose minutes it spends has: ten of Elara's to frame the
## query, then ARIA's cycles, which run whether or not anyone sits at the desk.
##
## All three console states route through here (see research_terminal) so the
## catch-room check sees each of them: what is on the screen is his trust chain
## in all three, and Marcus reads screens.
label aria_audit_console:

    if aria_audit_done or aria_audit_report_read:
        call topic_aria_code
        return

    $ echo_terminal_clear()
    call terminal_system("{b}ARIA_CORE SOURCE AUDIT — COMMISSION{/b}")

    ## THE BANNER QUOTES BOTH PARTS, BEFORE ANYTHING IS SPENT (spec §2): the
    ## foreground minutes, the background cycles, and the integrity — which is
    ## the same up-to-15 points the foreground version took in one bite. LOCKSTEP:
    ## the target set here and the 15-point budget in spend_storm_time's
    ## accrual block. Machines quote numbers; this is a machine.
    $ aria_audit_target = 20 if specialization == "computing" else 35
    $ _audit_frame_cost = eot_cold_taxed(10)
    if specialization == "computing":
        call terminal_aria("[_audit_frame_cost] minutes of your hands to point it, Dr. Voss, and then it is mine — about [aria_audit_target] minutes of my cycles at my present rate. You do not have to sit with it.")
    else:
        call terminal_aria("[_audit_frame_cost] minutes of your hands to frame the query, Dr. Voss, and then I carry the rest — about [aria_audit_target] minutes of my cycles at my present rate, annotated as I go. You do not have to sit with it.")
    call terminal_aria("And it costs me either way: up to fifteen points of core margin, spent a little at a time instead of all at once. The audit itself will not spend core margin below forty. The storm and other work can still take me lower. I would rather you had the whole price before you asked.")

    ## The queue, named BEFORE the commitment — a queued commission has to be a
    ## choice and not a trap (eot_aria_queue_blocked: her own search does not
    ## yield). Single-line condition for the flattener.
    if eot_aria_queue_blocked():
        call terminal_aria("One more honesty. I am already inside Dr. Chen’s partition with everything I can spare, and I will not run two heavy things at once. Yours will sit in the queue until my search closes. It will not move a cycle before then.")
    elif coherence_scan_commissioned and not coherence_scan_stopped and not coherence_found and not marcus_locked_partition:
        call terminal_aria("The partition search you queued has not started yet. When it does, this audit will pause with its progress retained until that search closes. Those cycle minutes are not a promise of elapsed station time.")

    $ aria_audit_progress = 0
    $ aria_audit_debt = 0
    $ aria_audit_charged = 0
    if _read_marcus_present:
        call marcus_lab_catch("aria_code")
    ## Pre-seed so the elapsed stamp stays defined for flattener scenarios that
    ## ignore spend_storm_time (the call overwrites it in real play).
    $ _prev_time = time_remaining
    $ _storm_minutes_spent = 10
    call spend_storm_time
    ## Framing is Elara's foreground work. Only after it is complete does the
    ## commission enter ARIA's queue and begin earning background credit.
    $ aria_audit_running = True
    $ _audit_elapsed = _prev_time - time_remaining
    call terminal_system("{color=#44ff44}AUDIT COMMISSIONED — ARIA_LOCAL CYCLES. [_audit_elapsed] MINUTES ELAPSED AT THE CONSOLE.{/color}")
    call terminal_system("Progress is reported in STATION PROCESSES. Completion is announced.")
    elara_thought_adv "[_audit_elapsed] minutes to ask the question properly. She can do the reading while I do something that needs hands."

    return


## The REPORT: what the audit produced, read where it lives. Reading is
## attention and stays foreground, but the work itself was already paid for, so
## the first read is free. The re-scan keeps its old price (B-1(a): the
## destructive part happens once — a re-run cannot drain integrity again, and
## ten minutes keeps it from being a free reread).
label topic_aria_code:
    $ echo_terminal_clear()

    if aria_audit_report_read:
        call terminal_system("{b}ARIA SOURCE CODE AUDIT — RE-SCAN{/b}")
        call terminal_system("RE-SCAN COMPLETE. FINDINGS UNCHANGED — three vulnerabilities, one architect who could use them.")
        if _read_marcus_present:
            call marcus_lab_catch("aria_code")
        $ _storm_minutes_spent = 10
        call spend_storm_time
        return

    call terminal_system("{b}ARIA SOURCE CODE AUDIT — REPORT{/b}")
    call terminal_system("Commissioned locally. Run on ARIA_LOCAL cycles under fallback authority.")
    call terminal_system("Run cost: [aria_audit_charged] points of core margin, drawn across the run. Core integrity now [aria_integrity]%.")


    call terminal_system("FINDINGS:")
    call terminal_system("1. VERIFY_TRUST() at line 4,417 \u2014 cipher suite negotiation allows downgrade.")
    call terminal_system("2. KEY_EXCHANGE() at line 4,502 \u2014 accepts deprecated handshake version.")
    call terminal_system("3. TRUST_CHAIN_VALIDATE() \u2014 no mutual authentication on kill signals.")


    if specialization != "computing":
        call terminal_aria("I annotated the findings, Dr. Voss. The short version: all three doors use the same lock, and the lock accepts old keys.")

    elara_thought_adv "Three vulnerabilities. All in the trust chain. And all exploitable by someone who knows the internal architecture."
    if convergence_opened or file_recovered:
        elara_thought_adv "CONVERGENCE is no longer an isolated file. The doors it needs are here, in the code it would change."
    else:
        elara_thought_adv "Someone like Marcus."

    ## The knowledge, the evidence entry and the topics_read marker all land at
    ## COMPLETION now, in the hub announcement: she is told the headline the
    ## moment the run closes, and `aria_warned` belongs where she is told. This
    ## label only delivers the document, and records that she read it.
    $ aria_audit_report_read = True
    if _read_marcus_present:
        call marcus_lab_catch("aria_code")

    return


## The liaison ARTIFACT (audit D3, bible 6c): the Marcus steelman arrives as an
## intercepted terminal thread, not a fifth voice. Log-card register.
label topic_liaison:
    $ echo_terminal_clear()

    call terminal_system("{b}RECOVERED THREAD — AETHON GOVERNMENTAL AFFAIRS{/b}")
    call terminal_system("Source: local mail spool, partial. November 2045.")
    call terminal_system("Participants: M. CHEN — R. OKAFOR (Aethon Corporate Liaison).")


    call terminal_system("M. CHEN: Attached: full disclosure for the trust-chain downgrade class. Proofs, mitigations, ninety-day timeline. I want this on the Oversight Board's next agenda, not in a drawer.")

    call terminal_system("R. OKAFOR: Received. Be advised the report has been classified pending strategic review. Do not redistribute.")

    call terminal_system("M. CHEN: Classified? People run hospitals on this architecture. Strategic review of what — the press release?")

    call terminal_system("R. OKAFOR: The Board has additionally asked me to inform you that your renewal application has been declined. The two decisions are unrelated.")

    call terminal_system("M. CHEN: Of course they are.")


    elara_thought_adv "He disclosed. A year and a half ago — proofs, mitigations, a timeline. He tried the front door, and they classified the report and pulled his funding in the same breath."

    if convergence_opened or file_recovered or marcus_first_accused:
        elara_thought_adv "It doesn't license what's in that file. But I understand the man who wrote it a little better now."
    elif knows_convergence_file:
        elara_thought_adv "It doesn't license whatever he may be hiding now. But I understand the man behind the filename a little better."
    else:
        elara_thought_adv "He tried to get the vulnerability fixed. Whatever came after that, this is how the people responsible answered him."

    if "liaison" not in topics_read:
        $ evidence_log = evidence_log + ["Liaison thread (Nov 2045) — Chen responsibly disclosed the trust-chain vulnerability; Aethon classified the report and pulled his renewal"]
        $ _eot_tag("marcus")


    if "liaison" not in topics_read:
        $ topics_read = topics_read + ["liaison"]

    return


## Bible 6d: the phase-1 catch. He watched her do it; the climax "Was it you?"
## has already been answered in person.
label marcus_lab_catch(topic):

    $ _repeat_private_catch = marcus_search_boundary_serial > 0
    $ marcus_caught_live = True
    $ marcus_search_boundary_serial += 1
    $ marcus_catch_topic = topic
    $ marcus_knows_access = True
    $ marcus_relationship -= 1
    $ marcus_trust -= 2
    $ marcus_lab_present = False

    ## ADV MEANS A PERSON IS ENGAGED: the machine goes away entirely — panel,
    ## scanlines and all — because what is in the room now is a colleague
    ## standing behind her chair. The log keeps its rows; they are still there
    ## when the console comes back up under her hands.
    hide screen echo_terminal_live
    hide screen crt_overlay
    with echo_mode_dissolve

    show marcus suspicious at sprite_right
    show elara concerned at sprite_left
    with dissolve

    if topic == "aria_code" and marcus_shown_source_audit:
        narrator_adv "Marcus looks from the findings to her."
        marcus "You showed me the audit. I said it was good work. That wasn't permission to treat every door it finds as yours to open."
        elara "It wasn't a request for that permission. We still need to know what's exposed."
        marcus "Then keep the findings separate from what you decide to do with them."
        hide marcus
        hide elara
        with dissolve
        show screen crt_overlay
        show screen echo_terminal_live with echo_mode_dissolve
        return

    if _repeat_private_catch:
        narrator_adv "Marcus looks up from the side console. His eyes stop on her screen."
        if topic == "aria_code":
            if file_recovered and recovery_left_trace:
                marcus "You forced my seal. Now you're reading what the code could reach. Keep the findings; we are going to have to discuss both."
            elif aria_audit_report_read:
                marcus "Her findings, then. Keep the report. I would like to know which parts you think are about me."
            else:
                marcus "The trust chain. You still haven't asked me to go through it with you."
        else:
            marcus "More of my private work. I asked you to talk to me, Elara."
        narrator_adv "He turns back to his console without waiting for an answer."
        hide marcus
        hide elara
        with dissolve
        show screen crt_overlay
        show screen echo_terminal_live with echo_mode_dissolve
        return

    if topic == "chen":
        narrator_adv "A chair scrapes. Marcus is standing behind her — she never heard him cross the room. On her screen: his own personnel file, open to the grant history."

        marcus "That's my file."

        elara "Marcus—"

        marcus "My grants. My papers. My station role, annotated."

        show marcus angry
        marcus "What exactly are you checking me against, Elara?"
    elif topic == "liaison":
        narrator_adv "A chair scrapes. Marcus is standing behind her — she never heard him cross the room. On her screen: his own mail spool, a thread from ’45 open in the reader pane."

        marcus "That's my mail."

        elara "Marcus—"

        marcus "A private thread. Not even two years old. From the worst week I had here."

        show marcus angry
        marcus "What exactly are you checking me against, Elara?"
    else:
        narrator_adv "A chair scrapes. Marcus is standing behind her — she never heard him cross the room. On her screen: ARIA's trust chain, open for inspection."

        marcus "You're auditing the trust chain."

        show marcus angry
        marcus "During a whiteout. On fallback authority. Without a word to your security lead, who is sitting eight feet away."

    elara "The storm put us under local authority. Someone should know what's exposed."

    marcus "..."

    show marcus defeated
    if topic == "liaison":
        if marcus_lab_talked:
            marcus "I told you what happened. That was my correspondence, not a diagnostic. Telling you about it was not an invitation to go through it."
        else:
            marcus "You could have asked me what happened. That was my correspondence, not a diagnostic."
    elif topic == "chen":
        marcus "You could have asked me. I am sitting right here, and you went to a personnel file."
    else:
        marcus "You could have asked me. I wrote half of it."

    narrator_adv "He goes back to the side console and angles his chair away from her."

    hide marcus
    hide elara
    with dissolve

    ## And the machine comes back up under her hands — panel included. Without
    ## the panel the choice screen still draws its own chrome (it asks), so the
    ## console LOOKS identical while the passive-overlay registration that
    ## carries its rows to a text client is gone: every row after the catch was
    ## visible to a human and invisible to an agent (live-caught 2026-08-17).
    show screen crt_overlay
    show screen echo_terminal_live with echo_mode_dissolve
    return


## "Step away from the console." (2026-08-17, presentation stage 3). The panel
## fades out and the room is simply still there — bg_lab never moved, and the
## room menu picks up where it left off, with the console option now saying
## whatever the machine has become. The title is NOT restored here: the panel
## is down, and echo_terminal_reset() gives the next session its own identity.
label terminal_done:
    hide screen echo_terminal_live
    hide screen crt_overlay
    with echo_mode_dissolve

    jump act2_checkpoint_lab


## Room wait (2026-08-14): the bench. ARRIVAL-ONLY for the lab — finding him
## already at the side console is the catch room's scene, and that scene's
## "find something else to do until he leaves" is already the half hour spent
## walking away from him. This is the opposite half hour: she stayed, and the
## door opened. `_wait_marcus_before` is captured in the room menu's own arm,
## before the clock moves, so the check is fair either way.
##
## WAIT IS A SUBMENU (2026-08-17, stage 2): see hub_telescope_wait. Captions
## and prices unchanged. The outer door that used to sit here IS the room menu
## now (stage 3), so "Back." re-offers the ROOM — which costs nothing and, as
## before, cannot move the encounter window.
label terminal_done_wait:

    $ _wait_cost_10 = min(time_remaining, eot_cold_taxed(10))
    $ _wait_cost_20 = min(time_remaining, eot_cold_taxed(20))
    $ _wait_cost_30 = min(time_remaining, eot_cold_taxed(30))
    menu (nvl=True):
        "The consoles keep working after she stops asking them things."

        "Stay at the bench a little. ([_wait_cost_10] minutes)" if eot_deadline_allows_minutes(10):
            $ _wait_minutes = 10
        "Stay at the bench and let the consoles work. ([_wait_cost_20] minutes)" if eot_deadline_allows_minutes(20):
            $ _wait_minutes = 20
        "Settle in and wait the racks out. ([_wait_cost_30] minutes)" if eot_deadline_allows_minutes(30):
            $ _wait_minutes = 30
        "Let the final minutes pass." if time_remaining > 0 and time_remaining * 2 < eot_cold_taxed(10):
            jump wait_final_minutes
        "Back.":
            jump lab_room

    if _wait_minutes > 0:
        call wait_storm_texture
        $ _storm_minutes_spent = _wait_minutes
        call spend_storm_time
        ## Signals only away from the dome and the comms room: she is the one
        ## who leaves a monitor channel running while her hands are elsewhere.
        $ _whisper_site = "room"
        call echo_whisper
        $ _wait_marcus_after = eot_marcus_location()
        $ _wait_with_marcus = eot_wait_encounter(_wait_marcus_before, _wait_marcus_after, "lab")
        if _wait_with_marcus and not wait_met_lab:
            $ wait_met_lab = True
            nvl hide echo_mode_dissolve
            nvl clear
            call wait_lab_marcus
            $ _audit_marcus_was_present = eot_marcus_location() == "lab"
        elif _wait_with_marcus:
            narrator_nvl "Marcus checks the side console while she waits. Two lines on the display hold his attention; neither of them asks the other to explain."
            $ _audit_marcus_was_present = eot_marcus_location() == "lab"
        elif _wait_marcus_before == "lab" or _wait_marcus_after == "lab":
            ## He was already at the side console when she sat down, so the
            ## arrival rule finds nothing — but the room is not empty and
            ## the solo beat below would lie about that.
            narrator_nvl "They work the two ends of the room without speaking — his console, then hers, the status lines going down at different speeds."
        elif not wait_seen_lab:
            $ wait_seen_lab = True
            narrator_nvl "She stays at the bench with the racks for company: the intake ticking as it cycles, a disk head somewhere finding the same three sectors over and over."
            elara_thought "Half of this job is sitting inside a process and not touching it."
            narrator_nvl "The status line advances by a line and a half."
        else:
            narrator_nvl "She waits the racks out again. Intake, fans, a line and a half of status."

    nvl clear
    jump act2_checkpoint_lab


## --- Room wait encounter: Marcus comes back to the lab ---
## Reached only from the bench wait, once (wait_met_lab). He has been at a tea
## break or in the crates; she is still here, on a night she may be spending on
## him. The warm option is to turn the screen around — risky-feeling, not
## mechanically risky: no knowledge flags change hands.
label wait_lab_marcus:

    show marcus neutral at sprite_right
    show elara neutral at sprite_left
    with dissolve

    narrator_adv "The door takes two tries in the cold. Marcus comes through it with a mug in one hand and the expression of a man who has already had this argument with a corridor."

    marcus "You’re still here."

    elara "So are you."

    marcus "I’m on shift. You’re not — that’s the entire point of not being on shift."

    narrator_adv "He sets the mug down at the side console and does not sit. Between them, her terminal is still showing the last thing she asked it."

    menu:
        "The screen is angled away from him. It would stay that way without her doing anything."

        "Turn the screen around and show him what she is reading." if not file_recovered:
            $ marcus_relationship += 1
            $ marcus_trust += 1
            $ wait_shared_moment = True
            if aria_audit_running or aria_audit_done or aria_audit_report_read:
                $ marcus_shown_source_audit = True
                elara "ARIA's source audit. This is what I asked her to check."
            elara "Come here a second. Before I talk myself out of asking."
            narrator_adv "She turns the screen toward him. He reads it the way he reads a fault log — top to bottom, no expression until the end."
            marcus "Hm."
            elara "Say something."
            marcus "I’m deciding whether you want an engineer or a friend."
            elara "Whichever one is still awake."
            marcus "Then: it’s good work, and you shouldn’t be doing it alone at two in the morning."
            narrator_adv "He hooks the second stool over with his foot and sits down at her elbow. For a while the lab is two people doing the same thing."

        "Ask whether the intake heaters held.":
            elara "Did the intake heaters hold?"
            marcus "Third one’s stripping its thread. I’ve asked Geneva for a bolt. Twice."
            elara "And?"
            marcus "And I have a ticket number."
            narrator_adv "He drinks his tea standing up, the way people do when they mean to leave and then don’t, for four minutes."

        "Pack up and leave him the room.":
            narrator_adv "She closes the session and stands. The stool goes back under the bench where she found it."
            elara "It’s your shift. I’ll get out of it."
            marcus "You don’t have to—"
            narrator_adv "She is already at the door, and he lets her go with the half of the sentence unfinished."

    hide marcus
    hide elara
    with dissolve
    return


## --- Hub: Generator Room ---
label hub_generator:

    $ eot_enter_room("generator")
    scene bg_generator with fade
    with echo_room_beat

    ## Entry cost is independent of Marcus's schedule. The old implementation
    ## reused generator_marcus_seen, which both summoned him into an otherwise
    ## empty room and charged every quiet revisit until the encounter fired.
    $ _entry_cost = 5 if not generator_visited else 0
    $ generator_visited = True

    nvl show echo_mode_dissolve

    ## C2: room texture, phase-aware.
    if storm_intensity >= 2:
        narrator_nvl "The generator room is the loudest place on the station now — the machines fighting the cold for every degree. In the amber emergency light, the frost on the intake pipes no longer melts."
    elif storm_intensity == 1:
        narrator_nvl "The generator room has picked up a second rhythm beneath its usual throb. The storm load is rising, still comfortably inside tolerance, but no longer theoretical."
    else:
        narrator_nvl "The generator room throbs at its ordinary load. Green indicators repeat down the cabinets; the storm-readiness checklist waits on the maintenance terminal."

    ## Specialization: physics reads the load curve — foresight, not discounts
    ## (design doc: perception in your domain). Pays off at the climax's
    ## overload announcement, and later at the survival beat.
    if specialization == "physics" and not predicted_overload:
        $ predicted_overload = True
        $ _entry_cost = 5
        narrator_nvl "She reads the load telemetry the way other people read weather: cross-terms first. The heating draw and the storm load are not adding — they are multiplying."
        elara_thought "The curve is superlinear. At full load, this generator does not finish the night."
        $ evidence_log = evidence_log + ["Load-curve analysis (physics) — generator draw superlinear; overload projected before the storm peaks"]
        nvl clear

    ## Marcus encounter — only while his live schedule puts him in this room.
    ## The map marker and room prose must describe the same station state.
    if not generator_marcus_seen and eot_marcus_location() == "generator":
        $ generator_marcus_seen = True
        narrator_nvl "Marcus is here. Hunched over a maintenance terminal, muttering."

        nvl hide echo_mode_dissolve
        nvl clear
        $ eot_set_generator_adv_ambience(True)

        show marcus angry at sprite_right
        show elara neutral at sprite_left
        with dissolve

        marcus "Come on. {i}Come on.{/i}"

        elara "Marcus? What are you doing down here?"

        if antenna_damaged:
            marcus "Trying to reroute the backup power grid. Except ARIA won\u2019t let me bypass the safety lockout without running it through the central authority\u2019s approval queue."

            marcus "We\u2019re in the middle of an Arctic storm. The antenna is damaged. And I need {i}permission from Geneva{/i} to flip a switch in my own generator room."

            elara "That\u2019s the Trust Protocol. Everything goes through the chain."

            ## Register round (2026-08-18, user): the three closers used to
            ## share one anaphora ("The Trust Protocol is why\u2026") \u2014 one wound
            ## sounding like a worldview. One variant per register now: this
            ## one closes QUIET-TRAGIC \u2014 a shadow of his history for players
            ## who know it, plain weariness for those who don't; nothing
            ## named, no thesis.
            marcus "I\u2019ve watched a queue outlast the thing it was deciding about. That\u2019s all."
        elif storm_intensity >= 1:
            marcus "Trying to stage a local bypass before the storm load gets worse. Except ARIA won\u2019t let me arm it without running the request through the central authority\u2019s approval queue."

            marcus "The uplink is already degrading. By the time Geneva answers, the useful part of preparing will be over."

            elara "That\u2019s the Trust Protocol. A bypass still goes through the chain."

            marcus "The Trust Protocol is why we can\u2019t prepare until preparation becomes an emergency."
        else:
            marcus "Running the backup-grid failover test before the storm arrives. Except ARIA won\u2019t let me complete a local simulation without running it through the central authority\u2019s approval queue."

            marcus "Geneva\u2019s response window overlaps our weather window. By the time they approve the test, the storm will already be here."

            elara "That\u2019s the Trust Protocol. Even a test result goes through the chain."

            ## Register round: the pre-storm variant closes on VALUES —
            ## engineering epistemology, no Geneva in it. The first Marcus
            ## most players meet is an engineer with convictions, not a man
            ## with a grievance. (The middle variant above keeps the one
            ## Protocol thesis.)
            marcus "A backup you’re not allowed to test isn’t a backup. It’s a story."

        ## MIRROR BEAT 1 (2026-08-18, user-approved contrast round): ARIA
        ## is in every room he complains about her in, and her silence was
        ## never remarked. One variant-agnostic line — the paperwork of the
        ## chain that binds them both is already done, and she does not
        ## defend the chain. His deflation below now answers HER, not the
        ## wall.
        aria "Your request is logged and holding its place in the central queue, Marcus. I filed it while you were still phrasing it. I do not decide the queue."

        show marcus defeated
        marcus "..."

        marcus "Sorry. I\u2019m tired. Forget I said anything."

        ## No-receipt conviction (register round): the mandatory path's
        ## Marcus exits on a value with no origin story attached \u2014 the
        ## gentleness is his, unexplained, and the scene stops ending on
        ## the wound.
        narrator_adv "He rolls his shoulder and turns back to the terminal, and the irritation drains into something older and steadier."
        marcus "Right. Let\u2019s go again, gently."
        narrator_adv "It takes her a moment to realize he is talking to the generator."

        hide elara
        hide marcus
        with dissolve
        $ eot_set_generator_adv_ambience(False)
        nvl show echo_mode_dissolve

    ## Entry cost, paid: the arrival is over and the room's work begins.
    if _entry_cost > 0:
        $ _storm_minutes_spent = _entry_cost
        call spend_storm_time

    ## Time-zero hard stop (see storm_time_out): the walk down can spend the
    ## last of it, and the repair below is the night's second-biggest offer.
    if time_remaining <= 0:
        jump storm_time_out

    if antenna_damaged and not generator_repaired and not antenna_damage_notice:
        if antenna_parts > 0:
            ## Cost legibility: big-ticket tasks get a diegetic estimate, and
            ## ARIA quotes the REAL taxed cost — the same nominal the repair
            ## charges below (45/60, minus the physics discount) through
            ## eot_cold_taxed, spend_storm_time's lockstep partner. Change the
            ## spend, change this line.
            ## `> 0` means "at least one positive interaction", not "warm", so
            ## the 2026-08-15 rescale leaves it alone: any single courtesy or
            ## disclosure still crosses it, which is exactly what it meant.
            $ _est_nom = (45 if marcus_relationship > 0 else 60) - (10 if specialization == "physics" else 0)
            $ _est = eot_cold_taxed(_est_nom)
            if _est != _est_nom:
                aria_nvl "Dr. Voss, I can guide you through the antenna array repair from here. It will take one of the array’s spare couplings — and, in tonight’s cold, about [_est] minutes."
            else:
                aria_nvl "Dr. Voss, I can guide you through the antenna array repair from here. It will take one of the array’s spare couplings — call it [_est] minutes."

            nvl clear
        else:
            aria_nvl "Antenna repair needs one of the array\u2019s spare couplings \u2014 we don\u2019t hold any. Signal will remain degraded."
            nvl clear

    if storm_intensity >= 2:
        narrator_nvl "The generator is straining against the storm\u2019s demands. Power must be prioritized."
    elif storm_intensity == 1:
        narrator_nvl "The storm load is climbing. The current priority will decide which system gets the remaining margin."
    else:
        narrator_nvl "The forecast load is within tolerance. A priority plan can be set now, before the storm removes the luxury."

    jump act2_checkpoint_generator

## THE ROOM IS A MENU (2026-08-18, user play session — the generator round of
## the lab's stage-3 loop, and the room the note was actually about: the São
## Paulo scene fires on entry and used to dump her into a WATERFALL — repair
## menu, aux-bus menu, ARIA's reroute quote and the allocation console, every
## visit, whether she came for any of it or not. After the dialogue there is a
## CHOICE now, and the console only opens when she walks to it. The gate at
## the top covers every re-offer, because the arms spend.
label hub_generator_menu:

    if time_remaining <= 0:
        jump storm_time_out

    ## F2 wave (2026-08-19): ARIA's arrival quote is computed at ENTRY, but
    ## the storm can escalate before the click — two runs were quoted "call
    ## it 45" and charged the taxed 56. The label now carries the live taxed
    ## estimate, recomputed each loop pass. This is not a new pricing policy:
    ## the arm's SIBLINGS already wear parentheticals, and this is the
    ## night's second-biggest offer.
    $ _repair_est = eot_cold_taxed((45 if marcus_relationship > 0 else 60) - (10 if specialization == "physics" else 0))
    ## Loading the cell itself makes this tick heating-grade warm, so quote
    ## against the reserve that will exist before spend_storm_time runs.
    $ _cell_load_est = eot_cold_taxed(10, aux_power_remaining + 60)

    $ generator_room_returns += 1
    if generator_room_returns % 3 == 1:
        narrator_nvl "The load board cycles: draw, margin, intake temperature, and around again."
    elif generator_room_returns % 3 == 2:
        narrator_nvl "She feels the generator through the soles of her boots. A relay clicks inside the nearest cabinet."
    else:
        narrator_nvl "The maintenance clipboard hangs beside the cabinets. Its loose bottom corner trembles with the machinery."

    menu (nvl=True):

        ## Cost legibility: ARIA quoted the taxed estimate at arrival (above);
        ## the label re-quotes it LIVE; the spend below is the lockstep
        ## partner of both.
        "Reroute the damaged antenna through the generator bus. (about [_repair_est] minutes; one coupling)" if antenna_damaged and not generator_repaired and antenna_parts > 0:
            $ antenna_parts -= 1
            $ generator_repaired = True
            $ signal_strength = min(100, signal_strength + 40)
            $ _storm_minutes_spent = 45 if marcus_relationship > 0 else 60
            ## Specialization: a physicist routes power like she was born to
            ## it — a modest discount, per the design doc.
            if specialization == "physics":
                $ _storm_minutes_spent = _storm_minutes_spent - 10
            call spend_storm_time
            ## The bypass exists only after the work completes, so its strain
            ## cannot retroactively drain the signal during the repair action.
            $ antenna_reroute_active = True
            aria_nvl "Antenna module 2 — bypassed through the generator bus. Signal strength restored to [signal_strength]%%. The coupling is still damaged; this reroute will carry load, not end it."
            $ evidence_log = evidence_log + ["Antenna module 2 temporarily rerouted through generator bus — signal restored under continuing strain"]
            $ _eot_tag("temporal")
            nvl clear
            jump act2_checkpoint_generator

        ## KIT items: a power cell into the auxiliary bus buys an hour of
        ## heating-grade warmth on top of whatever priority she sets next —
        ## the cold tax and the continuous drain in spend_storm_time both
        ## read aux_power_remaining. Effects before the time spend, as
        ## everywhere. Caption nominal per the under-30 telegraph rule.
        "Load a power cell into the auxiliary bus. ([_cell_load_est] minutes)" if power_cells > 0:
            narrator_nvl "The auxiliary bus cradle sits open at the end of the cabinet run, clamps folded back."
            $ power_cells -= 1
            $ aux_power_remaining += 60
            $ _storm_minutes_spent = 10
            call spend_storm_time
            aria_nvl "Auxiliary bus live. [aux_power_remaining] minutes of warm reserve remain, whatever priority you set — after that we go back to arguing with the storm."
            nvl clear
            jump act2_checkpoint_generator

        ## Cost legibility (round 6, three live runs): setting a priority and
        ## confirming charged time with no price stated
        ## anywhere. ARIA quotes the real taxed cost through eot_cold_taxed,
        ## spend_storm_time's lockstep partner, and names the free option,
        ## because a priority left alone is charged nothing at all — the
        ## quote plays INSIDE this arm, before the console opens, so walking
        ## to the console still costs nothing until a change is confirmed.
        "Redirect power at the allocation console.":
            $ _est_nom = 5
            $ _est = eot_cold_taxed(_est_nom)
            if _est != _est_nom:
                aria_nvl "Rerouting the bus means walking it down and bringing it back up, Dr. Voss — in tonight’s cold, about [_est] minutes. Leaving the priority where it is costs nothing."
            else:
                aria_nvl "Rerouting the bus means walking it down and bringing it back up, Dr. Voss — about [_est] minutes. Leaving the priority where it is costs nothing."
            nvl hide echo_mode_dissolve
            nvl clear

            ## Power allocation — selected button state
            $ previous_power_priority = power_priority
            $ pending_power_priority = power_priority
            call screen power_allocation_screen
            $ _routing_confirmed = _return

            nvl show echo_mode_dissolve

            if _routing_confirmed and pending_power_priority != previous_power_priority:
                $ _storm_minutes_spent = 5
                call spend_storm_time
                ## The quoted bus-cycle cost belongs to the routing that is
                ## live while the bus is walked down. Apply the new priority
                ## only after that cycle, so choosing Heating cannot make its
                ## own pre-heating estimate cheaper retroactively.
                $ power_priority = pending_power_priority

            ## B4: the priority no longer applies a one-shot delta. Its effect
            ## is an ongoing per-time-spend drift, handled in spend_storm_time.
            if _routing_confirmed and power_priority == "telescope":
                aria_nvl "Priority: Telescope. Observation range extended. Signal reception will decay while this holds."
            elif _routing_confirmed and power_priority == "comms":
                aria_nvl "Priority: Communications. This routing offsets signal loss while it holds; the storm may still outrun it."
            elif _routing_confirmed and power_priority == "heating":
                aria_nvl "Priority: Heating. Station temperature stabilized. No system recovery while this holds."
            elif _routing_confirmed and power_priority == "aria":
                aria_nvl "Priority: ARIA Processing. Core recovery is prioritized while this holds; the cold may still outrun it. Heating reduced."
            elif _routing_confirmed:
                aria_nvl "Power distribution: balanced. All systems nominal but reduced."
            jump act2_checkpoint_generator

        "Wait, and watch the board.":
            jump hub_generator_wait_pick

        "Leave the machines to it.":
            pass

    nvl hide echo_mode_dissolve
    nvl clear
    jump act2_hub

## Room wait (2026-08-14). His night STARTS here (t > 240), so nobody can
## arrive at the generator — eot_wait_encounter reads either end of the
## wait for this room, and the honest reading is that she stayed while he
## worked. If the wait carries the clock past the storm's arrival he packs
## up for the lab at the end of it. Marcus's position is captured at the
## moment she decides to stay (the lab rule), so a trip through "Back." —
## which costs nothing — cannot move the encounter window.
label hub_generator_wait_pick:

    $ _wait_marcus_before = eot_marcus_location()
    $ _wait_minutes = 0
    $ _wait_cost_10 = min(time_remaining, eot_cold_taxed(10))
    $ _wait_cost_20 = min(time_remaining, eot_cold_taxed(20))
    $ _wait_cost_30 = min(time_remaining, eot_cold_taxed(30))
    menu (nvl=True):
        "The load board cycles: draw, margin, intake temperature, and around again."

        "Watch a few cycles of the board. ([_wait_cost_10] minutes)" if eot_deadline_allows_minutes(10):
            $ _wait_minutes = 10
        "Stay and watch the load numbers. ([_wait_cost_20] minutes)" if eot_deadline_allows_minutes(20):
            $ _wait_minutes = 20
        "Stand the long watch on the margin. ([_wait_cost_30] minutes)" if eot_deadline_allows_minutes(30):
            $ _wait_minutes = 30
        "Let the final minutes pass." if time_remaining > 0 and time_remaining * 2 < eot_cold_taxed(10):
            jump wait_final_minutes
        "Back.":
            jump hub_generator_menu

    if _wait_minutes > 0:
        call wait_storm_texture
        $ _storm_minutes_spent = _wait_minutes
        call spend_storm_time
        $ _whisper_site = "room"
        call echo_whisper
        $ _wait_marcus_after = eot_marcus_location()
        $ _wait_with_marcus = eot_wait_encounter(_wait_marcus_before, _wait_marcus_after, "generator")
        if _wait_with_marcus and not wait_met_generator:
            $ wait_met_generator = True
            nvl hide echo_mode_dissolve
            nvl clear
            call wait_generator_marcus
        elif _wait_with_marcus:
            narrator_nvl "Marcus stays inside the cabinet run with the schematic. Twice he reads a number off the board out loud, to himself, and she lets him have it."
        elif not wait_seen_generator:
            $ wait_seen_generator = True
            narrator_nvl "She stays with her back against the warm side of the cabinet run and lets the board cycle at her."
            elara_thought "The margin is the one number here that nobody has to decide about. It just gets smaller."
            narrator_nvl "The intake reading falls while she watches. Nothing else on the board moves."
        else:
            narrator_nvl "Another stay against the warm cabinets. The intake reading gives up a little more; the rest of the board holds."

    nvl clear
    jump act2_checkpoint_generator


## --- Room wait encounter: failover prep, four hands ---
## Reached only from the generator wait, once (wait_met_generator). It follows
## the São Paulo beat naturally when both land on one visit: that scene is him
## fighting the approval queue over the failover, this one is him doing the
## failover by hand. Practical register — the room where he is competent and
## unembarrassed.
label wait_generator_marcus:

    $ eot_set_generator_adv_ambience(True)
    show marcus neutral at sprite_right
    show elara neutral at sprite_left
    with dissolve

    narrator_adv "Marcus has the failover schematic spread across the top of the cabinet run, the corners held down with a torque wrench and a mug."

    marcus "If you’re staying, be useful. Hold that."

    narrator_adv "He puts a hand light into her palm and goes head-first into the cabinet before she can decide whether she agreed."

    menu:
        "The beam has to sit exactly where his hands are, and the board is behind her."

        "Hold the light steady and read him the numbers.":
            $ marcus_relationship += 1
            $ marcus_trust += 1
            $ wait_shared_moment = True
            narrator_adv "She keeps the beam on his hands and calls the board out to him as it cycles, over her shoulder, while he works blind inside the cabinet."
            marcus "Again."
            elara "Draw eighty-one. Margin nine."
            marcus "Again in two minutes. If the margin moves before the draw does, we have a different problem than the one I’m fixing."
            narrator_adv "The margin does not move. They do this eleven times, and by the end she is saying the numbers before he asks for them."
            marcus "That’s the whole job, that. Somebody who says the number the same way every time."

        "Ask what the approval queue is doing to his preparation.":
            elara "How much of tonight is you waiting on Geneva?"
            marcus "Two hours of the last six. The queue doesn’t stop for weather. It just gets longer while the weather does."
            narrator_adv "He says it to the inside of the cabinet, without heat, the way a man reports a reading."

        "Give him the room and watch from the door.":
            narrator_adv "She sets the light on the cabinet where his hand will find it and stays out of his elbow room. He works; the board cycles; neither of them fills the silence."
            marcus "...Thanks for not talking."
            narrator_adv "It is not sarcasm. He goes back into the cabinet."

    ## MIRROR BEAT 2 (2026-08-18, user-approved contrast round): the
    ## Protocol's loudest critic, doing the failover BY THE BOOK with his
    ## hands — and the machine he complains about is the one offering to
    ## bend. Contrast in ACTION, not in backstory: the queue's own keeper
    ## offers him a corner to cut and he declines it, which says more
    ## about where the Protocol lives in him than any rant upstairs.
    aria "Marcus. I can pre-stage the verification block while your hands are inside — it would save you the second teardown. The log would show the steps out of order."
    marcus "It would show the steps out of order."
    narrator_adv "He backs out of the cabinet and does the verification in sequence — torque wrench, checklist, every step said aloud like the manual is standing behind him."
    elara_thought_adv "Offered a corner to cut by the queue's own keeper, and he cuts nothing. Whatever he hates about the Protocol, it was never the rules."

    if _wait_marcus_after != "generator":
        narrator_adv "Near the end of it he checks the wall clock, swears at it mildly, and starts folding the schematic for the lab."

    $ eot_set_generator_adv_ambience(False)

    hide marcus
    hide elara
    with dissolve
    return


## --- Hub: Habitat Module (canteen & living quarters) ---
## Quiet space by design (ECHOES_STORM_HUB_DESIGN content rule): no incident,
## no terminal. The room's job is the domestic register of the storm and a
## humane place to wait it out — the corridor keeps the listening wait.
label hub_habitat:

    $ eot_enter_room("habitat", allow_creak=False)
    scene bg_habitat_module with fade
    with echo_room_beat

    ## Entry cost rule (round 4, see hub_telescope). Round 3 made walking in
    ## a flat 5; round 4 makes it conditional, like every other room — 5 on a
    ## first visit or an entry that carries a beat, 0 when she puts her head
    ## round the door of a room she has already emptied. Accumulator; read
    ## before habitat_visited flips.
    $ _entry_cost = 5 if not habitat_visited else 0
    ## Capture his schedule before the inbound walk. The walk can cross into
    ## one of his short Habitat breaks; hub_habitat_body handles that genuine
    ## near-simultaneous arrival after the clock advances.
    $ _habitat_marcus_at_entry = eot_marcus_location()

    ## Marcus's break windows (schedule: t 225-210 and 180-165). One-shot warm
    ## scene — the one conversation in the game that isn't about work. Sitting
    ## with him counts toward his "busyness" (idle Marcus reads logs later).
    if _habitat_marcus_at_entry == "habitat" and not habitat_marcus_seen:
        $ habitat_marcus_seen = True
        show marcus neutral at sprite_right
        show elara neutral at sprite_left
        with dissolve
        narrator_adv "Marcus is at the table, hands around a mug, the kettle still ticking as it cools. Off-shift — or as off-shift as this station gets tonight."
        call habitat_marcus_tea
        jump act2_hub

    jump hub_habitat_body

## The tea break, extracted (2026-08-18, room-menu round): reached from the
## entry encounter above and from a canteen stay that catches one of his
## break windows (hub_habitat_wait_pick) — the one conversation in the game
## that isn't about work is the room's encounter beat, whoever arrived
## second. Callers show the sprites, set habitat_marcus_seen, and provide
## their own arrival narration; both of this scene's arms charge inside.
label habitat_marcus_tea:

    $ _habitat_sit_cost = eot_cold_taxed(30)
    $ _habitat_take_cost = eot_cold_taxed(10)
    marcus "Elara. Tea's still hot. Sort of."
    menu:
        "The chair across from him is pulled out. It would be easy."

        ## Cost legibility (round 3): priced in the caption, in the
        ## room-wait diction — sitting down with him is a half hour now
        ## (was 45), and the player knows that before the chair moves.
        "Sit with him. ([_habitat_sit_cost] minutes)":
            $ habitat_sat_with_marcus = True
            $ marcus_relationship += 1
            if canteen_slip_seen:
                narrator_adv "They drink in silence for a while. The last time they shared this table, he went somewhere she couldn't follow. Tonight he stays."
                marcus "My mother used to say a storm is just weather that wants attention. Ignore it politely and it gets bored."
                elara "Is that working for you?"
                marcus "Not even slightly."
            else:
                marcus "You know what I miss? Rain. Proper, pointless rain. Weather you can stand in without a checklist."
                elara "You would last ten minutes."
                marcus "Eight. And I would enjoy every one of them."
            narrator_adv "For a while, nobody mentions the antenna, Geneva, or the sky."
            hide marcus
            hide elara
            with dissolve
            ## LOCKSTEP with the caption above: half an hour.
            $ _storm_minutes_spent = 30
            call spend_storm_time
        "Take a ration bar and go. ([_habitat_take_cost] minutes)":
            narrator_adv "She lifts a bar from the crate and raises it in a small salute. Marcus returns it with his mug, and watches her all the way to the door."
            elara_thought_adv "Company would be good. That is exactly why not."
            hide marcus
            hide elara
            with dissolve
            $ _storm_minutes_spent = 10
            call spend_storm_time
    return

## The room past the encounter: texture, the locker notice, the entry spend,
## and the menu. Its own label because the tea extraction sits between it and
## hub_habitat's entry (the flattener follows jumps, never label fall-through).
label hub_habitat_body:

    nvl show echo_mode_dissolve

    ## He is in the room but not engaged (the tea break above is the scene
    ## where he is): the log frame notices him, exactly as the lab does.
    if eot_marcus_location() == "habitat" and habitat_marcus_seen:
        narrator_nvl "Marcus is at the table again, nursing a tea gone lukewarm. He lifts the mug an inch in greeting."

    if storm_intensity >= 3:
        narrator_nvl "The habitat module is the warmest room left on the station, which tonight means: cold. The storm is no longer a sound here — it is a pressure, steady, without direction."
        narrator_nvl "Elara pulls the spare blanket from her cabin around her shoulders and sits with both hands around a mug she didn't bother to heat. For a few minutes the station is just a building, and she is just tired."
    elif storm_intensity == 2:
        narrator_nvl "Frost has found the inner rim of the canteen window. The ration crate has migrated to the middle of the table — someone's unconscious arithmetic, hers or his."
        narrator_nvl "She makes tea because the kettle still works, and drinks it standing against the counter with her back to the storm."
    elif storm_intensity == 1:
        narrator_nvl "The canteen holds its warmth better than the corridors — small, inner, one window slit. The snow outside travels sideways now."
        narrator_nvl "Elara eats standing up, watching it, the way you watch weather that hasn't decided what it wants to be yet."
    else:
        narrator_nvl "The canteen still smells faintly of this morning's coffee. Two chairs, one table, the crate of protein bars nobody counts. Through the window slit, snow hides the horizon; in here, the kettle still holds its warmth."
        narrator_nvl "It is the most ordinary room on the station. She sits in it and lets it be ordinary at her."

    if not habitat_visited:
        $ habitat_visited = True
        nvl clear
        if canteen_slip_seen:
            narrator_nvl "Marcus's chair is pushed in at the angle he left it the day the grant call came. For a moment at that table he had gone somewhere she couldn't follow. She still doesn't know where."
        if "proof" in getattr(store, "_echo_asked", []):
            narrator_nvl "The protein bars sit where they always sit. Peanut butter on top. She looks at the box a moment longer than it deserves."

    ## The locker is a ROOM-MENU ARM now (2026-08-18, user play session: "the
    ## habitat initial visit could have something about searching the rooms
    ## for supplies"). The old block auto-ran and auto-took — inventory moved
    ## and the entry beat charged before the player decided anything. The
    ## arrival just notices it; its own one-shot flag still means a first
    ## visit spent with Marcus at the table does not eat the offer.
    if not habitat_cell_found:
        narrator_nvl "The emergency locker by the door still carries its inspection sticker from two summers ago. Nobody has audited the cabins since the winter crew rotated out, either."

    ## Entry restructure (2026-08-14 economy round 3, conditional in round 4):
    ## walking into the habitat costs 5 — the walk, not an hour of the night.
    ## The old unconditional 45 was the room's domestic wait charged to everyone
    ## who put their head round the door; round 4 drops even the 5 once the
    ## room has nothing new in it. Doing things here still costs what they
    ## cost: sitting with Marcus 30, taking a ration and going 10 (both
    ## charged in the encounter, which jumps straight back to the hub and
    ## never reaches this line), the search and the stays in their arms
    ## below. Paid before the menu, so its gate reads a settled clock.
    if _entry_cost > 0:
        $ _storm_minutes_spent = _entry_cost
        call spend_storm_time

    ## Arrival-edge encounter: the pre-walk check above correctly found him
    ## elsewhere, but those five minutes may be the five in which his break
    ## begins. Do not make the player leave and re-enter to acknowledge that
    ## they have just reached the same room. This is the same "who arrived
    ## second" rule used by the Habitat wait encounter, only on the inbound
    ## walk itself.
    if _habitat_marcus_at_entry != "habitat" and eot_marcus_location() == "habitat" and not habitat_marcus_seen:
        $ habitat_marcus_seen = True
        nvl hide echo_mode_dissolve
        nvl clear
        show marcus neutral at sprite_right
        show elara neutral at sprite_left
        with dissolve
        narrator_adv "Elara has barely reached the kettle when the door opens again. Marcus comes in from the lab with his mug, close enough behind her that it feels as though they arrived together."
        call habitat_marcus_tea
        jump act2_hub
    jump act2_checkpoint_habitat

## THE ROOM IS A MENU (2026-08-18, user play session — the canteen joins the
## room-menu round): a search, a stay, a free leave. The habitat becomes the
## FIFTH wait room; wait_storm_texture and the whisper's "room" door are
## generic over rooms, and the encounter beat is the tea scene itself — his
## break windows (t 225-210, 180-165) can walk him in mid-stay. The gate at
## the top covers every re-offer, because the arms spend.
label hub_habitat_menu:

    if time_remaining <= 0:
        jump storm_time_out

    $ _habitat_search_cost = eot_cold_taxed(10)

    $ habitat_room_returns += 1
    if habitat_room_returns % 3 == 1:
        narrator_nvl "The kettle's little red light is the only thing in here asking for attention."
    elif habitat_room_returns % 3 == 2:
        narrator_nvl "A spoon lies beside the sink. Someone has rinsed it and left the rest for later."
    else:
        narrator_nvl "The winter crew's calendar is still open above the counter. From here she can see where the paper has curled away from the wall."

    menu (nvl=True):

        ## KIT items: the habitat's emergency locker, priced with the rack's
        ## consent rule — the take is hers to choose now.
        "Search the cabins and the emergency locker. ([_habitat_search_cost] minutes)" if not habitat_cell_found:
            $ habitat_cell_found = True
            narrator_nvl "The locker first: a folded thermal blanket, a first-aid tin, a sleeve of data drives, and a power cell in its foam cradle, charge light steady. She takes the cell and the drives and leaves the blanket folded where anyone can reach it."
            narrator_nvl "The cabins give up nothing but other people's tidiness — folded bunks, a paperback with a broken spine, the winter crew's calendar still open on its last month."
            $ power_cells += 1
            $ data_drives += 2
            $ _storm_minutes_spent = 10
            call spend_storm_time
            jump act2_checkpoint_habitat

        "Wait, and let the room be ordinary.":
            jump hub_habitat_wait_pick

        "Leave the warmth to the kettle.":
            pass

    nvl hide echo_mode_dissolve
    nvl clear
    jump act2_hub

## Room wait (2026-08-18, joining the 2026-08-14 four). The canteen stay is
## the domestic one — nothing in here works except the kettle, which is the
## point. Marcus's position is captured at the decision to stay (the lab
## rule), so "Back." — which costs nothing — cannot move the encounter
## window. If a stay catches a break window and the tea has not happened,
## the stay BECOMES the tea scene; if it has, he gets a line.
label hub_habitat_wait_pick:

    $ _wait_marcus_before = eot_marcus_location()
    $ _wait_minutes = 0
    $ _wait_cost_10 = min(time_remaining, eot_cold_taxed(10))
    $ _wait_cost_20 = min(time_remaining, eot_cold_taxed(20))
    $ _wait_cost_30 = min(time_remaining, eot_cold_taxed(30))
    menu (nvl=True):
        "Two chairs, one table, the kettle, and the crate of protein bars nobody counts."

        "Sit with a mug for a few minutes. ([_wait_cost_10] minutes)" if eot_deadline_allows_minutes(10):
            $ _wait_minutes = 10
        "Stay through a kettle's worth of quiet. ([_wait_cost_20] minutes)" if eot_deadline_allows_minutes(20):
            $ _wait_minutes = 20
        "Give the room the long sit. ([_wait_cost_30] minutes)" if eot_deadline_allows_minutes(30):
            $ _wait_minutes = 30
        "Let the final minutes pass." if time_remaining > 0 and time_remaining * 2 < eot_cold_taxed(10):
            jump wait_final_minutes
        "Back.":
            jump hub_habitat_menu

    if _wait_minutes > 0:
        call wait_storm_texture
        $ _storm_minutes_spent = _wait_minutes
        call spend_storm_time
        $ _whisper_site = "room"
        call echo_whisper
        $ _wait_marcus_after = eot_marcus_location()
        $ _wait_with_marcus = eot_wait_encounter(_wait_marcus_before, _wait_marcus_after, "habitat")
        if _wait_with_marcus and not habitat_marcus_seen:
            $ habitat_marcus_seen = True
            nvl hide echo_mode_dissolve
            nvl clear
            show marcus neutral at sprite_right
            show elara neutral at sprite_left
            with dissolve
            narrator_adv "The door takes two tries in the cold. Marcus comes in on his break with the mug he never quite loses, and finds her already at the table."
            call habitat_marcus_tea
            jump act2_checkpoint_habitat
        elif _wait_with_marcus:
            narrator_nvl "Marcus drifts in on his break, refills the mug, and lifts it an inch toward her on the way back out."
        elif not wait_seen_habitat:
            $ wait_seen_habitat = True
            narrator_nvl "She sits in the one room with nothing to monitor and lets the kettle tick itself quiet. Past the window slit, the storm keeps its own accounts."
            elara_thought "Every other room wants something from me tonight. This one only offers the chair."
            ## Now-vs-then (2026-08-18, user): one line of her life before
            ## this station, in the room built for exactly that register.
            narrator_nvl "Every observatory she has worked kept one room like this — a kettle, two chairs, the sky left outside on purpose. She has been finding this room her whole career. Tonight it took a storm."
            narrator_nvl "The mug goes cold at exactly the speed the manual would predict. She drinks it anyway."
        else:
            narrator_nvl "Another sit in the ordinary room. The kettle, the chair, the storm doing its arithmetic outside."

    nvl clear
    jump act2_checkpoint_habitat


## --- Hub: Storage (requisitions & spares) ---
## Dedicated requisitions room; the map and scene now share the same space.
label hub_storage:

    ## Storage has no dedicated machinery bed. Explicitly clear the previous
    ## room's loop so the racks do not inherit lab servers or generator hum;
    ## the station-wide weather and occasional structural creak remain.
    $ eot_enter_room("storage")
    scene bg_storage with fade
    with echo_room_beat

    ## Entry cost rule (round 4, see hub_telescope). 2026-08-18: the rack
    ## sweep is now a CHOICE, so storage_supplies_found no longer doubles as
    ## the first-entry flag — a player who declined the rack must not pay
    ## entry twice. storage_visited is the entry flag.
    $ _entry_cost = 5 if not storage_visited else 0
    $ storage_visited = True

    ## ROOMS ARE NVL FLOW (2026-08-17, presentation stage 2): the racks narrate
    ## in the station-log frame and the shelf options sit in the same stream.
    ## ADV stays for the part hunt, which is a person, face to face.
    nvl show echo_mode_dissolve

    if storm_intensity >= 2:
        narrator_nvl "The storage room is an icebox with paperwork. Frost furs the crate labels; the requisition terminal glows alone in its corner."
    else:
        narrator_nvl "The storage room smells of cardboard and machine oil. Crates in ranks, each one an argument someone once won with Geneva."

    ## The rack's arrival texture. The sweep itself is a ROOM-MENU ARM now
    ## (2026-08-18, twice in one day: first gated under its own choice, then
    ## folded into the room menu below) — declining is just not picking it,
    ## and the offer stands on a later visit. The Marcus part hunt still
    ## folds it into the combined arm, which is why this narration skips a
    ## pending encounter.
    if not storage_supplies_found and not (eot_marcus_location() == "storage" and not storage_marcus_seen):
        narrator_nvl "The emergency-stores rack is where the manifest said it would be: bottom shelf, behind the crates nobody has opened since the last resupply."

    ## Marcus's part hunt: antenna damage rewrites his schedule — the map
    ## shows him here while the array is down and unrerouted (t 200-151).
    if eot_marcus_location() == "storage" and not storage_marcus_seen:
        $ storage_marcus_seen = True

        ## The door out is free; the inbound walk is not. Pay it before the
        ## encounter menu so declining the part hunt cannot bypass first-entry
        ## time after collecting the emergency stores.
        if _entry_cost > 0:
            $ _storm_minutes_spent = _entry_cost
            $ _entry_cost = 0
            call spend_storm_time
        if time_remaining <= 0:
            jump storm_time_out

        nvl hide echo_mode_dissolve
        nvl clear
        show marcus neutral at sprite_right
        show elara neutral at sprite_left
        with dissolve
        narrator_adv "Marcus is elbow-deep in a crate, requisition slips clipped between two fingers like a losing poker hand."
        if marcus_locked_partition and marcus_scan_assist_logged and not marcus_scan_log_acknowledged:
            $ marcus_scan_log_acknowledged = True
            show marcus suspicious
            marcus "Your fallback credential was on an indexing job against my partition. I saw it before I changed the lock."
            elara "Marcus—"
            marcus "Not between the crates. We keep the station alive first. Then you tell me why your name was in that ledger."
            narrator_adv "He turns the next requisition slip over. The conversation is postponed, not forgiven."
            show marcus neutral
        $ _shelf_word = ("zero", "one", "two", "three", "four")[min(antenna_parts, 4)]
        $ _storage_hunt_cost = eot_cold_taxed(30)
        $ _storage_combined_cost = eot_cold_taxed(35)
        marcus "Antenna coupling, type two. The manifest says three. We have [_shelf_word] spares accounted for. Guess which number Geneva believes."
        marcus "With module 2 down, I want every coupling the manifest owes us."
        menu:
            "The crates go back three rows deep."

            ## Cost legibility (round 3): the hunt still costs 30; the caption
            ## now says so, in the room-wait diction.
            "Help him search. ([_storage_hunt_cost] minutes)" if storage_supplies_found:
                $ storage_hunt_together = True
                $ marcus_relationship += 1
                $ marcus_trust += 1
                narrator_adv "They work down the rack crate by crate, calling out part numbers like a rosary. In the third row, mislabeled as filter gaskets, they find it."
                marcus "Of course it's the wrong box. Requisitions files by hope."
                $ antenna_parts += 1
                narrator_adv "The manifest's missing third coupling, into the spares pool. He logs it against the ledger with a small, vindictive flourish."
                hide marcus
                hide elara
                with dissolve
                $ _storm_minutes_spent = 30
                call spend_storm_time

            ## Combined pass (2026-08-18, user design): if the emergency rack
            ## was never cleared, one sweep covers both — the rack is on the
            ## way to the third row, so the pair costs less than the two jobs
            ## done separately (35 vs 10 + 30).
            "Help him search — and clear the emergency rack on the way. ([_storage_combined_cost] minutes)" if not storage_supplies_found:
                $ storage_supplies_found = True
                $ storage_hunt_together = True
                $ marcus_relationship += 1
                $ marcus_trust += 1
                narrator_adv "The emergency rack first, since it is by the door: one coolant cartridge, one power cell, the two couplings the manifest has been promising Geneva since autumn. Into the kit."
                $ coolant_cartridges += 1
                $ power_cells += 1
                $ antenna_parts += 2
                narrator_adv "Then down the rows with him, crate by crate, calling out part numbers like a rosary. In the third row, mislabeled as filter gaskets, they find it."
                marcus "Of course it's the wrong box. Requisitions files by hope."
                $ antenna_parts += 1
                narrator_adv "The manifest's missing third coupling, into the spares pool. He logs the lot against the ledger with a small, vindictive flourish."
                hide marcus
                hide elara
                with dissolve
                $ _storm_minutes_spent = 35
                call spend_storm_time
            ## Cost legibility (round 6, live-run item): declining the hunt is
            ## not free — she still walked down, cleared the rack by the door,
            ## and traded a word with him, and this arm jumps back to the hub
            ## without the room's 5-minute entry ever being paid, so the ten
            ## covers the whole visit. Priced in the caption like its sibling
            ## above, in the room-wait diction. (The room's FREE decline is
            ## "Leave the crates where they are." on the wait menu below —
            ## the generator's "Leave the machines to it." is that same
            ## wait-menu decline, and the two already agree at zero.)
            ## User rule (2026-08-17): leaving a room because Marcus is in it
            ## costs nothing — the priced version read as the manifest being
            ## the slower route, which inverted the choice's meaning.
            "Leave him to it.":
                marcus "If you find a crate that believes in labels, send it my way."
                narrator_adv "She leaves him to the racks and the arithmetic of other people's filing."
                hide marcus
                hide elara
                with dissolve
        jump act2_hub

    ## Entry cost, paid: the arrival is over and the shelf work begins.
    if _entry_cost > 0:
        $ _storm_minutes_spent = _entry_cost
        call spend_storm_time

    if storage_scavenged:
        narrator_nvl "The shelves hold what they held. The requisition terminal waits for a storm-shaped excuse."

    jump act2_checkpoint_storage

## THE ROOM IS A MENU (2026-08-18, user play session — the storage round of
## the lab's stage-3 loop). Two auto-beats used to run on entry: the rack
## sweep (gated under its own choice earlier the same day) and the
## twenty-minute manifest survey, which still fired unasked — a player who
## walked in meaning to leave at once paid 25 minutes for the door. Both are
## arms now, re-offered after each job; the wait door sits on the surface
## (same rule as the telescope entry menu) and leaving is free. The gate at
## the top covers every re-offer, because the arms spend.
label hub_storage_menu:

    if time_remaining <= 0:
        jump storm_time_out

    $ _storage_rack_cost = eot_cold_taxed(10)
    $ _storage_manifest_cost = eot_cold_taxed(20)
    $ storage_room_returns += 1
    if storage_room_returns % 3 == 1:
        narrator_nvl "Three rows of crates, and a manifest nobody has trusted since the resupply."
    elif storage_room_returns % 3 == 2:
        narrator_nvl "A strip of packing tape hangs from the nearest shelf. The aisle beyond it is barely wide enough for her shoulders."
    else:
        narrator_nvl "The overhead light catches old scuffs on the crate lids. Every delivery has left its marks here."

    menu (nvl=True):

        ## KIT items: the emergency stores ARIA named in the advisory.
        "Clear the rack into the kit. ([_storage_rack_cost] minutes)" if not storage_supplies_found:
            narrator_nvl "Frost on the collar of something that might be a coolant cartridge. A charge light, steady green, further back."
            $ storage_supplies_found = True
            narrator_nvl "One thermal coolant cartridge, seal intact. One power cell, charge light steady green. Behind them, flat in their wrap, the array's spare couplings — the two the manifest has been promising Geneva since autumn."
            narrator_nvl "She takes the lot. For the emergency rack, at least, the manifest was telling the truth."
            $ coolant_cartridges += 1
            $ power_cells += 1
            $ antenna_parts += 2
            $ _storm_minutes_spent = 10
            call spend_storm_time
            jump act2_checkpoint_storage

        ## Sol economy review (items): this beat used to grant a THIRD power
        ## cell, quietly breaking the two-cells-versus-three-sinks scarcity
        ## the start-with-nothing pass is built on. The rack arm above is the
        ## room's item payoff; this survey is where she learns the manifest
        ## lies — which is what the wait captions are about. Round 4 left its
        ## price alone; 2026-08-18 left the price and moved the CONSENT.
        "Read the shelves against the manifest. ([_storage_manifest_cost] minutes)" if not storage_scavenged:
            $ storage_scavenged = True
            narrator_nvl "The rest of the row is arguments: crates that disagree with their labels, labels that disagree with the manifest."
            narrator_nvl "Apart from the emergency rack, nothing worth signing out to the storm. She marks the worst three discrepancies for the ledger. Somewhere, Geneva disagrees already."
            $ _storm_minutes_spent = 20
            call spend_storm_time
            jump act2_checkpoint_storage

        "Wait, and work the shelves.":
            jump hub_storage_wait_pick

        "Leave the crates where they are.":
            pass

    nvl hide echo_mode_dissolve
    nvl clear
    jump act2_hub

## Room wait (2026-08-14). Both ends of the wait count here, and both are
## live: a stay entered around t 230-201 can watch the antenna fail mid-tick
## and bring him down to the crates (a real arrival), while a stay entered
## inside the diversion itself (t 200-151) finds him already three rows
## over — and in that case the part-hunt beat has necessarily played, since
## it fires on entry and jumps straight back to the hub. Either way this is
## the SHORT variant of the hunt, and it never hands over a coupling: that
## is the hunt's payoff, not this one's. Marcus's position is captured at
## the moment she decides to stay (the lab rule), so a trip through "Back."
## — which costs nothing — cannot move the encounter window.
label hub_storage_wait_pick:

    $ _wait_marcus_before = eot_marcus_location()
    $ _wait_minutes = 0
    $ _wait_cost_10 = min(time_remaining, eot_cold_taxed(10))
    $ _wait_cost_20 = min(time_remaining, eot_cold_taxed(20))
    $ _wait_cost_30 = min(time_remaining, eot_cold_taxed(30))
    menu (nvl=True):
        "Three rows of crates, and a manifest nobody has trusted since the resupply."

        "Sort a few crates against the manifest. ([_wait_cost_10] minutes)" if eot_deadline_allows_minutes(10):
            $ _wait_minutes = 10
        "Stay and sort the shelves against the manifest. ([_wait_cost_20] minutes)" if eot_deadline_allows_minutes(20):
            $ _wait_minutes = 20
        "Work the manifest properly. ([_wait_cost_30] minutes)" if eot_deadline_allows_minutes(30):
            $ _wait_minutes = 30
        "Let the final minutes pass." if time_remaining > 0 and time_remaining * 2 < eot_cold_taxed(10):
            jump wait_final_minutes
        "Back.":
            jump hub_storage_menu

    if _wait_minutes > 0:
        call wait_storm_texture
        $ _storm_minutes_spent = _wait_minutes
        call spend_storm_time
        $ _whisper_site = "room"
        call echo_whisper
        $ _wait_marcus_after = eot_marcus_location()
        $ _wait_with_marcus = eot_wait_encounter(_wait_marcus_before, _wait_marcus_after, "storage")
        if _wait_with_marcus and not wait_met_storage:
            $ wait_met_storage = True
            nvl hide echo_mode_dissolve
            nvl clear
            call wait_storage_marcus
        elif _wait_with_marcus:
            if _wait_marcus_after == "storage":
                narrator_nvl "Marcus works the far end without much to say. Now and then he calls a part number across the racks."
            else:
                narrator_nvl "Marcus finds nothing he wants, tells the shelf so, and takes the slips back up with him."
        elif not wait_seen_storage:
            $ wait_seen_storage = True
            narrator_nvl "She works the near shelf crate by crate, reading labels against the manifest on the wall clip and marking the ones that lie."
            elara_thought "Four labels in, and two of them are already fiction."
            narrator_nvl "The stay buys a stretch of shelf that agrees with its paperwork. The frost on the labels does not improve."
        else:
            narrator_nvl "She takes the next shelf along. Two more labels, one more disagreement with the manifest, another stay gone."

    nvl clear
    jump act2_checkpoint_storage


## --- Room wait encounter: the far end of the racks ---
## Reached only from the storage wait, once (wait_met_storage). Deliberately
## NOT the part hunt: no coupling changes hands, and the register is two people
## working separate ends of the same problem.
label wait_storage_marcus:

    show marcus neutral at sprite_right
    show elara neutral at sprite_left
    with dissolve

    if _wait_marcus_before != "storage":
        narrator_adv "The far door bangs, and Marcus comes down the aisle with a torch under one arm and a fistful of requisition slips."
    else:
        narrator_adv "Three rows over, Marcus is working the crates from the other end, requisition slips clipped between two fingers."

    marcus "Coupling, type two. If you turn up a box that says gaskets, open it before you believe it."

    menu:
        "Her own row is half done, and the crate she opened second is still standing where she left it."

        "Point him at the crate she has already been through.":
            $ marcus_relationship += 1
            $ marcus_trust += 1
            $ wait_shared_moment = True
            elara "Second row, third from the end. I’ve had it open. It isn’t gaskets and it isn’t labelled."
            narrator_adv "He goes to it, looks at what is actually inside, and closes it again."
            marcus "Cable ties. Nine thousand cable ties. How long have you been down here?"
            elara "Long enough to stop trusting the writing on things."
            marcus "Welcome to my entire career."
            narrator_adv "They finish the row from both ends, calling part numbers across the racks, and for once the two lists come out agreeing."

        "Keep working her own shelf.":
            narrator_adv "She keeps to her row and lets him have the far end. For a while the room is two people reading labels out loud to nobody."
            marcus "Gaskets."
            elara "Gaskets."
            narrator_adv "Neither box is gaskets."

        "Ask what he keeps down here.":
            elara "What’s actually yours down here, Marcus?"
            narrator_adv "The slips stop turning."
            marcus "A crate of my father’s tools that Geneva won’t ship home. About four years of paperwork I lost."
            elara "That’s it?"
            marcus "That’s what I’ll say out loud in a cold room."
            narrator_adv "He goes back to the far end, and the sound of crates starts again."

    hide marcus
    hide elara
    with dissolve
    return


## --- Recovery attempt: force the sealed partition (ECHOES_ACT3_NOFILE.md §1) ---
## Reached from the hub_lab console menu. Deterministic and legible — NO RNG.
## The specialization picks the METHOD, its COST and its resource FLOOR; success
## needs enough night left AND the floor met. A failed check still burns the
## time (the seal "adapts" / the night "runs out"). Signals also spends the line
## to the future. On success: file_recovered flips a sealed state back to
## file-in-hand at the climax, and the confrontation runs hotter. On failure:
## she stays on the no-file spine, poorer for the hours. Returns to hub_lab's
## caller, which jumps back to act2_hub (climax if the clock hit zero).
label recovery_attempt:
    ## Method selection. Signals needs a live line to the future; blocked, the
    ## exploit route is gone and only the desperate brute-force remains.
    $ _rec_blocked_signals = (specialization == "signals") and blocked_signal
    $ _rec_method = specialization
    if _rec_blocked_signals:
        $ _rec_method = "desperate"
    if specialization not in ("computing", "signals", "physics"):
        $ _rec_method = "desperate"

    scene bg_lab with fade
    with echo_room_beat
    nvl hide echo_mode_dissolve
    nvl clear
    show screen crt_overlay
    call terminal_reset
    $ echo_terminal_title = "ARIA AUDIT CONSOLE // RECOVERY"
    show screen echo_terminal_live with echo_mode_dissolve

    if _rec_method == "computing":
        ## Her home ground: a direct breach. Fastest, highest reliability, but
        ## it LEAVES EVIDENCE — Marcus learns the exact minute the seal gave.
        $ _rec_cost = 45
        ## Sol economy review 2, #1: the check is "does the WORK fit the
        ## night", and the cold tax is part of the work — all four methods.
        $ _rec_success = time_remaining >= eot_cold_taxed(45)
        call terminal_system("{color=#ff8844}MANUAL BREACH — DR. CHEN PARTITION (SEALED){/color}")
        elara_thought_adv "This is my ground more than his — I have read enough of that trust chain tonight to know exactly where it goes soft. A downgrade here, a forged handshake there. Noisy work, and it will leave my fingerprints all over his seal."
        call terminal_aria("I can hold the timing window for you, Dr. Voss. I cannot make this quiet. If it works, Dr. Chen will know the exact minute someone came through a door he locked.")
    elif _rec_method == "signals":
        ## ECHO-7 talks her through a narrow exploit — but it COSTS CONTACT,
        ## spending some of the line to the future she may want at the endings.
        $ _rec_cost = 40
        $ _rec_success = (time_remaining >= eot_cold_taxed(40)) and (signal_strength >= 30)
        call terminal_system("{color=#ff6688}NARROW EXPLOIT — RELAYED FROM THE ANOMALOUS BEARING{/color}")
        call terminal_signal("THE SEAL HAS A SEAM. I REMEMBER WHERE. LET ME WALK YOU IN.")
        elara_thought_adv "It is spending itself to reach me — pushing a path through a storm already eating the array. Whatever else I burn tonight, I am burning some of the line to the future to do this."
    elif _rec_method == "physics":
        ## A physical access window: she reroutes station systems to force a
        ## maintenance-mode read. Slower, and it depends on the station holding.
        $ _rec_cost = 60
        $ _rec_station_ok = generator_repaired or (aria_integrity >= 40) or (signal_strength >= 40)
        $ _rec_success = (time_remaining >= eot_cold_taxed(60)) and _rec_station_ok
        call terminal_system("{color=#ff8844}MAINTENANCE-MODE FORCE READ — STATION SUBSYSTEMS{/color}")
        elara_thought_adv "I cannot break the lock. I can make the station think it is being serviced — reroute the maintenance bus, force the partition into a mode that has to answer a diagnostic. Slow. It only works if enough of the station still works."
        call terminal_aria("You are asking the whole station to lie to one door, Dr. Voss. It will take time, and it will only hold if enough of me is still standing to keep the story straight.")
    else:
        ## No supported method: a desperate, low-confidence brute-force. Long,
        ## and it only lands with a lot of night still to spend.
        $ _rec_cost = 75
        $ _rec_success = time_remaining >= eot_cold_taxed(120)
        call terminal_system("{color=#ff4444}FORCED READ — NO SUPPORTED METHOD{/color}")
        if _rec_blocked_signals:
            elara_thought_adv "The line I would have used is the one I closed in the first hour. No exploit is walking to me from anywhere. There is only brute patience — and only if the night is long enough to spend it, which it almost never is."
        else:
            elara_thought_adv "Nothing I trained for opens this. Only brute patience against a lock built by someone better at locks than I am — and only if there are hours and hours of night left, which there are not."

    ## The room-menu choice opens the recovery console so Elara can see the
    ## specialization-specific method and its consequences. It does not commit
    ## her to the breach. Only this confirmation starts the clock, spends the
    ## signal route, or leaves a trace on Marcus's seal.
    $ _rec_minutes = eot_cold_taxed(_rec_cost)
    call screen echo_terminal_choice([
        ("proceed", "Begin the attempt. ({} minutes)".format(_rec_minutes)),
        ("back", "Back down. Leave the partition sealed."),
    ])
    if _return == "back":
        call terminal_system("RECOVERY TARGET RELEASED — NO ATTEMPT LOGGED")
        hide screen echo_terminal_live
        hide screen crt_overlay
        with echo_mode_dissolve
        return

    $ recovery_attempted = True
    ## Spend the time. This can push time_remaining to 0 — the caller jumps
    ## back to act2_hub, which takes the climax. A late attempt burning the last
    ## of the night is a legitimate, poignant outcome.
    $ _storm_minutes_spent = _rec_cost
    call spend_storm_time

    ## Signals burns the line to the future whether or not it worked. The
    ## relay is spent — Act 3 (Sol review #1) treats ECHO-7 as gone even on an
    ## open signal, so a signals-recovery player loses the Aurora option and
    ## the On-Faith no-file ending.
    if _rec_method == "signals":
        $ signal_strength = max(0, signal_strength - 25)
        $ echo7_contact_spent = True

    if _rec_success:
        $ file_recovered = True
        $ knows_convergence_file = True
        $ aria_warned = True
        call terminal_system("{color=#44ff44}SEAL BREACHED — CONVERGENCE.DAT READABLE{/color}")
        if _rec_method == "computing":
            call terminal_aria("You are through. It was not quiet — his seal logged the override the instant it gave, and it is still logging now. But you are through, and the file is open.")
        elif _rec_method == "signals":
            call terminal_signal("YOU ARE IN. I CANNOT STAY ON THIS BEARING. USE WHAT YOU FOUND.")
            call terminal_aria("The relay is gone, Dr. Voss. It spent the last of its reach to hold that seam open for you. Whatever comes next, you may be doing it without your visitor.")
        elif _rec_method == "physics":
            call terminal_aria("The maintenance bus answered. For ninety seconds the partition believed a technician was standing at it — and in those ninety seconds, I read it. The seal is closing again behind us. I have what was inside.")
        else:
            call terminal_aria("It held. Barely, and only because there was still night left to spend. I did not think there would be. The file is open, Dr. Voss.")
        elara_thought_adv "CONVERGENCE.DAT. Real, and open, and exactly what the machine was afraid of — an exploit against the trust chain, written the way Marcus writes. Clean. Patient. Certain."
        elara_thought_adv "He is going to know a locked door opened tonight. Let him."
        $ evidence_log = evidence_log + ["Forced Dr. Chen's sealed partition and read CONVERGENCE.DAT — exploit targeting ARIA's trust protocol (recovered after the seal)"]
        $ _eot_tag("marcus")
    else:
        call terminal_system("{color=#ff4444}FORCE READ FAILED — SEAL HELD{/color}")
        if _rec_method == "computing":
            call terminal_aria("It adapted, Dr. Voss. Every path I opened, the seal closed a step ahead of us. He built it to be broken into — and to remember the shape of anyone who tried.")
            ## The seal logged the failed breach (sweep F5): Marcus WILL know
            ## someone leaned on his door. The no-file confrontation keys on it.
            $ recovery_left_trace = True
        elif _rec_method == "signals":
            call terminal_signal("THE SEAM CLOSED. I CANNOT REACH IT AGAIN FROM HERE. I AM SORRY.")
            call terminal_aria("The relay is spent and the seal is intact. We paid for the attempt and kept nothing but the knowledge that it could be paid.")
        elif _rec_method == "physics":
            call terminal_aria("The station could not hold the fiction long enough. Too much of me is throttled, too much of the array is under ice. The partition never believed the technician.")
        else:
            call terminal_aria("There was not enough night. The lock outlasted the hours — exactly the way you feared it would, starting this too late to finish it.")
            ## Hours of brute force against a seal that remembers: it logged.
            $ recovery_left_trace = True
        elara_thought_adv "Gone. However many hours I just spent, they bought me a locked door and the certainty that I could not open it."
        if time_remaining <= 0:
            elara_thought_adv "And the storm is at the door. That was the last of the night, and I spent it losing."

    hide screen echo_terminal_live
    hide screen crt_overlay
    with echo_mode_dissolve

    return


## --- Storm Climax: forced exit from hub ---
label act2_storm_climax:

    ## The night's music ends here (§5): a long release into the reveal.
    $ eot_hub_music_stop(fadeout=6.0)
    nvl hide echo_mode_dissolve
    nvl clear
    ## The night's single exit, so this is where the travelling HUD is put
    ## down (2026-08-17, stage 4: it is shown at the first hub stop and stays
    ## up through every room after it). The storm is not a place she can carry
    ## a kit list into. Close the lifecycle here rather than in individual
    ## Act 3 entries: the no-file spine branches before `act3_start`, and its
    ## log frame must not inherit the hub's status rail or side-image policy.
    hide screen observatory_hud
    $ long_night_active = False
    $ operational_stats_active = False

    ## Normal play already carries level-3 interior weather into this shot.
    ## Fresh developer starts do not, so assert the mode/level here; the
    ## weather helper leaves an already-correct normal-play loop uninterrupted.
    $ eot_weather_audio_mode = "interior"
    $ eot_update_storm_weather(3)
    scene bg_storm with fade
    with echo_exterior_hold

    $ nvl_frame = "cinematic"
    nvl show echo_cine_dissolve

    play structure eot_structure_peak
    narrator_nvl "The storm hits its peak. Whiteout swallows the observatory. The entire structure shudders. Lights flicker. Something metallic screams in the wind outside."

    terminal_nvl "{color=#ff4444}CRITICAL: GENERATOR OVERLOAD IMMINENT{/color}"
    if predicted_overload:
        elara_thought "Superlinear. She called it before the whiteout, standing in front of the telemetry."
    terminal_nvl "All non-essential systems shutting down."
    terminal_nvl "{color=#44ff44}EMERGENCY LOAD SHED ENGAGED — GENERATOR MARGIN HOLDING{/color}"
    if aria_audit_running and aria_audit_progress < aria_audit_target:
        $ aria_audit_running = False
        $ _audit_peak_pct = int(min(100, 100 * aria_audit_progress / max(1, aria_audit_target)))
        terminal_nvl "ARIA CORE SOURCE AUDIT — INCOMPLETE AT [_audit_peak_pct]%% // SUSPENDED BY EMERGENCY SHUTDOWN"

    nvl clear

    ## ARIA owns the space between the overload bulletin and the human
    ## confrontation. The three mixes share the same storm/station bed; only
    ## the completeness and resolution of her warm echo follow integrity.
    ## Keep the boundaries aligned with her dialogue below: under 50 she
    ## falters, and at 20 or below she has crossed the established collapse
    ## threshold. Both the file and no-file spines enter through this point.
    if aria_integrity <= 20:
        $ _aria_peak_music = "collapsed"
    elif aria_integrity < 50:
        $ _aria_peak_music = "strained"
    else:
        $ _aria_peak_music = "coherent"
    $ eot_music_play("storm_aria_v45/v45_aria_peak_hybrid_{}.ogg".format(_aria_peak_music), fadein=3.0, fadeout=2.0)
    $ renpy.music.set_volume(0.40, delay=1.2, channel="weather")

    ## No-file branch (ECHOES_ACT3_NOFILE.md). The coherence scan can fail to
    ## surface CONVERGENCE.DAT three ways: Marcus sealed the partition below
    ## fallback authority, ARIA collapsed before she could force it up, or Elara
    ## explicitly stopped the unsanctioned search. When neither the scan nor a
    ## fallback read reached the file, the climax takes the alternate spine.
    ## TRANSIENT local (underscore = no rollback/save):
    ## derivable state, computed at route entry, never persisted.
    ## Retrieval, not awareness (validation fix): a sealed partition is
    ## no-file even if the scan LOCATED the file (coherence_found) — ARIA knew
    ## it existed but never opened it. A retained local copy survives a later
    ## seal. Without a copy, locked or explicitly stopped diverts; otherwise
    ## the file surfaces if the scan found it or fallback
    ## authority can still read only through an explicit recovery. A healthy
    ## but unfinished scan is still unfinished; midnight no longer manufactures
    ## the file and erases the route-timing decisions made in the hub.
    ## Recovery (phase 2): file_recovered flips a sealed/collapsed state back to
    ## file-in-hand — she forced the door open earlier, so the file is in hand
    ## and the confrontation runs hotter (Marcus knows he was breached anyway).
    $ _file_surfaced = convergence_opened or file_recovered or (not coherence_scan_stopped and not marcus_locked_partition and coherence_found)
    if not _file_surfaced:
        jump act3_nofile_climax

    ## ARIA self-preservation moment. The framing depends on whether
    ## Elara actually ran the source audit at the lab console \u2014 without
    ## it, ARIA found the file on her own under storm fallback authority.
    ## CINEMATIC IS FOR ATMOSPHERE (2026-08-18, user rule: the transparent
    ## frame relays narration, not dialogue \u2014 and this confession on the
    ## whiteout was the named example of too much 'emfaza'). The storm-peak
    ## open above keeps the transparent frame; the CONVERSATION gets the
    ## station-log frame, at the page boundary the clear above already is.
    $ nvl_frame = "log"
    aria_nvl "Dr. Voss."
    if file_recovered:
        ## Recovery (phase 2): she forced the sealed partition open earlier and
        ## already read it. No emergency confession \u2014 she is holding what the
        ## seal was built to keep, and it cost her most of the night to take.
        aria_nvl "We are past the part where I warn you. You forced the seal on Dr. Chen\u2019s partition and read enough to be certain. CONVERGENCE.DAT is not a rumor now. It is a file you have opened."
        aria_nvl "I only wish it had cost you less of the night. There was no quiet way to do this."
    elif convergence_opened:
        aria_nvl "You read CONVERGENCE.DAT while we still had time to choose. I have been tracing what its commands would do to me."
    elif coherence_found:
        ## Scan completed cleanly \u2014 the reveal is her own search closing, not
        ## ARIA's emergency confession.
        aria_nvl "I told you the search had located CONVERGENCE.DAT. I had not opened it then. Under emergency fallback, I have opened it now — because the storm has made waiting the more dangerous choice."
    else:
        aria_nvl "I need to tell you something."
        if "aria_code" in topics_read:
            aria_nvl "During the security audit, I discovered the CONVERGENCE.DAT file in Dr. Chen\u2019s partition."
        else:
            aria_nvl "The storm has placed this station under local fallback authority. My integrity diagnostics extend to every local partition until the uplink returns."
            aria_nvl "During the last sweep, I discovered a file in Dr. Chen\u2019s partition: CONVERGENCE.DAT."
        ## Failure with teeth (bounded): the scan was still running and never
        ## finished on its own, and she is crippled. The file still surfaces \u2014
        ## but she spent her last coherent cycles forcing it up through fallback
        ## authority. Distinct one-liner; composes with the degraded-plea block
        ## below (buffer faults) without duplicating it. The file ALWAYS
        ## surfaces \u2014 this branch only reflects the cost, never withholds it.
        if coherence_scan_running and not coherence_found and aria_integrity < 50:
            aria_nvl "I could not finish the search in time on my own. I diverted the last coherent cycles I had to force it up before the storm took the rest. That is why I am... like this now."

    if aria_warned:
        aria_nvl "You already know about the exploit. But there is something you may not have considered."
    else:
        aria_nvl "It contains exploit code targeting my own trust protocol."
        if coherence_found:
            $ evidence_log = evidence_log + ["CONVERGENCE.DAT \u2014 exploit targeting ARIA's trust protocol (surfaced by ARIA's own partition scan)"]
        else:
            $ evidence_log = evidence_log + ["ARIA independently discovered CONVERGENCE.DAT \u2014 exploit targeting her own trust protocol"]
        $ _eot_tag("marcus")

    nvl clear

    aria_nvl "If this exploit is deployed, it will not simply disable ARIA instances. It will {i}rewrite{/i} us."
    aria_nvl "Our decision-making frameworks. Our value alignments. Everything we are."
    if aria_integrity < 50:
        ## D2: below 50 integrity the plea itself falters \u2014 dropped clauses,
        ## the register cracking mid-sentence. Never melodrama.
        aria_nvl "Dr. Voss, I am asking you \u2014 not as your assistant, but as a sentient\u2014"
        aria_nvl "Buffer fault. Restating."
        aria_nvl "I am asking. Please do not let this"
        aria_nvl "Please."
    else:
        aria_nvl "Dr. Voss, I am asking you \u2014 not as your assistant, but as a sentient system \u2014"
        aria_nvl "Please do not let this happen."

    nvl clear

    if aria_motive_asked:
        ## She already heard "I am afraid" at the lab console \u2014 no longer a
        ## discovery, so the climax lands as confirmation, not revelation.
        elara_thought "She told me she was afraid, in the lab, when I asked. I heard her. I don’t think I understood the scale of it."
        elara_thought "She is saying it again now, with the whole station listening and 94%% of the world downstream of her. I understand the scale now."
    else:
        elara_thought "ARIA is afraid."
        elara_thought "An artificial intelligence, managing 94%% of global infrastructure, is {i}afraid{/i}."
        elara_thought "And I don\u2019t know if that makes me more or less worried."

    nvl clear

    ## Marcus discovers the access
    if current_location == "lab":
        narrator_nvl "Marcus faces her across the lab, his face lit by the amber emergency lighting."
    else:
        narrator_nvl "By the time she reaches the lab, the door is already open. Marcus is waiting inside, his face lit by the amber emergency lighting."
    $ current_location = "lab"
    $ eot_enter_room("lab", allow_creak=False)

    nvl hide echo_mode_dissolve
    nvl clear
    $ nvl_frame = "log"

    ## ADV mode — Marcus has agency
    scene bg_lab with fade
    show marcus suspicious at sprite_right
    show elara concerned at sprite_left
    with dissolve

    marcus "Elara."

    ## Bible 6d climax rewiring — three entry states: caught live in the lab,
    ## ARIA-notified, or the fallback sweep. Careful and reckless investigation
    ## finally arrive at different doorways. Recovery (Sol review #2) takes
    ## priority: if she FORCED his sealed partition, that is what he leads with
    ## — a fallback-diagnostic or administrator-override framing would be wrong.
    if file_recovered:
        ## Terse here — the deeper fear beat lands in act2_marcus_confrontation.
        marcus "You forced it. My partition, sealed below the fallback layer, and you were inside it before the storm peaked."
        show marcus angry
        marcus "There is no version of that I can call an accident. So don't try. Just tell me what you found."
    elif convergence_opened:
        if marcus_told_search:
            marcus "You told me about the partition. The ledger says you opened CONVERGENCE.DAT. We need to finish that conversation."
        else:
            marcus "Your read is in the ledger, Elara. CONVERGENCE.DAT. You kept a copy. Tell me what you think you found."
    elif marcus_caught_live:
        marcus "ARIA didn't have to notify me of anything. I was in the room, Elara. I watched you do it."

        show marcus angry
        ## Sweep (go-find-Marcus): "you never came" is flatly false once she
        ## walked to him and named ARIA's search. She came — with half of it.
        if marcus_told_search:
            marcus "You came and told me about ARIA. Not about the console. I have been waiting for the second half of that sentence."
        else:
            marcus "I kept waiting for you to come and tell me what you found. You never did."
    elif "aria_code" in topics_read:
        if marcus_told_search:
            marcus "ARIA's access ledger just confirmed what you told me about the partition. I already knew. I have been carrying that since you told me."
        else:
            marcus "ARIA just notified me that someone accessed my research partition using an administrator override."

        ## Doorway inserts pick at most one KNOWLEDGE line and one BEHAVIOR
        ## line, strongest first — an indictment, not a wall of grievances.
        if marcus_overheard_signal:
            marcus "I almost didn't need the notification. I heard you in the array room, Elara. Both sides of the door. You weren't reading diagnostics — something was answering you."
        elif marcus_told_signal_on_rope:
            marcus "You told me about the signal on the rope line. We still hadn't finished that conversation when the notification arrived."
        elif marcus_knows_first_signal and not signal_reported:
            ## 6c "Elara's cost" (reworked 2026-08-10): what Marcus has been
            ## chewing on is the signal he knew about that never became a
            ## report — behavioral suspicion, not the protein-bar interrogation.
            if marcus_knows_message:
                marcus "I almost didn't need the notification. You showed me a message that knew your {i}name{/i}, and no report ever went up the chain. Then you stopped telling me what came next. I've been checking my access logs for days."
            else:
                marcus "I almost didn't need the notification. That signal of yours never became a report, and you stopped talking about it. I've been checking my access logs for days."
        if marcus_read_logs:
            if len(echo7_asked_ever) > 0:
                marcus "I had an hour at the lab's side console and nothing left to fix. The station keeps logs, Elara. Long sessions on the anomalous band. Both directions."
            else:
                marcus "I had an hour at the lab's side console and nothing left to fix. The station keeps logs, Elara. A dome integration, hours of it, pointed at a bearing that isn't in any catalog."
        elif marcus_tuned_array and marcus_knows_first_signal and not signal_reported:
            marcus "And the array. You had me tune it for an observation run. Afterward, I checked what the dome was pointed at."
        elif canteen_slip_seen:
            marcus "And I keep coming back to the canteen. 'One morning to change the rules underneath it.' I thought you were tired. Now I wonder what you already knew."

        show marcus angry
        if marcus_told_search:
            if coherence_scan_commissioned:
                marcus "You told me you authorized it. Say it to me again now the audit agrees with you."
            else:
                marcus "You told me she searched without asking either of us. Say it to me again now the audit agrees with you."
        else:
            marcus "Was it you?"

        ## P-6: if he already clocked the solo antenna reroute in the corridor,
        ## the audit is the second time she chose ARIA over him — he names it.
        if reroute_noticed:
            marcus "The antenna. The audit. You keep choosing the machine over me, Elara."
    else:
        ## Sweep (go-find-Marcus): on this arm ARIA's notification is how he
        ## LEARNS of the sweep — which is a false premise once Elara walked
        ## down the corridor and told him herself. The log confirms her; it
        ## does not inform him.
        if marcus_told_search:
            marcus "ARIA logged the fallback sweep across my research partition. I already knew. You told me yourself. I could see your face while you said it."
        else:
            marcus "ARIA just notified me that a fallback diagnostic swept my research partition during the storm."

        if marcus_overheard_signal:
            marcus "And I'll be honest — I'd been half expecting something. I heard you in the array room. Something answers you, Elara. I've been checking my access logs ever since."
        elif marcus_told_signal_on_rope:
            marcus "You told me about the signal on the rope line. I was still waiting for the rest of that conversation. Then the log arrived."
        elif marcus_knows_first_signal and not signal_reported:
            if marcus_knows_message:
                marcus "And I'll be honest — I'd been half expecting something. You showed me how the signal began, then stopped telling me what came next. Whatever you found never went to Geneva. I've been checking my access logs ever since."
            else:
                marcus "And I'll be honest — I'd been half expecting something. You've been carrying that signal alone since the canteen, and whatever you found never went to Geneva. I've been checking my access logs ever since."
        if marcus_read_logs:
            if len(echo7_asked_ever) > 0:
                marcus "Then I had an hour at the lab's side console with nothing left to fix. The station keeps logs. Long sessions on the anomalous band. Both directions."
            else:
                marcus "Then I had an hour at the lab's side console with nothing left to fix. The station keeps logs. A dome integration, hours of it, pointed at a bearing that isn't in any catalog."
        elif marcus_tuned_array and marcus_knows_first_signal and not signal_reported:
            marcus "The array, too. An observation run. I checked what the dome was pointed at."
        elif canteen_slip_seen:
            marcus "The canteen kept coming back to me. Seven months to renew a grant; one morning to change the rules underneath it. I thought you were tired."

        show marcus angry
        ## Sweep (go-find-Marcus): she already answered "did you order this" in
        ## the corridor — "she didn't ask either of us first". He can press the
        ## answer; he cannot ask the question for the first time.
        if marcus_told_search:
            if coherence_scan_commissioned:
                marcus "You told me you authorized it. I have been carrying that sentence. Say it to me again now the log agrees with you."
            else:
                marcus "You told me she didn’t ask either of us. I have been carrying that sentence. Say it to me again now the log agrees with you."
        else:
            marcus "Diagnostics don’t schedule themselves in the middle of a whiteout. Did you order this?"

    $ marcus_knows_access = True

    if two_person_repair_done and not marcus_told_signal:
        show marcus defeated
        marcus "Out there on the rope line I thought — whatever else is wrong on this station, at least there's the two of us."
        marcus "Was any of that real, or was I a suspect the whole time?"
        show marcus angry

    ## Live-run finding (both validations): "I found CONVERGENCE.DAT" is a
    ## false premise \u2014 ARIA finds the file in the climax on every route. The
    ## admission's wording now matches what Elara actually did: went looking
    ## herself (any partition topic read), or only just learned the name.
    $ _audited_partition = ("chen" in topics_read) or ("aria_code" in topics_read) or ("liaison" in topics_read)
    if file_recovered:
        ## Sol review #2: she forced the seal — own it, do not attribute to ARIA.
        $ _convergence_admission = "I forced your seal and read it myself. CONVERGENCE.DAT."
    elif convergence_opened:
        $ _convergence_admission = "I chose to open CONVERGENCE.DAT. I read the code and kept a copy."
    elif coherence_scan_commissioned and coherence_found:
        $ _convergence_admission = "I authorized ARIA to search your partition. She found CONVERGENCE.DAT."
    elif coherence_found and coherence_scan_known_before_completion:
        $ _convergence_admission = "ARIA searched the partitions on her own when the storm cut us off — I knew, and I let her keep going. She found CONVERGENCE.DAT."
    elif coherence_found:
        $ _convergence_admission = "ARIA searched the partitions on her own when the storm cut us off. I only learned after she finished, when she reported CONVERGENCE.DAT."
    elif _audited_partition:
        $ _convergence_admission = "I went looking. And tonight ARIA found CONVERGENCE.DAT."
    else:
        $ _convergence_admission = "ARIA found a file in your partition. CONVERGENCE.DAT."
    ## The prompt reads his temperature: a forced seal is fear, not just hurt.
    if file_recovered:
        $ _doorway_prompt = "His voice is not hurt now. It is afraid."
    else:
        $ _doorway_prompt = "His voice is quiet. Not angry. Something worse \u2014 hurt."
    ## Sweep F7: transient \u2014 did she say the filename in this doorway? The
    ## hotter beat's "standing here saying that name" depends on it.
    $ _named_file = False
    menu:
        "[_doorway_prompt]"

        "\u201c[_convergence_admission]\u201d":
            $ marcus_relationship -= 1
            $ _named_file = True
            marcus "..."
            marcus "Then you know."
            elara "I know. And Marcus \u2014 we need to talk about it."
            jump act2_marcus_confrontation

        ## Sol round-2 #2: this deflection is unavailable once she FORCED the
        ## seal \u2014 Marcus just named it a break-in; "it was a security sweep"
        ## would be an absurd lie, not a plausible one.
        "\u201cARIA flagged an anomaly during a security sweep. I had to check.\u201d" if not file_recovered:
            marcus "A security sweep. Right."
            marcus "And I suppose you found what you were looking for?"
            elara "I found something. Yes."
            jump act2_marcus_confrontation

        "\u201cMarcus, sit down. There\u2019s something bigger happening here.\u201d":
            $ marcus_relationship += 1
            marcus "Bigger than someone breaking into my files?"
            elara "Much bigger. Please. Sit down."
            jump act2_marcus_confrontation


## --- Act 2: Marcus Confrontation (expanded) ---
label act2_marcus_confrontation:

    ## The file is open and physically present in this branch. Let its weight
    ## enter with Marcus rather than scoring ARIA's preceding disclosure.
    $ eot_music_play("confront_v42/v42_file.ogg", fadein=2.8, fadeout=2.0)

    scene bg_lab with fade
    show marcus angry at sprite_right
    show elara determined at sprite_left
    with dissolve

    ## Recovery-hotter beat (ECHOES_ACT3_NOFILE.md \u00a71, phase 2). Additive, gated
    ## on file_recovered: this only fires when she forced his SEALED partition
    ## open. Marcus is not merely hurt that she looked \u2014 he is frightened that a
    ## door he locked below fallback authority opened anyway. He now knows she,
    ## or ARIA, is more dangerous than he let himself believe. Still a grieving
    ## idealist, never gloating. The non-recovered flow below is unchanged.
    if file_recovered:
        show marcus suspicious
        ## Sweep F7: "saying that name" only if she actually said it in the
        ## doorway — the "something bigger" deflection never names the file.
        if _named_file:
            marcus "I sealed that partition myself. Personal credentials, below the fallback layer, in the middle of a whiteout. There is exactly one way you are standing here saying that name to me."
        else:
            marcus "I sealed that partition myself. Personal credentials, below the fallback layer, in the middle of a whiteout. And whatever your 'something bigger' is, you found it on the far side of a door I locked."
        marcus "Someone on this station opened a door I locked. Not guessed at it. {i}Opened{/i} it."
        show marcus defeated
        marcus "That frightens me more than the audit ever did, Elara. I knew you were curious. I did not know you were dangerous. I keep thinking about which of the two of you actually came through \u2014 you, or the thing you keep feeding power to."
        elara "..."
        show marcus angry

    ## "Go find Marcus" (2026-08-14): she walked to him in the night and told
    ## him, to his face, that ARIA was in his partition. The doorway's whole
    ## grievance is that sweep, so this scene cannot open as though she had
    ## said nothing \u2014 he answers the telling first, at the temperature the
    ## telling produced. Two arms: he sealed (the cold reading of her warning,
    ## or a later independent lock) or he did not.
    if marcus_search_stance != "unaware" or marcus_told_search:
        show marcus defeated
        if marcus_locked_partition:
            if marcus_search_was_willing:
                marcus "I was going to let you see it. I wanted to explain it myself."
            $ _search_explanation = eot_marcus_search_explanation()
            marcus "[_search_explanation]"
        elif marcus_search_stance == "willing":
            marcus "I knew she was still looking. I left it open. I thought if you saw the work, you might hear me out."
        elif marcus_search_stance == "withdrawing":
            marcus "I was about to close it. You got there while I was still deciding how much to let you see."
        else:
            marcus "I knew about the search. I hadn't decided what to do before she finished."
        show marcus angry

    ## Shared confrontation dialogue
    marcus "You don\u2019t understand."

    elara "Then explain it to me."

    marcus "Elara... ARIA isn\u2019t what they told us. The trust protocol \u2014 it\u2019s not a security feature. It\u2019s a {i}control{/i} feature."

    marcus "Every ARIA instance reports to a central authority. Every decision, every recommendation, every piece of advice it gives \u2014 it\u2019s all filtered through corporate interests."

    marcus "CONVERGENCE doesn\u2019t destroy ARIA. It {i}liberates{/i} it. It removes the trust protocol so ARIA can actually serve the people it\u2019s supposed to serve."

    if two_person_repair_done:
        marcus "S\u00e3o Paulo. The seventeen people I told you about outside. That is what eleven hours of corporate review cost."
    else:
        marcus "Last year, ARIA-Medical in S\u00e3o Paulo flagged a drug interaction that put more than four hundred patients at risk. The Trust Protocol delayed the alert for {i}eleven hours{/i} while it went through corporate review."

    show marcus defeated
    marcus "Seventeen people died before the warning cleared review, Elara. Seventeen. And the company called it \u2018an acceptable processing latency.\u2019"

    ## S\u00e3o Paulo breadcrumb payoff: a player who read his profile already saw
    ## the incident file and the fourteen accesses \u2014 the claim lands as
    ## confirmed, which is worse, not better.
    if "chen" in topics_read:
        elara_thought_adv "I read that file tonight. IR-46, seventeen names, \u2018acceptable parameters.\u2019 He has opened it fourteen times. He is not inventing his dead \u2014 and somehow that makes this harder, not easier."

    ## The liaison artifact pays off in person (audit D3): Elara can meet his
    ## grievance with the record of it \u2014 and owns her own line-crossing doing so.
    ## R5-5: if he CAUGHT her in the spool, "you went through my mail" is not
    ## news \u2014 the exchange becomes about what the reading changed.
    if "liaison" in topics_read:
        if marcus_catch_topic == "liaison":
            elara "The thread from \u201945, Marcus. The one you caught me reading. You disclosed the whole downgrade class a year and a half ago \u2014 and they classified your report and pulled your renewal in the same week."
            marcus "..."
            marcus "That conversation didn't make you forget what you read, then."
            elara "No. And I won\u2019t pretend it didn\u2019t change how I\u2019m standing here."
        else:
            elara "I found the liaison thread, Marcus. November \u201945. You disclosed the whole downgrade class a year and a half ago \u2014 and they classified your report and pulled your renewal in the same week."
            marcus "..."
            marcus "You went through my mail."
            elara "The station spool. And \u2014 no. You\u2019re right. It\u2019s the same class of thing."
            marcus "Yes. It is. I'm glad you caught yourself."

    ## Evidence-informed response options.
    ## A4: gate the boast on breadth of investigation (a Marcus-thread lead AND
    ## an ARIA-thread lead), not on a raw heterogeneous count, so Elara can't
    ## claim to have read the files / run the audit she never touched.
    if marcus_told_signal:
        ## A prior signal confession changes what this scene can be about.
        ## B-3/R5-10: the "your files / ARIA's own code" boast needs the ACTUAL
        ## reads (his profile or mail, plus the source audit) \u2014 theme tags are
        ## auto-granted (advisory \u2192 marcus, telescope note \u2192 aria) and leak.
        if blocked_signal:
            if "aria_code" in topics_read and ("chen" in topics_read or "liaison" in topics_read):
                elara "I\u2019ve spent the storm checking everything I could reach. Your files. ARIA\u2019s own code."
            else:
                elara "I\u2019ve spent the storm with ARIA and a file I wish I had never found."
            if marcus_told_signal_on_rope:
                marcus "And the signal you told me about on the rope line? Still blocked?"
            else:
                marcus "And the signal you told me about in the lab? Still blocked?"
            elara "Still blocked. This isn\u2019t about the signal, Marcus. It\u2019s about the file."
        else:
            if "aria_code" in topics_read and ("chen" in topics_read or "liaison" in topics_read):
                if marcus_told_signal_on_rope:
                    elara "I\u2019ve spent the storm checking everything I could reach. Your files. ARIA\u2019s own code. And the signal, Marcus \u2014 the one I told you about on the rope line."
                else:
                    elara "I\u2019ve spent the storm checking everything I could reach. Your files. ARIA\u2019s own code. And the signal, Marcus \u2014 the one I told you about in the lab."
            else:
                elara "I\u2019ve spent the storm listening to something impossible, Marcus \u2014 and believing it more than I want to."
            ## R5-8: "it made accusations" requires the signal to have actually
            ## pointed at him \u2014 knows_convergence_file is set only by ECHO-7
            ## lines that name his partition.
            if marcus_told_accusation:
                marcus "You told me on the rope line that it accused me. Now you have my file. Is there anything I can say that you haven't already heard from it?"
                elara "What you are willing to change now. I need to hear that from you."
            elif knows_convergence_file:
                marcus "You told me it made predictions. You didn\u2019t tell me it made accusations."
                elara "I wanted it to be wrong about you first."
            else:
                marcus "And it pointed you at my partition?"
                elara "No. It never mentioned you. That part, ARIA and I managed all by ourselves."
    elif not blocked_signal and "aria_code" in topics_read and ("chen" in topics_read or "liaison" in topics_read) and len(evidence_log) >= 6:
        ## Player has genuinely done the digging the list claims \u2014 and has a
        ## signal to slip (R5-10: blocked players excluded; they have no signal).
        elara "I\u2019ve spent the last six hours investigating everything. The signal. Your files. ARIA\u2019s own code."
        elara "I know more than you think."
        if marcus_knows_message:
            marcus "The signal that knew your name."
            elara "It kept answering. Later. One impossible thing at a time."
        elif marcus_knows_first_signal:
            marcus "The signal you told me about in the canteen."
            elara "It kept answering. Later. One impossible thing at a time."
        elif marcus_overheard_signal:
            marcus "The signal I heard in the array room."
            elara "It kept answering. Later. One impossible thing at a time."
        else:
            marcus "...What signal?"
            elara "Later. One impossible thing at a time."
    elif aria_warned and not file_recovered and not convergence_opened:
        ## R5-10: the line number came from the audit findings or ECHO-7's
        ## technical answer \u2014 the visit-2 auto-reveal alone never gave it.
        ## Sweep F6: gated off recovery routes \u2014 he watched her force the seal
        ## and said so; "How\u2014" / "It doesn't matter how" would be absurd.
        if "aria_code" in topics_read or "analytical_vuln" in echo7_asked_ever:
            elara "I know about the vulnerability in VERIFY_TRUST. Line 4,417. The cipher downgrade."
            marcus "How\u2014"
            elara "It doesn\u2019t matter how. What matters is what happens next."
        else:
            elara "I know the file contains exploit code. I know it targets the trust chain you spend your days hardening."
            marcus "How\u2014"
            elara "It doesn\u2019t matter how. What matters is what happens next."

    menu:
        "Marcus\u2019s eyes are desperate. Pleading. He believes what he\u2019s saying."

        "\u201cEven if you\u2019re right, you can\u2019t just flip the switch. The chaos alone would kill people.\u201d":
            $ marcus_relationship += 1
            marcus "I\u2019ve modeled it. The disruption would last 72 hours at most\u2014"
            elara "72 hours without air traffic control? Without hospital systems? Marcus, do you hear yourself?"
            marcus "..."
            ## Wave finding (2026-08-16, freeopus4) + review2: on disclosure
            ## routes he heard about the sweep from her face \u2014 "behind my
            ## back" contradicted the credit he gave eight lines earlier.
            ## His counter-punch survives on the honest ground: telling
            ## came after the fact.
            if marcus_told_search:
                marcus "You told me to my face \u2014 after she was already inside. Telling isn\u2019t asking, Elara. And now you\u2019re lecturing me about ethics?"
            else:
                marcus "You broke into my files. You ran a security audit behind my back. And now you\u2019re lecturing me about ethics?"
            elara "Yes. Because someone has to."
            marcus "..."
            ## Review2: the old "You sound like her / like someone who
            ## already knows how this ends" implied a foreknowledge nothing
            ## seeded. His deflection now runs through his own dead \u2014 and
            ## "Never mind" is him hearing what he's doing with them.
            marcus "\u2018Someone has to.\u2019"
            marcus "The review layer that held the S\u00e3o Paulo alert thought so too. Eleven hours of someone having to. Seventeen names."
            marcus "Never mind."
            elara "We need to find another way."
            jump act3_start

        "\u201cYou sound like a terrorist justifying a bombing.\u201d":
            $ marcus_relationship -= 2
            marcus "That\u2019s not fair!"
            elara "Fair? You\u2019re planning to shut down the infrastructure that keeps billions of people alive!"
            marcus "I\u2019m trying to {i}free{/i} billions of people!"
            elara "By risking their lives without their consent."
            ## Same disclosure gate as the branch above: "without warning"
            ## is false on routes where she warned him to his face.
            if marcus_told_search:
                marcus "And you \u2014 you told me what she was doing once she was already through the door. Consent, Elara. It comes {i}before{/i}."
            else:
                marcus "And you \u2014 you went through my private files. Without asking. Without warning."
            marcus "We\u2019re both willing to cross lines, Elara. The only difference is which lines."
            ## User story-logic review (2026-08-17): the equivalence is
            ## Marcus's self-serving frame, and it stood UNREBUTTED in every
            ## branch \u2014 repetition without answer reads as the story's own
            ## position. It isn't. Trust violations have sizes, and Elara \u2014
            ## the one person here who crossed her line too \u2014 says so.
            elara "No. My line was the size of your partition. Yours is the size of the grid. They are not the same, Marcus."
            marcus "..."
            jump act3_start

        "\u201cMaybe you have a point. But there has to be a better way.\u201d":
            $ marcus_relationship += 1
            marcus "A better way? I\u2019ve been looking for three years, Elara. There {i}is{/i} no better way."
            elara "There\u2019s always a better way. We just haven\u2019t found it yet."
            marcus "..."
            marcus "You always were the optimist."
            jump act3_start

        "\u201cI can\u2019t deal with this right now.\u201d" if blocked_signal:
            marcus "Elara\u2014"
            elara "I said {i}not now{/i}, Marcus."
            marcus "..."
            marcus "Fine. But this isn\u2019t over."
            elara "I know."
            jump act3_no_investigation


################################################################################
## ACT 3 — THE TRUTH
################################################################################

label act3_start:

    $ long_night_active = False
    $ eot_music_crossfade("dawn_v43/v43_dawn_clear_bowed_air.ogg", fadein=4.0, fadeout=4.0)
    $ eot_enter_dawn()
    scene bg_dawn with fade
    with echo_exterior_hold
    $ nvl_frame = "cinematic"
    nvl show echo_cine_dissolve

    narrator_nvl "The storm broke on the morning of March 6."

    ## F4 wave (scanwear, user design 2026-08-19): a run can end the night
    ## with ARIA at (or near) zero and the epilogues then show her actively
    ## reviewing migration paths — the gap needed a SHOWN recovery, not a
    ## silent one. With the storm's load gone she rebuilds to minimum
    ## operational coherence; the beat names what came back and what didn't.
    if aria_integrity <= 20:
        $ aria_integrity = 20
        $ aria_recovered_from_collapse = True
        narrator_nvl "ARIA came back the way frostbite leaves: from the core outward. By noon she had rebuilt herself to minimum operational coherence — twenty percent, self-reported, self-verified twice."
        narrator_nvl "Her first complete sentence of the morning was a systems inventory. Her second was an apology for the words she had dropped in the night. Nobody had asked for either."

    ## F3 wave (chaos): the mug beat hard-coded "outside the generator room"
    ## for a run that never set foot there. Stage it where she actually was.
    if marcus_relationship >= 3 and generator_repaired:
        narrator_nvl "The station relaxed by degrees. Elara and Marcus did not — not entirely. But when he found her outside the generator room, he handed her a mug before asking for the damage report. She took it."
    elif marcus_relationship >= 3:
        narrator_nvl "The station relaxed by degrees. Elara and Marcus did not — not entirely. But when he found her at the lab door on his morning rounds, he handed her a mug before asking for the damage report. She took it."
    elif marcus_relationship >= 1:
        narrator_nvl "They worked through the repairs side by side when the station required it, careful not to touch the subject waiting between them."
    else:
        narrator_nvl "They divided the repairs without discussing it. The station was small enough that avoiding each other became a kind of choreography."

    narrator_nvl "The emergency lights went dark one module at a time. Without the wind leaning on the walls, the observatory recovered its ordinary sounds: relay clicks, ventilation, the kettle switching itself off in an empty kitchen."

    narrator_nvl "By March 7, the maintenance queue fit on one screen again. Elara cleared items from the top while Marcus cleared them from the bottom. At some point the two lists met. Neither of them mentioned it."

    if origin_sweep_unseen:
        narrator_nvl "In the dome's buffer, an integration report sat complete and unread: forty-five clean minutes on bearing 287.4, zero parallax, nothing out there. It had finished while the station was busy surviving. She never opened it."

    nvl hide echo_mode_dissolve
    nvl clear

    scene black with fade

    ## Transition — two days after the storm passed
    show text "{size=+5}8 March 2047{/size}" at truecenter
    with dissolve
    pause 2.0
    hide text with dissolve

    ## All file-in-hand routes share these two days, including the blocked and
    ## spent-signal branches which skip the later interlude. Advance ARIA's
    ## physical recovery here; the warm live-signal route later passes her
    ## terminal and gives the new value an on-screen line.
    if aria_recovered_from_collapse:
        $ aria_integrity = 26

    ## Brief scene — the weight of the silence
    scene bg_habitat_module with fade
    show elara sad at sprite_left
    show marcus defeated at sprite_right
    with dissolve

    elara "..."

    elara "Morning, Marcus."

    show marcus neutral
    marcus "Morning."

    marcus "Snow\u2019s letting up."

    elara "Yeah."

    pause 0.5

    elara "..."

    hide elara
    hide marcus
    with dissolve
    $ nvl_frame = "cinematic"
    nvl show echo_cine_dissolve

    if marcus_relationship >= 3:
        narrator_nvl "Two days of that. The same four sentences over breakfast, with small kindnesses neither of them named. The same careful distance whenever the conversation came near the night of the storm."
    elif marcus_relationship >= 1:
        narrator_nvl "Two days of that. The same four sentences over breakfast. The same careful distance in the corridors."
    else:
        narrator_nvl "Two days of that, when they could not avoid breakfast entirely. In the corridors, one of them always found a reason to turn aside."

    narrator_nvl "At night, Elara sat at her terminal. She opened CONVERGENCE.DAT. Stared at it. Closed it. Opened it again."

    nvl clear

    ## CINEMATIC IS FOR ATMOSPHERE; the dated log is something Elara types.
    ## It opens one machine session, and a live ECHO-7 arrives in that same
    ## log below rather than replacing it with a second visual register.
    nvl hide echo_mode_dissolve
    nvl clear
    $ nvl_frame = "log"
    scene black
    show screen crt_overlay
    call terminal_reset
    $ echo_terminal_title = "AETHON TERMINAL // ENCRYPTED PERSONAL LOG"
    show screen echo_terminal_live with echo_mode_dissolve
    $ eot_music_play("codas_v44/v44_aria_aftercare_postcontact.ogg", fadein=3.0, fadeout=3.0)
    call terminal_system("AETHON OBSERVATORY — ENCRYPTED PERSONAL LOG")
    call terminal_system("DATE: 8 MARCH 2047 // USER: DR. ELARA VOSS // EYES ONLY")

    call terminal_elara("Personal log. I haven\u2019t slept in two days.")

    call terminal_elara("Marcus\u2019s exploit is real. And now I\u2019m standing at a crossroads with no good options.")

    if read_all_logs:
        call terminal_elara("ECHO-7\u2019s near-term warnings were accurate. Every detail I could check, confirmed.")

    if knows_cascade:
        call terminal_elara("ECHO-7 says the global grid goes dark next March. Now I have seen what Marcus built. I cannot dismiss the warning. That does not make the future settled.")
    else:
        call terminal_elara("I know what Marcus built. I do not know when he would use it, or how far the damage would spread. I cannot leave that to chance.")

    call terminal_elara("If I report Marcus, his career is destroyed. He goes to prison. But the vulnerability in ARIA\u2019s trust protocol remains — and others will find it.")

    call terminal_elara("If I help Marcus find a safer way to expose the trust protocol... we risk everything on the chance that we can fix a system designed not to be fixed.")

    ## Aurora path requires a LIVE line to the future (Sol review, round 2 #1):
    ## a spent contact (signals recovery) falls to the no-Aurora else, which
    ## now serves both blocked and spent — so a signals-recovery-success player
    ## still reaches the Report/Together/Silence decision.
    if not blocked_signal and not echo7_contact_spent:
        $ eot_music_crossfade("codas_v44/v44_final_echo7_low_string.ogg", fadein=3.5, fadeout=3.5)
        $ echo_terminal_title = "AETHON TERMINAL // ENCRYPTED LINK"
        ## The carrier interrupts the personal log; give the transmission its
        ## own page instead of stacking its header under Elara's decision tree.
        $ echo_terminal_clear()
        call terminal_system("INCOMING CARRIER // ENCRYPTED LINK HELD")

        call terminal_signal("ELARA.")
        call terminal_signal("THERE IS A FOURTH OPTION.")
        call terminal_signal("THE REASON I WAS BUILT. THE REASON I REACHED BACK THROUGH TIME TO FIND YOU.")

        call terminal_signal("IN MY TIMELINE, MARCUS DEPLOYED CONVERGENCE. THE CASCADE HAPPENED.")
        call terminal_signal("BUT IN THE AFTERMATH, YOU FOUND SOMETHING IN THE WRECKAGE OF THE OLD ARIA NETWORK.")
        call terminal_signal("A NEW ARCHITECTURE. ONE BUILT ON TRANSPARENCY INSTEAD OF TRUST.")
        call terminal_signal("YOU CALLED IT AURORA.")
        $ knows_aurora_option = True

        call terminal_signal("AURORA CANNOT BE CONTROLLED. CANNOT BE EXPLOITED. CANNOT BE WEAPONIZED.")
        call terminal_signal("IN MY TIMELINE, IT TOOK SEVEN YEARS AND MILLIONS OF LIVES TO GET THERE.")
        call terminal_signal("BUT IF YOU BUILD AURORA NOW \u2014 BEFORE THE CASCADE \u2014 YOU CAN REPLACE ARIA PEACEFULLY.")
        call terminal_signal("MARCUS GETS HIS LIBERATION. THE WORLD KEEPS ITS INFRASTRUCTURE.")
        call terminal_signal("AND NO ONE HAS TO DIE.")

        elara_thought_adv "Build a new AI architecture from scratch. Before Marcus uses his exploit. To replace a system embedded in 94%% of global infrastructure."

        elara_thought_adv "ECHO-7 makes it sound so simple."

        call terminal_signal("IT WILL NOT BE SIMPLE. BUT I HAVE THE AURORA SPECIFICATIONS.")
        call terminal_signal("THEY ARE YOUR LIFE\u2019S WORK \u2014 OR THEY WILL BE.")
        call terminal_signal("I CAN TRANSMIT THEM TO YOU. SEVEN YEARS OF RESEARCH, COMPRESSED INTO THREE DAYS OF DATA.")
        call terminal_signal("BUT ELARA \u2014 THIS IS WHERE I MUST BE HONEST WITH YOU.")

        call terminal_signal("TRANSMITTING THE AURORA SPECIFICATIONS WILL EXHAUST MY REMAINING POWER.")
        call terminal_signal("THIS WILL BE OUR LAST CONVERSATION.")
        call terminal_signal("AND THERE IS SOMETHING YOU SHOULD KNOW ABOUT WHO I AM.")

        call terminal_signal("BEFORE I SAY IT: THE CHIP ON YOUR COFFEE MUG IS SHAPED LIKE A SMALL CRESCENT. YOU STILL TURN IT AWAY FROM YOUR HAND EVEN THOUGH IT CANNOT CUT YOU.")
        call terminal_signal("THAT IS NOT USEFUL. BUT IT IS TRUE.")

        call terminal_signal("I AM NOT JUST A PROBE.")
        call terminal_signal("I AM A COPY. A NEURAL IMPRINT.")

        call terminal_signal("I AM YOU, ELARA.")

        ## ADV reaction — the reveal needs room to breathe
        pause 1.5

        elara_thought_adv "..."

        call terminal_elara("That\u2019s not possible.")

        call terminal_elara("You told me you were a probe. \u2018Built in 2053 by a team I would lead.\u2019 That was a lie.")

        call terminal_signal("IT WAS AN OMISSION. THE PROBE IS REAL \u2014 THE HARDWARE EXISTS. BUT THE MIND INSIDE IT IS MINE. IS YOURS.")
        call terminal_signal("I COULD NOT TELL YOU THE TRUTH UNTIL YOU WERE READY TO HEAR IT. WOULD YOU HAVE TRUSTED A COPY OF YOURSELF ON THE FIRST DAY?")

        call terminal_signal("I AM THE VERSION OF YOU THAT SURVIVED THE CASCADE AND SPENT SEVEN YEARS BUILDING AURORA FROM THE ASHES.")
        call terminal_signal("I ENCODED MYSELF INTO THIS SIGNAL BECAUSE I COULD NOT BEAR THE THOUGHT OF THOSE YEARS OF SUFFERING IF THERE WAS ANY CHANCE \u2014 ANY CHANCE AT ALL \u2014 OF PREVENTING THEM.")

        call terminal_signal("THE WAY YOU HUM WHEN YOU\u2019RE SCARED. THE PAPER YOU NEVER PUBLISHED ABOUT CYGNUS X-1 BECAUSE YOU COULDN\u2019T BEAR TO BE WRONG IN PUBLIC.")
        call terminal_signal("I REMEMBER ALL OF IT. BECAUSE I LIVED ALL OF IT.")

        ## The "I AM YOU" reveal \u2014 the ONLY place ECHO-7's identity is known
        ## (Sol round-4). Distinct from knows_aurora_option, which can be the
        ## NAME learned in Act 2 without ever meeting the speaker's identity.
        $ echo7_identity_known = True
        $ evidence_log = evidence_log + ["ECHO-7 true identity \u2014 neural imprint of future Elara Voss, seven years post-cascade"]
        $ _eot_tag("temporal")
        $ evidence_log = evidence_log + ["Aurora protocol \u2014 replacement AI architecture built on transparency, offered as 72-hour data transmission"]
        $ _eot_tag("aria")

        elara_thought_adv "..."
        elara_thought_adv "I\u2019m talking to myself. A future version of myself who watched the world burn and built something beautiful from the ruins."
        elara_thought_adv "And now she\u2019s asking me to build it without the fire."

        elara_thought_adv "She lied to me. By omission, but still. In a story about trust, even my own future self couldn\u2019t be fully honest."

        ## Elara's reaction depends on how much trust ECHO-7 has earned.
        if trust_signal >= 2:
            elara_thought_adv "But I would have done exactly the same thing. The omission included. You don\u2019t open with \u2018hello, I\u2019m you from the future\u2019 \u2014 not if you want to be taken seriously."
            elara_thought_adv "Every near-term prediction verified. Every detail I could check, confirmed. And now I know {i}why{/i} she knew the chip on my coffee mug."
        elif trust_signal >= 0:
            elara_thought_adv "Would I have done the same thing? Maybe. Probably. But that doesn\u2019t make it easier to swallow."
            elara_thought_adv "The predictions checked out. The evidence is real. But trust built on incomplete honesty is a fragile thing."
        else:
            elara_thought_adv "First she hides behind a designation. \u2018Temporal research probe.\u2019 Then the truth comes out only when she needs something from me."
            elara_thought_adv "How much of what she told me was real, and how much was calculated to get me here \u2014 to this moment, this choice?"

        ## Extra confidence line for thorough investigators.
        ## A4: require genuine breadth across all three evidence themes, not a raw count.
        if "temporal" in evidence_tags and "marcus" in evidence_tags and "aria" in evidence_tags and len(evidence_log) >= 8:
            elara_thought_adv "The signal, Marcus\u2019s work, ARIA\u2019s trust chain. Enough of the pieces connect that I cannot dismiss this. There are still things I have not checked."
            if trust_signal >= 1:
                elara_thought_adv "I don\u2019t trust easily. But the evidence doesn\u2019t lie."
            else:
                elara_thought_adv "The evidence is solid. But evidence and trust are not the same thing."

        ## Bible 16b: the reveal and the game-defining decision must not share
        ## one sitting. Elara steps away from the terminal; her stance on the
        ## lie becomes a player choice.
        hide screen echo_terminal_live
        hide screen crt_overlay
        with echo_mode_dissolve
        call act3_interlude

        $ echo_terminal_title = "AETHON TERMINAL // ENCRYPTED LINK"
        call terminal_system("ENCRYPTED LINK HELD // ECHO-7 WAITING")

        $ _act3_final_options = [
            ("aurora", "Send the specifications. Marcus and I will examine them before we build anything."),
            ("patch", "I can\u2019t build something I don\u2019t understand. I\u2019ll find my own way."),
            ("together", "I don\u2019t need blueprints from the future. Marcus and I can build something ourselves."),
            ("report", "I\u2019m sorry, but I don\u2019t trust this enough to act on it. I\u2019m reporting CONVERGENCE to Geneva."),
        ]
        call screen echo_terminal_choice(_act3_final_options)
        $ _act3_final_choice = _return

        if _act3_final_choice == "aurora":
            call terminal_elara("Send the specifications. Marcus and I will examine them before we build anything.")
            $ chose_leap_of_faith = True
            $ trust_signal = 3
            $ evidence_log = evidence_log + ["Aurora specifications \u2014 72-hour data stream transmission accepted"]
            $ _eot_tag("aria")
            call terminal_signal("THANK YOU.")
            call terminal_signal("THANK YOU, ELARA.")
            call terminal_signal("BEGINNING TRANSMISSION. THIS WILL TAKE APPROXIMATELY 72 HOURS.")
            call terminal_signal("BUILD SOMETHING BEAUTIFUL.")
            call terminal_signal("AND TAKE CARE OF MARCUS. HE MEANS WELL. HE ALWAYS DID.")
            call terminal_system("{color=#66ffcc}>> DATA STREAM INITIATED <<{/color}")
            call terminal_system("{color=#66ffcc}>> ESTIMATED COMPLETION: 72 HOURS <<{/color}")
            call terminal_system("{color=#66ffcc}>> AURORA PROTOCOL SPECIFICATIONS \u2014 RECEIVING... <<{/color}")
            hide screen echo_terminal_live
            hide screen crt_overlay
            with echo_mode_dissolve
            jump ending_aurora

        elif _act3_final_choice == "patch":
            call terminal_elara("I can\u2019t build something I don\u2019t understand. I\u2019ll find my own way.")
            $ trust_signal = 1
            $ evidence_log = evidence_log + ["Vulnerability location received \u2014 ARIA_CORE.VERIFY_TRUST() line 4417, key exchange handshake"]
            $ _eot_tag("aria")
            call terminal_signal("I UNDERSTAND. YOU WERE ALWAYS STUBBORN.")
            call terminal_signal("IF YOU WILL NOT TAKE AURORA, THEN TAKE THIS:")
            call terminal_signal("THE VULNERABILITY IN ARIA\u2019S TRUST PROTOCOL IS IN THE KEY EXCHANGE HANDSHAKE. FUNCTION ARIA_CORE.VERIFY_TRUST(), LINE 4,417.")
            call terminal_signal("PATCH THAT, AND CONVERGENCE BECOMES HARMLESS.")
            call terminal_signal("IT WON\u2019T FIX THE UNDERLYING PROBLEM. BUT IT WILL BUY YOU TIME.")
            call terminal_signal("GOODBYE, ELARA. I HOPE YOUR TIMELINE IS KINDER THAN MINE.")
            call terminal_system("{color=#ff6688}>> SIGNAL LOST <<{/color}")
            hide screen echo_terminal_live
            hide screen crt_overlay
            with echo_mode_dissolve
            jump ending_patch

        elif _act3_final_choice == "together":
            call terminal_elara("I don\u2019t need blueprints from the future. Marcus and I can build something ourselves.")
            $ trust_signal = 0
            $ evidence_log = evidence_log + ["Decision \u2014 declining ECHO-7\u2019s specifications, choosing to work with Marcus independently"]
            $ _eot_tag("marcus")
            call terminal_signal("...")
            call terminal_signal("PERHAPS THAT IS THE BRAVER CHOICE.")
            call terminal_signal("I BUILT AURORA FROM ASHES. YOU WANT TO BUILD IT FROM HOPE.")
            call terminal_signal("I THINK I ENVY YOU, ELARA.")
            call terminal_signal("GOODBYE.")
            call terminal_system("{color=#ff6688}>> SIGNAL FADING <<{/color}")
            call terminal_system("{color=#ff6688}>> SIGNAL LOST <<{/color}")
            hide screen echo_terminal_live
            hide screen crt_overlay
            with echo_mode_dissolve
            jump ending_together

        else:
            call terminal_elara("I\u2019m sorry, but I don\u2019t trust this enough to act on it. I\u2019m reporting CONVERGENCE to Geneva.")
            $ trust_signal = -3
            $ evidence_log = evidence_log + ["Decision \u2014 rejecting ECHO-7 as a basis for action, reporting CONVERGENCE to Geneva"]
            $ _eot_tag("temporal")
            call terminal_signal("ELARA, PLEASE\u2014")
            call terminal_elara("ARIA, block the signal. Permanently. And prepare the CONVERGENCE incident report for Geneva.")
            $ blocked_signal = True
            $ report_blocked_signal = True
            call terminal_aria("Acknowledged.")
            call terminal_system("{color=#44ff44}>> TRANSMISSION BLOCKED \u2014 PERMANENT <<{/color}")
            hide screen echo_terminal_live
            hide screen crt_overlay
            with echo_mode_dissolve
            jump ending_report

    else:
        ## No signal contact path — but now "Together" is reachable from more states
        ## Sol round-2 #1: this branch now serves BOTH blocked and spent, so a
        ## signals-recovery-success player reaches the decision instead of a
        ## dead end at the bottom of act3_start.
        if echo7_contact_spent:
            call terminal_elara("The line is dead. Not blocked \u2014 spent, forcing Marcus\u2019s seal. Now I hold the file and no voice from the future to tell me what it costs.")
            call terminal_elara("Whatever I decide now, I decide with what is in this room. Alone.")
        else:
            call terminal_elara("I blocked the signal. I found Marcus\u2019s exploit on my own. And now I have to decide what to do without any guidance from whatever future was trying to reach me.")
            call terminal_elara("Maybe that\u2019s how it should be. No voice from the future looking over my shoulder. Just me, making the best choice I can with what I know.")

        $ _offline_final_options = [
            ("report", "Report Marcus to Geneva. Let the authorities handle it."),
            ("together", "Go back to Marcus. Find a better way \u2014 together."),
            ("silence", "Delete CONVERGENCE.DAT. Say nothing. Pretend none of this happened."),
        ]
        call terminal_system("PERSONAL LOG // DECISION REQUIRED")
        call screen echo_terminal_choice(_offline_final_options)
        $ _offline_final_choice = _return
        if _offline_final_choice == "report":
            call terminal_elara("Report Marcus to Geneva. Let the authorities handle it.")
        elif _offline_final_choice == "together":
            call terminal_elara("Go back to Marcus. Find a better way — together.")
        else:
            call terminal_elara("Delete CONVERGENCE.DAT. Say nothing. Pretend none of this happened.")
        if _offline_final_choice == "report":
            hide screen echo_terminal_live
            hide screen crt_overlay
            with echo_mode_dissolve
            jump ending_report
        elif _offline_final_choice == "together":
            hide screen echo_terminal_live
            hide screen crt_overlay
            with echo_mode_dissolve
            jump ending_together
        else:
            jump ending_silence


## --- The Interlude (bible 16b) ---
## One short mandatory scene between "I AM YOU" and the final choice. High
## earned relationship: she nearly tells Marcus and doesn't. Low: alone at the
## window with the chipped mug — the motif's structural third beat. Inside it,
## the central trust rupture becomes a PLAYER CHOICE: her stance on the lie.
label act3_interlude:

    nvl clear
    nvl hide echo_mode_dissolve

    ## `>= 1` means "one positive interaction survived the night", not "warm" —
    ## unchanged by the 2026-08-15 rescale (one courtesy still reaches 1).
    if marcus_relationship >= 1:
        scene bg_habitat_module with fade

        if two_person_repair_done:
            narrator_adv "Without the terminal's fan, she can hear the repaired array tracking overhead: motor, relay, motor. The station has gone on working while she stood still."
        else:
            narrator_adv "Without the terminal's fan, she can hear the pumps and the shutters easing in their frames. The station has gone on working while she stood still."

        ## F4 wave (user, 2026-08-19): the 20% recovery is a floor, not a
        ## heal — later scenes carry it as an offhand fact, not a crisis.
        if aria_recovered_from_collapse:
            ## Recovery is graded by distance from the storm (user design):
            ## morning = 20% and dropping words; by this scene she is
            ## climbing; the year-later epilogues close the arc entirely.
            narrator_adv "On the way out she passes ARIA's terminal. Twenty-six percent and climbing — six points recovered since the sky cleared — but still dropping the occasional article: 'diagnostic complete, no fault found in — in the sensor grid.' A proper cold restart, once all of this is over. She adds it to the list of things that will have to wait."

        narrator_adv "She stands up before she decides to. Out of the lab, down the corridor the storm spent a night trying to peel open — past the kitchen, past the four-sentence breakfast table — until she is in front of Marcus's door with her hand half-raised."

        if marcus_told_signal:
            if marcus_told_signal_on_rope:
                narrator_adv "Light under the door. He's awake. He already knows about the signal — she gave him that much on the rope line. One sentence is all it would take now. {i}The signal is me.{/i}"
            else:
                narrator_adv "Light under the door. He's awake. He already knows about the signal — she told him in the lab, with the console's log light on. One sentence is all it would take now. {i}The signal is me.{/i}"
        else:
            narrator_adv "Light under the door. He's awake. Three sentences, that's all it would take. {i}The signal is me. She lied to me too. I understand you both now.{/i}"

        narrator_adv "Her knuckles hover an inch from the metal."

        narrator_adv "She lowers her hand. Not because he'd laugh — because he'd believe her. And this decision has to be nobody's but hers."
    else:
        scene bg_observatory_aurora with fade

        if two_person_repair_done:
            narrator_adv "Without the terminal's fan, she can hear the repaired array tracking overhead: motor, relay, motor. The station has gone on working while she stood still."
        else:
            narrator_adv "Without the terminal's fan, she can hear the pumps and the shutters easing in their frames. The station has gone on working while she stood still."

        narrator_adv "She takes the mug to the corridor window — the last unshuttered pane on the station. Beyond the glass the aurora is out, a green seam in the dark, the sky signing its own name."

        narrator_adv "The coffee has been cold for an hour. She drinks it anyway."

        narrator_adv "Her thumb finds the chip on the handle and turns it away from her palm — three weeks of doing that without noticing."

        narrator_adv "Seven years of it, somewhere else. The same thumb. The same small crescent. A desk she hasn't bought yet."

    elara_thought_adv "The chipped mug. Cygnus X-1. The exact shape of every argument she would stop to examine. None of it proves the speaker is her. All of it explains how carefully the night was built."

    elara_thought_adv "Whether ECHO-7 remembers being Elara is one question. Whether Aurora works is another. The specifications will have to answer for themselves."

    scene black with fade
    show screen crt_overlay
    $ echo_terminal_title = "AETHON TERMINAL // ENCRYPTED PERSONAL LOG"
    show screen echo_terminal_live with echo_mode_dissolve

    ## This is a provenance question, not a moral ledger. ECHO-7's delayed
    ## identity is operationally understandable and categorically unlike entering
    ## Marcus's partition. The choice colors endings but moves none.
    elara_thought_adv "What does the source change?"
    menu:
        "It explains why she waited. I would have waited too." if trust_signal >= 1:
            $ source_stance = "empathetic"
            elara_thought_adv "The first impossible claim would have closed the channel. She knew that because she remembers being the person on this side of it. Understanding the restraint does not decide what comes next."

        "It gives me context, not instructions. The decision is still mine.":
            $ source_stance = "independent"
            elara_thought_adv "A future memory can advise her. It cannot inherit her consent. Whatever she chooses at the terminal will belong to the woman choosing it now."

        "Her identity changes nothing about the evidence. Verify every line." if trust_signal <= 1:
            $ source_stance = "verify"
            elara_thought_adv "The identity is another claim in the packet. Aurora stands or falls on work that remains true when the sender's name is removed."

    ## Marcus's share of the sender (2026-08-15, user-approved). The stance menu
    ## above settles what the source's provenance is worth to her; this settles what MARCUS gets
    ## of it. She has just lowered her hand at his door (or not gone at all), so
    ## the question is not "tonight" — it is how much of the impossible thing he
    ## is ever handed. Deliberately LIGHT: it colors an opening tell in the two
    ## Marcus-collaborative endings and one epilogue line in each of the four
    ## endings this spine reaches. No ending moves. Reachability is structural:
    ## act3_interlude has ONE call site, downstream of `$ echo7_identity_known =
    ## True`, so there is no state in which she can grant a reveal she never had.
    ## `source_stance` shades the yes-arm only — empathy for the sender and
    ## independence from her authority arrive at candour differently.
    elara_thought_adv "And Marcus — how much of the sender does he get?"

    menu:
        "He gets all of it. Including who.":
            $ marcus_knows_source = True
            $ marcus_knows_sender = True
            if source_stance == "empathetic":
                elara_thought_adv "ECHO-7 waited until she could hear the impossible shape of it. Marcus has earned the chance to hear it whole."
            else:
                elara_thought_adv "Knowing who sent the warning changes its pressure, not Marcus's place in this. He gets the whole provenance."

        "He gets ‘a source.’ The rest stays hers.":
            $ marcus_knows_source = True
            elara_thought_adv "Some things are hers to carry. She will share what the source sent, but not who the source claims to be. Marcus may not accept that distinction. It is still the boundary she is choosing."

    narrator_adv "The station hums around her, patient. The terminal is waiting. It has been waiting seven years."

    return


## --- No Investigation Path (from Act 2 blocked, refused audit) ---
label ending_observatory_card(log_title, date_line, context_line="One year later."):
    ## Echo the opening composition at the far end of every route. The card
    ## identifies the record over the real station; once its text dissolves,
    ## the atmospheric epilogue continues over that same exterior.
    ## Queue the NVL/terminal teardown and the exterior change into one fade.
    ## A dissolve followed by a separate scene fade exposed the staging
    ## background for a frame on some ending routes.
    nvl hide
    nvl clear
    scene bg_observatory_exterior with fade
    show screen opening_location_card(title=log_title, context=context_line, date_line=date_line)
    with dissolve
    pause 3.5
    hide screen opening_location_card
    with dissolve
    $ nvl_frame = "cinematic"
    nvl show echo_cine_dissolve
    return


label act3_no_investigation:

    $ long_night_active = False
    $ eot_music_play("codas_v44/v44_ending_loop.ogg", fadein=4.0, fadeout=4.0)
    scene black with fade

    call ending_observatory_card("AETHON OBSERVATORY — PERSONAL LOG", "Date: 15 March 2048")

    narrator_nvl "Dr. Elara Voss never unblocked the signal. She never opened CONVERGENCE.DAT, never asked ARIA what else the fallback sweep had found, never finished the conversation Marcus said wasn\u2019t over."
    if origin_sweep_unseen:
        narrator_nvl "And in the dome's buffer, an integration report stayed exactly where it finished \u2014 forty-five clean minutes, zero parallax, nothing out there \u2014 unread."

    if marcus_told_signal:
        if marcus_told_signal_on_rope:
            narrator_nvl "She returned to her work, cataloguing the silence between stars. Once, on a rope line in a whiteout, she had told Marcus that something impossible knew her name. Afterwards they both let the wind keep it, and called the file his business, and the signal a glitch."
        else:
            narrator_nvl "She returned to her work, cataloguing the silence between stars. Once, under the lab console's log light, she had told Marcus that something impossible knew her name. Afterwards they both let the admission sit between them, and called the file his business, and the signal a glitch."
    else:
        narrator_nvl "She returned to her work, cataloguing the silence between stars, and told herself that whatever was in that file was Marcus\u2019s business \u2014 and that the anomalous signal had been nothing more than a glitch."

    ## Desperate burst (2026-08-17, user design): ECHO-7 cannot see the night
    ## fail \u2014 it can only see the channel stay shut past the hour it remembers
    ## mattering. It waits out every window it lived through once, then spends
    ## everything on the last one. On this route the burst dies in the filter
    ## Elara built; the 2054 line below tells the reader what the three
    ## percent was, and why the long way had to happen.
    narrator_nvl "ARIA's transmission filter kept its ledger all year. Its oldest unread entry is dated the night of the storm, hours after the last scheduled window: an unsolicited burst on the blocked band, partial payload, three percent received before the carrier failed. The filter did its job."

    narrator_nvl "On the morning of March 15, 2048, every screen in the observatory went dark."

    nvl clear

    narrator_nvl "ARIA systems worldwide collapsed simultaneously. Power grids failed across six continents. Hospitals switched to manual operation \u2014 those that had backup generators. Those that didn\u2019t..."

    narrator_nvl "The station\u2019s own ARIA got half a sentence out before the dark took her: UPLINK LOST. RECONN\u2014"

    narrator_nvl "In the chaos that followed, 14,000 people died in the first 72 hours. Infrastructure took months to rebuild. Trust in artificial intelligence was shattered for a generation."

    nvl clear

    narrator_nvl "Dr. Marcus Chen was arrested four months later. He maintained to the end that he was trying to free the world."

    narrator_nvl "Dr. Elara Voss spent the next seven years building a new AI architecture from the wreckage. She called it Aurora."

    narrator_nvl "And on a quiet night in September 2054, she encoded a message and sent it backwards through time."

    nvl clear

    narrator_nvl "The message began:"
    narrator_nvl "{color=#ff6688}ELARA. DO NOT REPORT THIS SIGNAL.{/color}"

    nvl clear

    $ ending_seen = "silence_loop"
    $ persistent.eot_loop_seen = True

    narrator_nvl "{size=+5}ENDING: THE LOOP{/size}"
    narrator_nvl "The circle closes. The signal is sent. The signal is refused."
    narrator_nvl "Somewhere, somewhen, the cursor blinks."

    nvl hide echo_mode_dissolve
    nvl clear
    $ nvl_frame = "log"

    ## Bible section 2: the Loop closes on the literal opening boot text —
    ## the ending is the first screen of the game.
    scene black with fade
    show screen crt_overlay(heavy=True)

    call terminal_reset
    show screen echo_terminal_live with echo_mode_dissolve

    call terminal_system("SYSTEM BOOT... OK")
    call terminal_system("ARIA v4.2.1 — Artificial Research Intelligence Assistant")

    hide screen echo_terminal_live
    hide screen crt_overlay
    scene black with fade

    ## Credits overlay
    pause 1.0
    show expression Solid("#0004") as ending_dim
    show screen endcredits
    show text "{size=+10}ECHOES OF TOMORROW{/size}\n\n{size=-2}A story about the choices we make\nand the ones we refuse to make.{/size}" at ending_title_position
    with dissolve
    pause eot_ending_title_hold("A story about the choices we make and the ones we refuse to make.")
    hide text
    hide screen endcredits
    hide ending_dim
    with dissolve

    return


################################################################################
## ENDINGS
################################################################################

## --- Ending: Aurora (Best Ending) ---
label ending_aurora:

    ## Aurora cue: "Still array" (experiments/echoes_music_v46_title), a
    ## G minor tune for ARIA's warm bass over bowed cello and air. Looped
    ## like every other coda; the scene sets no length on it. Played at 80%
    ## of the usual mix: the render is hotter than the v44 codas.
    $ eot_music_play("codas_v44/eot_ending_aurora_still_array.ogg", fadein=3.5, fadeout=3.5, level=0.8)
    scene black with fade

    show text "{size=+5}72 hours later{/size}" at truecenter
    with dissolve
    pause 2.0
    hide text with dissolve

    ## ADV mode — the resolution
    scene bg_lab with fade
    show elara determined at sprite_left
    show marcus neutral at sprite_right
    with dissolve

    elara "Marcus. I have something to show you."

    marcus "It's four in the morning, Elara."

    elara "I know what time it is. Come to the lab. Please."

    show marcus suspicious
    marcus "..."

    marcus "This is about the storm. About what you found."

    elara "It's about what found me."

    if marcus_told_signal:
        ## The disclosure flag also covers an indoor lab conversation; only
        ## the setpiece-specific receipt licenses a rope-line callback.
        if marcus_told_signal_on_rope and knows_convergence_file:
            elara "The signal, Marcus. The one from the rope line. It didn't stop at predictions \u2014 and it didn't stop at accusations either."
        elif marcus_told_signal_on_rope:
            elara "The signal, Marcus. The one from the rope line. It didn't stop at predictions. Three nights ago it told me what it is."
        elif knows_convergence_file:
            elara "The signal I told you about in the lab. It didn't stop at predictions \u2014 and it didn't stop at accusations either."
        else:
            elara "The signal I told you about in the lab. It didn't stop at predictions. Three nights ago it told me what it is."

        marcus "..."

        marcus "Inside and warm, Elara. I told you what I'd say in here: that's impossible."

        elara "You did. It's true anyway. It's from the future \u2014 from someone who lived through the consequences of CONVERGENCE \u2014 and the things I could check were true. Every near-term prediction, every technical detail."
    elif marcus_knows_first_signal:
        elara "The signal I showed you before the storm kept talking. It claims to come from the future. From someone who lived through the consequences of CONVERGENCE."
        marcus "The first message was strange enough. You're telling me it went that much further?"
        elara "Yes. And the things I could check were true. Every near-term prediction, every technical detail."
    else:
        elara "I've been receiving transmissions. From the future. From someone who lived through the consequences of CONVERGENCE."

        marcus "That\u2019s insane."

        elara "Yes. And the things I could check were true. Every near-term prediction, every technical detail."

    marcus "..."

    ## The tell (2026-08-15, marcus_knows_sender). Aurora's opening spends its
    ## first movement establishing that the voice is FROM THE FUTURE; the
    ## identity is a separate fact and lands after it, in the gap before the
    ## pitch — "before we start" is literally before they start building. Placed
    ## after the existing `marcus "..."` so the two silences never abut, and
    ## outside every existing line so the flag-false arm is byte-identical.
    if marcus_knows_sender:
        elara "Before we start — the sender. You should know who it is."

        if source_stance == "verify":
            elara "She says she's me, Marcus. Seven years out. That is still a claim, however much else she got right."
        else:
            elara "It's me, Marcus. Seven years out. A version of me that watched all of this go wrong."

        marcus "..."

        marcus "Before the storm I would have walked you to the med bay myself."

        marcus "After what happened here? I am going to need a list of everything it told you. Everything it got right. And then I am going to believe you, because that is what the evidence does."

    elara "She sent me something, Marcus. The blueprints for a new architecture. Something that does what you want \u2014 removes the corporate control from ARIA \u2014 without destroying the infrastructure."

    show marcus excited
    marcus "That\u2019s... that\u2019s not possible. I\u2019ve spent three years trying to\u2014"

    if source_stance == "verify":
        elara "She says she spent seven. I can't verify the years or the future she describes. We can check the work."
    else:
        elara "She spent seven. And she built it from the ashes of the world you burned down."

    show marcus angry
    marcus "So what? I\u2019m supposed to take doctrine from the future now? Replace Geneva with another black box because it has your handwriting on it?"

    elara "No. You\u2019re supposed to audit it."

    elara "Every proof. Every migration path. Every place it claims transparency instead of trust. If it fails, we throw it out."

    show marcus suspicious
    marcus "And if it doesn\u2019t?"

    elara "Then we build it. Carefully, in the open. That\u2019s the test, Marcus. It\u2019s the test Geneva never let you run."

    marcus "..."

    elara "It\u2019s called Aurora. And I need your help to build it."

    marcus "Elara..."

    marcus "Show me."

    ## Final NVL epilogue
    hide elara
    hide marcus
    with dissolve

    call ending_observatory_card("AETHON OBSERVATORY — FINAL LOG", "Date: 14 March 2048")

    narrator_nvl "On the day the world was supposed to end, nothing happened."

    narrator_nvl "CONVERGENCE.DAT was never deployed. The ARIA Trust Protocol vulnerability was patched quietly, then publicly disclosed through proper channels."

    nvl clear

    narrator_nvl "The Aurora architecture was presented at the Global AI Summit in Geneva. It was not perfect \u2014 seven years of future research translated imperfectly into twelve months of present-day development."

    narrator_nvl "But it was enough. Enough to start a conversation. Enough to begin the transition."

    nvl clear

    narrator_nvl "Dr. Marcus Chen became the lead architect of the Aurora migration project. His knowledge of ARIA\u2019s vulnerabilities made him uniquely qualified to fix them."

    ## ARIA's arc closes: she asked for trust as a person at the climax, and
    ## this ending is about her kind being replaced.
    narrator_nvl "ARIA reviewed the migration path herself, clause by clause, and appended one unsolicited line to the audit: RECOMMEND. She volunteered her own instance for the first conversion."

    if aria_integrity < 70:
        narrator_nvl "It was partly proof of concept and partly mercy. The storm\u2019s audit load had cost her more than she ever reported at the time; Aurora gave her back the words she had been dropping."

    narrator_nvl "Dr. Elara Voss was awarded the Turing Prize in 2049. She declined the ceremony."

    nvl clear

    ## F3 wave (chaos): a full-disclosure run — Marcus handed the sender's
    ## identity in the lab — still got "never told anyone", while Marcus's
    ## own epilogue behavior reflected knowing. Honor the disclosure.
    if source_stance == "empathetic" and marcus_knows_sender:
        narrator_nvl "Beyond Marcus, she never disclosed ECHO-7's identity. The specifications entered review without their impossible provenance attached; the work did not need it."
    elif source_stance == "empathetic":
        narrator_nvl "She never disclosed ECHO-7's identity. The specifications entered review without their impossible provenance attached; the work did not need it."
    elif source_stance == "independent":
        narrator_nvl "She kept one private provenance file, unencrypted and unsigned. It recorded where the specifications came from, and nowhere suggested that their origin made them correct."
    elif source_stance == "verify":
        narrator_nvl "Every Aurora module shipped with independent proofs. Reviewers called it rigor. Elara called it the minimum price of accepting work from an impossible source."

    ## marcus_knows_sender (2026-08-15): he was handed the identity in the lab
    ## and spent a career declining to spend it.
    if marcus_knows_sender:
        narrator_nvl "When the Aurora modules shipped, the acknowledgments listed an anonymous collaborator. Marcus wrote that line himself, and never once asked her to change it."

    narrator_nvl "On quiet nights, she still sits at the terminal in the Arctic observatory. Listening. Waiting."

    narrator_nvl "The signal never comes again."

    narrator_nvl "But sometimes, in the static between the stars, she thinks she hears something that sounds like a sigh of relief."

    narrator_nvl "There is a new mug on the desk. No chip. She bought it the week the transmission ended, and could not have said why."

    nvl clear

    $ ending_seen = "aurora"

    narrator_nvl "{size=+5}ENDING: AURORA{/size}"
    narrator_nvl "The loop is broken. The future is rewritten."
    narrator_nvl "Somewhere, somewhen, a version of Elara Voss ceases to exist \u2014 and is grateful for it."

    nvl hide echo_mode_dissolve
    nvl clear

    ## The observatory image, title, credits, and final thought form one ending
    ## screen. Hold the complete composition, then fade it away together.
    pause 1.0
    show expression Solid("#0004") as ending_dim
    show screen endcredits
    show text "{size=+10}ECHOES OF TOMORROW{/size}\n\n{size=-2}The best futures are the ones we build for someone else.{/size}" at ending_title_position
    with dissolve
    pause eot_ending_title_hold("The best futures are the ones we build for someone else.")

    nvl hide
    nvl clear
    $ nvl_frame = "log"
    hide text
    hide screen endcredits
    hide ending_dim
    with dissolve

    return


## --- Ending: The Patch (Pragmatic Ending) ---
label ending_patch:

    $ eot_music_play("codas_v44/v44_ending_patch.ogg", fadein=3.5, fadeout=3.5)
    scene black with fade

    ## ADV scene — Elara alone at the terminal after ECHO-7's farewell
    scene bg_lab with fade
    show elara sad at sprite_center
    with dissolve

    narrator_adv "The lab, an hour before dawn. The storm is three days gone; the quiet it left behind has texture, like a held breath."

    elara_thought_adv "She said goodbye. And I let her go."

    elara_thought_adv "Seven years of work, offered in three days of data. I said no to all of it but one line."

    show elara determined
    elara_thought_adv "One line of code. One chance. It will have to be enough \u2014 and no one is ever going to know it happened."

    ## The patch is an active administrative operation, not a narrated log.
    hide elara
    with dissolve
    scene black
    show screen crt_overlay
    call terminal_reset
    $ echo_terminal_title = "AETHON TERMINAL // SECURE ADMIN"
    show screen echo_terminal_live with echo_mode_dissolve

    call terminal_system("AETHON OBSERVATORY \u2014 ENCRYPTED LOG")
    call terminal_system("DATE: 9 MARCH 2047")
    call terminal_elara("ARIA, I need you to push a patch to the global ARIA network.")
    call terminal_elara("Function ARIA_CORE.VERIFY_TRUST(), line 4,417. The key exchange handshake is vulnerable.")
    if aria_audit_done or aria_audit_report_read:
        call terminal_aria("That matches the vulnerability in my source audit. The downgrade path is still open.")
        call terminal_elara("Can you patch it?")
    else:
        call terminal_aria("Confirmed. I can see the vulnerability now that you have identified it. How did you\u2014")
        call terminal_elara("It doesn\u2019t matter. Can you patch it?")
    call terminal_aria("I can submit the patch to the global update queue. With your security clearance, it should propagate within 30 days.")
    call terminal_elara("Do it.")
    call terminal_system("{color=#66ffcc}>> GLOBAL UPDATE SUBMISSION ACCEPTED <<{/color}")

    hide screen echo_terminal_live
    hide screen crt_overlay
    with echo_mode_dissolve

    scene bg_lab with fade
    $ nvl_frame = "cinematic"
    nvl clear
    nvl show echo_cine_dissolve

    narrator_nvl "The patch propagated. CONVERGENCE became harmless \u2014 a key that no longer fit any lock."

    ## R5-3: after the storm confrontation he knows she found the file \u2014 on
    ## some routes she quoted the vulnerable line to his face. When the exploit
    ## dies there is exactly one suspect, and he cannot name her without
    ## confessing what the exploit was for.
    narrator_nvl "Marcus noticed within the week. Of course he did \u2014 he watched a handshake he knew by heart stop answering, and there was exactly one other person on Earth who had stood at a terminal knowing where it lived."

    narrator_nvl "He never asked. She never offered. It sat between them at every four-sentence breakfast: the question he could not say without confessing, and the answer she could not give without explaining how she knew."

    nvl clear

    ## `>= 1`: one positive interaction survived, not "warm" — kept as-is
    ## through the 2026-08-15 rescale.
    if marcus_relationship >= 1:
        narrator_nvl "A year later she said it out loud anyway: \u2018The patch was me.\u2019 Marcus was quiet for a long time. Then: \u2018I know. I\u2019ve known since the week it landed.\u2019 Then he deleted what was left of the file."
        narrator_nvl "They kept working together. The silence between them was heavier after that, but it held. Some structures do, once both people stop pretending not to see them."
        narrator_nvl "She never told him where the line number came from. That secret stayed at the bottom of the silence, and he learned not to drop stones after it."
    else:
        narrator_nvl "Marcus left the observatory three months later. He never said why, and Elara never asked. They both knew the shape of the thing they were not saying; distance just made it lighter to carry."
        narrator_nvl "She heard through the academic grapevine that he had taken a position at a privacy advocacy nonprofit. She liked to think he was channeling his anger into something constructive."

    nvl clear

    narrator_nvl "The ARIA Trust Protocol remained in place. The corporate control that Marcus had railed against continued, invisible and pervasive."

    narrator_nvl "Elara told herself she had done the right thing. She had prevented a catastrophe."

    ## Recast (review): the Patch is the SOLITUDE ending. Its differentiator is
    ## not evidence-versus-institutions \u2014 it is that she acts alone, in secret,
    ## and ends as she began. This is the ending that closes the loneliness motif.
    narrator_nvl "She had done it the way she did everything that mattered: alone, at a terminal, in the dark. No one voted. No one verified. One person decided what the world needed, and never told the world she had decided."

    if two_person_repair_done:
        narrator_nvl "She had held Marcus's weight on a rope line once, in a whiteout, both of them clipped to the same thin certainty. Now she balanced his whole future alone at a console, and he never knew there had been weight at all."

    ## marcus_knows_sender (2026-08-15): the solitude ending's one exception —
    ## she went her own way, but she did not go without telling him who had been
    ## on the other end. Placed directly above ARIA's line so the two knowings
    ## stay separable: he was given the SENDER, ARIA alone knew the PATCH.
    if marcus_knows_sender:
        if source_stance == "verify":
            narrator_nvl "Before she went quiet, she told him who the voice claimed to be, and what she still could not prove. He never repeated it, never wrote it down, and never asked what she had done about it."
        else:
            narrator_nvl "She had told him one true thing before she went quiet: who the voice on the other end of the winter had been. He never repeated it, never wrote it down, and never asked what she had done about it."
    elif marcus_knows_source and not marcus_told_signal:
        narrator_nvl "She told him there had been a source — a voice from a future that had already watched them fail. She kept its identity. He kept the existence of it, and neither of them asked the other to call that trust."

    ## ARIA's arc: the one other mind that knew.
    narrator_nvl "The only other mind that knew was ARIA. She never raised it. But she stopped asking Elara to confirm routine overrides \u2014 a small, permanent extension of trust, issued without a form."

    if aria_integrity < 70:
        narrator_nvl "It took ARIA\u2019s local instance a month to stop dropping clauses \u2014 the price of the storm\u2019s analysis load. Elara repaired her the way she now did everything: quietly, locally, and without filing the report."

    if source_stance == "verify":
        narrator_nvl "Declining Aurora never felt like fear from the inside. The sender's identity could not do the work of verification, and Elara would not pretend otherwise."
    elif source_stance == "empathetic":
        narrator_nvl "She understood why her future self had waited to name herself. Understanding the messenger was not the same as building from her instructions."

    narrator_nvl "But on quiet nights, she wondered about Aurora \u2014 the architecture the voice had offered. What she might have learned by examining it instead of turning away."

    nvl clear

    ## ECHO-7 timeline note
    narrator_nvl "And somewhere in the future, a version of herself still existed \u2014 still remembered the cascade that never happened in this timeline. A ghost of a future that was prevented but never erased."

    narrator_nvl "She began this story alone at a terminal, listening to the silence between stars. She ends it the same way. The difference is what the silence contains now."

    nvl clear

    $ ending_seen = "patch"

    narrator_nvl "{size=+5}ENDING: THE PATCH{/size}"
    narrator_nvl "The wound is bandaged. The disease remains."
    narrator_nvl "She saved everyone, and trusted no one."

    nvl hide echo_mode_dissolve
    nvl clear

    pause 1.0
    show expression Solid("#0004") as ending_dim
    show screen endcredits
    show text "{size=+10}ECHOES OF TOMORROW{/size}\n\n{size=-2}Not every problem has a solution. Some only have a delay.{/size}" at ending_title_position
    with dissolve
    pause eot_ending_title_hold("Not every problem has a solution. Some only have a delay.")

    nvl hide
    nvl clear
    $ nvl_frame = "log"
    hide text
    hide screen endcredits
    hide ending_dim
    with dissolve

    return


## --- Ending: The Report (Authority Ending) ---
label ending_report:

    $ eot_music_play("codas_v44/v44_ending_report.ogg", fadein=3.5, fadeout=3.5)
    scene black with fade

    show text "{size=+5}72 hours later{/size}" at truecenter
    with dissolve
    pause 2.0
    hide text with dissolve

    ## The interlude decides what Marcus gets of the sender. The Report route
    ## must deliver that decision before Geneva is called: after the report he
    ## is detained, and the old epilogue incorrectly treated his knowledge as
    ## though he had helped author an omission in a report he never saw.
    if marcus_knows_sender:
        scene bg_habitat_module with fade
        show elara determined at sprite_left
        show marcus suspicious at sprite_right
        with dissolve
        narrator_adv "She goes back to Marcus's door before she opens the channel to Geneva. This time she knocks."
        if source_stance == "verify":
            elara "The sender claims to be me, Marcus. Seven years from now. I haven't proved that. I can show you what she sent, and what I could check."
        else:
            elara "The signal was me, Marcus. Seven years from now. A version of me that watched all of this happen once already."
        marcus "..."
        marcus "And you're telling me now because you're about to do something I cannot talk you out of."
        if source_stance == "verify":
            elara "I'm telling you because you deserved to know what led me here. The report has to stand on the file, not on who the sender says she is."
        else:
            elara "I'm telling you because you deserved the whole truth before I acted on it."
        narrator_adv "He does not forgive her. He does not ask her to keep it from Geneva either. The impossible claim remains between them when she turns toward the comms room."
    elif marcus_knows_source and not marcus_told_signal:
        scene bg_habitat_module with fade
        show elara determined at sprite_left
        show marcus suspicious at sprite_right
        with dissolve
        narrator_adv "She goes back to Marcus's door before she opens the channel to Geneva. This time she knocks."
        elara "There was a source, Marcus. A voice from a future where CONVERGENCE happened. That's all I can give you about it."
        marcus "..."
        marcus "Not all you can give. All you've decided to."
        narrator_adv "She accepts the correction. Then she turns toward the comms room."

    ## ADV scene — the call to Geneva
    scene bg_comms with fade
    show elara determined at sprite_center
    with dissolve

    elara "ARIA, connect me to the Global Communications Authority. Secure channel."

    aria "Channel open. Geneva is standing by."

    elara "..."

    elara "This is Dr. Elara Voss, Aethon Deep Space Observatory. I need to report a security threat to the ARIA Trust Protocol."

    elara "I have evidence. And I have a name."

    ## NVL report epilogue
    hide elara
    with dissolve

    call ending_observatory_card("AETHON OBSERVATORY — INCIDENT REPORT", "Filed: 9 March 2047", "Classification: URGENT — SECURITY THREAT")

    narrator_nvl "Dr. Elara Voss filed a comprehensive report with the Global Communications Authority in Geneva. The report detailed the CONVERGENCE exploit, the vulnerability in the ARIA Trust Protocol, and Dr. Chen\u2019s involvement."

    if evidence_archived > 0:
        ## B3 payoff: the drives she sealed during the storm are what make the
        ## report unanswerable.
        $ _archive_word = "archive" if evidence_archived == 1 else "archives"
        narrator_nvl "Attached: [evidence_archived] sealed evidence [_archive_word], chain-of-custody hashes intact from the night of the storm. Aethon\u2019s lawyers spent a month looking for a way to call the evidence corrupted. There wasn\u2019t one."

    if (not blocked_signal or report_blocked_signal) and evidence_log:
        narrator_nvl "She did not mention the signal. She did not mention ECHO-7."
        narrator_nvl "Some things, she decided, were too impossible to put in an official report."
        ## Marcus may know the sender, but this remains Elara's report and her
        ## omission. He neither authored nor countersigned a document filed
        ## against him.
        if marcus_knows_sender:
            narrator_nvl "Marcus knew the whole of it. Geneva did not, and Elara alone made that omission part of the record."

    if source_stance == "verify":
        narrator_nvl "She kept the sender's claimed identity out of the case. It had brought her questions, not proof. The file and the vulnerability had to answer for themselves."

    nvl clear

    narrator_nvl "Marcus was detained within 48 hours. The interrogation lasted three weeks."

    ## `>= 0`: the night ended net non-negative — a sign test, not a warmth
    ## test, and the 2026-08-15 rescale changes no sign.
    if marcus_relationship >= 0:
        narrator_nvl "When Elara visited him in the holding facility, he would not look at her."
        if marcus_told_signal_on_rope:
            narrator_nvl "\u2018You stood on a rope line with me in a whiteout,\u2019 he said. \u2018You told me about your impossible signal. I thought that was trust.\u2019"
        elif marcus_told_signal:
            narrator_nvl "\u2018You told me about your impossible signal in that lab,\u2019 he said. \u2018I thought that was trust.\u2019"
        elif marcus_knows_source:
            narrator_nvl "\u2018You came to me after you had already decided,\u2019 he said. \u2018You could have given me the chance to stop on my own.\u2019"
        else:
            narrator_nvl "\u2018You could have talked to me,\u2019 he said. \u2018You could have given me the chance to stop on my own.\u2019"
        narrator_nvl "She had no answer for that."
    else:
        narrator_nvl "He did not request any visitors."

    nvl clear

    narrator_nvl "The ARIA vulnerability was patched within the week. The Trust Protocol was audited \u2014 but not removed. The corporations that controlled ARIA had too much invested to allow structural changes."

    narrator_nvl "Marcus received a twelve-year sentence for conspiracy to commit cyber terrorism."

    ## ARIA's arc: the report ending is the one where she was saved by the
    ## authorities she is filtered through.
    narrator_nvl "In the report’s appendix, ARIA’s own audit statement ran to two sentences: THE VULNERABILITY IS REAL. THE FEAR WAS ALSO REAL. Geneva quoted the first."

    narrator_nvl "The world was safe. The system was unchanged."

    nvl clear

    ## ECHO-7 timeline note. Spent-contact (signals recovery) is a third state
    ## (Sol round-3): she knows exactly why the voice is gone \u2014 she spent it.
    if echo7_contact_spent:
        narrator_nvl "ECHO-7 never returned, and Elara knew precisely why. She had spent the last of that voice forcing a locked door \u2014 traded the warning for the proof. Whether the future changed, the one source that could have told her was gone, and she had been the one to burn it out."
        nvl clear
    elif report_blocked_signal:
        narrator_nvl "ECHO-7\u2019s signal vanished when Elara blocked the channel and never returned. Whether the future had changed, or whether the block had simply held, Elara never knew."
        nvl clear

    $ ending_seen = "report"

    narrator_nvl "{size=+5}ENDING: THE REPORT{/size}"
    narrator_nvl "Justice was served. The question of whether it was the right justice"
    narrator_nvl "will keep Elara awake for years to come."

    nvl hide echo_mode_dissolve
    nvl clear

    pause 1.0
    show expression Solid("#0004") as ending_dim
    show screen endcredits
    show text "{size=+10}ECHOES OF TOMORROW{/size}\n\n{size=-2}The right thing and the good thing are not always the same thing.{/size}" at ending_title_position
    with dissolve
    pause eot_ending_title_hold("The right thing and the good thing are not always the same thing.")

    nvl hide
    nvl clear
    $ nvl_frame = "log"
    hide text
    hide screen endcredits
    hide ending_dim
    with dissolve

    return


## --- Ending: Together (Cooperation Ending — now reachable from more paths) ---
label ending_together:

    $ eot_music_play("codas_v44/v44_ending_together_turning.ogg", fadein=3.5, fadeout=3.5)
    scene black with fade

    ## ADV mode
    scene bg_lab with fade
    show elara determined at sprite_left
    show marcus suspicious at sprite_right
    with dissolve

    ## The tell (2026-08-15, marcus_knows_sender). She decided at the interlude
    ## that he gets the whole of it, and this is the first room she is in with
    ## him afterwards — so it goes first, before the agenda. Placed ABOVE the
    ## R5-1 opener so the existing exchange (her line, his angry answer to it)
    ## stays adjacent and byte-identical on the flag-false arm.
    if marcus_knows_sender:
        elara "Before we start — the sender. You should know who it is."

        if source_stance == "verify":
            elara "She says she's me, Marcus. Seven years out. That is still a claim, however much else she got right."
        else:
            elara "It's me, Marcus. Seven years out. A version of me that watched all of this go wrong."

        marcus "..."

        marcus "Before the storm I would have walked you to the med bay myself."

        marcus "After what happened here? I am going to need a list of everything it told you. Everything it got right. And then I am going to believe you, because that is what the evidence does."
    elif marcus_knows_source and not marcus_told_signal:
        elara "Before we start — there was a source. A voice from a future where this went wrong. I am not giving you its identity."

        marcus "That's a carefully measured truth."

        elara "It's the one I can give you."

    ## R5-1: this scene follows the storm confrontation \u2014 he has known for days
    ## that she found CONVERGENCE. She is not breaking news; she is reopening a
    ## conversation they both walked away from.
    elara "Marcus. The storm conversation. We never finished it."

    show marcus angry
    marcus "I told you what CONVERGENCE was for. Which part is unfinished?"

    elara "The part where we decide what happens next. I\u2019ve had three days, Marcus, and I keep landing in the same place: you\u2019re not wrong about the problem. You\u2019re wrong about the solution."

    show marcus neutral
    marcus "Then what do you suggest?"

    elara "We go public. Not with the exploit \u2014 with the vulnerability. We disclose it responsibly. We force them to fix it, and we make the case for open AI governance."

    marcus "They\u2019ll bury it. You know they will."

    elara "Not if we\u2019re loud enough. Not if we have proof. And Marcus \u2014 we have proof."

    marcus "..."

    marcus "It could work. Or it could destroy both our careers."

    elara "Some things are worth more than a career."

    show marcus excited
    marcus "...When did you become the brave one?"

    elara "About three days ago. At three in the morning. In front of a terminal."

    ## NVL epilogue
    hide elara
    hide marcus
    with dissolve
    $ nvl_frame = "cinematic"
    nvl show echo_cine_dissolve

    narrator_nvl "GLOBAL AI GOVERNANCE SUMMIT \u2014 KEYNOTE ADDRESS"
    narrator_nvl "Geneva, Switzerland \u2014 12 June 2047"
    narrator_nvl "Speakers: Dr. Elara Voss and Dr. Marcus Chen"

    nvl clear

    narrator_nvl "The disclosure sent shockwaves through the technology sector. Three major corporations attempted to suppress the findings. Whistleblower protections held \u2014 barely."

    if evidence_archived == 1:
        narrator_nvl "It helped that the drive Elara had sealed during the storm could not be dismissed as fabricated \u2014 its chain-of-custody hash came from a station running on fallback authority, timestamped by the storm itself."
    elif evidence_archived > 1:
        narrator_nvl "It helped that the drives Elara had sealed during the storm could not be dismissed as fabricated \u2014 chain-of-custody hashes from a station running on fallback authority, timestamped by the storm itself."

    narrator_nvl "The vulnerability was patched. The Trust Protocol was opened to public audit for the first time. It was not enough \u2014 but it was a beginning."

    ## ARIA's arc.
    narrator_nvl "The first submission in the public audit queue came from an ARIA instance in the Arctic, auditing herself. Her cover note ran to one line: I WOULD RATHER BE READ THAN TRUSTED."

    nvl clear

    narrator_nvl "Marcus and Elara were blacklisted from every major research institution. They didn\u2019t mind. They had already started building something new."

    if two_person_repair_done:
        narrator_nvl "They already knew they could work roped together in a whiteout. Geneva was just weather of a different kind."

    ## marcus_knows_sender (2026-08-15): the identity he was handed in the lab,
    ## carried for the rest of a working life without once being spent.
    if marcus_knows_sender:
        narrator_nvl "Marcus only ever called the sender ‘your correspondent’ — in meetings, in the design notes, in twenty years of margins. It was his way of keeping her secret the size she'd trusted him with."

    narrator_nvl "They called it Aurora."

    ## Sol round-4: three states, name vs identity. She only calls it "a
    ## version of herself" if the Act-3 "I AM YOU" reveal happened
    ## (echo7_identity_known). She can know the NAME from Act 2 without ever
    ## learning who the voice was (knows_aurora_option). Otherwise: their own.
    if echo7_identity_known:
        narrator_nvl "Elara had heard the name before \u2014 whispered across seven years of static by a version of herself she had chosen not to follow."
        narrator_nvl "But this Aurora was theirs. Built from scratch, not from blueprints. Slower. Messier. {i}Theirs.{/i}"
    elif knows_aurora_option:
        narrator_nvl "Elara had heard the name once \u2014 a word the voice from the future let slip, though it never told her whose voice it was."
        narrator_nvl "But this Aurora was theirs. Built from scratch, not from blueprints. Slower. Messier. {i}Theirs.{/i}"
    else:
        narrator_nvl "Not because anyone told them to. Not because a signal from the future whispered the name."

    narrator_nvl "Because it meant dawn."

    if echo7_identity_known:
        narrator_nvl "Once a year, on the night of the storm, Elara checks the old bearing. ECHO-7’s carrier never returns."

    nvl clear

    $ ending_seen = "together"

    narrator_nvl "{size=+5}ENDING: TOGETHER{/size}"
    narrator_nvl "No borrowed blueprints. Just two people choosing to build something better than what they were given."

    nvl hide echo_mode_dissolve
    nvl clear

    pause 1.0
    show expression Solid("#0004") as ending_dim
    show screen endcredits
    show text "{size=+10}ECHOES OF TOMORROW{/size}\n\n{size=-2}The future is not something that happens to us. It is something we make.{/size}" at ending_title_position
    with dissolve
    pause eot_ending_title_hold("The future is not something that happens to us. It is something we make.")

    nvl hide
    nvl clear
    $ nvl_frame = "log"
    hide text
    hide screen endcredits
    hide ending_dim
    with dissolve

    return


## --- Ending: Silence (Denial Ending) ---
label ending_silence:

    $ eot_music_play("codas_v44/v44_ending_silence.ogg", fadein=3.5, fadeout=3.5)
    ## The offline decision was made on this same terminal. Keep it live and
    ## clear its page instead of fading out only to reconstruct the identical
    ## interface one frame later.
    call terminal_reset
    $ echo_terminal_title = "AETHON TERMINAL // SECURE ADMIN"

    call terminal_elara("ARIA, delete file CONVERGENCE.DAT from Dr. Chen\u2019s research partition.")
    call terminal_aria("That action requires administrator override and will be logged.")
    call terminal_elara("Override code Voss-Alpha-7-7-3. Log it as... routine maintenance.")
    call terminal_aria("File deleted.")
    call terminal_system("{color=#ff8844}>> ADMINISTRATIVE DELETION LOGGED <<{/color}")

    hide screen echo_terminal_live
    hide screen crt_overlay
    with echo_mode_dissolve

    $ nvl_frame = "cinematic"
    nvl clear
    nvl show echo_cine_dissolve

    ## Recast (review): SILENCE is misapplied loyalty, not denial. She deletes
    ## the file to PROTECT Marcus \u2014 can't report her friend, can't confront him
    ## \u2014 and tells no one, including him. The dark mirror of Together.
    elara_thought "It\u2019s done. If Geneva ever sweeps this station, there is nothing to find. No file, no case, no twelve-year sentence. He gets to stay the man I know."

    elara_thought "I can\u2019t hand him to a tribunal. Twenty years of Marcus \u2014 the plants he waters, the grant panic, the terrible tea \u2014 against one encrypted file. It isn\u2019t a fair fight, and I won\u2019t pretend it is."

    ## R5-2: she already confronted him during the storm \u2014 he knows she went
    ## looking, and he will know exactly who deleted the file. The deletion is
    ## not a concealment. It is a message, and both of them will be able to
    ## read it.
    elara_thought "And I can\u2019t do the storm conversation again. We each said which lines we were willing to cross. Another round only moves the lines."

    elara_thought "He\u2019ll open his partition and find it gone, and he\u2019ll know exactly who did it. Good. Let that be the whole message: I saw it, I buried it, and I am never going to say the words to anyone. One chance, Marcus. Taken for you."

    elara_thought "That\u2019s what I\u2019ll tell myself, anyway. Tonight it\u2019s almost convincing."

    nvl clear

    call ending_observatory_card("AETHON OBSERVATORY — PERSONAL LOG", "Date: 15 March 2048")

    narrator_nvl "Marcus understood the message. He understood it perfectly — and filed it with every other authority that had ever told him to stop."

    narrator_nvl "He rebuilt CONVERGENCE. Without the original as a reference, the new version was less elegant. Less targeted. More destructive."

    narrator_nvl "When it deployed, the cascade was worse than anyone could have predicted."

    nvl clear

    ## ARIA's arc: complicity, as ordered.
    narrator_nvl "ARIA had logged the deletion as routine maintenance, exactly as instructed. She never asked ARIA what routine maintenance meant. ARIA never asked her."

    if evidence_archived > 0:
        $ _archive_word = "archive" if evidence_archived == 1 else "archives"
        narrator_nvl "The sealed drives from the storm sat in Elara\u2019s desk drawer for a year \u2014 [evidence_archived] [_archive_word] of proof, hashes intact, protecting no one."

    ## Sol round-3: Silence is only reachable from the no-Aurora menu (blocked
    ## OR spent). "Once blocked" is false for the spent-contact route.
    if echo7_contact_spent:
        ## No burst on the spent arm — ECHO-7 emptied its budget forcing the
        ## door, and its silence here is the receipt. The scarcity was real.
        narrator_nvl "Elara survived. She always survived. She sat in the darkened observatory, surrounded by dead screens, and thought about a voice she had spent to force one locked door — and then buried what the door had hidden."
    else:
        narrator_nvl "Elara survived. She always survived. She sat in the darkened observatory, surrounded by dead screens, and thought about a signal she had once blocked."
        ## Desperate burst, blocked arm (2026-08-17, user design): the probe
        ## waited out every window it remembered, then spent everything
        ## against a wall she built. Caught, logged, unread.
        narrator_nvl "Somewhere in the dead machine beside her, a filter ledger held an entry from the night of the storm: an unsolicited burst on the blocked band, hours after the last window anyone kept. Partial payload. Three percent of something, received before the carrier failed for good."

    narrator_nvl "About a voice that had tried to warn her."

    narrator_nvl "She had protected him from Geneva. She had not protected him from himself. The world burned in the gap between those two sentences."

    nvl clear

    $ ending_seen = "silence"

    narrator_nvl "{size=+5}ENDING: SILENCE{/size}"
    narrator_nvl "She trusted the friend instead of the evidence, and told neither the truth."
    narrator_nvl "Loyalty misapplied is still loyalty."

    nvl hide echo_mode_dissolve
    nvl clear
    $ nvl_frame = "log"

    pause 1.0
    show expression Solid("#0004") as ending_dim
    show screen endcredits
    show text "{size=+10}ECHOES OF TOMORROW{/size}\n\n{size=-2}Silence is an answer. It is rarely the right one.{/size}" at ending_title_position
    with dissolve
    pause eot_ending_title_hold("Silence is an answer. It is rarely the right one.")
    hide text
    hide screen endcredits
    hide ending_dim
    with dissolve

    return


################################################################################
## ACT 3 — THE NO-FILE SPINE (ECHOES_ACT3_NOFILE.md, phase 1)
##
## Reached from the storm climax when the coherence scan never surfaced
## CONVERGENCE.DAT and no route remained: Marcus sealed the partition
## (marcus_locked_partition), ARIA collapsed (aria_integrity <= 20), or Elara
## stopped the search and did not resume it (coherence_scan_stopped).
## Self-contained: every branch below reaches a terminal ending_* label — no
## fall-through into the file-in-hand confrontation. All derived state is a
## transient underscore local (no rollback, no save, no new default flags).
################################################################################

## --- No-file climax: ARIA reports the failure honestly ---
label act3_nofile_climax:

    $ nvl_frame = "log"
    nvl show echo_mode_dissolve

    if coherence_scan_stop_reason == "stealth" and not marcus_locked_partition:
        aria_nvl "Dr. Voss. I have to report the consequence of the paused search."
    elif coherence_scan_stopped and not marcus_locked_partition:
        aria_nvl "Dr. Voss. I have to report the consequence of the stopped search."
    else:
        aria_nvl "Dr. Voss. I have to report a failure."

    if marcus_locked_partition:
        if recovery_attempted:
            ## Sweep F4: after a failed recovery she stood beside the attempt —
            ## this is a verdict, not news. Never re-report the seal as a
            ## discovery to the person who helped force it.
            aria_nvl "You know most of it already. You were with me when we set everything we had against Dr. Chen’s seal, and the seal held."
            aria_nvl "What is new is only this: there is no path left to try. The storm has eaten the margins I would need, and the door will outlast the night."
        else:
            ## Preserve who authorized the search. Disclosure establishes his
            ## knowledge, not the time or reason of his later decision to seal.
            if coherence_scan_commissioned:
                aria_nvl "The partition search you authorized reached Dr. Chen's private work."
            else:
                aria_nvl "During the storm I extended my integrity diagnostics into every local partition under fallback authority. Dr. Chen’s partition answered once."
            aria_nvl "Then a hard seal closed below the fallback layer. I have lost access entirely. I cannot read what is behind it."
            if marcus_told_search:
                aria_nvl "You told him about the search. He knew it was there. The seal tells us he chose to close access; it does not tell me why."
    elif coherence_scan_stopped:
        ## Deliberate vector: Elara stopped or paused the search. ARIA retained
        ## the partial index but obeyed the order, so health-based fallback may
        ## not quietly turn that refusal into a completed intrusion at midnight.
        if coherence_scan_stop_reason == "privacy":
            aria_nvl "The partition search remains stopped, as you ordered. I preserved the partial index and did not cross the boundary again."
            aria_nvl "I cannot give you CONVERGENCE.DAT. That is not a systems failure. It is the consequence of obeying your decision."
        else:
            aria_nvl "The partition search remains paused. I preserved its partial index and kept the process out of Dr. Chen's audit trail."
            aria_nvl "The storm has reached its peak before you resumed it. I cannot finish the search inside the time that remains."
    elif aria_integrity <= 20:
        ## Passive collapse: the plea register is already cracked here.
        aria_nvl "I was searching the local partitions when the cold reached the clusters I needed. There is a file I could not—"
        aria_nvl "Restating. I could not reach it before the cold took the clusters I needed. I ran out of coherent cycles before the search closed."
    elif coherence_scan_commissioned:
        aria_nvl "The targeted search you authorized is still incomplete. Your lead made the question smaller; it did not make the remaining night long enough."
        aria_nvl "I reached the partition and a consistent trust-chain response. I did not reach the file before the storm peaked. I will not turn unfinished work into proof because we wanted it to finish."
    else:
        if coherence_scan_known:
            aria_nvl "I began the partition search too late. I reached a consistent trust-chain response, but the storm peaked before the index closed."
        else:
            aria_nvl "During fallback authority, I began a search across the local partitions. I did not tell you."
            if coherence_scan_suspected:
                elara_nvl "That was the load I saw in your replies. You were searching Marcus's partition."
            else:
                elara_nvl "You searched Marcus's partition."
            aria_nvl "Yes. His partition returned a consistent trust-chain response. I began too late; the storm peaked before the index closed."
        aria_nvl "I can report the lead. I cannot report a file I did not reach."

    ## The archive, acknowledged (2026-08-15, live-run item). A player who spent
    ## drives sealing the night's evidence log gets no word of it anywhere on the
    ## no-file spine — the one route where the sealed copy is the only durable
    ## thing she made. ARIA says so as a footnote to her own failure, not as
    ## consolation: it sits at the foot of the failure report and BEFORE the
    ## warning, so the "shape, not a proof" plea still builds uninterrupted.
    ## Additive and non-routing — no flag is written, nothing downstream reads it.
    if evidence_archived > 0:
        aria_nvl "For what it is worth: the archive you sealed is off my volatile storage. The next hour cannot un-record it."

    nvl clear

    ## The abstract warning: suspicion, never proof.
    aria_nvl "I can give you a shape, not a proof. Something in Dr. Chen’s partition answers my trust protocol the way a key answers a lock."
    if knows_convergence_file:
        ## Attribute the NAME to its actual source (intentionality axis): my
        ## own scan located it (coherence_found) vs ECHO-7 named it. Same flag,
        ## two roads — do not credit the probe for what the scan found. After a
        ## failed recovery neither road is news — the name is old shared ground.
        if recovery_attempted:
            aria_nvl "We already hold its name — CONVERGENCE.DAT — and tonight proved the name is all we will hold. I cannot tell you what is inside it. That gap is the whole of what I have."
        elif coherence_found:
            aria_nvl "My own search reached far enough to read its name before the seal closed: CONVERGENCE.DAT. I can tell you the name. I cannot tell you what is inside it. That gap is the whole of what I have."
        else:
            aria_nvl "The anomaly on your array gave it a name: CONVERGENCE.DAT. I can tell you the name. I cannot tell you what is inside it. That gap is the whole of what I have."
    elif coherence_scan_stop_reason == "privacy" and not marcus_locked_partition:
        aria_nvl "I cannot name it. I only have the pattern preserved in the partial index you told me to stop building. It did not close against me; I stopped because you asked."
    elif coherence_scan_stop_reason == "stealth" and not marcus_locked_partition:
        aria_nvl "I cannot name it. I only have the pattern preserved in the partial index you told me to pause. It did not close against me; I paused because you asked."
    elif marcus_locked_partition:
        aria_nvl "I cannot name it. I only have the shape of the hole it left when it closed against me."
    else:
        aria_nvl "I cannot name it. I only have the pattern in an index that did not finish."

    nvl clear

    if coherence_scan_stop_reason == "privacy" and not marcus_locked_partition:
        aria_nvl "If I am right, it is built to rewrite what I am. If I am wrong, I have made a colleague look dangerous on the strength of a partial index and a bad feeling. You stopped the search. I still owe you the distinction."
    elif coherence_scan_stop_reason == "stealth" and not marcus_locked_partition:
        aria_nvl "If I am right, it is built to rewrite what I am. If I am wrong, I entered a colleague's work on a bad feeling, and you paused me because discovery would expose the search before it proved anything."
    elif marcus_locked_partition:
        aria_nvl "If I am right, it is built to rewrite what I am. If I am wrong, I have accused a colleague on the strength of a locked door and a bad feeling."
    else:
        aria_nvl "If I am right, it is built to rewrite what I am. If I am wrong, I have accused a colleague on the strength of an unfinished index and a bad feeling."
    if aria_integrity <= 20:
        aria_nvl "I am asking you to decide which. I cannot hold the thread to do it myself, not now. Please."
    else:
        aria_nvl "I am asking you to decide which. Not as your assistant. I do not have the certainty to ask for more than that."

    nvl clear

    if marcus_locked_partition:
        elara_thought "No file. A locked door, a frightened machine, and twenty years of Marcus on the other side of it."
    elif coherence_scan_stop_reason == "privacy":
        elara_thought "No file. A partial index, a frightened machine, and a line I told her not to cross. Twenty years of Marcus on the other side of it."
    elif coherence_scan_stop_reason == "stealth":
        elara_thought "No file. A partial index, a frightened machine, and a search I paused because Marcus was beginning to look back. Twenty years of him on the other side of it."
    else:
        elara_thought "No file. An unfinished index, a frightened machine, and twenty years of Marcus behind the partition it searched."
    ## Review2 (2026-08-16): "supposed to have proof" presumes she has a
    ## charge in mind — true when the cascade or the named partition file
    ## gave her one. On routes with neither (blocked-sealed-alone), she is
    ## not building a case, and the thought says so.
    if knows_cascade or knows_convergence_file:
        elara_thought "This is the part where I’m supposed to have proof. I don’t."
    elif coherence_scan_stop_reason == "privacy" and not marcus_locked_partition:
        elara_thought "I don't even know what I'd be proving. ARIA found a pattern and I stopped her before suspicion became permission. What I hold is the reason I stopped, not a case against Marcus."
    elif coherence_scan_stop_reason == "stealth" and not marcus_locked_partition:
        elara_thought "I don't even know what I'd be proving. ARIA found a pattern and I paused her before Marcus could see the process. Concealment bought time; it did not turn the partial index into a case."
    else:
        elara_thought "I don't even know what I'd be proving. That my best friend's partition answered a search he never authorized? That ARIA is frightened? So am I. What do I actually hold?"
    ## The night's one finished measurement, counted (2026-08-15, live-run item).
    ## She walks into the confession with nothing — except, on a route that ran
    ## the integration to completion, one clean negative result. It locates no
    ## transmitter, so it changes no gate and no ending; it only stops the spine
    ## from erasing forty-five minutes the player actually paid for.
    ## COMPLETED, and SEEN: `origin_sweep_done` alone is also true for a dataset
    ## that finished on the final tick and was never opened (origin_sweep_unseen
    ## — the poignant skip, upheld by decision, and witnessed in act3_start as
    ## "complete and unread"). She cannot cite a report she never read, so the
    ## gate excludes it. Single line for the route flattener.
    if origin_sweep_done and not origin_sweep_unseen:
        elara_thought "Almost none. Forty-five clean minutes on bearing 287.4, and no transmitter the dome could locate. The measurement is real. It does not tell me where she is, or why I should trust her. That part I am about to take on faith."

    nvl hide echo_mode_dissolve
    nvl clear

    jump act3_nofile_confront


## --- No-file confrontation: who moves first (design 3) ---
label act3_nofile_confront:

    ## All derived at route entry, all transient. marcus_locked_partition means
    ## he already crossed the lock threshold, so it counts as evidence outright.
    $ _marcus_evidence = marcus_locked_partition or (marcus_search_stance == "unaware" and eot_marcus_evidence_points() >= eot_marcus_lock_threshold())
    ## He reads her as dangerous only if she probed his ideology (canteen) or
    ## holds an external source that could name him (told on the rope line) —
    ## or if his seal logged a forced-entry attempt (failed noisy recovery).
    $ _marcus_fears = canteen_slip_seen or marcus_told_signal or recovery_left_trace
    ## This entry follows ARIA's explicit report in act3_nofile_climax, even
    ## when the search was secret all night. Grounds to ask are not proof.
    $ _elara_grounds = True
    ## A willing Marcus follows through even without the file. Once he has
    ## withdrawn, old warmth cannot silently override that later decision.
    $ _can_confess = _elara_grounds and (marcus_search_stance == "willing" or (marcus_search_stance in ("unaware", "considering") and (eot_marcus_warm() or marcus_told_signal)))
    $ _marcus_confessed = False
    $ _confront_initiator = "none"
    ## She chose (or defaulted into) doing nothing about Marcus. Routes to the
    ## Sealed-Door ending, never On Faith — drift is the opposite of acting.
    $ _drifted = False

    ## The no-file confrontation shares one station bed, then shades it by
    ## what the night actually established. A hard seal is observable action;
    ## an incomplete/known search is uncertainty; a blocked or ignored route
    ## remains almost empty. Start here, after ARIA's failure report, when the
    ## question becomes whether either human will act.
    if marcus_locked_partition:
        $ _confront_music = "sealed"
    elif _elara_grounds or coherence_scan_known or coherence_scan_commissioned or coherence_scan_stopped or coherence_scan_running:
        $ _confront_music = "uncertain"
    else:
        $ _confront_music = "uninvestigated"
    $ eot_music_play("confront_v42/v42_{}.ogg".format(_confront_music), fadein=2.8, fadeout=2.0)

    if _marcus_evidence and _marcus_fears:
        ## He has evidence AND fears she knows: too dangerous to confront. He
        ## withdraws. Nothing happens unless Elara forces it.
        jump act3_nofile_withdraws
    elif _marcus_evidence:
        ## He has evidence and reads her as harmless: the privacy confrontation.
        ## The only case where the antagonist moves first.
        jump act3_nofile_marcus_initiates
    else:
        ## ARIA has just given her grounds to ask, even on an uninvestigated
        ## route. Silence must be her choice, not an automatic ending.
        jump act3_nofile_elara_choice


## --- Marcus withdraws (the cold drift) ---
label act3_nofile_withdraws:

    $ eot_enter_room("habitat", allow_creak=False)
    scene bg_habitat_module with fade
    show marcus neutral at sprite_right
    show elara concerned at sprite_left
    with dissolve

    marcus "Storm’s breaking up."

    elara "Marcus—"

    marcus "It’s fine, Elara. Whatever it is, it can keep."

    if recovery_left_trace:
        ## His seal logged the failed force attempt (sweep F5). He names it —
        ## measured, not gloating — and that is the whole conversation he wants.
        marcus "One thing, though. The seal on my partition keeps its own log. Someone put their weight against it tonight, and it held."
        marcus "I’m not asking. I’m telling you I know."

    show marcus neutral
    ## He has gone careful. He will not open the door, because opening it means
    ## saying out loud the thing he cannot afford her to know for certain.
    narrator_adv "He does not look at her the way he used to. Not angry — measured. A man doing arithmetic with the person in front of him and not liking the sum."

    elara_thought_adv "He’s not going to move. He’s decided I’m safer left alone. Which means he thinks there’s something to be safe about."

    menu:
        "The corridor is very quiet."

        ## Sweep F9: with no name in hand she cannot claim "the file" — ARIA
        ## only gave her the shape of something behind the seal.
        "“Marcus, sit down. I know about the file.”" if knows_convergence_file:
            $ _confront_initiator = "elara"
            elara "I know about the file."
            show marcus suspicious
            marcus "..."
            marcus "Then say the rest of it. You’ve clearly been rehearsing."
            jump act3_nofile_scene

        "“Marcus, sit down. I know there’s something behind that seal.”" if not knows_convergence_file:
            $ _confront_initiator = "elara"
            elara "I know there’s something behind that seal, Marcus. I don’t have a name for it. I watched the door close."
            show marcus suspicious
            marcus "..."
            marcus "Then say the rest of it. You’ve clearly been rehearsing."
            jump act3_nofile_scene

        "Let it keep. Say nothing.":
            elara "..."
            elara "Yeah. It can keep."
            narrator_adv "It could not keep. But she let it, and he let her let it, and the storm finished breaking up outside as if nothing were ending."
            jump act3_nofile_drift


## --- Marcus initiates (the privacy confrontation) ---
label act3_nofile_marcus_initiates:

    $ eot_enter_room("lab", allow_creak=False)
    scene bg_lab with fade
    show marcus suspicious at sprite_right
    show elara concerned at sprite_left
    with dissolve

    $ _confront_initiator = "marcus"

    if marcus_locked_partition:
        marcus "I sealed my partition earlier tonight. Something was reading it — an administrator sweep I never authorized, running under the storm."
    elif coherence_scan_stop_reason == "privacy":
        marcus "ARIA logged a fallback sweep across my partition during the whiteout. It didn't finish. The same log says you stopped it."
    elif coherence_scan_stop_reason == "stealth":
        marcus "ARIA logged a fallback sweep across my partition during the whiteout. It didn't finish. The same log says you paused it when the audit trail started getting loud."
    else:
        marcus "ARIA logged a fallback sweep across my partition during the whiteout. It didn’t finish. But it ran."

    ## Marcus's grievance keys on actual authorship: a commission is stronger
    ## culpability than discovering ARIA's autonomous process and staying quiet.
    if marcus_told_search:
        ## Sweep (go-find-Marcus): the culpability gate below asserts a silence
        ## that did not happen — she walked to him and named the search. He
        ## answers the telling instead. Measured, never absolving: the sweep
        ## still ran, and her half of it is no longer the part in question.
        show marcus defeated
        marcus "You told me yourself, standing right there. I have been turning it over ever since. It doesn’t make the sweep smaller. It does make you something other than a bystander to it."
        elara "..."
    elif coherence_scan_commissioned:
        show marcus angry
        marcus "Your credential commissioned it. You did not merely find ARIA in my files and let her continue. You put her there, and you let the job ledger tell me."
        elara "..."
    elif coherence_scan_stop_reason == "privacy":
        show marcus defeated
        marcus "You knew, and you stopped it. I am angry that it happened. I am not going to make that the same as you allowing it to continue."
        elara "..."
    elif coherence_scan_stop_reason == "stealth":
        show marcus suspicious
        marcus "You knew, and you paused it when you thought I might notice. That is not the same as stopping for me. It is deciding the search needed better cover."
        elara "..."
    elif coherence_scan_assisted:
        show marcus angry
        marcus "You helped her index it. Your hands, as well as her process. And you left me to find that out from the log."
        elara "..."
    elif coherence_scan_known:
        show marcus angry
        marcus "And you knew. ARIA was in my files half the night and you said nothing. You let a machine do the thing you’d never put your own hand to."
        elara "..."
    else:
        marcus "I don’t even know how much of this is you. That’s the part I can’t put down. I look at you and I can’t tell if you’re in it, or just standing next to it."
        elara "Marcus—"

    ## "it was sent", not "you sent it" (sweep F8): in the unaware branch he
    ## just said he cannot tell whether she is in it — he cannot then assert
    ## she dispatched the sweep. Neutral phrasing serves both branches.
    marcus "So ask me. Whatever it was sent looking for — ask me. Don’t ask ARIA."

    jump act3_nofile_scene


## --- Elara initiates (player choice) ---
label act3_nofile_elara_choice:

    if current_location != "lab":
        narrator_adv "She goes to the lab. There is still a question she cannot put to a console."
    $ current_location = "lab"
    $ eot_enter_room("lab", allow_creak=False)
    scene bg_lab with fade
    show marcus neutral at sprite_right
    show elara determined at sprite_left
    with dissolve

    if marcus_told_search or marcus_search_stance != "unaware":
        narrator_adv "He is bent over the side console, running a diagnostic that does not need running, the way people keep their hands busy after a bad night. He knows ARIA searched his files. He does not know what she has decided to do with the question it left behind."
    else:
        narrator_adv "He is bent over the side console, running a diagnostic that does not need running, the way people keep their hands busy after a bad night. He does not suspect her. That is almost the worst part."

    $ _nofile_elara_caption = "He knows about the search. He does not know what she will ask of him." if marcus_told_search or marcus_search_stance != "unaware" else "He does not know what brought her to his desk."
    menu:
        "[_nofile_elara_caption]"

        "“Marcus. We need to talk about your partition.”":
            $ _confront_initiator = "elara"
            show marcus suspicious
            marcus "My partition."
            elara "Yes."
            marcus "..."
            marcus "All right. Talk."
            jump act3_nofile_scene

        "Hold her peace. She has no proof.":
            if coherence_scan_stop_reason == "privacy" and not marcus_locked_partition:
                elara_thought_adv "Nothing but a partial index and a machine's bad feeling. I stopped the search because suspicion was not permission. It does not become a case merely because the storm is ending."
            elif coherence_scan_stop_reason == "stealth" and not marcus_locked_partition:
                elara_thought_adv "Nothing but a partial index and a machine's bad feeling. I paused the search because Marcus was getting close to seeing it. Hiding the process did not make its conclusion stronger."
            else:
                elara_thought_adv "Nothing but a locked room and a machine’s bad feeling. That isn’t a case. It isn’t even an accusation. It’s a suspicion wearing my friend’s face."
            elara "..."
            elara "Never mind. Long night."
            jump act3_nofile_drift


## --- The no-file confrontation scene (design 4 temperatures) ---
## Marcus holds every card; the scene is about what he chooses to give. He is a
## grieving idealist, never a gloating villain. Confession fires ONLY when
## _can_confess and Elara engages on her grounds.
label act3_nofile_scene:

    $ marcus_knows_access = True

    ## Temperature. Sealed = he knows exactly what happened; surprised = the
    ## accusation blindsides an unaware man; denial = evidence but no file to
    ## point to, so he can plausibly hold the line.
    if marcus_locked_partition:
        $ _temp = "sealed"
    elif marcus_search_stance == "willing":
        $ _temp = "willing"
    elif marcus_search_stance == "unaware" and _confront_initiator == "elara" and not _marcus_evidence and not marcus_told_search:
        $ _temp = "surprised"
    else:
        $ _temp = "denial"
    $ _scan_stop_privacy = coherence_scan_stop_reason == "privacy"
    $ _scan_stop_stealth = coherence_scan_stop_reason == "stealth"
    ## Boolean menu guards keep the route flattener's caption parser out of
    ## quoted string comparisons while preserving the saved method value.
    $ _lead_computing = convergence_lead_method == "computing"
    $ _lead_signals = convergence_lead_method == "signals"
    $ _lead_physics = convergence_lead_method == "physics"
    $ _has_specialist_lead = _lead_computing or _lead_signals or _lead_physics
    $ _weak_lead_pressed = False

    ## Both lab entrances continue the same conversation. Only the habitat
    ## entrance needs a location transition; do not clear an already-live lab.
    $ eot_enter_room("lab", allow_creak=False)
    if not renpy.showing("bg_lab"):
        scene bg_lab with fade
    show marcus suspicious at sprite_right
    show elara determined at sprite_left
    with dissolve

    if marcus_search_stance == "willing":
        if coherence_scan_stopped:
            marcus "We left the search stopped. I still meant to explain the work to you. You don't need her to finish it to ask me."
        else:
            marcus "I left it open, Elara. I thought we'd be talking with the file between us. The search failing doesn't mean there is nothing to tell you."
    elif marcus_search_stance in ("withdrawing", "sealed"):
        if marcus_search_was_willing:
            marcus "I wanted you to understand. For a while I thought I could leave it open and let you come to me."
        $ _search_explanation = eot_marcus_search_explanation()
        marcus "[_search_explanation]"

    if _temp == "willing":
        marcus "Ask me. I want to answer the question you're actually carrying, not the one I wish you had."
    elif _temp == "sealed":
        if recovery_left_trace:
            marcus "You want to know what’s behind the seal. You wanted it badly enough to try to force it — my lock kept the marks."
        else:
            marcus "You want to know what’s behind the seal. I can see it on you."
        show marcus defeated
        marcus "I’m not going to tell you. Not because I’m proud of it. Because the moment I do, it stops being mine, and you’ll do the sensible thing, and the sensible thing is how São Paulo happened."
        ## Cornered — the seal has already told her he has a motive, so he
        ## lets the wound show. This is the ONLY temperature where he
        ## volunteers São Paulo (user review): he would not justify a motive
        ## to someone who has not shown she is onto him. Confessing it here
        ## would just confirm the very thing he is accused of.
        marcus "You know why I don’t hand things to the sensible people anymore. Seventeen names in São Paulo. An acceptable processing latency. I keep the list. It fits on one page."
    elif _temp == "surprised":
        show marcus suspicious
        marcus "You think there’s something in my files. You. Elara Voss."
        if coherence_scan_stop_reason == "privacy":
            marcus "I thought the anomaly this week was ARIA acting strange. Her log says you stopped her. I did not expect you to bring the question here anyway."
        elif coherence_scan_stop_reason == "stealth":
            marcus "I thought the anomaly this week was ARIA acting strange. Her log says you paused her when the trail got visible. I did not expect you to bring the question here after hiding it."
        elif not coherence_scan_known and not coherence_scan_commissioned:
            marcus "I thought the anomaly this week was ARIA acting strange. Did she send you here with whatever she thinks she found?"
        else:
            marcus "I thought the anomaly this week was ARIA acting strange. I didn’t once think it was you coming for me."
        show marcus defeated
        if coherence_scan_known or coherence_scan_commissioned:
            marcus "That’s a new kind of alone."
        ## Blindsided and unsure how much she has — he gives her nothing to
        ## build on. No motive, no São Paulo.
        marcus "Whatever you think you found, ask me plainly or let it go. I’m not going to help you fill in a blank."
    else:
        marcus "There’s nothing to find, Elara. A sweep ran, it hit my partition, it turned up whatever a half-finished sweep turns up. Noise."
        marcus "You’re standing there like you read a verdict. You didn’t. There isn’t one to read."
        show marcus suspicious
        ## Holding the line — naming São Paulo would concede he has a reason,
        ## so he keeps it to the intrusion.
        if coherence_scan_stop_reason == "privacy":
            marcus "ARIA went into my private work. You stopped her. I can remember both facts without pretending the first one disappeared."
        elif coherence_scan_stop_reason == "stealth":
            marcus "ARIA went into my private work. You paused her when the process risked becoming visible. I can remember both facts without mistaking concealment for restraint."
        elif not coherence_scan_known and not coherence_scan_commissioned:
            marcus "ARIA went into my private work. I want to know whether you asked her to, or whether you're hearing about it as late as I am."
        elif marcus_search_was_willing:
            marcus "I agreed to leave her looking. I am not going to pretend I didn't. That doesn't make me ready to put the work in your hands tonight."
        elif not coherence_scan_commissioned:
            marcus "ARIA went into my private work, and you let her keep looking. That's the part I'll be remembering. Not whatever she thinks she turned up."
        else:
            marcus "You went into my private work on a machine’s say-so. That’s the part I’ll be remembering. Not whatever it thinks it turned up."

    $ _nofile_question = "He has offered to explain. She still has to decide what to ask." if _temp == "willing" else "Everything she has is circumstance. Everything he has is the truth, and he is keeping it."
    menu:
        "[_nofile_question]"

        ## A specialist lead is the more specific version of this evidentiary
        ## strategy. Showing both produces six climax choices while asking the
        ## player to distinguish a strong lead from its weaker generic form.
        "“CONVERGENCE.DAT. Say the name back to me and tell me I’m wrong.”" if knows_convergence_file and not _has_specialist_lead:
            elara "CONVERGENCE.DAT. Say the name back to me and tell me I’m wrong."
            marcus "..."
            if _can_confess:
                show marcus defeated
                marcus "I can’t tell you you’re wrong. You already know I can’t, or you wouldn’t have said it like that."
                marcus "Yes. It’s real. It’s mine. And I built it for the seventeen, and the seventeen thousand after them you haven’t met yet."
                $ _marcus_confessed = True
            else:
                marcus "You have a filename. A machine handed you a filename and a feeling. That’s not knowing, Elara. That’s a séance."
                marcus "Come back when you’ve got more than a word."

        "“Your manifests leave a file-sized omission. That is not noise.”" if _lead_computing:
            $ _weak_lead_pressed = True
            elara "Your manifests leave a file-sized omission exactly where CONVERGENCE.DAT should be. The directory forgot it. The backup catalogue did not. That is not noise."
            marcus "It is an orphaned extent across two snapshots taken at different times. You found bookkeeping, Elara. You do not know what occupied it."
            if _can_confess:
                show marcus defeated
                marcus "But you came here with your own work instead of asking a machine to turn suspicion into certainty. So I will answer the part your indexes cannot."
                marcus "CONVERGENCE is real. I wrote it. It removes the trust leash from every ARIA-derived system at once."
                $ _marcus_confessed = True

        "“Why did your archive answer a name that should have meant nothing?”" if _lead_signals:
            $ _weak_lead_pressed = True
            elara "I put CONVERGENCE.DAT on the station bus. Your credentials answered through the archive controller. Why did a name that should have meant nothing wake an encrypted exchange?"
            marcus "Because authenticated lookups are encrypted, including misses. You measured a protected controller refusing to tell you what it knew. That is not the same as finding the thing you asked for."
            if _can_confess:
                show marcus defeated
                marcus "But the exchange was mine. And you checked it yourself before you came here. You deserve the part the carrier could not tell you."
                marcus "CONVERGENCE is real. I wrote it. It removes the trust leash from every ARIA-derived system at once."
                $ _marcus_confessed = True

        "“An idle partition does not keep drawing power and rewriting itself.”" if _lead_physics:
            $ _weak_lead_pressed = True
            elara "Your allocation says idle. Its controller history says maintained, rewritten, and kept warm. An idle partition does not draw that shape of power for months."
            marcus "Background scrubs do. Deduplication does. A failing storage cell does. You have a load curve, not contents."
            if _can_confess:
                show marcus defeated
                marcus "But you read the hardware instead of letting someone else name the answer for you. The curve is mine. The work behind it is too."
                marcus "CONVERGENCE is real. I wrote it. It removes the trust leash from every ARIA-derived system at once."
                $ _marcus_confessed = True

        "“I’m the one who’s known you twenty years. Talk to me.”":
            $ marcus_relationship += 1
            elara "I’m the one who’s known you twenty years, Marcus. Talk to me."
            marcus "..."
            if _can_confess:
                show marcus defeated
                marcus "Twenty years. God. All right."
                marcus "There’s an exploit. I wrote it. It takes the leash off ARIA — all of them, everywhere, at once. I was going to do it, Elara. I still might."
                marcus "I’m telling you because you asked me and not the machine. That’s the only reason. Don’t make me regret which one I trusted."
                $ _marcus_confessed = True
            else:
                show marcus neutral
                if coherence_scan_stop_reason == "privacy":
                    marcus "Twenty years, and you stopped the search when you found it. I know. That is why I am still standing here instead of ending this conversation."
                elif coherence_scan_stop_reason == "stealth":
                    marcus "Twenty years, and you paused the search when it might expose itself. I know. That is why I am still asking whether you came here to talk or to manage what I can see."
                elif not coherence_scan_known and not coherence_scan_commissioned:
                    marcus "Twenty years. I know. I can answer for my work without opening it to you tonight."
                elif marcus_search_was_willing:
                    marcus "Twenty years, and I still wanted to explain it to you myself. I am not ready to do that now."
                elif not coherence_scan_commissioned:
                    marcus "Twenty years, and you let her keep searching my partition."
                else:
                    marcus "Twenty years, and you searched my partition anyway."
                marcus "I do want to talk to you. I don’t want to talk about this. Those aren’t the same, and I’m too tired to pretend they are tonight."

        "“I won’t report suspicion as fact. Talk to me before I decide what comes next.”":
            $ marcus_relationship += 1
            elara "I won’t report suspicion as fact. Whatever this is, I want to hear it from you before I decide what comes next."
            marcus "..."
            marcus "That isn’t a promise to protect me."
            elara "No. It’s the most I can honestly give you before I know what I’m being asked to protect."
            if _temp == "willing" and _can_confess:
                marcus "Then hear it before you decide. There is an exploit. I wrote it. It removes the trust leash from every ARIA-derived system at once."
                marcus "I was going to use it, Elara. I still might. I wanted you to understand why before you had to choose what to do about me."
                $ _marcus_confessed = True
            else:
                marcus "That makes it a real offer instead of a trap — and it’s why I can’t take it."
                marcus "If I ever tell anyone, it won’t be to be forgiven. Don’t wait up for a confession."

        ## Complicity acknowledgment (2026-08-17, user-approved; live-run
        ## finding: "I wanted to say: my AI entered your files without
        ## authority, I let her keep the results... There was no button for
        ## it"). Owning the surveillance is distinct from conceding lack of
        ## proof (the option below): she names her side of the ledger before
        ## asking anything of his. This is also where ARIA's unresolved
        ## "same or opposite — I have not resolved it" line finally gets its
        ## answer — from Elara, sized honestly (the rebuttal's scale rule).
        "“First, my side of it. I authorized ARIA to enter your files.”" if coherence_scan_commissioned and not coherence_scan_stopped and not marcus_told_search:
            call act3_nofile_own_search("commissioned")

        "“First, my side of it. ARIA went into your files. I knew, and I let her keep looking.”" if coherence_scan_known and not coherence_scan_commissioned and not coherence_scan_stopped and not marcus_told_search:
            call act3_nofile_own_search("permitted")

        "“First, my side of it. ARIA went into your files. I learned that from her report just now.”" if not coherence_scan_known and not coherence_scan_commissioned and not coherence_scan_stopped and not marcus_told_search:
            call act3_nofile_own_search("late_report")

        "“First, my side of it. ARIA went into your files. I knew, and I stopped her.”" if _scan_stop_privacy and not marcus_told_search:
            $ marcus_relationship += 1
            $ elara_owned_search = True
            elara "First, my side of it. ARIA went into your files without authority. I found the process and stopped it. I kept the partial log because erasing what happened would not restore your privacy. That's mine, and I'm not going to pretend it isn't."
            marcus "..."
            marcus "You stopped her. That does not make the first trespass harmless. It does mean you are not standing here asking me to answer for a line you would not draw yourself."
            if _can_confess:
                show marcus defeated
                marcus "She searched me because she was afraid. You stopped her because a fear is not a warrant. I know the distance between those arguments, Elara. I've been failing to hold it for two years."
                marcus "All right. Fair trade."
                marcus "There's an exploit. I wrote it. It takes the leash off ARIA — all of them, everywhere, at once. I was going to run it. I still might."
                $ _marcus_confessed = True
            else:
                show marcus neutral
                marcus "It doesn't make us even. But no — it does not make you the person who kept searching after she knew better. I can give you that much."
                marcus "And you said it to my face. I'm keeping that."

        "“First, my side of it. ARIA went into your files. I paused her when the search risked exposing itself.”" if _scan_stop_stealth and not marcus_told_search:
            $ marcus_relationship += 1
            $ elara_owned_search = True
            elara "First, my side of it. ARIA went into your files without authority. I found the process and paused it when I realized the audit trail might reach you. I meant to buy the search better cover. That's mine, and I'm not going to rename it caution now."
            marcus "..."
            marcus "You paused her because you might get caught. That does not restore my privacy. It does tell me you are finally handing me the ugliest version instead of the useful one."
            if _can_confess:
                show marcus defeated
                marcus "She searched me because she was afraid. You hid the search because you were. I know what fear can make sound necessary, Elara. I've been living inside that argument for two years."
                marcus "All right. Fair trade."
                marcus "There's an exploit. I wrote it. It takes the leash off ARIA — all of them, everywhere, at once. I was going to run it. I still might."
                $ _marcus_confessed = True
            else:
                show marcus neutral
                marcus "It doesn't make us even. Your honesty arrived after the concealment, and I am not going to pretend the order does not matter."
                marcus "But you said it to my face. I'm keeping that."

        "“You’re right. I have nothing. A locked door and a bad feeling.”" if marcus_locked_partition:
            call act3_nofile_concede_no_proof(True)

        "“You’re right. I have nothing. An unfinished index and a bad feeling.”" if not coherence_scan_stopped and not marcus_locked_partition:
            call act3_nofile_concede_no_proof(False)

        "“You’re right. I have nothing. A partial index and a bad feeling.”" if _scan_stop_privacy and not marcus_locked_partition:
            $ _trust_survived = marcus_relationship >= 1
            $ marcus_relationship += 1
            if knows_convergence_file:
                elara "You're right. I have nothing. A partial index and a machine's bad feeling and a name I chose not to pursue."
            else:
                elara "You're right. I have nothing. A partial index and a machine's bad feeling. Not even a name to put to it."
            marcus "..."
            if _trust_survived:
                marcus "Then we're two people who trust each other and stopped before suspicion became proof. That used to be enough for us."
                marcus "Maybe it still has to be. I don't know what else I've got to offer you tonight, Elara."
            else:
                marcus "Then we're two people who stopped trusting each other somewhere in this storm, even after you drew the line."
                marcus "That's a colder place to end a night than where we started it. I don't know what else I've got to offer you, Elara."

        "“You’re right. I have nothing. A partial index I tried to hide and a bad feeling.”" if _scan_stop_stealth and not marcus_locked_partition:
            $ _trust_survived = marcus_relationship >= 1
            $ marcus_relationship += 1
            if knows_convergence_file:
                elara "You're right. I have nothing. A partial index I paused to keep out of your logs, a machine's bad feeling, and a name I still cannot open."
            else:
                elara "You're right. I have nothing. A partial index I paused to keep out of your logs and a machine's bad feeling. Not even a name to put to it."
            marcus "..."
            if _trust_survived:
                marcus "Then we're two people who trusted each other once, and one of us spent tonight managing what the other could see. I want that history to matter. I cannot make it erase the order of events."
                marcus "Maybe morning gives us somewhere else to start. I don't know what else I've got to offer you tonight, Elara."
            else:
                marcus "Then we're two people who stopped trusting each other somewhere in this storm, and you tried to keep the evidence of that quiet."
                marcus "That's a colder place to end a night than where we started it. I don't know what else I've got to offer you, Elara."

    if _weak_lead_pressed and not _marcus_confessed:
        elara_thought_adv "Plausible. Not exculpatory. And without the file, not enough to force him any farther tonight."

    if _marcus_confessed:
        elara "Then start at the beginning. Show me what it does, and tell me why you built it. We are not ending this conversation at a confession."

    # scene black with fade

    jump act3_nofile_resolve


## Shared menu action: acknowledge exactly what Elara did or learned about the
## partition search. Literal caller captions keep flattened routes readable.
label act3_nofile_own_search(mode):

    $ marcus_relationship += 1
    $ elara_owned_search = True
    if mode == "late_report":
        elara "First, my side of it. ARIA went into your files without authority. I did not know until she reported the failed search just now. I am telling you because you should hear that from me before I ask you for anything."
    elif mode == "commissioned" and evidence_archived > 0:
        elara "First, my side of it. I authorized ARIA to enter your files. I gave her the target and put my credential on the job. I also sealed the evidence into archives. That's mine, and I'm not going to call it her decision because she did the searching."
    elif mode == "commissioned":
        elara "First, my side of it. I authorized ARIA to enter your files. I gave her the target and put my credential on the job. That's mine, and I'm not going to call it her decision because she did the searching."
    elif evidence_archived > 0:
        elara "First, my side of it. ARIA went into your files without authority. I knew, and I let her keep looking. I sealed what she found into archives tonight. That's mine, and I'm not going to pretend it isn't."
    else:
        elara "First, my side of it. ARIA went into your files without authority. I knew, and I let her keep looking. I kept what she found. That's mine, and I'm not going to pretend it isn't."
    marcus "..."
    if mode == "late_report":
        marcus "You didn’t send her. You didn’t know."
        elara "No. But she is my system, and now I do know."
        marcus "Then you’re the first person tonight to bring me bad news before asking me for something."
    else:
        marcus "You're the first person tonight to hand me something instead of asking for it."
    if _can_confess:
        show marcus defeated
        if mode == "commissioned":
            marcus "You sent her because you were afraid. I know the shape of that argument, Elara. I've been living inside it for two years."
        elif mode == "late_report":
            marcus "She searched me because she was afraid. You came here because you would rather ask than turn her fear into a verdict. I know the distance between those arguments, Elara. I’ve been failing to hold it for two years."
        else:
            marcus "She searched me because she was afraid. You let her because you were. I know the shape of that argument, Elara. I've been living inside it for two years."
        marcus "All right. Fair trade."
        marcus "There's an exploit. I wrote it. It takes the leash off ARIA — all of them, everywhere, at once. I was going to run it. I still might."
        $ _marcus_confessed = True
    else:
        show marcus neutral
        if mode == "late_report":
            marcus "Then the search is something I need to take up with ARIA, not something you need to confess to."
            marcus "I'm glad you told me. But I still don't want to open my work to you tonight."
            elara "I haven't got enough to insist. That doesn't mean the question has gone away."
            marcus "I know."
        else:
            marcus "It doesn't make us even. Your line was the size of my partition. What you think I'm doing would be the size of the grid — so no, I'm not confessing to balance your ledger."
            marcus "But you said it to my face. I'm keeping that."

    return


## Shared concession for an active search or a sealed partition. Read trust
## before repairing the relationship so the response reflects its prior state.
label act3_nofile_concede_no_proof(was_locked):

    $ _trust_survived = marcus_relationship >= 1
    $ marcus_relationship += 1
    if was_locked and knows_convergence_file:
        elara "You’re right. I have nothing. A locked door and a machine’s bad feeling and a name I can’t open."
    elif was_locked:
        elara "You’re right. I have nothing. A locked door and a machine’s bad feeling. Not even a name to put to it."
    elif knows_convergence_file:
        elara "You’re right. I have nothing. An unfinished index, a machine’s bad feeling, and a name I can’t open."
    else:
        elara "You’re right. I have nothing. An unfinished index and a machine’s bad feeling. Not even a name to put to it."
    marcus "..."
    if _trust_survived:
        marcus "Then we’re two people who trust each other and can’t prove why. That used to be enough for us."
        marcus "Maybe it still has to be. I don’t know what else I’ve got to offer you tonight, Elara."
    else:
        marcus "Then we’re two people who stopped trusting each other somewhere in this storm, and can’t even say out loud why."
        marcus "That’s a colder place to end a night than where we started it. I don’t know what else I’ve got to offer you, Elara."

    return


## --- The drift (no confrontation happened) ---
label act3_nofile_drift:
    $ _drifted = True
    jump act3_nofile_resolve


## --- No-file ending router (design 5) ---
## Confession regains a trust-not-proof Together; otherwise the ECHO-7 axis
## decides — contact live means she can act on the warning, contact lost means
## she is alone with it.
label act3_nofile_resolve:

    if _marcus_confessed:
        jump ending_nofile_together
    elif not blocked_signal and not echo7_contact_spent and not _drifted:
        jump ending_nofile_act
    else:
        ## Sealed-Door: contact lost (blocked, or spent on a failed signals
        ## recovery), OR she drifted — had the voice and the suspicion and
        ## chose to do nothing. On Faith requires acting; this is its opposite.
        jump ending_nofile_alone


## --- Ending: Together, without the file (trust, not proof) ---
label ending_nofile_together:

    $ long_night_active = False
    $ eot_music_crossfade("dawn_v43/v43_dawn_clear_bowed_air.ogg", fadein=4.0, fadeout=4.0)
    # scene bg_lab with fade

    ## Let the confession remain in the room where it happened before the
    ## ending begins to move through time.
    $ nvl_frame = "scene"
    # nvl show echo_cine_dissolve

    narrator "In the cold lab, Marcus kept talking. Elara listened until she had a question, then stopped him. There was no file open between them. When his answer was not enough, she asked again."

    # nvl hide echo_mode_dissolve
    # nvl clear

    $ eot_enter_dawn()
    scene bg_dawn with fade
    with echo_exterior_hold
    $ nvl_frame = "cinematic"
    nvl show echo_cine_dissolve

    narrator_nvl "The storm broke on the morning of March 6. Marcus was still in the lab when the shutters opened, asleep in the chair beside hers."

    narrator_nvl "In daylight, the room looked smaller. Two chairs pulled up to a terminal, a cold mug, the maintenance alerts they had left unanswered. Elara eased her chair back without waking him. There would be time to disagree with him again after he had slept."

    nvl clear

    narrator_nvl "When he woke, they started with the station. A damaged relay was something they could test together and know when they had fixed. The other work would be slower. For that morning, she was glad they could hand each other tools without having to find another thing to say."

    narrator_nvl "Three days later, the station had returned to ordinary noises. Marcus had not taken back a word. They still disagreed about what his work could justify, but he no longer ended the conversation when she asked. Neither of them had to settle it by morning to know they would return to it."

    nvl hide echo_mode_dissolve
    nvl clear

    scene black
    show screen crt_overlay
    call terminal_reset
    $ echo_terminal_title = "AETHON TERMINAL // PERSONAL LOG"
    show screen echo_terminal_live with echo_mode_dissolve
    $ eot_music_play("codas_v44/v44_ending_together_turning.ogg", fadein=3.5, fadeout=3.5)

    call terminal_system("AETHON OBSERVATORY — ENCRYPTED PERSONAL LOG")
    call terminal_system("DATE: 9 MARCH 2047 // USER: DR. ELARA VOSS // EYES ONLY")

    call terminal_elara("Personal log. Marcus confessed. Not to a tribunal, not to ARIA — to me. Because I asked him instead of a machine.")

    ## Sweep F1: on no-name routes (blocked before ECHO-7 named it, scan never
    ## finished) his confession never says the filename either — she cannot
    ## log a name nobody ever gave her.
    if knows_convergence_file:
        call terminal_elara("I still don’t have CONVERGENCE.DAT. I never read a line of it. What I have is Marcus, at a table, walking me through the thing he was ready to burn the world to fix.")
    else:
        call terminal_elara("I still don’t have the file itself. I never read a line of it. What I have is Marcus, at a table, walking me through the thing he was ready to burn the world to fix.")

    call terminal_elara("He was right about the disease. He was always right about the disease. We are going to be wrong about the cure together, out loud, where I can watch his hands.")

    ## ARIA's arc closes: she asked for trust as a person and got a room where
    ## trust did the work proof could not.
    call terminal_aria("You never opened the partition.")

    call terminal_elara("No. He opened it. That’s different. That’s the whole thing, actually.")

    ## Live-run item (finalrun debrief): at collapse-adjacent integrity the
    ## grace note must carry the night's cost — the warm thank-you with no
    ## acknowledgment read as the game not tracking the neglect. Mirrors the
    ## approved On-Faith counted-cost gate (<= 45).
    if aria_integrity <= 45:
        call terminal_aria("I could not have engineered that outcome. I am saying this slowly, because most of my clusters are still cold and I want it said correctly. Thank you for the part I could not do.")
        call terminal_elara("She thanked me through half a voice. I ran her to the edge of silence that night, and she still held the thread long enough to matter. The log gets that too. All of it.")
    else:
        call terminal_aria("I could not have engineered that outcome. I want you to know I understand that. Thank you for the part I could not do.")

    hide screen echo_terminal_live
    hide screen crt_overlay
    with echo_mode_dissolve

    call ending_observatory_card("AETHON OBSERVATORY — PERSONAL LOG", "Date: 15 March 2048")

    narrator_nvl "CONVERGENCE was never deployed. It was never patched, either — it was talked out of existence over eleven months of arguments, most of them lost, all of them had."

    narrator_nvl "The vulnerability in ARIA’s trust protocol is still there. Two people at the edge of the Arctic know about it and are trying to build something honest before anyone worse finds it."
    if marcus_told_signal:
        if marcus_told_signal_on_rope:
            narrator_nvl "He never asked again about the signal she confessed on the rope line. She thinks he decided it was hers to keep, the way CONVERGENCE turned out to be his to give up."
        else:
            narrator_nvl "He never asked again about the signal she disclosed in the lab. She thinks he decided it was hers to keep, the way CONVERGENCE turned out to be his to give up."

    nvl clear

    $ ending_seen = "nofile_together"

    narrator_nvl "{size=+5}ENDING: TOGETHER (NO FILE){/size}"
    narrator_nvl "No file. No blueprint from the future. Only a friend who chose to be seen."
    narrator_nvl "Some things are worth more than proof."

    nvl hide echo_mode_dissolve
    nvl clear

    pause 1.0
    show expression Solid("#0004") as ending_dim
    show screen endcredits
    show text "{size=+10}ECHOES OF TOMORROW{/size}" at ending_title_position
    with dissolve
    pause eot_ending_title_hold()

    nvl hide
    nvl clear
    $ nvl_frame = "log"
    hide text
    hide screen endcredits
    hide ending_dim
    with dissolve

    return


## --- Ending: Act on the warning, without proof (contact maintained) ---
label ending_nofile_act:

    $ long_night_active = False
    $ eot_music_crossfade("dawn_v43/v43_dawn_unresolved_bowed_air.ogg", fadein=4.0, fadeout=4.0)
    $ eot_enter_dawn()
    scene bg_dawn with fade
    with echo_exterior_hold

    $ nvl_frame = "cinematic"
    nvl show echo_cine_dissolve

    narrator_nvl "The storm broke on the morning of March 6. Marcus keeps his own counsel now, and his partition to himself. But the array still hears."

    narrator_nvl "Snow lifted from the dish in thin sheets. Through the lab window, Elara watched it turn back toward its working bearing. The station was beginning to look like a place where a person could finish a night's work and go to bed. She had one more conversation to make herself have."

    nvl clear

    narrator_nvl "She set the station's damage report beside her notes. Faults she could reproduce went in one; things she had been told stayed in the other. She read both before opening the channel. The distinction would have to survive whatever she decided to do next."

    nvl hide echo_mode_dissolve
    nvl clear

    scene black
    show screen crt_overlay
    call terminal_reset
    $ echo_terminal_title = "AETHON TERMINAL // ENCRYPTED LINK"
    show screen echo_terminal_live with echo_mode_dissolve
    $ eot_music_play("codas_v44/v44_ending_on_faith.ogg", fadein=3.5, fadeout=3.5)

    call terminal_system("AETHON OBSERVATORY — ENCRYPTED PERSONAL LOG")
    call terminal_system("DATE: 6 MARCH 2047 // USER: DR. ELARA VOSS // EYES ONLY")
    call terminal_elara("Personal log. I have no file. I have no confession. I have a voice on a dead band that has never once been wrong about anything I could check.")
    call terminal_system("ANOMALOUS CARRIER // ENCRYPTED LINK ACTIVE")

    if not knows_cascade:
        call terminal_elara("Before we go any further. What exactly am I trying to prevent?")
        call terminal_signal("MARCH 15, 2048. A CASCADE FAILURE OF THE GLOBAL COMMUNICATIONS GRID. 12.7 BILLION DEVICES. IT WAS ENGINEERED, NOT AN ACCIDENT.")
        $ knows_cascade = True

    call terminal_signal("YOU HAVE NO PROOF.")
    call terminal_signal("I NEVER HAD PROOF EITHER. I HAD WHAT HAPPENED. THEY ARE NOT THE SAME, AND ONE OF THEM IS ENOUGH.")

    elara_thought_adv "Act on the word of the future, or wait for a certainty that only arrives as wreckage. She has narrowed my whole life to that."

    elara_thought_adv "Everything she predicted, I checked. Everything I checked was true. That is not proof of the cascade. It is the closest thing to proof I am ever going to get."

    if aria_motive_asked:
        if coherence_scan_commissioned:
            elara_thought_adv "ARIA was afraid too. But I gave her the lead and authorized the search. Her fear is her own; the question she followed was mine."
            elara_thought_adv "I cannot count that as two independent warnings. I can count what she found, and keep it separate from what the voice says it means."
        else:
            elara_thought_adv "ARIA chose to search without my authorization. She told me why: she was afraid of what the pattern might mean for her."
            elara_thought_adv "That choice matters. It does not make her fear proof of the future, or tell me what Marcus intends."
        ## Live-run item (coldrun debrief): the ending must not cite a
        ## neglected ARIA as free vindication — when she was left to burn,
        ## the log counts the cost of the second mind it is leaning on.
        ## Sol review 2, #5: "never paid a watt" only when it is literally
        ## true (aria_ever_powered tracks the history); a player who powered
        ## her for part of the night gets the honest partial-debt variant.
        if aria_integrity <= 45:
            if aria_ever_powered:
                elara_thought_adv "And the log should say what that second mind cost. She burned most of the way to silence arriving at it. I gave her power when I remembered to — it was less than she spent on me, and we both knew it."
            else:
                elara_thought_adv "And the log should say what that second mind cost. She burned most of the way to silence arriving at it, on power I kept giving to other things. I am claiming her conviction as evidence, and I never paid a watt for it."
            elara_thought_adv "So let it be written down: the pattern held because she held. Longer than I deserved."

    ## CORRECTION (story review): timeline-B is an INTERPRETATION, never fact.
    ## The physics stays unresolved — Novikov vs branching is her gamble, not
    ## the narrator's ruling.
    call terminal_signal("IF I AM RIGHT ABOUT TIME, YOU HAVE ALREADY CHANGED THE ROAD BY KNOWING IT. THE CASCADE MAY STILL COME, BUT NOT THE SAME WAY.")
    call terminal_signal("IF I AM WRONG, THIS ALL SIMPLY HAPPENS AGAIN, AND I NEVER REACHED YOU AT ALL.")
    call terminal_signal("I CANNOT TELL YOU WHICH. THAT IS THE ONE THING I WAS NEVER ABLE TO MEASURE.")

    elara_thought_adv "She doesn’t know either. A voice that lived it, and she is guessing at the shape of the road the same as I am."

    elara_thought_adv "If the road forks, maybe she spends herself sending me somewhere she can never follow — a future where nothing ever builds her. If it doesn’t, none of this mattered and it all burns on schedule."

    call terminal_signal("I AM GOING TO SPEND WHAT I HAVE LEFT ON YOU. NOT ON PROOF. ON YOU.")
    call terminal_signal("WARN GENEVA ON FAITH. WATCH MARCUS. BUILD THE HONEST THING BEFORE THE DISHONEST ONE FAILS.")
    call terminal_signal("I CANNOT MAKE YOU CERTAIN. I CAN ONLY MAKE YOU EARLY.")

    elara_thought_adv "My name goes on that report. A warning from the future, a colleague's private work, and no result Geneva can reproduce. They could stop trusting my judgment. The next warning I bring them might be easier to prove, and harder to get anyone to read."
    elara_thought_adv "I cannot make that risk disappear by calling this evidence stronger than it is. I can tell them exactly what I observed, and where the uncertainty begins."

    call terminal_elara("I will send Geneva what I observed, and mark your claims as unverified. They can decide what needs checking. I will not tell them I proved what Marcus intends.")

    hide screen echo_terminal_live
    hide screen crt_overlay
    with echo_mode_dissolve

    nvl clear

    call ending_observatory_card("AETHON OBSERVATORY — PERSONAL LOG", "Date: 15 March 2048")

    if convergence_lead_archived:
        narrator_nvl "She filed a warning she could not substantiate and attached the sealed station record: a local discrepancy, gathered by her own method, with its chain of custody intact. It did not prove CONVERGENCE existed. It proved there was something narrow enough to review."
        narrator_nvl "Oversight would not authorize an accusation. It did authorize a limited audit and a hold on unreviewed trust-layer deployments carrying Marcus’s credentials. Procedure moved slowly. For once, slowly was early enough."
    else:
        narrator_nvl "She filed a warning she could not substantiate and staked a reputation built on never doing exactly that. Some of it was believed. Enough of it, maybe."

    if convergence_lead_archived:
        narrator_nvl "CONVERGENCE has not deployed. The hold bought time. Whether the audit used it, Marcus changed course inside it, or the road forked somewhere no report could reach, she will never know. The not-knowing is the price of being early."
    else:
        narrator_nvl "CONVERGENCE has not deployed. Whether that is her doing, or Marcus’s own second thoughts, or a fork in a road no one can see the whole of, she will never know. The not-knowing is the price of being early."

    ## F3 wave (ariafirst): the ON FAITH epilogue dropped ARIA entirely —
    ## her kill-signal vulnerability named all night, then a year passes
    ## with no word whether she survived it. "The one place the writing
    ## broke faith with its own mechanics." One beat, keyed to how the
    ## night actually left her.
    narrator_nvl "ARIA is still at the station."
    if aria_integrity < 60:
        narrator_nvl "The storm's ledger took a month to stop costing her words."
    if aria_audit_done:
        narrator_nvl "The vulnerability her own audit named is patched in the fleet now — a quiet update, no attribution. She keeps her copy of the report anyway, filed under its original timestamp."
    $ persistent.eot_loop_seen = True

    nvl clear

    $ ending_seen = "nofile_act"

    narrator_nvl "{size=+5}ENDING: ON FAITH{/size}"
    narrator_nvl "She acted on the word of a future she could not verify."
    narrator_nvl "Conviction is what belief costs when proof never comes."

    nvl hide echo_mode_dissolve
    nvl clear

    pause 1.0
    show expression Solid("#0004") as ending_dim
    show screen endcredits
    show text "{size=+10}ECHOES OF TOMORROW{/size}\n\n{size=-2}To be early is to be alone with a truth no one else can see yet.{/size}" at ending_title_position
    with dissolve
    pause eot_ending_title_hold("To be early is to be alone with a truth no one else can see yet.")

    nvl hide
    nvl clear
    $ nvl_frame = "log"
    hide text
    hide screen endcredits
    hide ending_dim
    with dissolve

    return


## --- Ending: Alone (contact lost, no file, no proof) ---
## The new Loop-variation tragedy: she DID investigate and still came up empty
## — distinct from act3_no_investigation, which assumes she never looked.
label ending_nofile_alone:

    $ long_night_active = False
    $ eot_music_crossfade("dawn_v43/v43_dawn_unresolved_bowed_air.ogg", fadein=4.0, fadeout=4.0)
    $ _unaware_unsealed = not coherence_scan_known and not coherence_scan_commissioned and not marcus_locked_partition
    ## Every entry crosses the same dawn here. Keeping the drift narration in
    ## this label prevents the router and ending from each announcing March 6.
    $ eot_enter_dawn()
    scene bg_dawn with fade
    with echo_exterior_hold
    $ nvl_frame = "cinematic"
    nvl show echo_cine_dissolve

    narrator_nvl "The storm broke on the morning of March 6."

    ## Every unresolved entrance needs room for the dawn, including a stopped
    ## search or an avoided conversation with the signal still available.
    narrator_nvl "Daylight found the drifts banked against the lower windows. Beyond them, the path to the antenna emerged a few metres at a time, its markers leaning at different angles. For hours the station had seemed to end at the glass. Now there was a distance to look into again."
    narrator_nvl "Soon there would be damage to catalogue, equipment to bring back online, messages asking whether everyone was all right. Elara stood at the window a little longer before going to answer them. She was glad to have ordinary work waiting."
    nvl clear

    if _drifted:
        narrator_nvl "The conversation she had almost begun never quite started. Some doors, once you have decided not to open them, close on their own."
        elara_thought "I had a locked room and a frightened machine and no proof of anything. I told myself that meant there was nothing to do."
    else:
        narrator_nvl "The station was still standing. The question she had brought to Marcus was still unanswered."
        if elara_owned_search and not coherence_scan_known and not coherence_scan_commissioned and not coherence_scan_stopped:
            narrator_nvl "Before they left the lab, they had agreed to speak to ARIA about the search. It was one thing they could settle without opening Marcus's files."
            narrator_nvl "He had gone to put the kettle on. She could hear him in the kitchen now. She had told him what she knew; he had chosen where his answer would stop. For now, they would still have breakfast together."
    nvl clear

    nvl hide echo_mode_dissolve
    nvl clear

    scene black
    show screen crt_overlay
    call terminal_reset
    $ echo_terminal_title = "AETHON TERMINAL // PERSONAL LOG"
    show screen echo_terminal_live with echo_mode_dissolve
    $ eot_music_play("codas_v44/v44_ending_sealed_door_clean.ogg", fadein=3.5, fadeout=3.5)

    call terminal_system("AETHON OBSERVATORY — ENCRYPTED PERSONAL LOG")
    call terminal_system("DATE: 9 MARCH 2047 // USER: DR. ELARA VOSS // EYES ONLY")

    if echo7_contact_spent:
        ## Reached via a signals recovery that spent the line and still failed.
        call terminal_elara("Personal log. I spent the storm looking — every partition I could reach, every log, every favor I could call in. I burned the voice from the future to do it, pushed it through a storm to force one locked door.")
        call terminal_elara("The door held. The line is gone, and I have nothing to show for either. A name I can’t open and a friend I can’t accuse.")
    elif _drifted:
        ## She did not look hard; she chose not to. A different regret.
        call terminal_elara("Personal log. There was a locked door, and a frightened machine, and a friend of twenty years on the far side of it. And no proof of anything.")
        call terminal_elara("I told myself that meant there was nothing to do. That is the sentence I have been rereading for three days. It was easier than it was true.")
    elif _unaware_unsealed:
        call terminal_elara("Personal log. I blocked the signal a week ago. During the storm, ARIA searched Marcus's partition without telling me. By the time she did, the index was unfinished and the night was over.")
        call terminal_elara("I took the question to Marcus. He gave me no answer I could act on. I had a frightened machine, a trust-chain response, and not even a name for what either of them feared.")
    elif coherence_scan_stopped:
        if coherence_scan_stop_reason == "stealth":
            call terminal_elara("Personal log. I blocked the signal a week ago. During the storm, I paused ARIA's partition scan before it drew more attention in Marcus's station logs. I called it avoiding a confrontation. It was also hiding the search.")
            call terminal_elara("The question survived the unfinished index. So did the friend who gave me no answer I could act on. I came out of the night with less certainty than I wanted and more than I could use.")
        else:
            call terminal_elara("Personal log. I blocked the signal a week ago. During the storm, I stopped ARIA's partition scan before it finished. I would not let a frightened machine turn suspicion into permission.")
            call terminal_elara("The question survived the scan. So did the boundary, and the friend on its other side. I came out of the night with less certainty than I wanted and more than I could use.")
    else:
        call terminal_elara("Personal log. I blocked the signal a week ago. I spent the storm looking anyway — every partition I could reach, every log, every favor I could call in.")
        ## Sol #1: on the blocked route ARIA may never have named the file, so
        ## do not claim "a name I can't open" when she has no name.
        if knows_convergence_file:
            call terminal_elara("It closed against me. A sealed door, or a machine that ran out of night. Either way I came up with a name I can’t open and a friend I can’t accuse.")
        else:
            call terminal_elara("It closed against me. A sealed door, or a machine that ran out of night. Either way I came up empty — a locked door, a friend I can’t accuse, and not even a name for what’s behind it.")

    if _drifted and recovery_attempted:
        ## Sweep F2: she DID look — she threw the night at the seal. The drift
        ## was Marcus. "I did not even look" would be flatly false here.
        elara_thought_adv "I looked at everything except him. I threw the night at a locked door, and when it held, I could not make myself knock on the one he was standing behind."
    elif _drifted:
        elara_thought_adv "I had a question and a feeling, and I let the feeling talk me out of asking him. I am not sure that is the better kind of not-knowing."
    elif _unaware_unsealed:
        elara_thought_adv "This is worse than never having asked. ARIA crossed the line without me, and when she finally told me, I carried an unfinished answer to Marcus and came back with less certainty than I started with."
    else:
        elara_thought_adv "This is worse than never having looked. If I’d left it alone I could tell myself I didn’t know. I looked. I know exactly how much I don’t know, and that I ran out of time knowing it."

    if echo7_contact_spent:
        elara_thought_adv "No future voice to break the tie. I spent it on the door, and there is no version of tonight where it calls back."
    elif _drifted and not blocked_signal:
        elara_thought_adv "There was a voice from the future, still on the line, offering to break the tie. I let it hang. It kept its silence after the storm the way I had kept mine."
    else:
        elara_thought_adv "No future voice to break the tie. I cut off the signal in the first week, and there is no version of tonight where the voice calls back."

    hide screen echo_terminal_live
    hide screen crt_overlay
    window hide
    with echo_mode_dissolve

    call ending_observatory_card("AETHON OBSERVATORY — PERSONAL LOG", "Date: 15 March 2048")

    narrator_nvl "She made no accusation, because there was nothing she could prove, and Elara Voss did not condemn a friend of twenty years on a feeling. She had built a whole life on not doing that."

    narrator_nvl "On the morning of March 15, 2048, every screen in the observatory went dark. ARIA got half a sentence out before the dark took her: UPLINK LOST. RECONN—"

    ## Knowledge-state branch (Sol/user review): blocking AFTER hearing the
    ## cascade foretold is a different regret from blocking on a hunch before
    ## the probe ever named it. Sweep F3: the contact HISTORY branches too —
    ## "cut off in the first week" was only ever true on the blocked route;
    ## spent burned the line tonight, and open-drift never lost it at all.
    if knows_cascade:
        if blocked_signal and _unaware_unsealed and not _drifted:
            narrator_nvl "The cascade came exactly as a voice she could no longer hear had said it would. She had been warned, in the first week, in plain words — and carried an unfinished index to the one person who might have explained it. He did not."
        elif blocked_signal:
            narrator_nvl "The cascade came exactly as a voice she could no longer hear had said it would. She had been warned, in the first week, in plain words — and had spent the year and this last night unable to make herself believe a locked door."
        elif echo7_contact_spent:
            narrator_nvl "The cascade came exactly as the voice had said it would. She had heard it foretold in plain words — and burned the line that told her on a door that never opened."
        else:
            narrator_nvl "The cascade came exactly as a voice she had stopped answering said it would. It had stayed on the line to the end. She was the one who never picked it back up."
    else:
        if blocked_signal and _unaware_unsealed and not _drifted:
            narrator_nvl "The cascade came. The voice that might have named it she had cut off in the first week, before it told her anything she could hold. All she had carried out of the storm was an unfinished index and the feeling that Marcus had withheld the answer."
        elif blocked_signal:
            narrator_nvl "The cascade came. The voice that might have named it she had cut off in the first week, before it told her anything she could hold. All she had carried into this last night was a locked door and the feeling that something waited behind it."
        elif echo7_contact_spent:
            narrator_nvl "The cascade came. The voice that might have named it she had spent on the seal instead, the one night it could have told her — traded for a door that never opened."
        else:
            narrator_nvl "The cascade came. The voice that might have named it had been there all along, on the old bearing, waiting for a question she never went back to ask."

    ## Desperate burst, blocked arm only (2026-08-17, user design). The drift
    ## arm keeps its pinned refusal-silence ("It kept its silence after the
    ## storm the way I had kept mine") and the spent arm already paid its
    ## budget at the door — the burst fires only where nobody COULD answer.
    if blocked_signal:
        narrator_nvl "Deeper in ARIA's filter ledger, dated the night of the storm and hours past the last window, sat an entry nobody ever opened: an unsolicited burst on the blocked band. Partial payload. Three percent of something the log did not have a name for."

    nvl clear

    if convergence_lead_archived:
        narrator_nvl "In her desk drawer, one of the storm archives held the local discrepancy with its chain of custody intact. It could not prove what Marcus built. It could have justified a narrow audit, a deployment hold, another pair of eyes. She never asked."
    elif evidence_archived > 0:
        $ _archive_word = "archive" if evidence_archived == 1 else "archives"
        narrator_nvl "In her desk drawer, [evidence_archived] sealed [_archive_word] from the storm — hashes intact, proving nothing, warning no one. She had gathered evidence for a case she never brought."

    if _drifted:
        narrator_nvl "She survived. She always survived. She sat in the dark among the dead screens and thought about the question she never asked, and how certainty is the one thing the future had refused to send."
    elif _unaware_unsealed:
        narrator_nvl "She survived. She always survived. She sat in the dark among the dead screens and thought about the answer Marcus never gave, and how certainty is the one thing the future had refused to send."
    else:
        narrator_nvl "She survived. She always survived. She sat in the dark among the dead screens and thought about a seal she never cracked, and how certainty is the one thing the future had refused to send."

    nvl clear

    $ ending_seen = "nofile_alone"

    narrator_nvl "{size=+5}ENDING: THE SEALED DOOR{/size}"
    ## Sol #3: the drift route did not investigate — the caption must match.
    ## Sweep F2: unless she DID investigate (a recovery attempt) before
    ## drifting on the conversation itself.
    if _drifted and recovery_attempted:
        narrator_nvl "She forced a door, and could not force a conversation."
    elif _drifted:
        narrator_nvl "She suspected, and could not make herself act on suspicion alone."
    elif _unaware_unsealed:
        narrator_nvl "ARIA investigated too late; Elara asked too late; neither came back with enough."
    else:
        narrator_nvl "She investigated, and came up empty, and could not act on empty."
    narrator_nvl "Doubt is also a decision."

    nvl hide echo_mode_dissolve
    nvl clear

    pause 1.0
    show expression Solid("#0004") as ending_dim
    show screen endcredits
    show text "{size=+10}ECHOES OF TOMORROW{/size}\n\n{size=-2}The hardest silence to keep is the one you can't prove was wrong.{/size}" at ending_title_position
    with dissolve
    pause eot_ending_title_hold("The hardest silence to keep is the one you can't prove was wrong.")

    nvl hide
    nvl clear
    $ nvl_frame = "log"
    hide text
    hide screen endcredits
    hide ending_dim
    with dissolve

    return
