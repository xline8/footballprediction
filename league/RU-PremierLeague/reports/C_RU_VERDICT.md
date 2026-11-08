# Verdict — C-RU (RU-Premier League corners)

**FAIL. Nothing ships.**

Prereg: `prereg/PREREG_C_RU.md`. Primary line 9.5. All numbers
recomputed by the coordinator from the per-match CSVs and match
the engine JSONs.

## Dev (n = 720, LL @ 9.5)

| arm | pooled | 2022/2023 | 2023/2024 | 2024/2025 |
|---|---|---|---|---|
| Gate Zero (X9) | 0.6973 | 0.7081 | 0.6945 | 0.6894 |
| X7 (box touches) | 0.6943 | 0.6932 | 0.6967 | 0.6931 |
| league base rate | 0.7333 | | | |
| naive trailing-10 | 0.7288 | | | |

Dev gate: both arms beat both baselines — both pass. X7 sign check
vs Gate Zero (leg iii): better in 1 of 3 dev seasons.

Note on X7 mechanics: the per-season grid fit selected
beta_bt = 0 in every dev season and again in the virgin fit, so
the X7 arm never actually applied a box-touch multiplier — its
predictions are the plain core without the X9 territorial
multiplier. Its dev/virgin edges over Gate Zero are the value of
*dropping* the X9 multiplier in this league, not of box touches.

## Virgin (2025/2026, n = 240, read once)

| arm | LL @ 9.5 | calibration | SE |
|---|---|---|---|
| Gate Zero | 0.7008 | −2.02 pp | 3.26 pp |
| X7 | 0.6898 | −2.04 pp | 3.22 pp |
| league base rate | 0.6988 | | |
| naive trailing-10 | 0.7055 | | |

Gate arithmetic. Gate Zero leg (i): 0.7008 ≤ best baseline 0.6988?
**No — FAIL** (by 0.0020). X7 leg (i): 0.6898 ≤ 0.7008 and ≤
0.6988 PASS; leg (ii): excess 1.04 pp ≤ SE 3.22 → provisional
PASS; leg (iii): dev sign check 1 of 3 — **FAIL**. No arm passes
all legs: Gate Zero fails (i), X7 fails (iii). Verdict FAIL,
nothing ships. Fitted virgin params remain in
`engine/corners/fitted_params_virgin.json` for the record.
