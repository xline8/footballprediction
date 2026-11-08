# Step 1 — Data Understanding: NI-Premiership

Source: FotMob world warehouse, index `data_enrichment/fotmob_world_index.csv`
(filter `league_id == 129`), payloads under
`data_enrichment/fotmob_world/Northern Ireland/Premiership/<season>/`.
Inventory: `league/NI-Premiership/analysis/inventory_summary.json`.
Builder: `league/NI-Premiership/data/build_data.py` → `ni_matches.csv`
(1,242 rows, one per played match).

## Identity — one true league, verified from payloads

- `general.parentLeagueId == 129` in ALL 1,242 payloads.
  `general.leagueName` is phase-labelled, not a sub-competition
  marker: "Premiership" 1,077, "Premiership Championship Group" 75,
  "Premiership Relegation Group" 75, "Premiership ECL Playoff" 15 —
  the group/playoff names are the split and playoff phases of the
  same competition under parent 129.
  No hidden sub-competitions: unlike FotMob 8938 (AU-Championship, a
  parent container of 10 competitions), 129 is a single competition.
- The season-specific `general.leagueId` splits each season into: one
  main id (198 matches = 33 rounds x 6), TWO split-group ids (15 each
  = top-6 / bottom-6, 5 rounds x 3), ONE playoff id (3 matches).
- **2021/2022 round-label trap:** split rounds 34–38 reuse round
  labels "1"–"5" under the split leagueIds (878453 top-6, 878454
  bottom-6). Counting by round label alone double-counts rounds 1–5
  (12 matches each). Phase must be identified by season leagueId (or
  by date: split matches are April 2022), never by round label alone.
  From 2022/2023 the split rounds are labelled 34–38.
- No other Northern Ireland league exists in the warehouse (index:
  only league_id 129 for country Northern Ireland). There is no
  sibling league, so no X2 mover-prior arm is possible (FEATURES.md).

## Seasons and format

| Season | Index rows | Regular | Playoffs | Status |
|---|---|---|---|---|
| 2021/2022 | 231 | 228 | 3 | complete |
| 2022/2023 | 231 | 228 | 3 | complete |
| 2023/2024 | 231 | 228 | 3 | complete |
| 2024/2025 | 231 | 228 | 3 | complete |
| 2025/2026 | 231 | 228 | 3 | complete (virgin) |
| 2026/2027 | 87 | 87 | 0 | in progress, rounds 1–15 (reserve) |

Format (all six seasons): 12 teams; 33 rounds single table (198
matches); then a split into top-6 / bottom-6 playing 5 further rounds
(30 matches) = 38 rounds, 228 regular-season matches. Then a
European-playoff mini-tournament: two one-legged semi-finals + final
(3 matches) among the teams finishing 3rd–7th (2025/26: a 1/4 round
appears instead of one semi-final — 1 + 1 + 1 = 3 matches; the count
is 3 every season). Playoff matches CAN go to extra time — e.g.
3873126 Glentoran–Larne 2022-05-13 (FT 2-2, AET 2-4, goals at 100'
and 120'). Playoffs are EXCLUDED from all model data (different
competition; ET goals in the score). Calendar: August–April/May;
2025/26 ran 2025-08-09–2026-04-25 (regular) + playoffs to 2026-05-12.

## Field coverage per season (from payloads, not index flags)

The index `has_stats` / `has_shotmap` / `has_lineup` /
`has_period_splits` flags are key-presence flags and are False
everywhere here; all coverage below was verified by reading the
1,242 payloads.

| Field | Coverage |
|---|---|
| FT score (`header.teams[].score`) | 1,242/1,242; every payload `finished=True` |
| `content.stats` | null in ALL 1,242 — no stats feed in any season |
| `content.shotmap.shots` | empty list in ALL 1,242 — no shots/xG data |
| xG (`expected_goals*`) | absent everywhere (consequence of stats null) |
| Referee | never present — no referee key/text in any payload |
| Lineup / playerStats | absent (lineup key absent; playerStats empty) |
| Events (`matchFacts.events.events`) | present in 1,169/1,242 matches with goals; 73 matches have an empty events list, all of them 0-0 |
| Goal events | 3,515 total; count == header goal total in 1,241/1,242 matches |
| Half events (`HT`/`FT`/`AET`) | 2,357 total; HT event present in 1,178/1,242 matches; the 64 missing are all 0-0 |
| Card events | 261 total in 225 matches (0.21/match) — ONLY Red (210) and YellowRed (51); NO plain Yellow event exists anywhere |

## Quirks (all recorded, none silently patched)

1. **3907917** (2022/2023, Newry City AFC–Portadown, 2022-12-04):
   index/header say 3-0, but the event trail is internally consistent
   at 1-3 (4 goal events with `newScore` ending [1,3]; FT Half event
   1-3). The header score (3-0) is used for the model (it agrees with
   the index); the match's halves columns are left EMPTY (missing,
   not zero) in the CSV. It contributes 3 goals to the FT tally and 0
   goals to the 1H/2H split.
2. **3873126** (2021/2022 playoff, Glentoran–Larne): went to extra
   time; the 90' Half event says 2-2, the 120' (`AET`) Half event says
   2-4. The header score (2-4) is the AET result. This is a playoff
   and is excluded from model data anyway; it is the proof that
   playoff scores are not 90-minute scores.
3. **2021/2022 round labels** (see above): split rounds reuse labels
   "1"–"5". Handled by leagueId, not label.
4. **Card feed is fragmentary, not just thin:** cards appear in only
   225/1,242 matches (18%), with no yellows at all. A real
   Premiership match averages ~3–4 cards; 0.21/match means the feed
   records a small, non-random subset (mostly reds). No cards
   candidate can be built from this.
5. **No period-split stats:** the only 1H/2H information is the
   goal-event times (and the HT Half-event score, which agrees with
   them in all 1,162 matches where both exist — 0 disagreements).
   There are no 1H SOT/corner/card splits because those targets do
   not exist at all.

## What this league is

A **scores-only league**: FT scores + goal-event times, nothing else.
Only the goals candidate (G-NI) is buildable. SOT, corners, total
shots are not buildable (no stats/shotmap in any season); cards is
not buildable (no yellows; reds fragmentary; no referee). The goals
model is goals-only Dixon-Coles (no xG blend anywhere).
