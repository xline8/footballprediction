# Verdict — C-ENGCH (England Championship corners) — **PROVISIONAL PASS** (Gate Zero ships)

Prereg: `prereg/PREREG_C_ENGCH.md`. Primary line 9.5. Dev n=1,671,
virgin 2025/2026 n=555.

## Dev (pooled LL@9.5; baselines: league 0.7499, naive 0.7437)

| Arm | Dev LL | Dev gate |
|---|---|---|
| Gate Zero (X9) | 0.6884 | PASS |
| X7 (box touches) | 0.6905 | PASS (sign vs GZ 2/3, incl. one exact tie) |

## Virgin 2025/2026

Both arms: LL@9.5 **0.6898** (≤ best baseline 0.7418 — leg (i) ✓);
calibration +1.11pp, SE 2.12pp → breach beyond 1pp by 0.11pp, well
within 1 SE → leg (ii) PROVISIONAL; sign leg ✓. The arms are
numerically identical on the virgin because the fitted territorial
betas are **0.0 in both arms** (gamma 0.15, r 1.1437, beta [0.0, 0.0];
X7's box-touch beta also 0) — the F2 box-touch trait is real
(r=0.841) but worth zero inside this multiplier structure, the same
pattern as C-J1/C-SCO/C-AR. Tie → simpler arm.

**Ships: Gate Zero** (`engine/corners/fitted_params_virgin.json`;
`predictions/c_engch_virgin_predictions.csv`; halves via 0.4638).
Independent check: virgin actual over-9.5 rate from raw CSV =
0.5477 = harness actual exactly; coordinator's own dev re-run was
bit-identical to the builder's results_dev.json.
