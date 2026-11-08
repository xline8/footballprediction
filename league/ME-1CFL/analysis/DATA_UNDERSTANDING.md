# Phase 1 — Data Understanding: FotMob Montenegro 1. CFL Warehouse

Corpus: `data_enrichment/fotmob_world/` — FotMob league id 232,
"1. CFL", Montenegro. Inventory tool: `analysis/eda_compute.py`
(raw results in `inventory_summary.json`). Every number below was
measured on the files, not taken from the coordinator scouting.

## 0. Integrity headline

- 972 index rows = 972 files on disk, 0 missing, 0 duplicate match
  ids. One row is NOT a played match — 3818692 (Sutjeska vs Mornar,
  round 36, 2021/2022): `started`/`finished` False, no `scoreStr`
  (the index "0-0" is a placeholder), four phantom goal events in a
  feed for a match that never started. It is EXCLUDED from every
  analysis table. Played matches = **971**.
- The index's own `has_*` flags are pull-time key-presence flags and
  are wrong in the optimistic direction here too: every row says
  `has_stats: False` / `has_shotmap: False`, which is true in
  content terms — but the payload probe the coordinator ran found
  `content.shotmap` is a dict with 2 keys. Measured on all 972
  payloads, that dict is `{"shots": [], "Periods": {"All": []}}` on
  EVERY row: the shots list is empty everywhere. **SOT and total
  shots are not buildable** — the index flag and the payload agree
  once content, not key presence, is measured.
- `general.coverageLevel` is `"lower"` on all 972 rows, faithfully.

## 1. Payload anatomy (one matchDetails JSON)

| Section | Contents | Modelling relevance |
|---|---|---|
| `general` | matchId, leagueId/Name 232 / "1. CFL", `matchRound`, home/away team **ids + names**, `coverageLevel`, kickoff UTC | identity, season/round structure |
| `header.status` | `scoreStr` (official FT score), red-card counts, `awarded` flag, status `reason`, half timestamps | FT target, anomaly flags |
| `header.events` | goals/red cards grouped by player | redundant with matchFacts events |
| `content.matchFacts.events.events` | event list: Goal (scorer, `isHome` = credited side, `ownGoal`, minute), Card (`card` ∈ Yellow/YellowRed/Red — **Yellow never occurs**), Half markers | HT derivation, red-family counts only |
| `content.matchFacts.infoBox` | Tournament, Match Date, Stadium (null), **Referee `{text: ""}`**, Attendance (null) | referee identity absent everywhere |
| `content.stats` | **None on all 972 rows** | no team stats: no SOT, corners, cards, xG, possession, anything |
| `content.shotmap` | `{"shots": [], "Periods": {"All": []}}` on all rows | no shots at all — SOT/total-shots targets do not exist |
| `content.lineup` | **None on all rows** | no lineups/formations |
| `content.events` | **None on all rows** | goal events live in matchFacts, not here |
| `content.table`, `h2h`, `momentum` | standings snapshot, head-to-head, momentum flag | not used (post-match snapshots; leakage risk) |

## 2. Coverage matrix (share of matches with real content, %)

| Season | n (played) | Shotmap (shots>0) | Team stats FT | Team stats per half | Lineups | Referee | Events present | HT derivable |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 179 | 0 | 0 | 0 | 0 | 0 | 92.7 | 92.7 |
| 2022/2023 | 180 | 0 | 0 | 0 | 0 | 0 | 89.4 | 89.4 |
| 2023/2024 | 180 | 0 | 0 | 0 | 0 | 0 | 91.7 | 91.7 |
| 2024/2025 | 179 | 0 | 0 | 0 | 0 | 0 | 94.4 | 93.9 |
| 2025/2026 | 180 | 0 | 0 | 0 | 0 | 0 | 90.6 | 90.6 |
| 2026/2027 (partial) | 73 | 0 | 0 | 0 | 0 | 0 | 83.6 | 83.6 |
| **All played** | **971** | **0** | **0** | **0** | **0** | **0** | **91.1** | **91.0** |

Reading of the matrix:

- **This is a scores-only corpus.** The only modelling target that
  exists is FT goals (and the HT split derived from goal events).
  SOT, corners, cards (yellows), total shots, xG, referee, lineups:
  all absent, in every season, with no calendar window where any
  of them appears. There is no "stats era" to wait for.
- Event-feed coverage is 91.1%: 86 played matches have an empty
  event list (13–19 per complete season). Those matches have no
  derivable HT score and no card counts — missing, not zero.
- Card events total 125 across the corpus: Red 74, YellowRed 51,
  **Yellow 0**. The event feed omits yellow cards entirely (same
  provider pattern as J3), so **no yellow-card target exists** even
  via events. Red-family counts (0.13/match) are a rare-event count
  and are not a modelling target either.

