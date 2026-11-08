# G-CZ-FNL goals engine

Reads `league/CZ-FNL/data/fnl_matches.csv` and retains included regular-season matches. This is the frozen goals-only Dixon–Coles engine (`hl=270`) with arms `gate_zero`, `shrink`, and `x2`.

```text
python3 run_g_cz_fnl.py dev
python3 run_g_cz_fnl.py virgin-metrics
python3 run_g_cz_fnl.py virgin-predict --arm gate_zero
```

DEV writes `results_dev.json` and `results_dev.csv`. Virgin commands rerun DEV and read 2025/2026 only for arms passing the pooled gate: 1X2 LL and RPS beat expanding prior-season climatology, and OU2.5 LL beats its base-rate baseline. Predictions write `league/CZ-FNL/predictions/g_cz_fnl_virgin_predictions.csv`, using frozen 1H/2H share `0.449598`.
