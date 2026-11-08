# C-NL corners engine

League-local implementation of the frozen C-NL preregistration
(`league/NL-Eredivisie/prereg/PREREG_C_NL.md`), seeded from
`league/J1/engine/corners/` (the production `model_corners_v3.py`
pattern): decay-weighted base rates (HL 270), rolling-5 shots
relative factors, NB total, territorial multiplier fitted on the
preceding-season fit window only. Arms: Gate Zero (X9 possession +
big-chance covariates), X7 (opp-box touches, min-8 trailing rule).

Inputs: `league/NL-Eredivisie/data/nl_matches.csv`.
Outputs: `results_dev.json` (+ CSV), `results_virgin.json`,
`fitted_params_virgin.json`, `league/NL-Eredivisie/predictions/c_nl_virgin_predictions.csv`.

Run from the repository root:

```bash
~/workspace/footballprediction/.venv/bin/python league/NL-Eredivisie/engine/corners/run_c_nl.py dev
~/workspace/footballprediction/.venv/bin/python league/NL-Eredivisie/engine/corners/run_c_nl.py virgin --arms gate_zero
```

The virgin command must be given only arms that pass the persisted
dev gate. The harness uses date-grouped state so same-date matches
cannot see one another. Season 2026/2027 is never loaded.
