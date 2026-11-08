# C-DE2 corners engine

Reads `data/de2_matches.csv`, uses the chronological corners mechanics, primary line 10.5, and frozen halves shares 0.454/0.546. Dev uses the 2021/2022 seed and scores n=918 across 2022/2023–2024/2025; virgin is 2025/2026 (n=306).

```text
/home/hatch/workspace/footballprediction/.venv/bin/python league/DE-2Bundesliga/engine/corners/run_c_de2.py dev
/home/hatch/workspace/footballprediction/.venv/bin/python league/DE-2Bundesliga/engine/corners/run_c_de2.py virgin --arms gate_zero x7
```

The engine writes dev/virgin results and conditional fitted parameters plus `predictions/c_de2_virgin_predictions.csv`.
