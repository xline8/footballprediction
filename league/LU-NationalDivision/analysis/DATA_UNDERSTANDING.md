# Step 1 — Data Understanding: LU-NationalDivision (Luxembourg National Division)

FotMob id **229**. Country Luxembourg. Slug `LU-NationalDivision`.
Source: the FotMob world warehouse (`data_enrichment/fotmob_world_index.csv`,
1,296 index rows; all 1,296 payload JSONs present on disk).

## Identity check (payloads, not the index label)

- `general.leagueName` is `"National Division"` in **all 1,296** payloads;
  `parentLeagueId` is 229 in all 1,296. FotMob 229 is a single true
  league, NOT a parent container of sub-competitions (contrast FotMob
  8938 / AU-Championship). No split is needed.
- No sibling Luxembourg league exists in the warehouse: the index
  carries exactly one Luxembourg league (id 229). There is therefore
  no in-warehouse second tier from which a mover prior could be
  estimated — X2 is dropped on data absence (see FEATURES.md).
- Season labels as in the warehouse: `2021/2022` … `2026/2027`.

## Inventory

| Season | Matches | Dates | Teams | Status |
|---|---|---|---|---|
| 2021/2022 | 240 | 2021-08-07 – 2022-05-22 | 16 | complete |
| 2022/2023 | 240 | 2022-08-06 – 2023-05-21 | 16 | complete |
| 2023/2024 | 240 | 2023-08-05 – 2024-05-26 | 16 | complete |
| 2024/2025 | 240 | 2024-08-03 – 2025-05-25 | 16 | complete |
| 2025/2026 | 240 | 2025-08-02 – 2026-05-24 | 16 | complete |
| 2026/2027 | 96 | 2026-08-08 – 2026-10-31 | 16 | in progress (partial) |
| **Total** | **1,296** | | | |

Format: 16 teams, 30 rounds × 8 matches, single table, double
round-robin. No playoffs (`content.hasPlayoff` is False where the key
exists, 2025/26 onward; absent before that — no playoff rounds exist
in any season's round list, which runs 1–30 in every season). No
championship/relegation split. Team turnover between seasons: 2 new
teams in 2022/23, 2 in 2023/24, 3 in 2024/25, 4 in 2025/26, 4 in
2026/27 (promoted from the Division of Honour / relegated out; that
tier is not in the warehouse).

## Field coverage per season (verified in payloads, all seasons identical)

| Field | Coverage | Note |
|---|---|---|
| Score (`header.teams[].score`, `status.scoreStr`) | 1,296/1,296 (100%) | `finished` True everywhere; no unplayed fixtures |
| `content.stats` | **absent (null) in 1,296/1,296** | No SOT, corners, total shots, xG, fouls, possession — in ANY season. The stats era never starts. |
| `content.shotmap.shots` | empty list in 1,296/1,296 | Key present, zero shots everywhere |
| `content.lineup`, `content.playerStats` | absent in 1,296/1,296 | No lineups, no player data |
| Events (`matchFacts.events.events`) | 1,251/1,296 non-empty | Types: Goal 4,062; Half 2,502; Card 385 |
| Goal-event times | 4,062 events, minutes 1–90 | Gives the 1H/2H goal split |
| Card events | 385: Red 232, YellowRed 153 | **No plain Yellow event exists anywhere** |
| Referee (`infoBox.Referee.text`) | key present, text `""` in 1,296/1,296 | Referee identity absent in content |
| Stadium / Attendance | null in 1,296/1,296 | — |
| `coverageLevel` | `lower` in 1,296/1,296 | — |

The world-index flags agree here (`has_stats`/`has_shotmap`/
`has_period_splits`/`has_lineup` all False, 1,296/1,296) — but that
agreement was NOT trusted: every figure above was re-derived from
the payloads, because the flags are key-presence flags, not content
checks (they would have missed the empty-shotmap and empty-referee
cases, which are key-present-but-empty).

## Gaps and quirks

1. **Scores-only league.** The only modelling target that exists is
   goals (FT score + goal-event times). SOT / corners / cards /
   total shots are NOT BUILDABLE in any season.
2. **One match with goals but no goal events:** 4520839 (2024/25,
   Swift Hesperange 0–3 US Mondorf les Bains) has an empty events
   list. Score-vs-event goal totals agree everywhere else (4,062
   events vs 4,065 scored goals; the 3-goal gap is this match alone).
   Its halves columns are missing, not zero (see PREPROCESSING.md).
   The other 44 empty-events matches are all 0–0, so their halves
   are 0/0 by construction.
3. **Cards are reds only.** 385 red-card events (0.30/match) exist,
   but the cards market is a total-cards (yellow + red) line; with
   zero yellow data the target does not exist. Red-card counts are
   carried in the CSV as descriptive columns only.
4. **Referee names are empty strings** despite the key existing —
   the index-style "referee present" reading would be wrong.
5. **Goals level drifts down** across complete seasons: 3.21 → 3.34
   → 3.13 → 2.99 → 2.85 goals/match (2021/22 → 2025/26). The partial
   2026/27 (96 matches) sits at 3.55 — small-sample early-season
   noise, untouched as the confirmatory reserve.
6. No awarded/cancelled matches are flagged in the payloads
   (`status.awarded` False everywhere the key was inspected; the
   4520839 events gap is a feed gap, not an award flag — recorded
   as such, not assumed).

## Calendar

Autumn–spring season (August–May), 30 rounds. The 2026/27 season is
in progress at the warehouse cut (last match 2026-10-31, 96/240
played, rounds 1–12). It is the untouched confirmatory reserve:
built into the CSV, read by no analysis, fit, or gate in this league.
