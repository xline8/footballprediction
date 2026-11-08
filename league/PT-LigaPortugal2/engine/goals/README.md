# G-PT2 goals engine

This goals-only Dixon–Coles engine reads `league/PT-LigaPortugal2/data/pt2_matches.csv`. Dev uses seed 2021/2022 and expanding, season-blocked evaluation in 2022/2023–2024/2025 (pooled n=918). The virgin is 2025/2026 (n=306), read only when at least one arm passes the frozen dev gate. The reserved 2026/2027 season is rejected by an assertion and is never read.

The preregistered arms are `gate_zero` and `shrink`; SHRINK scales fitted attack and defence ratings by prior in-league matches divided by six only when the count is below six. Constants and gates are defined by `league/PT-LigaPortugal2/prereg/PREREG_G_PT2.md`.

Run from this directory:

```text
python3 run_g_pt2.py dev
python3 run_g_pt2.py virgin
```

Outputs are `results_dev.json/csv`, conditional `results_virgin.json`, and conditional `fitted_params_virgin.json`. On a preregistered PASS, predictions are written to `league/PT-LigaPortugal2/predictions/g_pt2_virgin_predictions.csv` with FT-only columns.
