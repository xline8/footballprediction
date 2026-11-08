# Phase 3 — EDA: Mexico Liga MX (2021/2022 - Apertura – 2025/2026 - Clausura)

Computations: `eda.py` (digest in `eda_summary.json` +
`inventory_summary.json`); the cards stats-vs-events audit and the
altitude comparison were also recomputed by the coordinator through
an independent path (raw index + JSON probe). Sample: 1,530
regular-phase matches (10 complete tournaments × 153). Standard
(same as J1/AR): a trait is a signal candidate only if it reproduces
on disjoint halves of the same teams' matches (split-half,
career-pooled per team ≥24 matches, 60 random splits averaged;
ratio traits as **ratios of sums**) or survives a variance
decomposition against its sampling-noise floor.

## Levels (regular phase)

| Tournament | Goals | Shots | SOT | Corners | Yellows (events) | Team xG |
|---|---|---|---|---|---|---|
| 2021/2022 - Apertura | 2.17 | 24.65 | 7.57 | 8.97 | 4.07 | 2.28 |
| 2021/2022 - Clausura | 2.53 | 25.84 | 8.51 | 9.46 | 4.76 | 2.43 |
| 2022/2023 - Apertura | 2.75 | 27.48 | 9.16 | 9.72 | 4.76 | 2.48 |
| 2022/2023 - Clausura | 2.82 | 28.46 | 9.54 | 10.12 | 4.44 | 2.76 |
| 2023/2024 - Apertura | 2.85 | 27.43 | 9.57 | 10.14 | 5.05 | 2.73 |
| 2023/2024 - Clausura | 2.99 | 27.24 | 8.96 | 10.09 | 4.47 | 2.70 |
| 2024/2025 - Apertura | 2.63 | 26.80 | 9.03 | 10.11 | 4.16 | 2.60 |
| 2024/2025 - Clausura | 2.86 | 25.78 | 8.91 | 10.12 | 4.34 | 2.50 |
| 2025/2026 - Apertura | 3.11 | 26.12 | 9.00 | 9.41 | 4.71 | 2.76 |
| 2025/2026 - Clausura (virgin) | 2.74 | 27.43 | 9.13 | 9.38 | 4.28 | 2.66 |
| **Pooled** | **2.74** | **26.72** | **8.94** | **9.75** | **4.50** | **2.59** |

Pooled: home goals 1.54 / away 1.20 (home edge **+0.34**); home/
draw/away 44.5 / 26.3 / 29.2%; BTTS 55.8%; Over 2.5 52.8%.
Dispersion (variance/mean): goals 0.97 (Poisson-like), SOT 1.13,
corners 1.07, yellows 1.03, total shots 1.31.

Context: Liga MX sits between AR and the European leagues —
mid-scoring (2.74 vs AR 2.13, J1 2.55, NL 3.12), high shots
(26.7), high yellows (4.50, second only to AR's 4.89 in the
program). Per-league fitting is again the whole point.

## Findings

**F1 — Levels drift by tournament.** Goals rose from 2.17
(2021/2022 Apertura — a clear low outlier, the warm-up block) to a
2.6–3.1 band; corners stepped from ~9.0–9.5 to ~10.1 in 2022/2023
Clausura and stayed there until a cooler virgin (9.38); shots
peaked at 28.5 in 2022/2023 Clausura. Home edge +0.34 pooled.
Verdict: **SIGNAL** (descriptive). Time-decayed per-league fitting,
as in production.

**F2 — Core team traits are strongly reliable.** Career split-half
r: shots-for **0.845** / against 0.890, SOT-for **0.848** / 0.797,
xG-for 0.811 / 0.881, goals-for 0.773 / 0.790, corners-for 0.670 /
0.718, yellows-for 0.528 / 0.535, big-chance-for 0.726,
possession-for 0.927, box-touches-for **0.863** / 0.890. At or
above J1's values in most markets. Verdict: **SIGNAL** — the
feasibility base for all five candidates.

**F3 — Half shares are (near-)noise; frozen constants it is.**
True variance of the per-match 1H share (observed minus binomial
floor): goals **+0.0010**, SOT **+0.0014**, corners **+0.0014**,
total shots **+0.0004**, yellows **+0.0071** — all at or near the
noise floor (yellows the largest, as in AR's +0.0047; still no
team-level mechanism licensed by the program standard). Verdict:
**NOISE** for modelling. **Frozen constants (ratio of sums)**:
goals **0.456** (n=1,419 matches with HT data), SOT **0.455**,
corners **0.465**, total shots **0.458** (splits-present matches,
n≈1,020), yellows **0.385** (event timing, n=1,497 matches with
yellows > 0).

**F4 — No movers exist in this league.** The team set is exactly
the same 18 clubs in all 10 tournaments; every one of the 9
transitions has zero entrants and zero departures (no
promotion/relegation since 2020). There is nothing to measure a
mover gap on. Verdict: **X2 DROPPED** (see FEATURES) — and the
G-J2 thin-team lesson does not bind here either: with an expanding
window across tournaments, every club carries deep history into
every block after warm-up.

**F5 — Set-play xG share is a real team identity.** Split-half
r = **0.558** (ratio of sums), measured on Liga MX regular rows.
(0.353). Verdict: **SIGNAL-CANDIDATE** — justifies the X3
decomposition arm in the goals design.

**F6 — Shot quality is real; on-target rate is real; finishing is
not.** Split-half r: xG per shot **0.626**, on-target rate
(SOT/shots) **0.488**, finishing (goals − xG) **0.171**. As in AR:
X4 is a legitimate SOT arm; the on-target-rate result does not
license a standalone covariate (v5's internal Beta-Binomial ratio
already carries it; the RS arm tests its shrinkage); finishing is
**NOISE** and not consumed.

