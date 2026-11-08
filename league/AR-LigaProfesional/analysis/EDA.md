# Phase 3 — EDA: Argentina Liga Profesional (2021 – 2026 - Clausura)

Computations: `eda.py` (digest in `eda_summary.json` +
`inventory_summary.json`); newcomer pooled gaps, the cards
stats-vs-events audit and the event-based yellows halves share were
computed by the coordinator through independent paths (see
Verification note). Sample: 2,419 group-phase matches (blocks of
325 / 378 / 378 / 378 / 240 / 240 / 240 / 240). Standard (same as
J1): a trait is a signal candidate only if it reproduces on
disjoint halves of the same teams' matches (split-half, career-
pooled per team ≥24 matches, 60 random splits averaged; ratio
traits as **ratios of sums**) or survives a variance decomposition
against its sampling-noise floor (per-match floor
`mean(p(1−p)/n_i)`).

## Levels (group phase)

| Quantity (per match) | Pooled | Block range | J1 (ref) | NL (ref) |
|---|---|---|---|---|
| Goals | **2.13** (SD≈1.47) | 1.93 – 2.45 | 2.55 | 3.12 |
| Home goals / away goals | 1.22 / 0.91 | — | 1.38 / 1.18 | 1.72 / 1.40 |
| Home win / draw / away win % | ≈43 / ≈31 / ≈26 | — | 41.3 / 26.8 / 31.9 | 43.5 / 24.4 / 32.1 |
| BTTS % / Over 2.5 % | 43.4 / 36.1 | — | 50.4 / 47.0 | 57.4 / 60.0 |
| Total shots | 24.41 | 23.2 – 26.8 | 24.8 | 27.4 |
| SOT | 7.87 | 7.5 – 8.5 | 8.08 | 9.81 |
| Corners | 9.23 | 8.5 – 9.8 | 9.47 | 10.24 |
| Yellow cards (event target) | 4.89 | 4.43 – 5.31 | 2.34 | 2.94 |
| Red cards | 0.27 | 0.21 – 0.34 | 0.11 | 0.15 |
| Team xG (match total, 2023+ only) | ≈2.2 | 2.14 – 2.26 | 2.52 | 2.97 |

Dispersion (variance/mean of the match total): goals 1.04
(Poisson-like), SOT 1.15, corners 1.14, yellows (event target)
≈0.95, total shots 1.35. The count markets sit in the same mild-
overdispersion regime as production (shots the most dispersed).

Context: this is a **low-scoring, high-cards league** — the
mirror image of the Eredivisie. Goals (2.13) run far below the
top-5 spine (2.84), J1 (2.55) and NL (3.12); draws are frequent
(≈31%); yellows (4.89, event definition) are the highest in the
program so far (top-5 reference 4.04, NL 2.94, J1 2.34). Any
ported level prior from Europe or Japan is wrong here by
construction — the empirical core of 1-league-1-model. The virgin
block (2026 - Clausura) ran **hot** against the dev period on
every attacking count (goals 2.30 vs dev 2.11; shots 26.75 vs
24.15; SOT 8.52 vs 7.79; corners 9.44 vs 9.20) — design-level
context, recorded here because EDA inspects all blocks; the
virgin stays virgin for fitting, arm selection and gate setting.

## Findings

**F1 — Levels drift by block, with a structural break at the
2025 format change.** Goals: 2.45, 2.19, 2.06, 2.03, 2.00, 1.93,
2.05, 2.30 across the eight blocks — a long decline through the
single-tournament era, a floor in the first split year, then a
hot virgin block. Shots drift the same way (24.7 → 23.2 → 26.8).
Home edge +0.31 goals pooled. Verdict: **SIGNAL** (descriptive).
Per-league levels with time-decayed fitting, as in production.

