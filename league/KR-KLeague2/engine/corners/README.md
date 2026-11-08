# KR2 corners engine

Run `python3 league/KR-KLeague2/engine/corners/run_c_kr2.py dev` or `virgin --arms gate_zero,x7`. Inputs are regular-phase target-complete corner rows; outputs are JSON/CSV results and prediction artifacts.

Shared mechanics live in ../count_common.py and ../market_runner.py: damped IPF Poisson ratings (step 0.25 x 100; the goals-scale 0.7 x 14 step oscillates on count targets), centred so unseen teams predict the league level, frozen moment-r for the NB totals. Virgin mode refuses to run when Gate Zero failed the dev gate.
