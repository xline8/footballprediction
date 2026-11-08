# PREREG C-AUW — frozen before fitting

Reference is the sibling corners_v3 Gate Zero with possession+big-chance covariates, adapted to AUW regular-only windows. Training seed 2021/2022; dev evaluation 2022/2023, 2023/2024, 2024/2025 regular only, n=369; virgin 2025/2026 regular only, n=110, read once only for dev-passing arms. Finals are excluded; 2026/2027 is reserved/unread.

Target is stats-feed corners. Primary line is O9.5 (dev over-rate 46.7%). Arms are Gate Zero and one X7 box-touch multiplier arm. X7 is eligible because touches-for reliability is r=0.876. X9 possession+big-chance is part of Gate Zero and remains the reference pattern.

Shared-engine constants (grids, half-lives, clamps, min-sample rules) are carried verbatim in form from the corresponding league/AU-ALeague/prereg/PREREG_C_AU.md and its in-tree engine; only league, windows, lines and frozen halves constants change.

GATE LEGS (frozen): dev gate beats BOTH league base-rate/climatology and naive trailing-10 baselines. Virgin (i) LL <= Gate Zero and <= best baseline; (ii) calibration absolute error <=1.0pp clean, within one `SE=sd(p_i−y_i)/sqrt(n)` provisional, otherwise fail; (iii) variant per-season sign check. Both-pass ships lower pooled virgin LL; ties go simpler. Gate Zero dev failure fails the candidate and virgin is not read. Halves on PASS use corners 0.480/0.520.
