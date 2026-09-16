################################################################################
## Echoes of Tomorrow — Game Variables
##
## All game state defaults. These are reset in label start for replay.
################################################################################

## --- One-time presentation reset (2026-08-18) ---
## Dev-era agent sessions ran this sample game in turbo and could die
## holding preferences.transitions at 0 — the shim now stash-protects its
## own mutations (vnflight c6030ee + the 789bc17 ownership fix), but
## persistents damaged BEFORE that carry plain zeros with no provenance,
## and the shim rightly refuses value-based guessing (values are not
## proof of who wrote them). The GAME may assert its own presentation
## defaults, though: Echoes is built around its dissolves, so ONCE per
## persistent, if transitions are fully off, turn them back on. A player
## who turns them off after this is never second-guessed again.
init 5 python:
    if not getattr(persistent, "_echoes_presentation_reset", False):
        persistent._echoes_presentation_reset = True
        try:
            if renpy.game.preferences.transitions == 0:
                renpy.game.preferences.transitions = 2
        except Exception:
            pass

## --- Core Story Variables ---

default trust_signal = 0            # -3 to +3: how much Elara trusts the signal
default lab_room_returns = 0        # presentation only: lab_room re-offer count, drives ambient return texture
default telescope_room_returns = 0
default comms_room_returns = 0
default generator_room_returns = 0
default habitat_room_returns = 0
default storage_room_returns = 0

## Marcus has two deliberately separate relationship axes. `marcus_relationship`
## is CLOSENESS: affection, shared history, and willingness to be vulnerable.
## It retains the established name because endings and older saves already read
## it. `marcus_trust` is operational confidence: whether Elara is transparent,
## competent, and acting in good faith. Warm scenes use closeness; partition
## access and benefit-of-doubt use trust. Major disclosures grant +2 trust;
## transparent work and shared operational decisions grant +1. Closeness uses
## the same +2/+1 rhythm for vulnerability versus ordinary companionship, but
## the axes move independently: a kind colleague is not automatically an
## honest one, and an honest disagreement need not make them less close.
default marcus_relationship = 0     # roughly -4 to +8: personal closeness with Marcus
default marcus_trust = 0            # roughly -4 to +8: confidence in Elara's conduct
default investigated_privately = False
default signal_reported = False     # Act 1: the anomalous signal was reported up the chain
default marcus_knows_first_signal = False   # Act 1 "Tell him.": Marcus knows a signal arrived
default marcus_knows_message = False        # Act 1: Marcus knows it was a message addressed to Elara by name
default marcus_knows_signal_blocked = False # Canteen: Elara explicitly told Marcus the signal returned and was blocked
default canteen_slip_seen = False           # Canteen slip beat: Elara sorted the Protocol's endings into kinds; Marcus went quiet twice
default blocked_signal = False
default report_blocked_signal = False       # Act 3 Report choice explicitly closed a live ECHO-7 channel
## 0 = normal/open, 1 = reopened before the investigation log,
## 2 = reopened after the log and needs compressed catch-up at the comms array.
default late_signal_reconnect = 0
default read_all_logs = False
default echo7_designation_known = False
default knows_cascade = False
default knows_prediction_evidence = False
default knows_convergence_file = False
default knows_origin_claim = False  # ECHO-7 claimed the origin is temporal, not spatial (act-1 signals spec Q or comms cautious_trace)

## --- ARIA coherence scan (forensic twin of the dome origin sweep) ---
## Elara can prepare a specialization-specific local lead in the lab and
## commission a targeted search for the full fallback window, or put ARIA on
## standby so she independently acts earlier without using Elara's credential.
## With neither instruction ARIA starts later: first on a known filename, then
## on a source-audit signature, and latest as a blind self-preservation trawl. The search
## accrues in the background, integrity-gated, and completion is now required
## to surface the file; a healthy but unfinished process reaches the no-file
## spine rather than manufacturing proof at midnight.
default coherence_scan_running = False
default coherence_scan_prepared = False      # Elara built a local lead/search manifest in the lab
default coherence_scan_standby = False       # ARIA may independently begin earlier, without Elara's credential
default coherence_scan_commissioned = False  # Elara explicitly queued ARIA's targeted partition search
default coherence_scan_signature = False     # Source audit found the trust-chain signature; partial narrowing without a filename
default convergence_lead_method = None        # "computing", "signals", or "physics"; weaker local evidence retained if the file is lost
default coherence_scan_stopped = False       # Elara explicitly stopped the search; prevents silent restart
default coherence_scan_stop_reason = None    # "stealth" = operational pause; "privacy" = principled refusal
default coherence_scan_stopped_at = None     # time_remaining snapshot; stealth resume requires the situation to advance
default coherence_scan_stop_knew_cascade = False
default coherence_scan_stop_knew_file = False
default coherence_scan_target = 0           # Minutes to completion, fixed at route-dependent start (clues collapse it)
default coherence_scan_progress = 0         # FLOAT: += eot_scan_credit_tick(...) — phase-integrated, with bounded integer-carry stepping; display renders int(...)
default coherence_scan_wear_debt = 0        # Fixed-point carry: active scan costs ARIA 2 integrity per 20 wall-clock minutes
default coherence_found = False             # Scan completed before the climax — she found the file
default convergence_opened = False          # Elara read and retained the file before the storm peak
default coherence_scan_suspected = False    # Computing tell: unexplained cycles, but Elara has not identified the process
default coherence_scan_known = False        # Player has identified ARIA's partition scan
default coherence_scan_known_before_completion = False  # Elara knew early enough that choosing not to stop it was possible
default coherence_scan_named = False        # ECHO-7 supplied CONVERGENCE.DAT while the blind scan was running; target narrowed once
default coherence_scan_assisted = False     # Elara spent a lab action indexing the scan; target narrowed once
default marcus_scan_assist_logged = False   # Her assisted search is visible in the station job ledger (Marcus evidence)
default marcus_scan_commission_logged = False # Her initial targeted-search commission is a separate signed job (Marcus evidence)
default marcus_scan_notice_remaining = 0    # Busy Marcus may take 15 minutes to reach the signed indexing job in the ledger
default marcus_scan_log_acknowledged = False # He has named Elara's signed indexing job to her after seeing/sealing it
default marcus_access_watch_seen = False    # One-shot: ARIA reported Marcus checking the partition access ledger
default marcus_search_stance = "unaware"   # unaware -> considering/willing -> withdrawing -> sealed
default marcus_search_reason = None
default marcus_search_since = None         # Remaining storm minutes at the last decision
default marcus_search_accepted = ()         # Facts already considered, not fresh provocations
default marcus_search_was_willing = False
default marcus_search_boundary_serial = 0  # New witnessed private-console intrusions
default aria_motive_asked = False           # Elara asked ARIA why it searched Chen's partition on its own (storm-time lab beat; ARIA-as-mirror-of-Marcus)
default coherence_stall_hint_seen = False   # One-shot: first time the lab shows the crawling/stalled rate (names the power lever)
default coherence_scan_notice = False       # Transient: completion not yet announced at the hub
default knows_aurora_option = False
default aria_warned = False
default chose_leap_of_faith = False
default ending_seen = None
default evidence_log = []           # Evidence/information Elara collects (display strings)
default evidence_tags = []          # Parallel theme tags for evidence_log (audit A4): "temporal"/"marcus"/"aria"
default archive_hash_includes_convergence_lead = False # Snapshot receipt: the hashing drive captured Elara's local lead
default convergence_lead_archived = False # At least one completed chain-of-custody archive contains that lead

## --- Specialization (class gating system) ---

default specialization = "signals"          # "signals", "physics", or "computing"

## --- Station Audit Console (two-step interaction system) ---

default audit_focus = "trust"              # "trust", "temporal", "chen", or "aria_code"

