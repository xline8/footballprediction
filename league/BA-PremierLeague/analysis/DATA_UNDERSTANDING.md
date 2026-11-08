# Phase 1 — Data Understanding: FotMob Bosnia-Herzegovina Premier League

Corpus: `data_enrichment/fotmob_world/` — FotMob league id **267**,
1,036 matchDetails JSONs, seasons 2021/2022 → 2026/2027 (in progress).
Inventory: every number below was measured on the files
(`league/BA-PremierLeague/analysis/inventory_summary.json`), not taken
from the index flags — the index's own `has_stats` / `has_shotmap` /
`has_period_splits` flags are all `False` for this league, which turns
out to understate the event feed and correctly state the stats feed.

## 0. Integrity headline

- 1,036 files = 1,036 unique match ids = 1,036 rows in
  `fotmob_world_index.csv` for league 267. No duplicates, nothing on
  disk missing from the index, nothing in the index missing on disk.
- All 1,036 finished (`header.status.finished`, `reason = FT` except
  the 4 awarded matches, reason `AW`).

## 1. Payload anatomy (one matchDetails JSON)

| Section | Contents | Modelling relevance |
|---|---|---|
| `general` | matchId, leagueId (tournament id, varies by season), parentLeagueId 267, round name, home/away team **ids + names**, `coverageLevel = 'lower'`, kickoff UTC | identity, season/round structure |
| `header.status` | `scoreStr` (official FT score), red-card counts, `awarded` flag, `reason` (FT / AW) | FT target, anomaly flags |
| `header.events` | goals/red cards grouped by player | redundant with matchFacts events |
| `content.matchFacts.events.events` | event list of exactly three types: Goal (scorer, `isHome` = credited side, minute), Half (minute 45 = HT score, minute 90 = FT score), Card (`card` ∈ YellowRed/Red only — **no Yellow events exist**) | HT derivation, (red-only) cards |
| `content.stats` | **null in 1,036/1,036** | no team stats of any kind: no SOT, corners, xG, possession, cards |
| `content.shotmap.shots` | present as a key, **empty list in 1,036/1,036** | no shots, no xG, no xGOT |
| `content.lineup` | present in 13/1,036 (scattered, 2022/23–2025/26) | unusable — no lineup features |
| `content.playerStats` | absent (falsy) in 1,036/1,036 | no player-level data |
| `content.matchFacts.infoBox` | Tournament (round), Stadium (null), Referee (`text` empty in 1,036/1,036), Attendance (null) | no referee, no attendance |
| `content.table`, `h2h`, `momentum` | standings snapshot, head-to-head, momentum flag | not used (post-match snapshots; leakage risk if used naively) |

## 2. Coverage matrix (share of matches with real content, %)

| Season | n | Stats FT | Shotmap shots>0 | Lineups | Referee | Events>0 | HT derivable |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 198 | 0 | 0 | 0 | 0 | 90 | 90 |
| 2022/2023 | 198 | 0 | 0 | 4 | 0 | 94 | 94 |
| 2023/2024 | 198 | 0 | 0 | 0 | 0 | 95 | 95 |
| 2024/2025 | 198 | 0 | 0 | 2 | 0 | 96 | 96 |
| 2025/2026 | 180 | 0 | 0 | 1 | 0 | 89 | 89 |
| 2026/2027 (partial) | 64 | 0 | 0 | 0 | 0 | 89 | 89 |
| **Total** | **1,036** | **0** | **0** | **1** | **0** | **93** | **93** |

Reading of the matrix: **this is a scores + events corpus, nothing
else.** The stats feed never existed for this league in FotMob (not a
windowed death like J2's — it is 0 in every season including the
current one). The shotmap block is an empty shell. The event feed is
the only enrichment, and it is itself thin: goals + half markers +
red-family cards only — no substitutions, no yellow cards, no
assist/shot detail.

## 3. Format (verified from payloads, not from the web)

- 2021/2022–2024/2025: **12 teams, 33 rounds** (6 matches per round,
  rounds 1–33, uniform). Triple round-robin; **no split-group /
  championship / relegation round and no playoff phase** — round
  names are plain 1–33 in every season, `hasPlayoff` never set.
