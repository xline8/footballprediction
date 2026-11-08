# Phase 3.5 — Feature Engineering (J1 template X1–X9 applied to NO-OBOSLigaen)

Consumption rule, causality contract, and rejected-feature discipline
are inherited verbatim from `league/J1/analysis/FEATURES.md` (trailing
or expanding-with-decay windows only, strictly pre-match, ratio
features as ratios of sums, NaN → arm inactive — never filled). For
EVERY J1 template feature: ADOPTED or DROPPED, with the OBOS number.

## §1 Template features — verdicts

### X1 — Blend observation pair (goals training input) — **ADOPTED, goals-only**
No xG exists in this feed in any season, so the production blend's
documented goals-only fallback is the whole design (the J2/J3
situation). Availability: goals, all seasons. Justification: F1/F2
(goals traits r = 0.825/0.727) + the reference pattern's gate history.

### X2 — Mover tier offset — **ADOPTED (arm only, Eliteserien scope)**
Definition as J1: for a club whose previous completed season was in
the parent tier (NO-Eliteserien, id 59), its rating prior at season
entry is shifted by a tier-step offset estimated **inside the dev
fit** from historical mover transitions completed before the target
season (J1 leakage guard). Raw inputs: tier membership by season from
the two corpora, keyed by FotMob team id. Scope limit, recorded
honestly: only Eliteserien→OBOS entrants are measurable (13
entrant-seasons, 2022–2026); entrants promoted from 2. divisjon
(2–3 per season) have no parent corpus, take the league-mean prior,
and are covered by the goals candidate's SHR shrinkage arm instead.
Justification: F4 (**SIGNAL** — pooled entrant GF 2.053 / GA 1.348
per match vs league team-goal mean 1.619).

### X3 — Set-play xG share and rate — **DROPPED (data absent)**
No expected_goals keys of any kind exist in the OBOS stats feed (F5).

### X4 — xG per shot — **DROPPED (data absent)**
No shotmap exists in any season (F5).

### X5 — Trailing target-rate means — **ADOPTED**
Naive/ensemble component and harness baseline for every count market.
Justification: F2 (SOT-for 0.858, corners-for 0.730, shots-for 0.895,
yellows-for 0.408). Availability: SOT/corners/shots where the stats
keys exist (2021 partial — the min-sample rule absorbs the gap; full
from 2022, minus 1 row in 2025 and 3 in 2026); yellows all seasons
(events).

### X6 — Attacking xGOT per shot — **DROPPED (data absent)**
No shotmap, no xGOT, in any season (F7).

### X7 — Opp-box touches for/against — **DROPPED (data absent)**
The stats feed carries no touches_opp_box key in any season.

### X8 — Referee yellow rate (trailing) — **ADOPTED (arm only)**
Definition as J1 (trailing mean of unified yellows within the league,
shrunk to the league mean; <8 prior in-league matches → shrunk league
mean; fixture without a named referee → base arm, no imputation).
Availability: no referee named in 2021 (warm-up only); 95.4% of
2022–2026 matches; 95.4% in the virgin season. Justification: F8,
split-half r = **0.715** (second seed stream 0.723) on the
event-unified target — the program's strongest referee reading.
Consumed by K-NO-OBOS's referee arm.

### X9 — Reference territorial covariates (corners Gate Zero) — **ADOPTED, possession-only**
The production corners_v3 multiplier uses possession + big chances;
big_chance does not exist in this feed. Following the RU-1Division
precedent, Gate Zero carries the **possession** covariate only, so
Gate Zero remains the production pattern reduced to the covariates
this league actually has — not a straw man. Justification:
possession trait r = **0.834** for / 0.830 against (F2 family),
production adoption evidence for the multiplier form.

## §2 Architectural components (not features) — as J1 FEATURES §2
Ratings, home advantage, Dixon-Coles rho, NB sizes are fitted
parameters, not covariates. v5's Beta-Binomial on-target ratio is a
fitted component of the SOT reference architecture (its shrinkage arm
tests it; no standalone trailing on-target-rate covariate exists —
that object is R4, and in this league it is not even measurable, F6).
League half-share constants (F3) are frozen presentation constants,
never features. Baselines belong to the harness.

## §3 REJECTED features (explicit)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (all stats) | **NOISE** — F3: true variance −0.0067 (goals), +0.0039 (cards); and no per-half stats exist at all |
| R2 | Trailing finishing (goals − xG) | **NOT MEASURABLE** — no xG (F6) |
| R3 | Trailing conversion (goals/shot) | **REJECTED** — outcome-contaminated; dominated by volume + ratings; J1 template verdict stands |
| R4 | Standalone trailing on-target rate | **REJECTED as a covariate** — consumed only through v5's fitted BB component (§2) |
| R5 | Defensive xGOT per shot | **NOT MEASURABLE** — no shotmap (F7) |
| R6 | Lineup / absence features | **CLOSED** — F10: V10 null stands; reopening standard not met |
| R7 | Top-shooter concentration share | **NO EVIDENCE** — never reliability-tested; no shotmap to test it with |
| R8 | Formation / coach features | **NO EVIDENCE** — no reliability check run; ineligible |
| R9 | Standings / h2h / teamForm snapshots | **LEAKAGE** — post-match snapshots of the target match |
| R10 | Attendance | **LEAKAGE / NOT PRE-MATCH** |
| R11 | Game-state traits | **NOT PRE-MATCH** |
| R12 | Red-card rates (target or covariate) | **REJECTED** — 81 reds + 73 YellowReds in 1,440 matches is a rare-event count; production cards design excludes reds as a target |
| R13 | Momentum | **NOT PRE-MATCH** |
| R14 | X2 mover offset imported from another league's magnitudes | **REJECTED** — the offset is estimated inside this league's dev fit from its own parent-tier transitions (F4) |

## §4 Halves constants (frozen, presentation only — F3)

goals **0.440** · yellow cards **0.306** (ratio of sums over event
times, all seasons). SOT / corners / total shots: **null** — no
period splits and no event source exist; those markets are FT-only.

## §5 Consumption map

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-NO-OBOS | X1 (goals-only) | SHR thin-team shrinkage arm (G-J2 lesson); X2 mover-offset arm (Eliteserien entrants) |
| S-NO-OBOS | X5 + v5 architecture (§2 ratio component) | ratio-shrink arm (§2) |
| C-NO-OBOS | X5, X9-possession (Gate Zero multiplier) | plain no-multiplier ablation arm |
| K-NO-OBOS | X5 | X8 referee arm |
| T-NO-OBOS | X5 + shots architecture | E9 trailing-r arm (mechanism, not a feature) |
