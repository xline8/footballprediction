### P6 worst-fold block — AE-ProLeague cards (primary metric: ll_3.5)

Source: `league/AE-ProLeague/engine/cards/results_dev.json` (persisted dev artefacts; information only — no gate change).
Worst dev season (highest ll_3.5 for the reference arm): **2022/2023**.

| Entity | Pooled ll_3.5 | Pooled source | Worst-season (2022/2023) ll_3.5 | n (worst) | Δ vs pooled |
|---|---|---|---|---|---|
| gate_zero | 0.7087 | n-weighted, computed | 0.7162 | 182 | +0.0076 |
| gate_zero [base] | 0.7062 | n-weighted, computed | 0.7109 | 182 | +0.0047 |
| gate_zero [naive] | 0.7085 | n-weighted, computed | 0.7110 | 182 | +0.0025 |

Per-season legs for every entity are in the machine-readable output of the tool (`--json`). Reading: the worst-season column is the model's hardest dev fold; compare it against the baselines' worst-season values on the same fold before trusting the pooled margin.

wrote league/improvement_scratch/P2P6/p6_ae_cards.json
