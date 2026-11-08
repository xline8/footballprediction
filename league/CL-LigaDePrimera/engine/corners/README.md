# C-CL corners engine

Reads `data/cl_matches.csv`; seed is 2021 and dev scores 2022–2024 (855 stats matches). The only arm is Gate Zero with the possession-only territorial covariate and beta grid ±{0,.0025,.005,.0075,.010}; the big-chance term is omitted because it is all-null. The primary line is corners 9.5 with ladder 8.5/9.5/10.5. FT-only presentation. Calibration uses actual minus predicted. Run `python3 league/CL-LigaDePrimera/engine/corners/run_c_cl.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
