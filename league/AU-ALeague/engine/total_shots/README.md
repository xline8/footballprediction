# T-AU total-shots engine

Reads `data/au_matches.csv`, uses A/B/C shots-family arms, line ladder 26.5/27.5/28.5, and frozen 1H share 0.451. Dev uses 2021/2022 seed and scores 2022/2023–2024/2025; virgin is 2025/2026.

```text
python3 league/AU-ALeague/engine/total_shots/run_t_au.py dev
python3 league/AU-ALeague/engine/total_shots/run_t_au.py virgin
```

The engine writes dev/virgin results, fitted parameters, and conditional `predictions/t_au_virgin_predictions.csv`.
