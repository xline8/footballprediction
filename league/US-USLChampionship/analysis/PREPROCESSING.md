# Stage A — Preprocessing: USA USL Championship

Run `python3 league/US-USLChampionship/data/build_data.py` (adapts the
US-MLS builder; warehouse JSONs are read from the main checkout via the
same WAREHOUSE_REPO fallback, because the world warehouse is gitignored
and lives there). It filters league_id 8972, sorts chronologically by
(date, match_id), and asserts 2,590 matches and 5,180 team rows at
build time.

Rules:
1. Played matches only; both regular and playoff matches are included
   and flagged. Calendar season labels remain strings (`2021`…`2026`);
   `season_start` is the integer year. 2026 is reserved/incomplete and
   excluded from modelling windows, EDA levels/reliability/halves, and
   gates.
2. Phase uses `general.leagueName`, not `matchRound`: `USL Championship`
   → `regular`, `USL Championship Playoff` → `playoff`; raw league name
   is retained as `fotmob_league_name`. Cross-checked against
   `matchRound`: 0 disagreements.
3. Stats are the `All` period of `content.stats.Periods`. First/second-
   half fields (`fh_*`, `sh_*`) are retained only where the feed supplies
   period splits (0% in 2021–22, 92.7% in 2023, 100% from 2024); absent
   splits stay null — never fabricated.
4. Missing data stays missing (NaN) with provenance flags; targets are
   never imputed and absent feeds are never read as zeros. Shotmap
   aggregates (`sm_*`) are null everywhere because no match carries a
   shotmap; `expected_goals*` columns are null everywhere because the
   stats feed never carries xG in this league.
5. HT goals and event cross-checks come from match events
   (`ht_source="events"` where derivable). Playoff shootout attempts, if
   any, are counted separately (`n_shootout_shots`) and excluded from
   shot aggregates — moot here (no shotmap).
6. Cards — the stats-vs-events audit, run before any target choice:

   | season | n | exact-match rate | mean (stats − events) yellows |
   |---|---:|---:|---:|
   | 2021 | 510 | 0.314 | +3.218 |
   | 2022 | 472 | 0.140 | +4.333 |
   | 2023 | 423 | 0.714 | −0.149 |
   | 2024 | 423 | 0.719 | −0.196 |
   | 2025 | 375 | 0.835 | −0.083 |

   The artefact in this league runs the opposite way from
   IT-SerieB/ES/AR: here the EVENT feed is the broken one — it contains
   almost no Card events in 2021–22, so an events target would be
   unusable in the warm-up and the first dev season. In the seasons
   where events exist (2023–25) stats agree closely (exact 71–83%,
   mean diff −0.08…−0.20, stats marginally lower). Unified target:
   `yellow_*` = stats-feed `yellow_cards_*`, `cards_source="stats"`
   for all rows (the US-MLS precedent). Event counts are kept as
   cross-check columns (`ev_yellow_*`); in event counts a YellowRed is
   a red, not a yellow.
   One caution recorded: stats-feed yellows jump from 3.24/match (2021)
   to 4.33 (2022) and 4.67–4.91 (2023–24). Whether that is a real
   disciplinary change or a 2021 feed undercount cannot be separated
   from this corpus; 2021 is warm-up only and is never scored, so the
   ambiguity does not touch any gate.
7. Team identity is FotMob `team_id` everywhere (renames on stable ids
   documented in DATA_UNDERSTANDING.md).
