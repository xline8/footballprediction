# T-AR total-shots engine

League-local implementation of the frozen T-AR preregistration
(`league/AR-LigaProfesional/prereg/PREREG_AR.md`), seeded from
`league/J1/engine/total_shots/` (the shots family: v1 pattern,
v2 level layer, E9 trailing-r). Arms: A (v1), B (v2 level layer),
C (E9 trailing-r). Primary line 23.5; the port's corpus-mean input
M_BAR is 27.01 for this league (a data input, per the prereg).

Inputs: `league/AR-LigaProfesional/data/ar_matches.csv`.
Outputs: `results_dev.json` (+ CSV), `results_virgin.json`,
`fitted_params.json`, `league/AR-LigaProfesional/predictions/t_ar_virgin_predictions.csv`.

Run from the repository root:

```bash
~/workspace/footballprediction/.venv/bin/python league/AR-LigaProfesional/engine/total_shots/run_t_ar.py dev
~/workspace/footballprediction/.venv/bin/python league/AR-LigaProfesional/engine/total_shots/run_t_ar.py virgin --export-arm A
```

The virgin export refuses arms that did not pass the recorded dev
gate. Season 2026 - Clausura is never loaded.
