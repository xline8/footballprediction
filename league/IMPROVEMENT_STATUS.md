# Improvement Program — Status Ledger

Charter: `league/IMPROVEMENT_PROGRAM.md` (user decisions 2026-11-11
03:25 + 03:56 WIB). Launched 2026-11-11 on the user's direct order
(18:27 WIB: "jalankan program perbaikan"), after the final league
audit closed and the build/join program reached ALL-DONE
(runner 59 leagues / 119 markets).

HEARTBEAT: 2026-11-13 17:58 WIB — Watchdog RESUMED coordination
(heartbeat 16:58 was 60 min old, ≥ 45-min threshold). Merged state
verified intact: active.yaml parses to 62 leagues / 123 markets, CO
cards arm x8 line 5.5, run_daily.py compiles; no Codex process
running, no new commits since 16:58 (HEAD 1d716f69 is the 16:58
heartbeat commit). Nothing launchable this run:
all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
candidates wait for a method difference, K-MX forensic dev
certification has no defined procedure in the charter (deferred, not
launched by the watchdog), K-TR waits for the completed 2026/2027
window; P2 formal verdict still PENDING-BUILDS (0 of 10 new builds).
No QUOTA-WAIT, no PAUSED-BY-USER.

## Workstream state

| WS | Gate Zero (pre-registered, AUDIT.md §6) | GZ state | Build state |
|---|---|---|---|
| P1 forward-stability admission leg | Replay over 221 dev-passers' persisted dev artefacts: adopt iff the forward (last-dev-season) leg would have stopped ≥⅓ of the sealed calibration failures AND killed ≤10% of the 122 eventual passes | **FAILED 18:40 — P1 KILLED.** Measure A = 18/68 = 26.5% stopped (< ⅓ required); Measure B = 11/120 = 9.2% killed (≤10% ✓). Coverage 68/70 cal failures, 120/122 passes. Robust: max attainable A under every arm-selection variant = 32.9% < 33.3%. Finding: most cal failures kept last-season ranking but drifted in LEVEL — an LL-only forward leg structurally cannot catch them (that mechanism is P4's target) | DEAD — not built |
| P2 design-seal EDA | Process control: zero sealed-season rows in EDA/reliability artefacts over the program's first 10 new builds | TOOLING DELIVERED 18:35; verdict PENDING-BUILDS by construction (0 of 10 builds yet) | Filter + scanner built (`league/design_seal/`); self-test PASS on AE-ProLeague (post-filter zero sealed rows). Baseline census: **153 of 157** league dirs carry sealed-season aggregates in builder-facing `analysis/` artefacts (138 JSON + 135 MD-table); 1 MENTION (J3), 1 CLEAN (J2), 2 NO_SEAL |
| P3 variance-component ratings | Offline on 6 thin built leagues (2 scores-only, 2 one-stats-season, 2 mid): pooled dev LL improves vs shipped Gate Zero in ≥5/6, none worse by >0.002 | **FAILED 18:37 — P3 KILLED** (improvements 4/6 < 5/6; tolerance leg held, worst regression +0.001890 < 0.002). Split recorded as evidence only, NO re-scope: VC improved all 4 goals leagues (Δ −0.0042…−0.0135) and lost narrowly in both SOT leagues (+0.0019, +0.0003). Replication gate passed first (shipped GZ reproduced exactly, MX within 3e-6) | DEAD — not built |
| P4 recalibration arm | Same replay protocol as P1 (level-only refit on last dev slice): adopt iff it rescues ≥⅓ of sealed calibration failures AND breaks ≤10% of passes (kill rule "as P1") | **FAILED 18:41 — P4 KILLED on both measures.** Rescue A = 12/40 = 30.0% (< ⅓, short by one); break B = 26/84 = 31.0% (limit ≤10%). Coverage A 57.1%, B 68.9% (above floor; SOT nearly unmeasurable — template persists no per-match dev). Mechanism: last-dev-season bias is often OPPOSITE in sign to the sealed bias, so the shift pushes passers out of band. Stricter provisional form dies harder (8/38, 35/82) | DEAD — not built |
| P5 shared gate library | Library must reproduce every shipped verdict's legs from persisted artefacts bit-for-bit on 10 sampled leagues | **PASSED 18:50 — P5 ADOPTED.** 283 comparison rows: 275 reproduced, **0 mismatches**, 8 not-reproducible BY DESIGN (dev-fails have no sealed artefacts — the correct reproduction of a dev FAIL; pooled-only dev schemas reproduce at decision level). Leg decisions 60/60 agree. Criterion \|Δ\| ≤ 5e-7; observed ≤ 2.5e-14. Zero artefact inconsistencies; one sign-convention case (C-GR, prereg froze actual−predicted) translated exactly — the §5.11 class the library now eliminates | **BUILT** — `league/gate_lib/` (fail-closed sealed loader, mechanical prereg parser, derived-constant checker, one sign convention; stdlib-only, self-tests pass). All future program builds MUST consume it |
| P6 worst-fold dev reporting | No statistical Gate Zero pre-registered (information only, adoptable independently) | N/A — **ADOPTED** by coordinator 18:35 into this program's verdict format (worst dev season's legs beside pooled legs in every verdict from now on) | Tool built (`league/worst_fold/`); extracts 373/428 (87%) of persisted dev artefacts; demos on AE SOT, J1 goals, AT corners, AE cards |

