# G-RL2 goals engine

Reads `league/RO-LigaII/data/rl2_matches.csv` (phase !=
`relegation_playoff` only). Dixon-Coles, goals-only (the RL2 source has
no xG columns), hl=270. Dev loads only 2021/2022–2024/2025
(2021/2022 seed); virgin reads 2025/2026 only after the recorded dev
gate. Arms: `gate_zero`, `shrink`.

```text
python3 league/RO-LigaII/engine/goals/run_g_rl2.py dev
python3 league/RO-LigaII/engine/goals/run_g_rl2.py virgin-metrics
python3 league/RO-LigaII/engine/goals/run_g_rl2.py virgin-predict --arm gate_zero
```

Outputs `results_dev.json/.csv`, conditional `results_virgin.json`; a
shipped arm also writes `fitted_params_virgin.json` and
`predictions/g_rl2_virgin_predictions.csv` (1H/2H via frozen 0.457419 / 0.542581).
