# S-DE2 shots-on-target engine

The frozen DE-2 prereg uses warm-up 2021/2022, scored dev seasons 2022/2023–2024/2025 (n=918), primary line 9.5, and ladders 8.5/9.5/10.5. Arms are Gate Zero, RS (BB prior P=20,000), and X4 (trailing 25 shotmap matches, minimum 8, clamped [0.15, 0.50], Gate Zero fallback). Virgin 2025/2026 is not read by the `dev` command. Frozen SOT halves shares are 0.443/0.557.

```text
python3 league/DE-2Bundesliga/engine/sot/run_s_de2.py dev
python3 league/DE-2Bundesliga/engine/sot/run_s_de2.py virgin-metrics
```

Results are written here; a shipped arm writes `fitted_params_virgin.json` and `predictions/s_de2_virgin_predictions.csv`.
