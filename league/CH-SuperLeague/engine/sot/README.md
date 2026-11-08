# S-CH shots-on-target engine

Reads `data/ch_matches.csv` with target `ShotsOnTarget_home + ShotsOnTarget_away`. Dev uses 2021/2022 warm-up and scores 2022/2023–2024/2025 at lines 8.5/9.5/10.5. Arms are GZ, RS, and X4; virgin is 2025/2026 and conditional on the recorded gate.

```text
python3 league/CH-SuperLeague/engine/sot/run_s_dk.py dev
python3 league/CH-SuperLeague/engine/sot/run_s_dk.py virgin-metrics
```

Results are written here; a shipped arm writes `fitted_params_virgin.json` and `predictions/s_ch_virgin_predictions.csv`.
