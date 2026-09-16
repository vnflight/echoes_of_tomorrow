################################################################################
## Echoes of Tomorrow — Custom Game Screens
##
## Observatory UI: map, equipment, star map, power allocation, research
## terminal, approach buttons, credits, HUD, CRT overlay.
##
## Exercises Ren'Py patterns: unlabelled imagebuttons, SetField toggles,
## modal overlays, selected button state, smart quotes, image-only buttons,
## two-click interactions, end credits overlay.
################################################################################

################################################################################
## Background Images
################################################################################

## Background image declarations live in script.rpy. This file only defines
## reusable UI overlays and custom interaction screens.


################################################################################
## CRT Scanline Overlay
##
## Subtle retro terminal effect for boot sequences and terminal screens.
## Shows faint horizontal scanlines and a vignette-like edge darkening.
################################################################################

init python:

    class _CRTScanlines(renpy.Displayable):
        """Draws horizontal scanlines as a semi-transparent overlay."""

        def __init__(self, spacing=3, alpha=0.10, **kwargs):
            super(_CRTScanlines, self).__init__(**kwargs)
            self.spacing = spacing
            self.alpha = alpha

        def render(self, width, height, st, at):
            w, h = int(width), int(height)
            rv = renpy.Render(w, h)
            a = int(255 * self.alpha)
            for y in range(0, h, self.spacing):
                line = renpy.Render(w, 1)
                line.fill((0, 0, 0, a))
                rv.blit(line, (0, y))
            return rv

        def visit(self):
            return []

    class _TerminalSweep(renpy.Displayable):
        """Draws a runtime-driven sweep so dialogue updates do not reset it."""

        def __init__(self, width=1168, height=558, bar_width=3, **kwargs):
            super(_TerminalSweep, self).__init__(**kwargs)
            self.width = width
            self.height = height
            self.bar_width = bar_width
            self.fade_in = 0.18
            self.travel = 2.2
            self.fade_out = 0.18
            self.pause_before = 0.4
            self.pause_after = 1.2
            self.cycle = self.pause_before + self.fade_in + self.travel + self.fade_out + self.pause_after

        def render(self, width, height, st, at):
            rv = renpy.Render(self.width, self.height)
            phase = renpy.get_game_runtime() % self.cycle
            alpha = 0.0
            x = 0

            phase -= self.pause_before
            if phase >= 0:
                if phase < self.fade_in:
                    alpha = 0.50 * (phase / self.fade_in)
                else:
                    phase -= self.fade_in
                    if phase < self.travel:
                        alpha = 0.50
                        x = int((self.width - self.bar_width) * (phase / self.travel))
                    else:
                        phase -= self.travel
                        x = self.width - self.bar_width
                        if phase < self.fade_out:
                            alpha = 0.50 * (1.0 - (phase / self.fade_out))

            if alpha > 0.0:
                renpy.redraw(self, 0.033)
                for dx, multiplier in ((-5, 0.12), (-3, 0.20), (-1, 0.34), (0, 1.0), (1, 0.34), (3, 0.20), (5, 0.12)):
                    px = x + dx
                    if 0 <= px < self.width:
                        line = renpy.Render(1, self.height)
                        line.fill((102, 255, 204, int(255 * alpha * multiplier)))
                        rv.blit(line, (px, 0))
            else:
                renpy.redraw(self, 0.05)

            return rv

        def visit(self):
            return []

    _crt_scanlines = _CRTScanlines(spacing=3, alpha=0.10)
    _crt_scanlines_heavy = _CRTScanlines(spacing=2, alpha=0.18)
    _terminal_sweep = _TerminalSweep()

    def _echo_terminal_animation_tick():
        renpy.redraw(_terminal_sweep, 0.0)


screen crt_overlay(heavy=False):
    zorder 90
    on "show" action SetVariable("terminal_mode", True)
    on "hide" action SetVariable("terminal_mode", False)
    timer 0.05 action Function(_echo_terminal_animation_tick) repeat True
    add Solid("#071b2630" if not heavy else "#071b2648") at echo_terminal_flicker
    if heavy:
        add _crt_scanlines_heavy
    else:
        add _crt_scanlines
    ## Vignette: darken the edges slightly.
    add Solid("#00000000") at _crt_vignette

screen opening_location_card(
        title="AETHON DEEP SPACE OBSERVATORY",
        context="Northernmost Research Station - 71.3°N, 156.8°W",
        date_line="Date: 2 March 2047 - 03:17 UTC"):
    zorder 20

    frame:
        background None
        xpos 34
        ypos 492
        xsize 900
        ysize 150
        at echo_location_card_in

        vbox:
            spacing 12

            text title:
                font "gui/fonts/Inconsolata-Regular.ttf"
                size 27
                color "#f4fbff"
                outlines [(3, "#02070bee", 0, 0), (1, "#66ffccaa", 0, 0)]

            text context:
                font "gui/fonts/Inconsolata-Regular.ttf"
                size 22
                color "#e5f2fa"
                outlines [(3, "#02070bee", 0, 0)]

            text date_line:
                font "gui/fonts/Inconsolata-Regular.ttf"
                size 22
                color "#e5f2fa"
                outlines [(3, "#02070bee", 0, 0)]

## Station UI arrives and leaves as one layer rather than popping over the
## room. Both phases stay short because the map is navigation, not a scene
## transition. This lives on the displayables rather than on a `with` clause
## at the call site: `call screen` has to stay bare for the route flattener.
transform echo_ui_appear:
    on show:
        alpha 0.0
        linear 0.3 alpha 1.0
    on hide:
        linear 0.24 alpha 0.0

transform _crt_vignette:
    alpha 0.0

transform echo_location_card_in:
    alpha 0.0
    yoffset 10
    pause 0.25
    ease 0.75 alpha 1.0 yoffset 0

transform echo_terminal_power_on:
    alpha 0.0
    zoom 1.02
    linear 0.28 alpha 0.92 zoom 1.0
    linear 0.10 alpha 0.78
    linear 0.14 alpha 0.96
    pause 0.20
    linear 0.12 alpha 1.0

transform echo_terminal_flicker:
    alpha 0.20
    linear 0.08 alpha 0.34
    linear 0.12 alpha 0.18
    linear 0.18 alpha 0.28
    linear 0.24 alpha 0.22
    repeat

transform echo_terminal_sweep:
    alpha 0.0
    xoffset 0
    pause 0.4
    linear 0.18 alpha 0.50
    linear 2.2 xoffset 1038
    linear 0.18 alpha 0.0
    pause 1.2
    repeat

transform echo_database_sweep:
    alpha 0.0
    xoffset 0
    pause 0.35
    linear 0.16 alpha 0.45
    linear 1.7 xoffset 488
    linear 0.16 alpha 0.0
    pause 1.0
    repeat

transform echo_wave_pulse(delay=0.0):
    alpha 0.30
    pause delay
    linear 0.55 alpha 0.90
    linear 0.75 alpha 0.24
    repeat

transform echo_ui_pulse:
    alpha 0.42
    linear 0.9 alpha 0.12
    linear 0.9 alpha 0.42
    repeat

transform echo_ui_blink:
    alpha 1.0
    linear 0.45 alpha 0.35
    linear 0.45 alpha 1.0
    repeat

transform echo_corridor(angle=0):
    rotate angle
    rotate_pad False

transform echo_storm_shear(angle=0, delay=0.0):
    rotate angle
    rotate_pad False
    alpha 0.10
    pause delay
    linear 0.7 alpha 0.35
    linear 1.1 alpha 0.08
    repeat

style echo_panel_frame:
    background Solid("#06111ce8")
    xpadding 24
    ypadding 18

style echo_utility_panel_frame:
    background Solid("#030b13f2")
    xpadding 26
    ypadding 22

style echo_terminal_button is button:
    background Solid("#091a2add")
    hover_background Solid("#12314dee")
    selected_background Solid("#1c466bee")
    insensitive_background Solid("#08111aaa")
    xpadding 14
    ypadding 10

style echo_terminal_button_text is button_text:
    color "#d8f2ff"
    hover_color "#ffffff"
    selected_color "#9ee7ff"
    insensitive_color "#7d9cab"
    size 14

## Map tiles sit ON the drawn deck plan (images/ui/map_underlay.png), so the
## idle fill is a tint rather than a lid: the room's walls, floor panelling and
## fixtures have to read through it. Hover and selected still take over.
style echo_map_room_button is button:
    background Solid("#0a172548")
    hover_background Solid("#153a5ab4")
    selected_background Solid("#1f4c71a0")
    xpadding 0
    ypadding 0

## Share the rendered roof-and-drum silhouette across hover, selection and
## pointer focus, so the empty corners outside the dome stay inactive.
image echo_map_dome_mask = Transform("images/ui/map_dome_mask.png", xysize=(150, 105))

style echo_map_dome_button is echo_map_room_button:
    background None
    hover_background AlphaMask(Solid("#153a5ab4"), "echo_map_dome_mask")
    selected_background AlphaMask(Solid("#1f4c71a0"), "echo_map_dome_mask")
    focus_mask "echo_map_dome_mask"

style echo_icon_button is button:
    background Solid("#091a2add")
    hover_background Solid("#14324dee")
    selected_background Solid("#224c6aee")
    xpadding 8
    ypadding 8

style echo_icon_button_text is button_text:
    color "#d7f1ff"
    hover_color "#ffffff"
    selected_color "#a6efff"
    size 12

style echo_utility_dock_button is button:
    background Solid("#07131d80")
    hover_background Solid("#14324db8")
    selected_background Solid("#173b56d8")
    xpadding 8
    ypadding 6

style echo_utility_dock_button_text is button_text:
    font "gui/fonts/Inconsolata-Regular.ttf"
    color "#b9d9e8"
    hover_color "#ffffff"
    selected_color "#9ee7ff"
    size 11

style echo_utility_close_button is button:
    background Solid("#07131d80")
    hover_background Solid("#173b56d8")
    xpadding 12
    ypadding 7

style echo_utility_close_button_text is button_text:
    font "gui/fonts/Inconsolata-Regular.ttf"
    color "#8fb8cc"
    hover_color "#ffffff"
    size 11

style echo_star_layer_button is button:
    background Solid("#07131d9c")
    hover_background Solid("#102a3db8")
    selected_background Solid("#15364dcc")
    insensitive_background Solid("#06101970")
    xpadding 12
    ypadding 8

style echo_star_layer_button_text is button_text:
    font "gui/fonts/Inconsolata-Regular.ttf"
    color "#b9d9e8"
    hover_color "#ffffff"
    selected_color "#9ee7ff"
    insensitive_color "#587585"
    size 12

style echo_power_route_button is button:
    background Solid("#07131d9c")
    hover_background Solid("#102a3dcc")
    selected_background Solid("#3b2d1dcc")
    xpadding 10
    ypadding 7

style echo_power_route_button_text is button_text:
    font "gui/fonts/Inconsolata-Regular.ttf"
    color "#b9d9e8"
    hover_color "#ffffff"
    selected_color "#ffd3a0"
    size 12

style echo_power_apply_button is button:
    background Solid("#332516d8")
    hover_background Solid("#573b1bea")
    xpadding 18
    ypadding 10

style echo_power_apply_button_text is button_text:
    font "gui/fonts/Inconsolata-Regular.ttf"
    color "#ffd3a0"
    hover_color "#fff2df"
    size 13

style echo_database_button is button:
    background Solid("#091a2add")
    hover_background Solid("#12314dee")
    insensitive_background Solid("#08111aaa")
    xpadding 14
    ypadding 12
    xfill True

style echo_database_button_text is button_text:
    font "gui/fonts/Inconsolata-Regular.ttf"
    color "#d8f2ff"
    hover_color "#ffffff"
    insensitive_color "#7d9cab"
    size 17


################################################################################
## Data Definitions
################################################################################

