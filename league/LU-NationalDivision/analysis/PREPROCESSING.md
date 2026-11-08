# Step 2 — Preprocessing: LU-NationalDivision

Builder: `league/LU-NationalDivision/data/build_data.py` (run:
`python3 build_data.py [BASE]`; BASE is the checkout holding the
gitignored warehouse, default this repo root). Output:
`league/LU-NationalDivision/data/lu_matches.csv` (1,296 rows, one per
played match; gitignored by repo norm `*.csv` — the builder script
is the reproducible source).

## Inclusion rules

- **Played matches only.** Every index row is a played match here:
  `header.status.finished` True and a score present in all 1,296
  payloads. No unplayed fixtures exist (contrast SE-Ettan's 2021
  placeholders); CSV count == index count == 1,296, verified.
- **Season labels as in the warehouse** (`2021/2022` … `2026/2027`).
- **Team identity keyed by FotMob team id** (`header.teams[].id`);
  names are carried for readability only (no name canonicalisation
  was needed — ids are stable; team counts per season are 16 in
  every season).
- **Scores are ground truth** from `header.teams[].score`
  (cross-checked against `status.scoreStr` in the builder's
  verification pass; they agree in all 1,296 rows).

## Split-source rules

- **Goals 1H/2H** come ONLY from goal-event times
  (`matchFacts.events.events`, type `Goal`, minute ≤ 45 → 1H,
  > 45 → 2H). Never fabricated, never imputed from the FT score.
- Where the events list is empty AND the scoreline is 0–0 (44
  matches), halves are 0/0 — that is arithmetic, not imputation
  (there are no goals to split).
- Where the events list is empty AND goals were scored (exactly one
  match, 4520839, 2024/25), all four halves columns are left EMPTY
  (missing). That match contributes to every FT analysis and to
  nothing halves-based.
- **No period splits exist for any other market** — `content.stats`
  is absent, so there are no stats-period splits at all. The goals
  halves constant is the only halves object in this league.
- **Red cards** are event-derived descriptive columns
  (`red_cards_home/away`, Red + YellowRed events). They are NOT a
  model target (no yellows exist) and are not used by any candidate.
- **Referee** is carried as an (always empty) string column to record
  the absence; no referee feature is built from it.

## Columns

`match_id, season, date, round, home_team, away_team, home_id,
away_id, home_goals, away_goals, goals_1h_home, goals_1h_away,
goals_2h_home, goals_2h_away, red_cards_home, red_cards_away,
has_events, referee, source_path`

## Verification (re-run of the builder)

- 1,296 rows; seasons 240/240/240/240/240/96; dates 2021-08-07 –
  2026-10-31.
- Halves consistency: `goals_1h_* + goals_2h_* == *_goals` in every
  row where halves are present (1,295/1,296).
- Halves missing in exactly 1 row (4520839).
- Red-card events total 385, matching the raw count.
- Referee non-empty in 0 rows.
