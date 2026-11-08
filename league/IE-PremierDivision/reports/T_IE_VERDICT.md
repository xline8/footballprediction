# Verdict — T-IE (Ireland Premier Division total shots) — **FAIL** (virgin legs i + ii)

Prereg: `prereg/PREREG_T_IE.md`. Primary line 24.5. Arms A (v1
pattern), B (v2 level layer), C (E9 trailing-r); tuned
lambda = 300, r_A = 63.53, level cell (30, 1.0, 50).

## Dev (walk-forward, warm-up 2022, scored 2023–2025, n = 540)

| | LL@24.5 |
|---|---|
| B | **0.6702** |
| A | 0.6707 |
| C | 0.6710 |
| Naive trailing-10 | 0.6775 |
| League base rate | 0.6859 |

All three arms pass the dev gate.

## Virgin (2026, n = 180, read ONCE for all three dev-passing arms)

| | LL@24.5 | calib (SE) |
|---|---|---|
| Naive trailing-10 | **0.6074** | +0.28pp (3.41) |
| B | 0.6084 | −5.74pp (3.38) |
| A | 0.6111 | −7.27pp (3.38) |
| C | 0.6130 | −7.63pp (3.38) |
| League base rate | 0.6415 | −9.10pp (3.47) |

- Leg (i): every arm loses to the naive baseline (best arm B by
  0.0010) — FAIL for all arms.
- Leg (ii): every arm's calibration breach (−5.7 to −7.6pp) is
  beyond 1 SE of the 1pp boundary (band ≈ 4.4pp) — FAIL for all
  arms.

2026 was a level-break season for shots: 27.47/match (dev seasons
23.4 → 24.6 → 26.3) and an over-24.5 rate of 68.3% against a dev
rate of 48.7%. The ratings/level arms, anchored to trailing
levels, under-predicted the jump; plain trailing-10 adapted
fastest and still only just won. **FAIL — nothing ships**, no
predictions CSV.
