# G-CZ goals engine

Reads `league/CZ-Liga/data/cz_matches.csv` (phase != placement only).
Dixon-Coles, goals-only (no xG is published for this league — the DC
blend's goals-only fallback is the whole observation model), hl=270.
Dev loads only 2021/2022–2024/2025 (2021/2022 seed); virgin reads
2025/2026 only for arms passing the recorded dev gate. Arms:
`gate_zero`, `shrink`, `x2` (mover offset per PREREG_G_CZ; mover
clubs and frozen offsets live in `arms.py` — the mover set is the
prereg definition evaluated on this corpus: one promoted club per
season, verified against the FNL (id 253) index; `arms.mover_ids`
asserts all four mover names appear in that index).

```text
python3 league/CZ-Liga/engine/goals/run_g_cz.py dev
python3 league/CZ-Liga/engine/goals/run_g_cz.py virgin-metrics
python3 league/CZ-Liga/engine/goals/run_g_cz.py virgin-predict --arm gate_zero
```

Outputs `results_dev.json/.csv`, conditional `results_virgin.json`;
a shipped arm also writes `fitted_params_virgin.json` and
`predictions/g_cz_virgin_predictions.csv` (1H/2H via frozen 0.4509).
