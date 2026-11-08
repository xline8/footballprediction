# Verdict — C-SCO (Scotland Premiership corners) — **PROVISIONAL PASS** (Gate Zero ships)

Prereg: `prereg/PREREG_C_SCO.md`. Primary line 10.5. Dev n=684,
virgin 2025/2026 n=228.

## Dev (pooled LL@10.5; baselines: league 0.7286, naive 0.7251)
| Arm | Dev LL | Dev gate |
|---|---|---|
| Gate Zero (X9) | 0.6978 | PASS |
| X7 (box touches) | 0.6926 | PASS |

## Virgin 2025/2026
Both arms: LL@10.5 **0.6954** (≤ best baseline 0.7037 — leg (i) ✓);
calibration +2.43pp, SE 3.30pp → within 1 SE → leg (ii)
PROVISIONAL; sign leg ✓. The arms are numerically identical on the
virgin because the fitted X7 box-touch beta is **0.0** (gamma 0.15,
r 1.2327, beta [0.0]) — the territorial term carries no weight as
fitted, the same pattern the AR join documented. Tie → simpler arm.

**Ships: Gate Zero** (`engine/corners/fitted_params_virgin.json`;
`predictions/c_sco_virgin_predictions.csv`; halves via 0.4704).
Independent check: virgin actual over-10.5 rate from raw CSV =
0.4561 = harness actual exactly.
