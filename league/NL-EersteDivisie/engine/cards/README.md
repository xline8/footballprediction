# K-NL cards engine

League-local implementation of the frozen K-NL preregistration
(`league/NL-Eredivisie/prereg/PREREG_K_NL.md`), seeded from
`league/J1/engine/cards/` (the production `model_cards.py` pattern):
270-day decayed venue-split team yellow rates, shrinkage prior
K = 8, NB r = 112.39. Arms: Gate Zero, X8 (referee factor from the
CSV `referee` column — 100% coverage in this corpus, so no
warehouse extraction is needed or done).

Inputs: `league/NL-Eredivisie/data/nl_matches.csv`.
Outputs: `results_dev.json` (+ CSV), `results_virgin.json`,
`fitted_params_virgin.json`, `league/NL-Eredivisie/predictions/k_nl_virgin_predictions.csv`.

Run from the repository root:

```bash
~/workspace/footballprediction/.venv/bin/python league/NL-Eredivisie/engine/cards/run_k_nl.py dev
~/workspace/footballprediction/.venv/bin/python league/NL-Eredivisie/engine/cards/run_k_nl.py virgin-metrics
~/workspace/footballprediction/.venv/bin/python league/NL-Eredivisie/engine/cards/run_k_nl.py virgin-predict --arm gate_zero
```

`virgin-metrics` follows the port's fallback pattern (Gate Zero
virgin metrics + labelled predictions file are written even when
the dev gate fails — see the verdict for the gate reading).
Ordering is by kickoff timestamp (tie-break match_id), inherited
from the J1 port. Season 2026/2027 is never scored.
