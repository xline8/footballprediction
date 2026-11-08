# Verdict — G-ITB (Italy Serie B goals) — **FAIL** (dev gate, all three legs; virgin NOT read)

Prereg: `prereg/PREREG_G_ITB.md` (frozen 369a3a7, before fitting).
Goals-only DC by design (xG era starts inside the virgin: 13 of
1,559 dev matches carry `expected_goals`). Calibration in this
league is defined as actual − predicted (not needed here — the
virgin was never read). Dev = walk-forward 2022/2023–2024/2025
(pooled n=1,169), seed 2021/2022. Virgin = 2025/2026 (n=390) —
**deliberately NOT read**: Gate Zero failed the dev gate, and the
prereg's mechanical reading makes the variants moot.

## Dev (per season)

| Season | Arm | 1X2 LL | RPS | OU2.5 LL | Climatology LL / RPS / OU LL |
|---|---|---|---|---|---|
| 2022/2023 (n=390) | Gate Zero | 1.1135 | 0.2277 | 0.6889 | 1.0851 / 0.2196 / 0.6745 |
| 2023/2024 (n=390) | Gate Zero | 1.1024 | 0.2253 | 0.7076 | 1.0993 / 0.2247 / 0.7049 |
| 2024/2025 (n=389) | Gate Zero | 1.1089 | 0.2244 | 0.7126 | 1.0843 / 0.2175 / 0.6912 |
| **Pooled (n=1,169)** | **Gate Zero** | **1.1083** | **0.2258** | **0.7030** | **1.0896 / 0.2206 / 0.6902** |
| Pooled | SHRINK | 1.1083 | 0.2258 | 0.7030 | identical to Gate Zero (see below) |
| Pooled | X2 | 1.1099 | 0.2261 | 0.7022 | worse than Gate Zero pooled |

## Gate arithmetic (pooled dev, verbatim legs)

- 1X2 LL leg: 1.1083 > climatology 1.0896 ✗
- RPS leg: 0.2258 > climatology 0.2206 ✗
- OU2.5 LL leg: 0.7030 > base-rate 0.6902 ✗

Gate Zero loses **all three legs** — the most complete goals dev
failure in the program so far (ES/ITC lost only the OU leg). It
loses the 1X2 leg in every dev season, not on one bad fold. A
plausible mechanism is visible in the levels: the dev window
contains both the league's coldest season (2022/2023, 2.328
goals, after a 2.485 seed) and its home-win collapse season
(2023/2024, HW 36.9% vs 41% in the seed) — an expanding DC with a
fitted home advantage and slow 270-day decay prices both regimes
late, while climatology's pooled rates sit closer to each
season's realised mix. That is an explanation, not an excuse:
the gate is the gate.

- SHRINK is numerically identical to Gate Zero in every dev
  season: under season-blocked expanding fits, target-season
  teams are either unseen (n=0) or carry full prior seasons, so
  no team ever sits at 1–5 prior matches — the arm reduces to
  the n=0 case by construction (the G-BG2 / G-SCO / G-ITC shape).
- X2 (frozen mover offsets, Serie A +0.145/−0.143, Serie C
  −0.070/+0.118) improves on Gate Zero in two dev seasons
  (1X2 LL 1.1124 and 1.0985 vs 1.1135 and 1.1024) but is worse
  pooled and much worse in 2024/2025 (1.1189 vs 1.1089); it
  fails the same three legs against climatology. The mover
  signal measured in EDA is real descriptively; it does not
  rescue a base model that is already behind climatology.

**Verdict: FAIL. Nothing ships.** No fitted params, no
predictions CSV. `engine/goals/results_virgin.json` records
`{"virgin_read": false, "reason": "gate zero failed dev gate"}`
— 2025/2026 remains untouched for a future pre-registered
attempt, and 2026/2027 remains reserved as confirmatory.

## Verification (builder-side, independent of the engine)

- Climatology pooled dev (LL 1.089581 / RPS 0.220603 / OU LL
  0.690184) recomputed from the raw CSV by a separate script —
  exact match, per season and pooled.
- `dc.py` is the proven ES/ITC goals-only reference (diff vs
  IT-SerieC shows only the xG-blend branch that ITB does not
  use, per the era-dead design).
- The dev harness loads only 2021/2022–2024/2025; the virgin
  season is unreachable in the dev path.

## League completion state (goals)

G-ITB has run its full gate honestly to FAIL. See the other
verdicts for S/C/K/T.
