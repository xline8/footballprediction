# S-CH verdict — PASS (calibration PROVISIONAL) — RS SHIPS

Prereg: `prereg/PREREG_S_CH.md` (frozen ccf74a9, before fitting).
Primary line 9.5. Dev pooled n = 636; virgin 2025/2026 n = 228,
read once, for both dev-passing arms. Arms: Gate Zero + RS only
(X4 dropped on reliability, EDA F6 r=0.247; X6 dropped, F7).

## Dev results — pooled LL@9.5

| Arm / baseline | LL@9.5 |
|---|---|
| Gate Zero | 0.6863 |
| RS (BB prior 20,000) | 0.6858 |
| League base rate | 0.6915 |
| Naive trailing-10 | 0.6973 |

Both arms beat both baselines → both pass the dev gate. RS
per-season sign check vs Gate Zero: 0.6644 > 0.6637 (2022/2023),
0.6959 ≤ 0.6971, 0.6926 ≤ 0.6933 → 2/3.

## Virgin results (2025/2026, n = 228)

| Arm / baseline | LL@9.5 | Calibration (mean P − actual) |
|---|---|---|
| Gate Zero | 0.6860 | −3.77pp (SE 3.29pp) |
| RS | 0.6853 | −3.76pp (SE 3.28pp) |
| League base rate | 0.7010 | — |
| Naive trailing-10 | 0.6933 | — |

## Gate arithmetic

- Leg (i): RS 0.6853 ≤ Gate Zero 0.6860 and ≤ best baseline 0.6933.
  PASS. Gate Zero also ≤ both baselines.
- Leg (ii): both arms breach the 1.0pp boundary by ~2.8pp, within
  1 SE (~3.3pp) → **PROVISIONAL PASS** for both. The virgin season
  ran hot on SOT (9.87/match vs dev 9.37); both arms under-predicted
  the over-rate by the same margin.
- Leg (iii): RS sign check 2/3 (above).
- Both arms pass; the both-pass rule ships the lower pooled virgin
  LL: **RS** (0.6853 < 0.6860 — a 0.0007 margin, recorded as such).

**Ships:** RS (v5 pattern with the ratio-shrink prior P = 20,000),
fitted parameters in `engine/sot/fitted_params_virgin.json`, virgin
predictions in `predictions/s_ch_virgin_predictions.csv` (228 rows;
FT ladder + 1H/2H via the frozen SOT constant 0.453). **CH joins
the daily runner with SOT.** Coordinator verification: virgin
LL@9.5 recomputed from the shipped predictions CSV = 0.6853,
matching the results JSON.
