# G-LV goals engine

This goals-only Dixon–Coles engine uses team ids and the frozen LV
preregistration: calendar-year seasons, an expanding season-blocked fit,
Gate Zero, and SHRINK. The DC half-life is 270 days. The presentation
halves constant is 0.4569.

Input: `league/LV-Virsliga/data/lv_virsliga_matches.csv`. Development
loads only seasons 2021–2025, trains on 2021, and scores 2022–2025
(720 matches). The CSV already excludes the six relegation finals.

From this directory:

```text
python run_g_lv.py dev
python run_g_lv.py virgin-metrics --arm gate_zero shrink
python run_g_lv.py virgin-predict --arm gate_zero
```

The dev command writes `results_dev.json`, `predictions_dev.csv`, and
`fitted_params.json`. Virgin commands write `results_virgin.json` and,
for prediction, `fitted_params_virgin.json` plus
`league/LV-Virsliga/predictions/g_lv_virgin_predictions.csv`.
