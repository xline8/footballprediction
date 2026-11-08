# T-DE2 total-shots engine

Reads `data/de2_matches.csv`, uses A/B/C shots-family arms, line ladder 26.5/27.5/28.5 with gate and primary line 27.5, and frozen halves shares 0.447/0.553. Dev uses 2021/2022 seed and scores n=918; virgin is 2025/2026 (n=306).

```text
python3 league/DE-2Bundesliga/engine/total_shots/run_t_de2.py dev
python3 league/DE-2Bundesliga/engine/total_shots/run_t_de2.py virgin
```

The engine writes dev/virgin results, fitted parameters, and conditional `predictions/t_de2_virgin_predictions.csv`.
