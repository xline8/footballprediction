# Verdict — C-SCOCH (Scotland Championship corners)

**FAIL at the virgin calibration leg. Nothing ships.**

Prereg: `prereg/PREREG_C_SCOCH.md`. Primary line 9.5, Gate Zero
only (possession-only territorial covariate). Dev n=427 stats
rows, virgin 2025/2026 n=177. All numbers recomputed by the
coordinator from the per-match prediction CSVs. Calibration =
predicted − actual.

## Dev

Pooled LL@9.5 **0.6889**, beating both baselines (league base
rate 0.7435; naive trailing-10 0.7402) — dev gate PASS, the
largest dev margin of any candidate in this league.

## Virgin

- LL@9.5 **0.70644** vs baselines 0.73388 (league) / 0.73551
  (naive) — leg (i) PASS.
- Calibration: mean P(over 9.5) 0.4467 vs actual over-rate
  0.4972 → breach **−5.05pp**, SE 3.80pp. The frozen rule allows
  |breach| ≤ 1.0pp clean, or ≤ 1pp + 1 SE = 4.80pp provisional.
  5.05pp is beyond 1 SE of the boundary — leg (ii) **FAIL**.

The model under-predicted the virgin corner level (virgin corners
ran at 9.54/match with a higher over-9.5 share than the fitted
state expected after the 2024/2025 stats outage, during which 98
matches never updated the state). The gate is mechanical:
**C-SCOCH is FAIL. Nothing ships.**
