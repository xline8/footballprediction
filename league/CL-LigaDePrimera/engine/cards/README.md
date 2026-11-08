# K-CL cards engine

Reads event-unified `ev_yellow_home + ev_yellow_away` from `data/cl_matches.csv`; seed is 2021 and dev scores 2022–2024 (720 matches). The only arm is Gate Zero; referee/x8 is removed. The primary line is cards 5.5 with ladder 4.5/5.5/6.5. FT-only presentation. Calibration uses actual minus predicted. Run `python3 league/CL-LigaDePrimera/engine/cards/run_k_cl.py dev`.

The dev runner intentionally has no virgin command; virgin evaluation is coordinator-controlled.
