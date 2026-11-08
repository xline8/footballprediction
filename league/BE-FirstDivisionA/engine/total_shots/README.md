# T-BE total-shots engine

Reads `data/be_matches.csv`, uses A/B/C shots-family arms, line ladder 24.5/25.5/26.5 with gate and primary line 25.5, and frozen halves shares 0.456/0.544. Dev uses 2021/2022 seed and scores n=956 in 2022/2023–2024/2025; virgin is 2025/2026 (n=313).

```text
python3 league/BE-FirstDivisionA/engine/total_shots/run_t_be.py dev
python3 league/BE-FirstDivisionA/engine/total_shots/run_t_be.py virgin
```

The engine writes dev/virgin results, fitted parameters, and conditional `predictions/t_be_virgin_predictions.csv`.
