# S-DE2 verdict — PASS (calibration PROVISIONAL) — RS SHIPS

Prereg: `prereg/PREREG_S_DE2.md` (frozen 4261ad8, before fitting).
Primary line **9.5** (dev over-rate 0.450). Dev pooled n = 918;
virgin 2025/2026 n = 306, read once. Arms: Gate Zero + RS + X4
(X4 adopted on DE-2 reliability, EDA F7 r = 0.529 — the program's
strongest xG/shot reading; X6 dropped, F8 r = 0.182).

## Dev results — pooled LL@9.5

| Arm / baseline | LL@9.5 |
|---|---|
| Gate Zero | 0.6849 |
| RS (BB prior 20,000) | 0.6848 |
| X4 (xG/shot quality) | 0.6849 |
| League base rate | 0.6882 |
| Naive trailing-10 | 0.6979 |

All three arms beat both baselines → all pass the dev gate.
Per-season sign checks vs Gate Zero: RS 2/3 (better 2022/2023 and
2023/2024, worse 2024/2025); X4 1/3 (better only 2024/2025).

## Virgin results (2025/2026, n = 306)

| Arm / baseline | LL@9.5 | Calibration (mean P − actual) |
|---|---|---|
| Gate Zero | 0.6622 | +2.69pp (SE 2.77pp) |
| RS | 0.6622 | +2.61pp (SE 2.77pp) |
| X4 | 0.6617 | +3.99pp (SE 2.76pp) |
| League base rate | 0.6798 | — |
| Naive trailing-10 | 0.6649 | — |

## Gate arithmetic

- Leg (i): Gate Zero and RS pass (both ≤ Gate Zero trivially /
  0.66218 ≤ and ≤ best baseline 0.66487). X4's LL is the best of
  the three (0.66165) — leg (i) is not its problem.
- Leg (ii): Gate Zero and RS breach the 1.0pp boundary by 1.69pp /
  1.61pp, each within 1 SE (2.77pp) → **PROVISIONAL PASS** for
  both. **X4 FAILS leg (ii) outright**: its breach beyond the
  boundary is 2.99pp, beyond 1 SE (2.76pp) — the program's
  strongest xG/shot trait produces the worst-calibrated virgin
  arm. (X4 also fails leg (iii), sign 1/3.) The virgin season ran
  hot on SOT relative to every arm's prediction (actual over-9.5
  rate above prediction throughout).
- Leg (iii): RS sign check 2/3 (above).
- Both Gate Zero and RS pass; the both-pass rule ships the lower
  pooled virgin LL: **RS** (0.662183 < 0.662198 — a 0.000015
  margin, recorded as such; the same RS-by-a-hair shape as
  S-BE/S-CH).

**Ships:** RS (v5 pattern with the ratio-shrink prior P = 20,000),
fitted parameters in `engine/sot/fitted_params_virgin.json`,
virgin predictions in `predictions/s_de2_virgin_predictions.csv`
(306 rows; FT ladder 8.5/9.5/10.5 + 1H/2H via the frozen SOT
constant 0.443). **DE-2 joins the daily runner with SOT.**
Builder verification: virgin LL@9.5 recomputed from the shipped
predictions CSV = 0.6622, matching the results JSON; calibration
recomputed +2.61pp.

Recorded plainly (engine deviations, both prereg-faithful):
(1) this league's SOT walk-forward is date-grouped (same-date
matches never see each other) as PREREG_S_DE2's text requires —
the BE/J1 engine code updates per-match instead; (2) the league
base rate is computed per line (BE's code reuses its 8.5 rate for
every ladder line). Neither changes any gate comparison's fairness:
arms and baselines share the harness. Also recorded: the harness's
own virgin selection excluded X4 over leg (iii) before the read;
the builder read X4's virgin metrics once, separately, for the
record (table above) — it fails leg (ii) outright, so the
exclusion changed no outcome.
