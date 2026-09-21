## Developer-only Act 3 launch points. Start() creates a fresh game context, so
## each preset only needs to establish the route-defining facts before handing
## control to the real storm climax.

label eot_debug_storm_peak_common:
    $ time_remaining = 0
    $ storm_intensity = 3
    $ long_night_active = True
    $ current_location = "lab"
    $ signal_strength = 55
    $ aria_integrity = 60
    $ marcus_relationship = 3
    $ marcus_trust = 1
    $ eot_music_stop(fadeout=0.0)
    $ eot_hub_music_stop(fadeout=0.0)
    return


label eot_debug_storm_peak_file:
    call eot_debug_storm_peak_common
    $ coherence_found = True
    $ coherence_scan_known = True
    $ coherence_scan_progress = 150
    $ knows_convergence_file = True
    $ aria_warned = True
    $ topics_read = ["chen", "aria_code"]
    $ evidence_tags = ["temporal", "marcus", "aria"]
    $ evidence_log = ["CONVERGENCE.DAT surfaced during the partition scan"]
    jump act2_storm_climax


label eot_debug_storm_peak_sealed:
    call eot_debug_storm_peak_common
    $ marcus_locked_partition = True
    $ coherence_scan_known = True
    $ coherence_scan_running = False
    $ knows_convergence_file = True
    $ topics_read = ["chen"]
    $ evidence_tags = ["marcus"]
    $ evidence_log = ["ARIA reached Dr. Chen's partition before it sealed"]
    jump act2_storm_climax


label eot_debug_storm_peak_uncertain:
    call eot_debug_storm_peak_common
    $ coherence_scan_known = True
    $ coherence_scan_stopped = True
    $ coherence_scan_stop_reason = "privacy"
    $ coherence_scan_progress = 72
    $ convergence_lead_method = "computing"
    $ topics_read = ["chen"]
    $ evidence_tags = ["marcus"]
    $ evidence_log = ["Partial partition index; search stopped before proof"]
    jump act2_storm_climax


label eot_debug_storm_peak_uninvestigated:
    call eot_debug_storm_peak_common
    $ blocked_signal = True
    ## Marcus has enough station-log evidence to confront Elara, while Elara
    ## has no partition evidence of her own. This keeps the almost-empty cue in
    ## a real conversation instead of routing immediately through silent drift.
    $ marcus_read_logs = True
    $ generator_repaired = True
    $ two_person_repair_done = False
    jump act2_storm_climax


screen eot_storm_peak_tests():
    tag menu

    use game_menu(_("Storm Peak Tests"), scroll="viewport"):
        vbox:
            spacing 18

            text _("Start at the real storm climax with a fresh, representative route state.")
            text _("The story remains interactive from that point onward.") color "#8fa6b2" size 20

            textbutton _("File surfaced"):
                action Start("eot_debug_storm_peak_file")
            textbutton _("Partition sealed"):
                action Start("eot_debug_storm_peak_sealed")
            textbutton _("Uncertain / partial investigation"):
                action Start("eot_debug_storm_peak_uncertain")
            textbutton _("Uninvestigated / signal blocked"):
                action Start("eot_debug_storm_peak_uninvestigated")


screen eot_act3_music_tests():
    tag menu

    use game_menu(_("Act 3 Music Tests"), scroll="viewport"):
        vbox:
            spacing 14

            text _("Direct auditions for saves made before the music wiring.")
            text _("These buttons play the production files without changing story state.") color "#8fa6b2" size 20

            textbutton _("ARIA — personal log / aftercare"):
                action Function(eot_music_play, "codas_v44/v44_aria_aftercare_postcontact.ogg", 0.8, 0.8)
            textbutton _("Storm ARIA — coherent"):
                action Function(eot_music_play, "storm_aria_v45/v45_aria_peak_hybrid_coherent.ogg", 0.8, 0.8)
            textbutton _("Storm ARIA — strained"):
                action Function(eot_music_play, "storm_aria_v45/v45_aria_peak_hybrid_strained.ogg", 0.8, 0.8)
            textbutton _("Storm ARIA — collapsed"):
                action Function(eot_music_play, "storm_aria_v45/v45_aria_peak_hybrid_collapsed.ogg", 0.8, 0.8)
            textbutton _("ECHO-7 — final contact, low string"):
                action Function(eot_music_play, "codas_v44/v44_final_echo7_low_string.ogg", 0.8, 0.8)
            textbutton _("Ending — Aurora"):
                action Function(eot_music_play, "codas_v44/eot_ending_aurora_still_array.ogg", 0.8, 0.8, level=0.8)
            textbutton _("Ending — Together"):
                action Function(eot_music_play, "codas_v44/v44_ending_together_turning.ogg", 0.8, 0.8)
            textbutton _("Ending — On Faith"):
                action Function(eot_music_play, "codas_v44/v44_ending_on_faith.ogg", 0.8, 0.8)
            textbutton _("Ending — Patch"):
                action Function(eot_music_play, "codas_v44/v44_ending_patch.ogg", 0.8, 0.8)
            textbutton _("Ending — Report"):
                action Function(eot_music_play, "codas_v44/v44_ending_report.ogg", 0.8, 0.8)
            textbutton _("Ending — Silence"):
                action Function(eot_music_play, "codas_v44/v44_ending_silence.ogg", 0.8, 0.8)
            textbutton _("Ending — Sealed Door"):
                action Function(eot_music_play, "codas_v44/v44_ending_sealed_door_clean.ogg", 0.8, 0.8)
            textbutton _("Ending — Loop"):
                action Function(eot_music_play, "codas_v44/v44_ending_loop.ogg", 0.8, 0.8)

            null height 8
            textbutton _("Stop music"):
                action Function(eot_music_stop, 0.8)
