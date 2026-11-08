# Phase 3.5 — Feature Engineering (J1 template X1–X9 applied to NO-Eliteserien)

Consumption rule, causality contract, and rejected-feature discipline
are inherited verbatim from `league/J1/analysis/FEATURES.md` (trailing
or expanding-with-decay windows only, strictly pre-match, ratio
features as ratios of sums, NaN → arm inactive — never filled). For
EVERY J1 template feature: ADOPTED or DROPPED, with the Norway number.

## §1 Template features — verdicts

### X1 — Blend observation pair (goals training input) — **ADOPTED**
Goals + stats-feed xG, production blend weight. Availability: **all
seasons** (xG 100% from 2021 — no goals-only era, unlike J1).
Justification: F11 (goals/xG 0.98–1.05 in four of five complete
seasons, pooled 1.068; the 2022 feed reads 1.216 — a recorded caveat
on that dev season, not a correction) + F1.

### X2 — Mover tier offset — **DROPPED (data absent)**
The feeder tier (1. divisjon) has no build in this league's scope, so
no mover transition can be estimated (F4). The problem X2 solves —
promoted teams entering with no in-league history — is instead
addressed by the goals candidate's pre-registered shrinkage arm
(template-sanctioned response to the G-J2 post-mortem). No offset is
invented from another league's magnitudes.

### X3 — Set-play xG share and rate (trailing) — **ADOPTED (arm only)**
Definition as J1 (ratio of sums over trailing window, min 8 matches
with xG splits). Availability: all seasons (splits ~100%; two seasons
carry a handful of missing rows at 99.6%). Justification: F5,
split-half r = **0.577**. Consumed by G-NO's decomposition-tilt arm
only.

### X4 — xG per shot (trailing) — **ADOPTED (arm only)**
Definition as J1 (Σ sm_xg / Σ sm_shots, regulation shots, min 8).
Availability: all seasons (shotmap 100%). Justification: F6,
split-half r = **0.770** — the strongest X4 reading in the program.
Consumed by S-NO's quality-input arm.

### X5 — Trailing target-rate means — **ADOPTED**
Naive/ensemble component and harness baseline for every count market.
Justification: F2 (SOT-for 0.759, corners-for 0.832, yellows-for
0.423 on the event-unified target, shots-for 0.844). Availability: all seasons, all markets.

### X6 — Attacking xGOT per shot (trailing, era-guarded) — **DROPPED (era starts in the virgin season)**
Era guard applied as in J1 (only matches from 2025, where the field
is populated for ~99.5% of shots). Measured split-half r = **0.546**
(19 clubs) — the trait is real where it can be measured. It is
dropped anyway: the guarded era begins with season 2025, this build's
virgin window, so no dev season carries the feature and an arm could
never pass a dev gate before touching the virgin — the BR-SerieA X6
precedent exactly (F7). The feature is dropped, never faked; S-NO has
no xGOT arm. A future prereg with 2025 in its dev window may test it.

### X7 — Opp-box touches for/against (trailing) — **ADOPTED (arm only)**
Definition as J1 (trailing means, min 8 window matches with the stat,
else arm falls back to Gate Zero for that team). Availability: 100%
from 2024; partial before (40.4% / 42.9% / 38.3%) — the min-8 rule
absorbs the ramp. Justification: F9 (for r = **0.935**, against
r = **0.766**; per-match corr with corners 0.600 vs possession 0.449).
Consumed by C-NO's territorial-multiplier arm.

### X8 — Referee yellow rate (trailing) — **ADOPTED (arm only) — as amended**
Definition as J1 (trailing mean of unified yellows within the league,
shrunk to the league mean; <8 prior matches → shrunk league mean;
fixture without a named referee → base arm, no imputation).
Availability: named referee in 95.9% of matches (76.3% in the 2021
warm-up season, 100% from 2022, 100% in the virgin season).
Justification: F8, split-half r = **0.316** on the corrected
event-unified target (independent second stream: 0.348) — modest,
above the 0.3 noise-zone line, far below J1's 0.646 / AT's 0.547.
**Amendment record**: this feature was first recorded DROPPED on a
reading of r = 0.291 taken on the stats-feed yellows, before the
per-match audit showed that feed undercounts yellows in every season
(Phase 1 §3.5). On the corrected target the trait clears the bar, so
X8 is adopted as an arm, exactly as the template prescribes for a
passing trait. The amendment predates any cards fitting on the
corrected target; the discarded stats-target dev run is documented
in PREREG_K_NO. Consumed by K-NO's referee arm.

### X9 — Reference territorial covariates (corners Gate Zero) — **ADOPTED**
Trailing possession + big-chance rates, production `model_corners_v3`
covariates, carried unchanged so Gate Zero is the true production
pattern. Justification: production adoption evidence + big-chance
trait r = 0.812 measured here (F9).

## §2 Architectural components (not features) — as J1 FEATURES §2
Ratings, home advantage, Dixon-Coles rho, NB sizes are fitted
parameters, not covariates. v5's Beta-Binomial on-target ratio is a
fitted component of the S-NO reference architecture (its shrinkage arm
tests it; the standalone trailing on-target-rate covariate stays
rejected — but note the league difference recorded in F6: the
on-target-rate *trait* is reliable here at r = 0.477, unlike J1/AT,
which is precisely why the RS arm's verdict in this league is
informative either way). League half-share constants (F3) are frozen
presentation constants, never features. Baselines belong to the
harness.

## §3 REJECTED features (explicit)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (all stats) | **NOISE** — F3: true variance ≤ +0.0007 for goals/SOT/corners/shots; team goal-share r = −0.089. (Yellows' +0.0076 is a recorded watch item, not a modelling licence.) |
| R2 | Trailing finishing (goals − xG) | **REJECTED** — F6: r = 0.312, weakest of the shot family and outcome-contaminated; dominated by X4 + volume |
| R3 | Trailing conversion (goals/shot) | **REJECTED** — F6: r = 0.473 but outcome-contaminated; dominated by X4 + volume |
| R4 | Standalone trailing on-target rate | **REJECTED as a covariate** — trait reliable here (F6: r = 0.477) but consumed through v5's fitted BB ratio component (§2); no design may add it as a separate trailing covariate |
| R5 | Defensive xGOT per shot | **DROPPED with X6** — era/dev mismatch (F7); no defensive arm may be built on an untestable trait family |
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

goals 0.439 · SOT 0.456 · corners 0.473 · total shots 0.465 ·
yellow cards 0.317 (complete period-split era 2023–2025).

## §5 Consumption map

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-NO | X1 (blend) | thin-team shrinkage arm (F4/G-J2 lesson); X3 set-play tilt arm |
| S-NO | X5 + v5 architecture (§2 ratio component) | ratio-shrink arm (§2); X4 quality-input arm |
| C-NO | X5, X9 (Gate Zero multiplier) | X7 box-touch multiplier arm |
| K-NO | X5 | X8 referee arm (as amended, F8) |
| T-NO | X5 + shots architecture | E9 trailing-r arm (mechanism, not a feature) |
