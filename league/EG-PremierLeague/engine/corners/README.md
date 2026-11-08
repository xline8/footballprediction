# C-EG corners engine
Reads `data/eg_matches.csv`, target total corners. Production model_corners_v3 port. Per-season season-blocked fits over the walk-forward feature builder; warm-up 2021/2022, scored 2022/2023–2024/2025 (n=826 with target). Primary line 8.5, ladder 7.5/8.5/9.5. Arms: gate_zero (X9 possession/big-chance multiplier), x7 (opp-box touches multiplier). Virgin 2025/2026 read once for dev-passers; halves via frozen 0.4604.
Run: `python3 league/EG-PremierLeague/engine/corners/run_c_eg.py dev` then `virgin --arms gate_zero x7`.
