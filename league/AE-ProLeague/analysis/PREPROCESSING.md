# Step 2 — Preprocessing: UAE Pro League

Builder: `league/AE-ProLeague/data/build_data.py` (regenerates both CSVs
from the warehouse; asserts the season counts 182×5 + 49 = 959).
Outputs (gitignored by repo norm): `data/ae_matches.csv` (959 rows),
`data/ae_team_matches.csv` (1,918 rows).

## Inclusion rules

- Played matches only (all 959 index rows are played). One row per match,
  keyed by FotMob match id; teams keyed by FotMob team **id** (one id has
  two display names — 209190 "Al Ittihad Kalba"/"Kalba FC").
- The 2 awarded matches (3640606, 4211602) stay in the CSV with
  `awarded=1` and are excluded from every fit, score, and EDA level that
  feeds a gate (precedent: forfeit exclusions in TR/SA builds).
- Season labels exactly as in the warehouse ("2021/2022", …). No phase
  column variation: `phase="regular"` for all rows (verified — no
  play-off competition exists in this feed).

## Column provenance

- Goals: `header.status.scoreStr` (official).
- Count stats (possession, SOT, corners, total shots, big chances, box
  touches, yellows, reds): stats feed `Periods.All`; duplicated keys
  across stat groups agree (extractor takes the flattened map, J.League
  library pattern). `*_1h_*` columns from `Periods.FirstHalf` where
  present (never fabricated where absent).
- Cards target: `yellow_home/away` = stats-feed yellows, `cards_source=
  "stats"` on every row (decision + reason in DATA_UNDERSTANDING §3).
  Event yellows kept as `ev_yellow_*` for the artefact record only.
- HT goals: goal-event minutes ≤45, only where goal events reproduce the
  FT score (`ht_source="events"`; 19 rows flagged otherwise, incl. the
  2 awarded and matches with an empty event list — excluded from the
  goals halves computation only).
- Referee: `matchFacts.infoBox.Referee.text`, empty string where unnamed.
- Stat values arrive as ints or percent-suffixed strings; the extractor
  takes the leading number (J.League `_num` pattern).