init python:

    ## Every KIT item names WHERE it is spent and WHAT it buys (freeplay
    ## live-run item: the run ended with the player unsure what any of it
    ## was for).
    _equipment_descriptions = {
        "power_cell": "Charged reserve cell. Load into the GENERATOR auxiliary bus for about an hour of station-wide warmth — or spend at COMMS to boost the signal window. One cell, one use.",
        "data_drive": "Removable crystalline drive. Archive the evidence log at the LAB console — a sealed copy with chain-of-custody hashes.",
        "antenna_part": "Spare coupling for antenna module 2. Supports either the local generator bypass or the permanent exterior repair.",
        "coolant_cartridge": "Thermal coolant cartridge. Install in ARIA's cluster loop at the LAB to bring her core clusters back inside tolerance.",
        "signal_amp": "RF preamplifier, still bagged. Fit at the COMMS bench to lift the array's reception.",
    }

    _star_region_descriptions = {
        "known_sources": "Standard radio sources \u2014 pulsars, quasars, satellite transponders. All catalogued and accounted for.",
        "signal_origin": "Bearing 287.4 - anomalous signal origin. No known source in any stellar catalog matches this position.",
        "anomaly_cluster": "A cluster of faint anomalies detected in the past 72 hours. Possible temporal resonance echoes.",
    }

    def echo_equipment_description(item):
        if item == "data_drive" and echo7_designation_known:
            return "High-capacity crystalline drives for storing ECHO-7 transmissions."
        return _equipment_descriptions.get(item, "")

    def echo_star_region_description(region):
        if region == "signal_origin" and echo7_designation_known:
            return "Bearing 287.4 - ECHO-7's signal origin. No known source in any stellar catalog matches this position."
        return _star_region_descriptions.get(region, "")

    def echo_weather_label(intensity):
        if intensity <= 0:
            return "Clear"
        if intensity == 1:
            return "Snow"
        if intensity == 2:
            return "Storm"
        return "Blizzard"

    def echo_time_left_label(minutes):
        minutes = max(0, int(minutes))
        hours = minutes // 60
        mins = minutes % 60
        if hours > 0:
            return "{}h {:02d}m left".format(hours, mins)
        return "{}m left".format(mins)

    def echo_thermal_status(intensity, priority, aux_minutes):
        """Derived station condition; the story has no Celsius simulation."""
        if int(aux_minutes) > 0:
            return ("THERMAL  AUX HEAT · {}m".format(int(aux_minutes)), "#8ee8b4")
        if priority == "heating":
            return ("THERMAL  HEATING PRIORITY", "#8ee8b4")
        if int(intensity) >= 3:
            return ("THERMAL  SEVERE COLD", "#ff8f82")
        if int(intensity) >= 2:
            return ("THERMAL  COLD LOAD", "#ffbd6b")
        return ("THERMAL  NOMINAL", "#8ccff7")

    def echo_storm_meter_color(intensity):
        if int(intensity) >= 3:
            return "#ff796d"
        if int(intensity) >= 2:
            return "#ff9a78"
        if int(intensity) >= 1:
            return "#ffbd6b"
        return "#6fe4ff"

    def echo_storm_meter_label(intensity, eta):
        if int(intensity) > 0:
            return "STORM {}/3  PEAK {}".format(int(intensity), eta.replace(" ", ""))
        return "STORM PEAK IN  {}".format(eta)


################################################################################
## ECHO-7 Question Bank
##
## The comms exchange runs inside the live terminal, so the questions are data
## rather than a screen: echo_terminal_choice renders them into the log, and
## the SAME caption is the line Elara types back. That is what keeps the
## transcript readable as a conversation instead of answers with no questions.
##
## Pattern: conditional menu items, built in Python instead of screen language.
################################################################################

init python:
    ## The question bank as a declarative graph (user design 2026-08-17).
    ## Each node: caption + the conditions that admit it. Two condition
    ## kinds, kept separate on purpose:
    ##   requires_flags — EXTERNAL store facts (named as strings so tests
    ##       can statically audit that every flag has a real setter);
    ##   requires_asked — INTERNAL edges (question B needs question A asked
    ##       first; the vulnerability explanation uses this two-step path).
    ## `min_visit` is an opening window, not a room: unasked questions
    ## CARRY FORWARD to later visits (user decision — the old visit-pools
    ## silently destroyed unasked questions when the visit advanced; a
    ## compressed-visits player lost four without ever seeing them).
    ## `carries_until` (2026-08-18 user refinement: "not all should
    ## migrate to different storm stages — some could") bounds that
    ## window: the node is offered while visit <= carries_until (default
    ## 3 = full carry). A question of its MOMENT expires with the moment;
    ## the timeless ones keep the standing rule.
    ## `reconnect` nodes are the blocked-then-unblocked catch-up set and
    ## only appear for that player. "Asked once = asked for good" stays.
    ECHO7_QUESTION_GRAPH = [
        {"id": "late_catchup",     "min_visit": 1, "reconnect": True,
         "caption": u"Start over. What are you claiming is happening?"},
        {"id": "late_believe",     "min_visit": 1, "reconnect": True,
         "excludes_flags": ["knows_prediction_evidence"],
         "caption": u"Give me something I can verify."},
        {"id": "late_need",        "min_visit": 1, "reconnect": True,
         "caption": u"Assume you are from the future. What do you want?"},

        ## Technical follow-ups belong to the audience in which Elara opens
        ## them. They do not return as stale agenda items on a later night.
        {"id": "analytical_mechanism", "min_visit": 1, "carries_until": 2,
         "caption": u"How is this possible? How are you talking to me from the future?"},
        {"id": "analytical_proof", "min_visit": 1, "carries_until": 2,
         "thread": "temporal", "requires_session_asked": ["analytical_mechanism"],
         "caption": u"Show me the mathematical proof of temporal displacement."},
        {"id": "analytical_error", "min_visit": 1, "carries_until": 2,
         "thread": "temporal", "requires_session_asked": ["analytical_mechanism"],
         "caption": u"What’s the error margin on your predictions?"},
        {"id": "empathetic_cascade", "min_visit": 1, "min_storm": 1,
         "requires_flags": ["knows_cascade"],
         "caption": u"How do you know what happened after my time?"},
        {"id": "cautious_verify",  "min_visit": 1, "carries_until": 2,
         "thread": "temporal", "requires_session_asked": ["analytical_mechanism"],
         "excludes_flags": ["origin_sweep_staged", "origin_sweep_running",
                             "origin_sweep_done", "knows_prediction_evidence"],
         "caption": u"How do I verify any of this independently?"},
        ## Once ECHO-7 has named the file, Elara can ask for its purpose without
        ## accepting the accusation on faith. The practical approach is an
        ## included follow-up: motive first, method second.
        {"id": "file_motive", "min_visit": 1,
         "requires_flags": ["knows_convergence_file"],
         "excludes_flags": ["coherence_found", "file_recovered"],
         "caption": u"Why do you want me to find CONVERGENCE.DAT?"},
        {"id": "file_method", "min_visit": 1,
         "requires_flags": ["knows_convergence_file"],
         "excludes_flags": ["coherence_found", "file_recovered"],
         "thread": "file_search", "requires_session_asked": ["file_motive"],
         "caption": u"If you were here, how would you look for it?"},
        ## Once Elara has the actual file, she can ask why its exploit passed
        ## safeguards she has now seen it target. Before that, a broad opinion
        ## about the Protocol sounds like the story asking its own question.
        {"id": "cautious_protocol", "min_visit": 2,
         "requires_flags": ["marcus_first_accused"],
         "requires_any_flags": ["coherence_found", "file_recovered"],
         "caption": u"CONVERGENCE passed the Trust Protocol. Why didn't the safeguards stop it?"},

        ## Direct answer to the second-audience opener: ECHO-7 says it must
        ## tell her about Marcus, so Elara can ask for exactly that instead of
        ## spending an unrelated question before the automatic reveal.
        {"id": "marcus_warning", "min_visit": 2, "carries_until": 2,
         "excludes_flags": ["marcus_first_accused"],
         "caption": u"What do you want to tell me?"},
        ## Knowledge before jargon: knowing a filename does not mean Elara has
        ## seen its contents. The accusation first establishes that Marcus has
        ## a way through the Trust Protocol; she can ask what that means, then
        ## drill into the implementation as a real follow-up.
        {"id": "analytical_vuln",  "min_visit": 2,
         "requires_flags": ["marcus_first_accused"],
         "caption": u"You said Marcus found a way through ARIA’s Trust Protocol. What does it do?"},
        {"id": "analytical_vuln_technical", "min_visit": 2,
         "requires_flags": ["marcus_first_accused"],
         "thread": "trust_protocol", "requires_session_asked": ["analytical_vuln"],
         "caption": u"Show me the technical mechanism."},
        {"id": "analytical_code",  "min_visit": 2,
         "requires_flags": ["knows_convergence_file", "marcus_first_accused"],
         "specialization": "computing",
         "caption": u"Give me a specific code check I can verify locally."},
        ## The mug test is the first concrete sign that ECHO-7 knows Elara
        ## personally. This follow-up challenges that specific slip.
        {"id": "cautious_trust",   "min_visit": 3, "min_storm": 2,
         "thread": "mug", "requires_asked": ["cautious_test"],
         "caption": u"I never told anyone about the mug."},
        ## The trace threat is a second-audience moment; once the night is
        ## deciding itself it reads as posturing (carries_until 2).
        {"id": "cautious_trace",   "min_visit": 2, "specialization": "signals",
         "carries_until": 2,
         "caption": u"I can trace your signal origin. You know that."},
        {"id": "cautious_alert", "min_visit": 2, "requires_flags": ["marcus_first_accused"],
         "caption": u"If ARIA goes through his partition — won't he know?"},

        ## Marcus's outcome opens at visit 3, gated on the accusation. Elara
        ## asks what the future records say; she does not assume a probe knew
        ## him personally.
        {"id": "empathetic_marcus", "min_visit": 3, "min_storm": 2,
         "requires_flags": ["marcus_first_accused"],
         "caption": u"What happened to Marcus in your timeline?"},
        ## A late personal question stays reciprocal rather than assuming an
        ## intimacy the player may not feel. Its response offers free stances.
        {"id": "echo7_stakes", "min_visit": 3, "min_storm": 2,
         "requires_flags": ["knows_cascade"],
         "caption": u"If I succeed, what happens to you?"},
        {"id": "cautious_test",    "min_visit": 3, "min_storm": 2,
         "min_questions_asked": 1,
         "caption": u"Tell me something only I should know."},
    ]

    ECHO7_QUESTIONS = dict(
        (node["id"], node["caption"]) for node in ECHO7_QUESTION_GRAPH
    )

    ECHO7_THREAD_NAVIGATION = [
        ("temporal", "analytical_mechanism", u"Return to the temporal mechanics."),
        ("trust_protocol", "analytical_vuln", u"Return to the Trust Protocol details."),
        ("file_search", "file_motive", u"Return to finding CONVERGENCE.DAT."),
        ("mug", "cautious_test", u"Return to the mug."),
    ]

    def echo7_question_caption(token):
        if token == "cautious_alert" and getattr(store, "marcus_locked_partition", False):
            return "Marcus sealed his partition. Did the search alert him?"
        if token == "cautious_alert" and (getattr(store, "marcus_told_search", False) or getattr(store, "marcus_search_stance", "unaware") != "unaware"):
            return "Marcus knows about the search. What can he do now?"
        return ECHO7_QUESTIONS.get(token, "")

    def echo7_node_available(node, visit, reconnect, asked, session_asked=()):
        if node["id"] in asked:
            return False
        if node.get("reconnect") and not reconnect:
            return False
        ## A late-reconnect player's first window is the catch-up set alone —
        ## the compressed recap must not be diluted by the ordinary pool
        ## (which opens for them from visit 2, carry-forward included).
        if reconnect and visit == 1 and not node.get("reconnect"):
            return False
        if visit < node.get("min_visit", 1):
            return False
        if visit > node.get("carries_until", 3):
            return False
        if getattr(store, "storm_intensity", 0) < node.get("min_storm", 0):
            return False
        if len(asked) < node.get("min_questions_asked", 0):
            return False
        for flag in node.get("requires_flags", ()):
            if not getattr(store, flag, False):
                return False
        any_flags = node.get("requires_any_flags", ())
        if any_flags and not any(getattr(store, flag, False) for flag in any_flags):
            return False
        for flag in node.get("excludes_flags", ()):
            if getattr(store, flag, False):
                return False
        for prior in node.get("requires_asked", ()):
            if prior not in asked:
                return False
        for prior in node.get("requires_session_asked", ()):
            if prior not in session_asked:
                return False
        for prior in node.get("excludes_asked", ()):
            if prior in asked:
                return False
        spec = node.get("specialization")
        if spec and specialization != spec:
            return False
        return True

    def echo7_question_options(visit=1, reconnect=False, asked=(),
                               session_asked=(), thread=None, can_end=False,
                               end_caption=None):
        """Question list for this comms visit, as (token, caption) pairs.

        `asked` is echo7_asked_ever, so a question asked once is asked for
        good -- no re-ask farming of trust or evidence across visits.
        This visit's newly opened questions lead; carried-forward leftovers
        from earlier windows follow, in their original order.
        """
        fresh = []
        carried = []
        for node in ECHO7_QUESTION_GRAPH:
            node_thread = node.get("thread")
            if thread:
                if node_thread != thread:
                    continue
            elif node_thread:
                ## Thread children never leak into the general question list.
                ## "Ask something else" leaves that subtopic; it does not turn
                ## every contextual follow-up into a root-level agenda item.
                continue
            if not echo7_node_available(node, visit, reconnect, asked,
                                        session_asked):
                continue
            entry = (node["id"], echo7_question_caption(node["id"]))
            if node.get("min_visit", 1) >= min(visit, 3):
                fresh.append(entry)
            else:
                carried.append(entry)
        options = fresh + carried

        ## Leaving a thread returns to a clean root list, but it is not a
        ## one-way door. While this audience remains open, an answered opener
        ## with unanswered children contributes one explicit topic-return row.
        if not thread:
            for thread_id, opener, caption in ECHO7_THREAD_NAVIGATION:
                if opener not in session_asked:
                    continue
                has_followup = any(
                    node.get("thread") == thread_id
                    and echo7_node_available(
                        node, visit, reconnect, asked, session_asked)
                    for node in ECHO7_QUESTION_GRAPH
                )
                if has_followup:
                    options.append(("thread:" + thread_id, caption))

        ## A technical subthread is contextual navigation, not a paid query.
        ## The player can return to the ordinary audience without consuming
        ## time, signal, or one of the carrier's question slots.
        if thread:
            options.append(("other", u"Ask something else."))

        ## An exhausted pool must never leave the log with nothing to click,
        ## even when the caller did not ask for an exit.
        if can_end or not options:
            options.append(("done", end_caption or u"End transmission."))

        return options


