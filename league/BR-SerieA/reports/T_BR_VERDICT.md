# T-BR verdict — PASS (calibration PROVISIONAL) — arm C (E9) SHIPS

Prereg: `prereg/PREREG_T_BR.md` (frozen 7056902, before fitting).
Primary line 26.5. Dev pooled n = 1,140; virgin 2025 n = 380, read
once for all three dev-passing arms.

## Dev results — pooled LL@26.5

| Arm / baseline | LL@26.5 | Per-season (2022, 2023, 2024) |
|---|---|---|
| A (v1 pattern) | 0.676118 | 0.676188 / 0.688596 / 0.663571 |
| B (v2 level layer) | 0.674877 | 0.670254 / 0.689393 / 0.664984 |
| C (E9 trailing-r) | 0.676030 | 0.676585 / 0.688299 / 0.663205 |
| League base rate | 0.697826 | — |
| Naive trailing-10 | 0.684003 | — |

All three arms beat both baselines → all pass the dev gate.

## Virgin results (2025, n = 380)

| Arm / baseline | LL@26.5 | Calibration (pp) |
|---|---|---|
| A | 0.689921 | +2.02 (SE 2.55) |
| B | 0.691163 | +0.71 (SE 2.56) |
| C | **0.689848** | +1.99 (SE 2.55) |
| League base rate | 0.693533 | +4.28 |
| Naive trailing-10 | 0.700525 | +1.33 |

## Gate arithmetic

- Reference arm = A (passed dev). Leg (i): virgin LL ≤ A's **and**
  ≤ best baseline (0.693533). A: PASS (trivially vs itself;
  0.689921 ≤ 0.693533). B: **FAIL** (0.691163 > A's 0.689921 —
  despite B's clean calibration and best dev LL; the frozen legs
  are applied as written). C: PASS (0.689848 ≤ 0.689921 and
  ≤ 0.693533).
- Leg (ii): A and C both breach the 1.0pp boundary (~2.0pp) but
  each breach is within 1 SE (2.55pp) → PROVISIONAL PASS for
  both. (2025 ran cold on shots — 26.12/match vs the dev era's
  ~27 — and every arm over-predicted the over-rate alike.)
- Leg (iii) sign check vs A on dev: C ≤ A in 2023 and 2024, worse
  in 2022 (0.676585 > 0.676188) → 2/3, PASS. B: 1/3, FAIL
  (consistent with its leg (i) failure).
- Passing arms: A and C. Both-pass rule: lower pooled virgin LL
  ships → **C (0.689848 < 0.689921)**.

**Ships:** arm C — the E9 mechanism (NB r from the trailing
200-match window) on the v1 pattern; fitted parameters in
`engine/total_shots/fitted_params_virgin.json` (λ = 300,
r_A = 96.04, level cell [120, 1.0, 20]); virgin predictions in
`predictions/t_br_virgin_predictions.csv` (380 rows, arm "C";
FT ladder 25.5/26.5/27.5 + 1H/2H via the frozen shots constant
0.463). **BR joins the daily runner with total shots (arm C).**
This replicates DK exactly — arm C winning by a hair (there
0.00013 LL, here 0.00007) — and the verdict records, as DK's did,
that A was effectively tied. Coordinator verification: virgin
LL@26.5 recomputed from the shipped predictions CSV = 0.689848,
matching the results JSON to 6dp.
