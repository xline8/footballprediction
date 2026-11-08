# Verdict — C-CZ (CZ-Liga corners, corners_v3 pattern, Gate Zero only)

**PASS (PROVISIONAL) — Gate Zero ships.**

Dev (pooled, stats-target n = 802, LL@10.5):

| | LL@10.5 | Dev gate |
|---|---|---|
| Gate Zero | **0.695828** | beats both baselines ✓ |
| League base rate | 0.720270 | |
| Naive trailing-10 | 0.713651 | |

Per-season model LL@10.5: 0.701983 / 0.693586 / 0.691841.

Virgin (2025/2026, n = 270):

| | LL@10.5 | Calibration (pp) |
|---|---|---|
| Gate Zero | **0.675211** | +3.06 (SE 2.99) |
| League base rate | 0.676546 | −4.84 |
| Naive trailing-10 | 0.679314 | −6.17 |

Gate arithmetic (PREREG_C_CZ): leg (i) LL@10.5 ≤ best baseline's:
0.675211 ≤ 0.676546 → PASS, by a thin margin (0.001335). Leg (ii)
calibration: |+3.06pp| breaches the 1.0pp boundary; the excess
(2.06pp) is within 1 SE (2.99pp) → PROVISIONAL PASS. Verdict:
**PASS (PROVISIONAL)**; Gate Zero ships. The model over-predicts
the over-10.5 rate in the virgin season (mean P 0.4269 vs actual
0.3963) — recorded plainly; the provisional tag is earned on both
legs' closeness, not just calibration.

Ships: `predictions/c_cz_virgin_predictions.csv` (270 rows, FT
ladder 9.5/10.5/11.5, `halves_share_1h` null — FT-only market) +
`engine/corners/fitted_params_virgin.json` (gamma 0.0, beta 0.0 —
the possession multiplier fitted to zero in the virgin fit;
r = 1.161).

Verification: headline numbers recomputed independently by the
coordinator from the shipped predictions CSV — LL@10.5 0.675211,
calibration +3.06pp, SE 2.99pp, exact match; actuals cross-checked
against the league CSV for all 270 matches. Defect found and fixed
during the build: the copied corners predictions writer still
computed 1H/2H lines from RO's 0.477 constant and crashed on its
own extra fields; it was rewritten FT-only before the virgin read
completed (the virgin metrics were identical across the re-run:
deterministic harness).
