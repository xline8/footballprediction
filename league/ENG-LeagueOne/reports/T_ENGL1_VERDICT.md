# Verdict — T-ENGL1 (ENG-LeagueOne total shots)

**PASS (calibration PROVISIONAL) — arm C (E9 trailing-r) SHIPS.**

Calibration = actual − predicted. Primary line 23.5.

## Dev gate (walk-forward 2022/2023–2024/2025, pooled n=1,671)

| Arm | LL@23.5 | vs league base 0.6953 | vs naive 0.6805 |
|---|---|---|---|
| A (v1 pattern) | 0.6730 | ✓ | ✓ |
| B (v2 level layer) | 0.6728 | ✓ | ✓ |
| C (E9 trailing-r) | 0.6729 | ✓ | ✓ |

All three arms pass the dev gate.

## Virgin (2025/2026, n=557, read ONCE)

| Arm | LL@23.5 | Calibration (act − pred) | SE | Legs |
|---|---|---|---|---|
| A | 0.66583 | +1.47pp | 2.06pp | (i) ✓ (ii) PROVISIONAL |
| B | 0.66552 | +1.75pp | 2.06pp | (iii) ✗ — sign check 1/3 vs A |
| **C** | **0.66581** | +1.58pp | 2.06pp | (i) ✓ (ii) PROVISIONAL (iii) 2/3 ✓ |
| league base rate | 0.69244 | — | — | — |
| naive trailing-10 | 0.67227 | — | — | — |

- B owns the lowest virgin LL but is ineligible: its dev LL beat
  the reference arm A in only 1 of 3 dev seasons (leg iii, frozen).
- A and C both pass; among passing arms the lower pooled virgin LL
  ships: **C 0.665813 < A 0.665830**, a margin of 0.000017 — the
  fourth arm-C win of the program, and the tightest (BR's was
  0.00007, DK's 0.00013). Recorded as measured; the gate is the gate.
- Calibration: all passing arms breach the 1pp clean band but lie
  within 1 SE → PROVISIONAL PASS.

Ships: `engine/total_shots/fitted_params_virgin.json` (arm C) +
`predictions/t_engl1_virgin_predictions.csv` (557 rows, arm C; FT
ladder 22.5/23.5/24.5; 1H/2H presentation-only via frozen shots
constant 0.4551). Coordinator's second-path recompute from the
shipped CSV: LL 0.665813, calibration −1.58pp (pred − actual) —
exact match; the virgin replay after the export fix reproduced
the first read's metrics bit-for-bit.

## Defect found and fixed during this build (presentation layer only)

The ported `write_predictions` fieldnames (carried from the
ENG-Championship file) named FT lines 23.5/24.5/25.5 and half lines
10.5–14.5, while the writer computes the preregistered ladder
(FT 22.5/23.5/24.5; 1H 9.5/10.5/11.5; 2H 11.5/12.5/13.5) — the
first virgin export crashed on the mismatch AFTER
`results_virgin.json` had been written. The fieldnames were aligned
to PREREG_T_ENGL1's Outputs section (no model math touched) and the
export was completed; metrics on replay are identical to the first
read. The same latent mismatch exists in the ENG-Championship
source file — flagged here for the final audit.
