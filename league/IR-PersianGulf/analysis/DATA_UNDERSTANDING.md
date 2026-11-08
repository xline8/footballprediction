# Phase 1 — Data Understanding: IR Persian Gulf Pro League (Iran, FotMob 523)

Source: the FotMob world warehouse. Index:
`data_enrichment/fotmob_world_index.csv` filtered to `league_id = 523`
(1,245 rows, league name `Persian Gulf`, country Iran). Per-match
JSONs at the index `path` column
(`data_enrichment/fotmob_world/Iran/Persian Gulf/<season>/<id>.json`,
same matchDetails format as the J.League warehouse). All coverage
figures below were measured from the **payload contents** of all 1,245
files, never from the index `has_*` flags (which read all-False here
and are in any case unreliable program-wide).

## Inventory

| season | index rows | played (league) | teams | rounds | date range |
|---|---:|---:|---:|---:|---|
| 2021/2022 | 240 | 240 | 16 | 1–30 | 2021-10-19 – 2022-06-02 |
| 2022/2023 | 240 | 240 | 16 | 1–30 | 2022-08-12 – 2023-05-18 |
| 2023/2024 | 240 | 240 | 16 | 1–30 | 2023-08-09 – 2024-06-01 |
| 2024/2025 | 240 | 240 | 16 | 1–30 | 2024-08-15 – 2025-05-15 |
| 2025/2026 | 180 | 178 | 16 | 1–23 (21, 23 partial) | 2025-08-18 – 2026-02-27 |
| 2026/2027 | 105 | 105 | 18 | 1–12 (11 partial, 6/9) | 2026-08-14 – 2026-11-08 |
| **total** | **1,245** | **1,243** | **23 ids** | | |

Played league n = 1,243: the two remaining index rows are **not
league matches** and are excluded from every analysis — 1000015890
(2026-06-26, Chadormalu vs Persepolis 2-1, "Asian Qualifiers
Play-offs - Semi-Final") and 1000015891 (2026-06-29, Gol Gohar vs
Chadormalu 0-0, "Asian Qualifiers Play-offs - Final"). They sit
under league 523 / season 2025/2026 in the index but their
`matchRound` is a playoff label, not a round number; the second
even carries a PenaltyShootout event. See `PREPROCESSING.md`.
Unlike the Azadegan sibling there are **no never-played
placeholder rows**: every payload has `header.status.finished`
True (1,245/1,245).

## Format

Double round-robin, 30 rounds, 16 teams — except 2026/2027, which
**expands to 18 teams (9 matches per round)**. The expansion year
relegated only one club (Mes Rafsanjan) and promoted three
(Sanat Naft Abadan, Nassaji Mazandaran FC, Mes Shahr Babak). No
playoffs, no split, no relegation round in the league itself: every
season is rounds 1–30 only. The regular season is modelled honestly
as one double round-robin per season.

**2025/2026 is partial in the warehouse, not in reality.** Rounds
1–20 are complete (8 matches each), round 21 has 5/8, round 22
8/8, round 23 5/8, and rounds 24–30 are entirely absent — the
warehouse simply stops at 2026-02-27 for this league (no Mar–May
2026 rows exist for it anywhere in the index; the Azadegan sibling
is complete through 2026-07-17, so this is a league-specific pull
gap). The virgin window is therefore n = 178, rounds 1–23, and the
verdict must carry that caveat; 2026/2027 is the confirmatory
window, reserved until complete.

Churn is small and regular: exactly 2 clubs turn over every season
through 2025/2026 (2 relegated, 2 promoted from the Azadegan
League), then 1 out / 3 in at the 2026/2027 expansion. Over the six
seasons 23 distinct team ids appear; a core of ~14 clubs is present
in most seasons. Promoted clubs arrive from the tier below
(Azadegan League, FotMob 9372 — the sibling build, whose goals
model failed its dev gate; see the X2 discussion in `FEATURES.md`
and `MODEL_DESIGN.md`).

## League-identity trap (read before filtering anything)

FotMob's `general.leagueId` is a **season-edition id, not the
competition id**. It reads 523 in most seasons but 880658 (one
match, 2022/2023 round 17, a postponed fixture), 886556
(2023/2024 rounds 12–30) and 893543 (all of 2024/2025).
`general.parentLeagueId` is 523 in **every** payload and
`general.leagueName` is "Persian Gulf Pro League" in all but the
latest 15 rows. Those 15 (2026/2027 rounds 11–12, from 2026-10-30)
read leagueName "Persian Gulf" — FotMob renamed the display name
mid-season; rounds continue the sequence with the same 18 teams,
so they are the same competition. Any filter on `leagueId == 523`
or on `leagueName == "Persian Gulf Pro League"` silently drops
real league matches (52 payloads across three seasons on the id
alone). The builder keys on `parentLeagueId == 523` plus an
accepted-name pair. **Id 523 is a single competition** — the
AU-Championship parent-container pattern (one id hiding ten
competitions) does not apply here: every payload has parent 523,
one league name per era, and one round sequence per season.

