# T-NLE Verdict — Eerste Divisie total shots model

Date: 2026-11-09. Branch `build/nl-eerste`. Prereg:
`league/NL-EersteDivisie/prereg/PREREG_T_NLE.md` (commit f267312,
frozen before any fitting; provenance: built ahead of the top-5
family's frozen prospective verdict under the user's standing
order, on this corpus only — that trial is untouched). Engine:
`league/NL-EersteDivisie/engine/total_shots/`. Implementation by
Codex (gpt-5.6-luna); dev and virgin headline numbers were
recomputed independently by the coordinator from the per-match
predictions CSVs (identical to the JSONs). Calibration =
actual − predicted. Predictions-only product.

## Verdict: PASS (calibration PROVISIONAL) — arm A (v1 pattern) ships

All three arms pass the dev gate. On the virgin window arm B
posts the best LL but fails the frozen leg (iii) dev sign check
(1/3 seasons); arm C fails leg (i) and the calibration leg. Arm
A passes legs (i) and (ii-provisional) and ships. The shipped
file is `predictions/t_nle_virgin_predictions.csv` (arm = A,
force-added), with fitted params in
`engine/total_shots/fitted_params.json` (r_A = 111.24).

## Dev results (per-match walk-forward, warm-up 2021/2022, scored 2022/2023–2024/2025, n = 1140)

LL@25.5 (binary log-loss on P(over 25.5)):

| Season | Arm A (v1) | Arm B (v2 level) | Arm C (E9 trailing-r) | Base rate | Naive t-10 |
|---|---|---|---|---|---|
| 2022/2023 | 0.6613 | 0.6616 | 0.6612 | — | — |
| 2023/2024 | 0.6883 | 0.6889 | 0.6877 | — | — |
| 2024/2025 | 0.6682 | 0.6681 | 0.6683 | — | — |
| **Pooled** | **0.6726** | 0.6729 | **0.6724** | 0.6930 | 0.6845 |

Dev gate (pooled LL@25.5 beats BOTH baselines): A **PASS**,
B **PASS**, C **PASS** — all three were read on the virgin
window.

## Virgin results (season "2025/2026", n = 380, read once after dev froze)

Actual over-25.5 rate 66.05%; mean total shots 28.49 (the virgin
season ran very hot vs the dev mean of 26.02).

| Arm | LL@25.5 | Mean P(over 25.5) | Calib (actual − pred) | Calib SE |
|---|---|---|---|---|
| Arm A (v1) | **0.6219** | 62.85% | +3.20pp | 2.38pp |
| Arm B (v2 level) | **0.6195** | 64.32% | +1.73pp | 2.38pp |
| Arm C (E9) | 0.6233 | 62.08% | +3.97pp | 2.38pp |
| Base rate (league NB) | 0.6499 | — | — | — |
| Naive t-10 | 0.6250 | 63.22% | +2.83pp | — |
| Base rate (constant) | 0.6882 | 50.79% | +15.26pp | — |

## Per-leg verdicts

| Leg | Arm A | Arm B | Arm C |
|---|---|---|---|
| Dev gate | PASS | PASS | PASS |
| Virgin (i) LL ≤ Arm A's (0.6219) and ≤ best baseline's (0.6250) | PASS | PASS (0.6195) | **FAIL** (0.6233 > 0.6219) |
| Virgin (ii) calibration ≤1.0pp (breach ≤1 SE = provisional) | PROVISIONAL PASS (breach 2.20pp ≤ SE 2.38pp) | PROVISIONAL PASS (breach 0.73pp) | **FAIL** (breach 2.97pp > SE 2.38pp) |
| (iii) dev sign check vs Arm A | n/a | **FAIL (1/3 seasons)** | PASS (2/3 seasons) |
| **Overall** | **PASS — ships** | FAIL | FAIL |

Reading: as in T-NL, the level layer (B) is the best virgin
performer and the best calibrated — it earns its keep exactly in
a hot season — and as in T-NL it is blocked by the frozen sign
check it failed on dev (worse than A in both 2022/2023 and
2023/2024). The gate rules are the gate rules; B's virgin form is
recorded here for any future prereg to weigh with 2025/2026 as
dev-era data. Arm A's provisional calibration is the same
hot-season pattern as S-NLE: real, inside 1 SE, not clean.

Coordinator correction applied to the shipped file: the ported
runner derived the 1H/2H presentation lines with the J1 constant
0.449; the shipped CSV's halves columns (and the engine code and
fitted params) were corrected to this league's frozen constant
**0.451**. FT probabilities — the gated quantities — are
unchanged. The 1H/2H ladder lines themselves (1H 10.5/11.5/12.5,
2H 12.5/13.5/14.5) follow the reference port's format, as in the
shipped T-NL file.
