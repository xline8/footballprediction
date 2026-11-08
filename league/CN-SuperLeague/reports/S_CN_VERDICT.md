# Verdict — S-CN (shots on target): **PROVISIONAL PASS** (Gate Zero ships)

Prereg: `prereg/PREREG_S_CN.md` (frozen and committed before fitting).
Primary line 9.5. Era 2023+; warm-up 2023; dev scored 2024+2025
(n = 480); virgin 2026 (n = 240). All numbers recomputed by the
coordinator from the per-match prediction CSVs against the league CSV.

## Dev (per-match walk-forward, predict-then-update)

| Arm | Pooled LL@9.5 | 2024 | 2025 |
|---|---|---|---|
| Gate Zero | 0.6774 | 0.6700 | 0.6848 |
| RS | 0.6784 | 0.6719 | 0.6849 |
| League base rate | 0.7316 | — | — |
| Naive trailing-10 | 0.6801 | — | — |

Dev gate: both arms beat both baselines → both read on the virgin.

## Virgin (2026, read once)

| Arm | LL@9.5 | Mean pred P(over) | Actual over-rate | Calibration (pp) | SE (pp) |
|---|---|---|---|---|---|
| Gate Zero | 0.6667 | 0.4217 | 0.4333 | +1.16 | 3.15 |
| RS | 0.6656 | 0.4208 | 0.4333 | +1.26 | 3.15 |
| League base rate | 0.6843 | — | — | — | — |
| Naive trailing-10 | 0.6798 | — | — | — | — |

## Gate arithmetic

- Leg (i) LL: GZ 0.6667 ≤ best baseline 0.6798 ✓. RS 0.6656 ≤ GZ ✓
  and ≤ baselines ✓.
- Leg (ii) calibration: GZ breach +1.16pp > 1.0pp boundary but within
  1 SE (3.15pp) → PROVISIONAL. RS +1.26pp → PROVISIONAL.
- Leg (iii) sign check (variants only): RS dev LL@9.5 ≤ GZ in 0 of 2
  dev seasons (0.6719 > 0.6700; 0.6849 > 0.6848) → **RS fails leg
  (iii)** and is ineligible despite its marginally lower virgin LL.

Gate Zero is the only eligible arm → **S-CN PROVISIONAL PASS; Gate
Zero ships** (`predictions/s_cn_virgin_predictions.csv`, fitted
params in `engine/sot/fitted_params_virgin.json`; 1H/2H presentation
via the frozen SOT constant 0.4580). The provisional status is a
calibration statement: the model under-predicts the 2026 over-rate
by 1.16pp, inside sampling noise at n = 240.
