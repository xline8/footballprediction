# G-BG2 goals engine

Reads `league/BG-SecondLeague/data/bg2_matches.csv`. All observations are goals-only; xG and period-split fields are not present. Dev loads only 2021/2022–2024/2025, using 2021/2022 as the seed and the remaining three seasons as walk-forward evaluation. Arms are `gate_zero` and `shrink`, with the latter shrinking ratings by prior in-league match count divided by 6 for teams with fewer than six matches.

Run from this directory:

```text
python3 run_g_bg2.py dev
python3 run_g_bg2.py virgin-metrics
python3 run_g_bg2.py virgin-predict --arm gate_zero
```

Virgin commands read 2025/2026 only after the dev gate. Outputs are `results_dev.json/csv`, conditional `results_virgin.json`, `fitted_params_virgin.json`, and (when predicting) `league/BG-SecondLeague/predictions/g_bg2_virgin_predictions.csv` with FT columns only. Authority: `league/BG-SecondLeague/prereg/PREREG_G_BG2.md`.
