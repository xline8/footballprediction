# EE-Meistriliiga goals engine (Phase B)

This directory contains the frozen, goals-only Dixon--Coles walk-forward engine
for FotMob league 248. It is development-only: there is deliberately no 2026
virgin loader, predictor, or verdict path here.

Inputs are `../../data/ee_matches.csv`; the harness loads only seasons 2021,
2022, 2023, 2024, and 2025 and asserts that no 2026 row enters memory. The
target-season fits use every earlier match strictly before that season's first
match date, half-life 270, 14 sweeps, damping 0.7, smoothing 0.25, fitted
home advantage initialized at 0.28, attack/defence initialized at zero, and a
0--10 Dixon--Coles score matrix. Rho is selected from the production grid.

Run from this directory with:

```sh
python run_dev.py
```

Outputs are `results_dev.json`, `results_dev.csv`, and the audit-friendly
`predictions_dev.csv`. Results contain the three frozen arms (Gate Zero,
SHRINK, X2), season and pooled metrics, expanding-fit rho/home advantage,
climatology, naive trailing-10 report-only metrics, mechanical gate arithmetic,
the SHRINK identity check, and the independent Gate Zero 2022 re-derivation.
