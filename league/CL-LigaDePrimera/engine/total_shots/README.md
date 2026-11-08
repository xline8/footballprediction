# T-CL total-shots engine

Reads `data/cl_matches.csv`; seed is 2021 and dev scores 2022–2024 (855 stats matches). Arms are A, B, and C. The primary line is total shots 25.5 with ladder 24.5/25.5/26.5. FT-only presentation; no halves constant or columns exist. Calibration uses actual minus predicted. Run `python3 league/CL-LigaDePrimera/engine/total_shots/run_t_cl.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
