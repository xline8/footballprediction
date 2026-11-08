# Verdict — T-CN (total shots): **PROVISIONAL PASS** (Arm B ships)

Prereg: `prereg/PREREG_T_CN.md` (frozen and committed before fitting).
Primary line 26.5. Era 2023+; tuning on warm-up 2023; dev scored
2024+2025 (n = 480); virgin 2026 (n = 240). All numbers recomputed by
the coordinator from the per-match prediction CSVs against the league
CSV (arm LLs and calibrations match the engine JSON exactly; baseline
LLs are taken from the same accumulator output).

Tuning (2023 only): ridge lambda 300, r_A = 57.56, level cell
(hl 60, scale 1.0, k 50).

## Dev

| Arm | Pooled LL@26.5 | 2024 | 2025 |
|---|---|---|---|
| A (v1 pattern) | 0.6778 | 0.6891 | 0.6665 |
| B (v2 level layer) | 0.6749 | 0.6819 | 0.6680 |
| C (E9 trailing-r) | 0.6784 | 0.6898 | 0.6670 |
| League base rate | 0.7099 | — | — |
| Naive trailing-10 | 0.6808 | — | — |

Dev gate: all three arms beat both baselines → all read on the virgin.

## Virgin (2026, read once)

| Arm | LL@26.5 | Calibration (pp) | SE (pp) |
|---|---|---|---|
| A | 0.6566 | +2.69 | 3.11 |
| B | 0.6556 | +3.20 | 3.11 |
| C | 0.6572 | +2.75 | 3.11 |
| League base rate | 0.6961 | — | — |
| Naive trailing-10 | 0.6717 | — | — |

## Gate arithmetic

- Leg (i) LL vs reference arm A and best baseline (0.6717): A ✓;
  B 0.6556 ≤ A ✓; C 0.6572 > A 0.6566 → **C fails leg (i)**.
- Leg (ii) calibration: A +2.69pp, B +3.20pp — both breaches are
  beyond the 1.0pp clean boundary but within 1 SE (3.11pp) →
  PROVISIONAL for both.
- Leg (iii) sign check (variants): B dev LL ≤ A in 2024
  (0.6819 < 0.6891) → ≥1 of 2 ✓.
- Both-pass rule: among eligible arms (A, B) the lower virgin LL
  ships → **Arm B**.

**T-CN PROVISIONAL PASS; Arm B (v2 level layer) ships**
(`predictions/t_cn_virgin_predictions.csv` — virgin rows only, 240;
fitted params in `engine/total_shots/fitted_params_virgin.json`;
1H/2H presentation via the frozen total-shots constant 0.4594).

Note: the exported virgin predictions file was initially written
with dev-season rows included (a defect inherited from the TH
runner's export); it was trimmed to the 240 virgin rows with values
unchanged, and the CN runner now filters on export.
