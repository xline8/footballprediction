# C-COA corners engine

Reads `data/co_primeraa_matches.csv`, uses the frozen chronological corners mechanics, and scores lines 8.5, 9.5, and 10.5. Dev loads 2021 Apertura/Clausura as seed and scores 2022 Apertura through 2025 Clausura; virgin is the complete 2026 Apertura tournament.

```text
~/workspace/footballprediction/.venv/bin/python run_c_coa.py dev
~/workspace/footballprediction/.venv/bin/python run_c_coa.py virgin
```

The engine writes dev/virgin results and conditional fitted parameters plus `predictions/c_coa_virgin_predictions.csv`. Virgin predictions use the frozen 0.4956/0.5044 halves presentation split.
