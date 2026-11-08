# S-IN shots-on-target engine

Production model_sot.py v5 pattern, ported from the AU-ALeague engine. Target `ShotsOnTarget_home + ShotsOnTarget_away` from `league/IN-ISL/data/in_matches.csv`. Per-match walk-forward: warm-up 2021/2022, scored dev 2022/2023–2024/2025 (n=419), virgin 2025/2026 (n=91). Arms: GZ, RS (ratio prior 20,000), X4 (xG/shot quality input). X6 not built (FEATURES: xGOT era = one dev season). Primary line 8.5, ladder 7.5/8.5/9.5; halves presentation via frozen constant 0.453.

```text
.venv/bin/python league/IN-ISL/engine/sot/run_s_in.py dev
.venv/bin/python league/IN-ISL/engine/sot/run_s_in.py virgin-metrics
.venv/bin/python league/IN-ISL/engine/sot/run_s_in.py virgin-predict --arm GZ
```

Verdict: PASS PROVISIONAL — Gate Zero ships; see `reports/S_IN_VERDICT.md`.
