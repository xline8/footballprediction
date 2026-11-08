# T-BR total-shots engine

Reads `league/BR-SerieA/data/br_matches.csv`, uses A/B/C shots-family arms, line ladder 25.5/26.5/27.5, and frozen 1H share 0.463. Dev uses 2021 seed and scores 2022–2024; virgin is 2025.

```text
python3 league/BR-SerieA/engine/total_shots/run_t_br.py dev
python3 league/BR-SerieA/engine/total_shots/run_t_br.py virgin
```

The engine writes dev/virgin results, fitted parameters, and conditional `predictions/t_br_virgin_predictions.csv`.
