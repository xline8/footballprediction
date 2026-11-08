# T-DK verdict — PASS (calibration PROVISIONAL) — arm C (E9) SHIPS

Prereg: `prereg/PREREG_T_DK.md` (frozen 6a0240b, before fitting).
Primary line 25.5. Dev pooled n = 579; virgin 2025/2026 n = 193,
read once for all three dev-passing arms.

## Dev results — pooled LL@25.5

| Arm / baseline | LL@25.5 | Per-season (22/23, 23/24, 24/25) |
|---|---|---|
| A (v1 pattern) | 0.6703 | 0.6696 / 0.6668 / 0.6746 |
| B (v2 level layer) | 0.6710 | 0.6709 / 0.6671 / 0.6750 |
| C (E9 trailing-r) | 0.6703 | 0.6693 / 0.6668 / 0.6747 |
| League base rate | 0.6934 | — |
| Naive trailing-10 | 0.6782 | — |

All three arms beat both baselines → all pass the dev gate.

## Virgin results (2025/2026, n = 193)

| Arm / baseline | LL@25.5 | Calibration (pp) |
|---|---|---|
| A | 0.68643 | −2.87 (SE 3.57) |
| B | 0.68677 | −2.45 (SE 3.57) |
| C | **0.68630** | −2.94 (SE 3.57) |
| League base rate | 0.69000 | −4.70 |
| Naive trailing-10 | 0.69178 | −0.81 |

## Gate arithmetic

- Reference arm = A (passed dev). Leg (i): virgin LL ≤ reference
  A's **and** ≤ best baseline (0.69000). A: PASS (trivially vs
  itself; 0.68643 ≤ 0.69000). B: **FAIL** (0.68677 > A's 0.68643).
  C: PASS (0.68630 ≤ 0.68643 and ≤ 0.69000).
- Leg (ii): all three arms breach the 1.0pp boundary (2.45–2.94pp)
  but each breach is within 1 SE (3.57pp) → PROVISIONAL PASS for
  A and C (B already out on leg (i)).
- Leg (iii) sign check vs A on dev: C ≤ A in 2022/2023 (0.6693 ≤
  0.6696) and 2023/2024 (equal), worse in 2024/2025 (0.6747 >
  0.6746) → 2/3, PASS. B: 0/3, FAIL (consistent with its leg (i)
  failure).
- Passing arms: A and C. Both-pass rule: lower pooled virgin LL
  ships → **C (0.68630 < 0.68643)**.

**Ships:** arm C — the E9 mechanism (NB r from the trailing
window) on the v1 pattern; fitted parameters in
`engine/total_shots/fitted_params_virgin.json` (r_A = 100.985,
level cell [120, 0.5, 50]); virgin predictions in
`predictions/t_dk_virgin_predictions.csv` (193 rows, arm column
"C"; FT ladder + 1H/2H via the frozen shots constant 0.470).
**DK joins the daily runner with total shots (arm C).** Note the
margin over A is 0.00013 LL — the frozen rule ships C, and the
verdict records that A was effectively tied. Coordinator
verification: dev rerun reproduced pooled LLs; virgin LL@25.5
recomputed from the shipped predictions CSV = 0.686304, matching
the results JSON to 6dp.
