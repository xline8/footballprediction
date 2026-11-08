# Verdict — S-EG (Egypt Premier League shots on target) — **FAIL** (virgin calibration leg, beyond 1 SE)

Prereg: `prereg/PREREG_S_EG.md` (frozen 6b86220, before fitting).
Dev = per-match walk-forward, warm-up 2021/2022, scored
2022/2023–2024/2025 (n = 826 with target). Virgin = 2025/2026
(n = 322), read once. Primary line 6.5. Calibration = actual −
predicted, as frozen.

## Dev (pooled LL@6.5)

| Arm | Pooled | 2022/2023 | 2023/2024 | 2024/2025 | vs baselines (league 0.6893 / naive 0.6951) |
|---|---|---|---|---|---|
| Gate Zero | 0.6844 | 0.6970 | 0.6684 | 0.6892 | beats both — PASS |
| RS | 0.6843 | 0.6963 | 0.6686 | 0.6895 | beats both — PASS |

(Baseline LLs independently recomputed from the raw CSV by the
coordinator: 0.6896 / 0.6774 / 0.7052 per season — exact match.)

RS's dev sign check vs Gate Zero is 1 of 3 seasons (better only in
2022/2023), below the frozen ≥2-of-3 for leg (iii). The harness
(applied as in the SA reference) therefore did not read RS on the
virgin; the outcome is invariant to that choice, because leg (iii)
is a pass condition and RS fails it on dev evidence alone.

## Virgin 2025/2026 (n = 322) — Gate Zero only

| Arm | LL@6.5 | Calibration actual − predicted (SE) |
|---|---|---|
| Gate Zero | 0.6777 | **+5.47pp (2.73pp)** |
| League base rate | 0.6822 | — |
| Naive trailing-10 | 0.6909 | — |

Gate arithmetic: leg (i) — GZ 0.6777 ≤ best baseline 0.6822 ✓.
Leg (ii) — calibration breach is 5.47pp against the 1.0pp
boundary; 1 SE is 2.73pp, so the breach lies **beyond** 1 SE of
the boundary (5.47 > 1.0 + 2.73) → FAIL, not provisional. The
virgin season's SOT came in hot (actual over-6.5 rate 57.8%,
mean SOT 6.89 with a higher over-share than the dev era's
distribution implied) while the model predicted 52.3% — a level
miss the LL leg alone would have forgiven.

**Ships: nothing.** No fitted params or predictions were written
for S-EG. S-EG is a complete FAIL.
