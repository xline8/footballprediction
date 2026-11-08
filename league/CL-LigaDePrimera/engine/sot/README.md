# S-CL shots-on-target engine

Reads `data/cl_matches.csv`; seed is 2021 and dev scores 2022–2024 (855 stats matches). Arms are GZ and RS; X4 is disabled. The primary line is SOT 8.5 with ladder 7.5/8.5/9.5. FT-only presentation; no halves constants or columns exist. Calibration uses actual minus predicted. Run `python3 league/CL-LigaDePrimera/engine/sot/run_s_cl.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
