# G-IN goals engine

Dixon-Coles + xG-blend pattern (production model_v2/model_xg), ported from the AU-ALeague engine. Reads `league/IN-ISL/data/in_matches.csv`. Season-blocked walk-forward: seed 2021/2022, scored dev 2022/2023–2024/2025 (n=419), virgin 2025/2026 (n=91) read once and only for dev-passing arms. Arms: gate_zero, shrink (thin-data prior), x3 (set-play decomposition). Gate: pooled 1X2 LL + RPS vs climatology and OU2.5 LL vs base rate.

```text
.venv/bin/python league/IN-ISL/engine/goals/run_g_in.py dev
.venv/bin/python league/IN-ISL/engine/goals/run_g_in.py virgin-metrics   # refuses if Gate Zero failed dev
```

Verdict: FAIL at dev (OU leg) — virgin not read; see `reports/G_IN_VERDICT.md`.
