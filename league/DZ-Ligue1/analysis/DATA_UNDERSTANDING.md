# Step 1 — Data Understanding: Algeria Ligue 1 (FotMob 516)

Corpus: `data_enrichment/fotmob_world/Algeria/Ligue 1/` — 1,332
matchDetails JSONs, seasons 2021/2022 → 2026/2027 (partial), one tier.
No other Algerian league is in the warehouse, so no parent/sibling
tier exists for a mover prior (see FEATURES.md X2). Inventory: the
content scan in `analysis/eda_numbers.py` (raw results in
`analysis/inventory_summary.json`) plus the coordinator's
payload-level scan of all 1,332 files. Every number below was
measured on the files, never taken from the index's `has_*` flags —
which are `False` for all 1,332 rows on stats/shotmap/period-splits
and are confirmed by content here (unlike other leagues, the flags
happen to be right for DZ — but the verification is by content, as
the program requires).

## 0. Integrity headline

- 1,332 index rows = 1,332 files on disk = 1,332 unique match ids. No
  duplicates, nothing on disk missing from the index, nothing in the
  index missing on disk. All scores parse.
- `header.teams[].score` equals the index `score` on **1,332/1,332**.
  Goal-event counts reproduce the official score in 1,331/1,332
  matches (the single exception is the awarded match, §5 — the
  header/index score is the source of truth).
- All 1,332 matches are `finished`. One match is `awarded`
  (4366461, §5); none is `cancelled`.

## 1. Payload anatomy (one matchDetails JSON)

| Section | Contents | Modelling relevance |
|---|---|---|
| `general` | matchId, leagueId 516, leagueName "Ligue 1", parentLeagueId 516, matchRound (1–34), team ids/names, coverageLevel `lower`, matchTimeUTC | identity, round structure |
| `header.teams` | home/away team **ids + names + scores** | FT score, team identity (ids) |
| `header.status` | utcTime, red-card counts, half timestamps, `awarded` flag, reason (`FT` / `AW`) | kickoff, anomaly flags |
| `content.matchFacts.events.events` | Goal (scorer, `isHome` = credited side, minute, `newScore`), Card (`card` ∈ Red/YellowRed only — see §4), Half (time 45/90, **with `homeScore`/`awayScore` at HT**) | HT derivation, dismissals |
| `content.matchFacts.infoBox` | Match Date, Tournament (id 516, parentLeagueId 516, round), Stadium (null), Referee (key present, **text always empty**), Attendance (null) | round, no usable referee/stadium data |
| `content.stats` | key present; `Periods` blocks carry **no stat rows in any payload** | SOT/corners/cards/xG targets: absent |
| `content.shotmap.shots` | key present; **empty list in every payload** | no per-shot data |
| `content.lineup` | key present; a lineup block exists in 10 payloads, but only ONE (4040543) carries starters (11+11); the other 9 are empty shells (0 starters) | effectively no lineup data |
| `content.playerStats` | key present; empty in every payload | no player data |
| `content.table`, `h2h`, `momentum` | standings snapshot, head-to-head, momentum flag | not used (post-match snapshots; leakage risk) |

## 2. Coverage matrix (share of matches with real content, %)

| Season | n | Stats (non-empty) | Shotmap (shots>0) | Events | HT score | Lineups (starters) | Player stats | Referee (non-empty text) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 306 | **0** | **0** | 88.2 | 88.2 | 0 | 0 | **0** |
| 2022/2023 | 240 | **0** | **0** | 89.2 | 89.2 | 0.4 (1 match) | 0 | **0** |
| 2023/2024 | 240 | **0** | **0** | 89.2 | 89.2 | 0 | 0 | **0** |
| 2024/2025 | 240 | **0** | **0** | 87.5 | 87.5 | 0 | 0 | **0** |
| 2025/2026 | 240 | **0** | **0** | 92.1 | 92.1 | 0 | 0 | **0** |
| 2026/2027 (partial) | 66 | **0** | **0** | 92.4 | 92.4 | 0 | 0 | **0** |
| **Total** | **1,332** | **0** | **0** | **89.3** | **89.3** | **0.08 (1 match)** | **0** | **0** |

Reading of the matrix:

- **Algeria Ligue 1 is a scores-only corpus, cleanly.** No season
  has any stats, shotmap, player-stat or referee content at all.
  The `has_stats`/`has_shotmap` index flags are `False` for all
  1,332 rows and the payloads confirm it by content.
- Events exist in 1,190/1,332 matches (89.3%). The 142 matches
  without events split exactly two ways (measured, §5): 141 are
  0-0 draws (played, goalless) and 1 is the awarded 0-3 in 4366461.
  No other event-less match carries goals.
