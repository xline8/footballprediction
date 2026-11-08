# Step 2 — Preprocessing (SK-2Liga)

Builder: `league/SK-2Liga/data/build_data.py` (regenerates
`data/sk2_matches.csv`, one row per finished match, +
`sk2_team_matches.csv`, `sk2_teams.csv`; CSVs gitignored by repo norm).
Adapted from the SK-1Liga builder; parsing follows the J.League rules.
The warehouse lives in the main repo; the builder reads it by absolute
path (`/home/hatch/workspace/footballprediction/data_enrichment/`).

## Inclusion rules (frozen)

1. Played/finished matches only (`header.status.finished`): 1,143 of
   1,269 index rows. The 126 unfinished rows are stale pre-match
   snapshots (DATA_UNDERSTANDING defect 1) and are excluded from
   every fit, scoring window, level and reliability computation.
2. **No phase rule.** The league has no split groups or play-off ties
   (single round-robin, rounds 1–30); every finished row is included
   as an ordinary league match. The short 2024/2025 season (14 clubs,
   26 rounds) is used whole.
3. FT score from `header.status.scoreStr` (authoritative; the two
   event-block defects do not touch the score).
4. Season labels exactly as in the warehouse (`2021/2022` style,
   split-year). Last COMPLETE season = **2025/2026** (virgin);
   2026/2027 is in progress (rounds 1–16) and is never read by any
   harness in this build.

## Targets and sources

- Goals: header score. xG columns do not exist (no xG in this
  league's feed, ever); the goals model is goals-only.
- SOT / corners / cards / total shots / possession: **no source**.
  `content.stats` is empty in all 1,269 payloads, so no stat columns
  are built at all. Those markets are NOT BUILDABLE (Step 6).
- HT goals: derived from matchFacts event times (minute ≤ 45) in
  the 610 events matches (`ht_source = events`); 0 where no events
  exist, with `has_events` / `events_reconciled` flags carried so no
  consumer mistakes a feed zero for a real 0. Used only for the
  halves constant (Step 3) and halves presentation. The two
  defect matches (4553752, 4838232) have `events_reconciled = 0`
  and contribute nothing to halves.
- Referee: `infoBox.Referee.text` stored verbatim (empty string in
  all 1,143 finished matches — a feed fact, not a builder gap).
- Team identity: `home_team_id`/`away_team_id` (FotMob ids, stable);
  display names canonicalised to the most recent payload string
  per id (the 2026/2027 diacritic variants never enter the CSV
  logic). Sub-league id (`general.leagueId`) and parent id
  (`general.parentLeagueId` = 8973) are stored per row for
  traceability; they play no modelling role.
