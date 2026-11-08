# G-SK2 goals engine

This dependency-free engine fits the frozen Dixon–Coles goals model for
SK-2Liga. It reads `data/sk2_matches.csv`; the dev harness uses only
2021/2022 through 2024/2025 and never reads the virgin 2025/2026 season or
the in-progress 2026/2027 season.

Run from this directory (or use the equivalent path):

```text
python run_g_sk2.py dev
python run_g_sk2.py virgin-metrics
python run_g_sk2.py virgin-predict --arm gate_zero
```

`dev` writes `results_dev.json` and `results_dev.csv`. It evaluates Gate
Zero, SHRINK, and X2 with expanding season-blocked folds, climatology, and
the trailing-10 naive baseline. `virgin-metrics` runs dev first and reads
only arms passing the per-arm dev gate. `virgin-predict` is an operator-only
command for a selected shipping arm and writes fitted parameters plus
`predictions/g_sk2_virgin_predictions.csv`.

Frozen constants are DC `MAXG=10`, 14 sweeps, damping 0.7, smoothing 0.25,
initial home advantage 0.28, rho grid `(0.0, -0.05, -0.10, -0.15)`, and
half-life 270 days. X2 movers are IDs 291155, 155166, 2255, and 2169 by
season, with offsets `(-0.022593,-0.133704)`, `(0.109050,-0.029839)`, and
`(0.150539,-0.236926)` after the zero offset for 2022/2023. Prediction
halves use the frozen goals constant 0.4940 for 1H and 0.5060 for 2H.
