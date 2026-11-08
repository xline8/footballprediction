# PREREG G-AUW — frozen before fitting

Reference is the AU-ALeague/J1 goals Dixon-Coles Gate Zero, adapted to AUW regular-season rows. Training seed 2021/2022; dev evaluation is season-blocked walk-forward over 2022/2023 (99), 2023/2024 (132), 2024/2025 (138), n=369. Virgin is 2025/2026 regular only (n=110), read once only for dev-passing arms. 2026/2027 is reserved and unread. Finals are excluded everywhere.

Target is goals-only DC: no xG blend because xG is absent from every dev row. Primary line is OU2.5 (dev Over rate 56.7%). Arms are Gate Zero and SHRINK. SHRINK applies the sanctioned expansion/new-team protection: for each team with fewer than 6 prior in-league matches, `a*=n/6` and `d*=n/6`; n=0 remains league mean. No other change is permitted.

Shared-engine constants (grids, half-lives, clamps, min-sample rules) are carried verbatim in form from the corresponding league/AU-ALeague/prereg/PREREG_G_AU.md and its in-tree engine; only league, windows, lines and frozen halves constants change.

GATE LEGS (frozen): dev gate beats BOTH baselines (league base rate/climatology + naive trailing-10 as applicable). Virgin legs: (i) LL <= Gate Zero's and <= best baseline's; (ii) `|mean predicted − actual| <= 1.0pp` is clean PASS, breach within 1 SE where `SE=sd(p_i−y_i)/sqrt(n)` is PROVISIONAL PASS, else FAIL; (iii) variant per-season sign check. Both-pass ships lower pooled virgin LL; ties go to simpler arm. Gate Zero dev failure means candidate FAILS and virgin is NOT read. Halves on PASS are FT + 1H/2H via constants goals 0.459 and 0.541.
