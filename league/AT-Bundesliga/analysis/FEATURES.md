# Phase 3.5 — Feature Engineering (J1 template X1–X9 applied to AT-Bundesliga)

Consumption rule, causality contract, and rejected-feature discipline
are inherited verbatim from `league/J1/analysis/FEATURES.md` (trailing
or expanding-with-decay windows only, strictly pre-match, ratio
features as ratios of sums, NaN → arm inactive — never filled). For
EVERY J1 template feature: ADOPTED or DROPPED, with the Austria number.

## §1 Template features — verdicts

### X1 — Blend observation pair (goals training input) — **ADOPTED**
Goals + stats-feed xG, production blend weight. Availability: **all
seasons** (xG 100% from 2021/2022 — no goals-only era, unlike J1).
Justification: F11 (goals/xG 0.92–1.00 per season, pooled 0.975) + F1.

### X2 — Mover tier offset — **DROPPED (data absent)**
The feeder tier (2. Liga) has no build in this league's scope, so no
mover transition can be estimated (F4). The problem X2 solves —
promoted teams entering with no in-league history — is instead
addressed by the goals candidate's pre-registered shrinkage arm
(template-sanctioned response to the G-J2 post-mortem). No offset is
invented from another league's magnitudes.

### X3 — Set-play xG share and rate (trailing) — **ADOPTED (arm only)**
Definition as J1 (ratio of sums over trailing window, min 8 matches
with xG splits). Availability: all seasons (splits 100%; the single
2024/2025 gap is 2 matches). Justification: F5, split-half
r = **0.477**. Consumed by G-AT's decomposition-tilt arm only.

### X4 — xG per shot (trailing) — **ADOPTED (arm only)**
Definition as J1 (Σ sm_xg / Σ sm_shots, regulation shots, min 8).
Availability: all seasons (shotmap 100%). Justification: F6,
split-half r = **0.480**. Consumed by S-AT's quality-input arm.

### X5 — Trailing target-rate means — **ADOPTED**
Naive/ensemble component and harness baseline for every count market.
Justification: F2 (SOT-for 0.867, corners-for 0.828, yellows-for
0.497, shots-for 0.896). Availability: all seasons, all markets.

### X6 — Attacking xGOT per shot (trailing, era-guarded) — **DROPPED (reliability failed)**
Era guard applied as in J1 (only matches from 2024/2025, where the
field is populated for ~all shots). Measured split-half r = **0.273**
(13 teams) — below the noise-zone line and far below J1's 0.518.
The feature is dropped, never faked; S-AT has no xGOT arm. (F7.)

### X7 — Opp-box touches for/against (trailing) — **ADOPTED (arm only)**
Definition as J1 (trailing means, min 8 window matches with the stat,
else arm falls back to Gate Zero for that team). Availability: 100%
from 2024/2025; partial before (63.6% / ~58% / 80.5%) — the min-8
rule absorbs the ramp. Justification: F9 (for r = **0.945**, against
r = **0.813**; per-match corr with corners 0.546 vs possession 0.407).
Consumed by C-AT's territorial-multiplier arm.

### X8 — Referee yellow rate (trailing) — **ADOPTED (arm only)**
Definition as J1 (trailing mean of unified yellows within the league,
shrunk to the league mean; <8 prior matches → shrunk league mean;
fixture without a named referee → base arm, no imputation).
Availability: named referee in 81.4% of matches (44.1% in 2021/2022,
≥82% from 2022/2023, 91.8% in the virgin season). Justification: F8,
split-half r = **0.547**. Consumed by K-AT's referee arm.

### X9 — Reference territorial covariates (corners Gate Zero) — **ADOPTED**
Trailing possession + big-chance rates, production `model_corners_v3`
covariates, carried unchanged so Gate Zero is the true production
pattern. Justification: production adoption evidence + big-chance
trait r = 0.873 measured here (F9).

## §2 Architectural components (not features) — as J1 FEATURES §2
Ratings, home advantage, Dixon-Coles rho, NB sizes are fitted
parameters, not covariates. v5's Beta-Binomial on-target ratio is a
fitted component of the S-AT reference architecture (its shrinkage arm
tests it; the standalone trailing on-target-rate covariate stays
rejected — F6, r = −0.114). League half-share constants (F3) are
frozen presentation constants, never features. Baselines belong to
the harness.

## §3 REJECTED features (explicit)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (all stats) | **NOISE** — F3: true variance ≤ +0.0004 for all five; team goal-share r = −0.38 |
| R2 | Trailing finishing (goals − xG) | **NOISE** — F6: r = 0.100 |
| R3 | Trailing conversion (goals/shot) | **REJECTED** — F6: r = 0.300, weak and outcome-contaminated; dominated by X4 + volume |
| R4 | Standalone trailing on-target rate | **NOISE** — F6: r = −0.114 |
| R5 | Defensive xGOT per shot | **NOT MEASURED / DROPPED with X6** — the attacking side already failed (F7); no defensive arm may be built on a failed trait family |
| R6 | Lineup / absence features | **CLOSED** — F10: V10 null + J1 replication stand; reopening standard not met |
| R7 | Top-shooter concentration share | **NO EVIDENCE** — never reliability-tested as a trait; ineligible |
| R8 | Formation / coach features | **NO EVIDENCE** — present in payload, no reliability check run; ineligible |
| R9 | Standings / h2h / teamForm snapshots | **LEAKAGE** — post-match snapshots of the target match |
| R10 | Attendance | **LEAKAGE / NOT PRE-MATCH** |
| R11 | Game-state traits | **NOT PRE-MATCH** |
| R12 | Red-card rates (target or covariate) | **REJECTED** — production cards design excludes reds as a target |
| R13 | Momentum | **NOT PRE-MATCH** |
| R14 | X2 mover offset imported from J.League magnitudes | **REJECTED** — another league's tier gap is not this league's measurement (F4) |

## §4 Halves constants (frozen, presentation only — F3)

goals 0.448 · SOT 0.447 · corners 0.476 · total shots 0.454 ·
yellow cards 0.316 (complete period-split era 2023/2024–2025/2026).

## §5 Consumption map

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-AT | X1 (blend) | thin-team shrinkage arm (F4/G-J2 lesson); X3 set-play tilt arm |
| S-AT | X5 + v5 architecture (§2 ratio component) | ratio-shrink arm (§2); X4 quality-input arm |
| C-AT | X5, X9 (Gate Zero multiplier) | X7 box-touch multiplier arm |
| K-AT | X5 | X8 referee arm |
| T-AT | X5 + shots architecture | E9 trailing-r arm (mechanism, not a feature) |
