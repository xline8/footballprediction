# Phase 1 — Data Understanding: FotMob Albania Kategoria Superiore

Corpus: `data_enrichment/fotmob_world/` — FotMob league id **260**,
969 matchDetails JSONs, seasons 2021/2022 → 2026/2027 (in progress).
Inventory: every number below was measured on the files
(`league/AL-KategoriaSuperiore/analysis/inventory_summary.json`), not taken
from the index flags — the index's own `has_stats` / `has_shotmap` /
`has_period_splits` flags are all `False` for this league, which turns
out to correctly state the stats/shotmap feed and understate the event
feed (events exist for 887/969 matches).

## 0. Integrity headline

- 969 files = 969 unique match ids = 969 rows in
  `fotmob_world_index.csv` for league 260. No duplicates, nothing on
  disk missing from the index, nothing in the index missing on disk.
- All 969 finished (`header.status.finished`, `reason = FT`).
  **No awarded matches** (0/969) — unlike BA, there is nothing to
  exclude on awarded grounds.

## 1. Payload anatomy (one matchDetails JSON)

| Section | Contents | Modelling relevance |
|---|---|---|
| `general` | matchId, leagueId (tournament id, varies by season), parentLeagueId 260, `leagueRoundName`, home/away team **ids + names**, `coverageLevel = 'lower'`, kickoff UTC | identity, season/round structure |
| `header.status` | `scoreStr` (official FT score), red-card counts, `awarded` flag, `reason` (FT) | FT target, anomaly flags |
| `header.events` | goals/red cards grouped by player | redundant with matchFacts events |
| `content.matchFacts.events.events` | event list of exactly three types: Goal (scorer, `isHome` = credited side, `time` = minute, `newScore`), Half (`time` 45 = HT score, `time` 90 = FT score, `halfStrShort` HT/FT), Card (`card` ∈ YellowRed/Red only — **no Yellow events exist**) | HT derivation, (red-only) cards |
| `content.stats` | **null in 969/969** | no team stats of any kind: no SOT, corners, xG, possession, cards |
| `content.shotmap.shots` | present as a key, **empty list in 969/969** | no shots, no xG, no xGOT |
| `content.lineup` | absent (falsy) in 969/969 | no lineup features |
| `content.playerStats` | absent (falsy) in 969/969 | no player-level data |
| `content.matchFacts.infoBox` | Tournament (round), Stadium (null), Referee (`text` empty in 969/969), Attendance (null) | no referee, no attendance |
| `content.table`, `h2h`, `momentum` | standings snapshot, head-to-head, momentum flag | not used (post-match snapshots; leakage risk if used naively) |

## 2. Coverage matrix (share of matches with real content, %)

| Season | n | Stats FT | Shotmap shots>0 | Lineups | Referee | Events>0 | HT derivable |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 180 | 0 | 0 | 0 | 0 | 89 | 89 |
| 2022/2023 | 180 | 0 | 0 | 0 | 0 | 92 | 92 |
| 2023/2024 | 184 | 0 | 0 | 0 | 0 | 92 | 92 |
| 2024/2025 | 184 | 0 | 0 | 0 | 0 | 89 | 89 |
| 2025/2026 | 186 | 0 | 0 | 0 | 0 | 93 | 93 |
| 2026/2027 (partial) | 55 | 0 | 0 | 0 | 0 | 98 | 98 |
| **Total** | **969** | **0** | **0** | **0** | **0** | **92** | **92** |

Reading of the matrix: **this is a scores + events corpus, nothing
else.** The stats feed never existed for this league in FotMob (not a
windowed death like J2's — it is 0 in every season including the
current one). The shotmap block is an empty shell. The event feed is
the only enrichment, and it is itself thin: goals + half markers +
red-family cards only — no substitutions, no yellow cards, no
assist/shot detail.

## 3. Format (verified from payloads, not from the web)

- Every season: **10 teams, 36 rounds** (5 matches per round,
  rounds 1–36, uniform). Quadruple round-robin; **no split-group /
  championship / relegation round** — the regular season is plain
  rounds 1–36 in every season.
- **A Final Four playoff follows the regular season from
  2023/2024** (14 matches total, flagged `playoff=True` in the CSV
  and excluded from every fit and evaluation — see §4):
  - 2023/2024 and 2024/2025: 2 semi-finals (round name `1/2`) +
    a bronze match + a final (4 matches each season). Regular
    season ended 2024-05-11 / 2025-04-27; playoffs 2024-05-17..26 /
    2025-05-04..12.
  - 2025/2026: a 6-match Final Four **round-robin** (each of the
    top 4 plays each other once), mislabelled by FotMob as rounds
    `1`/`2`/`3` and dated 2026-05-16..31 (regular season ended
    2026-05-10, round 36 played that day). The round label alone
    cannot separate these from regular rounds 1–3; the builder
    identifies them by season + date ≥ 2026-05-16.
  - 2021/2022 and 2022/2023 have no playoff (180 matches each).
