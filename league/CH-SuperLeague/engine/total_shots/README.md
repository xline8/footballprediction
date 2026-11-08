# T-CH total-shots engine

Reads `data/ch_matches.csv`, uses A/B/C shots-family arms, line ladder 24.5/25.5/26.5, and frozen 1H share 0.470. Dev uses 2021/2022 seed and scores 2022/2023–2024/2025; virgin is 2025/2026.

```text
python3 league/CH-SuperLeague/engine/total_shots/run_t_dk.py dev
python3 league/CH-SuperLeague/engine/total_shots/run_t_dk.py virgin
```

The engine writes dev/virgin results, fitted parameters, and conditional `predictions/t_ch_virgin_predictions.csv`.
