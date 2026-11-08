# Step 1 — Data understanding: Russia Second League (FotMob 9123)

Slug: `RU-SecondLeague`. Tier 3 of the Russian system, below Premier League
(FotMob 63) and 1. Division (FotMob 338). All counts below are
payload-verified (every one of the 6,558 index rows read; the index's
`has_stats` / `has_shotmap` flags were NOT trusted — see §4).

## 1. What FotMob 9123 is

9123 is a **parent league id**. Each payload's `general.leagueName` is one
of **44 sub-tournaments** — groups, subgroups, stages and playoffs — not a
single table. Two parallel tracks run from 2023:

- **Division A** (autumn–spring): Gold Group + Silver Group, each split
  into a First Stage and a Second Stage; the second stage re-sorts teams
  (top Silver teams move up to Gold, bottom Gold teams drop to Silver),
  so A is a single connected component per season. Ends with a Gold
  Promotion Playoff (2 matches) and a Silver Relegation Playoff (2).
- **Division B** (calendar year): 4 regional groups, each a double
  round-robin; Group 1 adds Promotion/Relegation Groups and Group 4 the
  same in 2025–2026; a 4-match Final Four between group winners (2026)
  is the only cross-group meeting. Otherwise B is **4 disconnected
  components** per season.
- **Before 2023** the same shape ran as FNL 2 / Second League: 4 groups,
  several split into Subgroup 1/2, each with Promotion and Relegation
  Groups (second phase inside the same group).

Sub-tournament counts (largest): Division B Group 3 (813), Group 2
(810), Group 1 (664), Group 4 (568); Division A Gold First Stage (354),
Silver First Stage (278), Gold Second Stage (270), Silver Second Stage
(269). Full list is in `eda_numbers.json` / the audit trail; every
sub-tournament is preserved verbatim in the CSV column `sub_tournament`.

## 2. Seasons and completeness

| season label | index | finished | note |
|---|---:|---:|---|
| 2021/2022 | 1,136 | 1,136 | complete (FNL 2, 4 groups) |
| 2022/2023 | 1,130 | 1,130 | complete (4 groups) |
| 2023 (B) | 512 | 512 | complete (Division B only) |
| 2023/2024 (A) | 362 | 362 | complete (Division A only) |
| 2024 (B) | 904 | 904 | complete (Division B only) |
| 2024/2025 (A) | 364 | 235 | **partial**: first stages ~complete (86/90 Silver, 89/90 Gold); second stages mostly phantom (18/90 Silver, 38/90 Gold) |
| 2025 (B) | 842 | 42 | **harvest fragment**: 5% coverage, distorted scorelines (see §3) |
| 2025/2026 (A) | 327 | 156 | **partial**: ~half of every stage present |
| 2026 (B) | 853 | 772 | near-complete: 16–24 phantom rows per group |
| 2026/2027 (A) | 128 | 128 | in progress (season runs to Jun 2027) |

Total: **6,558 index rows, 5,377 finished, 1,181 phantom fixtures**
(`started=False`, no `scoreStr`, index score the placeholder "0-0").
Phantoms are fixture stubs whose results were never harvested; they are
kept in the CSV with `finished=0` and null goals and excluded from every
fit and score. Finished matches all carry a real `scoreStr` that matches
the index score in every case (0 mismatches among finished rows).

**Connected components** (team graph, finished matches only):
2021/2022: 4 ([22, 21, 17, 15] teams); 2022/2023: 4; 2023: 4; 2023/2024:
1 ([25], via stage re-sorting); 2024: 4; 2024/2025: 1 ([24]);
2025/2026: 1 ([22]); 2026: 1 ([58], bridged by the Final Four); 2026/2027:
2 ([10 Gold, 7 Silver] — season in progress). Consequence for the goals
model: within a season, teams are rated only against their own
group/stage opponents; cross-group levels are identified only through
the fit's zero-init anchor. Only 4 virgin matches (the 2026 Final Four)
are cross-group predictions; this is recorded in MODEL_DESIGN.md, not
hidden.

## 3. The 2025 harvest fragment

Season label 2025 (Division B) has 42 finished rows out of 842. The 42
are a non-random fragment: mean goals 1.38 (league norm ~2.65–2.87),
0-0 share 42.9%, draw share 57.1%. Excluding the 13 awarded matches
among them leaves 29 rows at mean 2.00 goals and 17.2% 0-0 — still
distorted. The fragment's dates scatter Mar–Oct 2025 with no round
structure. **Frozen rule: season label 2025 is excluded from every fit
and score** (training history included). Cost, stated plainly: virgin
Division B ratings rest on 2024 B (one cycle stale). The 42 rows stay in
the CSV for inventory completeness.

