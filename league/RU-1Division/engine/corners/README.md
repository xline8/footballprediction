# C-RU1 corners engine

Reads `data/ru1_matches.csv`; seed is 2021/2022 and dev scores 2022/2023–2024/2025 (855 stats matches). The only arm is Gate Zero with the possession-only territorial covariate and beta grid ±{0,.0025,.005,.0075,.010}; the big-chance term is omitted because it is all-null. The primary line is corners 8.5 with ladder 7.5/8.5/9.5. FT-only presentation. Calibration uses actual minus predicted. Run `python3 league/RU-1Division/engine/corners/run_c_ru1.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
