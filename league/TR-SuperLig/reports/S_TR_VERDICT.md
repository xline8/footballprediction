# S-TR verdict — PROVISIONAL PASS (Gate Zero ships)

Prereg: `prereg/PREREG_S_TR.md` (frozen 06ad8d8, before fitting).
Primary line **8.5** (dev over-rate 0.527). Source JSONs:
`engine/sot/results_dev.json`, `engine/sot/results_virgin.json`.
No 2026/2027 rows were read.

Protocol correction (coordinator verification): the first builder run
scored the 2021/2022 warm-up season into the dev pool (n = 1,413),
contrary to the prereg's "Warm-up: 2021/2022 updates state, never
scored." The harness was fixed and dev rerun on the frozen scored
window 2022/2023–2024/2025 (n = 1,033); the corrected numbers below
were independently recomputed from the per-season values and match
the rerun exactly. The virgin state evolution is unaffected by the
scoring window, so the single virgin read stands.

## Dev results — pooled LL@8.5 (n = 1,033)

| arm | dev pooled LL@8.5 | league base | naive trailing-10 | dev gate | sign leg vs GZ (≥2/3) |
|---|---:|---:|---:|---|---|
| Gate Zero | 0.684831 | 0.692831 | 0.698833 | PASS | — |
| RS | 0.684922 | 0.692831 | 0.698833 | PASS | **FAIL** (better in 1/3 seasons) |
| X4 | 0.687828 | 0.692831 | 0.698833 | PASS | **FAIL** (better in 0/3 seasons) |

All three arms beat both baselines on pooled LL, but under the frozen
mechanical reading a variant must also win the sign leg; RS and X4 do
not, so only Gate Zero was virgin-read in the corrected run
(`read_arms` = ["GZ"]). RS's virgin numbers from the first,
off-protocol run (LL 0.678641, breach +1.089pp) cannot ship and are
disregarded; X4 was never virgin-read.

## Virgin results (2025/2026, n = 306, read once)

| arm | virgin LL@8.5 | calibration breach / SE | result |
|---|---:|---|---|
| Gate Zero | 0.677976 | +1.042pp / 2.819pp | PROVISIONAL PASS (breach within 1 SE of the 1.0pp boundary) |
| league base | 0.696773 | — | baseline |
| naive trailing-10 | 0.695087 | — | baseline |

Virgin leg (i): Gate Zero LL ≤ best baseline ✓. Leg (ii):
PROVISIONAL as above. **Gate Zero ships.**

Shipped fitted params: `engine/sot/fitted_params_virgin.json` (GZ;
NB r = 79.94 frozen). Predictions:
`predictions/s_tr_virgin_predictions.csv` (306 rows; FT ladder
7.5/8.5/9.5; 1H/2H presentation-only via frozen SOT constant 0.4435).
X6 (xGOT) was not an arm: population 33.5–40.9% of shots before
2024/2025 and era reliability r ≈ 0.26–0.30 (FEATURES). X4 is
era-guarded from 2022/2023 with Gate Zero fallback where shot-map
quality is missing.
