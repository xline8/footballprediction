# S-BR shots-on-target engine

Reads `league/BR-SerieA/data/br_matches.csv` with target `ShotsOnTarget_home + ShotsOnTarget_away`. Dev uses 2021 warm-up and scores 2022–2024 at lines 7.5/8.5/9.5. Arms are GZ, RS, and X4; virgin is 2025 and conditional on the recorded gate.

```text
python3 league/BR-SerieA/engine/sot/run_s_br.py dev
python3 league/BR-SerieA/engine/sot/run_s_br.py virgin-metrics
```

Results are written here; a shipped arm writes `fitted_params_virgin.json` and `predictions/s_br_virgin_predictions.csv`.
