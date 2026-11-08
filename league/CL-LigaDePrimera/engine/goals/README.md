# G-CL goals engine

Reads `data/cl_matches.csv`; seed is 2021 and dev scores 2022–2024 (720 matches). Arms are Gate Zero and SHRINK. The X1 blend falls back to goals-only because xG is null on every CL-LigaDePrimera row. Calibration uses actual minus predicted. Run `python3 league/CL-LigaDePrimera/engine/goals/run_g_cl.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