################################################################################
## Observatory Map
##
## Modal map with directional imagebuttons (unlabelled).
## Pattern: unlabelled imagebuttons, modal overlay, map/travel screen.
################################################################################

screen observatory_map():
    modal False

    ## THE MAP IS AN OVERLAY OVER THE ROOM (2026-08-17, presentation stage 4).
    ## It used to draw a ghost of bg_observatory at alpha 0.28 under its own
    ## wash, because it ran over a corridor scene the hub laid for it and the
    ## ghost was doing the corridor's job twice. The hub lays no scene now — the
    ## room she is leaving is the backdrop — so the ghost is gone and only the
    ## wash remains: the lights come down in whatever room she is standing in,
    ## and the plan table lights up. Screenshot-checked over bg_lab, bg_comms,
    ## bg_generator and bg_observatory; the wash is deep enough that the plan
    ## reads identically over all four while the room stays legible at the
    ## edges, which is the whole point of not cutting away from it.
    add Solid("#020712e0") at echo_ui_appear

    frame:
        at echo_ui_appear
        xalign 0.5 yalign 0.5
        style "echo_panel_frame"
        xsize 700 ysize 560

        text "{b}AETHON OBSERVATORY{/b}" xalign 0.5 ypos 6 size 16 color "#b8eeff"
        text "STORM ROUTING MAP // INTERNAL ACCESS ONLY" xalign 0.5 ypos 28 size 10 color "#6aa9c980"

        fixed:
            xpos 25 ypos 54 xsize 650 ysize 430

            ## Static site plan: exterior module shells, enclosed passages,
            ## and snow contours. Pre-rendered at 2x
            ## by tools/render_map.py, which holds the same room
            ## rectangles the buttons below use -- the drawing and the
            ## interaction layer only read as one map while they agree, so a
            ## geometry change here is a re-render there.
            add "images/ui/map_underlay.png" xysize (650, 430) pos (0, 0)

            ## Exterior service rails: the exposed array bridge and the lower
            ## utility apron are the two paths the storm shears run
            ## along. Dimmer than they were, now that a drawn plan sits under
            ## them — at storm 0 they should read as faint structure, not as
            ## marks on the drawing.
            add Solid("#ff805010", xysize=(78, 7)) pos (532, 267) at echo_corridor(24)
            add Solid("#ff80500c", xysize=(118, 7)) pos (385, 355) at echo_corridor(-8)

            if storm_intensity > 0:
                add Solid("#ff805020", xysize=(120, 6)) pos (520, 274) at echo_storm_shear(18, 0.0)
                add Solid("#ff805018", xysize=(105, 5)) pos (50, 185) at echo_storm_shear(-10, 0.35)
                add Solid("#ff668820", xysize=(65, 5)) pos (570, 150) at echo_storm_shear(70, 0.7)
            if storm_intensity > 1:
                add Solid("#ff884426", xysize=(180, 5)) pos (390, 355) at echo_storm_shear(-8, 0.15)
                add Solid("#ff66881c", xysize=(100, 4)) pos (80, 360) at echo_storm_shear(12, 0.55)
            if storm_intensity > 2:
                add Solid("#ff44442e", xysize=(210, 6)) pos (205, 50) at echo_storm_shear(-6, 0.25)
                add Solid("#ff44442a", xysize=(200, 6)) pos (220, 385) at echo_storm_shear(6, 0.65)

            $ _tele_here = current_location == "telescope"
            $ _lab_here = current_location == "lab"
            $ _comms_here = current_location == "comms"
            $ _gen_here = current_location == "generator"
            $ _hab_here = current_location == "habitat"
            $ _sto_here = current_location == "storage"
            $ _sto_parts_lead = marcus_eva_waiting_for_parts and not storage_supplies_found
            ## Two-person station: you generally know where the other one is.
            $ _marcus_at = eot_marcus_location()
            ## Late in the night Marcus remains reachable through ordinary
            ## station geography: COMMS while he works its cable run, then LAB
            ## while he reads at the side console. The marker therefore stays
            ## on the same room button the player uses to reach him.

            if _tele_here:
                add AlphaMask(Solid("#79d7ff28"), "echo_map_dome_mask") pos (260, 68) xysize (150, 105) at echo_ui_pulse
            if _lab_here:
                add Solid("#79d7ff28", xysize=(150, 108)) pos (180, 180) at echo_ui_pulse
            if _comms_here:
                add Solid("#79d7ff28", xysize=(120, 82)) pos (480, 180) at echo_ui_pulse
            if _gen_here:
                add Solid("#ffbd6b24", xysize=(118, 72)) pos (410, 276) at echo_ui_pulse
            if _hab_here:
                add Solid("#79d7ff28", xysize=(126, 76)) pos (28, 205) at echo_ui_pulse

            ## Room names stay on the tiles; contextual subtitles move to the
            ## shared hover line below the map. The Echoes vnflight mod emits
            ## those same strings as button annotations for agent parity.
            button:
                style "echo_map_room_button"
                selected _hab_here
                pos (28, 205) xysize (126, 76)
                action [SetVariable("hud_map_open", False), Return("habitat")]
                tooltip ("Warmest room left" if storm_intensity >= 3 else "Canteen & quarters")
                has fixed
                add "images/ui/icon_habitat.png" xpos 7 yalign 0.5 xysize (34, 34)
                text "HABITAT" xpos 43 yalign 0.5 size 11 color "#d8f2ff"

            if _sto_here:
                add Solid("#79d7ff28", xysize=(126, 62)) pos (28, 294) at echo_ui_pulse
            elif _sto_parts_lead:
                add Solid("#ffbd6b2e", xysize=(126, 62)) pos (28, 294) at echo_ui_pulse

            button:
                style "echo_map_room_button"
                selected _sto_here
                pos (28, 294) xysize (126, 62)
                action [SetVariable("hud_map_open", False), Return("storage")]
                tooltip ("Emergency rack — array couplings" if _sto_parts_lead else "Requisitions")
                has fixed
                add "images/ui/icon_storage.png" xpos 7 yalign 0.5 xysize (32, 32)
                text "STORAGE" xpos 41 yalign 0.5 size 11 color ("#ffd18a" if _sto_parts_lead else "#d8f2ff")

            frame:
                pos (552, 288) xysize (84, 62)
                background Solid("#2a0d0b3c")
                xpadding 0 ypadding 0
                text "ARRAY\nGANTRY" xalign 0.5 yalign 0.62 text_align 0.5 size 9 color "#ff9a7880"
                add "images/ui/icon_storm.png" xalign 0.5 ypos 2 xysize (20, 20) alpha 0.55
                if storm_intensity > 0:
                    add Solid("#ff805022", xysize=(78, 56)) pos (3, 3) at echo_ui_pulse

            frame:
                pos (342, 195) xysize (68, 78)
                background None
                xpadding 0 ypadding 0
                text "CENTRAL\nCORRIDOR" xalign 0.5 yalign 0.5 text_align 0.5 size 9 color "#d8f2ff80"

            button:
                style "echo_map_dome_button"
                selected _tele_here
                pos (260, 68) xysize (150, 105)
                action [SetVariable("hud_map_open", False), Return("telescope")]
                tooltip ("Storm telemetry" if storm_intensity >= 2 else "Observation dome")
                has fixed
                add "images/ui/icon_telescope.png" xpos 18 yalign 0.68 xysize (40, 40)
                text "TELESCOPE" xpos 60 yalign 0.68 size 11 color "#b8d7ff"

            button:
                style "echo_map_room_button"
                selected _lab_here
                pos (180, 180) xysize (150, 108)
                action [SetVariable("hud_map_open", False), Return("lab")]
                tooltip "ARIA station"
                has fixed
                add "images/ui/icon_lab.png" xpos 9 yalign 0.5 xysize (50, 50)
                text "LAB" xpos 62 yalign 0.5 size 12 color "#b8eeff"

            button:
                style "echo_map_room_button"
                selected _comms_here
                pos (480, 180) xysize (120, 82)
                action [SetVariable("hud_map_open", False), Return("comms")]
                tooltip ("ARRAY DAMAGED" if antenna_damaged and not generator_repaired else "Temporary reroute under strain" if antenna_reroute_active else "Antenna repaired" if antenna_damaged else "Antenna array")
                has fixed
                add "images/ui/icon_comms.png" xpos 7 yalign 0.5 xysize (42, 42)
                text "COMMS" xpos 51 yalign 0.5 size 11 color "#a8ffd0"
                if antenna_damaged and not generator_repaired:
                    add "images/ui/icon_storm.png" xpos 91 ypos 6 xysize (24, 24) at echo_ui_blink

            button:
                style "echo_map_room_button"
                selected _gen_here
                pos (410, 276) xysize (118, 72)
                action [SetVariable("hud_map_open", False), Return("generator")]
                tooltip (("Reroute ready" if antenna_parts > 0 else "Coupling required") if antenna_damaged and not generator_repaired else "Power systems")
                has fixed
                add "images/ui/icon_generator.png" xpos 6 yalign 0.5 xysize (40, 40)
                text "GENERATOR" xpos 47 yalign 0.5 size 9 color "#ffd3a0"
                if antenna_damaged and not generator_repaired:
                    add "images/ui/icon_storm.png" xpos 91 ypos 5 xysize (22, 22) at echo_ui_blink

            ## Marcus sits on the destination he can actually be reached
            ## through. About three fifths of the portrait stays inside the
            ## room; the remainder crosses its lower-right boundary so it
            ## reads as a presence badge rather than room equipment.
            if _marcus_at == "lab":
                add "images/ui/icon_marcus.png" pos (302, 255) xysize (42, 42)
            elif _marcus_at == "comms":
                add "images/ui/icon_marcus.png" pos (568, 229) xysize (42, 42)
            elif _marcus_at == "generator":
                add "images/ui/icon_marcus.png" pos (496, 315) xysize (42, 42)
            elif _marcus_at == "habitat":
                add "images/ui/icon_marcus.png" pos (122, 248) xysize (42, 42)
            elif _marcus_at == "storage":
                add "images/ui/icon_marcus.png" pos (122, 324) xysize (42, 42)

        $ _map_tooltip = GetTooltip()
        if _map_tooltip:
            text "[_map_tooltip]" xalign 0.5 yalign 0.91 size 13 color "#9ee7ff"
        else:
            text "Select station section" xalign 0.5 yalign 0.91 size 13 color "#5d859d"

        ## Corridor waiting removed (cost-legibility round 3): waiting belongs
        ## in the rooms. act2_hub still guards Return("stay") at zero cost —
        ## an auto-advance mis-dismiss of this screen can synthesize it.

        ## The old "Go find Marcus" verb stays retired. His marker rides COMMS
        ## or LAB late in the night, and those rooms expose the conversation.


