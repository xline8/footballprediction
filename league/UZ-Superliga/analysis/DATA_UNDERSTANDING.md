# Phase 1 — Data Understanding: Uzbekistan Superliga (FotMob 540)

## Inventory

- Source: FotMob world warehouse, `data_enrichment/fotmob_world_index.csv`,
  filter `league_id = 540`: **215 rows**, all country Uzbekistan, league
  "Superliga". 540 is the only Uzbekistan league id in the warehouse.
- Seasons: **exactly one — 2026** (calendar-year label), 215 rows,
  2026-02-27..2026-11-08, **IN PROGRESS**. Zero complete seasons.
- Teams: 16 (AGMK, Andijon, Bunyodkor Tashkent, Buxoro, Dinamo Samarkand,
  Kokand 1912, Lokomotiv Tashkent, Mashal Muborak, Nasaf Qarshi, Navbahor
  Namangan, Neftchi Fargona, Pakhtakor Tashkent, Qizilqum Zarafshon,
  Sogdiana, Surkhon-2011, Xorazm).
- Format (from payloads): 16 teams, double round-robin, 30 rounds x 8
  matches = 240 matches. Rounds 1–27 played (215 matches); round 26 has
  7 (Bunyodkor Tashkent vs Neftchi Fargona missing/postponed); rounds
  28–30 not yet played (~25 matches outstanding). Single regular phase:
  no split group, championship/relegation round, or playoff phase in any
  2026 payload (`general.leagueRoundName` is the round number throughout).

## Field coverage (215/215 payloads read directly)

| Field | Coverage | Note |
|---|---|---|
| FT score | 215/215 | Index score agrees with `header.teams` scores 215/215 |
| `general.finished` | 215/215 True | No unfinished, cancelled, or awarded matches |
| `content.stats` | null 215/215 | No stats block at all |
| `content.shotmap.shots` | empty 215/215 | Key present as empty skeleton `{shots: [], Periods: {All: []}}` |
| `content.lineup` | null 215/215 | No lineups |
| Referee (`matchFacts.infoBox.Referee`) | blank 215/215 | Empty text, no country |
| Structured period splits | 0/215 | `content.stats` is null, so no `Periods` beyond the shotmap skeleton |
| `matchFacts.events` | non-empty 99/215 | Rounds 10 and 14–27 only (live-coverage era) |
| HT score (derived) | 99/215 | From the Half event at minute 45; see below |

## The event-feed finding (the one place the index flags understate the data)

`matchFacts.events` is non-empty in 99/215 payloads. Those 99 carry:

- A `Half` event at minute 45 with `homeScore`/`awayScore` = the HT
  score: 99/99 consistent (0 ≤ HT ≤ FT on both sides).
- `Goal` events whose count equals the FT goal total: 99/99.
- 29 `Card` events (incl. reds) — sparse against ~300 expected at normal
  card rates, so cards are not a usable target.
- Event-type counts across the 99: Half 198 (HT + FT markers), Goal 279,
  Card 29.

HT goals total 128 vs 279 FT goals in the same 99 matches (share
0.4588). This is a descriptive measurement only: coverage is
late-season only (1 match in round 10, the rest rounds 14–27) and no
constant is frozen from it. The 116 matches without events have no HT
information at all.

## What the index flags get right and wrong

- `has_stats: False`, `has_shotmap: False`, `has_period_splits: False`,
  `has_lineup: False` on all 215 rows. Right about substance (stats null,
  shotmap empty, no structured splits, no lineups) but the flags are
  key-presence heuristics: the shotmap key IS present (empty skeleton),
  and the flags say nothing about the `matchFacts.events` feed that
  carries HT scores in 99 matches. Verify from payloads, never from flags.

## Calendar and quirks

- Season runs Feb–Nov/Dec (calendar-year league). A mid-season gap
  between rounds 11 (2026-05-02..04) and 12 (2026-07-16..18) — summer
  break, not missing data.
- Round 26 is short by one fixture (Bunyodkor–Neftchi, presumably
  postponed); it is not in the warehouse as either played or scheduled.
- No 0-0 anomaly: all 18 goalless matches are finished matches with
  genuine 0-0 scores (cross-checked against header scores).
- `coverageLevel` is `lower` in 215/215 payloads (FotMob basic coverage).

## Bottom line

A scores-only league with a single partial season. The only target that
exists is goals (FT everywhere, HT in 99/215). Everything else the
program models — SOT, corners, cards, total shots, xG, referee effects —
is absent from every payload.
