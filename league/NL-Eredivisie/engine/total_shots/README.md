# T-NL total-shots engine

League-local implementation of the frozen T-NL preregistration
(`league/NL-Eredivisie/prereg/PREREG_T_NL.md`), seeded from
`league/J1/engine/total_shots/` (the shots family: v1 pattern,
v2 level layer, E9 trailing-r). Arms: A (v1), B (v2 level layer),
C (E9 trailing-r). Primary line 26.5; the port's corpus-mean input
M_BAR is 27.01 for this league (a data input, per the prereg).

Inputs: `league/NL-Eredivisie/data/nl_matches.csv`.
Outputs: `results_dev.json` (+ CSV), `results_virgin.json`,
`fitted_params.json`, `league/NL-Eredivisie/predictions/t_nl_virgin_predictions.csv`.

Run from the repository root:

```bash
~/workspace/footballprediction/.venv/bin/python league/NL-Eredivisie/engine/total_shots/run_t_nl.py dev
~/workspace/footballprediction/.venv/bin/python league/NL-Eredivisie/engine/total_shots/run_t_nl.py virgin --export-arm A
```

The virgin export refuses arms that did not pass the recorded dev
gate. Season 2026/2027 is never loaded.
