# Verdict — T-BO (Bolivia Primera Division total shots)

**FAIL — all three arms passed the dev gate, read the transitional
virgin, and failed virgin leg (i): every arm loses to the league base
rate on the virgin window. Nothing ships.**

Prereg: `league/BO-PrimeraDivision/prereg/PREREG_T_BO.md` (frozen
ba94d70, before any fitting). Engine: `engine/total_shots/` (T-family
A/B/C port; ridge lambda tuned on the 2025 rows, level cell tuned on
the first dev block).

## Dev gate (pooled, 2025 rounds 11–30 in four expanding 5-round blocks, n=160 scored)

| arm | LL@29.5 |
|---|---|
| A (v1) | 0.687881 |
| B (v2 level layer) | 0.685406 |
| C (E9 trailing-r) | 0.688186 |
| league base rate | 0.698832 |
| naive trailing-10 | 0.692501 |

All three arms beat both baselines ✓ → dev gate PASS for A, B and C.
Per-block LLs (A / B / C): r11-15 0.7138 / 0.7048 / 0.7150; r16-20
0.7103 / 0.7156 / 0.7101; r21-25 0.6679 / 0.6702 / 0.6679; r26-30
0.6595 / 0.6511 / 0.6597. Tuning (frozen protocol, 2025 rows only):
lambda 300.0 — the top of the grid (3/10/30/100/300), so the ridge is
at its boundary; r_A = 87.84; level cell [30.0, 0.5, 20.0]. The
boundary lambda is recorded, not re-tuned — the virgin verdict does
not depend on it.

## Virgin — 2026 regular TRANSITIONAL (n=199 played)

| arm | LL@29.5 | calibration (actual − predicted) | SE |
|---|---|---|---|
| A (v1) | 0.699323 | −1.88pp | 3.57pp |
| B (v2 level layer) | 0.697619 | −1.23pp | 3.57pp |
| C (E9 trailing-r) | 0.698917 | −1.78pp | 3.57pp |
| league base rate (expanding) | **0.696591** | – | – |
| naive trailing-10 | 0.715627 | – | – |

- Leg (i) LL: every arm loses to the league base rate (best arm B by
  0.0010) → **FAIL** for all three arms. The margin is thin, but the
  gate is the gate. The expanding base-rate LL 0.696591 was
  independently recomputed from the CSV with a fresh implementation
  of the tracker — exact match (mean predicted over-rate 52.19%).
  Actual 2026 over-29.5 rate 0.4925 (98/199) vs 2025 base rate 0.5042.
- Leg (ii) calibration: all three arms pass (breaches 1.23–1.88pp are
  within 1pp + 1 SE 3.57pp → provisional territory, not a fail).
- Leg (iii): B and C each beat A in 2 of 4 dev blocks ✓ — moot, leg
  (i) fails.

The season-end confirmatory read of the completed 2026 season remains
outstanding by design (season in progress, rounds 1–25 of 30); it
cannot change this verdict.

## Frozen halves constant

Total shots 1H share **0.4633** (2025 regular, ratio-of-sums; true
variance ≤ 0).
