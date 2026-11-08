# Verdict — K-MXE (Liga de Expansión MX cards) — **FAIL (virgin LL leg)**

Prereg: `prereg/PREREG_K_MXE.md` (frozen before any fitting).
Target: unified event yellows (Yellow + YellowRed). Corpus: clean
era only — warm-up 2023/2024 - Apertura (n=105, unscored, r
estimated there: model 37.31 / base 23.74 / naive 47.21); dev
scored online walk-forward over 4 blocks (n=420); virgin =
2025/2026 - Clausura (n=105), read once because the dev gate
passed. Primary line 5.5 (dev over-rate 0.421, nearest the
median). All headline numbers were recomputed independently with
a fresh implementation of the preregistered pattern and match
the engine to 4 decimals (r values identical).

## Dev results (pooled, n=420, LL at primary line 5.5)

| Method | LL @5.5 |
|---|---|
| Model (Gate Zero) | **0.6784** |
| Base rate | 0.6803 |
| Naive trailing-10 | 0.6877 |

Dev gate: model beats BOTH baselines → PASS, by a thin margin
over base (−0.0019). Per block, the model beats base in 3 of 4
blocks (loses 2024/2025 - Apertura, 0.6661 vs 0.6548) and beats
naive in 3 of 4 (loses 2025/2026 - Apertura, 0.7265 vs 0.6987 —
the block where the yellow level jumped to 5.84/match and the
trailing naive adapted fastest).

## Virgin results (n=105, read once, LL at 5.5)

| Method | LL @5.5 | Mean p (over 5.5) | Actual | Calib |
|---|---|---|---|---|
| Model | 0.6953 | 0.4519 | 0.4190 | −3.28pp (SE 4.90) |
| Base | **0.6823** | 0.4500 | 0.4190 | −3.10pp |
| Naive | 0.7140 | 0.4950 | 0.4190 | −7.60pp |

## Gate arithmetic (mechanical, per the frozen prereg)

- (i) LL leg: model 0.6953 > base 0.6823 → **FAIL**. The team
  ratings add nothing over the decayed league mean on the virgin
  block; the virgin yellow level fell (5.51/match in the block,
  over-5.5 rate 0.419 vs dev 0.421 predicted 0.452) and the flat
  base tracked it as well as the model.
- (ii) Calibration leg: |−3.28pp| > 1.0pp but ≤ 1.0 + 4.90 →
  PROVISIONAL on its own. Moot: leg (i) already failed.

## What ships

Nothing. No fitted params, no predictions CSV. K-MXE = FAIL.