## 4. Field coverage — payload-level (not index flags)

Read from all 6,558 payloads:

- **Scores**: finished rows only (5,377). `scoreStr` == index score.
- **Stats** (`content.stats.Periods`): **empty in 6,558/6,558**. No
  `expected_goals`, no `corners`, no `ShotsOnTarget`, no `yellow_cards`,
  no `touches_opp_box`, nothing — in any season. (The index flag
  `has_stats` is False throughout here, but the finding is from the
  payloads, as required.)
- **Shotmap**: **empty in 6,558/6,558**. No xG, no shots, no xGOT.
- **Events** (`matchFacts.events`): present in **3,773** matches and
  **only** in seasons 2021/2022–2024 (1,078 / 1,054 / 480 / 320 / 841
  per season). **Zero events in all 2,402 rows from 2024/2025 onward.**
  Event types are only Goal (10,894), Half (7,546) and Card (959).
- **Cards in events**: all 959 Card events are dismissals — YellowRed
  (624) or Red (335). **Zero plain Yellow-card events exist anywhere.**
  Events-era matches with ≥1 card event: 835/3,773; mean 0.254
  cards/match; 77.9% of events-era matches show zero cards. The feed
  essentially omits cards.
- **Goal events vs score**: reconcile in all but 15 matches — and all 15
  are awarded matches (§5).
- **Referee**: `infoBox.Referee.text` is **empty in 6,558/6,558**.
- **Lineup**: 25 payloads carry a lineup shell (`homeTeam`/`awayTeam`
  with only `id`, `name`, `unavailable: []`). No player data anywhere.
- **Half splits**: no `Periods.FirstHalf/SecondHalf` stats anywhere.
  The ONLY half information is Goal-event times (events era), giving
  HT goals for 3,758 matches (see EDA.md §4).

## 5. Awarded matches (administrative results)

**50 finished matches are `awarded=True`**: 10 in 2021/2022, 15 in
2022/2023, 13 in 2025, 12 in 2026. Of these, 13 are classic forfeits
(3-0 / 0-3) and **37 are recorded 0-0 while their Goal events show
goals were scored** (e.g. 2022-10-21 Kuban-Holding vs Yessentuki, 5
Goal events, recorded 0-0). They concentrate on three clubs:
Yessentuki (13), Sokol Kazan (13), Irkutsk (12) — clubs expelled or
withdrawn mid-season, their results annulled/awarded. Following the
AE-ProLeague precedent, awarded matches **stay in the CSV with
`awarded=1` and are excluded from every fit, score and EDA level**.
The 15 goal-event/score mismatches in the whole corpus are exactly
these awarded matches; no other payload contradicts its score.

## 6. Team identity

FotMob team ids are stable across leagues and seasons (verified:
Alania Vladikavkaz id 268557 in both 338 and 9123). Five ids carry
renames across seasons (e.g. 8714 Saturn Ramenskoye / Leon Saturn
Ramenskoye; 198166 Znamya Truda / Znamya; 1070334 FC Novosibirsk /
FC Sibir). All joins are by **team id**, never by name. No team name
maps to more than one id.

## 7. Calendar and format changes

- 2021/2022–2022/2023: autumn–spring, 4 groups, subgroups + promotion/
  relegation groups (second phase inside each group).
- From Jul 2023: the split into Division A (autumn–spring) and
  Division B (calendar year) — two different team sets sharing one
  FotMob id (only 4 teams overlap between the 2023 B and 2023/2024 A
  labels; same pattern each year). The model is pooled over both
  tracks (see MODEL_DESIGN.md for the justification and the leakage
  guard); the CSV keeps `track` (A / B / pre-2023) and `phase` per row.
- Promotion/relegation between tiers: Division A Gold winner is
  promoted to 1. Division (338); Division B group winners enter
  Division A; bottom A teams drop to B. Mover evidence is in EDA.md §5.

## 8. What this means for candidates

Only **goals** has a target in the data. SOT, corners, total shots have
no target anywhere (no stats, no shotmap). Cards have no valid target
(no stats yellows; events carry dismissals only, and events die after
2024). See MODEL_DESIGN.md for the feasibility matrix.