## --- ARIA core source audit: BACKGROUND WORK (2026-08-17) ---
## design/DESIGN_echoes_process_log.md §2. A machine's work backgrounds;
## Elara's attention does not. The audit used to be a 30/45-minute FOREGROUND
## sink that decided a whole run by itself (live-observed). It is now ~10
## minutes of her hands to frame the query and then ARIA's own cycles, accruing
## exactly like the coherence scan (eot_scan_credit_tick, tiered on integrity)
## and queueing behind it — she runs ONE heavy process at a time. The integrity
## price remains UP TO 15 points (the historical 40-point floor still applies);
## what changed is that it is spent a little at a time instead of all at once,
## and the banner quotes both halves before she commits.
default aria_audit_running = False          # Commissioned and not yet finished (may be QUEUED — see eot_aria_queue_blocked)
default aria_audit_progress = 0             # FLOAT: ARIA-cycle minutes banked (same credit function as the coherence scan); display renders int
default aria_audit_target = 0               # Cycle-minutes to completion, fixed at commission: 20 computing / 35 otherwise
default aria_audit_debt = 0                 # Fixed-point carry for the integrity spread (progress-units) — short ticks cannot round their share to zero
default aria_audit_charged = 0              # Integrity points the run has taken so far, capped at 15 and by the 40-point floor
default aria_audit_done = False             # The run finished and ARIA reported the headline at the hub (sets aria_warned there)
default aria_audit_report_read = False      # The findings themselves have been read at the console (re-scan available after)
default marcus_shown_source_audit = False   # Shared-screen acknowledgement, not permission for private-file access

## --- Evidence archive sealing: DRIVE HARDWARE (2026-08-17) ---
## Same spec §2. Three foreground minutes to load the drive and start the
## hash, then the drive finishes on its own and RELEASES at the next station
## check. The drive is committed at START (decremented there) and the receipt
## lands at the end — a drive in the bay is not a drive in the bag. The hash is
## NOT in ARIA's queue: it is the drive's own controller, so it accrues at
## wall-clock rate and is unaffected by her integrity. A second seal while one
## is hashing is refused at the console, honestly, because the bay is full.
default archive_hash_running = False        # A sealed copy is being hashed on the removable drive
default archive_hash_progress = 0           # Wall-clock minutes of hashing done (actual elapsed span, same clamp discipline as every continuous effect)
default archive_hash_target = 0             # Minutes the hash needs, fixed at start (7 — the seal's old 10 minus its 3-minute foreground load)

## --- Inventory / Resources ---

## Start with NOTHING (user pass 2026-08-14): every item is found, not
## stocked — cells and coolant and the array couplings at the storage rack,
## a cell and the data drives in the habitat locker, the preamp at comms.
## ARIA's storm advisory points at storage; the rest is exploration.
default power_cells = 0
default data_drives = 0
default antenna_parts = 0
## Drive breadcrumbs (2026-08-15, user design). Archiving the evidence log is
## the one console action that spends a consumable, and at zero drives the
## button is not drawn at all — so the absence of a drive is invisible and the
## habitat locker never gets opened for it. TWO surfaces, and Elara thinks both
## herself: at the console, once, when she has something worth sealing and
## nothing to seal it onto (this flag); and in the storm advisory, for a
## computing specialist only, whose incident-response past would have thought
## of it before the night started (no flag — act2_investigation is a one-shot
## by construction).
default drive_thought_seen = False          # One-shot: the lab console has named the missing drive and the habitat lockers

## --- KIT items (2026-08-14) ---
## The station's emergency stores, made spendable during the Long Night.
## Found once each (storage rack, habitat locker, comms spares cabinet) and
## spent from the room menus for 10 minutes apiece. Coolant restores ARIA
## integrity; the RF preamplifier restores array signal; a power cell loaded
## into the auxiliary bus buys MINUTES of heating-grade warmth that both the
## cold tax and the continuous cold drain read (see spend_storm_time and
## eot_cold_taxed — the two must stay in lockstep).
default coolant_cartridges = 0              # Thermal coolant for ARIA's cluster loop (+35 integrity each)
default signal_amps = 0                     # RF preamplifiers for the array (+20 signal each)
default aux_power_remaining = 0             # Minutes of auxiliary bus power left — warm regardless of power_priority
default storage_supplies_found = False      # One-shot: emergency-stores rack in storage (+1 coolant, +1 cell)
default habitat_cell_found = False          # One-shot: emergency locker in the habitat module (+1 cell)
default comms_amp_found = False             # One-shot: RF preamplifier in the comms spares cabinet (+1 amp)

## --- Station Systems ---

default signal_strength = 80               # 0-100, affected by storm and power allocation
default aria_integrity = 100               # 0-100, degrades under heavy analysis AND continuous deep-storm cold (economy pass + scan-race retune 2026-08-13: 10/hr at intensity 2, 36/hr in the blizzard; zero when power_priority "aria", halved on "heating"; trust/temporal analysis topics -6 each)
default aria_cold_notice_seen = False       # One-shot hub notice at integrity <= 35 — collapse never arrives unannounced (checked BEFORE the time-zero climax jump)
default aria_cold_debt = 0                  # Fixed-point carry for the cold drain (rate-minutes) — short actions cannot round their drain to zero
default aria_cold_drain_hub_note = 0        # Integrity points lost to the CONTINUOUS cold since the last hub attribution line (presentation only — a long spend must not read as a hidden action cost)
default aria_analysis_cost_seen = False     # One-shot: ARIA has named the integrity cost of her annotated analysis (trust/temporal topics, -6 each) — fires on the FIRST charged topic
default aria_ever_powered = False           # History: power_priority was "aria" for at least one tick — gates the On-Faith "never paid a watt" line to routes where it is literally true
default aria_drift_debt = 0                 # Fixed-point carry for ARIA-priority recovery drift (rate-minutes)
default signal_drift_debt = 0               # SIGNED fixed-point carry for signal drift (comms +, telescope −) — equal time under opposing priorities nets to zero; residue never crosses subsystems
default power_priority = "balanced"         # "balanced", "telescope", "comms", "heating", "aria"
default generator_visited = False           # First-entry cost; independent of whether Marcus is present

## --- Observatory Navigation ---

default current_location = "lab"

## --- Storm System ---

default storm_intensity = 0                # 0-3, derived from minutes before storm peak
default time_remaining = 300              # minutes before storm forces confrontation (B1: tightened budget)
default long_night_active = False          # True only while the Act 2 storm clock is narratively current
default operational_stats_active = True   # Structured Signal/ARIA/Power footer belongs to the pre-climax station problem

## --- Hub State ---

default hub_visits = 0
default hub_return_location = None            # Room submenu to restore after act2_hub processes shared station events; None opens the map
default comms_visits = 0
default echo7_cooldown_remaining = 0        # Carrier recovery after any paid audience; one full 18m rebuild regardless of the signal-limited question count
default comms_session_questions = 0         # Paid questions in the CURRENT terminal session (decides whether comms_leave starts recovery). A real default, not an underscore transient: comms_leave reads it at its first statement, and a rollback/load landing there must not NameError (the _telescope_minutes crash class)
default telescope_visited = False           # She has been up to the dome (entry cost; progress mod). The WALK, not the work
default star_map_reviewed = False           # At least one analysis was commissioned; retained for old-save compatibility and the first signed-note receipt
default star_map_complete = False           # All three current layer jobs are complete (or a legacy reviewed save was migrated)
default star_map_open_requested = False     # Repeat room-menu choice bypasses the entry offer; entry prose then leads directly to the map
default star_map_known_sources_logged = False
default star_map_anomalies_correlated = False
default star_map_origin_analyzed = False    # The carrier layer supplied a reason to run the longer positional falsification
default lab_visited = False               # First lab visit (entry-cost rule: 5 on a first or event-bearing entry, 0 on a quiet repeat)
default origin_sweep_done = False           # The bearing-287.4 integration completed (45 clean minutes accumulated)
default origin_sweep_running = False        # Integration currently accruing clean minutes on the array
default origin_sweep_progress = 0           # Clean minutes accumulated (kept across interruptions)
default origin_sweep_staged = False         # Observing plan configured (setup paid); the 5-min resume re-arms it
default origin_sweep_interruptions = 0      # Times the RUNNING integration lost the array (never a failed arm)
default origin_sweep_notice = False         # Transient: interruption not yet announced at the hub
default origin_sweep_unseen = False         # Completed on the final tick — recorded, never seen (Act-3 witness line only)
## The 75/60 reception bar on that integration lived in ONE place: ARIA, at the
## dome, on the arm that only renders once the sweep is ALREADY out of reach.
## ECHO-7 names it on the first open comms session instead, early enough to
## plan the array around (2026-08-15 live review). Its own flag, not
## comms_visits: a blocked channel or a carrier lost in the noise floor leaves
## the room long before that line.
default echo7_origin_hint_seen = False      # One-shot: ECHO-7 has named the dome's 75-point price for finding it
default habitat_visited = False             # First habitat-module visit (one-shot chair / protein-bar beats)
default habitat_marcus_seen = False         # One-shot habitat break encounter (his tea windows)
default habitat_sat_with_marcus = False     # She sat with him (rel+1; counts toward his busyness)
default storage_marcus_seen = False         # One-shot storage part-hunt encounter (antenna damage diverts him)
default storage_hunt_together = False       # Helped him search (rel+1, +1 antenna part; counts toward busyness)
default storage_scavenged = False           # One-shot manifest-discrepancy sweep (no item grant)

