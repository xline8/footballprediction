# G-TR1 goals engine

Development-only walk-forward engine for Türkiye 1. Lig. It reads finished,
regular, non-awarded rows from `data/tr1_matches.csv`, seeds on 2021/2022,
and scores 2022/2023–2024/2025 (313 + 306 + 379 = 998 rows). The three arms
are Gate Zero, verbatim SHRINK, and X2, the Süper Lig down-mover prior.

Run from the repository root:

```bash
python3 league/TR-1Lig/engine/goals/run_g_tr.py dev
```

Outputs are `results_dev.json`, `results_dev.csv`, and `predictions_dev.csv`
in this directory. No virgin-season evaluation or prediction command exists.

## Development report

Lower is better for every metric. Each arm is compared with the expanding,
prior-seasons-only climatology; the gate requires all three pooled model
metrics to beat that baseline.

| arm | season | model LL | model RPS | model OU2.5 LL | climatology LL | climatology RPS | climatology OU2.5 LL | gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| gate_zero | pooled | 1.065849 | 0.227498 | 0.707038 | 1.074184 | 0.231945 | 0.692858 | FAIL |
| shrink | pooled | 1.065849 | 0.227498 | 0.707038 | 1.074184 | 0.231945 | 0.692858 | FAIL |
| x2 | pooled | 1.109489 | 0.239835 | 0.713493 | 1.074184 | 0.231945 | 0.692858 | FAIL |

The per-season rows are in `results_dev.csv`; the full JSON also records each
arm's per-season scores. X2 diagnostics:

| target season | mover count | dGF | dGA |
|---|---:|---:|---:|
| 2022/2023 | 20 | 0.000000 | 0.000000 |
| 2023/2024 | 19 | 0.303150 | -0.579604 |
| 2024/2025 | 20 | 0.099159 | -0.415814 |
