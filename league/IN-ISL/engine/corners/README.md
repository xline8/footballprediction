# C-IN corners engine

Production model_corners_v3 pattern, ported from the AU-ALeague engine. Target total corners from `league/IN-ISL/data/in_matches.csv`. Warm-up 2021/2022, scored dev 2022/2023–2024/2025 (n=419), virgin 2025/2026 (n=91). Arms: gate_zero (X9 covariates: possession + big chances), x7 (opp-box-touches multiplier). Primary line 10.5, ladder 9.5/10.5/11.5; halves presentation via frozen constant 0.458.

```text
.venv/bin/python league/IN-ISL/engine/corners/run_c_in.py dev
.venv/bin/python league/IN-ISL/engine/corners/run_c_in.py virgin --arms gate_zero x7
```

Verdict: PASS PROVISIONAL — Gate Zero ships (X7 beta = 0 on the virgin fit, again); see `reports/C_IN_VERDICT.md`.
