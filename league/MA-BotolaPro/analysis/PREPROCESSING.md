# Step 2 — Preprocessing: MA-BotolaPro

Builder: `data/build_data.py` (committed; regenerates both CSVs from
the warehouse in the main checkout). One row per played match in
`data/ma_botola_matches.csv` (1,255 rows) plus the long
`data/ma_botola_team_matches.csv` (2,510 rows). CSVs are gitignored
by repo norm; the builder is the reproducible artefact.

## Inclusion rules

- Played matches only, exactly as indexed (all 1,255 rows carry a
  final score). Sorted by (date, match_id).
- Every row is phase `regular` (verified format: 30 rounds, no
  play-off rows). No phase feature anywhere.
- Teams keyed on FotMob team ids; names are display only (four ids
  have two spellings — see DATA_UNDERSTANDING).

## Field rules

- Goals: `header.status.scoreStr`.
- Stats targets (`ShotsOnTarget`, `corners`, `total_shots`,
  `BallPossesion`): stats feed `Periods.All`, home/away as listed.
  Present only in the rich era; null elsewhere. Never fabricated,
  never carried across the era break.
- Cards: event-unified yellows per team = `Yellow` + `YellowRed`
  Card events (RU-1Division convention), stored as `yellow_home` /
  `yellow_away` with `cards_source = "events"` on every row. The
  column is only MEANINGFUL in the rich era: pre-rich-era rows
  mechanically show ~0 plain yellows because the feed carried none,
  and are excluded from every cards window by the era rule below.
- Era flag: `rich_era = 1` iff date >= 2024-11-01 (frozen boundary;
  the Aug–Oct 2024 sporadic rich payloads are excluded by it).
- Half-time goals: from Goal event times (time <= 45 = first half,
  stoppage time rides on the `time` minute + `overloadTime`, so a
  45+5 goal has time 45 and counts first half; a 90+2 goal has time
  90 and counts second half). Valid in all seasons (goal events
  reconcile exactly with scores in 1,255/1,255 matches).
- Half-time yellows: from Card event times the same way
  (`ht_yellows`), meaningful in the rich era only.
- Referee: stored verbatim; empty in all rows.
- `has_period_splits_content` is 0 on every row (no FirstHalf /
  SecondHalf periods exist); `has_shotmap` is 0 on every row.

## Windows frozen here (used by every prereg)

- Goals dev: seed 2021/2022; scored 2022/2023–2024/2025.
  Virgin: 2025/2026. Confirmatory: 2026/2027 (reserved, unread).
- Count markets (SOT, corners, cards, total shots): rich era only.
  Warm-up: rich-era matches 2024-11-01 – 2024-12-31 (64 matches, 55
  with stats) update state, never scored. Scored dev: rich-era
  matches 2025-01-01 – 2025-05-12 (112 matches, 109 with stats).
  Virgin: 2025/2026 (240 matches; 226 with stats). Rows without
  stats are never scored for SOT/corners/total shots and never
  update those targets' state; cards scores every rich-era match
  (events exist for all of them).