## --- Room waits (2026-08-14) ---
## Waiting is something you do in a ROOM, at the work: a person standing in a
## corridor for an hour reads as a person with something to hide, while a
## person waiting for results at their own bench reads as a person working.
## Each working room takes a 30-minute stay. If Marcus's schedule
## (eot_marcus_location) puts him in that room across the stay, it becomes a
## short scene with one choice — see eot_wait_encounter for the arrival rule.
## One encounter per room; one warm option each (rel+1) that also counts as a
## night that gave him something to do (wait_shared_moment feeds _together_any
## in act2_hub, alongside the habitat sit and the storage hunt).
default wait_seen_telescope = False         # First solo stay in the dome (repeat stays get one line)
default wait_seen_lab = False               # First solo stay at the lab bench
default wait_seen_generator = False         # First solo stay with the load board
default wait_seen_storage = False           # First solo stay among the shelves
default wait_seen_habitat = False           # First solo sit in the canteen (2026-08-18, fifth wait room)
default wait_seen_comms = False             # First solo watch on the band (2026-08-18, sixth wait room — comms room menu)
default wait_met_lab = False                # One-shot: he came back to the lab while she waited
default wait_met_generator = False          # One-shot: she stayed through his failover prep
default wait_met_storage = False            # One-shot: she stayed while he worked the crates
default wait_shared_moment = False          # A warm wait choice — busyness input, like habitat_sat_with_marcus
default wait_texture_phases_seen = []       # Storm phases whose one-shot wait texture has played (shared across all four rooms; reassign, never .append)
default marcus_overheard_signal = False     # He heard the array-room session from the corridor (phase 2, unreported routes)
default marcus_tuned_array = False          # She asked him to tune the array for "an observation run" (+15 signal)
default marcus_read_logs = False            # Idle Marcus read the station logs at the lab side console (nothing done together)
default marcus_read_logs_checked = False    # One-shot guard for the log-reading evaluation at t <= 60
default lab_lookout_seen = False            # One-shot ECHO-7 lookout whisper at the lab (open channel, his break windows)
default generator_repaired = False
default antenna_reroute_active = False      # Generator-room repair is a temporary bypass; the rope-line repair clears it
default antenna_reroute_debt = 0            # Fixed-point carry for continuing signal strain on the temporary bypass
default generator_marcus_seen = False       # First-visit flag for Marcus generator scene (B5)
default antenna_damaged = False
default marcus_knows_access = False
default marcus_first_accused = False        # Set when Marcus is first named as the engineer (bible beat 11 groundwork)
default reroute_noticed = False              # P-6: Marcus clocked the solo ARIA reroute in the corridor beat (weight for the climax)
default predicted_overload = False           # Physics foresight: read the superlinear load curve at the generator (climax + future survival-beat payoff)
default marcus_locked_partition = False      # Second failure vector: Marcus (>= evidence threshold) noticed ARIA's scan and sealed his partition — kills the scan (no-file consequence pending the alternate act 3)

## --- Recovery emergency window (ECHOES_ACT3_NOFILE.md §1, phase 2) ---
## When Marcus SEALS his partition (marcus_locked_partition) and she knows a
## file is there (knows_convergence_file), Elara gets ONE narrow, costly, and
## FALLIBLE chance to force it open anyway — from the lab console. It is not a
## spec freebie: the specialization only changes the METHOD, ODDS and COST.
## Success re-surfaces the file (routes back to the file-in-hand act 3, but a
## hotter confrontation — Marcus knows he was breached after sealing). Failure
## leaves her on the no-file spine, poorer for the time spent.
default file_recovered = False               # She forced the sealed partition open and read CONVERGENCE.DAT
default recovery_offered = False             # One-shot: ARIA announced the emergency window at the hub
default recovery_attempted = False           # One-shot: she made the attempt (success or failure)
default recovery_left_trace = False          # A failed NOISY attempt (computing breach / desperate brute-force) logged on his seal — Marcus knows someone tried
default echo7_contact_spent = False          # The signals recovery burned the line to the future (success OR fail) — Act 3 treats ECHO-7 as gone even on an open signal
default echo7_identity_known = False          # The "I AM YOU" reveal happened (act3_start live line only) — knows ECHO-7 IS her, distinct from knowing the Aurora name

## --- Marcus in the Long Night (bible 6d) ---
default marcus_lab_present = False          # Transient: Marcus at the lab side console this visit (phase 1)
default _audit_marcus_was_present = False   # Shared room/terminal observation; restored with the scene on load
default marcus_lab_talked = False           # Talked to Marcus at the lab console (seeds the '45 disclosure breadcrumb)
default marcus_caught_live = False          # He watched Elara investigate him at the lab console (early marcus_knows_access)
default marcus_catch_topic = None           # R5-5: WHAT he caught her reading ("chen"/"aria_code"/"liaison") — confrontation reads it
default marcus_corridor_seen = False        # One-shot phase-2 comms-corridor encounter
default marcus_eva_came_to_elara = False    # Transient: Marcus sought her out from the hub rather than waiting at Comms
default marcus_eva_deferred_at = None       # Time remaining when Elara postponed the rope-line decision; a later Comms return can reopen it
default marcus_eva_waiting_for_parts = False # The EVA was blocked by an unchecked storage rack; finding its couplings reopens the offer
default marcus_told_signal = False          # Elara told Marcus about the signal — the rope line, or the "Go find Marcus" walk (forks confrontation temperature)
default marcus_told_signal_on_rope = False  # Provenance: the disclosure happened during the exterior repair
default marcus_told_accusation = False     # Elara explicitly shared ECHO-7's allegation, not merely its existence

## --- "Go find Marcus" (2026-08-14) ---
## From storm phase 2 his schedule parks him at Comms and then the Lab. Those
## ordinary room destinations keep him reachable during the hours in which
## ARIA's partition search comes to light.
default marcus_told_search = False          # Voluntary disclosure; the search stance graph owns his response
default marcus_checked_in = False           # One-shot: she asked him how he was holding up instead of about the storm (rel+1)
default elara_owned_search = False          # No-file confrontation: she explicitly disclosed her part in ARIA's search
## Repeat-visit gates (2026-08-15 live-run bug: the full arrival prose played
## verbatim on every walk, at ten minutes and the cold each time). ONE FLAG PER
## LOCATION — the Comms cable run and Lab side console are different beats and
## each earns its full arrival once; every later conversation there is one
## short line and a 5-minute spend.
default marcus_found_corridor = False       # She has already found him at the comms-corridor cable run
default marcus_found_terminal = False       # She has already found him at the lab side console
default two_person_repair_done = False      # The whiteout antenna setpiece happened
default marcus_disclosure_hint = False      # Marcus obliquely mentioned the '45 disclosure (gates the liaison thread)
default stay_whisper_seen = False           # One-shot ECHO-7 "IT SOUNDS LIKE AFTER" whisper (label echo_whisper). Re-homed from the removed corridor stay in round 4: THREE doors, one flag — a telescope stay (any spec), comms-room arrival (any spec), or any other room's stay for a signals specialist
default echo7_asked_ever = []               # R5-4: questions asked across ALL comms visits (kills re-ask farming; reassign, never .append)