- HT scores are directly readable from the Half event at time 45
  (`homeScore`/`awayScore`): 1,190/1,332 matches (89.3%). The HT
  value was cross-validated against the goal-event feed: it equals
  the count of Goal events with `time <= 45` (credited side via
  `isHome`) in **1,190/1,190** matches. (Against `time < 45` it
  disagrees in 128 — there are 132 goals at minute 45, i.e.
  first-half stoppage time, which the Half event correctly counts
  as first-half goals. The `<= 45` rule is the right one.)
- Lineups are effectively absent: one match in 1,332 (4040543,
  2022/2023) has 11 starters per side; 9 further matches carry
  empty lineup shells. No lineup feature is possible.

## 3. Format

- **Single round-robin league, one season per year.** No
  sub-tournaments, no split seasons, no playoffs. 2021/2022: 18
  teams, 34 rounds, 9 matches/round (306). From 2022/2023: 16
  teams, 30 rounds, 8 matches/round (240/season). The league
  shrank 18 → 16 after 2021/2022: 4 teams left (NA Hussein Dey,
  WA Tlemcen, Olympique de Medea, RC Relizane) and 2 entered
  (MC El Bayadh, USM Khenchela).
- **Turnover is 2-in/2-out every season after the shrink:**
  2023/2024: US Souf + ES Ben Aknoun in, RC Arbaa + HB Chelghoum
  Laid out; 2024/2025: ES Mostaganem + Olympique Akbou in, US Souf
  + ES Ben Aknoun out; 2025/2026: ES Ben Aknoun (returning) + MB
  Rouissat in, US Biskra + NC Magra out; 2026/2027 (in progress):
  US Biskra (returning) + CR Temouchent + JS El Biar in, ES
  Mostaganem + Paradou AC + MC El Bayadh out. Two promoted clubs
  enter every season, so the SHRINK arm is the thin-data treatment
  (MODEL_DESIGN §2); no cross-league mover prior exists.
- Calendar: Aug/Sep → Jun/Jul. Season date ranges: 2021/2022
  2021-10-22→2022-06-17; 2022/2023 2022-08-26→2023-07-15;
  2023/2024 2023-09-15→2024-06-14; 2024/2025 2024-09-19→2025-06-21;
  2025/2026 2025-08-21→2026-06-06; 2026/2027 2026-09-03→2026-11-08
  (in progress, rounds 1–9, some rounds short: r2=6, r6=5, r9=7 —
  postponed matches, not missing files).
- Team identity is by **FotMob team id** (`header.teams[].id`): 27
  distinct ids across the corpus, 18 then 16 per season, no id
  maps to two clubs. Three ids carry two name spellings, all
  diacritic/order variants (101633 CR Bélouizdad / CR Belouizdad;
  45655 ES Sétif / ES Setif; 1531341 Ben Aknoun / ES Ben Aknoun).
  Keying on names would split three clubs in two; keying on ids
  is exact.

## 4. Cards: why K is not buildable

- The 244 Card events are **all dismissals**: Red 184, YellowRed
  60, **0 plain Yellow events in 1,332 payloads**. No stats
  yellows exist either (stats empty). There is therefore **no
  yellow-card target** in any form — neither a stats feed nor an
  event feed — in any season. K-DZ is NOT BUILDABLE
  (payload-level evidence in
  `prereg/PREREG_SCKT_DZ_NOT_BUILDABLE.md`).
- Referee identity is empty in all 1,332 payloads
  (`infoBox.Referee` key present, `text` always `''`), so X8 has
  no input even if a target existed. Dismissals themselves
  (0.18/match) are a rare event with no reliability evidence and
  are not a target.

## 5. Anomalies (frozen handling in PREPROCESSING.md)

| match | season | issue | handling |
|---|---|---|---|
| 4366461 US Souf vs Ben Aknoun | 2023/2024, round 19, 2024-03-02 | **Awarded win**: `awarded == True`, reason "Awarded win", score 0-3, first half started but never ended, EMPTY event feed (0 goal events vs official 0-3). The match was not played to completion | FT score from header/index (official) kept in the CSV; flagged `event_ft_mismatch=1`; **excluded from every fit/score/EDA level** (`eligible=0`, GH/NG precedent for awarded matches) |
| 141 event-less 0-0 draws | all seasons | Played goalless matches whose event feed is empty | FT score from header/index; HT missing (null — NOT inferred, SV precedent); stay eligible |
| 2026/2027 | 2026/2027 | **In progress**: rounds 1–9, 66 matches to 2026-11-08; rounds 2, 6, 9 short (postponed fixtures) | Reserved confirmatory window; not part of this build |

Total excluded from every fit/score/EDA level: **1 row** (the
awarded match). All other 1,331 rows are eligible; the dev/virgin
harness reads the `eligible` column.

## 6. What does not exist here (explicit)

- No xG (of any kind), no SOT, no corners, no total shots, no cards
  target, no referee, no player data, no usable lineups (1 match in
  1,332), no substitutions, no stadium, no attendance — in **any**
  season. S/C/K/T are not buildable (see MODEL_DESIGN §1). No
  proxy is constructed for any of them.
