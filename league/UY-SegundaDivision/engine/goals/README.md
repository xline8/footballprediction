# G-UYSEG goals engine

This dependency-free engine implements the frozen Uruguay Segunda Division
development protocol. It reads `data/uy_segunda_matches.csv`, uses calendar
season 2021 as the seed, and evaluates seasons 2022–2025 with expanding,
season-blocked folds. The loader rejects any forbidden virgin-season row.

Run from this directory:

```text
python run_g_uyseg.py dev
```

The command writes `results_dev.json`, `results_dev.csv`, and the current
two-field `results_virgin.json` sentinel. The CSV has one row per evaluated
match. The JSON includes per-season and pooled metrics, Gate Zero versus
climatology OU2.5, SHRINK/X2 bite counts, fitted rho and mu, and mechanical
dev-gate arithmetic.

Arms are Gate Zero, SHRINK (`a,d *= min(1,n/6)` with prior in-league match
count), and X2. X2 uses only the frozen relegated-mover offsets:

```text
2022: (0.000000, 0.000000)
2023: (-0.129264, 0.179378)
2024: (-0.044284, 0.134240)
2025: (0.004892, 0.066170)
```

The shared DC constants are MAXG 10, 14 sweeps, damping 0.7, smoothing
0.25, initial home advantage 0.28, rho grid `(0.0, -0.05, -0.10, -0.15)`,
half-life 270 days, and the production tau correction. The trailing-10
baseline falls back to league home/away means when either team has fewer than
six prior matches.
