### P6 worst-fold block — AT-Bundesliga corners (primary metric: ll_9.5)

Source: `league/AT-Bundesliga/engine/corners/results_dev.json` (persisted dev artefacts; information only — no gate change).
Worst dev season (highest ll_9.5 for the reference arm): **2023/2024**.

| Entity | Pooled ll_9.5 | Pooled source | Worst-season (2023/2024) ll_9.5 | n (worst) | Δ vs pooled |
|---|---|---|---|---|---|
| gate_zero | 0.6943 | n-weighted, computed | 0.7062 | 195 | +0.0119 |
| league_base_rate | 0.7322 | n-weighted, computed | 0.7247 | 195 | -0.0076 |
| naive_trailing_10 | 0.7365 | n-weighted, computed | 0.7350 | 195 | -0.0015 |
| x7 | 0.6921 | n-weighted, computed | 0.6933 | 195 | +0.0012 |

Per-season legs for every entity are in the machine-readable output of the tool (`--json`). Reading: the worst-season column is the model's hardest dev fold; compare it against the baselines' worst-season values on the same fold before trusting the pooled margin.

wrote league/improvement_scratch/P2P6/p6_at_corners.json