## Lane 1 — unread sealed windows

- INVENTORY COMPLETE 2026-11-11 18:29 WIB:
  `league/IMPROVEMENT_LANE1_INVENTORY.md` — **210 candidates**
  (Goals 135 · Cards 49 · SOT 13 · Corners 7 · Total shots 6),
  every FAIL-at-dev candidate from audit §1; sealed window named
  from the original prereg for 119, to be pinned verbatim at fresh
  preregistration for the remaining 91.
- State: wave-1 cohort FIXED 18:56 at **13 candidates** (cohort
  report: `league/improvement_scratch/LANE1_WAVE1/cohort_report.md`).
  Cohort A (variants-moot): 10 confirmed in inventory, 9 eligible
  now — K-CO, K-FO (SHRINK), K-ID (X5), K-NO-OBOS (X8), K-PE (X8),
  K-SE (X8), K-US (X8), C-PY (X7), G-TZ (SHRINK). Cohort B
  (bug-affected): 42 screened, **3 survivors**, all §5.9 M_BAR —
  T-CA, T-HU-NBI, T-AUW (§5.6/§5.1/§5.5/§5.10 yield zero; every
  instance certified neutral or FT-unaffected by the audit).
  **Coordinator rulings:** K-AT ACCEPTED as cohort A #10 (an 11th
  variants-moot case documented in its own verdict, X8 beats both
  baselines, window unread) → wave = 13. K-MX EXCLUDED from wave 1
  (uncertified dev computation, outside the named classes; needs a
  forensic dev certification first — deferred, not rejected).
  K-TR DEFERRED (its window was spoiled by the §5.7 realised
  breach — burned in substance; eligible on the completed
  2026/2027 window in a later wave). Inventory substance flags:
  K-BR, G-NL, C-NL sit in the mechanical inventory but their
  windows are burned in substance — NOT Lane-1-eligible.
  Execution design per entry: winning/corrected arm = arm of
  record, Gate Zero demoted to baseline (its veto is the defect
  being corrected), original prereg legs otherwise identical,
  gate_lib + P2 seal + P6 worst-fold, fresh prereg committed on
  the build branch BEFORE any sealed access, one read, verdict
  final; PASS → runner join by the established join-proof pattern;
  X8 cards entries check the referee operational gate before
  shipping. Batch 1 launched 18:56: K-PE, G-TZ, T-CA, K-NO-OBOS,
  K-AT. Batches 2–3 follow as lanes free.
