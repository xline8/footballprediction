# G-USLL1 goals engine

Dixon-Coles port (via US-USLChampionship/US-MLS) for
`data/usll1_matches.csv`, goals-only (no xG exists in this league).
Only `phase == "regular"` rows are fitted or scored (frozen phase rule).
Arms: `gate_zero`, `shr` (thin-team lambda shrinkage). Warm-up 2021,
scored dev 2022-2024 (n=489), virgin 2025 (n=210, coordinator-gated).

Run: `python3 run_g_usl.py dev` / `virgin-metrics` / `virgin-predict --arm X`
(virgin commands only for dev-passing arms, per prereg).
Predictions use the frozen 1H share 0.468.
