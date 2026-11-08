# S-RO shots-on-target engine

Reads `league/RO-LigaI/data/ro_matches.csv` (phase != ecl_playoff;
matches without stats-feed SOT are excluded by the loader). Target
`ShotsOnTarget_home + ShotsOnTarget_away`; v5 architecture verbatim
(ridge 100, HL 365, K=8, BB prior P=200, ensemble 50/50 naive-10,
NB r=79.94). Lines 7.5/8.5/9.5, gate at **8.5**. Arms: GZ, RS
(P=20000). X4/X6 not registered (no shotmap in this league).
Dev: 2021/2022 warm-up, scored 2022/2023–2024/2025; virgin 2025/2026
conditional on the dev gate. Declared risk: the raw total-shots
input's counting changes at 2025/2026 (see prereg).

```text
python3 league/RO-LigaI/engine/sot/run_s_ro.py dev
python3 league/RO-LigaI/engine/sot/run_s_ro.py virgin-metrics
```

A shipped arm writes `fitted_params_virgin.json` and
`predictions/s_ro_virgin_predictions.csv` (1H/2H via frozen 0.455).