- 2026/2027 (in progress): **10 teams**, rounds 1–11 played,
  55 matches, dates 2026-08-21 → 2026-11-08. No playoff yet.
- Team identity is stable by FotMob team id (15 ids total; no name
  maps to two ids). Four ids carry two name spellings, all
  diacritic variants (Teuta Durrës/Teuta Durres, Skënderbeu/
  Skenderbeu, Laçi/Laci, FC Dinamo City/Dinamo Tirana). In
  2026/2027 three matches carry the unaccented spelling (one each
  for Laçi, Skënderbeu, Teuta Durrës). Keying on names would split
  four clubs in two; keying on ids is exact.
- Churn is real: 2 clubs change in every season (2022/23: Bylis,
  KF Erzeni in; Dinamo Tirana, Skënderbeu out; 2023/24: Dinamo
  Tirana, Skënderbeu in; Bylis, Kastrioti out; 2024/25: Bylis,
  Elbasani in; Kukesi, KF Erzeni out; 2025/26: Flamurtari, Vora
  in; Laçi, Skënderbeu out; 2026/27: Laçi, Skënderbeu in; Bylis,
  Flamurtari out). Promoted clubs enter with no in-league history —
  the SHRINK-arm case (see MODEL_DESIGN).

## 4. Quirk register (each verified on the files)

1. **Fourteen playoff matches** (see §3): `4478609`, `4478610`,
   `4481143`, `4481144` (2023/24); `4781508`, `4781509`,
   `4784335`, `4784336` (2024/25); `5524078`–`5524083` (2025/26
   Final Four round-robin). They are single-leg knockouts (2023/24,
   2024/25) or a top-4 mini-league (2025/26) — a different
   competition structure from the 36-round regular season, played
   only by the top 4. They are **excluded from fitting and
   evaluation everywhere** (regular-phase scope, MODEL_DESIGN);
   kept in the CSV with `playoff = True`.
2. **Goal events vs official score**: goal events reproduce
   `scoreStr` exactly in 969/969 matches. `scoreStr` is the source
   of truth. Total goals in the corpus: 2,190.
3. **HT score is derived, not stored.** No explicit HT field exists.
   The Half event at `time` 45 (`halfStrShort` = HT) carries
   `homeScore`/`awayScore` = the HT score. It agrees with
   goal-events ≤ 45 on **887/887** matches where present. HT is
   present for 887/969 (92%); the other 82 matches have no events
   at all. (Note: Goal/Half events carry their minute in `time`,
   not `minute` — `minute` is null on these events.)
4. **Cards are red-family only.** 230 Card events total: 68
   YellowRed + 162 Red, **0 Yellow**. The event feed omits yellow
   cards entirely, so no yellow-cards target exists in any form
   (no stats feed to fall back on either). Red cards alone
   (0.24/match) are a rare-event count with no reliability evidence
   and are not a candidate.
5. **No substitutions in the event feed** (only Goal/Half/Card).
   No minutes, no game-state features beyond the HT score.
6. **No awarded matches** (0/969): no exclusion on awarded grounds,
   unlike BA (4) and AE.

## 5. Definition alignment

| Concept | FotMob AL source | Alignment result |
|---|---|---|
| FT score | `header.status.scoreStr` (official) | Source of truth; goal events reproduce it 969/969. |
| HT score | Half event, `time` 45, `halfStrShort` HT | Cross-validated against goal events ≤45: 887/887 agreement. Available 887/969. |
| Goals | FT score | The only target that exists. |
| SOT / corners / total shots / xG / xGOT | — | Do not exist (stats null, shotmap empty, all seasons). |
| Yellow cards | — | Do not exist (0 Yellow events; no stats feed). |
| Red cards | Card events (YellowRed/Red) | Exist but 0.24/match; rare-event, no candidate. |
| Referee | infoBox Referee text | Empty in 969/969. |
| Lineups | `content.lineup` | 0/969 — do not exist. |
| Playoff matches | round `1/2`/`bronze`/`final`, or 2025/26 rounds 1–3 dated ≥ 2026-05-16 | Flagged, excluded from fits/evaluations (different format). |