**F7 — xGOT is NOISE in this league, even in its complete era.**
Population rule (Phase 1): xGOT is populated for ~30–35% of shots
(on-target only, share ~0.57–0.59; off-target ~0.00–0.04) through
2023/2024, transitional in 2024/2025 Apertura (all-shots 0.855),
and complete (0.997+) only from 2024/2025 Clausura — the era guard
would be 2025-01-01. But era-restricted attacking xGOT-per-shot
split-half r = **0.073** (all-era 0.012). Unlike J1 (0.518) and AR
(0.422), the trait does not reproduce here. Verdict: **NOISE —
X6 DROPPED**; the SOT design runs GZ / RS / X4 only. This is the
build's clearest case of the measurement overruling the template.

**F8 — Referee strictness is a weak-moderate trait, with a
coverage collapse late in the window.** Yellows (event target) per
match by referee: split-half r = **0.331** (19 referees with ≥20
matches) — real but well below J1 (0.65) / AR (0.72). Coverage:
0% in the warm-up tournament, 95–100% from 2021/2022 Clausura
through 2024/2025 Clausura, then **24.8%** in 2025/2026 Apertura
and **58.2%** in the virgin block. Verdict: **SIGNAL-CANDIDATE
(weak)** — the X8 arm is preregistered and gated, with the
preregistered fallback (shrunk league mean) covering unnamed
referees; expectations set accordingly.

**F9 — Territorial pressure: box touches are the corners proxy.**
Team opp-box-touches trait split-half r = **0.863** for / 0.890
against (present in 39–96% of early-tournament matches, 100% from
2023/2024 Apertura). Production's own covariates are also strong
(possession-for 0.927, big-chance-for 0.726). Verdict:
**SIGNAL-CANDIDATE** — C-MX runs the box-touch multiplier (X7)
against Gate Zero's production covariates (X9), min-8 trailing
rule absorbing the early gaps.

**F10 — Star absence: NOT re-tested.** Closed program-wide (V10
null on top-5, replicated null on J1); no new reliability evidence
exists in this corpus that could meet the reopening standard, and
none was sought. Lineup/absence features remain forbidden.

**F11 — FotMob xG slightly UNDER-forecasts goals here.** Goals
per unit xG by tournament: 0.952, 1.043, 1.109, 1.024, 1.045,
1.105, 1.012, 1.144, 1.125, 1.029 — pooled ≈ **1.05** (NL-like;
the opposite sign to AR's ≈0.92). Verdict: **SIGNAL** (input
quality fact) — the production blend stays as-is; no xG-scale
correction is introduced.

**F12 — Altitude: a large descriptive home effect that cannot be
separated from team identity.** Stadium city is in every payload;
altitudes are mapped statically in `eda.py` (Ciudad de México
2,240m — América, Cruz Azul, Pumas; Toluca 2,600m; Pachuca
2,432m; Puebla 2,135m are the ≥2,000m group). Home-goal edge:
high-altitude home teams **+0.586** (n=510, home win 50.6%) vs
the rest **+0.221** (n=1,020, 41.5%). Restricted to visitors from
<1,000m: **+0.875** (n=120, 56.7%) vs +0.077 (n=220, 40.5%). The
gap is big — and unidentifiable as an *altitude* effect: altitude
is a fixed attribute of six specific clubs (several of them
historically strong), the team set never changes, and team /
venue-split ratings in the reference architectures already absorb
each club's home strength, altitude included. There is no
within-team altitude variation to identify a separate coefficient
from, and no reliability check can manufacture one. Verdict:
**DESCRIPTIVE / NOT ADOPTED** — no altitude feature or arm; the
measurement stands as the documentation.

**F13 — Feasibility boundary (fact).** Every market's target
exists for all 1,530 regular matches in all tournaments (goals,
SOT, corners, event yellows, total shots); xG and shotmap are
100% in every tournament (no goals-only era — the blend's fallback
never binds); referee exists from the second tournament (the
warm-up block is referee-free, so X8 is testable on every scored
dev block, subject to the late-window coverage collapse, F8);
period splits limit halves *grading*, not any FT market. The
virgin window (2025/2026 Clausura regular phase, complete,
n = 153) contains every target and the shotmap; referee coverage
there is 58.2%. **All five candidates are feasible**: G-MX, S-MX,
C-MX, K-MX, T-MX.

## Primary lines (from the dev line tables, dev n = 1,377)

| Market | Dev mean | Line | Dev over-rate | Ladder |
|---|---|---|---|---|
| SOT | 8.92 | **8.5** | 51.2% | 7.5 / 8.5 / 9.5 |
| Corners | 9.79 | **9.5** | 50.8% | 8.5 / 9.5 / 10.5 |
| Cards (events) | 4.53 | **4.5** | 47.5% | 3.5 / 4.5 / 5.5 |
| Total shots | 26.65 | **26.5** | 47.9% | 25.5 / 26.5 / 27.5 |

## Verification note (coordinator, independent of the EDA script)

- Levels and counts recomputed from the raw index + JSONs:
  1,829 index rows; regular 153 × 10 complete tournaments;
  playoffs 18 × 4 + 14 × 6 = 156; in-progress 2026/2027 Apertura
  143 regular rows excluded wholesale.
- Cards provenance audited through a second path (full-corpus
  probe): stats-feed yellows undercount the event feed in every
  dev tournament on regular-phase numbers too (builder table in
  DATA_UNDERSTANDING) — the event target was adopted on that
  dev-era evidence, before any fitting.
- Altitude city counts spot-checked against stadium cities in the
  raw payloads (Ciudad de México 324 matches incl. both spellings,
  Toluca 108, Pachuca 103, Puebla 110 in the all-phases probe).
