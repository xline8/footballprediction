# PREREG K-AUW — frozen before fitting

Reference is the sibling cards Gate Zero, with stats-feed yellow_cards as the target. The event-feed yellow artefact is documented: event totals agree in only 10/74, 9/103, 12/139 and 30/145 dev matches, so events are not used. Training seed 2021/2022; dev evaluation is 2022/2023, 2023/2024, 2024/2025 regular only, n=369; virgin is 2025/2026 regular only, n=110, read once only for dev-passing arms. Finals are excluded and 2026/2027 reserved/unread.

Primary line is O2.5 (dev over-rate 41.0%). Arms are Gate Zero and X8 referee strictness, using past stats-feed yellows only and falling back to the base arm when referee identity is missing. X8 is adopted at split-half r=0.424 across 9 referees with >=20 assignments.

Shared-engine constants (grids, half-lives, clamps, min-sample rules) are carried verbatim in form from the corresponding league/AU-ALeague/prereg/PREREG_K_AU.md and its in-tree engine; only league, windows, lines and frozen halves constants change.

GATE LEGS (frozen): dev must beat BOTH league base-rate/climatology and naive trailing-10 baselines. Virgin (i) LL <= Gate Zero and <= best baseline; (ii) calibration <=1.0pp clean, within one `SE=sd(p_i−y_i)/sqrt(n)` provisional, otherwise fail; (iii) variant dev per-season sign check. Both-pass ships lower pooled virgin LL; ties go to simpler arm. Gate Zero dev failure ⇒ FAIL and virgin NOT read. Halves on PASS use yellows 0.314/0.686.
