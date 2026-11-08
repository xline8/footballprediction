# T-EG total-shots engine
Reads `data/eg_matches.csv`, target `total_shots_home + total_shots_away`. Shots-family port (T-J1/T-SA pattern): A = v1 ratings+NB+naive ensemble, B = + level layer (cell tuned on 2022/2023, the first scored season), C = E9 trailing-r (window 200). Per-match walk-forward; warm-up 2021/2022, scored 2022/2023–2024/2025 (n=826 with target). Primary line 22.5, ladder 21.5/22.5/23.5. Virgin 2025/2026 read once for dev-passers; halves via frozen 0.4459.
Run: `python3 league/EG-PremierLeague/engine/total_shots/run_t_eg.py dev` then `virgin`.
