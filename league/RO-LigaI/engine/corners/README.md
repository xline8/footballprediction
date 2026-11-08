# C-RO corners engine

Reads `league/RO-LigaI/data/ro_matches.csv` (phase != ecl_playoff;
stats-less matches excluded by the loader). Chronological corners
mechanics as the production/J1 reference (HL 270 base rates,
rolling-5 factors, per-season gamma/beta/r on prior rows only).
RO divergence (preregistered): Gate Zero covariate is possession
ONLY — big chances and box touches exist only from 2025/2026, so
no variant arm is registered; single arm `gate_zero`. Lines
7.5/8.5/9.5, gate at **8.5**. Dev: 2021/2022 seed, scored
2022/2023–2024/2025; virgin 2025/2026 conditional on the dev gate.

```text
python3 league/RO-LigaI/engine/corners/run_c_ro.py dev
python3 league/RO-LigaI/engine/corners/run_c_ro.py virgin --arms gate_zero
```

Writes dev/virgin results, fitted params, and (on PASS)
`predictions/c_ro_virgin_predictions.csv` (1H/2H via frozen 0.477).
