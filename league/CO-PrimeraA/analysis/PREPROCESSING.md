# Step 2 — Preprocessing: CO-PrimeraA

Builder: `league/CO-PrimeraA/data/build_data.py` (committed;
regenerates both CSVs from the warehouse in the main checkout).
Outputs (gitignored): `data/co_primeraa_matches.csv` (2,582 rows,
one per played match) and `data/co_primeraa_team_matches.csv`
(5,164 team rows).

## Inclusion rules

- League_id 274 index rows only; a row enters the CSV iff
  `header.status.finished` is true. At build time (2026-11-09) that
  is all 2,582 rows — the builder ASSERTS this and the per-season
  counts, so a warehouse refresh that changes the corpus fails the
  build instead of silently changing it.
- FT score from `header.teams[].score` (cross-checked in EDA against
  goal events: exact in 99.9% of matches).
- 2026 - Clausura rows are in the CSV but are excluded by every
  consumer (in-progress tournament); engines load explicit season
  lists, never "everything except".

## Column rules

- Stats from `content.stats.Periods` (All + FirstHalf): SOT, corners,
  total shots, yellows/reds, big chances, possession, opp-box
  touches, fouls, offsides, keeper saves, and the expected_goals
  family — blank where the feed lacks the key (never fabricated,
  never carried across matches). Period splits are taken only where
  the FirstHalf block exists.
- Events from `matchFacts.events`: goal events give HT goals only on
  the event-exact subset (`events_exact` = 1 and `ht_source` =
  "events"); card events give `ev_yellow_*` (Yellow only) and
  `ev_yellow_inc2nd_*` (Yellow + YellowRed = the unified cards
  target), plus first-half unified yellows.
- Shotmap aggregates (regulation periods only; own goals credited to
  the opponent, per the jleague_lib rule): shot counts, ΣxG,
  ΣxGOT + its denominator, per side. Blank-era matches carry zeros
  with `n_shotmap` = 0 — consumers must key on `n_shotmap` /
  `has_xg`, never on the aggregates alone.
- `phase` ∈ {regular, quadrangular, final} from the payload
  Tournament name + round strings; `tournament` ∈ {apertura,
  clausura} from the season label. Season labels are the warehouse
  labels verbatim ("2025 - Clausura").
- Identity is team_id; display names canonicalised to the id's most
  frequent spelling. Engines key on team_id where the pattern allows
  and on the canonicalised names otherwise.
- `home/away_mover_up`: club absent from Primera A in the previous
  calendar year AND present in (finished) Primera B that year.
  `home/away_absent_prev`: absent from A regardless of source.
  Both are fixture facts known before the season starts.
- `referee` from `matchFacts.infoBox.Referee.text` ("" where absent);
  `stadium` / `stadium_city` from `infoBox.Stadium`.

## Frozen target decisions (from DATA_UNDERSTANDING, pre-fitting)

- Cards target = event-unified yellows, era 2023 - Apertura onward
  only. The stats-feed yellows are not a target anywhere.
- Goals target = header score (all eras). SOT / corners / total
  shots targets = stats feed (all eras; the single stats-missing dev
  match, 2022 - Apertura, is excluded from count scoring only).
- xG / shotmap fields are record-only in this build: no target, no
  feature (era starts at the virgin boundary).
