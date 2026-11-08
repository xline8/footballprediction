# Stage A — Preprocessing: USA USL League One

The builder filters league 9296, sorts chronologically by date and match_id,
and asserts 1,174 finished, scored matches. The CSV has one row per match;
the team CSV has two rows per match and is keyed on `team_id`.

Rules:

1. Played/finished matches only. Both regular and playoff rows are retained
   and carry a phase flag. Calendar season labels remain strings. Playoff
   rows are excluded from every fitting and scoring window; 2026 is reserved
   and excluded as in-progress inventory.
2. Phase is derived from the league-name suffix and is retained with the raw
   league name. It is not inferred from a missing or ambiguous round.
3. Stats use the `All` period. First/second-half values are retained only
   when supplied by the feed. Splits are never fabricated; absent splits stay
   null. Frozen half shares are presentation constants applied to FT
   predictions only.
4. Missing stats rows stay in the match CSV. Goals can use a row with missing
   stats; each non-goal market excludes the row when its own target is absent.
   Shotmap and xG fields remain absent/null because coverage is 0% everywhere.
5. Cards validity is explicit: `cards_target_valid` is true only when the
   season is at least 2023 and the stats-feed `yellow_cards` key is present.
   The reason is recorded as the season/key rule, not inferred from zero.
   Unified yellows are the stats-feed target on valid rows only. Period-split
   cards use consistency-filtered rows where `fh + sh == All`.
6. The cards artefact is bidirectional early: stats-feed yellows are broken
   in 2021–22, while the event feed has no card events in 2021–2025. Thus
   neither feed can rescue 2021–22. Valid regular card rows are 191 (2023),
   122 (2024), and 210 (2025). The 2024 regular exceptions are 8 matches
   with stats but no yellow_cards key, plus 2 without stats.
7. Team rows are keyed on `team_id`; no name-based identity repair is needed.

The missing-stats match IDs are 3560112 (2021), 4096791 (2023), and
4380894 plus 4380900 (2024). These remain available to goals and are
excluded per-market where the target is absent.