################################################################################
## Equipment Screen (Modal)
##
## Inventory with image-only item buttons.
## Pattern: unlabelled imagebuttons, modal overlay, image-only buttons,
##          inventory detail scanning (click to select, detail shows below).
################################################################################

screen echo_utility_header(icon, title, subtitle, close_screen, accent):

    fixed:
        xfill True ysize 54
        hbox:
            spacing 10
            add icon xysize (34, 34) yalign 0.5
            vbox:
                spacing 0
                text title:
                    font "gui/fonts/Inconsolata-Regular.ttf"
                    size 17 color "#d8f2ff"
                text subtitle:
                    font "gui/fonts/Inconsolata-Regular.ttf"
                    size 10 color "#668ba0"
        textbutton "CLOSE":
            xalign 1.0 yalign 0.0
            action Hide(close_screen)
            style "echo_utility_close_button"
        frame:
            xfill True ysize 1 yalign 1.0
            background Solid(accent)


screen equipment_screen():
    modal True
    on "show" action SetVariable("selected_item", None)

    add Solid("#020712b8")

    frame:
        xalign 0.5 yalign 0.5
        style "echo_utility_panel_frame"
        xsize 740

        vbox:
            spacing 14

            use echo_utility_header(
                "images/ui/icon_power_cell.png", "FIELD KIT",
                "AETHON // PERSONNEL ISSUE", "equipment_screen", "#6fe4ff70")

            frame:
                xfill True
                background Solid("#07131d70")
                xpadding 14 ypadding 14

                hbox:
                    spacing 12
                    xalign 0.5

                    vbox:
                        spacing 5
                        button:
                            style "echo_icon_button"
                            selected selected_item == "power_cell"
                            xysize (108, 96)
                            action SetVariable("selected_item", "power_cell")
                            add "images/ui/icon_power_cell.png" xalign 0.5 yalign 0.5 xysize (66, 66)
                        text "POWER CELL" xalign 0.5 size 11 color "#d8f2ff"
                        text "x[power_cells]" xalign 0.5 size 11 color "#8ccff7"

                    vbox:
                        spacing 5
                        button:
                            style "echo_icon_button"
                            selected selected_item == "data_drive"
                            xysize (108, 96)
                            action SetVariable("selected_item", "data_drive")
                            add "images/ui/icon_data_drive.png" xalign 0.5 yalign 0.5 xysize (66, 66)
                        text "DATA DRIVE" xalign 0.5 size 11 color "#d8f2ff"
                        text "x[data_drives]" xalign 0.5 size 11 color "#8ee8b4"

                    vbox:
                        spacing 5
                        button:
                            style "echo_icon_button"
                            selected selected_item == "antenna_part"
                            xysize (108, 96)
                            action SetVariable("selected_item", "antenna_part")
                            add "images/ui/icon_antenna_part.png" xalign 0.5 yalign 0.5 xysize (66, 66)
                        text "COUPLING" xalign 0.5 size 11 color "#d8f2ff"
                        text "x[antenna_parts]" xalign 0.5 size 11 color "#ffd19a"

                    if coolant_cartridges > 0:
                        vbox:
                            spacing 5
                            button:
                                style "echo_icon_button"
                                selected selected_item == "coolant_cartridge"
                                xysize (108, 96)
                                action SetVariable("selected_item", "coolant_cartridge")
                                add "images/ui/icon_aria.png" xalign 0.5 yalign 0.5 xysize (66, 66)
                            text "COOLANT" xalign 0.5 size 11 color "#d8f2ff"
                            text "x[coolant_cartridges]" xalign 0.5 size 11 color "#8ee8b4"

                    if signal_amps > 0:
                        vbox:
                            spacing 5
                            button:
                                style "echo_icon_button"
                                selected selected_item == "signal_amp"
                                xysize (108, 96)
                                action SetVariable("selected_item", "signal_amp")
                                add "images/ui/icon_signal.png" xalign 0.5 yalign 0.5 xysize (66, 66)
                            text "RF PREAMP" xalign 0.5 size 11 color "#d8f2ff"
                            text "x[signal_amps]" xalign 0.5 size 11 color "#8ccff7"

            if aux_power_remaining > 0:
                text "AUXILIARY BUS — ~[aux_power_remaining] min of reserve warmth" xalign 0.5 size 12 color "#8ee8b4"

            if selected_item:
                frame:
                    xfill True
                    background Solid("#07131db0")
                    xpadding 14 ypadding 10
                    text echo_equipment_description(selected_item) xalign 0.5 size 14 color "#d8f2ff"


################################################################################
## Star Map (Modal)
##
## Image-only constellation region buttons.
## Pattern: unlabelled imagebuttons, modal overlay, image-only buttons.
################################################################################

screen star_map_screen():
    zorder 110
    modal True

    ## Instrument commit rows quote the amount this exact click will remove
    ## from the night. Keep the nominal values in hub_telescope for the shared
    ## spend routine; these are the already-taxed display/admission values.
    $ _origin_commit_minutes = eot_cold_taxed(30 if specialization in ("signals", "physics") else 45)
    $ _cluster_commit_minutes = eot_cold_taxed(15)
    $ _baseline_commit_minutes = eot_cold_taxed(5)

    add Solid("#020712f2")

    frame:
        xalign 0.5 yalign 0.5 xsize 900 ysize 590
        style "echo_utility_panel_frame"

        vbox:
            spacing 12

            fixed:
                xfill True ysize 54
                hbox:
                    spacing 10
                    add "images/ui/icon_telescope.png" xysize (34, 34) yalign 0.5
                    vbox:
                        spacing 0
                        text "STAR MAP":
                            font "gui/fonts/Inconsolata-Regular.ttf"
                            size 17 color "#d8f2ff"
                        text "DOME ARCHIVE // BEARING ANALYSIS":
                            font "gui/fonts/Inconsolata-Regular.ttf"
                            size 10 color "#668ba0"
                textbutton "CLOSE":
                    xalign 1.0 yalign 0.0
                    action Return(None)
                    style "echo_utility_close_button"
                frame:
                    xfill True ysize 1 yalign 1.0
                    background Solid("#6fe4ff70")

            fixed:
                xalign 0.5 xsize 848 ysize 220
                add Solid("#020b13e8")

                for _x in (106, 212, 318, 424, 530, 636, 742):
                    add Solid("#31516a30", xysize=(1, 174)) pos (_x, 24)
                for _y in (58, 102, 146, 190):
                    add Solid("#31516a30", xysize=(800, 1)) pos (24, _y)

                text "AZIMUTH 287.4\u00b0" xpos 16 ypos 7 size 9 color "#60879b"
                text "ELEVATION 41.2\u00b0" xpos 832 ypos 7 xanchor 1.0 size 9 color "#60879b"
                text "ARCHIVE 72H" xpos 16 ypos 201 size 8 color "#456779"
                text "J2000 // LOCAL FRAME" xpos 832 ypos 201 xanchor 1.0 size 8 color "#456779"

                add Solid("#b8eeff", xysize=(3, 3)) pos (91, 72)
                add Solid("#8ccff7", xysize=(2, 2)) pos (176, 132)
                add Solid("#b8eeff", xysize=(4, 4)) pos (286, 53)
                add Solid("#8ccff7a0", xysize=(2, 2)) pos (458, 158)
                add Solid("#b8eeff", xysize=(3, 3)) pos (548, 88)
                add Solid("#8ccff7", xysize=(2, 2)) pos (677, 171)
                add Solid("#b8eeff", xysize=(3, 3)) pos (765, 112)

                add Solid("#7dffad90", xysize=(4, 4)) pos (620, 145) at echo_ui_pulse
                add Solid("#7dffad70", xysize=(3, 3)) pos (659, 121) at echo_ui_pulse
                add Solid("#7dffad60", xysize=(3, 3)) pos (705, 158) at echo_ui_pulse
                if selected_region == "anomaly_cluster":
                    add Solid("#7dffad28", xysize=(116, 64)) pos (602, 105)
                    add Solid("#7dffad70", xysize=(74, 1)) pos (620, 147)

                add Solid("#ff668828", xysize=(128, 1)) pos (327, 108)
                add Solid("#ff668828", xysize=(1, 128)) pos (391, 44)
                add Solid("#ff6688", xysize=(7, 7)) pos (388, 105) at echo_ui_pulse
                if selected_region == "signal_origin":
                    add Solid("#ff668870", xysize=(50, 1)) pos (366, 108)
                    add Solid("#ff668870", xysize=(1, 50)) pos (391, 83)
                    text ("ECHO-7 CARRIER" if echo7_designation_known else "UNRESOLVED CARRIER") xpos 404 ypos 116 size 9 color "#ff9aac"
                elif selected_region == "known_sources":
                    add Solid("#6fe4ff80", xysize=(38, 1)) pos (72, 73)
                    add Solid("#6fe4ff80", xysize=(1, 38)) pos (91, 54)

            hbox:
                spacing 12
                xalign 0.5

                button:
                    style "echo_star_layer_button"
                    selected selected_region == "known_sources"
                    sensitive not star_map_known_sources_logged
                    xysize (266, 60)
                    action SetVariable("selected_region", "known_sources")
                    has fixed
                    text "CATALOG BASELINE" ypos 0 style "echo_star_layer_button_text"
                    text ("LOGGED" if star_map_known_sources_logged else "REFERENCE FIELD // SELECT") ypos 24 size 9 color ("#7dffad" if star_map_known_sources_logged else "#6f9db5")

                button:
                    style "echo_star_layer_button"
                    selected selected_region == "signal_origin"
                    sensitive not star_map_origin_analyzed
                    xysize (266, 60)
                    action SetVariable("selected_region", "signal_origin")
                    has fixed
                    text ("ECHO-7 CARRIER" if echo7_designation_known else "RECORDED CARRIER") ypos 0 style "echo_star_layer_button_text"
                    text ("ANALYZED" if star_map_origin_analyzed else "ARCHIVE RECORD // SELECT") ypos 24 size 9 color ("#7dffad" if star_map_origin_analyzed else "#a97888")

                button:
                    style "echo_star_layer_button"
                    selected selected_region == "anomaly_cluster"
                    sensitive not star_map_anomalies_correlated
                    xysize (266, 60)
                    action SetVariable("selected_region", "anomaly_cluster")
                    has fixed
                    text "ANOMALY CLUSTER" ypos 0 style "echo_star_layer_button_text"
                    text ("CORRELATED" if star_map_anomalies_correlated else "72-HOUR RECORD // SELECT") ypos 24 size 9 color ("#7dffad" if star_map_anomalies_correlated else "#659f7e")

            ## Free browsing (2026-08-15, twice-reported live-run bug). The three
            ## region buttons above only select — they cost nothing and read as
            ## browsing, which is what they are. What they do NOT do any more is
            ## arm the exit: "Close" used to Return(True) and let hub_telescope
            ## charge for whichever region happened to be selected, so the one
            ## control that universally means "dismiss" was a 15-45 minute spend
            ## with an integrity drain behind it. Closing is now free, and the
            ## observation is its own button, named for the work and priced in
            ## the room-wait diction. LOCKSTEP with hub_telescope's
            ## _telescope_minutes: 5 known sources / 15 anomalies / 30 signals
            ## and physics, 45 otherwise for the origin trace.
            ## Reserve the description and commit-action track before a layer
            ## is selected, so populating it cannot resize or recenter the UI.
            if not selected_region:
                null height 108
            if selected_region:
                frame:
                    xfill True
                    background Solid("#091a2add")
                    xpadding 14 ypadding 10
                    text echo_star_region_description(selected_region) xalign 0.5 size 14 color "#d8f2ff"

                null height 8
                if selected_region == "signal_origin":
                    ## PURPOSE SPLIT (2026-08-18, user review): this is desk
                    ## analysis of the RECORDED carrier — the old "origin
                    ## trace" wording made it sound like the dome's live
                    ## integration (the three-numbers confusion). LOCKSTEP
                    ## with hub_telescope's _telescope_minutes and ARIA's
                    ## desk-work quote.
                    textbutton "ANALYZE CARRIER // [_origin_commit_minutes] MIN" xalign 0.5 action Return("signal_origin") sensitive eot_deadline_allows_minutes(_origin_commit_minutes, already_taxed=True) style "echo_terminal_button"
                elif selected_region == "anomaly_cluster":
                    textbutton "CORRELATE CLUSTER // [_cluster_commit_minutes] MIN" xalign 0.5 action Return("anomaly_cluster") sensitive eot_deadline_allows_minutes(_cluster_commit_minutes, already_taxed=True) style "echo_terminal_button"
                else:
                    textbutton "LOG BASELINE // [_baseline_commit_minutes] MIN" xalign 0.5 action Return("known_sources") sensitive eot_deadline_allows_minutes(_baseline_commit_minutes, already_taxed=True) style "echo_terminal_button"

