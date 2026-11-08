# Step 3 — EDA (CZ-Liga)

Computed by `analysis/run_eda.py` → `analysis/eda_numbers.json`;
mover/halves-variance/referee items computed by the coordinator from
the built CSV + FNL index and appended to the same JSON (keys
`movers_x2`, `halves_variance`, `referee_coverage`). Dev era for
reliability/halves = 2021/2022–2024/2025, included phases only.

## F1 — Levels per season (per match, included phases)

| Season | Goals | SOT | Corners | Total shots | Event yellows |
|---|---|---|---|---|---|
| 2021/2022 | 2.79 | 8.56 | 9.92 | 16.37 | 4.13 |
| 2022/2023 | 2.96 | 9.30 | 10.91 | 18.23 | 3.88 |
| 2023/2024 | 2.86 | 8.77 | 10.46 | 17.72 | 4.61 |
| 2024/2025 | 2.67 | 8.08 | 10.00 | 17.78 | 3.85 |
| 2025/2026 (virgin) | 2.60 | 8.51 | 9.96 | **25.54** | 3.96 |
| 2026/2027 (in progress) | 2.76 | 8.89 | 10.18 | **28.09** | 3.75 |

Goals drift mildly downward (2.79→2.60 across the window); SOT and
corners are level-stable; event yellows spike in 2023/2024 (4.61)
against ~3.8–4.1 elsewhere. Total shots breaks at the rich-feed
boundary (+44%) — see DATA_UNDERSTANDING defect 1.

## F2 — Team trait reliabilities (split-half, odd/even matches,
career-pooled team-seasons, ratio-of-sums; n = 64 units)

| Trait | r (for) | r (against) |
|---|---|---|
| Goals | 0.648 | 0.366 |
| SOT | 0.689 | 0.621 |
| Corners | 0.526 | 0.614 |
| Event yellows | 0.302 | 0.509 |
| Possession | 0.809 | 0.809 |
| Total shots (report only) | 0.680 | 0.711 |

All candidate targets have reliable team traits (weakest: yellows-for
0.302, goals-against 0.366 — real but modest). Possession is the most
reliable trait in the league (0.809), supporting the corners Gate Zero
covariate (X9 reduced form).

## F3 — Halves (event times, dev era): frozen constants, team shares are noise

Pooled 1H shares: **goals 0.4509** (3,045 goals), **yellows 0.3150**
(4,448 yellows). Variance decomposition (per-match share variance vs
binomial noise at the pooled share): goals observed 0.1066 vs noise
0.1116 → true variance ≈ **−0.005 (≈ 0)**; yellows observed 0.0738 vs
noise 0.0704 → true variance +0.0033 (tiny). Team split-half
reliability of the 1H share: goals r = −0.067, yellows r = −0.214 —
**per-team half shares are pure noise** (the J1 F3 result replicates).
Only the league constants ship, presentation-only. Stats markets
(SOT/corners/total shots) have **no dev-era halves source** (period
splits exist only in the virgin/current seasons) → those markets are
frozen **FT-only** (RU-1Division precedent).

## F4 — Movers (X2 evidence; FNL id 253 in-warehouse)

Exactly one promoted club per boundary in this window. First-season
deviation from the 1. Liga mean (included phases, n = 35 each):

| Boundary | Club | ΔGF/match | ΔGA/match | (FNL prior GF/GA) |
|---|---|---|---|---|
| →2022/2023 | FC Zbrojovka Brno | −0.308 | +0.349 | 2.03 / 0.97 |
| →2023/2024 | Karvina | −0.344 | +0.342 | 1.93 / 1.23 |
| →2024/2025 | Dukla Praha | −0.362 | +0.238 | 1.83 / 0.97 |
| →2025/2026 | FC Zlin | −0.071 | +0.300 | 1.50 / 0.47 |

4/4 transitions: attack below league mean, defence worse than league
mean — the J1 F4 pattern at ~half the J.League magnitude. Cumulative
mean offsets from completed transitions: before 2023/2024
(−0.308, +0.349); before 2024/2025 (−0.326, +0.345); before 2025/2026
(−0.338, +0.310). Before 2022/2023 no transition is completed inside
the warehouse window → X2 ≡ Gate Zero for that evaluation season by
construction. SIGNAL (unanimous, if thin: n = 1 mover/boundary).

## F5 — Referee strictness: NOT ESTIMABLE

Referee names exist in 0/1,105 dev-era matches (feed defect 2).
No reliability number can be computed; X8 is dropped on data absence
in the dev era, not on a failed test.

## F6 — Cards artefact (frozen target check)

Stats-vs-events yellows, rich era (n = 388): exact agreement 85.6%,
means 3.78 vs 3.88 (events count +0.10/match more), reds agree
386/388. Events are the only all-era source and are complete with
times → event-unified yellows frozen as the target (Step 2).

## Primary lines (dev pooled, included phases; over-rate closest to 0.5)

- SOT **8.5** (over 0.4986; 7.5 → 0.634, 9.5 → 0.379)
- Corners **10.5** (over 0.4565; 9.5 → 0.575, 8.5 → 0.688)
- Cards **3.5** (over 0.5676; 4.5 → 0.384, 5.5 → 0.246)
- Goals: programme-standard OU2.5 (dev over-rate 0.548)
