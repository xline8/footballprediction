### P6 worst-fold block — AE-ProLeague sot (primary metric: ll_9.5)

Source: `league/AE-ProLeague/engine/sot/results_dev.json` (persisted dev artefacts; information only — no gate change).
Worst dev season (highest ll_9.5 for the reference arm): **2022/2023**.

| Entity | Pooled ll_9.5 | Pooled source | Worst-season (2022/2023) ll_9.5 | n (worst) | Δ vs pooled |
|---|---|---|---|---|---|
| GZ | 0.6928 | persisted | 0.7087 | 182 | +0.0159 |
| RS | 0.6919 | persisted | 0.7081 | 182 | +0.0163 |
| baseline: league_base_rate | 0.7013 | persisted | 0.7084 | 182 | +0.0072 |
| baseline: naive | 0.7009 | persisted | 0.7269 | 182 | +0.0261 |

Per-season legs for every entity are in the machine-readable output of the tool (`--json`). Reading: the worst-season column is the model's hardest dev fold; compare it against the baselines' worst-season values on the same fold before trusting the pooled margin.

wrote league/improvement_scratch/P2P6/p6_ae_sot.json
