# Verdict — S-BO (Bolivia Primera Division shots on target)

**FAIL — both arms passed the dev gate, read the transitional virgin,
and failed virgin leg (ii) calibration. Nothing ships.**

Prereg: `league/BO-PrimeraDivision/prereg/PREREG_S_BO.md` (frozen
ba94d70, before any fitting). Engine: `engine/sot/` (production v5 port;
NB r=79.94 frozen, ratio prior 200 for GZ, 20,000 for RS).

## Dev gate (pooled, 2025 rounds 11–30 in four expanding 5-round blocks, n=160 scored)

| arm | LL@11.5 |
|---|---|
| Gate Zero | 0.685669 |
| RS | 0.686559 |
| league base rate | 0.691716 |
| naive trailing-10 | 0.701864 |

Both arms beat both baselines ✓ → dev gate PASS for GZ and RS. Per-block
GZ LLs: r11-15 0.6702, r16-20 0.6211, r21-25 0.7388, r26-30 0.7126. RS
beats GZ in 3 of 4 blocks (sign leg (iii) met). The league base rate is
the expanding pooled over-rate over all prior 2025 rows (seed included) —
the PY harness computed it over scored rows only, which gives q=0 for
the first block and an inflated LL of 1.0335; that defect is fixed here
and the corrected 0.691716 was independently recomputed from the CSV.

## Virgin — 2026 regular TRANSITIONAL (n=199 played)

| arm | LL@11.5 | calibration (actual − predicted) | SE |
|---|---|---|---|
| Gate Zero | 0.641409 | **−4.93pp** | 3.35pp |
| RS | 0.641045 | **−4.85pp** | 3.35pp |
| league base rate (2025 rate 0.45) | 0.670441 | – | – |
| naive trailing-10 | 0.656793 | – | – |

- Leg (i) LL: both arms ≤ Gate Zero and ≤ both baselines ✓ (RS lowest).
- Leg (ii) calibration: |−4.93pp| vs the frozen boundary 1.0pp + 1 SE
  3.35pp = 4.35pp → **breach exceeds the provisional band by 0.58pp
  (GZ) / 0.50pp (RS) → FAIL** for both arms. The model over-predicts:
  actual over-11.5 rate 0.3618 vs predicted 0.4111 (GZ). The 2026 SOT
  level dropped (mean 10.487 vs 2025 11.325), and the 2025-trained
  ratings did not follow it down.
- Leg (iii): RS beats GZ in 3 of 4 dev blocks ✓ — moot, leg (ii) fails.
- Base-rate LL 0.670441 independently recomputed from the CSV (2025
  rate 0.45, 2026 actual over-rate 0.3618) — exact match.

The season-end confirmatory read of the completed 2026 season remains
outstanding by design (season in progress, rounds 1–25 of 30); it
cannot change this verdict.

## Frozen halves constant

SOT 1H share **0.4555** (2025 regular, ratio-of-sums; true variance ≤ 0).
