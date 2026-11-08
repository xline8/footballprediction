# Verdict — T-ITB (Italy Serie B total shots) — **PASS** (clean; arm A ships)

Prereg: `prereg/PREREG_T_ITB.md` (frozen 369a3a7, before
fitting). Primary line 25.5. Tuning season 2022/2023 (reported,
never judges); dev gate pool 2023/2024–2024/2025 (n=779);
virgin 2025/2026 (n=390). **Calibration = actual − predicted**
(pp). Tuning outcome (2022/2023 only): ridge lambda **300**,
r_A **123.52**, level-layer cell (HL 30, s 0.5, K 50),
M̄ = 25.6 frozen.

## Dev gate pool (LL@25.5; baselines: league 0.6939, naive 0.6828)

| Arm | 2023/2024 | 2024/2025 | Pooled | Dev outcome |
|---|---|---|---|---|
| A (v1 pattern) | 0.6820 | 0.6696 | **0.6758** | PASS |
| B (v2 level layer) | 0.6833 | 0.6706 | 0.6769 | PASS |
| C (E9 trailing-r) | 0.6819 | 0.6700 | 0.6760 | PASS |
| League base rate | 0.6936 | 0.6941 | 0.6939 | |
| Naive trailing-10 | 0.6905 | 0.6751 | 0.6828 | |

All three arms beat both baselines pooled — dev PASS for all.

## Virgin 2025/2026 (all three arms, per the frozen rule)

| Arm | LL@25.5 | Calibration (SE) | Legs |
|---|---|---|---|
| A | **0.6666** | **+0.81pp (2.47pp)** | (i) ✓ (ii) **clean** |
| B | 0.6667 | +0.31pp (2.47pp) | **(i) ✗ — above reference arm A**; sign check 0/2 also ✗ |
| C | 0.6670 | +1.04pp (2.47pp) | **(i) ✗ — above reference arm A** (its (ii) would have been provisional; sign 1/2 ✓) |
| Baselines | naive 0.6732 / league 0.6931 | | |

Gate arithmetic: arm A is the reference (it passed dev).
Leg (i) requires virgin LL ≤ A's **and** ≤ the best baseline
(0.6732): A passes trivially on the first clause and beats
the naive by 0.0066; B and C both sit above A (by 0.0002 and
0.0004 — close, but the leg is mechanical). Leg (ii) for A:
|0.81pp| ≤ 1.0pp → **clean PASS**, the only clean calibration
in this league's build. B's level layer and C's trailing-r —
the two mechanisms that define the family's top-5 history —
add nothing on this corpus: the virgin ran hot on shots
(26.10/match vs dev ≈25.6) and plain arm A tracked it best.

**Ships:** arm A with fitted params (lambda 300, r_A 123.52)
in `engine/total_shots/fitted_params_virgin.json`, and
`predictions/t_itb_virgin_predictions.csv` (390 rows; FT
ladder 24.5/25.5/26.5; 1H/2H presentation-only via the frozen
0.4650 constant).

## Verification and one defect, stated plainly

- Virgin LL@25.5 and calibration recomputed independently
  from the shipped predictions CSV — exact match (0.666584,
  +0.810pp).
- Defect in the build (mine, not the data's): the first
  virgin run crashed in the predictions writer — a stale
  field-name list (`p_over_22_5/23_5` strings survived the
  line change because they use underscores) — **after** the
  virgin metrics had been computed and saved to
  `results_virgin.json`. The writer was fixed and the
  identical frozen computation re-run to complete the export;
  no number changed, nothing was re-tuned, and the metrics
  file from the first run matches the second. The virgin was
  read once for judging; the rerun was output plumbing.