## 3. Format

- 10 teams, 36 rounds, every complete season: each pair meets 4
  times (single round-robin phase repeated 4x). No split group, no
  championship/relegation round, no playoff phase in any season.
- Season date ranges: 2021/2022 Jul 24 2021–May 24 2022;
  2022/2023 Jul 23 2022–May 25 2023; 2023/2024 Jul 22 2023–May 25
  2024; 2024/2025 Aug 4 2024–May 24 2025; 2025/2026 Aug 4 2025–May
  24 2026; 2026/2027 Aug 1–Nov 8 2026 (in progress, rounds 1–15).
- 2024/2025 has 179 rows, not 180: round 36 carries 4 matches.
  The missing fixture is Buducnost Podgorica vs Decic Tuzi — it is
  absent from the warehouse index entirely (no row, no file). The
  reason is not recoverable from the warehouse; it is treated as a
  missing fixture, never as a 0-0. Buducnost and Decic each have 35
  appearances that season.
- 2021/2022 round 36 likewise carries 4 played matches (35 rounds
  x 5 + 1 round x 4 = 179): the fifth fixture is the never-started
  ghost 3818692 (§0).
- 2026/2027 round 10 carries 3 matches (73 rows over rounds 1–15):
  two fixtures presumably postponed; the season is in progress and
  is reserved as confirmatory, so this does not affect any gate.
- Team turnover is 1–2 ids per season (EDA F4). 15 distinct team
  ids appear across the corpus; two ids carry two name spellings,
  both diacritic variants appearing in 2026/2027 (Decic Tuzi /
  Dečić Tuzi, id 8100; Buducnost Podgorica / Budućnost Podgorica,
  id 8627). Team identity is keyed on FotMob team id everywhere.

## 4. Quirk register (each verified on the files)

1. **Ghost fixture 3818692** (Sutjeska vs Mornar, 2022-05-24,
   round 36, 2021/2022): never started, no `scoreStr`, empty
   `halfs`, yet the event feed lists 4 goals (1 home, 3 away).
   The other three Sutjeska–Mornar meetings that season were all
   played (rounds 9, 18, 27). Excluded from the analysis tables;
   the index "0-0" must never be used as a score.
2. **Phantom goal event in 4711154** (Buducnost Podgorica 5–2
   Jedinstvo BP, 2025-03-29, 2024/2025): the event feed lists 3
   away goals — Grivic own goal (8'), Komiya (15'), and a third at
   minute 8 by player "<TBD>" (id 0). The "<TBD>" entry is junk;
   the official score 5–2 is correct. The match's HT split is
   therefore unreliable (events would say 3–3, truth is 3–2) and
   is stored as NaN with `ht_source='mismatch_phantom'`. The FT
   score is unaffected. This is the ONLY score/event mismatch
   among the 971 played matches.
3. **No awarded matches.** `awarded` is False on every row
   (the ghost fixture has no `awarded` field set at all).
4. **Empty event lists are scattered, not windowed**: 86 played
   matches across all seasons have zero events (including
   goalless draws, where an empty list is expected — a 0-0 with
   no events is indistinguishable from a missing feed, so HT is
   NaN for all of them regardless of score).
5. **Shotmap dict with empty shots list** (§0): the 2-key dict is
   a schema placeholder, not data. Any check that counts keys
   instead of list length will wrongly conclude SOT exists.

## 5. Definition alignment

| Concept | FotMob ME-1CFL source | Alignment result |
|---|---|---|
| FT score | `header.status.scoreStr` (official) | Source of truth. Goal-event counts reproduce it in 970/971 played matches (1 flagged phantom, §4.2). |
| HT score | **No explicit field exists.** Derived from goal events (`time ≤ 45`, credited side) | Available for 884/971 played matches (91.0%). Unavailable for the 86 event-less matches and the 1 phantom-HT match. |
| Shots on target | — | Does not exist (empty shotmap, no stats). |
| Total shots | — | Does not exist. |
| Team xG | — | Does not exist. |
| Corners | — | Do not exist. |
| Yellow cards | — | Do not exist (no stats; event feed carries zero Yellow events). |
| Red cards | event feed `card='Red'` + `YellowRed` | 125 events in 971 matches (0.13/match) — a rare-event count, not a target. |
| Referee | infoBox `Referee.text` | Empty string on all 972 rows. |

## 6. What this corpus has

- 971 played matches of clean FT scores across 6 seasons, 15
  clubs, one stable format — enough for exactly one candidate:
  a scores-only goals model.
- An event-derived HT split for 91% of matches, enough to freeze
  a 1H goals share for presentation (EDA F3) but nothing more:
  no per-half stats feed exists to cross-validate it against.
