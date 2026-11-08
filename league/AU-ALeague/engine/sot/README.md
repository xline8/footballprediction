# S-AU shots-on-target engine

Reads `data/au_matches.csv` with target `ShotsOnTarget_home + ShotsOnTarget_away`. Dev uses 2021/2022 warm-up and scores 2022/2023–2024/2025 at lines 8.5/9.5/10.5. Arms are GZ, RS, X4, and era-guarded X6; virgin is conditional on the recorded gate. X6 only uses xGOT from the 2024/2025 population break onward.

```text
python3 league/AU-ALeague/engine/sot/run_s_au.py dev
python3 league/AU-ALeague/engine/sot/run_s_au.py virgin-metrics
```

Results are written here; a shipped arm writes `fitted_params_virgin.json` and `predictions/s_au_virgin_predictions.csv`.
