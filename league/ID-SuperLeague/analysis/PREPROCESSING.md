# Step 2 — Preprocessing: Indonesia Super League

Builder: `league/ID-SuperLeague/data/build_data.py` (regenerates both
CSVs from the main checkout's warehouse index + JSONs; data CSVs are
gitignored by repo norm). Output: `id_matches.csv` (1,620 rows) and
`id_team_matches.csv` (3,240 rows).

## Inclusion rules

1. One row per index row for league_id 8983 with
   `header.status.finished` true and not cancelled. All 1,620 index
   rows pass; no row is dropped at this stage.
2. Phase assignment (frozen):
   - `stray_playoff`: index season label "2021/2023" (2 rows). Stored
     under season 2022/2023 (their calendar position) with
     `season_label_raw` keeping the index label.
   - `championship_playoff`: `content.hasPlayoff == True` (8 rows, all
     2023/2024).
   - `regular`: everything else (1,610 rows: 306 × 5 completed seasons
     + 80 transitional).
   Engines and EDA use `regular` rows only.
3. Teams keyed on FotMob team ids from `general.homeTeam/awayTeam`;
   names are display only (renames documented in Step 1 §4.5).

## Column rules

- Goals: from `header.status.scoreStr` (authoritative; event goals
  are kept as audit columns `ev_goals_*` plus the reconciliation flag
  `goals_events_match_score`).
- Stats columns (`BallPossesion`, `total_shots`, `ShotsOnTarget`,
  `corners`, home/away): from `content.stats.Periods.All` content,
  last duplicate key wins; absent → empty. `fh_`/`sh_` columns are
  retained for schema parity and are empty everywhere (no splits
  exist). `has_stats` = all of total_shots/SOT/corners present both
  sides. The corrupted 2023/2024 total-shots values are stored as
  published (the corruption is documented, not silently repaired);
  no engine consumes them because T-ID is not buildable.
- Events: counts by type/card/side from `matchFacts.events.events`.
  `ev_yellow_*` = Yellow + YellowRed events (unified yellows).
  Half-time splits (`ht_*_goals`, `ev_yellow_1h_*`) split the event
  list by order relative to the half-time Half marker, which is
  stoppage-time safe; minute-field fallback only if no marker exists.
- `events_complete` = event list contains at least one Substitution
  and one Half event.
- Cards target columns: `yellow_*` = `ev_yellow_*` and `red_*` =
  `ev_red_*` **only where `events_complete` = 1**, else empty;
  `cards_source` = "events" / "none" accordingly. A truncated feed is
  never allowed to masquerade as a cardless match.
- Referee: `infoBox.Referee.text`, empty in all 1,620 payloads →
  column is empty throughout (kept for schema parity).
- `has_shotmap` = 0 in every row (shots list always empty).

## Season labels

Warehouse labels are kept verbatim in `season` except the two stray
rows above. Last complete season = 2025/2026 (306 regular matches,
2025-08-08 → 2026-05-23). 2026/2027 (80 finished at snapshot) is
transitional/confirmatory and is never loaded by the engines.