################################################################################
## Power Allocation (Modal)
##
## Selected-state textbuttons for power routing.
## Pattern: selected button state, modal overlay.
################################################################################

screen power_allocation_screen():
    zorder 110
    modal True

    add Solid("#020712e8")

    $ _routes = [
        ("balanced", "BALANCED", "No priority load", "images/ui/icon_generator.png", "#8fb8cc"),
        ("telescope", "TELESCOPE", "Observation range", "images/ui/icon_telescope.png", "#8ccff7"),
        ("comms", "COMMS ARRAY", "Signal recovery", "images/ui/icon_comms.png", "#66d9b0"),
        ("heating", "THERMAL LOOP", "Reduced cold load", "images/ui/icon_temperature.png", "#ffb86c"),
        ("aria", "ARIA CORE", "Cluster recovery", "images/ui/icon_aria.png", "#bd82ff"),
    ]
    $ _route_names = {row[0]: row[1] for row in _routes}
    $ _route_icons = {row[0]: row[3] for row in _routes}
    $ _route_colors = {row[0]: row[4] for row in _routes}
    $ _proj_sig, _proj_aria, _proj_warm = eot_power_projection(pending_power_priority)
    $ _proj_colors = {1: "#9dffc8", 0: "#8aa7b8", -1: "#ff9d9d"}
    $ _route_changed = pending_power_priority != previous_power_priority
    ## Precomputed: Ren'Py 7.x text interpolation cannot evaluate a call inside [ ].
    $ _current_route_label = _route_names.get(previous_power_priority, previous_power_priority.upper())

    key "game_menu" action Return(False)

    frame:
        xalign 0.5 yalign 0.5 xsize 960 ysize 610
        style "echo_utility_panel_frame"

        fixed:
            fixed:
                xfill True ysize 58
                hbox:
                    spacing 11
                    add "images/ui/icon_generator.png" xysize (38, 38) yalign 0.5
                    vbox:
                        spacing 0
                        text "POWER ROUTING":
                            font "gui/fonts/Inconsolata-Regular.ttf"
                            size 18 color "#ffd3a0"
                        text "GENERATOR BUS // LOAD ALLOCATION":
                            font "gui/fonts/Inconsolata-Regular.ttf"
                            size 10 color "#8f765c"
                textbutton "CLOSE":
                    xalign 1.0 yalign 0.0
                    action Return(False)
                    style "echo_utility_close_button"
                frame:
                    xfill True ysize 1 yalign 1.0
                    background Solid("#ffb86c70")

            fixed:
                xpos 0 ypos 76 xsize 330 ysize 408
                text "ROUTING TARGET" xpos 4 ypos 0 size 11 color "#b79570" font "gui/fonts/Inconsolata-Regular.ttf"
                text "CURRENT  [_current_route_label]" xpos 326 ypos 0 xanchor 1.0 size 10 color "#668ba0" font "gui/fonts/Inconsolata-Regular.ttf"

                vbox:
                    xpos 0 ypos 25
                    spacing 7
                    for _key, _name, _purpose, _icon, _color in _routes:
                        button:
                            style "echo_power_route_button"
                            selected pending_power_priority == _key
                            xysize (330, 65)
                            action SetVariable("pending_power_priority", _key)
                            has fixed
                            add _icon xpos 3 ypos 5 xysize (42, 42)
                            text _name xpos 58 ypos 5 style "echo_power_route_button_text"
                            text _purpose xpos 58 ypos 29 size 10 color (_color if pending_power_priority == _key else "#668ba0") font "gui/fonts/Inconsolata-Regular.ttf"
                            if previous_power_priority == _key:
                                text "LIVE" xpos 307 ypos 7 xanchor 1.0 size 9 color "#8fb8cc" font "gui/fonts/Inconsolata-Regular.ttf"
                            if pending_power_priority == _key:
                                add Solid(_color, xysize=(3, 49)) xpos 0 ypos 1

            fixed:
                xpos 350 ypos 76 xsize 558 ysize 408
                add Solid("#020b13d8")
                add Solid("#24394a55", xysize=(1, 408)) xpos 0

                text "LIVE BUS PREVIEW" xpos 18 ypos 14 size 11 color "#b8eeff" font "gui/fonts/Inconsolata-Regular.ttf"
                text ("PENDING CHANGE" if _route_changed else "CURRENT ROUTE") xpos 538 ypos 14 xanchor 1.0 size 10 color ("#ffd3a0" if _route_changed else "#7dffad") font "gui/fonts/Inconsolata-Regular.ttf"

                fixed:
                    xpos 18 ypos 45 xsize 522 ysize 104
                    add Solid("#07131de0")
                    add "images/ui/icon_generator.png" xpos 18 ypos 25 xysize (48, 48)
                    text "MAIN BUS" xpos 78 ypos 30 size 12 color "#d8f2ff" font "gui/fonts/Inconsolata-Regular.ttf"
                    text "STABLE // PRIORITY TAP" xpos 78 ypos 52 size 9 color "#668ba0" font "gui/fonts/Inconsolata-Regular.ttf"
                    add Solid("#ffb86c55", xysize=(244, 2)) xpos 184 ypos 51
                    add Solid(_route_colors.get(pending_power_priority, "#8fb8cc"), xysize=(72, 2)) xpos 356 ypos 51 at echo_ui_pulse
                    add _route_icons.get(pending_power_priority, "images/ui/icon_generator.png") xpos 448 ypos 18 xysize (56, 56)
                    text _route_names.get(pending_power_priority, pending_power_priority.upper()) xpos 504 ypos 80 xanchor 1.0 size 10 color _route_colors.get(pending_power_priority, "#8fb8cc") font "gui/fonts/Inconsolata-Regular.ttf"

                text "ROUTING EFFECT // OTHER LOADS EXCLUDED" xpos 18 ypos 166 size 10 color "#668ba0" font "gui/fonts/Inconsolata-Regular.ttf"

                fixed:
                    xpos 18 ypos 190 xsize 522 ysize 58
                    add "images/ui/icon_signal.png" xpos 0 ypos 8 xysize (38, 38)
                    text "ARRAY SIGNAL" xpos 52 ypos 6 size 11 color "#d8f2ff" font "gui/fonts/Inconsolata-Regular.ttf"
                    text "[signal_strength]%" xpos 504 ypos 5 xanchor 1.0 size 11 color "#8ccff7" font "gui/fonts/Inconsolata-Regular.ttf"
                    add Solid("#173044", xysize=(360, 7)) xpos 52 ypos 31
                    $ _sig_w = int(max(0, min(100, signal_strength)) * 3.6)
                    add Solid("#6fe4ff", xysize=(_sig_w, 7)) xpos 52 ypos 31
                    text "[_proj_sig[0]]" xpos 504 ypos 29 xanchor 1.0 size 10 color _proj_colors[_proj_sig[1]] font "gui/fonts/Inconsolata-Regular.ttf"

                fixed:
                    xpos 18 ypos 252 xsize 522 ysize 58
                    add "images/ui/icon_aria.png" xpos 0 ypos 8 xysize (38, 38)
                    text "ARIA CORE" xpos 52 ypos 6 size 11 color "#d8f2ff" font "gui/fonts/Inconsolata-Regular.ttf"
                    text "[aria_integrity]%" xpos 504 ypos 5 xanchor 1.0 size 11 color "#bd82ff" font "gui/fonts/Inconsolata-Regular.ttf"
                    add Solid("#2d2344", xysize=(360, 7)) xpos 52 ypos 31
                    $ _aria_w = int(max(0, min(100, aria_integrity)) * 3.6)
                    add Solid("#bd82ff", xysize=(_aria_w, 7)) xpos 52 ypos 31
                    text "[_proj_aria[0]]" xpos 504 ypos 29 xanchor 1.0 size 10 color _proj_colors[_proj_aria[1]] font "gui/fonts/Inconsolata-Regular.ttf"

                fixed:
                    xpos 18 ypos 317 xsize 522 ysize 72
                    add "images/ui/icon_temperature.png" xpos 0 ypos 7 xysize (38, 38)
                    text "THERMAL MARGIN" xpos 52 ypos 5 size 11 color "#d8f2ff" font "gui/fonts/Inconsolata-Regular.ttf"
                    text "15 MIN TASK" xpos 504 ypos 5 xanchor 1.0 size 9 color "#668ba0" font "gui/fonts/Inconsolata-Regular.ttf"
                    text "[_proj_warm[0]]" xpos 52 ypos 29 size 11 color _proj_colors[_proj_warm[1]] font "gui/fonts/Inconsolata-Regular.ttf"
                    if aux_power_remaining > 0:
                        text "AUX RESERVE  [aux_power_remaining] MIN" xpos 504 ypos 29 xanchor 1.0 size 10 color "#7dffad" font "gui/fonts/Inconsolata-Regular.ttf"
                    else:
                        text "AUX RESERVE  EMPTY" xpos 504 ypos 29 xanchor 1.0 size 10 color "#6f7780" font "gui/fonts/Inconsolata-Regular.ttf"

            fixed:
                xpos 0 ypos 505 xsize 908 ysize 55
                add Solid("#25394a55", xysize=(908, 1)) ypos 0
                $ _routing_cost = eot_cold_taxed(5)
                text ("Rerouting requires a {}-minute bus cycle.".format(_routing_cost) if _route_changed else "No routing change selected.") xpos 4 ypos 20 size 10 color ("#b79570" if _route_changed else "#668ba0") font "gui/fonts/Inconsolata-Regular.ttf"
                textbutton ("APPLY ROUTING // {} MIN".format(_routing_cost) if _route_changed else "KEEP CURRENT ROUTING"):
                    xpos 683 ypos 9 xsize 225
                    action Return(True)
                    sensitive (not _route_changed or eot_deadline_allows_minutes(_routing_cost, already_taxed=True))
                    style "echo_power_apply_button"


