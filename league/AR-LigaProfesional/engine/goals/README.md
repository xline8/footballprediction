# G-AR goals engine

League-local Dixon-Coles goals model for the Eredivisie, seeded from
`league/J1/engine/goals/` (the production `model_v2.py` pattern).
Arms: Gate Zero, X2 (newcomer priors −0.45/+0.26), X3 (X2 + set-play
tilt). Frozen per `league/AR-LigaProfesional/prereg/PREREG_AR.md`.

Inputs: `league/AR-LigaProfesional/data/ar_matches.csv`.
Outputs: `results_dev.json` (+ CSV), `results_virgin.json`,
`fitted_params_virgin.json`, predictions via the runner.

Run from the repository root:

```bash
~/workspace/footballprediction/.venv/bin/python league/AR-LigaProfesional/engine/goals/run_g_ar.py dev
~/workspace/footballprediction/.venv/bin/python league/AR-LigaProfesional/engine/goals/run_g_ar.py virgin-metrics
~/workspace/footballprediction/.venv/bin/python league/AR-LigaProfesional/engine/goals/run_g_ar.py virgin-predict --arm gate_zero
```

`virgin-metrics` reads the virgin season (2026 - Clausura) only for arms
that pass the persisted dev gate; with no passing arm it evaluates
Gate Zero as the labelled fallback (see the verdict for the gate
reading). Season 2026 - Clausura is never loaded.