- 2025/2026: **10 teams, 36 rounds** (5 matches per round, rounds
  1–36). Quadruple round-robin; the league contracted 12 → 10
  (3 clubs left, 1 promoted in).
- 2026/2027 (in progress): **10 teams**, rounds 1–13 played,
  64 matches (round 10 has 4 matches — one fixture not in the
  warehouse, presumably postponed; it is simply absent, not a
  missing file). Dates 2026-08-07 → 2026-11-08.
- Team identity is stable by FotMob team id (18 ids total; no name
  maps to two ids). Four ids carry two name spellings, all
  diacritic variants (Željezničar/Zeljeznicar, Široki/Siroki Brijeg,
  Velež/Velez Mostar, Čelik/Celik Zenica). Keying on names would
  split four clubs in two; keying on ids is exact.
- Churn is real: 2 clubs change in most seasons (2022/23: Igman
  Konjic, Sloga Doboj in; Radnik Bijeljina, Rudar Prijedor out;
  2023/24: GOSK Gabela, FK Zvijezda 09 in; Sloboda Tuzla, FK Leotar
  out; 2024/25: Sloboda Tuzla, Radnik Bijeljina in; Zvijezda 09,
  FK Tuzla City out; 2025/26: Rudar Prijedor in, 3 out;
  2026/27: Čelik Zenica, BSK Banja Luka in; Posušje, Rudar
  Prijedor out). Promoted clubs enter with no in-league history —
  the SHRINK-arm case (see MODEL_DESIGN).

## 4. Quirk register (each verified on the files)

1. **Four awarded matches** (official 3-0 / 0-3, reason `AW`):
   `3638998` (2021-09-21, Velež–Borac 0-3), `3844149` (2022-05-14,
   Široki–Sarajevo 3-0), `4575363` (2024-09-03, Zrinjski–Posušje
   3-0), `4757570` (2025-04-26, Sloboda–Posušje 0-3). In all four
   the goal events undercount the official score (the awarded
   scoreline does not reflect play). They are **excluded from
   fitting and evaluation everywhere** (AE-ProLeague precedent);
   kept in the CSV with `awarded = True`.
2. **Goal events vs official score**: apart from the 4 awarded
   matches, goal events reproduce `scoreStr` exactly in 1,032/1,032
   matches. `scoreStr` is the source of truth.
3. **HT score is derived, not stored.** No explicit HT field exists.
   The Half event at minute 45 carries `homeScore`/`awayScore` =
   the HT score. It agrees with goal-events ≤ 45 on **961/961**
   matches where present. HT is present for 961/1,036 (93%); the
   other 75 matches have no events at all.
4. **Cards are red-family only.** 205 Card events total: 77
   YellowRed + 128 Red, **0 Yellow**. The event feed omits yellow
   cards entirely, so no yellow-cards target exists in any form
   (no stats feed to fall back on either). Red cards alone
   (0.20/match) are a rare-event count with no reliability evidence
   and are not a candidate.
5. **No substitutions in the event feed** (only Goal/Half/Card).
   No minutes, no game-state features beyond the HT score.
6. **Round-10 2026/27 gap**: one fixture missing from the warehouse
   (4 matches in round 10 vs 5 elsewhere). Treated as absent, not
   imputed.

## 5. Definition alignment

| Concept | FotMob BA source | Alignment result |
|---|---|---|
| FT score | `header.status.scoreStr` (official) | Source of truth; goal events reproduce it except the 4 awarded matches. |
| HT score | Half event, minute 45 | Cross-validated against goal events ≤45: 961/961 agreement. Available 961/1,036. |
| Goals | FT score | The only target that exists. |
| SOT / corners / total shots / xG / xGOT | — | Do not exist (stats null, shotmap empty, all seasons). |
| Yellow cards | — | Do not exist (0 Yellow events; no stats feed). |
| Red cards | Card events (YellowRed/Red) | Exist but 0.20/match; rare-event, no candidate. |
| Referee | infoBox Referee text | Empty in 1,036/1,036. |
| Lineups | `content.lineup` | 13/1,036 scattered — unusable. |
