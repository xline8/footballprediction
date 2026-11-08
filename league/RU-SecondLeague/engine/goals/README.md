# G-RU2 goals engine

Reads `data/ru2_matches.csv`. Eligible rows are finished, non-awarded matches whose season is not `2025`. The seed is 2021/2022 and the expanding date-cutoff dev folds are 2022/2023, 2023, 2023/2024, 2024, 2024/2025, and 2025/2026. The two arms are Gate Zero and SHRINK. xG is absent, so the copied Dixon-Coles fit uses goals only.

Dev outputs are `results_dev.json`, `results_dev.csv`, and `predictions_dev.csv`. Run from this directory with `python3 run_g_ru2.py dev`. Dev gate: Gate Zero FAIL (pooled 1X2 LL and OU2.5 LL do not beat climatology/base-rate; RPS passes); SHRINK FAIL identically.

Virgin evaluation is coordinator-controlled via `harness.virgin()` and is intentionally not a CLI command.
