# G-NL goals engine

League-local Dixon-Coles goals model for the Eredivisie, seeded from
`league/J1/engine/goals/` (the production `model_v2.py` pattern).
Arms: Gate Zero, X2 (newcomer priors −0.45/+0.26), X3 (X2 + set-play
tilt). Frozen per `league/NL-Eredivisie/prereg/PREREG_G_NL.md`.

Inputs: `league/NL-Eredivisie/data/nl_matches.csv`.
Outputs: `results_dev.json` (+ CSV), `results_virgin.json`,
`fitted_params_virgin.json`, predictions via the runner.

Run from the repository root:

```bash
~/workspace/footballprediction/.venv/bin/python league/NL-Eredivisie/engine/goals/run_g_nl.py dev
~/workspace/footballprediction/.venv/bin/python league/NL-Eredivisie/engine/goals/run_g_nl.py virgin-metrics
~/workspace/footballprediction/.venv/bin/python league/NL-Eredivisie/engine/goals/run_g_nl.py virgin-predict --arm gate_zero
```

`virgin-metrics` reads the virgin season (2025/2026) only for arms
that pass the persisted dev gate; with no passing arm it evaluates
Gate Zero as the labelled fallback (see the verdict for the gate
reading). Season 2026/2027 is never loaded.
