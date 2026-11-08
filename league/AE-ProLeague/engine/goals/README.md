# G-AE goals engine
Dixon-Coles port (production model_v2 pattern, goals-only — no xG exists
in this league), arms gate_zero + shrink (thin-history shrinkage).
Reads `league/AE-ProLeague/data/ae_matches.csv`; awarded rows excluded.
Dev: `python3 run_g_ae.py dev` (seed 2021/2022, scored 2022/2023-2024/2025).
Virgin: `python3 run_g_ae.py virgin` (refuses arms failing the dev gate).
Prereg: `league/AE-ProLeague/prereg/PREREG_G_AE.md`.
