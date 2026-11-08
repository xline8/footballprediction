# S-PT repair

HL-365 season-blocked team shots-for/against ratings use K=8 shrinkage toward the league per-team mean; SOT ratios use the 200-shot league prior. X4 applies square-root xG/shot tilt and X6 applies square-root xGOT/shot tilt from the 2024/25+ era with an eight-match guard. Model probability is 50% NB plus 50% independently computed naive trailing-10 probability. Baselines use HL-270 as specified by the shared protocol.

Virgin: see the market virgin runner (`virgin_*_pt.py`) and `results_virgin.json`; verdict in `league/PT-LigaPortugal/reports/`.
