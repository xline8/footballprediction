# Verdict — S-RU (RU-Premier League shots on target)

**PASS (PROVISIONAL — calibration leg). Gate Zero ships.**

Prereg: `prereg/PREREG_S_RU.md`. Primary line 8.5. All numbers
recomputed by the coordinator from the per-match CSVs and match
`results_dev.json` / `results_virgin.json`.

## Dev (n = 720, LL @ 8.5)

| arm | pooled | 2022/2023 | 2023/2024 | 2024/2025 |
|---|---|---|---|---|
| Gate Zero | 0.6692 | 0.6588 | 0.6690 | 0.6797 |
| RS | 0.6694 | 0.6581 | 0.6695 | 0.6805 |
| league base rate | 0.6921 | | | |
| naive trailing-10 | 0.6756 | | | |

Dev gate: both arms beat both baselines — both pass. RS sign check
vs Gate Zero (leg iii): better in 1 of 3 dev seasons — RS fails
leg (iii) on frozen dev numbers and could never ship.

## Virgin (2025/2026, n = 240, read once)

Gate Zero: LL @ 8.5 = **0.6588**; baselines: naive 0.6649, league
base 0.7066. Leg (i): 0.6588 ≤ 0.6649 PASS. Leg (ii): actual
over-8.5 rate 0.4292, mean predicted 0.4698, calibration
(actual − predicted) = **−4.07 pp**, SE 3.11 pp. |breach| > 1 pp,
but the excess beyond the boundary (3.07 pp) is within 1 SE
(3.11 pp) → **PROVISIONAL PASS**.

Recorded protocol deviation: the ported PL virgin harness read
only Gate Zero (`scored_arms: ["GZ"]`); RS's virgin was not read
because the harness's internal gate required a variant to beat
Gate Zero's pooled dev LL. The deviation is outcome-neutral: RS
already fails leg (iii) (1 of 3 dev seasons), so no virgin result
could have shipped it. The virgin season was a low-SOT season
(7.97 SOT/match vs 8.83–9.45 in dev), which is what pushed the
calibration to the provisional boundary.

## What ships

Gate Zero (production v5 pattern unmodified), fitted params in
`engine/sot/fitted_params_virgin.json`; virgin predictions in
`predictions/s_ru_virgin_predictions.csv` (FT ladder 7.5/8.5/9.5;
1H/2H presentation-only via the frozen SOT constant 0.4612,
NB r = 79.94).
