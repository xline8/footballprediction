# PREREG T-AUW — frozen before fitting

Reference is the sibling total-shots Gate Zero/shots-family pattern, adapted to AUW regular-only windows. Training seed 2021/2022; dev evaluation is 2022/2023, 2023/2024, 2024/2025 regular only, n=369; virgin is 2025/2026 regular only, n=110, read once only for dev-passing arms. Finals are excluded; 2026/2027 is reserved/unread.

Target is stats-feed total_shots. Primary line is O27.5 (dev over-rate 49.9%). Arms are A (v1 pattern: ratings + NB + naive ensemble), B (v2 pattern: A + level layer) and C (E9: NB r from a trailing window), exactly as PREREG_T_AU; Gate Zero for this candidate is arm A. No xG, shotmap or xGOT arm is eligible because none has a dev window.

Shared-engine constants (grids, half-lives, clamps, min-sample rules) are carried verbatim in form from the corresponding league/AU-ALeague/prereg/PREREG_T_AU.md and its in-tree engine; only league, windows, lines and frozen halves constants change.

GATE LEGS (frozen): dev gate beats BOTH league base-rate/climatology and naive trailing-10 baselines. Virgin (i) LL <= Gate Zero and <= best baseline; (ii) `|mean predicted − actual| <=1.0pp` clean, within one `SE=sd(p_i−y_i)/sqrt(n)` provisional, otherwise fail; (iii) variant per-season sign check. Both-pass ships lower pooled virgin LL; ties go simpler. Gate Zero dev failure means FAIL and virgin NOT read. Halves on PASS use total-shots 0.467/0.533.
