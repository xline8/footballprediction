# T-RU total-shots engine

Reads `data/ru_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (720 matches). Arms are A, B, and C. The primary line is total shots 25.5 with ladder 24.5/25.5/26.5; frozen half split is 0.4602/0.5398. Calibration uses actual minus predicted. Run `python3 league/RU-PremierLeague/engine/total_shots/run_t_ru.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
