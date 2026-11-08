# S-BE shots-on-target engine

Reads `data/be_matches.csv` with target `ShotsOnTarget_home + ShotsOnTarget_away`. Dev uses 2021/2022 warm-up and scores n=956 in 2022/2023–2024/2025 at lines 7.5/8.5/9.5, with gate and primary line 8.5. Arms are GZ, RS, and X4; virgin is 2025/2026 (n=313) and conditional on the recorded gate. Frozen halves shares are 0.452/0.548.

```text
python3 league/BE-FirstDivisionA/engine/sot/run_s_be.py dev
python3 league/BE-FirstDivisionA/engine/sot/run_s_be.py virgin-metrics
```

Results are written here; a shipped arm writes `fitted_params_virgin.json` and `predictions/s_be_virgin_predictions.csv`.
