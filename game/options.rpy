## This file contains options that can be changed to customize your game.

## SDL/Wayland cannot publish a per-window bitmap icon the way X11 does.
## Plasma and other compositors instead match this application ID to an
## installed .desktop entry. Keep it aligned with the existing save/WM class.
python early:
    import os
    os.environ.setdefault(
        "SDL_VIDEO_WAYLAND_WMCLASS", "echoes_of_tomorrow-1")

## Basics ######################################################################

define config.name = _("Echoes of Tomorrow")

define gui.show_name = True

define config.version = "1.0"

define gui.about = _("A visual novel about time, choice, and the signals we send to ourselves.\n\nCreated with Ren'Py.\n\nWritten as a demonstration of NVL-mode features including NVL characters, NVL narrator, NVL menus, mixed NVL/ADV transitions, thought text, and branching narrative.")

define build.name = "echoes_of_tomorrow"

define build.version = "1.0"

## Sounds and music ############################################################

define config.has_sound = True
define config.has_music = True
define config.has_voice = False

## Title theme (experiments/echoes_music_v46_title, "Long night", piano at
## 70%). It plays on the music channel; label start fades it out before the
## opening cue starts.
define config.main_menu_music = "audio/music/title/eot_title_long_night.ogg"
define config.main_menu_music_fadein = 1.5

## Story cues scale the music channel to EOT_MUSIC_MIX (0.5) and that volume
## survives a return to the menu, so the title would play 6 dB quieter after
## a game than on first launch. Pin the channel before every main menu. 0.85
## puts the title (-12.3 dBFS RMS) at the opening cue's effective level
## (-7.8 dBFS RMS at EOT_MUSIC_MIX).
## 0.85 matched the opening cue's effective level; 0.68 is that at 80%.
define EOT_TITLE_MIX = 0.68

label before_main_menu:
    $ renpy.music.set_volume(EOT_TITLE_MIX, delay=0.0, channel="music")
    return


## Transitions #################################################################

define config.enter_transition = dissolve
define config.exit_transition = dissolve

define config.after_load_transition = None

define config.end_game_transition = fade


## Window management ###########################################################

## Controls when the dialogue window is displayed. If "show", it is always
## displayed. If "hide", it is only displayed when dialogue is present. If
## "auto", the window is hidden before scene statements and shown again once
## dialogue is displayed.

define config.window = "auto"

define config.window_show_transition = Dissolve(.2)
define config.window_hide_transition = Dissolve(.2)


## Preference defaults #########################################################

## Controls the default text speed. The default, 0, is infinite, while any other
## number is the number of characters per second to type out.

default preferences.text_cps = 40

## The default auto-forward delay. Larger numbers lead to longer waits, with 0
## to 30 being the valid range.

default preferences.afm_time = 15


## Save directory ##############################################################

## Controls the platform-specific place Ren'Py will place the save files for
## this game.

define config.save_directory = "echoes_of_tomorrow-1"


## Icon ########################################################################

define config.window_icon = "gui/window_icon_v2.png"


## Build configuration #########################################################

init python:

    config.searchpath.append(config.renpy_base + "/sdk-fonts")
    build.classify_renpy("sdk-fonts/**", "all")
    build._sdk_fonts = True

    build.classify('**~', None)
    build.classify('**.bak', None)
    build.classify('**/.**', None)
    build.classify('**/#**', None)
    build.classify('**/thumbs.db', None)

    build.documentation('*.html')
    build.documentation('*.txt')

## Normal-play defaults. Test utilities remain in source but are not exposed.
define config.developer = False
define config.console = False

## Allow rollback so players can revisit choices
define config.rollback_enabled = True

init python:
    ## Keep Space/Enter/click advancing dialogue even when a quick-menu or
    ## terminal button has focus.
    config.keymap["dismiss_unfocused"] = list(config.keymap["dismiss"])
