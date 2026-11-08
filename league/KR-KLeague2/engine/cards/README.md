# KR2 cards engine

Run `python3 league/KR-KLeague2/engine/cards/run_k_kr2.py dev` or `virgin --arms gate_zero`. The loader uses stats-feed yellows and excludes 2021/2022 entirely.

Shared mechanics live in ../count_common.py and ../market_runner.py: damped IPF Poisson ratings (step 0.25 x 100; the goals-scale 0.7 x 14 step oscillates on count targets), centred so unseen teams predict the league level, frozen moment-r for the NB totals. Virgin mode refuses to run when Gate Zero failed the dev gate.
