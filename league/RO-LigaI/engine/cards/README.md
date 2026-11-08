# K-RO cards engine

Reads event-unified `yellow_home`/`yellow_away` (= matchFacts card
events, `card == "Yellow"` — the only all-era source; the stats feed
exists only 2025/2026+ and undercounts, EDA F12) and `referee` from
`league/RO-LigaI/data/ro_matches.csv` (phase != ecl_playoff only).
2021/2022 warm-up, scored 2022/2023–2024/2025, gate at **4.5**
(ladder 3.5/4.5/5.5). Arms: `gate_zero`, `x8` (referee covariate,
8-match shrinkage prior). Virgin 2025/2026 conditional on the gate.

```text
python3 league/RO-LigaI/engine/cards/run_k_ro.py dev
python3 league/RO-LigaI/engine/cards/run_k_ro.py virgin --arms gate_zero x8
```

Outputs dev/virgin JSON, fitted params, and (on PASS)
`predictions/k_ro_virgin_predictions.csv` (1H/2H via frozen 0.330).
