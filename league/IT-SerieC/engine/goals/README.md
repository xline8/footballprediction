# G-ITC goals engine

Reads regular-phase rows only from `league/IT-SerieC/data/itseriec_matches.csv`. All observations are goals-only; xG and period-split fields are not present for the complete seasons. Dev loads only 2021/2022–2024/2025, using 2021/2022 as the seed and the remaining three seasons as walk-forward evaluation. Arms are `gate_zero` and `shrink`, with the latter shrinking ratings by prior in-league match count divided by 6 for teams with fewer than six matches.

Run from this directory:

```text
python3 run_g_itc.py dev
python3 run_g_itc.py virgin-metrics
python3 run_g_itc.py virgin-predict --arm gate_zero
```

Virgin commands read regular-phase 2025/2026 only after the dev gate. Outputs are `results_dev.json/csv`, conditional `results_virgin.json`, `fitted_params_virgin.json`, and (when predicting) `league/IT-SerieC/predictions/g_itc_virgin_predictions.csv` with FT columns only. Authority: `league/IT-SerieC/prereg/PREREG_G_ITC.md`.
