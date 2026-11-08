# Step 2 — Preprocessing (RO-LigaI)

Builder: `league/RO-LigaI/data/build_data.py` (regenerates
`ro_matches.csv` + `ro_team_matches.csv` from the warehouse index;
CSVs are gitignored, the builder is committed). One row per played
match, n = 1,701, ids unique (asserted in the builder).

## Inclusion rules (frozen)

1. Played matches only (`header.status.finished`); FT score from
   `header.status.scoreStr`.
2. Phase from `general.leagueId` sub-tournament name:
   regular / championship / relegation / ecl_playoff.
   **Modelling inclusion: phase != ecl_playoff** (n = 1,694;
   315/complete season, 119 in 2026/2027). ECL rows stay in the CSV
   flagged, for audit.
3. Season labels exactly as in the warehouse index
   ("2021/2022" … "2026/2027").

## Column rules

- Team stats from `content.stats.Periods` (All / FirstHalf /
  SecondHalf) flattened per key; a key absent in a match's era is
  None, never fabricated. Period splits exist only 2025/2026+.
- **Cards target (event-unified, frozen before fitting)**: 
  `yellow_home/away` = count of `matchFacts` events with
  `type == "Card"` and `card == "Yellow"` (straight yellows only),
  for every season. `red_*` = Red + YellowRed events. Stats-feed
  card counts are preserved as `stats_yellow_*` / `stats_red_*`
  (rich era only) purely for the artefact audit in
  DATA_UNDERSTANDING. Rationale: events are the only all-era source
  AND the stats feed measurably undercounts where both exist.
- HT goals from goal events (`time <= 45`), `ht_source = events`.
- Total shots: raw `total_shots` as published, plus `blocked_shots`
  where the rich feed has it. No cross-era adjustment is applied —
  the definition break is handled at candidate level (T-RO not
  built), not by silently rewriting the target.
- Referee from `matchFacts.infoBox.Referee.text` (None where absent).
- Shotmap aggregates: shotmap is empty in all 1,701 files;
  `has_shotmap = 0` throughout (recorded, not hidden).
- xG columns (`expected_goals*`): None throughout (key never
  published for this league).
