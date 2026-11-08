# Phase 3.5 — Feature Engineering (J1 template X1–X9 applied to AT-2Liga)

Consumption rule, causality contract, and rejected-feature discipline
are inherited verbatim from `league/J1/analysis/FEATURES.md` (trailing
or expanding-with-decay windows only, strictly pre-match, ratio
features as ratios of sums, NaN → arm inactive — never filled). For
EVERY J1 template feature: ADOPTED or DROPPED, with the Austria
2. Liga number.

## §1 Template features — verdicts

### X1 — Blend observation pair (goals training input) — **DROPPED (data absent)**
No xG exists in any of the 1,266 payloads (no `expected_goals` key,
no shotmap). The goals observation is **goals-only** throughout —
the reference blend's documented fallback becomes the whole design
(the RU-1 situation). F11 records why no calibration check is
possible.

### X2 — Mover tier offset — **MEASURED, not adopted as an offset (weak, small-n)**
Unlike AT-Bundesliga (whose feeder had no build at its build time),
the parent corpus **exists here** (league_id 38, already built in
this program), so mover transitions were measured against it by
entrant class (F4): relegated-from-Bundesliga entrants (n=4)
GF −0.06 / GA −0.29; from-below/returning entrants (n=10, incl.
returning B-teams) GF −0.12 / GA +0.05. B-teams are handled
honestly in the classification: non-promotable, never in the
relegated class, entering/leaving only via the Regionalliga.
The samples (4 and 10 entrant-seasons) are too thin to estimate a
hard-coded offset, so **no offset arm is registered**; the measured
gaps instead motivate the goals candidate's pre-registered
**shrinkage arm** (the template-sanctioned response to the G-J2
post-mortem; the RU-1 construction), which needs no imported
constant.

### X3 — Set-play xG share and rate (trailing) — **DROPPED (data absent)**
No xG splits exist (F5). No G-AT2 decomposition arm.

### X4 — xG per shot (trailing) — **DROPPED (data absent)**
No shotmap, no xG (F6). No S-AT2 quality-input arm.

### X5 — Trailing target-rate means — **ADOPTED**
Naive/ensemble component and harness baseline for every count
market. Justification: F2 (SOT-for 0.746, corners-for 0.617,
shots-for 0.816, event-yellows-for 0.445). Availability: SOT /
corners / shots on stats rows only (1,254; the 12 stats-less
2023/2024 matches never enter a trailing window for those markets);
yellows on all 1,266 (events complete).

### X6 — Attacking xGOT per shot (trailing, era-guarded) — **DROPPED (data absent)**
No shotmap (F7). No S-AT2 xGOT arm.

### X7 — Opp-box touches for/against (trailing) — **DROPPED (data absent)**
`touches_opp_box` is absent from every payload (F9). No C-AT2
box-touch arm.

### X8 — Referee yellow rate (trailing) — **DROPPED (data absent)**
Referee text is empty in 1,266/1,266 payloads — coverage 0.0% in
every season including the virgin (F8). No K-AT2 referee arm; the
cards candidate is Gate Zero only.

### X9 — Reference territorial covariates (corners Gate Zero) — **PARTIALLY ADOPTED (possession only)**
Trailing possession rates are adopted (trait r = 0.817 / 0.804,
F9) as the corners Gate Zero territorial covariate — the
production pattern reduced to the one covariate this feed carries
(the RU-1 construction). The big-chance component is **DROPPED
(data absent)**: `big_chance` appears in no payload. No variant
arm is registered for corners.

## §2 Architectural components (not features) — as J1 FEATURES §2
Ratings, home advantage, Dixon-Coles rho, NB sizes are fitted
parameters, not covariates. v5's Beta-Binomial on-target ratio is a
fitted component of the S-AT2 reference architecture (its
shrinkage arm tests it; no standalone trailing on-target-rate
covariate is built — unmeasurable here and rejected on principle,
F6). League half-share constants (F3) are frozen presentation
constants, never features. Baselines belong to the harness.

## §3 REJECTED features (explicit)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (all stats) | **NOISE / NO SOURCE** — F3: goals true variance −0.0011; SOT/corners/shots halves do not exist in the feed |
| R2 | Trailing finishing (goals − xG) | **NO SOURCE** — no xG (F6) |
| R3 | Trailing conversion (goals/shot) | **REJECTED** — outcome-contaminated on principle (J1 F6); also priced off a feed whose shot definition breaks in 2024/2025 (F12) |
| R4 | Standalone trailing on-target rate | **REJECTED** — J1 measured it NOISE (r=0.06); here additionally corrupted by the F12 definition break |
| R5 | Defensive xGOT per shot | **NO SOURCE** — no shotmap (F7) |
| R6 | Lineup / absence features | **CLOSED** — F10: V10 null stands; reopening standard not met |
| R7 | Top-shooter concentration share | **NO EVIDENCE** — never reliability-tested as a trait; ineligible |
| R8 | Formation / coach features | **NO EVIDENCE** — no reliability check run; ineligible |
| R9 | Standings / h2h / teamForm snapshots | **LEAKAGE** — post-match snapshots of the target match |
| R10 | Attendance | **LEAKAGE / NOT PRE-MATCH** |
| R11 | Game-state traits | **NOT PRE-MATCH** |
| R12 | Red-card rates (target or covariate) | **REJECTED** — production cards design excludes reds as a target |
| R13 | Momentum | **NOT PRE-MATCH** |
| R14 | X2 mover offset imported from another league's magnitudes, or hard-coded from this league's n=4/n=10 gaps | **REJECTED** — F4: measured, too thin to hard-code; the shrinkage arm is the registered response |

## §4 Halves constants (frozen, presentation only — F3)

goals **0.4543** · yellow cards **0.3430** (both event-derived,
ratio of sums over all 1,266 event matches). SOT, corners and
total shots: **no constant exists** — no period splits and no
event source; those markets are FT presentation only
(`halves_share_1h: null`, the RU-1 runner precedent).

## §5 Consumption map

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-AT2 | goals-only DC (X1 fallback as the whole design) | thin-team shrinkage arm (F4 / G-J2 lesson) |
| S-AT2 | X5 + v5 architecture (§2 ratio component) | ratio-shrink arm (§2) |
| C-AT2 | X5, X9-possession-only (Gate Zero) | — (no variant registered) |
| K-AT2 | X5 (event yellows) | — (no variant registered; X8 data absent) |
| T-AT2 | X5 + shots architecture | E9 trailing-r arm (mechanism, not a feature); v2 level-layer arm |
