# G-IL goals engine

This is the preregistered goals-only Dixon-Coles engine for Israel's Leumit
League. It uses the expanding, season-blocked window, 270-day decay, 14
production-style sweeps, and the three registered prediction arms:
`gate_zero`, `shrink`, and `x2`. X2 reads Ligat ha'Al team IDs from the
warehouse index and each match JSON's `general.homeTeam.id` and
`general.awayTeam.id`.

Run DEV from the repository root:

```bash
python3 league/IL-Leumit/engine/goals/run_g_il.py dev
```

DEV is hard-isolated to `2021/2022` through `2024/2025`, writes
`results_dev.json` and `results_dev.csv`, and prints the full per-arm,
per-season and pooled table.

The virgin entry point is separate and must only be run by the coordinator:

```bash
python3 league/IL-Leumit/engine/goals/run_g_il.py virgin \
  --arms gate_zero,x2 --out /path/to/predictions.csv
```

It requires a non-empty arm list, reads `2025/2026`, writes virgin results and
fitted parameters beside this README, and writes the requested predictions
CSV. No halves outputs are produced.
