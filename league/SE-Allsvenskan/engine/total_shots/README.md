# T-SE total-shots engine

Reads `data/se_matches.csv`, uses A/B/C shots-family arms, line ladder 25.5/26.5/27.5, and frozen 1H share 0.457. Dev uses 2021 seed and scores 2022–2024; virgin is 2025.

```text
python3 league/SE-Allsvenskan/engine/total_shots/run_t_se.py dev
python3 league/SE-Allsvenskan/engine/total_shots/run_t_se.py virgin
```

The engine writes dev/virgin results, fitted parameters, and conditional `predictions/t_se_virgin_predictions.csv`.
