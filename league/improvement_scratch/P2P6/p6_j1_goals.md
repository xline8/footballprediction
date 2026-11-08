### P6 worst-fold block — J1 goals (primary metric: ll_1x2)

Source: `league/J1/engine/goals/results_dev.json` (persisted dev artefacts; information only — no gate change).
Worst dev season (highest ll_1x2 for the reference arm): **2024**.

| Entity | Pooled ll_1x2 | Pooled source | Worst-season (2024) ll_1x2 | n (worst) | Δ vs pooled |
|---|---|---|---|---|---|
| climatology | 1.0860 | n-weighted, computed | 1.0914 | 380 | +0.0054 |
| gate_zero | 1.0675 | n-weighted, computed | 1.0817 | 380 | +0.0141 |
| x2 | 1.1119 | n-weighted, computed | 1.1564 | 380 | +0.0446 |
| x3 | 1.1245 | n-weighted, computed | 1.1741 | 380 | +0.0497 |

Per-season legs for every entity are in the machine-readable output of the tool (`--json`). Reading: the worst-season column is the model's hardest dev fold; compare it against the baselines' worst-season values on the same fold before trusting the pooled margin.

wrote league/improvement_scratch/P2P6/p6_j1_goals.json
