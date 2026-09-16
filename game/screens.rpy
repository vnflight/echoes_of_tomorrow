################################################################################
## Initialization
################################################################################

init offset = -1


################################################################################
## Styles
################################################################################

style default:
    properties gui.text_properties()
    language gui.language

style input:
    properties gui.text_properties("input", accent=True)
    adjust_spacing False

style hyperlink_text:
    properties gui.text_properties("hyperlink", accent=True)
    hover_underline True

style gui_text:
    properties gui.text_properties("interface")


style button:
    properties gui.button_properties("button")

style button_text is gui_text:
    properties gui.text_properties("button")
    yalign 0.5


style label_text is gui_text:
    properties gui.text_properties("label", accent=True)

style prompt_text is gui_text:
    properties gui.text_properties("prompt")


style bar:
    ysize gui.bar_size
    left_bar Frame("gui/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    xsize gui.bar_size
    top_bar Frame("gui/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    ysize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    xsize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    ysize gui.slider_size
    base_bar Frame("gui/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/slider/horizontal_[prefix_]thumb.png"

style vslider:
    xsize gui.slider_size
    base_bar Frame("gui/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/slider/vertical_[prefix_]thumb.png"


style frame:
    padding gui.frame_borders.padding
    background Frame("gui/frame.png", gui.frame_borders, tile=gui.frame_tile)



################################################################################
## In-game screens
################################################################################


## Say screen ##################################################################
##
## The say screen is used to display dialogue to the player. It takes two
## parameters, who and what, which are the name of the speaking character and
## the text to be displayed, respectively. (The who parameter can be None if no
## name is given.)
##
## This screen must create a text displayable with id "what", as Ren'Py uses
## this to manage text display. It can also create displayables with id "who"
## and id "window" to apply style properties.
##
## https://www.renpy.org/doc/html/screen_special.html#say

screen echo_terminal_panel(chrome=True):
    ## `chrome` off keeps the geometry and drops the paint. echo_terminal_choice
    ## is always shown over echo_terminal_live, which has already drawn the
    ## panel: a second copy stacks the backdrop (alpha .86 twice reads as .98,
    ## a visible darkening step over room art) and runs a second _terminal_sweep
    ## at its own phase. Both were invisible while the terminal only ever ran
    ## over `scene black`.
    if chrome:
        add Solid("#02070bdc")

    frame:
        style "terminal_nvl_window"
        background (Solid("#06111ced") if chrome else None)

        fixed:
            if chrome:
                add Solid("#12324530", xysize=(1168, 1)) pos (28, 48)
                add Solid("#12324522", xysize=(1168, 1)) pos (28, 118)
                add Solid("#12324518", xysize=(1168, 1)) pos (28, 188)
                add Solid("#12324514", xysize=(1168, 1)) pos (28, 258)
                add Solid("#12324512", xysize=(1168, 1)) pos (28, 328)
                add Solid("#12324510", xysize=(1168, 1)) pos (28, 398)
                add Solid("#12324510", xysize=(1168, 1)) pos (28, 468)
                add Solid("#1232450c", xysize=(1168, 1)) pos (28, 538)
                add Solid("#66ffcc18", xysize=(1, 558)) pos (28, 48)
                add Solid("#66ffcc18", xysize=(1, 558)) pos (1196, 48)
                add Solid("#66ffcc26", xysize=(1168, 1)) pos (28, 606)
                add _terminal_sweep pos (28, 48)
                add Solid("#66ffcc26", xysize=(42, 3)) pos (50, 628) at echo_wave_pulse(0.0)
                add Solid("#8ccff726", xysize=(24, 3)) pos (104, 628) at echo_wave_pulse(0.2)
                add Solid("#66ffcc26", xysize=(66, 3)) pos (140, 628) at echo_wave_pulse(0.4)
                add Solid("#ff668826", xysize=(30, 3)) pos (218, 628) at echo_wave_pulse(0.6)
                add Solid("#8ccff726", xysize=(54, 3)) pos (260, 628) at echo_wave_pulse(0.8)
                ## The panel's identity is a VARIABLE, not a second screen
                ## (2026-08-17, presentation stage 3): the comms rack and
                ## ARIA's audit console are the same machinery seen from two
                ## chairs, and duplicating the screen to change six words
                ## would have duplicated the scroller, the reserve and the
                ## sweep with it. echo_terminal_choice reads the same name,
                ## so the header does not flicker while a choice is up.
                text echo_terminal_title xpos 30 ypos 18 size 13 color "#66ffcc"
                ## Right-anchored: the degraded labels are longer than STABLE and
                ## would otherwise run past the panel edge. The strip adds
                ## NIGHT + ARIA while the storm clock is live (user design
                ## 2026-08-17): the header shows the accounts a question spends.
                text echo_terminal_status_label() xpos 1196 xanchor 1.0 ypos 18 size 13 color ("#8ccff7" if signal_strength >= 70 else ("#ffcc66" if signal_strength >= 40 else "#ff8844"))

            transclude


default echo_terminal_rows = []
default echo_terminal_reveal = 0
## Text-client delivery identity. It survives a choice-layer handoff, while a
## genuine clear/reset starts a new terminal page even if its text repeats.
default echo_terminal_generation = 0
## True once a choice has been shown, until the log is next cleared.
default echo_terminal_reserving = False
## Which machine she is sitting at. Restored by echo_terminal_reset(), so a
## session that does not claim a name gets the comms rack's — the terminal's
## default identity, and the only one act 1 has ever had.
define ECHO_TERMINAL_DEFAULT_TITLE = "AETHON TERMINAL // LIVE FEED"
default echo_terminal_title = "AETHON TERMINAL // LIVE FEED"

init python:
    ## Both terminal viewports are this tall (see echo_terminal_live_content).
    ECHO_TERMINAL_VIEWPORT_H = 434

    def echo_terminal_reserve_height():
        """Height the log holds after a choice, so its rows do not drop.

        The choice viewport measured rows-plus-buttons to set its own range,
        so range + viewport height IS that total -- wrapping and styles
        included, with no pixel arithmetic of ours to drift out of date. Read
        it live rather than caching it on a range change: a range only
        *changes* sometimes, and two choices of equal height in a row would
        leave a cached value stale (or zero, right after a clear).

        The adjustment keeps its last measurement after the screen is gone,
        which is exactly the number wanted here.
        """

        if not echo_terminal_reserving:
            return 0
        return int(echo_terminal_scroll_choice.adj.range) + ECHO_TERMINAL_VIEWPORT_H

    class EchoTerminalScroll(object):
        """Keeps a terminal viewport pinned to the newest line.

        A viewport reports a new range only when its content actually
        changes size, so following the bottom from `ranged` costs nothing
        while the log sits idle -- it fires exactly when a line is appended
        or a reveal grows one.

        Player scrolling arrives through `changed`, which the viewport
        raises for wheel and drag. Pinning assigns `.value` directly and so
        deliberately does NOT go through it: scrolling up to re-read stops
        the follow, and scrolling back to the bottom resumes it.
        """

        def __init__(self):
            self.follow = True
            self.adj = ui.adjustment(ranged=self._ranged, changed=self._scrolled)

        def _ranged(self, adj):
            if self.follow:
                adj.value = adj.range

        def _scrolled(self, value):
            self.follow = value >= self.adj.range - 1.0

        def follow_latest(self):
            self.follow = True

    def echo_terminal_follow_latest():
        echo_terminal_scroll_live.follow_latest()
        echo_terminal_scroll_choice.follow_latest()

    def echo_terminal_reset():
        store.echo_terminal_generation += 1
        store.echo_terminal_rows = []
        store.echo_terminal_reveal = 0
        store.echo_terminal_reserving = False
        store.echo_terminal_title = ECHO_TERMINAL_DEFAULT_TITLE
        echo_terminal_follow_latest()
        renpy.restart_interaction()

    def echo_terminal_clear():
        store.echo_terminal_generation += 1
        store.echo_terminal_rows = []
        store.echo_terminal_reveal = 0
        store.echo_terminal_reserving = False
        echo_terminal_follow_latest()
        renpy.restart_interaction()

    def echo_terminal_link_label():
        ## The panel header used to read STABLE unconditionally. Act 1 is the
        ## only place that was ever true; the comms terminal runs while the
        ## storm is eating the array, so it reports what the array can do.
        if signal_strength >= 70:
            return "ARRAY LINK: STABLE"
        if signal_strength >= 40:
            return "ARRAY LINK: DEGRADED {}%".format(int(signal_strength))
        if signal_strength >= 20:
            return "ARRAY LINK: CRITICAL {}%".format(int(signal_strength))
        return "ARRAY LINK: LOST"

    def echo_terminal_status_label():
        """Panel-header status strip (user design 2026-08-17): the terminal
        shows the accounts a question actually draws on. NIGHT + ARIA appear
        only while the storm clock is live — act 1's terminal predates the
        night budget and showing one would be a lie."""
        parts = []
        if long_night_active:
            parts.append("NIGHT {}h {:02d}m".format(
                max(0, int(time_remaining)) // 60,
                max(0, int(time_remaining)) % 60))
            parts.append("ARIA {}%".format(int(aria_integrity)))
        parts.append(echo_terminal_link_label())
        return "  //  ".join(parts)

    def echo_terminal_display_text(text):
        try:
            return renpy.filter_text_tags(text, allow=[])
        except Exception:
            return text

    def echo_terminal_visible(text, reveal):
        """The typewriter's partial row, cut where the text engine can read it.

        Rows keep their RAW text on purpose: the interpolation is done by the
        Text displayable at draw time, which is how `[data_drives] in the bag`
        stays live. The typewriter slices that raw text — and a slice landing
        INSIDE a `[...]` group hands Ren'Py a string that "ends with an open
        format operation", which is an exception, not a partial word.

        LIVE-CAUGHT 2026-08-17 at the lab console: the coherence-scan status
        row (`ARIA PARTITION SCAN — [_coh_pct]%% // rate: [_coh_rate]`) took
        the whole game down the first time it was typed with a scan running.
        Every interpolated row written since the console became a terminal was
        carrying the same landmine — the archive's drive count, the elapsed
        stamps, the audit's numbers.

        So the cut is pulled back to the start of any unclosed group: the
        interpolated value simply appears whole when its closing bracket is
        revealed, which is also what it looks like on a real console. A run of
        `[[` (the escape for a literal bracket) is pulled back as a unit, or
        the cut would leave a lone `[` behind and raise the same exception.
        """
        visible = text[:reveal]
        for opener, closer in (("[", "]"), ("{", "}")):
            start = visible.rfind(opener)
            if start > visible.rfind(closer):
                while start > 0 and visible[start - 1] == opener:
                    start -= 1
                visible = visible[:start]
        return visible

    def echo_terminal_system_color(text):
        if text.startswith("{color=") and "}" in text:
            return text.split("}", 1)[0][7:]
        return "#7dffad"

    def echo_terminal_system(text):
        display_text = echo_terminal_display_text(text)
        store.echo_terminal_rows = store.echo_terminal_rows + [{
            "kind": "system",
            "text": text,
            "display_text": display_text,
            "color": echo_terminal_system_color(text),
            "slow": True,
        }]
        store.echo_terminal_reveal = 0
        eot_terminal_reveal_start(store.echo_terminal_rows[-1])
        echo_terminal_follow_latest()
        renpy.restart_interaction()

    def echo_terminal_prompt(who, text, color="#dcfff0"):
        display_text = echo_terminal_display_text(text)
        store.echo_terminal_rows = store.echo_terminal_rows + [{
            "kind": "prompt",
            "who": who,
            "text": text,
            "display_text": display_text,
            "label_color": color,
            "color": "#dcfff0",
            "slow": True,
        }]
        store.echo_terminal_reveal = 0
        eot_terminal_reveal_start(store.echo_terminal_rows[-1])
        echo_terminal_follow_latest()
        renpy.restart_interaction()

    def echo_terminal_latest_text():
        if not store.echo_terminal_rows:
            return ""
        row = store.echo_terminal_rows[-1]
        return row.get("display_text", row.get("text", ""))

    def echo_terminal_reveal_delay(text=""):
        cps = preferences.text_cps
        if not cps:
            return 0.08
        plain = echo_terminal_display_text(text)
        return max(0.08, min(4.0, len(plain) / float(cps)))

    def echo_terminal_finish_reveal():
        store.echo_terminal_reveal = len(echo_terminal_latest_text())
        eot_terminal_reveal_finish()
        renpy.restart_interaction()

    def echo_terminal_tick():
        text = echo_terminal_latest_text()
        if not text:
            return
        if store.echo_terminal_reveal >= len(text):
            return
        cps = preferences.text_cps
        if not cps:
            store.echo_terminal_reveal = len(text)
        else:
            old_reveal = store.echo_terminal_reveal
            store.echo_terminal_reveal = min(
                len(text),
                store.echo_terminal_reveal + max(1, int(cps / 30.0))
            )
            eot_terminal_type_tick(old_reveal, store.echo_terminal_reveal)
        renpy.restart_interaction()

    def echo_terminal_pause_delay(text="", delay="auto"):
        if delay in ("afm", "manual"):
            return None
        if delay is None:
            return None
        if delay != "auto":
            return delay

        cps = preferences.text_cps
        if not cps:
            return 0.08

        try:
            plain = renpy.filter_text_tags(text, allow=[])
        except Exception:
            plain = text

        return max(0.18, min(4.0, len(plain) / float(cps)))


## One scroller per viewport, not one shared: echo_terminal_live and
## echo_terminal_choice are on screen together with different content heights
## (the choice screen carries the buttons too), so a shared adjustment would
## have each clobber the other's range. `define` keeps them out of saves.
define echo_terminal_scroll_live = EchoTerminalScroll()
define echo_terminal_scroll_choice = EchoTerminalScroll()


screen echo_terminal_live():
    on "show" action Function(eot_terminal_audio_enter)
    on "hide" action Function(eot_terminal_audio_exit)
    zorder -5
    use echo_terminal_panel:
        ## The choice overlay renders the same rows with its own scroll
        ## adjustment. Drawing both copies is invisible only while their
        ## offsets match; wheel-scrolling the choice viewport otherwise exposes
        ## a second, displaced log underneath. Keep this screen's chrome, but
        ## let the modal overlay own the row layer while it is present.
        if renpy.get_screen("echo_terminal_choice") is None:
            use echo_terminal_live_content()


screen echo_terminal_live_content():
    ## Viewport stops short of the say window. The panel is centred at y 30-690,
    ## so the viewport starts at 94; gui.textbox_height is 185 at yalign 1.0, so
    ## the box owns 535-720. 434 puts the last row at 528, seven pixels clear --
    ## the log follows its own bottom, so without this the newest line is exactly
    ## what an ADV line covers.
    viewport:
        ## The panel rules sit at x=28/1196. Starting at 50 gives a 22px
        ## inner margin, so 1124 is the matching right edge (1174), not the
        ## old 1168 that let rows draw 22px beyond the right rule.
        xpos 50 ypos 64 xsize 1124 ysize 434
        clipping True
        yadjustment echo_terminal_scroll_live.adj
        yinitial 1.0
        mousewheel True
        draggable True

        ## Holds the height the choice block had, so the rows do not drop
        ## when the buttons go away; each new line eats into the slack, so
        ## existing rows never move and the gap is gone once the answer has
        ## filled it.
        ##
        ## `box_align` doesn't exist at all in Ren'Py 7.5.2 (added in 8.x;
        ## absent from 7.5.2's style defaults, layout.py and sl2 property
        ## list), and referencing it anywhere in a screen — even inside a
        ## dead `if renpy.version_tuple >= (8,):` branch — fails to PARSE
        ## under 7.5.2's screen-language compiler regardless of which branch
        ## would run, since compiling a screen validates every branch's
        ## keywords up front. Its whole job here was to stop a Box from
        ## splitting leftover height evenly BETWEEN children (layout.py
        ## layout_line, yperchild = yfill / line_count) when `yminimum` makes
        ## the vbox taller than its content, spreading the log out instead of
        ## leaving the slack after the last row.
        ##
        ## A fitted `fixed` overlays a reserve spacer and the naturally sized
        ## vbox at the same origin. Its height is their maximum, so new rows
        ## consume the slack before extending the scroll range. This works on
        ## both engines without redistributing space between individual rows.
        fixed:
            xsize 1124
            yfit True

            ## A fitted fixed reports the larger of the rows and this reserve.
            ## yminimum alone leaves its reported height stuck at the viewport
            ## height, hiding overflow from the scrolling adjustment.
            null height echo_terminal_reserve_height()

            vbox:
                xsize 1124
                spacing 3

                use echo_terminal_rows_content()


screen echo_terminal_rows_content():

    if echo_terminal_rows and not renpy.in_rollback() and echo_terminal_reveal < len(echo_terminal_latest_text()):
        timer 0.033 repeat True action Function(echo_terminal_tick)

    for index, row in enumerate(echo_terminal_rows):
        $ latest = index == len(echo_terminal_rows) - 1
        $ row_text = row.get("display_text", row.get("text", ""))
        $ visible_text = echo_terminal_visible(row_text, echo_terminal_reveal) if latest and not renpy.in_rollback() else row_text

        if row["kind"] == "system":
            text visible_text:
                id ("terminal_row_{}".format(index))
                style "terminal_nvl_system"
                xpos 96
                xanchor 0
                xsize 1028
                color row.get("color", "#7dffad")
                size 18
                font "gui/fonts/JetBrainsMono-Regular.ttf"

        else:
            fixed:
                xfill True
                yfit True

                text row.get("who", ""):
                    style "terminal_nvl_label"
                    xpos 0
                    xanchor 0
                    xsize 88
                    min_width 88
                    size 18
                    font "gui/fonts/JetBrainsMono-Regular.ttf"
                    color row.get("label_color", "#66ffcc")
                    text_align 1.0

                text visible_text:
                    id ("terminal_row_{}".format(index))
                    style "terminal_nvl_dialogue"
                    xpos 96
                    xanchor 0
                    xsize 1028
                    color row.get("color", "#dcfff0")
                    size 18
                    font "gui/fonts/JetBrainsMono-Regular.ttf"
                    text_align 0.0
                    xalign 0.0


screen echo_terminal_choice(options):
    tag echo_terminal_choice
    modal True
    ## Stay modal over the game/HUD, but below quick_menu (zorder 100) so its
    ## navigation buttons remain usable while a terminal choice is waiting.
    zorder 90
    ## Arms the reserve. While this screen is up the live log behind it holds
    ## the same height, so the two are laid out identically and closing this
    ## screen moves nothing.
    on "show" action SetVariable("echo_terminal_reserving", True)
    key "dismiss" action NullAction()
    key "button_select" action NullAction()
    ## Draw the panel only when nothing else already has. In practice the live
    ## terminal is always underneath (beat 11 reaches this from hub_comms), but
    ## asking beats assuming: a caller that opens a choice without the live
    ## screen still gets a panel instead of floating buttons.
    use echo_terminal_panel(chrome=(renpy.get_screen("echo_terminal_live") is None)):
        ## Same height as echo_terminal_live_content, or the log would shift
        ## as the choice screen opens over it.
        viewport:
            xpos 50 ypos 64 xsize 1124 ysize 434
            clipping True
            yadjustment echo_terminal_scroll_choice.adj
            yinitial 1.0
            mousewheel True
            draggable True

            vbox:
                xsize 1124
                spacing 3

                use echo_terminal_rows_content()

                for value, caption in options:
                    textbutton caption:
                        action Return(value)
                        sensitive eot_deadline_allows_caption(caption)
                        style "terminal_nvl_button"
                        xpos 96
                        xsize 1028
                        top_margin 10


screen say(who, what):

    ## Ren'Py emits a menu caption through the ADV narrator with
    ## interact=False before opening an NVL menu. Keep the two presentation
    ## surfaces mutually exclusive: the caption remains in menu metadata, but
    ## its ADV panel cannot sit underneath the station-log choices.
    if renpy.get_screen("nvl") is None:
        window:
            id "window"

            if who is not None:

                window:
                    style "namebox"
                    text who id "who"

            text what id "what"


        ## If there's a side image, display it above the text. Do not display on
        ## the phone variant - there's no room.
        if not renpy.variant("small"):
            add SideImage() xalign 0.0 yalign 1.0


style window is default
style say_label is default
style say_dialogue is default
style say_thought is say_dialogue

style namebox is default
style namebox_label is say_label


## Dialogue furniture, on the station aesthetic: a dark panel under a thin
## cyan rule (images/ui/say_panel.png) instead of the stock fade, and a
## speaker chip with a cyan bar. The say SCREEN is unchanged.
style window:
    xalign 0.5
    xfill True
    yalign gui.textbox_yalign
    ysize gui.textbox_height

    background Image("images/ui/say_panel.png", xalign=0.5, yalign=1.0)

style namebox:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height

    background Frame("images/ui/namebox_panel.png", Borders(14, 6, 14, 6), tile=False, xalign=gui.name_xalign)
    padding (18, 6, 16, 6)

style say_label:
    properties gui.text_properties("name", accent=True)
    xalign gui.name_xalign
    yalign 0.5
    size 26
    outlines [(1, "#02070b", 0, 0)]

style say_dialogue:
    properties gui.text_properties("dialogue")

    xpos gui.dialogue_xpos
    xsize gui.dialogue_width
    ypos gui.dialogue_ypos

    color "#e2edf5"
    line_spacing 3
    ## The panel is translucent; a hairline keeps the prose off a bright room.
    outlines [(1, "#02070b", 0, 0)]

    adjust_spacing False


## Input screen ################################################################
##
## This screen is used to display renpy.input. The prompt parameter is used to
## pass a text prompt in.
##
## This screen must create an input displayable with id "input" to accept the
## various input parameters.
##
## http://www.renpy.org/doc/html/screen_special.html#input

screen input(prompt):
    style_prefix "input"

    window:

        vbox:
            xalign gui.dialogue_text_xalign
            xpos gui.dialogue_xpos
            xsize gui.dialogue_width
            ypos gui.dialogue_ypos

            text prompt style "input_prompt"
            input id "input"

style input_prompt is default

style input_prompt:
    xalign gui.dialogue_text_xalign
    properties gui.text_properties("input_prompt")

style input:
    xalign gui.dialogue_text_xalign
    xmaximum gui.dialogue_width


## Choice screen ###############################################################
##
## This screen is used to display the in-game choices presented by the menu
## statement. The one parameter, items, is a list of objects, each with caption
## and action fields.
##
## http://www.renpy.org/doc/html/screen_special.html#choice

screen choice(items):
    style_prefix "choice"

    vbox:
        for i in items:
            textbutton i.caption action i.action


style choice_vbox is vbox
style choice_button is button
style choice_button_text is button_text

style choice_vbox:
    xalign 0.5
    ## Bottom edge clear of the say panel's top rule (720 - 185 = 535): the
    ## chips are taller than the stock bars they replaced.
    ypos 505
    yanchor 1.0

    spacing 14

## STYLE ONLY. The vnflight shim scrapes choices out of the `choice` screen's
## structure and the caption-attribution pipeline depends on it, so the screen
## above is untouched: this is a chip background, padding and colour, nothing
## more.
style choice_button is default:
    properties gui.button_properties("choice_button")

    background Frame("images/ui/choice_idle.png", Borders(34, 12, 30, 12), tile=False)
    hover_background Frame("images/ui/choice_hover.png", Borders(34, 12, 30, 12), tile=False)
    insensitive_background Solid("#07131d80")
    padding (34, 12, 30, 12)

style choice_button_text is default:
    properties gui.text_properties("choice_button")

    outlines [(1, "#02070b", 0, 0)]


## Quick Menu screen ###########################################################
##
## The quick menu is displayed in-game to provide easy access to the out-of-game
## menus.

screen quick_menu():

    ## Ensure this appears on top of other screens.
    zorder 100

    if quick_menu:

        hbox:
            style_prefix "quick"

            xalign 0.5
            yalign 1.0

            textbutton _("Back") action Rollback()
            textbutton _("Forward") action RollForward()
            textbutton _("History") action ShowMenu('history')
            textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("Auto") action Preference("auto-forward", "toggle")
            textbutton _("Save") action ShowMenu('save')
            textbutton _("Q.Save") action QuickSave()
            textbutton _("Q.Load") action QuickLoad()
            textbutton _("Prefs") action ShowMenu('preferences')


## This code ensures that the quick_menu screen is displayed in-game, whenever
## the player has not explicitly hidden the interface.
init python:
    config.overlay_screens.append("quick_menu")

default quick_menu = True

style quick_button is default
style quick_button_text is button_text

style quick_button:
    properties gui.button_properties("quick_button")

    ## No plate under a quick button: it is furniture on the panel's edge.
    background None
    hover_background None

style quick_button_text:
    properties gui.text_properties("quick_button")

    font "gui/fonts/Inconsolata-Regular.ttf"


################################################################################
## Main and Game Menu Screens
################################################################################

## Navigation screen ###########################################################
##
## This screen is included in the main and game menus, and provides navigation
## to other menus, and to start the game.

screen navigation():

    vbox:
        style_prefix "navigation"

        xpos gui.navigation_xpos
        yalign 0.5

        spacing gui.navigation_spacing

        if main_menu:

            textbutton _("Start") action Start()

        else:

            textbutton _("History") action ShowMenu("history")

            textbutton _("Save") action ShowMenu("save")

        textbutton _("Load") action ShowMenu("load")

        textbutton _("Preferences") action ShowMenu("preferences")

        if _in_replay:

            textbutton _("End Replay") action EndReplay(confirm=True)

        elif not main_menu:

            textbutton _("Main Menu") action MainMenu()

        textbutton _("About") action ShowMenu("about")

        if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):

            ## Help isn't necessary or relevant to mobile devices.
            textbutton _("Help") action ShowMenu("help")

        if renpy.variant("pc"):

            ## The quit button is banned on iOS and unnecessary on Android and Web.
            textbutton _("Quit") action Quit(confirm=not main_menu)


style navigation_button is gui_button
style navigation_button_text is gui_button_text

style navigation_button:
    size_group "navigation"
    properties gui.button_properties("navigation_button")

style navigation_button_text:
    properties gui.text_properties("navigation_button")


screen main_menu_command_rail():

    style_prefix "main_menu_command"

    ## Keep the commands as one compact console rail. The exterior already
    ## carries the frame's visual weight; scattering controls to both edges
    ## made related actions read as separate navigation regions.
    fixed:
        xpos 34
        ypos 626
        xsize 1212
        ysize 70

        hbox:
            xalign 0.5
            yalign 0.5
            spacing 18

            textbutton _("Start") action Start()
            if config.developer:
                textbutton _("Storm Tests") action ShowMenu("eot_storm_peak_tests")
                textbutton _("Act 3 Music") action ShowMenu("eot_act3_music_tests")
            textbutton _("Load") action ShowMenu("load")
            textbutton _("Preferences") action ShowMenu("preferences")
            textbutton _("About") action ShowMenu("about")

            if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):
                textbutton _("Help") action ShowMenu("help")

            if renpy.variant("pc"):
                textbutton _("Quit") action Quit(confirm=False)


style main_menu_command_button is gui_button
style main_menu_command_button_text is gui_button_text

style main_menu_command_button:
    background None
    hover_background Solid("#163846b8")
    selected_background Solid("#163846b8")
    xpadding 14
    ypadding 10

style main_menu_command_button_text:
    font "gui/fonts/Inconsolata-Regular.ttf"
    size 21
    color "#a9bfca"
    hover_color "#8fffe0"
    selected_color "#8fffe0"
    outlines [(1, "#02090dcc", 0, 1)]


## Main Menu screen ############################################################
##
## Used to display the main menu when Ren'Py starts.
##
## http://www.renpy.org/doc/html/screen_special.html#main-menu

screen main_menu():

    ## This ensures that any other menu screen is replaced.
    tag menu
    on "show" action Hide("endcredits")

    style_prefix "main_menu"

    add gui.main_menu_background

    if renpy.variant("small"):
        ## Touch layouts retain the larger vertical controls.
        frame:
            pass

        use navigation
    else:
        ## A low command deck leaves the observatory readable from wing to dish.
        add Solid("#02090ddd"):
            xpos 0
            ypos 612
            xsize 1280
            ysize 108

        add Solid("#66ffcc70"):
            xpos 0
            ypos 612
            xsize 1280
            ysize 1

        use main_menu_command_rail

    if gui.show_name:

        vbox:
            text "[config.name!t]":
                style "main_menu_title"

            text _("A signal from the future"):
                style "main_menu_version"


style main_menu_frame is empty
style main_menu_vbox is vbox
style main_menu_text is gui_text
style main_menu_title is main_menu_text
style main_menu_version is main_menu_text

style main_menu_frame:
    xsize 280
    yfill True

    background "gui/overlay/main_menu.png"

style main_menu_vbox:
    xalign 0.0
    xoffset 34
    xsize 900
    yalign 0.0
    yoffset 28

style main_menu_text:
    properties gui.text_properties("main_menu", accent=True)

style main_menu_title:
    properties gui.text_properties("title")
    font "gui/fonts/Inconsolata-Regular.ttf"

style main_menu_version:
    properties gui.text_properties("version")
    font "gui/fonts/Inconsolata-Regular.ttf"


## Game Menu screen ############################################################
##
## This lays out the basic common structure of a game menu screen. It's called
## with the screen title, and displays the background, title, and navigation.
##
## The scroll parameter can be None, or one of "viewport" or "vpgrid". When
## this screen is intended to be used with one or more children, which are
## transcluded (placed) inside it.

screen game_menu(title, scroll=None):

    style_prefix "game_menu"

    if main_menu:
        add gui.main_menu_background
    else:
        add gui.game_menu_background

    frame:
        style "game_menu_outer_frame"

        hbox:

            ## Reserve space for the navigation section.
            frame:
                style "game_menu_navigation_frame"

            frame:
                style "game_menu_content_frame"

                if scroll == "viewport":

                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        pagekeys True

                        side_yfill True

                        vbox:
                            transclude

                elif scroll == "vpgrid":

                    vpgrid:
                        cols 1
                        yinitial 1.0

                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        pagekeys True

                        side_yfill True

                        transclude

                else:

                    transclude

    use navigation

    textbutton _("Return"):
        style "return_button"

        action Return()

    label title

    if main_menu:
        key "game_menu" action ShowMenu("main_menu")


style game_menu_outer_frame is empty
style game_menu_navigation_frame is empty
style game_menu_content_frame is empty
style game_menu_viewport is gui_viewport
style game_menu_side is gui_side
style game_menu_scrollbar is gui_vscrollbar

style game_menu_label is gui_label
style game_menu_label_text is gui_label_text

style return_button is navigation_button
style return_button_text is navigation_button_text

style game_menu_outer_frame:
    bottom_padding 30
    top_padding 120

    background "gui/overlay/game_menu.png"

style game_menu_navigation_frame:
    xsize 280
    yfill True

style game_menu_content_frame:
    left_margin 40
    right_margin 20
    top_margin 10

style game_menu_viewport:
    xsize 920

style game_menu_vscrollbar:
    unscrollable gui.unscrollable

style game_menu_side:
    spacing 10

style game_menu_label:
    xpos 50
    ysize 120

style game_menu_label_text:
    size gui.title_text_size
    color gui.accent_color
    yalign 0.5

style return_button:
    xpos gui.navigation_xpos
    yalign 1.0
    yoffset -30


## About screen ################################################################
##
## This screen gives credit and copyright information about the game and Ren'Py.
##
## There's nothing special about this screen, and hence it also serves as an
## example of how to make a custom screen.

screen about():

    tag menu

    ## This use statement includes the game_menu screen inside this one. The
    ## vbox child is then included inside the viewport inside the game_menu
    ## screen.
    use game_menu(_("About"), scroll="viewport"):

        style_prefix "about"

        vbox:

            label "[config.name!t]"
            text _("[config.version!t]\n")

            text _("A visual novel about time, choice, and the signals we send to ourselves.\n")

            hbox:
                spacing 15
                text _("Initial Idea") style "about_small"
                text _("Opus 4.5")

            hbox:
                spacing 15
                text _("Programming") style "about_small" yalign 0.0
                text _("Opus 4.5-5, Fable 5,\nChatGPT 5.6 Sol, ChatGPT Astra 6")

            hbox:
                spacing 15
                text _("Writing") style "about_small" yalign 0.0
                text _("Opus 4.5-5, Fable 5,\nChatGPT 5.6 Sol, ChatGPT Astra 6, vnflight")

            hbox:
                spacing 15
                text _("Music") style "about_small" yalign 0.0
                text _("Fable 5, ChatGPT 5.6 Sol\nWith help from ElevenLabs")

            hbox:
                spacing 15
                text _("Title Theme") style "about_small" yalign 0.0
                text _("Composed in-house from the game's own palette\n(procedural station tones and warm bass,\nElevenLabs sound-effect auditions, VSCO-2-CE piano, CC0)")

            hbox:
                spacing 15
                text _("In The Loop") style "about_small"
                text _("vnflight")

            null height 15

            hbox:
                spacing 15
                text _("Engine") style "about_small"
                text _("Ren'Py [renpy.version_only]")

            null height 15

            text _("\nMade with {a=https://www.renpy.org/}Ren'Py{/a} [renpy.version_only]")
            null height 15
            text _("[renpy.license!t]") size 20


style about_label is gui_label
style about_label_text is gui_label_text
style about_text is gui_text

style about_label_text:
    size gui.label_text_size

style about_small:
    size 20
    minwidth 260
    textalign 1.0
    yalign 0.9


## Load and Save screens #######################################################
##
## These screens are responsible for letting the player save the game and load
## it again. Since they share nearly everything in common, both are implemented
## in terms of a third screen, file_slots.
##
## https://www.renpy.org/doc/html/screen_special.html#save https://
## www.renpy.org/doc/html/screen_special.html#load

screen save():

    tag menu

    use file_slots(_("Save"))


screen load():

    tag menu

    use file_slots(_("Load"))


screen file_slots(title):

    default page_name_value = FilePageNameInputValue(pattern=_("Page {}"), auto=_("Automatic saves"), quick=_("Quick saves"))

    use game_menu(title):

        fixed:

            ## This ensures the input will get the enter event before any of the
            ## buttons do.
            order_reverse True

            ## The page name, which can be edited by clicking on a button.
            button:
                style "page_label"

                key_events True
                xalign 0.5
                action page_name_value.Toggle()

                input:
                    style "page_label_text"
                    value page_name_value

            ## The grid of file slots.
            grid gui.file_slot_cols gui.file_slot_rows:
                style_prefix "slot"

                xalign 0.5
                yalign 0.5

                spacing gui.slot_spacing

                for i in range(gui.file_slot_cols * gui.file_slot_rows):

                    $ slot = i + 1

                    button:
                        action FileAction(slot)

                        has vbox

                        add FileScreenshot(slot) xalign 0.5

                        text FileTime(slot, format=_("{#file_time}%A, %B %d %Y, %H:%M"), empty=_("empty slot")):
                            style "slot_time_text"

                        text FileSaveName(slot):
                            style "slot_name_text"

                        if "save_delete" in config.keymap:
                            key "save_delete" action FileDelete(slot)

            ## Buttons to access other pages.
            hbox:
                style_prefix "page"

                xalign 0.5
                yalign 1.0

                spacing gui.page_spacing

                textbutton _("<") action FilePagePrevious()
                if "save_page_prev" in config.keymap:
                    key "save_page_prev" action FilePagePrevious()

                if config.has_autosave:
                    textbutton _("{#auto_page}A") action FilePage("auto")

                if config.has_quicksave:
                    textbutton _("{#quick_page}Q") action FilePage("quick")

                ## range(1, 10) gives the numbers from 1 to 9.
                for page in range(1, 10):
                    textbutton "[page]" action FilePage(page)

                textbutton _(">") action FilePageNext()
                if "save_page_next" in config.keymap:
                    key "save_page_next" action FilePageNext()


style page_label is gui_label
style page_label_text is gui_label_text
style page_button is gui_button
style page_button_text is gui_button_text

style slot_button is gui_button
style slot_button_text is gui_button_text
style slot_time_text is slot_button_text
style slot_name_text is slot_button_text

style page_label:
    xpadding 50
    ypadding 3

style page_label_text:
    textalign 0.5
    layout "subtitle"
    hover_color gui.hover_color

style page_button:
    properties gui.button_properties("page_button")

style page_button_text:
    properties gui.text_properties("page_button")

style slot_button:
    properties gui.button_properties("slot_button")

style slot_button_text:
    properties gui.text_properties("slot_button")


## Preferences screen ##########################################################
##
## The preferences screen allows the player to configure the game to better suit
## themselves.
##
## https://www.renpy.org/doc/html/screen_special.html#preferences

screen preferences():

    tag menu

    if renpy.mobile:
        $ cols = 2
    else:
        $ cols = 4

    use game_menu(_("Preferences"), scroll="viewport"):

        vbox:

            hbox:
                box_wrap True

                if renpy.variant("pc") or renpy.variant("web"):

                    vbox:
                        style_prefix "radio"
                        label _("Display")
                        textbutton _("Window") action Preference("display", "window")
                        textbutton _("Fullscreen") action Preference("display", "fullscreen")

                vbox:
                    style_prefix "check"
                    label _("Skip")
                    textbutton _("Unseen Text") action Preference("skip", "toggle")
                    textbutton _("After Choices") action Preference("after choices", "toggle")
                    textbutton _("Transitions") action InvertSelected(Preference("transitions", "toggle"))

                ## Additional vboxes of type "radio_pref" or "check_pref" can be
                ## added here, to add additional creator-defined preferences.

#begin language_picker

                vbox:
                    style_prefix "radio"
                    label _("Language")

                    textbutton "English" text_font "DejaVuSans.ttf" action Language(None)
                    textbutton "Česky" text_font "DejaVuSans.ttf" action Language("czech")
                    textbutton "Dansk" text_font "DejaVuSans.ttf" action Language("danish")
                    textbutton "Français" text_font "DejaVuSans.ttf" action Language("french")
                    textbutton "Italiano" text_font "DejaVuSans.ttf" action Language("italian")
                    textbutton "Bahasa Melayu" text_font "DejaVuSans.ttf" action Language("malay")
                    textbutton "Русский" text_font "DejaVuSans.ttf" action Language("russian")

                vbox:
                    style_prefix "radio"
                    label _(" ")

                    textbutton "Español" text_font "DejaVuSans.ttf" action Language("spanish")
                    textbutton "Українська" text_font "DejaVuSans.ttf" action Language("ukrainian")
                    textbutton "日本語" text_font "SourceHanSansLite.ttf" action Language("japanese")
                    textbutton "한국어" text_font "SourceHanSansLite.ttf" action Language("korean")
                    textbutton "简体中文" text_font "SourceHanSansLite.ttf" action Language("schinese")
                    textbutton "繁體中文" text_font "SourceHanSansLite.ttf" action Language("tchinese")

#end language_picker

            null height (4 * gui.pref_spacing)

            hbox:
                style_prefix "slider"
                box_wrap True

                vbox:

                    label _("Text Speed")

                    bar value Preference("text speed")

                    label _("Auto-Forward Time")

                    bar value Preference("auto-forward time")

                vbox:

                    if config.has_music:
                        label _("Music Volume")

                        hbox:
                            bar value Preference("music volume")

                    if config.has_sound:

                        label _("Sound Volume")

                        hbox:
                            bar value Preference("sound volume")

                            if config.sample_sound:
                                textbutton _("Test") action Play("sound", config.sample_sound)


                    if config.has_voice:
                        label _("Voice Volume")

                        hbox:
                            bar value Preference("voice volume")

                            if config.sample_voice:
                                textbutton _("Test") action Play("voice", config.sample_voice)

                    if config.has_music or config.has_sound or config.has_voice:
                        null height gui.pref_spacing

                        textbutton _("Mute All"):
                            action Preference("all mute", "toggle")
                            style "mute_all_button"


style pref_label is gui_label
style pref_label_text is gui_label_text
style pref_vbox is vbox

style radio_label is pref_label
style radio_label_text is pref_label_text
style radio_button is gui_button
style radio_button_text is gui_button_text
style radio_vbox is pref_vbox

style check_label is pref_label
style check_label_text is pref_label_text
style check_button is gui_button
style check_button_text is gui_button_text
style check_vbox is pref_vbox

style slider_label is pref_label
style slider_label_text is pref_label_text
style slider_slider is gui_slider
style slider_button is gui_button
style slider_button_text is gui_button_text
style slider_pref_vbox is pref_vbox

style mute_all_button is check_button
style mute_all_button_text is check_button_text

style pref_label:
    top_margin gui.pref_spacing
    bottom_margin 2

style pref_label_text:
    yalign 1.0

style pref_vbox:
    xsize 225

style radio_vbox:
    spacing gui.pref_button_spacing

style radio_button:
    properties gui.button_properties("radio_button")
    foreground "gui/button/radio_[prefix_]foreground.png"

style radio_button_text:
    properties gui.text_properties("radio_button")

style check_vbox:
    spacing gui.pref_button_spacing

style check_button:
    properties gui.button_properties("check_button")
    foreground "gui/button/check_[prefix_]foreground.png"

style check_button_text:
    properties gui.text_properties("check_button")

style slider_slider:
    xsize 350

style slider_button:
    properties gui.button_properties("slider_button")
    yalign 0.5
    left_margin 10

style slider_button_text:
    properties gui.text_properties("slider_button")

style slider_vbox:
    xsize 450


## History screen ##############################################################
##
## This is a screen that displays the dialogue history to the player. While
## there isn't anything special about this screen, it does have to access the
## dialogue history stored in _history_list.
##
## https://www.renpy.org/doc/html/history.html

screen history():

    tag menu

    ## Avoid predicting this screen, as it can be very large.
    predict False

    use game_menu(_("History"), scroll=("vpgrid" if gui.history_height else "viewport")):

        style_prefix "history"

        for h in _history_list:

            window:

                ## This lays things out properly if history_height is None.
                has fixed:
                    yfit True

                if h.who:

                    label h.who:
                        style "history_name"
                        substitute False

                        ## Take the color of the who text from the Character, if
                        ## set.
                        if "color" in h.who_args:
                            text_color h.who_args["color"]

                $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)
                text what:
                    substitute False

        if not _history_list:
            label _("The dialogue history is empty.")

define gui.history_allow_tags = { "alt", "noalt", "rt", "rb", "art" }

style history_window is empty

style history_name is gui_label
style history_name_text is gui_label_text
style history_text is gui_text

style history_text is gui_text

style history_label is gui_label
style history_label_text is gui_label_text

style history_window:
    xfill True
    ysize gui.history_height

style history_name:
    xpos gui.history_name_xpos
    xanchor gui.history_name_xalign
    ypos gui.history_name_ypos
    xsize gui.history_name_width

style history_name_text:
    min_width gui.history_name_width
    textalign gui.history_name_xalign

style history_text:
    xpos gui.history_text_xpos
    ypos gui.history_text_ypos
    xanchor gui.history_text_xalign
    xsize gui.history_text_width
    min_width gui.history_text_width
    textalign gui.history_text_xalign
    layout ("subtitle" if gui.history_text_xalign else "tex")

style history_label:
    xfill True

style history_label_text:
    xalign 0.5


## Help screen #################################################################
##
## A screen that gives information about key and mouse bindings. It uses other
## screens (keyboard_help, mouse_help, and gamepad_help) to display the actual
## help.

screen help():

    tag menu

    default device = "keyboard"

    use game_menu(_("Help"), scroll="viewport"):

        style_prefix "help"

        vbox:
            spacing 15

            hbox:

                textbutton _("Keyboard") action SetScreenVariable("device", "keyboard")
                textbutton _("Mouse") action SetScreenVariable("device", "mouse")

                if GamepadExists():
                    textbutton _("Gamepad") action SetScreenVariable("device", "gamepad")

            if device == "keyboard":
                use keyboard_help
            elif device == "mouse":
                use mouse_help
            elif device == "gamepad":
                use gamepad_help


screen keyboard_help():

    hbox:
        label _("Enter")
        text _("Advances dialogue and activates the interface.")

    hbox:
        label _("Space")
        text _("Advances dialogue without selecting choices.")

    hbox:
        label _("Arrow Keys")
        text _("Navigate the interface.")

    hbox:
        label _("Escape")
        text _("Accesses the game menu.")

    hbox:
        label _("Ctrl")
        text _("Skips dialogue while held down.")

    hbox:
        label _("Tab")
        text _("Toggles dialogue skipping.")

    hbox:
        label _("Page Up")
        text _("Rolls back to earlier dialogue.")

    hbox:
        label _("Page Down")
        text _("Rolls forward to later dialogue.")

    hbox:
        label "H"
        text _("Hides the user interface.")

    hbox:
        label "S"
        text _("Takes a screenshot.")

    hbox:
        label "V"
        text _("Toggles assistive {a=https://www.renpy.org/l/voicing}self-voicing{/a}.")

    hbox:
        label "Shift+A"
        text _("Opens the accessibility menu.")


screen mouse_help():

    hbox:
        label _("Left Click")
        text _("Advances dialogue and activates the interface.")

    hbox:
        label _("Middle Click")
        text _("Hides the user interface.")

    hbox:
        label _("Right Click")
        text _("Accesses the game menu.")

    hbox:
        label _("Mouse Wheel Up")
        text _("Rolls back to earlier dialogue.")

    hbox:
        label _("Mouse Wheel Down")
        text _("Rolls forward to later dialogue.")


screen gamepad_help():

    hbox:
        label _("Right Trigger\nA/Bottom Button")
        text _("Advances dialogue and activates the interface.")

    hbox:
        label _("Left Trigger\nLeft Shoulder")
        text _("Rolls back to earlier dialogue.")

    hbox:
        label _("Right Shoulder")
        text _("Rolls forward to later dialogue.")

    hbox:
        label _("D-Pad, Sticks")
        text _("Navigate the interface.")

    hbox:
        label _("Start, Guide")
        text _("Accesses the game menu.")

    hbox:
        label _("Y/Top Button")
        text _("Hides the user interface.")

    textbutton _("Calibrate") action GamepadCalibrate()


style help_button is gui_button
style help_button_text is gui_button_text
style help_label is gui_label
style help_label_text is gui_label_text
style help_text is gui_text

style help_button:
    properties gui.button_properties("help_button")
    xmargin 8

style help_button_text:
    properties gui.text_properties("help_button")

style help_label:
    xsize 250
    right_padding 20

style help_label_text:
    size gui.text_size
    xalign 1.0
    textalign 1.0



################################################################################
## Additional screens
################################################################################


## Confirm screen ##############################################################
##
## The confirm screen is called when Ren'Py wants to ask the player a yes or no
## question.
##
## http://www.renpy.org/doc/html/screen_special.html#confirm

screen confirm(message, yes_action, no_action):

    ## Ensure other screens do not get input while this screen is displayed.
    modal True

    zorder 200

    style_prefix "confirm"

    add "gui/overlay/confirm.png"

    frame:

        vbox:
            xalign .5
            yalign .5
            spacing 30

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("Yes") action yes_action
                textbutton _("No") action no_action

    ## Right-click and escape answer "no".
    key "game_menu" action no_action


style confirm_frame is gui_frame
style confirm_prompt is gui_prompt
style confirm_prompt_text is gui_prompt_text
style confirm_button is gui_medium_button
style confirm_button_text is gui_medium_button_text

style confirm_frame:
    background Frame([ "gui/confirm_frame.png", "gui/frame.png"], gui.confirm_frame_borders, tile=gui.frame_tile)
    padding gui.confirm_frame_borders.padding
    xalign .5
    yalign .5

style confirm_prompt_text:
    textalign 0.5
    layout "subtitle"

style confirm_button:
    properties gui.button_properties("confirm_button")

style confirm_button_text:
    properties gui.text_properties("confirm_button")


## Skip indicator screen #######################################################
##
## The skip_indicator screen is displayed to indicate that skipping is in
## progress.
##
## https://www.renpy.org/doc/html/screen_special.html#skip-indicator

screen skip_indicator():

    zorder 100
    style_prefix "skip"

    frame:

        hbox:
            spacing 6

            text _("Skipping")

            text "▸" at delayed_blink(0.0, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.2, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.4, 1.0) style "skip_triangle"


## This transform is used to blink the arrows one after another.
transform delayed_blink(delay, cycle):
    alpha .5

    pause delay

    block:
        linear .2 alpha 1.0
        pause .2
        linear .2 alpha 0.5
        pause (cycle - .4)
        repeat


style skip_frame is empty
style skip_text is gui_text
style skip_triangle is skip_text

style skip_frame:
    ypos gui.skip_ypos
    background Frame("gui/skip.png", gui.skip_frame_borders, tile=gui.frame_tile)
    padding gui.skip_frame_borders.padding

style skip_text:
    size gui.notify_text_size

style skip_triangle:
    ## We have to use a font that has the BLACK RIGHT-POINTING SMALL TRIANGLE
    ## glyph in it.
    font "DejaVuSans.ttf"


## Notify screen ###############################################################
##
## The notify screen is used to show the player a message. (For example, when
## the game is quicksaved or a screenshot has been taken.)
##
## https://www.renpy.org/doc/html/screen_special.html#notify-screen

screen notify(message):

    zorder 100
    style_prefix "notify"

    frame at notify_appear:
        text "[message!tq]"

    timer 3.25 action Hide('notify')


transform notify_appear:
    on show:
        alpha 0
        linear .25 alpha 1.0
    on hide:
        linear .5 alpha 0.0


style notify_frame is empty
style notify_text is gui_text

style notify_frame:
    ypos gui.notify_ypos

    background Frame("gui/notify.png", gui.notify_frame_borders, tile=gui.frame_tile)
    padding gui.notify_frame_borders.padding

style notify_text:
    properties gui.text_properties("notify")


## NVL screen ##################################################################
##
## This screen is used for NVL-mode dialogue and menus.
##
## http://www.renpy.org/doc/html/screen_special.html#nvl


screen nvl(dialogue, items=None):

    ## The live ECHO-7 terminal owns its own framing and always wins.
    ## Outside the live terminal there are two visual registers: the station
    ## log throughout the Long Night, and the cinematic letterbox for act
    ## turns/endings. `bulletin` is retained as a legacy scene value but maps
    ## to the station log so hub notices do not oscillate blue/amber.
    if terminal_mode:
        use echo_terminal_nvl(dialogue, items)

    elif nvl_frame == "bulletin":
        ## ALERT OUTLINE (2026-08-18, user: the amber re-skin was "too
        ## distinct... too many options"; an outline that goes away with
        ## the alert is enough). Same log chrome, same palette — the
        ## `bulletin` scene value now only adds a transient amber outline
        ## for the block's lifetime; every alert site resets nvl_frame to
        ## "log" when its prose ends, so the outline clears on the next
        ## ordinary text event.
        use echo_nvl_log(dialogue, items, alert=True)

    elif nvl_frame == "cinematic":
        use echo_nvl_cinematic(dialogue, items)

    elif nvl_frame == "scene":
        use echo_nvl_scene(dialogue, items)

    else:
        use echo_nvl_log(dialogue, items)

    ## No side image under the cinematic or mixed-scene registers: the former
    ## leaves only words, while the latter keeps the room itself visible.
    if (nvl_frame not in ("cinematic", "scene") or terminal_mode) and not long_night_active:
        add SideImage() xalign 0.0 yalign 1.0


screen echo_terminal_nvl(dialogue, items=None):

    use echo_terminal_panel:
        viewport:
            xpos 50 ypos 64 xsize 1124 ysize 534
            clipping True
            yinitial 1.0
            mousewheel True
            draggable True

            vbox:
                xsize 1124
                spacing 3

                use nvl_dialogue(dialogue)

                use echo_terminal_nvl_choices(items)


screen echo_terminal_nvl_choices(items=None):

    if items:
        for i in items:

            textbutton i.caption:
                action i.action
                style "terminal_nvl_button"
                xpos 96
                xsize 1028
                top_margin 10


screen nvl_dialogue(dialogue):

    for index, d in enumerate(dialogue):

        if terminal_mode:
            window:
                id d.window_id
                style "terminal_nvl_entry"
                top_margin (
                    10 if index > 0 and
                    ((d.who == "THOUGHT" or d.who is None) !=
                     (dialogue[index - 1].who == "THOUGHT" or dialogue[index - 1].who is None))
                    else 0
                )

                if d.who == "SYSTEM":
                    text d.what:
                        id d.what_id
                        style "terminal_nvl_system"
                        xpos 96
                        xanchor 0
                        xsize 1028
                        color "#7dffad"
                        size 18
                        font "gui/fonts/JetBrainsMono-Regular.ttf"

                elif d.who == "THOUGHT":
                    text d.what:
                        id d.what_id
                        style "terminal_nvl_thought"
                        xpos 96
                        xanchor 0
                        xsize 1028
                        color "#c9c1dd"

                else:
                    fixed:
                        xfill True
                        yfit True

                        if d.who is not None:

                            text d.who:
                                id d.who_id
                                style "terminal_nvl_label"
                                xpos 0
                                xanchor 0
                                xsize 88
                                min_width 88
                                size 18
                                font "gui/fonts/JetBrainsMono-Regular.ttf"
                                text_align 1.0

                        text d.what:
                            id d.what_id
                            style ("terminal_nvl_dialogue" if d.who is not None else "terminal_nvl_narration")
                            xpos 96
                            xanchor 0
                            xsize 1028
                            color ("#dcfff0" if d.who is not None else "#eee8dc")
                            size (18 if d.who is not None else 20)
                            font ("gui/fonts/JetBrainsMono-Regular.ttf" if d.who is not None else gui.text_font)
                            text_align 0.0
                            xalign 0.0

        else:
            window:
                id d.window_id

                fixed:
                    yfit gui.nvl_height is None

                    if d.who is not None and d.who not in ("SYSTEM", "THOUGHT"):

                        text d.who:
                            id d.who_id

                    text d.what:
                        id d.what_id


## This controls the maximum number of NVL-mode entries that can be displayed at
## once.
define config.nvl_list_length = 10

style nvl_window is default
style nvl_entry is default

style nvl_label is say_label
style nvl_dialogue is say_dialogue

style nvl_button is button
style nvl_button_text is button_text

style nvl_window:
    xfill True
    yfill True

    background "gui/nvl.png"
    padding gui.nvl_borders.padding

style nvl_entry:
    xfill True
    ysize gui.nvl_height

style nvl_label:
    xpos gui.nvl_name_xpos
    xanchor gui.nvl_name_xalign
    ypos gui.nvl_name_ypos
    yanchor 0.0
    xsize gui.nvl_name_width
    min_width gui.nvl_name_width
    textalign gui.nvl_name_xalign

style nvl_dialogue:
    xpos gui.nvl_text_xpos
    xanchor gui.nvl_text_xalign
    ypos gui.nvl_text_ypos
    xsize gui.nvl_text_width
    min_width gui.nvl_text_width
    textalign gui.nvl_text_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_thought:
    xpos gui.nvl_thought_xpos
    xanchor gui.nvl_thought_xalign
    ypos gui.nvl_thought_ypos
    xsize gui.nvl_thought_width
    min_width gui.nvl_thought_width
    textalign gui.nvl_thought_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_button:
    properties gui.button_properties("nvl_button")
    xpos gui.nvl_button_xpos
    xanchor gui.nvl_button_xalign

style nvl_button_text:
    properties gui.text_properties("nvl_button")

style terminal_nvl_window is default:
    xalign 0.5
    yalign 0.5
    xsize 1224
    ysize 660
    background Solid("#06111ced")
    xpadding 0
    ypadding 0

style terminal_nvl_entry is default:
    xfill True

style terminal_nvl_label is default:
    font "gui/fonts/JetBrainsMono-Regular.ttf"
    min_width 88
    xsize 88
    text_align 1.0
    color "#66ffcc"
    size 18
    outlines [(1, "#123245", 0, 0)]

style terminal_nvl_dialogue is default:
    font "gui/fonts/JetBrainsMono-Regular.ttf"
    xsize 1028
    color "#dcfff0"
    size 18
    line_spacing 0
    text_align 0.0
    ## Each typewriter tick supplies a longer prefix. Do not rebalance its
    ## lines or redistribute glyph spacing to match the scaled text bounds:
    ## either would move characters that have already appeared.
    layout "greedy"
    adjust_spacing False
    outlines [(1, "#123245", 0, 0)]

style terminal_nvl_system is terminal_nvl_dialogue:
    xsize 1028
    color "#baffd1"
    size 18

style terminal_nvl_narration is terminal_nvl_dialogue:
    xsize 1028
    font gui.text_font
    color "#eee8dc"
    size 20
    line_spacing 5
    outlines [(1, "#06111c", 0, 0)]

style terminal_nvl_thought is terminal_nvl_narration:
    color "#c9c1dd"
    italic True

style terminal_nvl_button is button:
    ## General UI buttons are 36px tall; terminal replies may wrap.
    yminimum 36
    ymaximum None
    background Solid("#091a2add")
    hover_background Solid("#12314dee")
    insensitive_background Solid("#08111aaa")
    xpadding 14
    ypadding 10
    xfill False

style terminal_nvl_button_text is button_text:
    font "gui/fonts/JetBrainsMono-Regular.ttf"
    color "#d8f2ff"
    hover_color "#ffffff"
    insensitive_color "#7d9cab"
    size 18


################################################################################
## Mobile Variants
################################################################################

style pref_vbox:
    variant "medium"
    xsize 450

## Since a mouse may not be present, we replace the quick menu with a version
## that uses fewer and bigger buttons that are easier to touch.
screen quick_menu():
    variant "touch"

    zorder 100

    hbox:
        style_prefix "quick"

        xalign 0.5
        yalign 1.0

        textbutton _("Back") action Rollback()
        textbutton _("Forward") action RollForward()
        textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
        textbutton _("Auto") action Preference("auto-forward", "toggle")
        textbutton _("Menu") action ShowMenu()


style window:
    variant "small"
    background "gui/phone/textbox.png"

style nvl_window:
    variant "small"
    background "gui/phone/nvl.png"

style main_menu_frame:
    variant "small"
    background "gui/phone/overlay/main_menu.png"

style game_menu_outer_frame:
    variant "small"
    background "gui/phone/overlay/game_menu.png"

style game_menu_navigation_frame:
    variant "small"
    xsize 340

style game_menu_content_frame:
    variant "small"
    top_margin 0

style game_menu_viewport:
    variant "small"
    xsize 870

style pref_vbox:
    variant "small"
    xsize 400

style slider_pref_vbox:
    variant "small"
    xsize None

style slider_pref_slider:
    variant "small"
    xsize 600

# Shrink the title.
style main_menu_vbox:
    variant "small"
    xsize 900
