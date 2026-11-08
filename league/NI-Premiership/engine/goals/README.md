# G-NI goals engine

Development-only NI-Premiership goals engine. It reads
`../../data/ni_matches.csv`, uses regular matches from warm-up 2021/2022 and
scored seasons 2022/2023–2024/2025, and hard-checks the frozen counts (228
warm-up and 684 scored). Playoffs, virgin 2025/2026, and reserve 2026/2027
rows are excluded from every fit, baseline, and metric.

Run from this directory:

```sh
python3 run_g_ni.py
```

The engine follows the frozen preregistration: weighted direct Poisson
Dixon-Coles fits, 270-day decay, rho grid, MAXG=10, Gate Zero and SHRINK,
pooled climatology, and strict pre-date bounded trailing-10 means. Outputs
are `results_dev.json` (summary), `results_dev.csv` (684 per-match rows), and
`fitted_params_dev.json`.
