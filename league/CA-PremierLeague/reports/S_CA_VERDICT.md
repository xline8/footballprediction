# Verdict — S-CA (CA-PremierLeague shots on target, v5 pattern)

**FAIL — both arms pass dev and pass virgin calibration cleanly,
but both fail virgin leg (i): the league base rate beats them.**

Dev (pooled, stats-target n = 336, LL@7.5):

| Arm | LL@7.5 | vs base 0.698400 | vs naive 0.688758 | Dev gate |
|---|---|---|---|---|
| Gate Zero | 0.688126 | ✓ | ✓ | PASS |
| RS | 0.687384 | ✓ | ✓ | PASS |

RS per-season LL@7.5 vs Gate Zero: 0.696157 < 0.696254 ✓;
0.691685 < 0.693467 ✓; 0.674311 < 0.674657 ✓ → sign check 3 of 3
→ both arms were read on the virgin window.

Virgin (2025, n = 112), both arms:

| | LL@7.5 | Calibration (pp) |
|---|---|---|
| Gate Zero | 0.686156 | −0.29 (SE 4.71) |
| RS | 0.685119 | −0.34 (SE 4.71) |
| League base rate | **0.680771** | −4.24 |
| Naive trailing-10 | 0.698682 | +1.15 |

Gate arithmetic (PREREG_S_CA): leg (ii) calibration is a CLEAN
pass for both arms (|−0.29pp| and |−0.34pp| ≤ 1.0pp). Leg (i)
requires LL ≤ Gate Zero's AND ≤ the best baseline's: RS beats
Gate Zero (0.685119 ≤ 0.686156 ✓) but neither arm beats the
league base rate (0.680771) — Gate Zero 0.686156 ✗, RS 0.685119
✗. Leg (i) fails for both arms → verdict FAIL, nothing ships.

Context, stated plainly: 2025 was a high-SOT season (actual
over-7.5 rate 0.5893 vs the 2021–2024 pooled rate 0.5469 the base
rate carries). The constant base rate happened to sit closer to
the season's centre than the walk-forward's team-level estimates
at n = 112; the models were better calibrated but less sharp.
The dev margin over naive was already thin (0.0006 for Gate
Zero) — this candidate was borderline at dev and the virgin
window settled it against the model.

Verification: headline numbers recomputed independently by the
coordinator from the per-match virgin CSVs (LL@7.5, calibration
and SE match to 3+ decimals for both arms); the base-rate LL was
recomputed from the league CSV (rate 0.546875 over 448 prior
matches → LL 0.680771, exact).

Ships: nothing. Virgin read: YES (both dev-passing arms, once).
