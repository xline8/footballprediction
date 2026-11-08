# T-IN total-shots engine

Shots family (v1 / v2 level layer / E9 trailing-r, as T-J1), ported from the AU-ALeague engine. Target `total_shots_home + total_shots_away` from `league/IN-ISL/data/in_matches.csv`. Warm-up 2021/2022, scored dev 2022/2023–2024/2025 (n=419), virgin 2025/2026 (n=91). Arms: A, B, C. Primary line 26.5, ladder 25.5/26.5/27.5; halves presentation via frozen constant 0.447.

```text
.venv/bin/python league/IN-ISL/engine/total_shots/run_t_in.py dev
.venv/bin/python league/IN-ISL/engine/total_shots/run_t_in.py virgin --arms A B C
```

Verdict: FAIL at virgin legs (i) and (ii), all arms — nothing ships; see `reports/T_IN_VERDICT.md`.
