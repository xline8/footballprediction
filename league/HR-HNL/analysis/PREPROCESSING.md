# Step 2 — Preprocessing: HR-HNL

Builder: `data/build_data.py` (adapted from the FI-Veikkausliiga builder,
itself from `league/jleague_lib.py`). Output (gitignored, reproducible):
`data/hr_matches.csv` (964 rows) + `data/hr_team_matches.csv` (1,928 rows).

## Rules

1. **Inclusion**: index rows with league_id = 252 whose payload has
   `header.status.finished` true — all 964 (900 in the five complete
   seasons + 64 played so far in 2026/2027). The in-progress season's
   rows are in the CSV for inventory completeness but are excluded by
   every harness season filter; no engine may load them.
2. **Score**: FT goals from `header.status.scoreStr`.
3. **Team identity**: FotMob team ids (`general.homeTeam.id` /
   `awayTeam.id`); names recorded as published (two ids have diacritic
   name variants — 10165, 187866 — never merged or split by name).
4. **Stats**: `content.stats.Periods` flattened per period
   (All / FirstHalf / SecondHalf); values from each stat's `stats`
   [home, away] pair. A stat absent from a payload stays empty — never
   imputed, never fabricated. Period-split columns exist only where the
   payload carries FirstHalf/SecondHalf (0 matches in 2021/2022,
   51 in 2022/2023, all from 2023/2024).
5. **Halves from events**: HT goals counted from Goal events with
   `time <= 45` (45 = first half incl. stoppage); the same rule gives
   event 1H yellows (meaningful only from 2023/2024 — before that the
   event feed has no yellow events).
6. **Cards recorded from BOTH sources, never merged**: stats-feed
   `yellow_cards`/`red_cards` (→ `yellow_*`, `stats_yellow_*`) and
   event-derived unified yellows (`ev_yellow_*`: Card events with card
   in {Yellow, YellowRed}). The modelling-target decision is frozen in
   PREREG_K_HR (outcome: not built — era definition break, EDA F6).
7. **Referee**: `content.matchFacts.infoBox.Referee.text` as published
   (empty string where unnamed).
8. **Shotmap**: none exists in this league (0/964); the `sm_*` columns
   are structural zeros carried for schema compatibility with the
   programme's other league CSVs and are used by nothing.
9. **Season labels** are the warehouse's split-year labels
   ("2021/2022", …). Rounds are `general.matchRound` (1..36).
10. **Phase**: "regular" for every row — HNL has no split/play-off
    phase (Step 1); `league_name` records the payload's own league
    name ("1. Division" → "HNL" rename) per row.