**F2 — Core team traits are reliable.** Career split-half r:
shots-for **0.747** / shots-against 0.808, SOT-for **0.763** /
0.632, xG-for 0.666 / 0.659 (2023+ era matches), goals-for 0.670 /
0.498, corners-for 0.622 / 0.634, yellows-for 0.564 /
yellows-against **0.740**, big-chance-for 0.641, possession-for
0.940. Below NL's exceptional values (0.85–0.94) but at or above
J1's — a ratings architecture has real signal in every market.
Verdict: **SIGNAL** — the feasibility base for all five
candidates.

**F3 — Half shares are noise here too; frozen constants it is.**
Measured on splits-present matches (goals/SOT/corners/shots) and
on event timing (yellows): true variance of the per-match 1H
share (observed minus per-match binomial floor): goals
**−0.0039**, SOT **+0.0012**, corners **+0.0003**, total shots
**+0.0003**, yellows **+0.0047**. Team-level split-half r of the
1H share: goals 0.13, SOT −0.10, corners −0.36, shots −0.15,
yellows −0.04 — **no team has a half tendency**. Verdict:
**NOISE** for modelling; frozen league constants are the only
halves mechanism. **Frozen constants (ratio of sums)**: goals
**0.444** (splits-era matches, n = 1,402; event-HT cross-check
over all 2,419 matches: 0.447), SOT **0.459**, corners **0.480**,
total shots **0.462**, yellows **0.373** (event timing, all
blocks, n = 2,389 matches with yellows > 0; splits-era-only
cross-check 0.379).

**F4 — Newcomers arrive modestly down (promedios era).** Teams
present in block S but absent in S−1 (exactly 2 at each year
boundary; none within a year): pooled over the five transitions
with movers (10 team-blocks, 226 team-matches): GF gap **−0.12**
goals/match vs the block's team mean, GA gap **+0.18**.
Per-transition GF gaps: +0.25, −0.20, −0.09, −0.35, −0.43 — the
2022 pair (Barracas Central, Tigre) arrived strong, every later
pair arrived down; GA gaps: +0.19, +0.10, −0.04, +0.49, +0.41.
Verdict: **SIGNAL (weak-moderate)** — a preregistered newcomer-
offset arm for the goals candidate uses exactly the pooled
magnitudes (−0.12 / +0.18), per the template's G-J2-lesson
allowance. The arm is gated; Gate Zero is the fallback.

**F5 — Set-play xG share is a real but modest team identity.**
Split-half r = **0.353** (ratio of sums; 2023+ era, the only era
with xG splits). Weaker than J1 (0.62) and NL (0.61) but clearly
positive. Verdict: **SIGNAL-CANDIDATE (modest)** — justifies the
X3 decomposition arm in the goals design (as in J1), with the
expectation set accordingly.

**F6 — Shot quality is real; on-target rate is real here;
finishing is not.** Split-half r: xG per shot **0.472**,
on-target rate (SOT/shots) **0.555**, finishing (goals − xG)
**0.138**. Consequences, stated carefully: (i) X4 (xG/shot) is a
legitimate SOT arm candidate; (ii) the on-target-rate result does
**not** license a standalone trailing SOT-rate covariate — v5's
internal Beta-Binomial ratio component already carries that
information, and the harder-shrinkage arm (RS) is retained
precisely to test how much team ratio signal the gate believes;
(iii) finishing is **not consumed** by any arm: the DC blend (X1)
fits on goals directly, so team finishing is already inside the
goals ratings — adding it again would double-count (and at
r = 0.138 it is near-noise here anyway). Verdict:
**SIGNAL-CANDIDATE** (X4), recorded-not-consumed (on-target
rate), **NOISE** (finishing).

