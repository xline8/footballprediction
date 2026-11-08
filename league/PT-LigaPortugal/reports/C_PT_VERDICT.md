# C-PT Verdict — Liga Portugal corners model

Date: 2026-11-09. Branch `build/pt-liga`. Prereg:
`league/PT-LigaPortugal/prereg/PREREG_C_PT.md` (dc457f5, frozen
before fitting). Engine: `league/PT-LigaPortugal/engine/corners/`.

## Verdict: FAIL at the dev gate — virgin deliberately NOT read

Both arms lose the dev gate to both baselines. Unlike J1, where
corner levels rose and the decay-weighted baselines ran cold, PT
corner levels are stable-to-falling, the baselines are well
calibrated, and the reference pattern's fitted dispersion
(r ≈ 1.27–1.37) flattens its probabilities past the point where
its (accurate) mus can win: pooled mean mu 9.82 vs actual 9.93,
yet mean P(over 9.5) only ~0.39–0.42.

## Dev results (pooled n=1,224, LL@9.5)

| Arm / baseline | LL@9.5 |
|---|---|
| Gate Zero (X9) | 0.7161 |
| X7 (box touches) | 0.7173 |
| League base rate | 0.6978 |
| Naive trailing-10 | 0.6965 |

Per-season Gate Zero: 0.7468 / 0.7187 / 0.6891 / 0.7097 (baselines
win every season pooled-wise; full table in results_dev.csv).
Fitted gamma hit the grid edge (0.8) in every season for both
arms; territorial betas were small (possession +0.0025, big-chance
0 to +0.05; box-touch +0.01 fading to 0). X7's strong EDA trait
(r=0.88) earned nothing inside the multiplier structure — the
C-J1 result repeating in a second league.

Dev gate: both arms FAIL → per the frozen rule the virgin window
(2026/2027) was NOT read and remains virgin for one future read
under a new prereg. No virgin predictions exist for this market.
Nothing ships.

## Verification notes

Coordinator fixes before dev froze: gamma is now selected by
full-count NB NLL per the prereg (Codex's repair used binary LL),
training rows require ≥10 prior league matches, and baselines are
scored with their own r_base rather than the arm's r. Mus were
spot-checked for calibration in mean (above); the naive baseline
is asserted equal to a brute-force recomputation inside the
runner on every run.
