# G-GT goals engine

This is the preregistered, goals-only Dixon-Coles engine for Guatemala Liga Nacional. It uses the 2021/2022 seed, expanding season-blocked development in 2022/2023–2024/2025, and conditionally reads the complete 2025/2026 virgin only after an arm passes all three pooled development gates. The reserved 2026/2027 season is assertion-rejected.

The two frozen arms are `gate_zero` and `shrink`. SHRINK scales each fitted attack and defence rating by prior in-league matches divided by six when the count is below six. Constants are not tunable here: 14 multiplicative sweeps, damping 0.7, +0.25 smoothing, home advantage 0.28, `MAXG=10`, production tau correction, the frozen rho grid, and 270-day half-life.

Run from this directory:

```text
python3 run_g_gt.py dev
python3 run_g_gt.py virgin
```

Development writes `results_dev.json/csv`. Virgin output is conditional: `results_virgin.json`, and on a preregistered PASS only, `fitted_params_virgin.json` plus `league/GT-LigaNacional/predictions/g_gt_virgin_predictions.csv`.
