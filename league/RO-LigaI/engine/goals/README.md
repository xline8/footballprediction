# G-RO goals engine

Reads `league/RO-LigaI/data/ro_matches.csv` (phase != ecl_playoff only).
Dixon-Coles, goals-only (no xG is published for this league — the DC
blend's goals-only fallback is the whole observation model), hl=270.
Dev loads only 2021/2022–2024/2025 (2021/2022 seed); virgin reads
2025/2026 only after the recorded dev gate. Arms: `gate_zero`, `shrink`
(X3 not registered for RO — no xG splits exist).

```text
python3 league/RO-LigaI/engine/goals/run_g_ro.py dev
python3 league/RO-LigaI/engine/goals/run_g_ro.py virgin-metrics
```

Outputs `results_dev.json/.csv`, conditional `results_virgin.json`;
a shipped arm also writes `fitted_params_virgin.json` and
`predictions/g_ro_virgin_predictions.csv` (1H/2H via frozen 0.453).
