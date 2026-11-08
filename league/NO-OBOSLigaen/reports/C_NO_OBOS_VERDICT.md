# C-NO-OBOS verdict — corners

**PASS (calibration PROVISIONAL) — Gate Zero SHIPS.**

Reference: production `model_corners_v3` pattern (NO-Eliteserien
engine), territorial multiplier reduced to the possession covariate
only (big_chance does not exist in this feed — prereg, RU-1Division
precedent). Primary line 10.5. Prereg: `prereg/PREREG_C_NO_OBOS.md`.
FT-only market (no halves source).

## Dev (season-blocked walk-forward, target seasons 2022–2025, n=959)

| Arm | LL@10.5 pooled | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
| Gate Zero | 0.6969 | 0.6996 | 0.6995 | 0.6960 | 0.6925 |
| PLAIN | 0.6956 | 0.6996 | 0.6963 | 0.6938 | 0.6925 |
| League base rate | 0.7257 | | | | |
| Naive trailing-10 | 0.7205 | | | | |

Both arms beat both baselines → both passed the dev gate. Pooled
values verified by the coordinator as n-weighted means of the season
rows in `engine/corners/results_dev.json` — exact agreement.

## Virgin (2026, read ONCE, n=237 with target)

| Arm | LL@10.5 | Mean P(over) | Actual | Cal. diff | SE |
|---|---|---|---|---|---|
| Gate Zero | 0.6898 | 0.5051 | 0.4937 | +1.14pp | 3.24pp |
| PLAIN | 0.6898 | 0.5051 | 0.4937 | +1.14pp | 3.24pp |
| League base rate | 0.7287 | 0.3629 | 0.4937 | | |
| Naive trailing-10 | 0.7187 | 0.3736 | 0.4937 | | |

The two arms' virgin predictions are **identical**: the virgin fit
chose β = 0.0 for the possession multiplier (`fitted_params_virgin.json`:
gamma 0.15, r 1.1653, beta [0.0], fit_n 1,080), so the multiplier is
inactive and Gate Zero ≡ PLAIN on the virgin window. Virgin LL
recomputed by the coordinator from the shipped predictions CSV —
0.6898, exact agreement.

## Gate arithmetic

- Leg (i): 0.6898 ≤ Gate Zero's 0.6898 and ≤ best baseline 0.7187 → pass.
- Leg (ii): calibration breach |+1.14pp| > 1.0pp, but within 1 SE
  (3.24pp) → **PROVISIONAL PASS**.
- Leg (iii) (PLAIN): dev LL ≤ Gate Zero's in 4 of 4 dev seasons
  (strictly better 2023/2024, identical 2022/2025) → pass.
- Both arms pass; virgin LLs tie exactly → the frozen tie rule ships
  the simpler arm: **Gate Zero**.

## What ships

**Gate Zero** (possession-multiplier architecture; the fitted virgin
multiplier is β=0, i.e. the ratings+NB core carries the predictions).
Predictions: `predictions/c_no_obos_virgin_predictions.csv` (237 rows,
FT ladder 9.5/10.5/11.5, arm `gate_zero`). Fitted params:
`engine/corners/fitted_params_virgin.json`. This is the league's
first passing market → NO-OBOSLigaen joins the daily runner with
corners/Gate Zero (FT-only, no halves).
