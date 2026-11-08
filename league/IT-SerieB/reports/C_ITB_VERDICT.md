# Verdict — C-ITB (Italy Serie B corners) — **PROVISIONAL PASS** (Gate Zero ships)

Prereg: `prereg/PREREG_C_ITB.md` (frozen 369a3a7, before
fitting). Primary line 9.5. Gate Zero (X9) only — the X7
box-touch arm was dropped in FEATURES (for r=0.320 on 16 teams,
against r=−0.129). Dev n=1,169, virgin 2025/2026 n=390.
**Calibration = actual − predicted** (this league's definition).

## Dev (pooled LL@9.5; baselines: league 0.7126, naive 0.7224)

| Season | Gate Zero | League base rate | Naive trailing-10 |
|---|---|---|---|
| 2022/2023 | 0.6974 | 0.7353 | 0.7428 |
| 2023/2024 | 0.6958 | 0.7134 | 0.7241 |
| 2024/2025 | 0.6865 | 0.6892 | 0.7002 |
| **Pooled** | **0.6932** | **0.7126** | **0.7224** |

Gate Zero beats both baselines pooled and in every season —
dev PASS.

## Virgin 2025/2026 (read once, Gate Zero only)

| Arm | LL@9.5 | Calibration actual−pred (SE) |
|---|---|---|
| Gate Zero | **0.6995** | **+3.29pp (2.55pp)** |
| Baselines | naive 0.7194 / league 0.7286 | |

Gate arithmetic: leg (i) 0.6995 ≤ best baseline 0.7194 ✓;
leg (ii) |calibration| = 3.29pp > 1.0pp clean boundary, but
the breach beyond the boundary (3.29 − 1.00 = 2.29pp) is
within 1 SE (2.55pp) → **PROVISIONAL PASS**. The model
under-predicts the virgin's corner rate (mean predicted
over-rate 45.2% vs actual 48.5%): Serie B corners had fallen
for three straight dev seasons (10.13 → 9.00) and the virgin
bounced back to 9.50/match — the fitted state priced the
decline, the season reversed it. That is exactly the regime
the provisional band exists for; it is recorded, not argued
away.

**Ships:** Gate Zero with its virgin-fit parameters
(gamma 0.15, beta_poss 0.0, beta_bc +0.025, NB r 1.1914,
fit_n 1,549) in `engine/corners/fitted_params_virgin.json`,
and `predictions/c_itb_virgin_predictions.csv` (390 rows; FT
ladder 8.5/9.5/10.5; 1H/2H presentation-only via the frozen
0.4734 constant).

## Verification

- Virgin LL@9.5 and calibration recomputed independently from
  the shipped predictions CSV — exact match (0.699528,
  +3.292pp).
- The corners core is the proven J1/ES engine, including the
  coordinator's date-grouped naive correction; the dev harness
  never loads 2025/2026 rows.
