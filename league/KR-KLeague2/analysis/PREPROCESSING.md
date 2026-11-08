# Phase 2 — Preprocessing: KR-KLeague2

Builder: `league/KR-KLeague2/data/build_data.py` (adapted from the
KR-KLeague1 builder; regenerates `kr2_matches.csv` +
`kr2_team_matches.csv`, both gitignored, from the warehouse index in
the main checkout). One row per played match; all 1,407 index rows are
finished, so rows in = rows out (asserted in the builder).

Inclusion rules (frozen):

- Population for every model: `phase == "regular"` only. The 10
  play-off rows (2 per season 2021–2025) stay in the CSV flagged
  `phase=playoff` and are excluded from levels, fitting, and scoring.
- Scores from `header.status.scoreStr`. HT goals from Goal events
  (events exist in 100% of 2021 and ≥91% of later seasons).
- Team stats from `content.stats.Periods` (All / FirstHalf /
  SecondHalf). Period splits are used only where the FirstHalf block
  is present and non-null; never fabricated.
- Cards target: STATS-feed yellows only (`yellow_cards` stat), frozen
  after the artefact check in DATA_UNDERSTANDING.md. Event-feed yellow
  counts are kept as `ev_yellow_*` audit columns and are never used as
  the target (they are identically zero for 2022–2025). Cards
  population: 2023–2025 only (2021 no stats; 2022 stats-yellows
  artefact era).
- Stats-market targets (SOT, corners, total shots) exist only where
  the stats block carries them: 2022–2025 minus the 8 identified
  missing rows; matches without the target are excluded from that
  market's fitting and scoring (never imputed).
- Referee from `matchFacts.infoBox.Referee.text` (sparse: 10–52% by
  season; see FEATURES.md X8 drop).
- Season labels are the warehouse labels (calendar years). Team
  identity is the FotMob team ID; name/ID mapping verified 1:1.