## --- Act 3 interlude (bible 16b) ---
default source_stance = None                # "empathetic" / "independent" / "verify" — what ECHO-7's identity changes for Elara
## Marcus's share of the truth (2026-08-15, user-approved). The interlude
## already establishes what ECHO-7's identity changes; nothing let the player decide whether
## Marcus learns that there was a source, and whether he also learns WHO was on
## the other end of the winter. Deliberately LIGHT: the two knowledge levels
## color the endings but re-route NOTHING — no ending, gate, or economy. Set
## only in act3_interlude, which has exactly one call site on the spine where
## `$ echo7_identity_known = True` has already run, so the question can never be
## asked about a reveal that did not happen.
default marcus_knows_source = False         # Marcus is told that Elara had a source, without necessarily learning its identity
default marcus_knows_sender = False         # Marcus is told the sender is future Elara (identity, not just "a source")

## --- Loop NG+ echo (audit D5) ---
default persistent.eot_loop_seen = False    # The Loop ending was reached at least once on this install
default storm_lights_event_seen = False
default storm_frost_event_seen = False
default antenna_damage_notice = False       # Transient: damage flipped in spend_storm_time, not yet announced at the hub
default telescope_damage_notice_seen = False
default antenna_damage_signal = 0           # Signal value AT damage time — the announcement quotes this, not the live value (a repair can land between tick and announcement; F3 ariafirst)
default aria_recovered_from_collapse = False # ARIA hit <=20 in the night; act3_start rebuilt her to the 20% floor (SHOWN) and act-3 scenes carry low-coherence texture + the cold-restart offhand, graded better with distance from the storm (F4 scanwear + user design)

## --- Stealth scan assists (F4 user design 2026-08-19, split + spec-tuned
## 2026-08-19 round 2) ---
## TWO separate un-alerting lab actions, BOTH gated on aria_motive_asked
## (the "Investigate ARIA's unsanctioned scan" beat — we know she does
## something AND what) in addition to the scan actually running.
##
## 1) BOOST ("Quietly lend the search idle cycles"): target trims 10/use,
##    15-minute recharge, only offered with Marcus out of the room. The
##    price of quiet is the thermal ledger: past the free allowance the
##    next use starts a 30-minute delayed trace, one more makes it
##    immediate. Free allowance is 1 — except specialization "computing",
##    whose throttle work doesn't warm the pipes until the FOURTH use
##    (3 free, 4th delayed, 5th immediate).
## 2) DAMP ("Re-phase the search to spare her core"): scan WEAR halved for
##    ~40 minutes — specialization "physics" instead zeroes it for a full
##    hour (decoherence is her literal field). Re-usable once the window
##    expires. It leaves NO ledger shape at all; the only way it is ever
##    known is Marcus standing in the same room when she does it
##    (scan_damp_seen_by_marcus, +1 evidence) — the choice stays on offer
##    with him present, labelled honestly.
default scan_boost_count = 0                # Quiet cycle-lends this night
default scan_boost_last_at = None           # time_remaining at last use (recharge check)
default scan_boost_trace_delay = 0          # Minutes until the delayed trace lands (first past-allowance use)
default scan_boost_traced = False           # Marcus-readable thermal-ledger shape (evidence point)
default scan_damp_count = 0                 # Re-phasings this night (texture only)
default scan_damp_until = None              # Wear reduction active while time_remaining > this
default scan_damp_zero = False              # Physics: wear zeroed inside the window (else halved)
default scan_damp_seen_by_marcus = False    # He was in the lab when she did it (evidence point)
default storm_frost_notice = False          # Transient: frost effects applied in spend_storm_time, not yet announced
default storm_frost_hit_antenna = False     # The frost tick's ice-loading branch fired (announcement wording)
default cold_tax_seen = False               # B4: set when the cold-time tax first applies (spend_storm_time)
default cold_tax_line_seen = False          # B4: guards the one-time cold-tax narration in act2_hub

## --- Evidence archiving (B3: data drives get a use) ---
default evidence_archived = 0               # count of evidence-log snapshots written to data drives

## --- Research Terminal ---

default topics_read = []
default topic_first_read = False
default terminal_mode = False

## --- Power Routing ---

default previous_power_priority = "balanced"
default pending_power_priority = "balanced"

## --- Shared-scene return target (2026-08-18) ---
## marcus_room_visit is shared by the find-Marcus flows (exit to the hub),
## the late-lab room-menu talk arm (exit back to lab_room), and the Comms
## doorway selector (exit back to comms_entry). A real default rather than a
## transient lets load/rollback preserve the intended return.
default marcus_visit_return = None

## --- Star Map ---

default selected_region = None

## --- Equipment ---

default selected_item = None


## --- Evidence tagging helper (audit A4) ---
## evidence_log keeps human-readable strings (the mod's evidence screen reads it);
## evidence_tags is a parallel theme index gated on by confrontation/reveal dialogue.
## Reassign (never .append) so Ren'Py rollback tracks the change.