- WAVE 1 VERDICTS — FINAL (tally **2 CLEAN PASS / 2 PROVISIONAL PASS / 9 FAIL** of 13; cohort A 2 clean / 2 provisional / 6 fail, cohort B 0-for-3):
  - **K-NO-OBOS — FAIL** (19:00). Prereg first commit bde0aefb;
    dev reproduced exactly (X8 0.655345 vs GZ 0.669336 / base
    0.668295 / naive 0.672943; sign 4/4). Single sealed read
    (2026, n=240): X8 LL@3.5 **0.712425 — leg (i) FAIL**, last of
    four (GZ 0.696439, base 0.690062, naive 0.697490); calibration
    PASSED outright (−0.92pp, SE 3.29pp); sign 4/4. Nothing ships;
    the 2026 window is now burned for this candidate. Branch
    merged to the mainline as programme record (a5311c4f).
  - **K-AT — FAIL** (19:01). Prereg first commit 39b18fec;
    dev reproduced exactly (X8 0.6560816 vs base 0.6802749 /
    naive 0.6636086; sign 3/3). Single sealed read (2025/2026,
    n=195): leg (i) FAIL — X8 LL@4.5 0.6569 > GZ 0.6509 and best
    baseline 0.6503; leg (ii) FAIL — calibration +7.25pp (SE
    3.42pp), beyond tolerance AND the 1-SE provisional boundary.
    Cause: sealed-season level drop (over-rate 34.4% vs 42.4% dev)
    that every arm missed — era drift again, now measured on a
    Lane 1 window. Nothing ships; window burned for this
    candidate. Side finding: the original harness's virgin
    verdict writer crashes when Gate Zero isn't dev-passing
    (KeyError 'gate_zero', §5.6 class) — verdict-neutral here; all
    leg arithmetic was gate_lib's. Merged as record (a8fa4bdd).
  - **K-PE — FAIL** (19:02). Prereg first commit 4ce8a892; dev
    reproduced (X8 0.687450 vs base 0.707846 / naive 0.692826;
    sign 3/3). Single sealed read (2025, n=323): leg (i) FAIL —
    X8 LL@4.5 0.690626 beat both baselines but lost to Gate Zero
    0.680517 (leg i is vs Gate Zero under the original both-pass
    semantics); calibration −3.376pp (provisional band, moot);
    sign 3/3. Nothing ships; window burned for this candidate.
    Merged as record (611f6539).
  - **G-TZ — PROVISIONAL PASS** (19:02). Prereg first commit
    2b5b21a4; dev reproduced EXACTLY (max diff 0.0; SHRINK 1X2 LL
    0.925501 vs climatology 1.069080, RPS 0.180158 vs 0.223944,
    OU 0.689404 vs base 0.692720; sign 3/3). Single sealed read
    (2025/2026, n=239): leg (i) PASS — 1X2 LL 0.882665 ≤
    climatology 1.068084 (margin −0.185); calibration: home-win
    −0.509pp CLEAN, OU +2.669pp within 1 SE → leg PROVISIONAL;
    sign 3/3. SHRINK ships provisionally. Join prep on branch
    build/lane1-gtz (active.yaml + opt-in `team_key: name` —
    FotMob IDs are shared across TZ club renames and ID-keying
    would destroy the method; runner fit verified float-exact vs
    the virgin fit). **Join proof launched 19:03** (two full
    runner runs + byte-compare + merged-state verification
    before merge, per the established pattern). **JOINED
    2026-11-11 20:12 WIB** — proof MERGE-READY: two runs of
    13,283 predictions each, 0 errors, all 451 prediction/state
    files bit-identical (only run_log.jsonl differs, by design);
    TZ 137 upcoming / 137 predicted / 0 errors; independent
    recompute of all 137 live predictions diff 0.0 on every
    float field. Merged c979d05a; merged state verified
    (active.yaml parses: 60 leagues / 120 markets, TZ present).
    **Runner now 60 leagues / 120 markets.** K-ID join proof
    launched into the freed join slot.
  - **T-CA — FAIL (dev)** (19:04). Cohort B test of the §5.9
    M_BAR case: prereg first commit d7f3cbff, M_BAR derived via
    gate_lib = 22.8326 (copied 24.15 forbidden). Corrected arm C
    dev LL@22.5 0.687304 vs naive 0.686318 — still loses by
    0.000986 (shipped margin 0.000902; the correction moved C by
    only +0.000084, the wrong way). The copied constant did NOT
    decide the original fail; the cohort-B plausibility case is
    refuted by the corrected run itself. Sign check also 1/3.
    **Window 2025 (n=112) was never read and remains sealed.**
    Merged as record (36dde961).
  - **K-SE — FAIL (sealed leg ii)** (19:05). Prereg first commit
    6e3804f3; dev reproduced byte-identically (X8 0.677040 vs
    base 0.6884 / naive 0.6871; sign 3/3). Single sealed read
    (2025, n=240): leg (i) **PASSED** — X8 LL@3.5 0.6803 ≤ GZ
    0.6970 and ≤ naive 0.6952, the best ranking on the window;
    leg (ii) FAIL outright — calibration −4.52pp (SE 3.18pp;
    provisional boundary 4.18pp). The sealed season's card level
    ROSE (actual over-rate 0.5292 vs dev 0.4431) and every arm
    under-predicted it. Nothing ships; window burned for this
    candidate. Merged as record (ac2af5b9).
  - **K-US — FAIL (sealed leg ii)** (19:06). Prereg first commit
    bdb4d3aa; dev reproduced exactly (X8 0.670898 vs base
    0.677134 / naive 0.682714; sign 2/3). Single sealed read
    (2025, n=540): leg (i) **PASSED** — X8 LL@4.5 0.674312, best
    of four (GZ 0.676249, base 0.684326, naive 0.695332);
    leg (ii) FAIL — calibration −4.220pp (SE 2.105pp; provisional
    boundary 3.105pp). A shared level miss: Gate Zero also failed
    calibration (−4.067pp); actual over-rate 0.4204 vs predicted
    0.3782. P6 note: X8 loses its worst dev fold (2022); its
    pooled margin rests on 2023–2024. Nothing ships; window
    burned for this candidate. Merged as record (48f07243).
  - **K-CO — PROVISIONAL PASS, shipping BLOCKED** (19:08).
    Prereg first commit 6557938e; dev reproduced (X8 0.691751
    vs base 0.695579 / naive 0.707987). Single sealed read
    (2026-Apertura, n=204): leg (i) PASS — X8 LL@5.5 0.665796,
    best of four; calibration −1.574pp (SE 3.413pp) →
    PROVISIONAL; sign 5/5. The wave's first X8 pass — and its
    level held within the band where K-SE/K-US's did not.
    **Referee operational gate: 0/10** — no upcoming CO fixture
    carries a referee name in FotMob, so live it would run as
    Gate-Zero-equivalent on every fixture. Verdict banked;
    join prep committed on branch build/lane1-kco (423d37b7)
    but NOT merged. **USER DECISION 2026-11-11 19:47 WIB: HOLD
    AND RECHECK — do NOT drop it.** K-CO X8 stays in the join
    queue as **HELD-BY-REFEREE-GATE** (it passed provisionally
    on the numbers). Recheck referee presence on its upcoming
    fixtures as matchdays approach (appointments often publish
    only near kickoff — the DE-2.Bundesliga precedent); when
    ≥1 upcoming fixture carries a named referee, run the
    standard join proof and join it as PROVISIONAL.
    Prereg+verdict cherry-picked to the mainline as record
    (6753b8de, 6833c495).
  - **K-ID — CLEAN PASS** (19:12). Prereg first commit 61bbb96c;
    dev reproduced EXACTLY (abs diff 0.0; X5 blend 0.694041 vs
    base 0.695916 / naive 0.697785; sign 3/3). Single sealed read
    (2025/2026, n=306): leg (i) PASS — X5 LL@4.5 0.684568 ≤ GZ
    0.685854 ≤ base 0.692258; leg (ii) PASS CLEAN — calibration
    −0.91pp (SE 2.84pp); leg (iii) 3/3. X5 ships clean. ID is a
    NEW league to the runner (cards only); join prep on branch
    build/lane1-kid (dd63dee2: x5 adapter whitelist + exclude_
    phases opt-in, smoke-tested: history loads exactly the
    frozen harness's 1,376 rows). **Join proof queued** behind
    G-TZ and K-FO (join lane cap 2). Prereg+dev+verdict
    cherry-picked as record (e26f4441, 758a6cf8, 1f9575b7).
    **JOINED 2026-11-11 21:49 WIB** — proof MERGE-READY: two
    runs of 13,374 predictions, 0 errors, 301/301 snapshot
    files bit-identical; ID 226 upcoming / 226 predicted / 0
    errors; independent recompute diff 0.0 on all 12 float
    fields; history load 1,376 rows verified twice. Merged
    8f8b4b00 (conflicts in active.yaml/README/run_daily.py
    resolved as unions of the three Lane 1 adapter opt-in sets;
    merged state verified functionally: config parses to 62
    leagues / 122 markets via the runner's own parser, and
    _cards_history_rows under the merged code loads ID 1,376
    and FO 809 rows exactly). **Runner now 62 leagues / 122
    markets. All unblocked wave-1 joins are done.**
  - **T-HU-NBI — FAIL (dev)** (19:13). Cohort B, both corrections
    applied: prereg first commit c5dfe1ff; M_BAR derived =
    19.0425 (exactly the prereg-documented own level; copied
    24.9 forbidden) and the §5.12 naive restored to the true
    trailing-10 (0.716694, far weaker than the corrupt =B
    0.705784). Both arms of record (B 0.705654, C 0.704224)
    beat the true naive pooled and per-season but lose the
    binding leg to the base rate (0.695587) by 0.0101 / 0.0086;
    sign leg vs base also fails (1 of 3 seasons). The +5.86-shot
    distortion did NOT decide the fail — as with T-CA, the
    §5.9 plausibility case is refuted by the corrected run.
    **Window 2025/2026 (n=198) never read, remains sealed.**
    Merged as record (c5f8e977).
  - **T-AUW — FAIL (dev)** (19:10). Cohort B's last case (§5.9
    M_BAR): prereg first commit 8843187b designates arms B/C of
    record (A never touches M_BAR; its FAIL reproduces exactly —
    T-CA precedent); M_BAR derived via gate_lib = 27.6788 (copied
    24.9 forbidden). Corrected dev (n=369): B 0.698867, C 0.698633
    — both lose to naive 0.696919 AND to base rate 0.698602 (C by
    0.00003). The correction moved B only −0.000083 (right
    direction, far from enough) and C +0.000216 (wrong way);
    shipped A + baselines reproduced to ≤6e-16. Sign 1/3 both
    arms (moot). **Window 2025/2026 (n=110) never read, remains
    sealed.** Cohort B closes 0-for-3: in all three cases the
    copied constant did NOT decide the original fail. Merged as
    record (4bdd8412).
  - **C-PY — FAIL (sealed legs i+ii)** (19:11). Wave 1's last
    verdict. Prereg first commit 40ab323a; dev reproduced
    EXACTLY (X7 0.6918 vs base 0.7313 / naive 0.7180; sign 2/2).
    Single sealed read on the FROZEN cohort — 2026-Clausura,
    n=112 exactly as the original prereg froze it (snapshot held
    exactly 112 rows; no widening): leg (i) FAIL — X7 0.6973 >
    Gate Zero 0.6927 (X7 beat both baselines, but the leg is
    conjunctive); leg (ii) FAIL — calibration −7.80pp (SE
    4.70pp), beyond the 1-SE provisional boundary (Gate Zero
    itself −8.21pp); sign 2/2. Cause: the sealed tournament's
    corner level jumped (actual over-rate 0.625 vs dev 0.4905);
    every arm under-predicted. Sealed numbers cross-checked
    against the original harness's virgin() — identical to every
    digit. Window now burned for this candidate. Merged as
    record (25e32e29).
  - **K-FO — CLEAN PASS** (19:10). Prereg first commit 49dc7666;
    dev reproduced EXACTLY (abs diff 0.0; SHRINK 0.681000 vs base
    0.682420 / naive 0.693044; sign 3/4). Single sealed read
    (2026, n=135): leg (i) PASS — SHRINK LL@3.5 0.686989 ≤ GZ
    0.688355 ≤ base 0.693280; leg (ii) PASS CLEAN — calibration
    −0.634pp (SE 4.293pp); leg (iii) 3/4. SHRINK ships clean —
    the wave's first clean pass, and the second SHRINK winner
    (with G-TZ). FO is a NEW league to the runner; join prep on
    branch build/lane1-kfo (adapter + builder brought to the
    runner contract; inertness on AU cards proven; first-virgin-
    fixture replay float-exact). **Join proof launched 19:11.**
    Note: FO's 2026 season is complete — it predicts live only
    when FotMob publishes 2027 fixtures (seasons list then needs
    2027). Prereg+verdict cherry-picked as record (3a3b963f,
    5fc54fce). **JOINED 2026-11-11 20:39 WIB** — proof
    MERGE-READY: runs of 13,146 / 13,148 predictions, 0 errors
    (one transient LV feed pull error in run 2, zero output
    impact); FO/AU snapshots byte-identical between runs, all
    other diffs concretely live-feed-explained (GR new fixture,
    AR/RU reschedules, ZA name change); synthetic settlement on
    match 5136308 settled 1-then-0 with files restored
    byte-identical; AU cards inertness confirmed (133 both
    runs). Merged 885a27bb (active.yaml + README conflicts
    resolved as the union of the TZ and FO entries; merged
    state verified: 61 leagues / 121 markets, both entries
    present, run_daily.py compiles, both adapter feature sets
    intact). **Runner now 61 leagues / 121 markets.**

