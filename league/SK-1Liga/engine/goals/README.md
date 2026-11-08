# G-SK goals engine

Reads `league/SK-1Liga/data/sk_matches.csv` (phase != playoff only).
Dixon-Coles, goals-only (no xG is published for this league — the DC
blend's goals-only fallback is the whole observation model), hl=270.
Dev loads only 2021/2022–2024/2025 (2021/2022 seed); virgin reads
2025/2026 only for arms passing the recorded dev gate. Arms:
`gate_zero`, `shrink`, `x2` (mover offset per PREREG_G_SK; mover
clubs and frozen offsets live in `arms.py` — the mover set is the
prereg definition evaluated on this corpus: three promoted clubs
for 2022/2023 (the licence-collapse season), one per season after,
verified against the 2. Liga (id 8973) index; `arms.mover_ids`
asserts all six mover names appear in that index).

```text
python3 league/SK-1Liga/engine/goals/run_g_sk.py dev
python3 league/SK-1Liga/engine/goals/run_g_sk.py virgin-metrics
python3 league/SK-1Liga/engine/goals/run_g_sk.py virgin-predict --arm gate_zero
```

Outputs `results_dev.json/.csv`, conditional `results_virgin.json`;
a shipped arm also writes `fitted_params_virgin.json` and
`predictions/g_sk_virgin_predictions.csv` (1H/2H via frozen 0.4448).
