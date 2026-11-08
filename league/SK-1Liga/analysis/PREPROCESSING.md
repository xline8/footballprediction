# Step 2 — Preprocessing (SK-1Liga)

Builder: `league/SK-1Liga/data/build_data.py` (regenerates
`data/sk_matches.csv`, one row per played match, +
`sk_team_matches.csv`, `sk_teams.csv`; CSVs gitignored by repo norm).
Adapted from the CZ-Liga builder; parsing follows the J.League rules.

## Inclusion rules (frozen)

1. Played/finished matches only (all 1,053 index rows are finished).
2. **Phase rule**: `phase` from `general.leagueName` —
   `regular` / `championship` / `relegation` / `playoff`
   (ECL Playoff). `included = phase != playoff` → 1,044 rows
   (192 per complete season, 84 in-progress 2026/2027). The split
   groups are ordinary league matches and are included as ordinary
   rows with the phase flag set (programme precedent: SCO/CY/CZ);
   the ECL play-off ties are one-off cross-group ties between the
   split groups — a different population — and are excluded from
   every fit and scoring window. All modelling, EDA levels for gate
   purposes, and both windows use included rows only.
3. FT score from `header.status.scoreStr` (authoritative; the one
   events mismatch is the empty-events match, DATA_UNDERSTANDING
   defect 4).
4. Season labels exactly as in the warehouse (`2021/2022` style,
   split-year). Last COMPLETE season = **2025/2026** (virgin);
   2026/2027 is in progress (regular phase only so far) and is never
   read by any harness in this build.

## Targets and sources

- Goals: header score. xG columns exist in the schema but are None
  throughout (no xG in this league's feed, ever).
- SOT / corners / possession / total shots: stats feed
  `Periods.All` keys `ShotsOnTarget` / `corners` / `BallPossesion` /
  `total_shots`. Matches without stats (61 early 2021/2022, 5 in
  2023/2024) carry NaN targets and are excluded from those markets'
  scoring (they still count for goals and cards). **Total shots is
  extracted but NOT a buildable target** (level break, Step 6); it
  is also the v5 SOT engine's ratio/level input — the break is
  declared in the S-SK prereg as CZ/RO did.
- Cards target: **event-unified yellows** = count of matchFacts
  events with `card == "Yellow"` per team (`yellow_home/away` in
  the CSV = `ev_yellow_*`). YellowRed and Red events are stored
  separately and are NOT in the target (production cards design
  excludes reds). The stats feed has no cards key in the dev era
  (1 stray match), so the event target is the only all-era source —
  chosen by construction, and audited against the stats feed in
  the virgin era in EDA F6 (agreement 159/192, means 4.016 stats
  vs 4.005 events — no artefact). Stats-feed yellows are kept as
  `stats_yellow_*` for that audit only.
- Period splits: `fh_`/`sh_` stat columns populated only where the
  payload carries them (2025/2026+); never fabricated for earlier
  seasons.
- HT goals / HT yellows: derived from event times (minute ≤ 45,
  stoppage strings like `45+2` parse to 45) in ALL eras
  (`ht_source = events`); used only for the halves constants
  (Step 3) and halves presentation. The one empty-events match
  (defect 4) contributes false zeros here — flagged, immaterial
  (<0.2% of the dev aggregates).
- Referee: `infoBox.Referee.text` stored verbatim (empty string in
  the whole dev era — a feed fact, not a builder gap).
- Team identity: `home_team_id`/`away_team_id` (FotMob ids, stable);
  display names canonicalised to the most recent payload string
  per id (the index's 2026/2027 diacritic variants never enter
  the CSV logic).
