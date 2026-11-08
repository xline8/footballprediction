# Phase 1 — Data Understanding: Costa Rica Primera Division

Corpus: FotMob world warehouse, league id **121**, `Primera Division`, Costa Rica, top tier.
Index: `data_enrichment/fotmob_world_index.csv` (filter `league_id = 121`) → **1,350 matches**.
Per-match JSONs: `data_enrichment/fotmob_world/Costa Rica/Primera Division/<season-dashed>/<match_id>.json`
(same matchDetails format as the J.League warehouse). All 1,350 matches are finished/played.

## Seasons

| Season | Matches | Dates | Note |
|---|---|---|---|
| 2021/2022 | 280 | 2021-07-27 → 2022-07-07 | Complete (Apertura + Clausura + playoffs) |
| 2022/2023 | 244 | 2022-07-19 → 2023-05-29 | Apertura regular rounds 17–22 missing (96/132) |
| 2023/2024 | 276 | 2023-07-26 → 2024-05-26 | Complete except no Championship Finals (same winner both tournaments) |
| 2024/2025 | 278 | 2024-07-20 → 2025-05-29 | Near-complete; Clausura round 22 has 4/6 matches |
| 2025/2026 | 192 | 2025-07-25 → 2026-05-17 | Partial pull + format change (10 teams, 18 rounds); no Final Stage rows |
| 2026/2027 | 80 | 2026-07-24 → 2026-11-09 | In progress (Apertura only so far) |

## Calendar / format

Each football year = **Apertura** (Jul–Dec) + **Clausura** (Jan–May). Each tournament is a double
round-robin: 12 teams × 22 rounds (6 matches/round) in 2021/22–2024/25, then **10 teams × 18 rounds
(5 matches/round) from 2025/26**. After each tournament: a **Final Stage** (2 semifinals × 2 legs = 4
+ final × 2 legs = 2; 6 matches) and, when the two tournament winners differ, a **Championship Final**
(2 legs). Playoff total: 60 matches across the six seasons. The model scope is the **regular season**
(1,290 matches); playoffs are a different format (two-legged ties) and are excluded from fitting.

Tournament naming quirk: 22 matches in 2025/26 sit under the variant league name
`Costa Rica Primera Division Apertura` (rounds 1–5) — same tournament as `Primera Division Apertura`.

## Field coverage per season (verified from payloads, NOT from the index flags)

| Field | 21/22 | 22/23 | 23/24 | 24/25 | 25/26 | 26/27 |
|---|---|---|---|---|---|---|
| FT score (`header.teams[].score`) | 280/280 | 244/244 | 276/276 | 278/278 | 192/192 | 80/80 |
| HT score (Half event) | 264/280 | 239/244 | 276/276 | 274/278 | 192/192 | 79/80 |
| Goal events (count == FT total) | 279/280 | 244/244 | 276/276 | 274/278 | 192/192 | 78/80 |
| Stats block (`content.stats`) | 0 | 0 | 0 | 0 | 0 | 0 |
| Shotmap shots | 0 | 0 | 0 | 0 | 0 | 0 |
| Card events usable | NO | Apertura NO / Clausura patchy | YES | YES | YES | YES |
| Referee text non-empty | 0 | 0 | 0 | 0 | 22 | 0 |

- **Scores-only league.** `content.stats` is null in every match and `shotmap.shots` is empty:
  no corners, no shots on target, no total shots, no xG. SOT / corners / total shots are NOT candidates.
- Goals and cards come from `content.matchFacts.events.events` (Goal / Card / Half / Substitution /
  MissedPenalty). Goal-event count matches the FT score in 1,343/1,350 matches.
- HT score comes from the `Half` event (time 45, carries `homeScore`/`awayScore`): present in 1,324/1,350
  (98.1%).

## Gaps and quirks

1. **Card-feed gap, 2021/22.** Zero `Yellow` events in the whole season (only Red/YellowRed recorded);
   mean 0.24 yellows/match, 221/280 zero-card matches. Yellows are missing from the feed, not from the games.
2. **Card-feed gap, Apertura 2022/23.** Jul–Oct 2022 monthly means 0.11–0.35 yellows/match.
   The feed turns on in Jan 2023 (Clausura): monthly means 3.93–5.00.
3. **Card-feed patchiness, Clausura 2022/23.** 14/132 regular matches are zero-card (10.6%) against an
   NB-implied ~2% at mean 4.70 — including 8 zero-card matches in Feb 2023 (rounds 5–10, spread across
   teams). The era is not clean enough for fitting; it is excluded from cards entirely.
4. **Playoff card events missing, 2021–2024.** 29/60 playoff matches are zero-card, including all 6
   Apertura Final Stage matches of Dec 2023. (2024/25 playoffs have cards.) Playoffs are excluded from
   fitting in any case.
5. **No-events matches: 25.** Their events list is empty; 21 are 0–0 draws (score consistent), 5 carry a
   3–0/0–3 score with no events (the goal-mismatch set). FT score is still authoritative.
6. **Goal-event mismatches: 7** (`3788567`, `4511508`, `4684899`, `4684935`, `4684941`, `5833754`,
   `5961115`): 5 have an empty events list, 2 are missing exactly one goal event. FT goals always come
   from the header score, never from event counts.
7. **No-Half-event matches: 26** (the 25 no-events matches + `3788567`). HT goals are null for these;
   they are excluded from halves estimation only.
8. **Round gaps.** 2022/23 Apertura regular rounds 17–22 absent from the warehouse (96/132 present);
   2024/25 Clausura round 22 has 4/6. Both are warehouse gaps, not forfeits — no matches exist for them.
9. **Team-name variants.** e.g. `C.S. Cartagines` vs `C.S. Cartaginés`, `LD Alajuelense` vs `Alajuelense`.
   Teams are keyed by FotMob team id (17 distinct ids); canonical names in `team_aliases.json`.
10. **Referee absent.** `infoBox.Referee.text` is empty in every season except 22 matches in 2025/26.
    There is no referee feature for this league.
11. **Team churn.** One promotion/relegation per year 2022–2025; the 2025/26 shrink drops Santos de
    Guapiles, AD Guanacasteca and Santa Ana FC and brings Guadalupe FC back (12 → 10 teams); 2026/27
    adds two brand-new ids (Inter San Carlos, Escorpiones). Full churn table in `inventory_summary.json`.
