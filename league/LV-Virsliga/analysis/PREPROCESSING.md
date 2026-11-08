# Step 2 — Preprocessing: LV-Virsliga

Builder: `data/build_data.py` → `data/lv_virsliga_matches.csv`
(1,011 rows) + `data/lv_virsliga_team_matches.csv` (2,022 rows).
CSVs are gitignored (repo norm); the builder script is committed
and regenerates them from the warehouse.

## Inclusion rules

- Played matches only (every index row carries a final score;
  `general.finished` is true for all 1,011 kept rows).
- **Excluded: the 6 relegation-playoff finals**
  (`leagueRoundName == 'final'`, match ids 4064841, 4064842,
  4365408, 4365409, 4673639, 4673640). They are two-legged ties
  between the 9th-place Virsliga side and a 1. liga side — not
  league matches, and one participant is not a Virsliga team in
  that season. Warehouse 1,017 rows → tables 1,011 rows.
- Season labels are the warehouse calendar-year labels
  ("2021" … "2026") as in the index.
- Teams keyed on FotMob team id, never on name (diacritic drift:
  FK Liepaja/Liepāja id 8016, Grobina/Grobiņa id 662738).

## Split-source rules

- Scores: the index `score` column ("H-A") is authoritative.
  Goal events reconcile with it in 1,010/1,011 kept matches
  (2021 has 17 matches with no events at all; one 2022 match is
  short one goal event).
- Period splits: `FirstHalf` / `SecondHalf` stats are used only
  where present (2025+; 359/359 stats-era matches). Never
  fabricated for 2021–2024.
- Goals 1H: goal-event times (time ≤ 45), where events exist.
- Cards target: **event-unified yellows = Yellow + YellowRed
  events** (RU-1Division / MA convention). The stats
  `yellow_cards` key is NOT the target: it reads 0/0 in 43/180
  2025 matches while events record 187 yellows there. Stats
  yellows are kept in the CSV as `yellow_stats_home/away` for
  audit only. Cards 1H: card-event times.
- SOT / corners / total shots: stats `Periods.All` values
  (2025+ only); 1H values from `Periods.FirstHalf`.
- `big_chance`: carried in the CSV but identically 0 in all 359
  stats-era matches — never used as a covariate.
- Referee: `infoBox.Referee.text`, carried verbatim; empty in
  78% of 2025 matches.
- Shotmap: empty everywhere; no xG column exists in any table.

## Era flags in the CSV

- `stats_era` = 1 for matches dated ≥ 2025-03-05 (first stats
  match), else 0.
- `has_stats_all`, `has_period_splits_content`, `has_events`,
  `has_shotmap` (= 0 everywhere) per match.
- `phase` = "regular" for every kept row (no split phase exists).
