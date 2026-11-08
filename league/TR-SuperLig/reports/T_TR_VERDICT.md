# T-TR verdict

Source JSONs: `engine/total_shots/results_dev.json` and `engine/total_shots/results_virgin.json`. Dev loaded 1,413 rows (2021/2022 seed + tuning season 2022/2023) with the gate pool scored on 2022/2023–2024/2025 (n = 1,033, as in the dev JSON's `protocol.gate_pool`); virgin scored 306 rows in 2025/2026. No 2026/2027 rows were read. (The first builder run mislabelled the gate pool as all four seasons in the protocol block; the pooled metrics were always the 1,033-row pool — verified by coordinator recompute and a rerun with the corrected label, numbers identical.)

| arm | dev pooled LL@25.5 | dev gate | virgin LL@25.5 | calibration breach / SE |
|---|---:|---|---:|---:|
| A | 0.661411 | PASS | 0.643136 | −0.844pp / 2.699pp |
| B | 0.660752 | PASS | 0.644155 | −0.895pp / 2.703pp |
| C | 0.661831 | PASS | 0.644840 | −1.430pp / 2.702pp |
| league base | 0.692591 | baseline | 0.693485 | +1.968pp / 2.836pp |
| naive trailing-10 | 0.671477 | baseline | 0.651598 | +0.953pp / 2.742pp |

All three arms beat both dev baselines. Virgin LL and calibration legs pass for all arms (A and B clean calibration; C provisional). The reference arm A has the lowest passing virgin LL and ships; variant sign checks are recorded in the persisted dev metrics. Fitted params: `engine/total_shots/fitted_params.json` (lambda=100, r_A=131.056201, level cell=[30,0.5,50]); virgin export is `engine/total_shots/results_virgin.json` with A and predictions in `predictions/t_tr_virgin_predictions.csv`.
