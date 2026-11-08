# Phase 3.5 — Feature Engineering (J1 template X1–X9 applied to US-USLChampionship)

Consumption rule, causality contract, and rejected-feature discipline are
inherited from `league/J1/analysis/FEATURES.md`: trailing or
expanding-with-decay windows only, strictly pre-match, ratio features as
ratios of sums, and NaN → arm inactive — never filled. For every J1 template
feature, this document records a USL verdict and the USL number.

The modelled pooled sample is 2,203 matches from 2021–2025. The dev period
is 2022–2024; 2021 is warm-up and 2025 is the virgin season. The 2026
inventory is reserved and never read in this build. Regular and playoff
matches remain in every window and are phase-flagged.

## §1 Template features — verdicts

### X1 — Blend observation pair (goals training input) — **ADOPTED, goals-only**
xG does not exist in this league (0 of 2,590 matches carry
`expected_goals`; no shotmap). The production blend's documented
goals-only fallback is therefore the whole G-USL fit, not an exception
path. Justification: F6 + the production blend's gate history for the
goals-only mode (J2/J3 precedent).

### X2 — Mover tier offset — **DROPPED (no mover population)**
USL has no promotion/relegation and therefore no mover population from
which an offset can be estimated. The thin-team problem is handled by
the pre-registered SHR shrinkage arm in G-USL. Churn is contraction
(MLS reserve sides leaving after 2021–22) plus expansion/returning
entries; F4 measures their first-season effects as mixed and small
(−0.50…+0.45 GD/match), so no imported or invented offset is used.

### X3 — Set-play xG share and rate (trailing) — **DROPPED (data absent)**
No xG anywhere (F6). Dropped by design; not a reliability failure.

### X4 — xG per shot (trailing) — **DROPPED (data absent)**
No shotmap and no xG anywhere (F6). Dropped by design.

### X5 — Trailing target-rate means — **ADOPTED**
The team's trailing-10 means for the candidate target and the
corresponding conceded rate are the naive/ensemble component and harness
baseline. Stats/target coverage is 100% in modelled seasons. F2
reliability is SOT-for r = .652, corners-for r = .585, yellows-for
r = .759, shots-for r = .716. Used across count markets.

### X6 — Attacking xGOT per shot (trailing, era-guarded) — **DROPPED (data absent)**
No shotmap anywhere (F6). Dropped by design.

### X7 — Opp-box touches for / against (trailing) — **ADOPTED (arm only)**
Definition as the template: trailing means of `touches_opp_box` for and
against, minimum 8 matches with the stat; otherwise the arm falls back
to Gate Zero. F8 gives box-touches-for r = .556 and against r = .495;
corner correlation is .514 with box touches versus .305 with
possession. Coverage ramps 21.4% / 33.7% / 39.0% in 2021–2023 to 100%
in 2024–2025, so early dev predictions mostly fall back to Gate Zero —
the same ramp discipline as US-MLS.

### X8 — Referee yellow rate (trailing) — **ADOPTED (arm only)**
Definition as the template: the named referee's trailing in-league
unified-yellow mean, shrunk per the K-J1 construction, no imputation,
fallback to the base arm. F7 gives r = .378 across 31 referees with
≥20 matches. Coverage is 0% in 2021 (warm-up only), 98.7% / 97.2% /
91.7% in dev 2022–2024, and 96.3% in virgin 2025. The K-USL arm obeys
the K-J1 binding conditions, including the operational condition that
the appointment must be published pre-match in the live pipeline.

### X9 — Reference territorial covariates (corners Gate Zero) — **ADOPTED**
Trailing possession and big-chance rates remain the production
`model_corners_v3` covariates so Gate Zero is the true reference
pattern. Big-chance-for reliability is r = .592 (F2). Consumed by
C-USL Gate Zero.

## §2 Architectural components — explicitly not features

Ratings, home advantage, Dixon-Coles rho, and Negative Binomial sizes are
fitted parameters, not covariates. The v5 Beta-Binomial on-target ratio is a
fitted component of the S-USL reference architecture; its RS arm tests the
prior. League half-share constants are frozen presentation constants, never
team features. League base rates and naive baselines belong to the
evaluation harness.

## §3 Rejected features (explicit)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (all stats) | **NOISE** — F3 true variances: goals −0.0042, SOT −0.0026, corners +0.0022, shots +0.0009, yellows +0.0032. Constants are frozen; team shares are not features. |
| R2 | Trailing finishing (goals − xG) | **NOT MEASURABLE** — no xG (F6). |
| R3 | Trailing conversion (goals/shot) | **REJECTED** — outcome-contaminated, and dominated by volume + the fitted ratio component; not reliability-adopted in this league. |
| R4 | Standalone trailing on-target rate | **NOT ADOPTED** — the v5 fitted Beta-Binomial ratio remains an architectural component and its RS arm tests the prior. |
| R5 | Conference features | **NO DATA** — conferences exist operationally but no conference field exists in the warehouse. |
| R6 | Lineup / absence features | **CLOSED** — no USL reliability evidence for reopening. |
| R7 | Top-shooter concentration share | **NO EVIDENCE / NO DATA** — no shotmap. |
| R8 | Formation / coach features | **NO EVIDENCE** — not reliability-tested; ineligible. |
| R9 | Standings / h2h / teamForm snapshots | **LEAKAGE** — post-match snapshots of the target match. |
| R10 | Attendance | **LEAKAGE / NOT PRE-MATCH**. |
| R11 | Game-state traits | **NOT PRE-MATCH**. |
| R12 | Red-card rates (target or covariate) | **REJECTED** — production cards design excludes reds as a target. |
| R13 | Momentum | **NOT PRE-MATCH**. |
| R14 | X2 mover offset imported from another league | **REJECTED** — USL has no relegation/mover population (F4). |

## §4 Halves constants (frozen, presentation only — F3)

Goals **0.459** · SOT **0.456** · corners **0.460** · total shots
**0.453** · yellow cards **0.369**. These are the complete-split-era
2024–2025 constants; the halves mechanism is presentation only.

## §5 Consumption map

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-USL | X1 goals-only | SHR thin-team shrinkage |
| S-USL | X5 + v5 architecture (§2 ratio component) | RS ratio prior |
| C-USL | X5 + X9 production corners covariates | X7 box-touch multiplier |
| K-USL | X5 | X8 referee covariate |
| T-USL | X5 + shots architecture | B v2 level layer; C E9 trailing-r mechanism |
