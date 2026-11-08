# Phase 3.5 — Feature Engineering (J1 template X1–X9 applied to US-MLS)

Consumption rule, causality contract, and rejected-feature discipline are
inherited from `league/AT-Bundesliga/analysis/FEATURES.md`: trailing or
expanding-with-decay windows only, strictly pre-match, ratio features as
ratios of sums, and NaN → arm inactive — never filled. For every J1 template
feature, this document records an MLS verdict and the MLS number.

The modelled pooled sample is 2,544 matches from 2021–2025. The dev period is
2022–2024; 2021 is warm-up and 2025 is the virgin season. The 2026 inventory
is reserved and never read in this build. Regular and playoff matches remain
in every window and are phase-flagged.

## §1 Template features — verdicts

### X1 — Blend observation pair (goals training input) — **ADOPTED**

Goals plus stats-feed xG enter the production blend pair. xG is available for
100% of modelled seasons except 99.2% coverage in 2021, so the reference
blend's documented goals-only fallback applies to the small missing set.
Justification: F11, pooled goals/xG calibration **1.039** (season values
1.049, 1.041, 1.042, 1.054, 1.011), plus the production blend's gate history.

### X2 — Mover tier offset — **DROPPED (no mover population)**

MLS has no relegation and therefore no mover population from which an offset
can be estimated. The thin-team problem is handled by the pre-registered SHR
shrinkage arm in G-US, not by importing a tier offset. Expansion clubs are
Charlotte (2022), St. Louis City (2023), and San Diego FC (2025); F4 describes
the problem as entry variance from zero history rather than a measured level
gap. Imported magnitudes are rejected as R14.

### X3 — Set-play xG share and rate (trailing) — **ADOPTED (arm only)**

Definition as the template: trailing ratio of sums for set-play xG share and
set-play xG rate, with a minimum of 8 window matches with xG present. F5 gives
split-half **r = 0.684**, the strongest MLS ratio trait and above the J1 value
of 0.62. Consumed by the G-US set-play decomposition tilt arm only.

### X4 — xG per shot (trailing) — **ADOPTED (arm only)**

Definition as the template: Σ shotmap xG / Σ regulation shots over a trailing
window, minimum 8 matches with shotmap. Shotmap coverage is 100% in every
modelled season. F6 gives split-half **r = 0.559**. Consumed by the S-US
quality-input arm.

### X5 — Trailing target-rate means — **ADOPTED**

The team's trailing-10 means for the candidate target and corresponding
conceded rate are the naive/ensemble component and harness baseline. Stats,
shotmap, and target coverage are 100% in modelled seasons. F2 reliability is
SOT-for **r = 0.655**, corners-for **r = 0.582**, yellow-for **r = 0.571**,
and shots-for **r = 0.725**. The feature is used across count markets.

### X6 — Attacking xGOT per shot (trailing, era-guarded) — **ADOPTED (arm only)**

Definition as the template, with the era guard beginning **2024-01-01** and a
minimum of 8 era-valid window matches. F7 measures **1,062 matches / 2,124
team-matches** and split-half **r = 0.355**. It clears the approximately 0.3
noise screen but is well below J1's 0.518: this is the weakest adopted trait
and the S-US dev gate decides whether it ships. It is constructed only as the
S-US era-guarded arm.

### X7 — Opp-box touches for / against (trailing) — **ADOPTED (arm only)**

Definition as the template: trailing means of `touches_opp_box` for and
against, minimum 8 matches with the stat; otherwise the arm falls back to Gate
Zero. F2 gives box-touches-for **r = 0.711** and against **r = 0.695**; corner
correlation is **.513** with box touches versus **.343** with possession.
Coverage is only approximately **39–45%** in 2021–2023 and 100% in 2024–2025.
The arm uses the J1/AT minimum-8 trailing rule with fallback to Gate Zero.

### X8 — Referee yellow rate (trailing) — **ADOPTED (arm only)**

Definition as the template: the named referee's trailing in-league unified-
yellow mean, with no imputation and fallback to the base arm. F8 gives **r =
0.634** across **32 referees with at least 20 matches**. Coverage is 0% in
2021 (warm-up only), then approximately 96–99% in dev and virgin seasons,
including **96.1%** in 2025. The K-US arm obeys the K-J1 binding conditions.

### X9 — Reference territorial covariates (corners Gate Zero) — **ADOPTED**

Trailing possession and big-chance rates remain the production `model_corners_v3`
covariates so Gate Zero is the true reference pattern. F9 gives a big-chance-
for trait reliability of **r = 0.594**. Consumed by C-US Gate Zero and the
X5/X9 production-corners base inputs.

## §2 Architectural components — explicitly not features

Ratings, home advantage, Dixon-Coles rho, and Negative Binomial sizes are
fitted parameters, not covariates. The v5 Beta-Binomial on-target ratio is a
fitted component of the S-US reference architecture; its RS arm tests the
prior, while standalone trailing on-target rate remains rejected. League
half-share constants are frozen presentation constants, never team features.
League base rates and naive baselines belong to the evaluation harness.

## §3 Rejected features (explicit)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (all stats) | **NOISE** — F3 true variances are goals **−0.0035**, SOT **+0.0012**, corners **+0.0033**, total shots **+0.0007**, yellows **+0.0040**. Constants are frozen; team shares are not features. |
| R2 | Trailing finishing (goals − xG) | **NOISE** — F6: **r = 0.238**. |
| R3 | Trailing conversion (goals/shot) | **REJECTED** — F6: **r = 0.368**, weak and outcome-contaminated; dominated by X4 plus volume. |
| R4 | Standalone trailing on-target rate | **NOT ADOPTED** — F6: **r = 0.376**. The v5 fitted Beta-Binomial ratio remains an architectural component and its RS arm tests the prior. |
| R5 | Defensive xGOT per shot | **NOT MEASURED / DROPPED with X6** — no defensive arm is built on the weakest short-era adopted trait family. |
| R6 | Lineup / absence features | **CLOSED** — no MLS reliability evidence is supplied for reopening. |
| R7 | Top-shooter concentration share | **NO EVIDENCE** — not reliability-tested; ineligible. |
| R8 | Formation / coach features | **NO EVIDENCE** — not reliability-tested; ineligible. |
| R9 | Standings / h2h / teamForm snapshots | **LEAKAGE** — post-match snapshots of the target match. |
| R10 | Attendance | **LEAKAGE / NOT PRE-MATCH**. |
| R11 | Game-state traits | **NOT PRE-MATCH**. |
| R12 | Red-card rates (target or covariate) | **REJECTED** — production cards design excludes reds as a target. |
| R13 | Momentum | **NOT PRE-MATCH**. |
| R14 | X2 mover offset imported from another league | **REJECTED** — MLS has no relegation/mover population, and another league's tier gap is not an MLS measurement. |

## §4 Halves constants (frozen, presentation only — F3)

Goals **0.445** · SOT **0.450** · corners **0.464** · total shots **0.456** ·
yellow cards **0.341**. These are the complete-split-era 2024–2025 constants;
the halves mechanism is presentation only.

## §5 Consumption map

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-US | X1 blend | SHR thin-team shrinkage; X3 set-play tilt |
| S-US | X5 + v5 architecture (§2 ratio component) | RS ratio prior; X4 xG/shot; X6 era-guarded xGOT/shot |
| C-US | X5 + X9 production corners covariates | X7 box-touch multiplier |
| K-US | X5 | X8 referee covariate |
| T-US | X5 + shots architecture | E9 trailing-r mechanism arm |
