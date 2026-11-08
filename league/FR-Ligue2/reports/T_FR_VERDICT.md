# Verdict — T-FR (FR-Ligue2 total shots)

**PASS (calibration PROVISIONAL) — arm A (v1 pattern) SHIPS.**

Calibration: actual − predicted. Primary line 22.5. Prereg:
`prereg/PREREG_T_FR.md`. Dev scored n = 1,065; virgin 2025/2026
n = 306, read ONCE for the three dev-passing arms.

## Dev gate (pooled LL@22.5)

| Arm | LL@22.5 | vs base 0.6916 | vs naive 0.6758 |
|---|---:|---|---|
| A | 0.6703 | pass | pass |
| B | 0.6694 | pass | pass |
| C | 0.6702 | pass | pass |

## Virgin legs (2025/2026)

| Arm | LL@22.5 | Calibration (pp) | SE (pp) |
|---|---:|---:|---:|
| A | **0.65432** | −1.16 | 2.75 |
| B | 0.65433 | −1.07 | 2.75 |
| C | 0.65442 | −1.03 | 2.75 |
| League base rate | 0.6968 | — | — |
| Naive trailing-10 | 0.6617 | — | — |

Leg (i) (LL ≤ reference arm A's **and** ≤ best baseline 0.6617):
A passes against itself and the baseline. B fails against A by
0.00001 LL (0.65433 > 0.65432) — a hairline margin, applied as
written. C fails against A (0.65442) as well.
Leg (ii): A's |−1.16pp| breaches the 1pp boundary by 0.16pp,
within 1 SE (2.75pp) — **PROVISIONAL PASS**.
Leg (iii): B's dev sign vs A was 2/3 and C's 1/3 — moot, both
already dead on leg (i).

**Ships:** arm A — `engine/total_shots/fitted_params_virgin.json`
and `predictions/t_fr_virgin_predictions.csv` (306 rows; FT ladder
21.5/22.5/23.5, halves presentation via the frozen 0.4702
constant). Coordinator verification: dev harness re-run reproduced
`results_dev.json` exactly; virgin LL (0.6543) and calibration
(−1.16pp) recomputed from the shipped CSV, exact.

Defect recorded: the first virgin export crashed —
`write_predictions` still carried the ES ladder in its fieldnames
(p_over_22_5/23_5/24_5) while the FR rows emit p_over_21_5/22_5/23_5,
leaving a header-only CSV. The coordinator fixed the fieldnames
(one line) and re-ran the export; the recomputed virgin metrics
were bit-identical to the first read's `results_virgin.json`
(all five arm/baseline blocks), so the virgin was read once in
substance — the re-run reproduced the same numbers deterministically
and only completed the export step.