init python:
    def _eot_tag(tag):
        if tag and tag not in store.evidence_tags:
            store.evidence_tags = store.evidence_tags + [tag]

    def eot_sweep_conditions_ok():
        # The origin integration runs on the array: it needs a functioning
        # antenna (undamaged, or rerouted through the generator) and workable
        # reception. The blizzard raises the bar — at storm 3 the array must
        # be in genuinely good shape (signal >= 75) to hear anything at all.
        s = renpy.store
        array_ok = (not getattr(s, "antenna_damaged", False)) or getattr(s, "generator_repaired", False)
        threshold = 75 if getattr(s, "storm_intensity", 0) >= 3 else 60
        return array_ok and getattr(s, "signal_strength", 0) >= threshold

    def eot_sweep_credit(t_start, t_end):
        # Clean-minute credit for the integration running from clock t_start
        # down to t_end (t_start > t_end), split across storm-phase rate
        # boundaries (Sol review #2): full speed above t=150, half through
        # the storm phase (150 >= t > 60), a third in the blizzard (t <= 60).
        # Returns a FLOAT: repeated int truncation at the storm-3 third-rate
        # melted small ticks to zero (live run finding). Display sites render
        # int(origin_sweep_progress); thresholds compare >= 45 unaffected.
        credit = 0.0
        for hi, lo, div in ((99999, 150, 1), (150, 60, 2), (60, 0, 3)):
            seg = min(t_start, hi) - max(t_end, lo)
            if seg > 0:
                credit += float(seg) / div
        return credit

    def eot_cold_taxed(minutes, aux_minutes=None):
        # The cold tax, as ONE shared arithmetic (Sol economy review 2, #1):
        # spend_storm_time inflates every action's minutes by storm/heating
        # state, so any check of the form "is there enough night left for an
        # N-minute task" must compare against the TAXED cost, not the nominal
        # one. Mirrors the inflation block in spend_storm_time exactly.
        # KIT items (2026-08-14): auxiliary bus power runs the station
        # heating-grade warm whatever the power priority says, so a task the
        # reserve can cover for its WHOLE nominal length is taxed at the
        # heating grade. Same comparison as the inline block (aux minutes vs
        # the NOMINAL spend) — keep the two in lockstep.
        s = renpy.store
        si = getattr(s, "storm_intensity", 0)
        pp = getattr(s, "power_priority", "balanced")
        if aux_minutes is None:
            aux_minutes = getattr(s, "aux_power_remaining", 0)
        warm = (pp == "heating" or aux_minutes >= int(minutes))
        if si >= 3:
            return int(int(minutes) * (1.15 if warm else 1.40))
        if si >= 2 and not warm:
            return int(int(minutes) * 1.25)
        return int(minutes)

    def eot_deadline_allows_minutes(minutes, already_taxed=False):
        """Allow a task when at least half of it fits before storm peak."""
        s = renpy.store
        if not getattr(s, "long_night_active", False):
            return True
        cost = int(minutes) if already_taxed else eot_cold_taxed(minutes)
        remaining = max(0, int(getattr(s, "time_remaining", 0)))
        return remaining * 2 >= max(0, cost)

    def eot_deadline_allows_caption(caption):
        """Apply the deadline rule to an explicitly priced menu caption."""
        import re

        text = str(caption or "").lower()
        match = re.search(
            r"\(([^()]*(?:minute|hour)[^()]*)\)\s*$", text)
        if not match:
            return True
        price = match.group(1)

        numeric = re.search(r"(\d+)\s*(?:minutes?|min)\b", price)
        if numeric:
            # Dynamic numeric captions already quote eot_cold_taxed().
            return eot_deadline_allows_minutes(
                int(numeric.group(1)), already_taxed=True)

        word_costs = (
            ("thirty-five minutes", 35),
            ("half an hour", 30),
            ("half hour", 30),
            ("quarter hour", 15),
            ("an hour", 60),
            ("one hour", 60),
            ("thirty minutes", 30),
            ("twenty minutes", 20),
            ("fifteen minutes", 15),
            ("ten minutes", 10),
            ("five minutes", 5),
            ("few minutes", 5),
        )
        for phrase, minutes in word_costs:
            if phrase in price:
                return eot_deadline_allows_minutes(minutes)
        return True

    def eot_power_projection(pp, work_minutes=15):
        # Rows for the allocation console's projection panel (2026-08-18,
        # user idea: the two-step select should SHOW the change before
        # Confirm commits it). Reads the same accounts spend_storm_time's
        # drift/drain blocks and eot_cold_taxed write — LOCKSTEP: change a
        # rate there, change it here. Each row: (delta text, direction) with
        # direction 1 recover / 0 hold / -1 decay, colored by the screen.
        s = renpy.store
        t = getattr(s, "time_remaining", 300)
        aux_minutes = max(0, int(getattr(s, "aux_power_remaining", 0)))
        # Signal drift: +-3/hr, comms up, telescope down, others none.
        if pp == "comms":
            sig = ("+3/h", 1)
        elif pp == "telescope":
            sig = ("-3/h", -1)
        else:
            sig = ("steady", 0)
        # ARIA: +3/hr recovery on her priority (cold drain zeroed); the
        # continuous cold drain otherwise, by the night's bands (10/hr
        # inside t 150-60, 36/hr in the blizzard tail), halved by heating
        # or the aux reserve.
        cold_rate = 36 if t <= 60 else (10 if t <= 150 else 0)
        if pp == "aria":
            aria = ("+3/h", 1)
        elif cold_rate:
            _drain_horizon = min(60, max(1, int(t)))
            if pp == "heating" or aux_minutes >= _drain_horizon:
                aria = ("-{}/h cold".format(cold_rate // 2), -1)
            elif aux_minutes > 0:
                aria = ("{}m half, then -{}/h".format(
                    aux_minutes, cold_rate), -1)
            else:
                aria = ("-{}/h cold".format(cold_rate), -1)
        else:
            aria = ("steady", 0)
        # The work tax: eot_cold_taxed's grade, qualitatively.
        si = getattr(s, "storm_intensity", 0)
        if si >= 2:
            if pp == "heating" or aux_minutes >= int(work_minutes):
                warm = ("runs warm", 1)
            elif aux_minutes > 0:
                warm = ("warm {}/{}m".format(
                    aux_minutes, int(work_minutes)), -1)
            else:
                warm = ("cold-taxed", -1)
        else:
            warm = ("mild night", 0)
        return sig, aria, warm

    def eot_coherence_rate():
        # Rate multiplier for ARIA's coherence scan, scaled by her integrity:
        # frost and thermal stress throttle the core clusters, and below 20
        # integrity the scan stalls entirely. Routing power to her
        # (power_priority "aria") recovers integrity in spend_storm_time's
        # drift block and so speeds the search — the lever, no new mechanic.
        # Scan-race retune (2026-08-13): tiers squeezed so sustained
        # mid-range degradation actually slows the search — the old table
        # held 0.8 across the whole 75-45 band, which let a neglected scan
        # finish anyway.
        return eot_rate_at(getattr(renpy.store, "aria_integrity", 100))

    def eot_rate_at(integ):
        # The rate-tier table, addressable at ANY integrity value — the
        # credit integrator must rate a segment at the segment's own
        # integrity, never at the live store's end-of-tick value (Sol
        # economy review 5 fallout: the flat-segment branch was quietly
        # reading the store).
        if integ > 75:
            return 1.0
        if integ > 60:
            return 0.8
        if integ > 45:
            return 0.6
        if integ > 20:
            return 0.3
        return 0.0

    def eot_coherence_credit(integ_start, integ_end, minutes):
        # Scan credit integrated across integrity-TIER crossings (Sol economy
        # review 3, #1): rating a whole tick at its end-of-tick tier made
        # progress depend on menu cadence — one long blizzard action earned
        # nothing for the minutes ARIA was still functional. Model: integrity
        # moves linearly from integ_start to integ_end over `minutes`; credit
        # each tier segment its time share. Same discipline as the origin
        # sweep's phase splitting. Returns a FLOAT.
        if minutes <= 0:
            return 0.0
        hi = max(integ_start, integ_end)
        lo = min(integ_start, integ_end)
        if hi == lo:
            return float(minutes) * eot_rate_at(hi)
        credit = 0.0
        # Tier segments (lo_bound, hi_bound] with their rates.
        for seg_lo, seg_hi, rate in ((75, 1000, 1.0), (60, 75, 0.8),
                                     (45, 60, 0.6), (20, 45, 0.3),
                                     (-1000, 20, 0.0)):
            overlap = min(hi, seg_hi) - max(lo, seg_lo)
            if overlap > 0:
                credit += float(minutes) * (float(overlap) / (hi - lo)) * rate
        return credit

    def _eot_integrity_segments(integ_start, integ_end,
                                t_start, t_end, frost_fired):
        # The measured environmental integrity path, divided at storm-rate
        # boundaries and then into stable one-minute pieces. The minute grid is
        # anchored to the station clock, so one long action and adjacent short
        # actions traverse the same pieces. Both the coherence scan and the
        # commissioned audit consume this path; only the audit layers its own
        # progressive cost over it.
        span = t_start - t_end
        if span <= 0:
            return []
        s = renpy.store
        pp = getattr(s, "power_priority", "balanced")
        drift = 3.0 if pp == "aria" else 0.0
        segs = []
        for hi, lo, cold in ((10 ** 6, 150, 0.0), (150, 60, 10.0), (60, -10 ** 6, 36.0)):
            a = min(t_start, hi)
            b = max(t_end, lo)
            if a > b:
                if pp == "aria":
                    cold = 0.0
                elif pp == "heating":
                    cold = cold / 2.0
                segs.append((a, a - b, (drift - cold) / 60.0))
        cont_total = (integ_end - integ_start) + (10 if frost_fired else 0)
        expected = sum(m * sl for _, m, sl in segs)
        result = []
        cur = float(integ_start)
        stepped = not frost_fired
        for upper, minutes, slope in segs:
            if not stepped and upper <= 150:
                cur -= 10
                stepped = True
            if expected != 0:
                delta = cont_total * (minutes * slope) / expected
            else:
                delta = cont_total * (float(minutes) / span)
            left = float(minutes)
            phase_left = float(minutes)
            while left > 0.000001:
                step = min(1.0, left)
                step_delta = delta * (step / phase_left)
                result.append((step, cur, cur + step_delta))
                cur += step_delta
                left -= step
                delta -= step_delta
                phase_left -= step
        return result

    def eot_scan_credit_tick(integ_start, integ_end, t_start, t_end, frost_fired):
        # Tick-level scan credit (Sol economy reviews 4-5, #1): continuous
        # integrity movement is PIECEWISE-linear inside a tick — the cold
        # drain switches on at t=150 and jumps 10/hr -> 36/hr at t=60 — so
        # the credit walks the shared environmental segments. The discrete
        # frost step (-10) lands at its t=150 moment.
        credit = 0.0
        for minutes, seg_start, seg_end in _eot_integrity_segments(
                integ_start, integ_end, t_start, t_end, frost_fired):
            credit += eot_coherence_credit(seg_start, seg_end, minutes)
        return credit

    def eot_audit_credit_tick(integ_start, integ_external_end,
                              t_start, t_end, frost_fired,
                              target, progress, debt, charged,
                              cold_debt_start, cold_debt_end):
        # The audit both USES integrity and spends it. Calculating its work
        # first and subtracting the cost afterward lets one long action run at
        # the pre-charge tier, while several short actions see the lower tier.
        # Couple the two here: solve the tick's credit against the fractional
        # cost produced by that same credit. `debt` is fixed-point cost already
        # earned but not yet large enough to display as a whole integrity point.
        target = max(1.0, float(target))
        prior_fraction = float(debt) / target
        cost = prior_fraction
        max_cost = max(0.0, 15.0 - float(charged))
        gain = 0.0
        # The cold drain also pays whole points with a fractional carry. Use
        # its virtual endpoints for work-rate accounting; otherwise an action
        # boundary temporarily hides that fraction and can change whether the
        # audit completes. Its carry remains a separate ledger and is not
        # folded into the audit's displayed integrity charge.
        path_start = max(
            0.0, float(integ_start) - float(cold_debt_start) / 60.0)
        path_end = max(
            0.0, float(integ_external_end) - float(cold_debt_end) / 60.0)

        for minutes, env_start, env_end in _eot_integrity_segments(
                path_start, path_end,
                t_start, t_end, frost_fired):
            remaining_work = max(
                0.0, target - (float(progress) + gain))
            if remaining_work <= 0.000000001:
                break

            effective_start = env_start - cost
            base_end = env_end - cost
            segment_gain = min(
                remaining_work,
                eot_coherence_credit(
                    effective_start, base_end, minutes))

            # Solve this minute's work and cost together. Headroom is read
            # while the minute is happening, not from the final tick endpoint:
            # cold arriving later cannot forgive work already paid for.
            segment_cost = 0.0
            for _unused in range(32):
                wanted = segment_gain * 15.0 / target
                remaining = max(0.0, max_cost - cost)
                headroom = max(
                    0.0, max(effective_start, base_end) - 40.0)
                next_cost = min(wanted, remaining, headroom)
                next_gain = min(
                    remaining_work,
                    eot_coherence_credit(
                        effective_start,
                        base_end - next_cost,
                        minutes))
                if (abs(next_gain - segment_gain) < 0.000001
                        and abs(next_cost - segment_cost) < 0.000001):
                    segment_gain = next_gain
                    segment_cost = next_cost
                    break
                segment_gain = next_gain
                segment_cost = next_cost

            gain += segment_gain
            cost += segment_cost

        # Iteration around an exact fixed-point boundary may leave a value such
        # as 5.999999999999998. Treat that as the whole point it represents;
        # otherwise splitting the same interval can lose one charged point.
        points = int(cost + 0.000000001)
        next_debt = max(0.0, (cost - points) * target)
        return gain, next_debt, points

    ## --- The STATION PROCESSES readout (design/DESIGN_echoes_process_log.md
    ## §1, 2026-08-17) -----------------------------------------------------
    ## Live grounding: the origin sweep already accrued in the background and
    ## was praised for it — and was ALSO once reported as "never delivered",
    ## because nothing on the station ever showed it running. Visibility is
    ## what turns a background process from a mystery into a plan.
    ##
    ## This is a READOUT. It starts nothing, finishes nothing and announces
    ## nothing: completions still land where they always did (hub-tick
    ## notices, the dome report, the act-3 witnesses). Everything here is
    ## derived, every tick, from the accrual variables the tick itself writes.

    def _eot_ceil_minutes(value):
        # Minutes remaining always round UP: a process with 0.2 minutes left
        # has a minute of work left, not none, and "~0m" on something still
        # running is the one number this panel must never print.
        whole = int(value)
        if value > whole:
            whole += 1
        return max(1, whole)

    def eot_aria_rate_label(integ):
        # ARIA's work rate, in one word, for the panel's right-hand side.
        # LOCKSTEP with eot_rate_at (above): same four boundaries, same
        # meanings — pinned in tests/test_sweep_boundaries.py. The lab
        # console's own scan-status row keeps its lowercase sentence diction;
        # this is the terminal-strip register.
        if integ > 75:
            return "NOMINAL"
        if integ > 60:
            return "THROTTLED"
        if integ > 45:
            return "STRAINING"
        if integ > 20:
            return "CRAWLING"
        return "STALLED"

    def eot_sweep_rate_divisor():
        # The origin sweep's clean-minute cost per wall-clock minute, by storm
        # phase. LOCKSTEP with eot_sweep_credit's rate table (full / half /
        # third at storm 0-1 / 2 / 3).
        si = getattr(renpy.store, "storm_intensity", 0)
        if si >= 3:
            return 3
        if si >= 2:
            return 2
        return 1

    def eot_aria_queue_blocked():
        # ONE HEAVY PROCESS AT A TIME (spec §2, the difficulty knob).
        #
        # THE RULE, and the decision behind it: ARIA's coherence scan is her
        # own house and her own fear — she started it without being asked and
        # she does not yield it. A COMMISSIONED audit therefore queues behind
        # it, whenever it was commissioned; if the scan starts while the audit
        # is mid-run, the audit stops there and keeps its progress. One
        # predicate, no claim bookkeeping, and the fiction is exactly what the
        # panel says: QUEUED BEHIND PARTITION SCAN. The banner names it before
        # she pays, so a queued commission is a choice and not a trap.
        #
        # WHAT IS NOT IN THE QUEUE: the origin sweep (the ARRAY's work, on the
        # dome's own hardware) and the archive hash (the DRIVE's controller).
        # The spec lists "sweep support" among ARIA's heavy work; the sweep as
        # implemented never spends her cycles — eot_sweep_credit reads the
        # array and the storm and nothing else — so putting it in the queue
        # would have invented a coupling the arithmetic does not have.
        #
        # A sealed or completed scan releases the queue immediately, so no
        # audit can be starved by a search that is no longer running.
        s = renpy.store
        if (getattr(s, "coherence_found", False)
                or getattr(s, "file_recovered", False)):
            return False
        return bool(getattr(s, "coherence_scan_running", False))

    def eot_station_processes():
        # One entry per process the station is running for her, as
        # (label, status, state) triples. `state` is the panel's colour key:
        # "live" (accruing), "hold" (running or armed but earning nothing,
        # and the status says why), "done" (finished, report not yet seen),
        # "idle" (the empty-list line).
        #
        # HONESTY RULES (the point of the panel):
        #  - every percentage divides the REAL accrual variable by the REAL
        #    target: origin_sweep_progress/45, coherence_scan_progress/
        #    coherence_scan_target, aria_audit_progress/aria_audit_target,
        #    archive_hash_progress/archive_hash_target. Nothing is synthesised.
        #  - ETAs are CONDITIONAL and say so. The sweep's rate tiers on the
        #    storm and dies on reception ("AT CURRENT SIGNAL"); ARIA's work
        #    tiers on her integrity ("AT CURRENT RATE").
        #  - a process that is not earning names WHY, in the diction its own
        #    notice already uses.
        #  - visibility mirrors knowledge: the coherence scan is invisible
        #    until coherence_scan_known. A computing specialist can suspect an
        #    unnamed workload first; the panel must not identify it for her.
        s = renpy.store
        rows = []

        sweep_prog = float(getattr(s, "origin_sweep_progress", 0))
        sweep_done = getattr(s, "origin_sweep_done", False)
        sweep_pct = int(min(100.0, 100.0 * sweep_prog / 45.0))
        if sweep_prog >= 45 and not sweep_done:
            # Complete, and the hub has not announced it yet — the one final
            # line, which drops off the moment the report is delivered.
            rows.append(("ORIGIN SWEEP — BEARING 287.4",
                         "COMPLETE — REPORT AT THE NEXT STATION CHECK", "done"))
        elif getattr(s, "origin_sweep_running", False):
            if not eot_sweep_conditions_ok():
                # It is armed and the array cannot hear: the next tick will
                # suspend it and it is earning nothing right now.
                rows.append(("ORIGIN SWEEP — BEARING 287.4",
                             "{}% // HOLDING — RECEPTION BELOW THRESHOLD".format(sweep_pct),
                             "hold"))
            else:
                eta = _eot_ceil_minutes((45.0 - sweep_prog) * eot_sweep_rate_divisor())
                rows.append(("ORIGIN SWEEP — BEARING 287.4",
                             "{}% // ~{}m AT CURRENT STORM INTENSITY".format(sweep_pct, eta),
                             "live"))
        elif (sweep_prog > 0 or getattr(s, "origin_sweep_staged", False)) and not sweep_done:
            rows.append(("ORIGIN SWEEP — BEARING 287.4",
                         "{}% // SUSPENDED — RESUME FROM THE DOME".format(sweep_pct),
                         "hold"))

        if (getattr(s, "coherence_scan_commissioned", False)
                and not getattr(s, "coherence_scan_running", False)
                and not getattr(s, "coherence_scan_stopped", False)
                and not getattr(s, "coherence_found", False)
                and not getattr(s, "file_recovered", False)
                and not getattr(s, "marcus_locked_partition", False)):
            rows.append(("ARIA PARTITION SCAN",
                         "QUEUED — TARGETED SEARCH BEGINS UNDER FALLBACK AUTHORITY",
                         "hold"))
        elif (getattr(s, "coherence_scan_known", False)
                and not getattr(s, "coherence_found", False)
                and not getattr(s, "file_recovered", False)):
            target = max(1, int(getattr(s, "coherence_scan_target", 0) or 0))
            prog = float(getattr(s, "coherence_scan_progress", 0))
            pct = int(min(100.0, 100.0 * prog / target))
            integ = int(getattr(s, "aria_integrity", 100))
            if getattr(s, "coherence_scan_running", False):
                if prog >= target:
                    rows.append(("ARIA PARTITION SCAN",
                                 "COMPLETE — REPORT AT THE NEXT STATION CHECK", "done"))
                elif eot_rate_at(integ) <= 0:
                    rows.append(("ARIA PARTITION SCAN",
                                 "{}% // HOLDING — CORE CLUSTERS STARVED (CORE {}%)".format(pct, integ),
                                 "hold"))
                else:
                    eta = _eot_ceil_minutes((target - prog) / eot_rate_at(integ))
                    rows.append(("ARIA PARTITION SCAN",
                                 "{}% // ~{}m AT CURRENT RATE — {} (CORE {}%)".format(
                                     pct, eta, eot_aria_rate_label(integ), integ),
                                 "live"))
            elif getattr(s, "marcus_locked_partition", False):
                rows.append(("ARIA PARTITION SCAN",
                             "{}% // HALTED — PARTITION SEALED".format(pct), "hold"))

        if getattr(s, "aria_audit_running", False):
            target = max(1, int(getattr(s, "aria_audit_target", 0) or 0))
            prog = float(getattr(s, "aria_audit_progress", 0))
            pct = int(min(100.0, 100.0 * prog / target))
            integ = int(getattr(s, "aria_integrity", 100))
            if prog >= target:
                rows.append(("ARIA CORE SOURCE AUDIT",
                             "COMPLETE — REPORT AT THE NEXT STATION CHECK", "done"))
            elif eot_aria_queue_blocked():
                # The scheduling game, said out loud: she is not working on
                # this, and the panel does not pretend she is.
                rows.append(("ARIA CORE SOURCE AUDIT",
                             "{}% // QUEUED BEHIND PARTITION SCAN".format(pct), "hold"))
            elif eot_rate_at(integ) <= 0:
                rows.append(("ARIA CORE SOURCE AUDIT",
                             "{}% // HOLDING — CORE CLUSTERS STARVED (CORE {}%)".format(pct, integ),
                             "hold"))
            else:
                eta = _eot_ceil_minutes((target - prog) / eot_rate_at(integ))
                rows.append(("ARIA CORE SOURCE AUDIT",
                             "{}% // ~{}m AT CURRENT RATE — {} (CORE {}%)".format(
                                 pct, eta, eot_aria_rate_label(integ), integ),
                             "live"))
        elif (getattr(s, "aria_audit_done", False)
                and not getattr(s, "aria_audit_report_read", False)):
            # The hub has already announced the headline; the FINDINGS are a
            # document, and documents are read where they live.
            rows.append(("ARIA CORE SOURCE AUDIT",
                         "COMPLETE — REPORT AT THE LAB CONSOLE", "done"))

        if getattr(s, "archive_hash_running", False):
            target = max(1, int(getattr(s, "archive_hash_target", 0) or 0))
            prog = float(getattr(s, "archive_hash_progress", 0))
            pct = int(min(100.0, 100.0 * prog / target))
            if prog >= target:
                rows.append(("ARCHIVE HASH — EVIDENCE LOG",
                             "COMPLETE — DRIVE RELEASE AT THE NEXT STATION CHECK", "done"))
            else:
                # Drive hardware: one wall-clock minute per minute, whatever
                # ARIA's clusters are doing. No conditional clause, because
                # there is no condition to state.
                rows.append(("ARCHIVE HASH — EVIDENCE LOG",
                             "{}% // ~{}m ON THE DRIVE".format(
                                 pct, _eot_ceil_minutes(target - prog)),
                             "live"))

        aux = int(getattr(s, "aux_power_remaining", 0))
        if aux > 0:
            rows.append(("AUX RESERVE", "{}m WARM REMAINING".format(aux), "live"))

        if not rows:
            rows.append(("NO BACKGROUND PROCESSES", "", "idle"))
        return rows

    def eot_process_line(label, status, width=78, pad=2):
        # The terminal leader: label, dots to the measure, status. Rendered in
        # JetBrains Mono, so the dots line up as they do on a real console.
        if not status:
            return label
        fill = width - len(label) - len(status) - (2 * pad)
        if fill < pad:
            fill = pad
        return "{}{}{}{}".format(label, " " * pad, "." * fill, " " * pad) + status

    def eot_marcus_evidence_points():
        # How many signs Marcus has that Elara is investigating HIM. Each is a
        # concealment failure the player accrued during the Long Night. Gates
        # whether he notices ARIA's scan and seals his partition (second
        # failure vector). marcus_knows_access is excluded — it is set at the
        # confrontation, after any hub lock could fire.
        s = renpy.store
        pts = 0
        for flag in ("marcus_caught_live", "marcus_overheard_signal",
                      "canteen_slip_seen", "marcus_read_logs"):
            if getattr(s, flag, False):
                pts += 1
        # The solo reroute: she fixed the antenna through ARIA instead of
        # asking him — she chose the machine over him, a trace he can read
        # regardless of whether the corridor beat fired (reroute_noticed is
        # schedule-dependent and unreliable). This is the evidence point the
        # BLOCKED path needs: with the signal closed, the canteen probe and
        # ECHO-7-overhear points are both unavailable, so without this the
        # sealed-door/alone ending (the payoff of blocking) was unreachable.
        if (getattr(s, "generator_repaired", False)
                and not getattr(s, "two_person_repair_done", False)):
            pts += 1
        # F4 stealth boost: repeated quiet cycle-lending leaves a readable
        # shape in the thermal ledger (delayed on the first past-allowance
        # use, immediate one later; a systems engineer's allowance is 3, not
        # 1) — unsigned help within the allowance is deniable.
        if getattr(s, "scan_boost_traced", False):
            pts += 1
        # The damp leaves NO ledger shape at all — its only failure mode is
        # Marcus physically in the lab watching her re-phase the search.
        if getattr(s, "scan_damp_seen_by_marcus", False):
            pts += 1
        # Codex #4: the array-tuning favor is only suspicious on the route
        # where he knew about the signal and it never went up the chain —
        # matching the climax's own gating. An innocent favor is not evidence.
        if (getattr(s, "marcus_tuned_array", False)
                and getattr(s, "marcus_knows_first_signal", False)
                and not getattr(s, "signal_reported", False)):
            pts += 1
        # Helping ARIA index his partition is faster because Elara signs the
        # job with her own fallback credential. It is not a hidden bonus: the
        # same trace that narrows the search gives Marcus one concrete reason
        # to inspect his access ledger.
        if getattr(s, "marcus_scan_assist_logged", False):
            pts += 1
        if getattr(s, "marcus_scan_commission_logged", False):
            pts += 1
        return pts

    def eot_marcus_warm():
        # THE WARM BOUNDARY, in one place (2026-08-15). Relationship weights
        # were rescaled so that DISCLOSURES — telling Marcus about the signal:
        # the act-1 "Tell him.", the rope-line confession, the "Go find
        # Marcus" signal tell — are worth +2, while COURTESIES (the habitat
        # sit, the storage hunt, the room-wait warm options, the check-in, the
        # confrontation's decent answers) stay worth +1. Warm therefore means
        # ONE REAL VULNERABLE MOMENT PLUS ONE KINDNESS, or three kindnesses:
        # marcus_relationship >= 3. This is emotional warmth only; operational
        # benefit of the doubt belongs to eot_marcus_trusts().
        return getattr(renpy.store, "marcus_relationship", 0) >= 3

    def eot_marcus_trusts():
        # Operational benefit of the doubt. A substantive disclosure (+2) is
        # enough on its own; two smaller pieces of transparent/shared work are
        # the other route. Courtesy without candour does not move this axis.
        return getattr(renpy.store, "marcus_trust", 0) >= 2

    def eot_marcus_lock_threshold():
        # Trust buys one additional piece of evidence before he locks her out.
        # Closeness colors what the breach costs emotionally; it no longer
        # substitutes for confidence in her conduct.
        if eot_marcus_trusts():
            return 3
        return 2

    def eot_marcus_search_breaches():
        # Only observed intrusions, not general suspicion or ordinary teamwork.
        s = renpy.store
        breaches = [name for name in (
            "scan_boost_traced", "scan_damp_seen_by_marcus",
        ) if getattr(s, name, False)]
        serial = getattr(s, "marcus_search_boundary_serial", 0)
        if serial:
            breaches.append("private_access_{}".format(serial))
        return tuple(breaches)

    def eot_marcus_consider_search(volunteered=False, trusted=False):
        s = renpy.store
        if getattr(s, "marcus_locked_partition", False):
            s.marcus_search_stance = "sealed"
            return
        previous = getattr(s, "marcus_search_stance", "unaware")
        if previous != "unaware" and not volunteered:
            return
        # An explicit conversation can repair hesitation, but cold candour
        # does not repeatedly restart the clock or undo a decision to seal.
        willing = volunteered and (trusted or eot_marcus_warm())
        if previous == "withdrawing" and not willing:
            return
        s.marcus_search_stance = "willing" if willing else "considering"
        s.marcus_search_reason = "disclosure" if volunteered else "discovery"
        s.marcus_search_since = getattr(s, "time_remaining", 0)
        s.marcus_search_accepted = eot_marcus_search_breaches()
        if willing:
            s.marcus_search_was_willing = True

    def eot_marcus_review_search():
        s = renpy.store
        stance = getattr(s, "marcus_search_stance", "unaware")
        if getattr(s, "marcus_locked_partition", False):
            s.marcus_search_stance = "sealed"
            return False
        if stance in ("unaware", "sealed"):
            return False
        now = getattr(s, "time_remaining", 0)
        since = getattr(s, "marcus_search_since", None)
        if since is None:
            s.marcus_search_since = now
            since = now
        accepted = getattr(s, "marcus_search_accepted", ())
        fresh = [name for name in eot_marcus_search_breaches() if name not in accepted]
        if fresh and stance != "withdrawing":
            s.marcus_search_stance = "withdrawing"
            s.marcus_search_reason = fresh[0]
            s.marcus_search_since = now
            return False
        # Free menu visits do not advance his decision. A busy engineer gets
        # to the ledger when his existing signed-job notice delay expires.
        if since - now < 10 or getattr(s, "marcus_scan_notice_remaining", 0) > 0:
            return False
        if stance == "considering":
            if eot_marcus_warm() or eot_marcus_trusts():
                s.marcus_search_stance = "willing"
                s.marcus_search_was_willing = True
            else:
                s.marcus_search_stance = "withdrawing"
                s.marcus_search_reason = "not_ready"
            s.marcus_search_since = now
        elif stance == "withdrawing":
            s.marcus_search_stance = "sealed"
            return True
        return False

    def eot_marcus_search_explanation():
        reason = getattr(renpy.store, "marcus_search_reason", None)
        if reason and reason.startswith("private_access_"):
            return "Then I saw you in my private work. I wanted a conversation, not to watch you go around me."
        return {
            "scan_boost_traced": "Then the thermal ledger showed the extra cycles somebody had tried to keep out of the job log. I stopped believing I knew the extent of it.",
            "scan_damp_seen_by_marcus": "Then I watched you change the search at the console without a word to me. I was standing right there, Elara.",
            "not_ready": "I looked at the job and couldn't leave it open. I wasn't ready to put all of that in someone else's hands.",
        }.get(reason, "I closed it because I wanted to decide what I told you myself.")

    def eot_coherence_target():
        # Minutes for ARIA's coherence scan to surface CONVERGENCE.DAT, fixed
        # when she starts the scan herself. Base is a blind sweep of the local
        # partitions; clues already gathered collapse it.
        s = renpy.store
        # Scan-race retune (2026-08-13): the scan must genuinely RACE the
        # night, or the passive collapse vector can never fire — the old
        # blind target (90 from t<=270) completed before the cold drain even
        # began. Blind trawl ~2.75h at full rate; a named search ~1.5h. A
        # a supported ARIA can still finish; an unattended one may consume
        # its own remaining integrity before the blind sweep lands.
        # The blind scan occupies nearly the whole long night. It used to take
        # 165 clean-equivalent minutes, which made ARIA's unauthorized search
        # resolve before the player had much chance to interleave with it.
        # The extra hour makes naming, research, and the signed human index
        # meaningful accelerators rather than optional victory laps.
        base = 225
        if getattr(s, "knows_convergence_file", False):
            base = 150  # ECHO-7 named the file — a search, not a trawl
        elif getattr(s, "coherence_scan_signature", False):
            base = 195  # source audit found the lock pattern, but not its name
        topics = getattr(s, "topics_read", []) or []
        for t in ("chen", "aria_code", "liaison"):
            if t in topics:
                base -= 15  # each partition topic narrows the field
        if getattr(s, "specialization", "signals") == "computing":
            base = int(base * 0.75)  # she can point the scan herself
        return max(base, 30)

    def eot_coherence_start_threshold():
        # Commissioning earns the full fallback window. Standby is not
        # authorization: ARIA waits another half-hour, then acts on her own.
        # Without either instruction she waits for progressively weaker grounds.
        s = renpy.store
        if getattr(s, "coherence_scan_commissioned", False):
            return 240
        if getattr(s, "coherence_scan_standby", False):
            return 210
        if getattr(s, "knows_convergence_file", False):
            return 180
        if getattr(s, "coherence_scan_signature", False):
            return 165
        return 150

    def eot_marcus_location(at_time=None):
        # Deterministic: clock + station state (bible 6d). No randomness — the
        # lab-catch mechanics stay fair — but the same events the player sees
        # rewrite his day: antenna damage pulls him to storage; otherwise his
        # lab shift has two short habitat breaks (the risky-topic windows).
        s = renpy.store
        t = (getattr(s, "time_remaining", 300)
             if at_time is None else at_time)
        if t > 240: return "generator"
        if t > 150:
            # A caller may ask where Marcus will be after a walk that crosses
            # t=200 before spend_storm_time has applied the deterministic
            # antenna fault. Forecast the guaranteed fault as well as the
            # already-committed state, or Lab can narrate him at the console
            # while the post-walk HUD correctly places him in Storage.
            _forecast_crosses_damage = (
                at_time is not None
                and getattr(s, "time_remaining", 300) > 200
                and t <= 200)
            if ((getattr(s, "antenna_damaged", False)
                    or _forecast_crosses_damage)
                    and not getattr(s, "generator_repaired", False)
                    and t <= 200):
                return "storage"
            if 210 < t <= 225 or 165 < t <= 180:
                return "habitat"
            return "lab"
        # Once the coupling is physically replaced, there is no reason for him
        # to spend the rest of the phase beside the airlock and cable run. A
        # temporary generator bypass keeps him at Comms because the outside
        # fault is still his next job; the permanent rope repair sends him back
        # to the lab.
        if t > 60:
            if getattr(s, "two_person_repair_done", False):
                return "lab"
            return "comms"
        return "lab"

    def eot_wait_encounter(before, after, room):
        # Does a stay in `room` (10/20/30 min) put Elara in it with Marcus? Pure
        # function of his schedule at both ends of the wait — deterministic,
        # like everything else about his day.
        #
        # The LAB is arrival-only: finding him already at the side console is
        # the catch room's scene, and the catch room's "find something else to
        # do until he leaves" already spends half an hour walking away from
        # him. The lab beat is the opposite — she stayed, and the door opened.
        #
        # The other two rooms count EITHER end of the wait, because the
        # schedule will not always let him arrive. Nobody can arrive at the
        # generator at all — the clock only runs down and his night starts
        # there — so the generator beat is "she stayed while he worked", and a
        # wait that carries the clock past 240 watches him pack up for the lab.
        # Storage takes both readings: entered around t 230-201 the antenna
        # fails mid-tick and brings him down to the crates (a real arrival);
        # entered inside the diversion he is already at the far end.
        if after != room:
            if room == "lab":
                return False
            return before == room
        if room == "lab":
            return before != room
        return True

