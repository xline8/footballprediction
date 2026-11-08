# C-AR corners engine

League-local implementation of the frozen C-AR preregistration
(`league/AR-Eredivisie/prereg/PREREG_C_AR.md`), seeded from
`league/J1/engine/corners/` (the production `model_corners_v3.py`
pattern): decay-weighted base rates (HL 270), rolling-5 shots
relative factors, NB total, territorial multiplier fitted on the
preceding-season fit window only. Arms: Gate Zero (X9 possession +
big-chance covariates), X7 (opp-box touches, min-8 trailing rule).

Inputs: `league/AR-Eredivisie/data/ar_matches.csv`.
Outputs: `results_dev.json` (+ CSV), `results_virgin.json`,
`fitted_params_virgin.json`, `league/AR-Eredivisie/predictions/c_ar_virgin_predictions.csv`.

Run from the repository root:

```bash
~/workspace/footballprediction/.venv/bin/python league/AR-Eredivisie/engine/corners/run_c_ar.py dev
~/workspace/footballprediction/.venv/bin/python league/AR-Eredivisie/engine/corners/run_c_ar.py virgin --arms gate_zero
```

The virgin command must be given only arms that pass the persisted
dev gate. The harness uses date-grouped state so same-date matches
cannot see one another. Season 2026 - Clausura is never loaded.
