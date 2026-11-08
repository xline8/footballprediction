# G-VN goals engine

This dependency-free engine implements the frozen Vietnam V-League
development protocol. It reads `data/vn_vleague_matches.csv`, uses season
2021 as the seed, and evaluates seasons 2022, 2023, 2023/2024, and 2024/2025
with expanding, season-blocked folds. The loader rejects any 2025/2026 row
during development.

Run from this directory:

```text
python run_g_vn.py dev
```

The command writes `results_dev.json`, `results_dev.csv`, and the current
two-field `results_virgin.json` sentinel. The CSV has one row per evaluated
match. The JSON includes per-season and pooled metrics, Gate Zero versus
climatology OU2.5, SHRINK bite counts, fitted rho and mu, and mechanical
dev-gate arithmetic.

Arms are Gate Zero and SHRINK (`a,d *= min(1,n/6)` with prior in-league
match count).

The shared DC constants are MAXG 10, 14 sweeps, damping 0.7, smoothing
0.25, initial home advantage 0.28, rho grid `(0.0, -0.05, -0.10, -0.15)`,
half-life 270 days, and the production tau correction. The trailing-10
baseline falls back to league home/away means when either team has fewer than
six prior matches. Virgin prediction halves use the frozen 1H goals share
0.4468 (2H 0.5532) and write `predictions/g_vn_virgin_predictions.csv`.