## Lane 2 — provisional shipping, live verdict

- CLOSED. Opens per workstream only after that workstream's method
  is frozen AND validated on Lane 1 windows (charter rule).

## Event log

- 2026-11-13 17:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  16:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 16:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO-PrimeraA cards
  arm x8 line 5.5, run_daily.py compiles. **Nothing launchable this
  run:** all wave-1 joins complete (4/4); no wave-2 cohort —
  remaining 197 candidates wait for a method difference, K-MX
  forensic dev certification has no defined procedure in the charter
  (deferred, not launched by the watchdog), K-TR waits for the
  completed 2026/2027 window; P2 formal verdict still
  PENDING-BUILDS (0 of 10 new builds). No QUOTA-WAIT, no
  PAUSED-BY-USER.
- 2026-11-13 16:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  15:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 15:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-13 15:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  14:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 14:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-13 14:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  13:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 13:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-13 13:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  12:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 12:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-13 12:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  11:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 11:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-13 11:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  10:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 10:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-13 10:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  09:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 09:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-13 09:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  08:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 08:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-11 18:29 WIB — Program launched by coordinator on user
  order. Charter + AUDIT.md §1/§2/§6 + EXPERT_METHOD_STUDY read.
  Lane 1 inventory generated from `league/audit_scratch/class_batch*.jsonl`
  (210 = audit §1's dev-gate count, reconciles exactly). Gate Zero
  workers launched for P1, P3, P4, P5 and P2+P6 tooling (5 lanes).
- 2026-11-11 18:35 WIB — P2+P6 worker completed. P2: design-seal
  filter + contamination scanner delivered and self-tested
  (`league/design_seal/`); census of the OLD program: 153/157 league
  dirs have sealed-season aggregate rows in builder-facing EDA
  artefacts — §4(b) contamination was the inherited template
  pattern, not an exception. P2 Gate Zero stays PENDING-BUILDS
  (first 10 Lane-1 builds under the seal). P6: worst-fold tool
  delivered (`league/worst_fold/`); coordinator ADOPTS P6 into the
  program verdict format effective immediately (information only,
  no gate changes). Report: `league/improvement_scratch/P2P6/report.md`.
- 2026-11-11 18:37 WIB — **P3 GATE ZERO: FAIL → P3 KILLED.**
  Variance components improved pooled dev LL in 4 of 6 sampled thin
  leagues (needed ≥5): MD-NationalDivision −0.0042, SG-PremierLeague
  −0.0062, J3 −0.0135, MX-ExpansionMX −0.0078 (all goals); LV-Virsliga
  SOT +0.0019 and SA-FirstDivision SOT +0.0003 regressed. Kill rule
  applied as written; the goals-vs-SOT split is evidence for the
  record, not a re-scope. Full report + code:
  `league/improvement_scratch/P3/` (run ≈10 s, numpy-only; worker
  implemented directly with an exact-replication gate in place of
  Codex — replication of shipped GZ was exact in 5/6, 3e-6 in MX).
- 2026-11-11 18:40 WIB — **P1 GATE ZERO: FAIL → P1 KILLED.**
  Forward (last-dev-season) leg replayed over persisted artefacts
  for all 221 dev-passers (no sealed reads). It would have stopped
  only 18/68 measurable sealed calibration failures (26.5%, needed
  ≥⅓) while killing 11/120 passes (9.2%, within the ≤10% leg).
  Sensitivity: under every arm-selection variant the stop rate caps
  at 32.9% — the kill does not hinge on judgement calls. Diagnosis
  recorded: calibration failures are predominantly LEVEL drift with
  ranking intact; a log-loss forward leg cannot see them. Full
  report + per-candidate CSV: `league/improvement_scratch/P1/`.
- 2026-11-11 18:41 WIB — **P4 GATE ZERO: FAIL → P4 KILLED.**
  Level-only refit on the last dev season, replayed over persisted
  per-match artefacts: rescues 12/40 measurable sealed calibration
  failures (30.0%, needed ≥⅓) and BREAKS 26/84 measurable passes
  (31.0%, limit ≤10%). The dev-era level is not a reliable estimate
  of the sealed-era level — era level shifts are not predictable
  from the final dev season in either direction. Both era-drift
  workstreams (P1, P4) are now dead; the era-drift problem (99
  sealed deaths, 70 on calibration) has NO adopted remedy in this
  program — what remains against it is P2's seal hygiene, P6's
  worst-fold visibility, and Lane 1's fresh windows. Report + CSV +
  replay script: `league/improvement_scratch/P4/`.
- 2026-11-11 18:50 WIB — **P5 GATE ZERO: PASS → P5 ADOPTED AND
  BUILT.** The shared gate library (`league/gate_lib/`) reproduced
  every reproducible shipped verdict leg on the 10-league sample
  (275/283 rows within \|Δ\| ≤ 5e-7, observed ≤ 2.5e-14; 60/60 leg
  decisions agree; 0 mismatches; 8 by-design non-reproductions are
  dev-fails with no sealed artefacts). No artefact inconsistencies
  found. **Gate Zero phase is now complete: P5 PASS, P6 adopted,
  P2 tooling delivered (verdict pending-builds), P1/P3/P4 killed
  by their own pre-registered rules.** Lane 1 wave-1 cohort
  analysis launched. Reports: `league/improvement_scratch/P5/`.
- 2026-11-11 18:55 WIB — Lane 1 wave-1 cohort analysis complete:
  cohort A 10/10 confirmed (9 eligible; K-TR deferred, window
  burned by the §5.7 breach), cohort B 42 screened → 3 survivors
  (all §5.9 M_BAR). Coordinator accepted K-AT as cohort A #10 and
  excluded K-MX (uncertified dev) → **wave 1 = 13 candidates**.
  Batch 1 (K-PE, G-TZ, T-CA, K-NO-OBOS, K-AT) launched 18:56.
  Report: `league/improvement_scratch/LANE1_WAVE1/`.
- 2026-11-11 19:00 WIB — Lane 1 verdict 1/13: K-NO-OBOS FAIL
  (sealed leg i; details in the wave tally above). Batch 2 opens:
  K-CO launched into the freed lane.
- 2026-11-11 19:01 WIB — Lane 1 verdict 2/13: K-AT FAIL (sealed
  legs i+ii; level drop). K-SE launched into the freed lane.
- 2026-11-11 19:02 WIB — Lane 1 verdicts 3–4/13: K-PE FAIL
  (sealed leg i vs Gate Zero); **G-TZ PROVISIONAL PASS** — the
  wave's first pass. Join proof for G-TZ launched; K-US and K-FO
  launched (build lanes: T-CA, K-CO, K-SE, K-US, K-FO).
- 2026-11-11 19:04 WIB — Lane 1 verdict 5/13: T-CA FAIL at dev
  under its corrected constant (window unread, stays sealed).
  K-ID launched into the freed lane.
- 2026-11-11 19:05 WIB — Lane 1 verdict 6/13: K-SE FAIL (sealed
  calibration; leg i passed). C-PY launched into the freed lane.
- 2026-11-11 19:06 WIB — Lane 1 verdict 7/13: K-US FAIL (sealed
  calibration; leg i passed — third consecutive X8 with the best
  sealed ranking and a failed level). T-HU-NBI launched.
- 2026-11-11 19:08 WIB — Lane 1 verdict 8/13: **K-CO PROVISIONAL
  PASS** (first X8 pass) but shipping blocked at the referee
  operational gate (0/10) — user decision flagged. T-AUW
  launched; all 13 wave-1 candidates now launched or done.
- 2026-11-11 19:10 WIB — Lane 1 verdict 9/13: **K-FO CLEAN
  PASS** (SHRINK; all legs clean). Join proof launched
  (join lane now 2/2 with G-TZ).
- 2026-11-11 19:12 WIB — Lane 1 verdict 10/13: **K-ID CLEAN
  PASS** (X5 blend; all legs clean). Join proof queued third.
- 2026-11-11 19:13 WIB — Lane 1 verdict 11/13: T-HU-NBI FAIL
  at dev under both corrections (window unread, stays sealed).
  Cohort B now 0-for-2; T-AUW is its last case.
- 2026-11-11 19:10 WIB — Lane 1 verdict 12/13: T-AUW FAIL at
  dev under corrected M_BAR 27.6788 (arms B/C lose naive and
  base; window 2025/2026 unread, stays sealed). **Cohort B
  closes 0-for-3** — the §5.9 copied-constant hypothesis is
  refuted in all three corrected re-runs. Only C-PY remains.
- 2026-11-11 19:11 WIB — Lane 1 verdict 13/13: C-PY FAIL
  (sealed legs i+ii; frozen n=112 cohort read exactly as
  preregistered). **WAVE 1 VERDICTS COMPLETE: 2 CLEAN PASS
  (K-FO, K-ID) / 2 PROVISIONAL PASS (G-TZ, K-CO) / 9 FAIL.**
  Ships pending join proofs (G-TZ, K-FO running; K-ID queued);
  K-CO held on the referee operational gate (user decision).
  Three dev-fail windows never read and stay sealed (T-CA
  2025, T-HU-NBI 2025/2026, T-AUW 2025/2026).
- 2026-11-11 19:47 WIB — **USER DECISION on K-CO: HOLD AND
  RECHECK** (not dropped). K-CO X8 stays in the join queue as
  HELD-BY-REFEREE-GATE. Recheck referee presence on upcoming
  CO fixtures as matchdays approach; when ≥1 upcoming fixture
  carries a named referee, run the standard join proof and
  join as PROVISIONAL. Join prep stays on branch
  build/lane1-kco (423d37b7), unmerged, until then.
- 2026-11-11 20:12 WIB — **G-TZ JOINED THE RUNNER** (merged
  c979d05a). Join proof MERGE-READY: 2 runs × 13,283
  predictions, 0 errors, 451/451 prediction/state files
  bit-identical; TZ 137/137 predicted, independent recompute
  diff 0.0. Merged state verified: 60 leagues / 120 markets.
  K-ID join proof launched into the freed slot.
- 2026-11-11 20:39 WIB — **K-FO JOINED THE RUNNER** (merged
  885a27bb). Join proof MERGE-READY: runs 13,146 / 13,148
  predictions, diffs all live-feed-explained, synthetic
  settlement 1-then-0, AU inertness confirmed. Merge conflicts
  in active.yaml/README resolved as union (TZ + FO entries);
  merged state verified: 61 leagues / 121 markets,
  run_daily.py compiles with both adapter feature sets.
- 2026-11-13 08:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  07:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 07:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. The production daily report
  run_daily_shadow.py is running concurrently (08:52 report — left
  alone). **Nothing launchable this run:** all wave-1 joins complete
  (4/4); no wave-2 cohort — remaining 197 candidates wait for a
  method difference, K-MX forensic dev certification has no defined
  procedure in the charter (deferred, not launched by the watchdog),
  K-TR waits for the completed 2026/2027 window; P2 formal verdict
  still PENDING-BUILDS (0 of 10 new builds). No QUOTA-WAIT, no
  PAUSED-BY-USER.
- 2026-11-13 07:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  06:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 06:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. The league runner run_daily.py is
  running concurrently (production daily run — left alone).
  **Nothing launchable this run:** all wave-1 joins complete (4/4);
  no wave-2 cohort — remaining 197 candidates wait for a method
  difference, K-MX forensic dev certification has no defined
  procedure in the charter (deferred, not launched by the watchdog),
  K-TR waits for the completed 2026/2027 window; P2 formal verdict
  still PENDING-BUILDS (0 of 10 new builds). No QUOTA-WAIT, no
  PAUSED-BY-USER.
- 2026-11-13 06:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  05:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 05:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-13 05:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  04:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 04:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-13 04:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  03:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 03:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-13 03:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  02:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 02:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-13 02:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  01:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 01:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-13 01:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  00:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 00:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-13 00:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  23:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 23:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 23:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  22:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 22:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 22:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  21:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 21:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 21:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  20:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 20:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 20:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  19:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 19:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 19:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  18:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 18:58). **Merged state verified intact:**
  active.yaml parses to 62 leagues / 123 markets, CO cards arm x8
  line 5.5, run_daily.py compiles. **Nothing launchable this run:**
  all wave-1 joins complete (4/4); no wave-2 cohort — remaining 197
  candidates wait for a method difference, K-MX forensic dev
  certification has no defined procedure in the charter (deferred,
  not launched by the watchdog), K-TR waits for the completed
  2026/2027 window; P2 formal verdict still PENDING-BUILDS (0 of 10
  new builds). No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 18:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  17:58 was 60 min old, ≥ 45-min threshold; K-CO join proof Codex
  process finished, no process running). **K-CO JOIN PROOF VERIFIED
  MERGE-READY and MERGED (c6ecf8fc)** — coordinator's independent
  checks: both runs exit 0 (13,521 / 13,520 predictions, 0 errors);
  diff file exactly 3 differing files (2 prediction CSVs +
  run_log.jsonl); 397 snapshot files per run; run-2 CO CSVs 10 rows
  each × 4 markets; branch diff vs merge-base exactly the 6 join
  files (active.yaml + run_daily.py opt-ins + README + proof docs).
  Byte-compare diffs as adjudicated in the report (AR duplicate
  removal, AR date move, ZA 'AmaZulu'→'AmaZulu FC' name flip — all
  live-feed, zero numeric impact). Merged state verified: active.yaml
  parses to 62 leagues / 123 markets, CO cards arm x8 line 5.5,
  run_daily.py compiles. **K-CO cards X8 is now LIVE in the runner
  as PROVISIONAL** (4th CO market; the 16:58 brief's "63 leagues"
  was a miscount — CO was already a runner league). All wave-1 joins
  complete (4/4). No wave-2 launch: no eligible cohort exists yet.
  P2 formal verdict still PENDING-BUILDS. No QUOTA-WAIT, no
  PAUSED-BY-USER.