################################################################################
## Observatory HUD
##
## Persistent status display during hub exploration.
## Also provides buttons to open equipment/evidence modals (tests overlay
## stale choice suppression when opened during a pending menu).
################################################################################

## Set around act2_hub's blocking `call screen observatory_map`: the STATION
## STATUS board belongs to the plan table, not to the rooms (see below).
default hud_map_open = False


screen echo_station_meter(icon, label, value, fill_color, width=270, icon_size=26, text_size=11, bar_height=7, label_color="#d8f2ff"):

    $ _track_width = width - icon_size - 8
    $ _fill_width = int(max(0, min(100, value)) * _track_width / 100.0)
    hbox:
        spacing 8
        add icon xysize (icon_size, icon_size)
        vbox:
            spacing 2
            text label:
                xmaximum _track_width
                size text_size color label_color
                font "gui/fonts/Inconsolata-Regular.ttf"
            fixed:
                xysize (_track_width, bar_height)
                add Solid("#173044", xysize=(_track_width, bar_height))
                add Solid(fill_color, xysize=(_fill_width, bar_height))


screen echo_station_icon_status(icon, label, label_color, width=270, icon_size=26, text_size=11):

    hbox:
        spacing 8
        xsize width
        add icon xysize (icon_size, icon_size)
        text label:
            yalign 0.5 xmaximum (width - icon_size - 8)
            size text_size color label_color
            font "gui/fonts/Inconsolata-Regular.ttf"


screen echo_station_primary_status(width=270, icon_size=26, text_size=11, show_details=True):

    $ _thermal_label, _thermal_color = echo_thermal_status(storm_intensity, power_priority, aux_power_remaining)
    $ _storm_pct = 100.0 * max(0, min(300, time_remaining)) / 300.0
    $ _storm_eta = echo_time_left_label(time_remaining).replace(" left", "")

    vbox:
        spacing 7
        text "{b}STATION STATUS{/b}":
            size (text_size + 1) color "#b8eeff"
            font "gui/fonts/Inconsolata-Regular.ttf"
        use echo_station_meter(
            "images/ui/icon_signal.png", "SIGNAL  {}%".format(signal_strength),
            signal_strength, "#6fe4ff", width, icon_size, text_size)
        use echo_station_meter(
            "images/ui/icon_aria.png", "ARIA COHERENCE  {}%".format(aria_integrity),
            aria_integrity, "#bd82ff", width, icon_size, text_size)
        use echo_station_meter(
            "images/ui/icon_storm.png", echo_storm_meter_label(storm_intensity, _storm_eta),
            _storm_pct, echo_storm_meter_color(storm_intensity),
            width, icon_size, text_size)
        use echo_station_icon_status(
            "images/ui/icon_temperature.png", _thermal_label, _thermal_color,
            width, icon_size, text_size)

        if show_details:
            vbox:
                spacing 4
                use echo_station_icon_status(
                    "images/ui/icon_power_cell.png",
                    "POWER  {}".format(power_priority.upper()), "#8fb8cc",
                    width, icon_size, text_size)
                if antenna_damaged and not generator_repaired:
                    text "Incident: Antenna module 2 offline" size text_size color "#ff9a78" xmaximum width
                    text "Response: Generator reroute" size text_size color "#ffbd6b" xmaximum width
                elif antenna_reroute_active:
                    text "Antenna module 2: temporary reroute" size text_size color "#ffbd6b" xmaximum width
                    text "Load: signal margin degrading" size text_size color "#ffbd6b" xmaximum width
                elif antenna_damaged:
                    text "Antenna module 2: permanent repair" size text_size color "#8ee8b4" xmaximum width


screen echo_station_passive_status(width=270, icon_size=24, text_size=10):

    vbox:
        spacing 7
        text "{b}PASSIVE RUNS{/b}":
            size (text_size + 1) color "#6f9db5"
            font "gui/fonts/Inconsolata-Regular.ttf"
        $ _passive_rows = echo_station_passive_meters()
        if _passive_rows:
            for _meter_label, _meter_pct, _meter_state in _passive_rows:
                $ _meter_color = "#7dffad" if _meter_state == "done" else ("#ffbd6b" if _meter_state == "hold" else "#6fe4ff")
                $ _meter_icon = ("images/ui/icon_telescope.png" if _meter_label == "ORIGIN SWEEP"
                                 else ("images/ui/icon_signal.png" if _meter_label == "CARRIER REBUILD"
                                       else "images/ui/icon_aria.png"))
                use echo_station_meter(
                    _meter_icon, "{}  {}%".format(_meter_label, _meter_pct),
                    _meter_pct, _meter_color, width, icon_size, text_size,
                    5, _meter_color)
        else:
            text "NO KNOWN RUNS":
                size text_size color "#789bad"
                font "gui/fonts/Inconsolata-Regular.ttf"


screen observatory_hud():
    zorder 50

    ## POCKETS TRAVEL, THE STATUS BOARD DOES NOT (2026-08-17, presentation
    ## stage 4; spec open question 4 answered by screenshot). This screen is
    ## shown at the first hub stop and stays up through every room after it —
    ## but its two halves have different jobs and different rights to the
    ## screen.
    ##
    ## KIT and LOG are pockets: they travel, top-right, clear of the log
    ## panel's measure. The STATION STATUS board is the plan table's
    ## instrument — the same compact rail used by hub NVL while choosing
    ## where to spend the night — and it sits at the top LEFT, which is
    ## exactly where the room's NVL log frame puts its header and the first
    ## two lines of every paragraph. Live screenshot, generator room: the
    ## arrival narration read "…he generator room has picked up a second
    ## rhythm beneath its usual thro…" with the board sitting on the rest of
    ## it. So the board is drawn while the map is, and stands down in the
    ## rooms, where the prose is saying the same things in words.
    ##
    ## Both halves stand down for a live terminal panel: that panel owns the
    ## full width, header strip and all, and repeats three of the board's
    ## numbers in its own status strip. Sitting at a machine is the one time
    ## the kit is not in her hands anyway.
    ##
    ## Both conditions are plain store variables on purpose. `terminal_mode` is
    ## crt_overlay's own on-show/on-hide flag — it is already exactly "she is at
    ## a machine" — and `hud_map_open` is set around the blocking `call screen
    ## observatory_map`. Asking `renpy.get_screen()` from inside a screen would
    ## make this screen's contents depend on another screen's lifetime, which
    ## is not something Ren'Py's screen cache tracks.
    if not terminal_mode:

        if hud_map_open:

            frame:
                at echo_ui_appear
                xalign 0.0 yalign 0.0 xpadding 14 ypadding 10
                background Solid("#020812c4")
                xsize 204

                use echo_station_primary_status(174, 22, 12, True)

            ## Match the NVL rail's passive-run content anchor exactly:
            ## frame origin (4, 484) + padding (14, 10) = (18, 494).
            ## Keeping this separate also prevents detail rows in the primary
            ## status block from moving long-running work up or down.
            frame:
                at echo_ui_appear
                xpos 4 ypos 484 xpadding 14 ypadding 10
                background Solid("#020812b8")
                xsize 204

                use echo_station_passive_status(174, 20, 11)

        frame:
            xalign 1.0 yalign 0.0 xpadding 4 ypadding 4
            background Solid("#020812c4")

            hbox:
                spacing 0
                button:
                    style "echo_utility_dock_button"
                    xysize (78, 40)
                    action ToggleScreen("equipment_screen")
                    tooltip "Equipment"
                    has hbox
                    spacing 5
                    xalign 0.5
                    yalign 0.5
                    add "images/ui/icon_power_cell.png" yalign 0.5 xysize (24, 24)
                    text "KIT" yalign 0.5 style "echo_utility_dock_button_text"
                add Solid("#6f9db548", xysize=(1, 28)) yalign 0.5
                button:
                    style "echo_utility_dock_button"
                    xysize (78, 40)
                    action ToggleScreen("evidence_screen")
                    tooltip "Evidence"
                    has hbox
                    spacing 5
                    xalign 0.5
                    yalign 0.5
                    add "images/ui/icon_evidence.png" yalign 0.5 xysize (24, 24)
                    text "LOG" yalign 0.5 style "echo_utility_dock_button_text"


################################################################################
## Evidence Screen (Modal) — the night's LOG
##
## Reviews evidence_log collected throughout the game.
## Pattern: modal overlay, stale choice suppression when opened mid-menu.
##
## STATION PROCESSES (2026-08-17, design/DESIGN_echoes_process_log.md §1) rides
## the TOP of this panel. The LOG is already the night's ledger and it is
## already a registered overlay, so the readout needs no button, no screen tag
## and no plumbing of its own — the passive-overlay text channel carries its
## rows to a text client for free, exactly as it carries the evidence entries.
##
## The rows come from eot_station_processes() (game_variables.rpy), which
## derives every number from the accrual variables the tick writes. This screen
## chooses only the leader width and the colour: cyan for accruing, amber for a
## process that is not earning (and says why), green for one that has finished
## and is waiting to be read.
################################################################################

screen evidence_screen():
    modal True

    add Solid("#020712b8")

    frame:
        xalign 0.5 yalign 0.5 xsize 800 ysize 560
        style "echo_utility_panel_frame"

        vbox:
            spacing 10

            use echo_utility_header(
                "images/ui/icon_evidence.png", "STATION LOG",
                "EVIDENCE // PROCESS RECORD", "evidence_screen", "#bd82ff70")

            ## Only during the Long Night: outside it there is no station
            ## clock, and a readout of nothing is worse than no readout.
            if long_night_active:
                frame:
                    xfill True
                    background Solid("#07131d70")
                    xpadding 14 ypadding 10
                    vbox:
                        spacing 5
                        text "{b}ACTIVE PROCESSES{/b}" color "#66ffcc" size 12
                        for _p_label, _p_status, _p_state in eot_station_processes():
                            text eot_process_line(_p_label, _p_status):
                                font "gui/fonts/JetBrainsMono-Regular.ttf"
                                size 13
                                color ("#8ccff7" if _p_state == "live" else ("#ff8844" if _p_state == "hold" else ("#44ff44" if _p_state == "done" else "#8fb8cc")))

            text "{b}EVIDENCE ENTRIES{/b}" color "#d8b8ff" size 12

            viewport:
                scrollbars "vertical"
                mousewheel True
                ysize 326

                vbox:
                    spacing 6
                    xfill True
                    for _entry in evidence_log:
                        frame:
                            xfill True
                            background Solid("#07131d70")
                            xpadding 12 ypadding 8
                            text "[_entry]" size 14 color "#d8f2ff"
                    if not evidence_log:
                        text "{i}No evidence collected yet.{/i}" xalign 0.5 color "#8fb8cc"



################################################################################
## Research Terminal Topics
##
## Sidebar with question buttons (smart quotes). Shown alongside NVL hub menu.
## Pattern: NVL hub, smart quotes, bookkeeping labels.
################################################################################

