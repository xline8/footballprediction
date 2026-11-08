# G-RU goals engine

Reads `data/ru_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (720 matches). Arms are Gate Zero and SHRINK. The primary market is OU2.5. Calibration uses actual minus predicted. Run `python3 league/RU-PremierLeague/engine/goals/run_g_ru.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
