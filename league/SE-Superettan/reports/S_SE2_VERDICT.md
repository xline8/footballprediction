# Verdict — S-SE2 (SE-Superettan SOT): **FAIL (virgin legs i + ii)**

Frozen gates: PREREG_S_SE2.md (730a5c1, before fitting). Primary line 9.5.

## Dev (warm-up 2022; scored 2023–2025, n = 710)
| Arm | LL@9.5 pooled | vs league base 0.694343 | vs naive 0.703502 |
|---|---|---|---|
| Gate Zero | 0.683628 | pass | pass |
| RS | 0.683467 | pass | pass |
RS sign check vs GZ: better in 2023 and 2025, worse in 2024 → 2/3, passes leg (iii) at dev stage.

## Virgin 2026 (n = 237 stats rows) — read ONCE
| Arm | LL@9.5 | Calibration (mean P − actual) | 1 SE |
|---|---|---|---|
| Gate Zero | 0.752973 | **+9.92pp** | 3.35pp |
| RS | 0.753092 | **+10.21pp** | 3.35pp |

Leg (i): the harness's own baseline block was computed on the WRONG season
(2025 rows — a stale-season remnant of the SE copy; defect recorded below), so
leg (i) was re-scored independently from the league CSV: the true 2026 league
base rate (prior-seasons over-9.5 rate 0.5105) gives LL **0.697544** on the
virgin — both arms (0.7530 / 0.7531) lose to it by ~0.055. Leg (i) FAIL.
Leg (ii): calibration breach +9.92pp / +10.21pp is far beyond the 1pp boundary
+ 1 SE (4.35pp). FAIL. → **FAIL; nothing ships.**

Cause, as frozen in EDA F1 before fitting: 2026 SOT collapsed (8.57/match,
over-9.5 rate 0.4008) after the anomalous hot 2025 (12.33/match); a model
trained through 2025 massively over-predicts the virgin.

## Defects found in the engine (recorded; neither changes the verdict)
1. Harness baseline block scored baselines on 2025 instead of the 2026 virgin
   rows (arms were scored correctly on 2026). Corrected comparison supplied
   independently above; arms fail regardless.
2. The harness auto-wrote a GZ predictions CSV + fitted params despite the
   FAIL (its choose/write path is unconditional). Both artifacts were DELETED
   before shipping anything; `predictions/` contains no SOT file.
