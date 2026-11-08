# PREREG S-AUW — frozen before fitting

Reference is the sibling SOT v5 Gate Zero, adapted to AUW regular-only windows. Training seed 2021/2022; dev evaluation is 2022/2023, 2023/2024, 2024/2025 regular only, n=369; virgin is 2025/2026 regular only, n=110, read once only for dev-passing arms. Finals are excluded everywhere and 2026/2027 is reserved/unread.

Target is stats-feed ShotsOnTarget. Primary line is O10.5 (dev over-rate 52.4%). Arms are Gate Zero (v5 unmodified) and RS (Gate Zero with the Beta-Binomial prior raised P = 200 -> 20,000, exactly as PREREG_S_AU); no xG/shot or xGOT arm can form a dev window. Cards are never substituted for SOT.

Shared-engine constants (grids, half-lives, clamps, min-sample rules) are carried verbatim in form from the corresponding league/AU-ALeague/prereg/PREREG_S_AU.md and its in-tree engine; only league, windows, lines and frozen halves constants change.

GATE LEGS (frozen): dev gate beats BOTH baselines (league base rate/climatology + naive trailing-10). Virgin: (i) LL <= Gate Zero and <= best baseline; (ii) `|mean predicted − actual| <= 1.0pp` clean PASS, within one `SE=sd(p_i−y_i)/sqrt(n)` PROVISIONAL PASS, otherwise FAIL; (iii) variant dev per-season sign check. Both-pass ships lower pooled virgin LL; ties go to the simpler arm. Gate Zero dev failure ⇒ FAIL and virgin NOT read. Halves on PASS: FT, 1H and 2H using SOT 0.469/0.531.