- 2026-11-12 17:58 WIB — **WATCHDOG CHECK — proof running, no
  stall.** Heartbeat 16:58 was 60 min old (≥ 45-min threshold), but
  a Codex luna process is LIVE since 17:40 WIB running the K-CO
  join proof (relaunched: the 16:58 launch crashed 32 s in on a
  Rust stderr-pipe panic; the second attempt was blocked by a
  read-only filesystem error at 17:38; this third attempt created
  `~/workspace/kco-proof/`, wrote pre_manifest.txt, and its first
  full runner run is ~13 min in with no error output). No duplicate
  launch — a second proof would corrupt the running one. Next
  watchdog run should verify MERGE-READY / NOT MERGE-READY from
  the proof's report before doing anything else. No wave-2 launch:
  no eligible cohort exists yet. P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 16:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  15:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 15:58). **K-CO referee-gate
  recheck: GATE PASSED 2/10** — Deportivo Pasto vs Junior FC (12 Nov,
  match 1000014235, referee Diego Alejandro Ruíz Casas) and Llaneros
  FC vs Chicó FC (13 Nov, match 1000014232, referee Carlos Márquez);
  the other 8 upcoming Clausura Round 19 fixtures still carry no
  referee name. Script + JSON snapshot in
  `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_1658.json`). Per the user's 19:47 decision the
  hold is lifted: **standard join proof LAUNCHED via Codex luna**
  (brief `league/improvement_scratch/KCO_JOIN/brief.md`; worktree
  `~/workspace/wt-lane1-kco`, branch build/lane1-kco, prep 423d37b7;
  log `league/improvement_scratch/KCO_JOIN/codex.log` in the
  worktree) — two full runner runs + byte-compare + recompute +
  synthetic settlement; merge ONLY if MERGE-READY (runner would
  become 63 leagues / 123 markets). K-CO no longer
  HELD-BY-REFEREE-GATE; it is JOIN-PROOF-RUNNING. No wave-2 launch:
  no eligible cohort exists yet (remaining 197 candidates wait for a
  method difference; K-MX needs forensic dev certification; K-TR
  waits for the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 15:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  14:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 14:58). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_1558.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 14:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  13:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 13:58). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_1458.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 13:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  12:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 12:58). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_1358.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 12:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  11:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 11:58). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_1258.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 11:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  10:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 10:58). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_1158.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 10:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  09:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 09:58). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_1058.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 09:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  08:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 08:58). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_0958.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 08:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  07:58 was 60 min old, ≥ 45-min threshold; no Codex process running,
  no new commits since 07:58; the 08:52 daily-report
  `run_daily_shadow.py` was running concurrently — morning report,
  not improvement work). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_0858.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 07:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  06:58 was 60 min old, ≥ 45-min threshold; no Codex/run_daily
  process running, no new commits since 06:58). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_0758.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 06:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  05:58 was 60 min old, ≥ 45-min threshold; no Codex/run_daily
  process running, no new commits since 05:58). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_0658.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 05:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  04:58 was 60 min old, ≥ 45-min threshold; no Codex/run_daily
  process running, no new commits since 04:58). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_0558.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 04:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  03:58 was 60 min old, ≥ 45-min threshold; no Codex/run_daily
  process running, no new commits since 03:58). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_0458.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 03:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  02:58 was 60 min old, ≥ 45-min threshold; no Codex/run_daily
  process running, no new commits since 02:58). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_0358.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 02:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  01:58 was 60 min old, ≥ 45-min threshold; no Codex/run_daily
  process running, no new commits since 01:58). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_0258.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 01:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  00:58 was 60 min old, ≥ 45-min threshold; no Codex/run_daily
  process running, no new commits since 00:58). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_0158.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-12 00:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  23:58 was 60 min old, ≥ 45-min threshold; no Codex/run_daily
  process running, no new commits since 23:58). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-12_0058.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-11 23:58 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  23:02 was 56 min old, ≥ 45-min threshold; no Codex/run_daily
  process running, no new commits since 23:02). **K-CO referee-gate
  recheck: still 0/10** — same 10 upcoming Clausura Round 19
  fixtures (12–14 Nov) carry no referee name in FotMob (fixture
  payload nor matchDetails infoBox); recheck script + JSON snapshot
  in `league/improvement_scratch/KCO_RECHECK/`
  (`recheck_2026-11-11_2358.json`). K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-11 23:02 WIB — **WATCHDOG RESUMED coordination** (heartbeat
  21:49 was 69 min old, ≥ 45-min threshold; no Codex/run_daily
  process running, no new commits since 21:49). **K-CO referee-gate
  recheck: still 0/10** — 10 upcoming Clausura Round 19 fixtures
  (12–14 Nov) carry no referee name in FotMob (fixture payload nor
  matchDetails infoBox); recheck script + JSON snapshot in
  `league/improvement_scratch/KCO_RECHECK/`. K-CO stays
  HELD-BY-REFEREE-GATE per the user's 19:47 decision; recheck again
  as the 12–14 Nov matchdays arrive. No wave-2 launch: no eligible
  cohort exists yet (remaining 197 candidates wait for a method
  difference; K-MX needs forensic dev certification; K-TR waits for
  the completed 2026/2027 window). P2 formal verdict still
  PENDING-BUILDS. No QUOTA-WAIT, no PAUSED-BY-USER.
- 2026-11-11 21:49 WIB — **K-ID JOINED THE RUNNER** (merged
  8f8b4b00). Join proof MERGE-READY: 2 runs × 13,374
  predictions, 0 errors, 301/301 files bit-identical, ID
  226/226, recompute diff 0.0. Three-way adapter conflicts
  resolved as unions; merged state verified functionally
  (62 leagues / 122 markets; ID history 1,376 rows, FO 809
  rows under merged code). **LANE 1 WAVE 1 FULLY CLOSED** —
  verdicts 13/13, joins 3/3 unblocked; K-CO remains
  HELD-BY-REFEREE-GATE per the user's 19:47 decision.
