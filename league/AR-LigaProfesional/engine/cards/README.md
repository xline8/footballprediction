# K-AR cards engine

League-local implementation of the frozen K-AR preregistration
(`league/AR-LigaProfesional/prereg/PREREG_AR.md`), seeded from
`league/J1/engine/cards/` (the production `model_cards.py` pattern):
270-day decayed venue-split team yellow rates, shrinkage prior
K = 8, NB r = 112.39. Arms: Gate Zero, X8 (referee factor from the
CSV `referee` column — 100% coverage in this corpus, so no
warehouse extraction is needed or done).

Inputs: `league/AR-LigaProfesional/data/ar_matches.csv`.
Outputs: `results_dev.json` (+ CSV), `results_virgin.json`,
`fitted_params_virgin.json`, `league/AR-LigaProfesional/predictions/k_ar_virgin_predictions.csv`.

Run from the repository root:

```bash
~/workspace/footballprediction/.venv/bin/python league/AR-LigaProfesional/engine/cards/run_k_ar.py dev
~/workspace/footballprediction/.venv/bin/python league/AR-LigaProfesional/engine/cards/run_k_ar.py virgin-metrics
~/workspace/footballprediction/.venv/bin/python league/AR-LigaProfesional/engine/cards/run_k_ar.py virgin-predict --arm gate_zero
```

`virgin-metrics` follows the port's fallback pattern (Gate Zero
virgin metrics + labelled predictions file are written even when
the dev gate fails — see the verdict for the gate reading).
Ordering is by kickoff timestamp (tie-break match_id), inherited
from the J1 port. Target is unified yellow_home + yellow_away; primary line 4.5, secondary 5.5, halves constant 0.373. Missing referees use factor 1.0.
