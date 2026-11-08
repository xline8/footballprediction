# T-BRB total-shots engine

Reads `league/BR-SerieB/data/brb_matches.csv` and evaluates arms A (v1), B (v2 level layer), and C (trailing-r). Dev uses 2021 seed and scores 2022–2024 at line 26.5; virgin is 2025 only for dev-passing arms.

```text
python3 league/BR-SerieB/engine/total_shots/run_t_br.py dev
python3 league/BR-SerieB/engine/total_shots/run_t_br.py virgin --arms A B C
```

Outputs are written here. A passing shipped run writes `fitted_params_virgin.json` and `predictions/t_brb_virgin_predictions.csv`; 1H/2H columns use the frozen shots split 0.473/0.527.
