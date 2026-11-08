# Step 2 — Preprocessing (CZ-Liga)

Builder: `league/CZ-Liga/data/build_data.py` (regenerates
`data/cz_matches.csv`, one row per played match, 166 columns, +
`cz_team_matches.csv`, `cz_teams.csv`; CSVs gitignored by repo norm).
Adapted from the RO-LigaI builder; parsing follows the J.League rules.

## Inclusion rules (frozen)

1. Played/finished matches only (all 1,492 index rows are finished).
2. **Phase rule**: `phase` from `general.leagueName` —
   `regular` / `championship` / `relegation` / `placement`.
   `included = phase != placement` → 1,461 rows (270 per complete
   season, 111 in-progress 2026/2027). All modelling, EDA levels for
   gate purposes, and both windows use included rows only.
3. FT score from `header.status.scoreStr` (authoritative; see
   DATA_UNDERSTANDING defect 3 for the one events mismatch).
4. Season labels exactly as in the warehouse (`2021/2022` style,
   split-year). Last COMPLETE season = **2025/2026** (virgin);
   2026/2027 is in progress (regular phase only so far) and is never
   read by any harness in this build.

## Targets and sources

- Goals: header score. xG columns exist in the schema but are None
  throughout (no xG in this league's feed, ever).
- SOT / corners / possession / total shots: stats feed
  `Periods.All` keys `ShotsOnTarget` / `corners` / `BallPossesion` /
  `total_shots`. Matches without stats (11 included) carry NaN targets
  and are excluded from those markets' scoring (they still count for
  goals). **Total shots is extracted but NOT a buildable target**
  (level break, Step 6); it is also the v5 SOT engine's ratio/level
  input — the break is declared in the S-CZ prereg as RO did.
- Cards target: **event-unified yellows** = count of matchFacts events
  with `card == "Yellow"` per team (`yellow_home/away` in the CSV =
  `ev_yellow_*`). YellowRed and Red events are stored separately and
  are NOT in the target (production cards design excludes reds).
  Stats-feed yellows are kept as `stats_yellow_*` for the artefact
  audit only.
- Period splits: `fh_`/`sh_` stat columns populated only where the
  payload carries them (2025/2026+); never fabricated for earlier
  seasons.
- HT goals / HT yellows: derived from event times (minute ≤ 45,
  stoppage strings like `45+2` parse to 45) in ALL eras (`ht_source =
  events`); used only for the halves constants (Step 3) and halves
  presentation. The one disallowed-goals match (defect 3) inflates
  its own HT event counts — presentation only, noted in the verdict
  if the match's row ships.
- Referee: `infoBox.Referee.text` stored verbatim (empty string in
  the whole dev era — a feed fact, not a builder gap).
- Team identity: `home_team_id`/`away_team_id` (FotMob ids, stable);
  display names canonicalised to the most recent string per id.
