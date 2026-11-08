# S-NL shots-on-target engine

League-local implementation of the frozen S-NL preregistration
(`league/NL-Eredivisie/prereg/PREREG_S_NL.md`), seeded from
`league/J1/engine/sot/` (the production `model_sot.py` v5 pattern):
joint ridge Poisson ratings, decayed total-shots component with a
Beta-Binomial on-target ratio, NB r = 79.94, 50/50 naive trailing-10
ensemble. Arms: GZ, RS (ratio prior 200 → 20,000), X4 (xG/shot
quality ratio), X6 (X4 + era-guarded xGOT, era = matches from
2024/2025 onward).

Inputs: `league/NL-Eredivisie/data/nl_matches.csv`.
Outputs: `results_dev.json` (+ CSV), `results_virgin.json`,
`fitted_params_virgin.json`, `league/NL-Eredivisie/predictions/s_nl_virgin_predictions.csv`.

Run from this directory:

```bash
~/workspace/footballprediction/.venv/bin/python run_s_nl.py dev
~/workspace/footballprediction/.venv/bin/python run_s_nl.py virgin-metrics
~/workspace/footballprediction/.venv/bin/python run_s_nl.py virgin-predict --arm GZ
```

The virgin step reads only arms that pass the dev gate (pooled
LL@9.5 beats both baselines; X6 judged on its era folds). Season
2026/2027 is never loaded.