screen terminal_topics():
    modal True
    zorder 70

    frame:
        xalign 0.72 yalign 0.5 xsize 540 ysize 500
        background Solid("#06111cf0")
        xpadding 0 ypadding 0

        fixed:
            add Solid("#12324532", xysize=(490, 1)) pos (25, 58)
            add Solid("#12324522", xysize=(490, 1)) pos (25, 122)
            add Solid("#12324518", xysize=(490, 1)) pos (25, 186)
            add Solid("#12324514", xysize=(490, 1)) pos (25, 250)
            add Solid("#12324518", xysize=(1, 410)) pos (25, 58)
            add Solid("#12324518", xysize=(1, 410)) pos (515, 58)
            add Solid("#66ffcc4c", xysize=(2, 410)) pos (25, 58) at echo_database_sweep

            hbox:
                xpos 28 ypos 16
                spacing 10
                add "images/ui/icon_data_drive.png" yalign 0.5 xysize (32, 32)
                vbox:
                    spacing 0
                    text "AETHON RESEARCH DATABASE" font "gui/fonts/Inconsolata-Regular.ttf" size 18 color "#b8eeff"
                    text "ARIA_LOCAL // SECURE INDEX" font "gui/fonts/Inconsolata-Regular.ttf" size 12 color "#66ffcc88"

            ## Precomputed: Ren'Py 7.x text interpolation cannot evaluate a call inside [ ].
            $ _topics_read_count = len(topics_read)
            text "TOPICS_READ [_topics_read_count]" xpos 390 ypos 24 font "gui/fonts/Inconsolata-Regular.ttf" size 12 color "#8ccff7"

            vbox:
                xpos 48 ypos 84 xsize 444
                spacing 12

                text "SELECT DATASET" font "gui/fonts/Inconsolata-Regular.ttf" size 13 color "#66ffcc"

                if "trust" not in topics_read:
                    textbutton "01  ARIA Trust Protocol" action Return("trust") style "echo_database_button"
                else:
                    textbutton "01  ARIA Trust Protocol  [[READ]" action Return("trust") style "echo_database_button"

                if "temporal" not in topics_read:
                    textbutton "02  Temporal Mechanics Theory" action Return("temporal") style "echo_database_button"
                else:
                    textbutton "02  Temporal Mechanics Theory  [[READ]" action Return("temporal") style "echo_database_button"

                if "chen" not in topics_read:
                    textbutton "03  Dr. Chen Research History" action Return("chen") style "echo_database_button"
                else:
                    textbutton "03  Dr. Chen Research History  [[READ]" action Return("chen") style "echo_database_button"

                ## Open to all specializations (design doc: perception and
                ## efficiency, never exclusive access) — non-computing pays
                ## more time and gets ARIA's annotated walkthrough.
                if "aria_code" not in topics_read:
                    textbutton "04  ARIA Source Code Audit" action Return("aria_code") style "echo_database_button"
                else:
                    textbutton "04  ARIA Source Code Audit  [[READ]" action Return("aria_code") style "echo_database_button"

                null height 8

                hbox:
                    spacing 8
                    add Solid("#66ffcc26", xysize=(46, 3)) yalign 0.5 at echo_wave_pulse(0.0)
                    add Solid("#8ccff726", xysize=(28, 3)) yalign 0.5 at echo_wave_pulse(0.3)
                    add Solid("#66ffcc26", xysize=(62, 3)) yalign 0.5 at echo_wave_pulse(0.6)
                    text "INDEX ACTIVE" font "gui/fonts/Inconsolata-Regular.ttf" size 12 color "#8ccff7"

                textbutton "Done reading" action Return("done") style "echo_database_button"


################################################################################
## Station Audit Console — RETIRED 2026-08-17 (presentation stage 3)
##
## `screen station_audit_console` was a modal side panel that rendered topic
## text in terminal STYLE without ever being the terminal: no `terminal_*` call
## functions, no live log, no typewriter, no header strip. The lab console is
## now the live terminal itself (`echo_terminal_live` over `bg_lab`, header
## "ARIA AUDIT CONSOLE"), and its two-step select-then-run moved into the
## terminal as ECHOED steps — `label lab_console` / `label research_terminal`
## in script.rpy. Nothing about the costs, the topics or the receipts changed.
##
## The dataset/action captions and their price parentheticals live on the
## `echo_terminal_choice` option lists built in `research_terminal`, and the
## coherence-scan status line is a `terminal_system` row written when the
## console comes up. Both are script-side and single-line-conditional, so the
## route flattener reads the console the same way a player does.
################################################################################


################################################################################
## End Credits Overlay
##
## Compact credits at high zorder — tests scraper ignoring credit text.
## The title card owns the scene dissolve. Credits enter on their own clock so
## they cannot flash in during that dissolve or appear as a late side panel.
## Pattern: end credits screen leak.
################################################################################

transform ending_credits_reveal:
    alpha 0.0
    pause 1.0
    ease 0.6 alpha 1.0

screen endcredits():
    zorder 100

    hbox:
        at ending_credits_reveal
        xalign 0.5
        yalign 0.82
        spacing 20

        vbox:
            xsize 140
            spacing 5
            text "Initial Idea" xalign 0.5 size 11
            text "Opus 4.5" xalign 0.5 size 13

        vbox:
            xsize 160
            spacing 5
            text "Programming" xalign 0.5 size 11
            text "Claude\nCodex" xalign 0.5 text_align 0.5 size 13

        vbox:
            xsize 180
            spacing 5
            text "Writing" xalign 0.5 size 11
            text "Claude\nCodex\nvnflight" xalign 0.5 text_align 0.5 size 13

        vbox:
            xsize 180
            spacing 5
            text "Sound" xalign 0.5 size 11
            text "Claude\nCodex\nElevenLabs" xalign 0.5 text_align 0.5 size 13

        vbox:
            xsize 140
            spacing 5
            text "In The Loop" xalign 0.5 size 11
            text "vnflight" xalign 0.5 size 13


################################################################################
## NVL Context Variants
##
## The same NVL stream, framed three ways. The framing is a property of the
## SCENE, not of the line.
##
##   "log"        (default) Elara's station personal log — cyan chrome, a
##                header strip, a speaker gutter. Where most of the night is
##                written down.
##   "cinematic"  act turns, endings, epilogues — letterboxed, no chrome, a
##                wide centred measure and nothing to read but the words.
##   "scene"      sustained narration mixed with a named station voice — a
##                translucent field record over the room where it is spoken.
##
## `bulletin` remains a legacy script value, but `screen nvl` maps it to the
## log frame. Hub narration and station notices use one visual language.
##
## The LIVE ECHO-7 terminal is NOT one of these. It has its own screens
## (echo_terminal_nvl / terminal_nvl_* styles) and `terminal_mode` still wins
## in `screen nvl`, so the variants never touch it.
##
## Blocks that switch away from "log" set it back at the end (usually right
## after `nvl clear`), so anything unvisited keeps the default.
##
## Chrome plates come from diagnostics/render_echoes_ui.py.
################################################################################

default nvl_frame = "log"


init python:

    def echo_nvl_props(args, style):
        """Merge a dialogue entry's who_args/what_args/window_args with our
        own style, our style always winning.

        NVL shares these dictionaries with screen.widget_properties, which
        Ren'Py reapplies after the screen properties for displayables with an
        id. Update that shared style too, keeping the text id needed for slow
        text and AFM without restoring default NVL geometry. This works on
        Ren'Py 7 and 8 and preserves other character properties."""
        if args is not None:
            args["style"] = style
        merged = dict(args or {})
        merged["style"] = style
        return merged


screen echo_nvl_entries(dialogue, prefix):

    for d in dialogue:

        window:
            properties echo_nvl_props(d.window_args, prefix + "_entry")

            fixed:
                xfill True
                yfit True

                if d.who is not None and d.who not in ("SYSTEM", "THOUGHT"):

                    text d.who:
                        properties echo_nvl_props(d.who_args, prefix + "_label")

                text d.what:
                    id d.what_id
                    properties echo_nvl_props(
                        d.what_args,
                        prefix + "_system" if d.who == "SYSTEM"
                        else prefix + "_thought" if d.who == "THOUGHT"
                        else prefix + "_dialogue" if d.who is not None
                        else prefix + "_narration"
                    )


init python:
    import re as _echo_re

    def echo_station_passive_meters():
        """Return known long-night processes for shared status panels."""
        rows = []
        s = store
        carrier_remaining = max(0, min(18, int(getattr(
            s, "echo7_cooldown_remaining", 0) or 0)))
        if carrier_remaining > 0:
            rows.append(("CARRIER REBUILD",
                         int(100.0 * float(18 - carrier_remaining) / 18.0),
                         "running"))
        for label, _status, state in eot_station_processes():
            if label.startswith("ORIGIN SWEEP"):
                short_label = "ORIGIN SWEEP"
                percent = int(min(100.0, 100.0 * float(
                    getattr(s, "origin_sweep_progress", 0)) / 45.0))
            elif label == "ARIA PARTITION SCAN":
                if "PARTITION SEALED" in _status:
                    short_label = "PARTITION SCAN SEALED"
                elif "QUEUED" in _status:
                    short_label = "PARTITION SCAN QUEUED"
                elif state == "hold":
                    short_label = "PARTITION SCAN HOLD"
                else:
                    short_label = "PARTITION SCAN"
                target = max(1, int(getattr(
                    s, "coherence_scan_target", 0) or 0))
                percent = int(min(100.0, 100.0 * float(getattr(
                    s, "coherence_scan_progress", 0)) / target))
            elif label == "ARIA CORE SOURCE AUDIT":
                if "QUEUED" in _status:
                    short_label = "ARIA AUDIT QUEUED"
                elif state == "hold":
                    short_label = "ARIA AUDIT HOLD"
                else:
                    short_label = "ARIA SOURCE AUDIT"
                target = max(1, int(getattr(
                    s, "aria_audit_target", 0) or 0))
                percent = int(min(100.0, 100.0 * float(getattr(
                    s, "aria_audit_progress", 0)) / target))
            elif label == "ARCHIVE HASH — EVIDENCE LOG":
                short_label = "EVIDENCE HASH"
                target = max(1, int(getattr(
                    s, "archive_hash_target", 0) or 0))
                percent = int(min(100.0, 100.0 * float(getattr(
                    s, "archive_hash_progress", 0)) / target))
            else:
                # AUX RESERVE already has its own thermal HUD readout.
                continue
            rows.append((short_label, max(0, min(100, percent)), state))
        return rows

    def echo_menu_cost_style(caption):
        """Render a trailing cost parenthetical smaller and dimmer, inline.

        RENDER-ONLY (2026-08-18, user design round): the choice caption is
        untouched in the menu pipeline; only the drawing changes, and the
        tags strip back to the exact original text, so the scrape dedup's
        label match still holds. A trailing parenthetical counts as a cost
        only if it names time ("minute"/"hour") — reason notes like
        "(No cartridge in the bag.)" keep full weight.
        """
        m = _echo_re.match(r"^(.*?)( \([^()]*(?:minute|hour)[^()]*\))\s*$", caption)
        if m:
            return m.group(1) + "{size=-4}{color=#8aa7b8}" + m.group(2) + "{/color}{/size}"
        return caption


screen echo_nvl_menu(items, prefix):

    if items:

        null height 10

        for i in items:

            ## A spent one-shot is drawn with its reason and must be DEAD:
            ## Ren'Py's Button.is_sensitive() prefers the screen property over
            ## the action's own, so an unconditional `sensitive` expression
            ## here would re-arm a ChoiceReturn the menu statement built
            ## insensitive — live-verified 2026-08-17, the bridge then replayed
            ## the lab conversation and paid its relationship a second time.
            ## The action's sensitivity is the floor; the per-item keyword
            ## argument can only take it further down.
            ## Cost styling is INLINE via text tags (2026-08-18): a gutter
            ## split was tried and reverted — the drawn button's label must
            ## keep equal to the choice caption after tag-stripping, or the
            ## scrape pipeline's label-match dedup breaks and agents see
            ## phantom cost-less duplicates (live-reproduced). Tags strip to
            ## the exact original caption, so both worlds hold.
            textbutton echo_menu_cost_style(i.caption):
                action i.action
                sensitive (renpy.is_sensitive(i.action) and (
                    (getattr(i.action, "kwargs", None) or {}).get(
                        "sensitive", True)) and
                    eot_deadline_allows_caption(i.caption))
                style (prefix + "_button")


screen echo_nvl_body(dialogue, items, prefix, top, height, width):

    viewport:
        xalign 0.5 ypos top xsize width ysize height
        yinitial 1.0
        mousewheel True
        draggable True

        vbox:
            xsize width
            spacing gui.nvl_spacing

            use echo_nvl_entries(dialogue, prefix)
            use echo_nvl_menu(items, prefix)