**F7 — xGOT: attacking post-shot quality is real in the
complete era.** Population rule (Phase 1 §2): xGOT is populated
for ~all shots only from **2025**. Era-restricted (matches from
2025-01-01, ratio of sums): split-half r = **0.422** attacking.
(The all-era figure, 0.845, mixes the on-target-only population
of earlier eras and is not comparable — do not use it.) No
defensive-side claim is made (not measured as a separate trait
here; J1's defensive side was NOISE and the design excludes it).
Verdict: **SIGNAL-CANDIDATE, era-guarded to 2025-01-01 onward** —
the X6 arm in the SOT design.

**F8 — Referee strictness is a strong trait here.** Yellows
(event target) per match by referee: split-half r = **0.724**
(23 referees with ≥20 matches; odd/even 0.77) — the strongest
referee signal in the program so far (NL 0.512, J1 0.65).
Coverage: 0% in 2021 (field empty), ~100% from 2022, **100% in
the virgin block** — X8 is honestly testable on the window that
decides. Verdict: **SIGNAL-CANDIDATE** for the cards design (X8
arm), subject to the walk-forward gate and the operational
pre-match-availability condition.

**F9 — Territorial pressure: box touches are the corners proxy,
where present.** Team opp-box-touches trait: split-half r =
**0.749** for / 0.802 against (measured on matches where the key
is present — 44–63% of 2021–2023, 100% from 2024). Production's
own covariates are also strong here (possession-for 0.940,
big-chance-for 0.641). Verdict: **SIGNAL-CANDIDATE** — the C-AR
design runs the box-touch multiplier (X7) against Gate Zero's
production covariates (X9), with the FEATURES min-8 trailing
rule absorbing the early gaps, exactly as C-J1 did for J1 2021.

**F10 — Star absence: NOT re-tested.** The question is closed
program-wide (V10 null on top-5, replicated null on J1); no new
reliability evidence exists in this corpus that could meet the
reopening standard, and none was sought. Lineup/absence features
remain forbidden.

**F11 — FotMob xG over-forecasts goals in this league.** Goals
per unit xG by block (2023+ only; 2021–2022 have no xG base to
calibrate against): 0.913, 0.937, 0.916, 0.898, 0.924, 0.938 —
pooled ≈ **0.92**. xG runs ~8% hot against actual goals here
(the opposite sign to NL's ≈1.05). Verdict: **SIGNAL** (input
quality fact) — the production blend (fit on goals + xG) remains
sound, but no xG-scale correction is introduced: the blend weight
is a frozen production constant, and any rescaling would be a
new design, not this program's port.

**F12 — Feasibility boundary (fact).** Every market's target
exists for **all 2,419 group matches in all blocks** (goals,
SOT, corners, event yellows, total shots). xG/shotmap exist from
2023 (the goals blend's goals-only fallback covers 2021–2022
training); referee exists from 2022 (the cards warm-up block is
2021, so X8 is testable on every scored block); period splits
limit halves *grading*, not any FT market. The virgin window
(2026 - Clausura group stage, complete, n = 240) contains every
target, the shotmap, and 100% referee coverage. **All five
candidates are feasible**: G-AR (goals), S-AR (SOT), C-AR
(corners), K-AR (cards), T-AR (total shots).

## Verification note (coordinator, independent of the EDA script)

- Levels and counts recomputed from the raw index + JSONs:
  2,464 index rows, 45 playoff exclusions, per-block group counts
  325/378/378/378/240/240/240/240, 1 score/event mismatch.
- Cards provenance audited through a second path: stats-feed vs
  event-feed yellows sampled per block (n≈40/block; full table in
  DATA_UNDERSTANDING §3.3) — the event target was adopted on that
  evidence, before any fitting.
- Newcomer pooled gaps recomputed directly from the match table
  (GF −0.121, GA +0.176 over 226 team-matches) — the script's
  per-transition table agrees.
- Yellows 1H share recomputed from raw card-event times over the
  warehouse (0.373 all blocks; 0.379 on 2024+ blocks) — the
  committed `eda.py` figure (0.373, via the builder's
  `fh_yellow_events_*` columns) agrees.
- xGOT population shares measured per block from the shotmap
  (Phase 1 §2): the 2025-01-01 era guard is set from the measured
  break (2024 is transitional at 0.85, 2025 is complete at
  0.996+), not copied from another league.