## Field coverage per season (played league matches, payload-verified)

| field | 21/22 | 22/23 | 23/24 | 24/25 | 25/26 | 26/27 | total |
|---|---:|---:|---:|---:|---:|---:|---:|
| FT score (header/index) | 240/240 | 240/240 | 240/240 | 240/240 | 178/178 | 105/105 | 1,243/1,243 |
| stats block non-null | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| shotmap shots > 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| lineup non-null | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| lineup (2025/26+ era) | — | — | — | — | 178/178 | 95/105 | 273 |
| referee text non-empty | 0 | 0 | 0 | 0 | 14 | 29 | **43** |
| event feed non-empty | 192 | 203 | 218 | 214 | 176 | 103 | 1,106 |
| Half marker (of non-empty) | 192 | 203 | 218 | 214 | 176 | 103 | 1,106/1,106 |
| period splits | 0 | 0 | 0 | 0 | 0 | 0 | **0** |

- **Scores**: every played league match has a parseable FT score;
  the index score, `header.status.scoreStr`, and
  `header.teams[].score` agree on all 1,243 played league matches
  (asserted in the builder).
- **Stats / xG / shotmap**: absent in **all** 1,245 payloads, in
  every season. `content.stats` is JSON null; `content.shotmap`
  is `{"shots": [], "Periods": ...}` with an empty shot list.
  There is no xG anywhere, no SOT, no corners, no total-shots —
  in any season, including the virgin window. This is a
  scores-only corpus for every candidate except cards (below).
- **Lineups**: absent in all 960 dev-season payloads; present
  (real XI data) in 2025/2026 (178/178 league) and 2026/2027
  (95/105). A lineup feature cannot be fitted on dev data that
  does not have it, and none is reliability-checked — see
  `FEATURES.md` R6.
- **Referee**: the `infoBox.Referee` dict *exists* in 2021/2022–
  2024/2025 but its `text` is `""` in all 960 matches — dict
  presence is not data. A referee NAME appears in only 14/178
  (2025/2026, 11 distinct) and 29/105 (2026/2027, 21 distinct)
  matches. No referee feature is possible on dev seasons.
- **Events**: present in 1,106/1,243 played league matches
  (89.0%). Every non-empty feed carries Half markers. Event
  types are Half, Goal, Card, Substitution (and one
  PenaltyShootout in the excluded playoff row). Goal events
  reproduce the FT score in all but 2 matches (see Quirks).
- **Cards from events — a feed break, not a trend**: Yellow
  events are **0 in 2021/2022–2024/2025** and present from
  2025/2026 (749 yellows in 178 league matches, 4.21/match,
  175/178 matches with a yellow event; 331 in 105 matches in
  2026/2027, 3.15/match). Red-family events (Red + YellowRed)
  rise steadily 0.096 → 0.129 → 0.188 → 0.233 → 0.242 → 0.219
  per match across the six seasons — a completeness ramp in the
  feed, not a plausible real trend in reds. Pre-2025/2026 card
  zeros are **feed absence, never true zeros**: no cards target
  can be built on dev seasons, and no cross-season card
  reliability may be pooled across the break. See EDA F6.

## Quirks

- **Team rename (same FotMob id, new name)**: id 139914 "Foolad
  Khouzestan" → "Foolad Khuzestan" during 2023/2024 (5 home
  matches under the old spelling, 10 under the new). Team
  identity is the FotMob id throughout; the builder and the fit
  key on ids, never names. No name maps to more than one id.
- **Goal-event feed gaps**: 137 played league matches (11.0%)
  have an empty event feed — 129 of them 0-0s, 8 with goals.
  Those 8 have no HT split; they keep their FT score and enter
  the goals fit normally. The 2 feeds that disagree with the FT
  score (3765423 undercounts 3-0 as 0-1; 3765395 totals 4-2
  against a 0-3 FT) are flagged `score_events_mismatch` and
  their HT is NaN. HT goals are therefore derivable for 1,233
  matches.
- **No shootouts, no extra-time scores in league matches**: the
  FT score is the regulation score in every league match.
- **2026/2027 round 11 is partial at the warehouse cutoff**
  (6/9 played by 2026-11-08); rounds 1–10 and 12 are complete as
  pulled. The 3 absent round-11 fixtures are postponed or not yet
  played — the warehouse holds no row for them, and nothing is
  imputed.