screen echo_nvl_log(dialogue, items=None, alert=False):

    ## Keep the current room present beneath the station record. The source
    ## plate stays near-opaque for standalone renders; this screen owns the
    ## in-game compositing balance.
    add Transform("images/ui/nvl_log_panel.png", alpha=0.84)

    ## ALERT BRACKETS: inset from both the status rail and the persistent
    ## KIT/LOG controls, so the right edge is never clipped while the left one
    ## remains fully visible. Short caps make the pair read as one restrained
    ## advisory frame rather than two unrelated full-height rules.
    if alert:
        add Solid("#ffbd6b70", xysize=(2, 600)) pos (244, 52)
        add Solid("#ffbd6b70", xysize=(2, 600)) pos (1034, 52)
        add Solid("#ffbd6b70", xysize=(72, 2)) pos (244, 52)
        add Solid("#ffbd6b70", xysize=(72, 2)) pos (964, 52)
        add Solid("#ffbd6b70", xysize=(72, 2)) pos (244, 650)
        add Solid("#ffbd6b70", xysize=(72, 2)) pos (964, 650)

    if long_night_active:
        use echo_nvl_status_rail

    if alert:
        text "AETHON OBSERVATORY  //  STATION ADVISORY":
            xpos 258 ypos 15 size 13 color "#ffbd6b"
            font "gui/fonts/Inconsolata-Regular.ttf"
        text "E. VOSS · 05 MAR 2047":
            xpos 1020 ypos 15 xanchor 1.0 size 13 color "#7f8790"
            font "gui/fonts/Inconsolata-Regular.ttf"
    else:
        text "AETHON OBSERVATORY  //  PERSONAL LOG":
            xpos 220 ypos 15 size 13 color "#8fd3f0"
            font "gui/fonts/Inconsolata-Regular.ttf"
        text "E. VOSS · 05 MAR 2047":
            xpos 1060 ypos 15 xanchor 1.0 size 13 color "#5d859d"
            font "gui/fonts/Inconsolata-Regular.ttf"

    use echo_nvl_body(
        dialogue, items,
        "echo_nvl_alert" if alert else "echo_nvl_log",
        74, 592, 840)


screen echo_nvl_status_rail():

    fixed:
        xpos 18 ypos 14 xsize 180 ysize 638

        use echo_station_primary_status(174, 22, 12, True)

        fixed:
            ypos 480 xsize 174 ysize 158
            use echo_station_passive_status(174, 20, 11)


screen echo_nvl_bulletin(dialogue, items=None):

    add "images/ui/nvl_bulletin_panel.png"

    text "STATION ADVISORY":
        xpos 180 ypos 28 size 15 color "#ffbd6b"
        font "gui/fonts/Inconsolata-Regular.ttf"

    text "AETHON OBSERVATORY · AUTOMATED NOTICE":
        xpos 1100 ypos 30 xanchor 1.0 size 12 color "#a8815080"
        font "gui/fonts/Inconsolata-Regular.ttf"

    use echo_nvl_body(dialogue, items, "echo_nvl_bulletin", 84, 566, 800)


## The letterbox eases in rather than cutting: the "slower dissolve" of the
## cinematic register.
##
## It used to be an ATL on the panel (`alpha 0.0; ease 0.9 alpha 1.0`), on the
## assumption that Ren'Py reuses the displayable across NVL updates. It does
## not: `nvl` is shown `_transient=True`, so it is torn down and rebuilt on
## every interaction and the ease restarted on EVERY LINE — a grey wash sliding
## back over the whiteout scene after each one (user report 2026-08-17). The
## register now rides the block's own `nvl show echo_cine_dissolve`, which runs
## exactly once, when the block opens, and the chrome is static thereafter.
screen echo_nvl_cinematic(dialogue, items=None):

    add "images/ui/nvl_cinematic_panel.png"

    use echo_nvl_body(dialogue, items, "echo_nvl_cine", 128, 470, 720)


screen echo_nvl_scene(dialogue, items=None):

    ## More transparent than the operational hub log and without its status
    ## rail: the room remains visible, named voices have a deliberate gutter,
    ## and long narration keeps an NVL-sized reading column.
    add Transform("images/ui/nvl_log_panel.png", alpha=0.68)

    text "AETHON OBSERVATORY  //  FIELD RECORD":
        xpos 220 ypos 15 size 13 color "#8fd3f0"
        font "gui/fonts/Inconsolata-Regular.ttf"

    use echo_nvl_body(dialogue, items, "echo_nvl_scene", 74, 592, 1000)


################################################################################
## Variant styles
##
## Geometry is per-variant: the log keeps a speaker gutter against its rule,
## the bulletin sits inside its ruled box, and the cinematic drops the gutter
## for a centred measure.
################################################################################

style echo_nvl_log_entry is default:
    xfill True

style echo_nvl_log_label is default:
    xpos 0
    xanchor 0.0
    xsize 142
    min_width 142
    text_align 1.0
    size 18
    font "gui/fonts/Inconsolata-Regular.ttf"

style echo_nvl_log_dialogue is default:
    xpos 158
    xanchor 0.0
    xsize 682
    size 21
    line_spacing 3
    color "#dbe9f4"
    outlines [(1, "#03090f", 0, 0)]

## Speaker-gutter rule (2026-08-18, user play session): ALL text — narration,
## dialogue, thought, system — shares ONE left edge (the dialogue column),
## and speaker tags hang in the gutter to its left. The old layout put
## narration at the frame margin and dialogue further in, which left the
## tags floating in a no-man's column between two ragged edges.
style echo_nvl_log_narration is echo_nvl_log_dialogue:
    color "#e6ded2"
    line_spacing 5

style echo_nvl_log_thought is echo_nvl_log_narration:
    color "#c3bcd6"

style echo_nvl_log_system is echo_nvl_log_narration:
    font "gui/fonts/Inconsolata-Regular.ttf"
    size 19
    color "#8fe8c0"

style echo_nvl_log_button is button:
    background Solid("#0b1e2caa")
    hover_background Solid("#153a5ad2")
    ## A spent one-shot stays on the list with its reason. Its menu item passes
    ## a local sensitivity argument instead of changing global menu policy. It has to
    ## READ as spent, or a visible-but-dead option is worse than an absent
    ## one: flatter ground, no hover, and the text greys out below.
    insensitive_background Solid("#08131b88")
    xpadding 16
    ypadding 10
    ## Speaker-gutter rule (2026-08-18, user screenshot): choices sit on the
    ## same text edge as narration and dialogue. The chip's padding would
    ## push its LABEL 16px past the edge, so the button starts one padding
    ## early — the text lands at 158 and the chip reads as a highlight
    ## behind the line, not an outdent. xmaximum keeps a long caption
    ## wrapping INSIDE the frame (user screenshot: "(a qu / to configure)"
    ## clipped at the panel edge without it): 840 column − 142 start.
    xpos 142
    xmaximum 698

style echo_nvl_log_button_text is button_text:
    color "#cfe9f7"
    hover_color "#ffffff"
    insensitive_color "#5d7787"
    size 20


## The alert brackets are inset 24px from the ordinary log body. Preserve the
## speaker gutter, but shorten prose and choice measures so neither can cross
## the right bracket on a long wrapped line.
style echo_nvl_alert_entry is echo_nvl_log_entry
style echo_nvl_alert_label is echo_nvl_log_label

style echo_nvl_alert_dialogue is echo_nvl_log_dialogue:
    xsize 632

style echo_nvl_alert_narration is echo_nvl_alert_dialogue:
    color "#e6ded2"
    line_spacing 5

style echo_nvl_alert_thought is echo_nvl_alert_narration:
    color "#c3bcd6"

style echo_nvl_alert_system is echo_nvl_alert_narration:
    font "gui/fonts/Inconsolata-Regular.ttf"
    size 19
    color "#8fe8c0"

style echo_nvl_alert_button is echo_nvl_log_button:
    xmaximum 648

style echo_nvl_alert_button_text is echo_nvl_log_button_text


style echo_nvl_bulletin_entry is default:
    xfill True

style echo_nvl_bulletin_label is default:
    xpos 0
    xanchor 0.0
    xsize 130
    min_width 130
    text_align 1.0
    size 17
    font "gui/fonts/Inconsolata-Regular.ttf"

style echo_nvl_bulletin_dialogue is default:
    xpos 158
    xanchor 0.0
    xsize 642
    size 21
    line_spacing 4
    color "#efe3d2"
    outlines [(1, "#0c0803", 0, 0)]

## Speaker-gutter rule (2026-08-18): same as the log frame — one text edge,
## tags in the gutter.
style echo_nvl_bulletin_narration is echo_nvl_bulletin_dialogue:
    color "#f0e6d6"

style echo_nvl_bulletin_thought is echo_nvl_bulletin_narration:
    color "#d5c8bb"

style echo_nvl_bulletin_system is echo_nvl_bulletin_narration:
    font "gui/fonts/Inconsolata-Regular.ttf"
    size 19
    color "#ffcf94"

style echo_nvl_bulletin_button is button:
    background Solid("#26190caa")
    hover_background Solid("#4a3210d2")
    insensitive_background Solid("#1a120788")
    xpadding 16
    ypadding 10
    ## Speaker-gutter rule (2026-08-18): label lands on the text edge (158),
    ## chip starts one padding early — see echo_nvl_log_button. xmaximum
    ## keeps long captions wrapping inside the 800 column.
    xpos 142
    xmaximum 658

style echo_nvl_bulletin_button_text is button_text:
    color "#ffdcaa"
    hover_color "#ffffff"
    insensitive_color "#8a7355"
    size 20


style echo_nvl_cine_entry is default:
    xfill True

style echo_nvl_cine_label is default:
    xpos 0
    xanchor 0.0
    xsize 720
    min_width 720
    text_align 0.5
    size 15
    color "#7fa5bb"
    font "gui/fonts/Inconsolata-Regular.ttf"

style echo_nvl_cine_dialogue is default:
    xpos 0
    xanchor 0.0
    xsize 720
    ## min_width so a SHORT line centres in the measure too: without it a
    ## one-line system notice is only as wide as itself and text_align has
    ## nothing to align inside.
    min_width 720
    ypos 22
    size 23
    line_spacing 9
    text_align 0.5
    layout "subtitle"
    color "#e8eef4"
    outlines [(1, "#01040a", 0, 0)]

style echo_nvl_cine_narration is echo_nvl_cine_dialogue:
    ypos 0
    color "#e9e2d6"

style echo_nvl_cine_thought is echo_nvl_cine_narration:
    color "#c8c0da"

style echo_nvl_cine_system is echo_nvl_cine_narration:
    font "gui/fonts/Inconsolata-Regular.ttf"
    size 20
    color "#9fe8c6"

style echo_nvl_cine_button is button:
    background Solid("#0a141ea0")
    hover_background Solid("#16303fd0")
    insensitive_background Solid("#070e1580")
    xpadding 20
    ypadding 12
    xalign 0.5

style echo_nvl_cine_button_text is button_text:
    color "#dbe6ef"
    hover_color "#ffffff"
    insensitive_color "#63717e"
    size 21
    text_align 0.5


style echo_nvl_scene_entry is default:
    xfill True

style echo_nvl_scene_label is default:
    xpos 0
    xanchor 0.0
    xsize 70
    min_width 70
    text_align 1.0
    size 18
    font "gui/fonts/Inconsolata-Regular.ttf"

style echo_nvl_scene_dialogue is default:
    xpos 88
    xanchor 0.0
    xsize 912
    size 22
    line_spacing 5
    color "#dbe9f4"
    outlines [(1, "#03090f", 0, 0)]

style echo_nvl_scene_narration is echo_nvl_scene_dialogue:
    color "#e6ded2"
    line_spacing 7

style echo_nvl_scene_thought is echo_nvl_scene_narration:
    color "#c3bcd6"

style echo_nvl_scene_system is echo_nvl_scene_narration:
    font "gui/fonts/Inconsolata-Regular.ttf"
    size 19
    color "#8fe8c0"

style echo_nvl_scene_button is echo_nvl_log_button:
    xpos 72
    xmaximum 928

style echo_nvl_scene_button_text is echo_nvl_log_button_text
