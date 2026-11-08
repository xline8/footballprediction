# Verdict — S-ENGL1 (ENG-LeagueOne shots on target)

**PASS (calibration PROVISIONAL) — Gate Zero SHIPS.**

Calibration = actual − predicted. Primary line 7.5.

## Dev gate (walk-forward 2022/2023–2024/2025, pooled n=1,671)

| Arm | LL@7.5 | vs league base 0.6917 | vs naive 0.6837 |
|---|---|---|---|
| Gate Zero | 0.6784 | ✓ | ✓ |
| RS | 0.6781 | ✓ | ✓ |
| X4 | 0.6800 | ✓ | ✓ |

All three arms pass the dev gate.

## Virgin (2025/2026, n=557, read ONCE)

| Arm | LL@7.5 | Calibration (act − pred) | SE | Legs |
|---|---|---|---|---|
| **Gate Zero** | **0.6909** | −1.68pp | 2.11pp | (i) ✓ (ii) PROVISIONAL |
| RS | 0.6913 | −1.75pp | 2.11pp | (i) ✗ — 0.6913 > Gate Zero 0.6909 |
| league base rate | 0.6981 | −4.98pp | — | — |
| naive trailing-10 | 0.7080 | +1.43pp | — | — |

- Leg (i): Gate Zero's LL ≤ its own and ≤ best baseline (0.6981) ✓.
- Leg (ii): |−1.68pp| breaches the 1pp clean band but the breach
  (0.68pp) is within 1 SE (2.11pp) → **PROVISIONAL PASS**.
- X4 was NOT virgin-read: the reference harness applies the leg
  (iii) per-season sign check as a read filter, and X4's dev LL
  beat Gate Zero in only 1 of 3 dev seasons (0.6816 ≤ 0.6820 in
  2022/2023; worse in 2023/2024 and 2024/2025). This is the
  ENG-Championship harness's carried mechanical reading, recorded
  here plainly: under the prereg text X4 had passed the dev gate;
  its exclusion rests on leg (iii), applied early. RS's sign check
  was 3/3, so RS was read and failed leg (i) on the virgin itself.
- Both-pass rule moot (only Gate Zero passes). **Gate Zero ships.**

Ships: `engine/sot/fitted_params_virgin.json` (arm GZ) +
`predictions/s_engl1_virgin_predictions.csv` (557 rows; FT ladder
6.5/7.5/8.5; 1H/2H presentation-only via frozen SOT constant
0.4414). Coordinator's second-path recompute from the shipped CSV:
LL 0.690926, calibration +1.68pp (pred − actual) — exact match.
