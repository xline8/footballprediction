# Phase 1 — Data Understanding: FotMob Armenia Premier League

Corpus: `data_enrichment/fotmob_world/` — FotMob league id **118**,
881 matchDetails JSONs, seasons 2021/2022 → 2026/2027 (in progress).
Inventory: every number below was measured on the files
(`league/AM-PremierLeague/analysis/inventory_summary.json`), not taken
from the index flags — the index's own `has_stats` / `has_shotmap` /
`has_period_splits` flags are all `False` for this league, which turns
out to state the stats/shotmap feed correctly and understate the event
feed (events exist for 828/881 matches).

## 0. Integrity headline

- 881 files = 881 unique match ids = 881 rows in
  `fotmob_world_index.csv` for league 118. No duplicates, nothing on
  disk missing from the index, nothing in the index missing on disk.
- All 881 finished (`header.status.finished`, `reason = FT` except
  the 7 awarded matches, `reason = AW`).
- **7 awarded matches** (all 2024/2025, all involving West Armenia —
  see §4 quirk 1). They stay in the CSV flagged `awarded = True`
  and are excluded from every fit and evaluation (BA/AE precedent).

## 1. Payload anatomy (one matchDetails JSON)

| Section | Contents | Modelling relevance |
|---|---|---|
| `general` | matchId, leagueId (tournament id, varies by season), parentLeagueId 118, `leagueRoundName`, home/away team **ids + names**, `coverageLevel = 'lower'`, kickoff UTC | identity, season/round structure |
| `header.status` | `scoreStr` (official FT score), red-card counts, `awarded` flag, `reason` (FT / AW) | FT target, anomaly flags |
| `header.events` | goals/red cards grouped by player | redundant with matchFacts events |
| `content.matchFacts.events.events` | event list of exactly three types: Goal (scorer, `isHome` = credited side, `time` = minute, `newScore`), Half (`time` 45 = HT score, `time` 90 = FT score, `halfStrShort` HT/FT), Card (`card` ∈ YellowRed/Red only — **no Yellow events exist**) | HT derivation, (red-only) cards |
| `content.stats` | **null in 881/881** | no team stats of any kind: no SOT, corners, xG, possession, cards |
| `content.shotmap.shots` | present as a key, **empty list in 881/881** | no shots, no xG, no xGOT |
| `content.lineup` | null in 865/881; the other 16 (all 2025/2026) are a shell with `lineupType = "unavailable"`, empty starters, no away-team starters | no lineup features |
| `content.playerStats` | absent (falsy) in 881/881 | no player-level data |
| `content.matchFacts.infoBox` | Tournament (round), Stadium (null), Referee (`text` empty in 881/881), Attendance (null) | no referee, no attendance |
| `content.table`, `h2h`, `momentum` | standings snapshot, head-to-head, momentum flag | not used (post-match snapshots; leakage risk if used naively) |

## 2. Coverage matrix (share of matches with real content, %)

| Season | n | Stats FT | Shotmap shots>0 | Lineups | Referee | Events>0 | HT derivable |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 144 | 0 | 0 | 0 | 0 | 94 | 94 |
| 2022/2023 | 180 | 0 | 0 | 0 | 0 | 93 | 93 |
| 2023/2024 | 180 | 0 | 0 | 0 | 0 | 96 | 96 |
| 2024/2025 | 165 | 0 | 0 | 0 | 0 | 95 | 95 |
| 2025/2026 | 135 | 0 | 0 | 0 | 0 | 92 | 92 |
| 2026/2027 (partial) | 77 | 0 | 0 | 0 | 0 | 96 | 96 |
| **Total** | **881** | **0** | **0** | **0** | **0** | **94** | **94** |

Reading of the matrix: **this is a scores + events corpus, nothing
else.** The stats feed never existed for this league in FotMob (not a
windowed death — it is 0 in every season including the current one).
The shotmap block is an empty shell. The event feed is the only
enrichment, and it is itself thin: goals + half markers +
red-family cards only — no substitutions, no yellow cards, no
assist/shot detail.

## 3. Format (verified from payloads, not from the web)

- **No split-group, championship/relegation round, or playoff in
  any season.** Round names are plain integers 1–36 in every
  season; there is no post-regular-season phase of any kind.
- The team count — and therefore the schedule — **changes every
  season** (verified from payloads; this is the league's defining
  format fact, and the reason the coordinator's "uneven seasons"
  scouting is real):
  - 2021/2022: **9 teams**, 36 rounds × 4 matches = 144; each team
    plays 32 matches (8 opponents × 4).
  - 2022/2023: **10 teams**, 36 rounds × 5 = 180; 36 matches/team.
  - 2023/2024: **10 teams**, 36 rounds × 5 = 180; 36 matches/team.
  - 2024/2025: **11 teams**, 33 rounds × 5 = 165; 30 matches/team
    (10 opponents × 3). Includes the 7 awarded matches; 158
    actually played.
  - 2025/2026: **10 teams**, 27 rounds × 5 = 135; 27 matches/team
    (triple round-robin, 9 opponents × 3). Complete.
  - 2026/2027 (in progress): **12 teams**, rounds 1–13 played,
    77 matches, dates 2026-07-31 → 2026-11-08. Round 13 has only
    5 matches (one fixture unplayed/postponed as of the warehouse
    snapshot) and one round-15 fixture (Van–Syunik 1-1,
    2026-08-20, match 5973016) was played early, ahead of its
    round. No round 14 has been played yet. The virgin window is
    therefore rounds 1–13 (+1 early round-15 fixture), n = 77.
- Team identity is stable by FotMob team id (15 ids total; each id
  carries exactly one name spelling — no diacritic variants, so
  names would also key cleanly, but ids are used regardless).
- Churn is real — at least one club changes every season:
  2022/23: Lernayin Artsakh, Shirak in; Noravank out. 2023/24:
  West Armenia in; Lernayin Artsakh out. 2024/25: Gandzasar in
  (11 teams). 2025/26: West Armenia out. 2026/27: Sardarapat,
  Syunik in (12 teams). Promoted clubs enter with no in-league
  history — the SHRINK-arm case (see MODEL_DESIGN).

## 4. Quirk register (each verified on the files)

1. **Seven awarded matches** (official 3-0 / 0-3, reason `AW`),
   all 2024/2025, all involving West Armenia: `4558174`
   (2024-09-18, Urartu FC–West Armenia 3-0 — played on the day,
   1-2 on goal events, then overturned to 3-0), `4558250`
   (2024-11-21, Pyunik–West Armenia 3-0), `4558261` (2025-02-28,
   Gandzasar–Ararat 0-3 — Ararat were awarded the win),
   `4558323` (2025-05-09, West Armenia–Ararat Armenia 0-3),
   `4558316` (2025-05-16, Alashkert FC–West Armenia 3-0),
   `4558304` (2025-05-22, West Armenia–Gandzasar 0-3), `4558305`
   (2025-05-27, Shirak–West Armenia 3-0). Six of the seven have
   zero goal events (never played — forfeits); the seventh was
   played and overturned. They are **excluded from every fit and
   evaluation** (administrative scorelines, not played football —
   the BA/AE precedent); kept in the CSV with `awarded = True`.
2. **Goal events vs official score**: goal events reproduce
   `scoreStr` exactly in 874/881 matches. The 7 exceptions are
   exactly the 7 awarded matches. `scoreStr` is the source of
   truth. Total goals in the corpus: 2,390 (2,369 excluding the
   7 awarded scorelines' 21 goals).
3. **HT score is derived, not stored.** No explicit HT field exists.
   The Half event at `time` 45 (`halfStrShort` = HT) carries
   `homeScore`/`awayScore` = the HT score. It agrees with
   goal-events ≤ 45 on **828/828** matches where present. HT is
   present for 828/881 (94%); the other 53 matches have no events
   at all (6 of them are the unplayed awarded forfeits; 47 are
   played matches whose event feed is simply empty). (Note:
   Goal/Half events carry their minute in `time`, not `minute` —
   `minute` is null on these events.)
4. **Cards are red-family only.** 186 Card events total: 135 Red +
   51 YellowRed, **0 Yellow**. The event feed omits yellow cards
   entirely, so no yellow-cards target exists in any form (no stats
   feed to fall back on either). Red cards alone (0.21/match) are
   a rare-event count with no reliability evidence and are not a
   candidate.
5. **No substitutions in the event feed** (only Goal/Half/Card).
   No minutes, no game-state features beyond the HT score.
6. **Lineup shells.** 16 payloads in 2025/2026 carry a `lineup`
   dict, but `lineupType = "unavailable"` with empty starters
   (the away side lists one unavailable player with an injury
   note). There is no usable lineup content in any season.

## 5. Definition alignment

| Concept | FotMob AM source | Alignment result |
|---|---|---|
| FT score | `header.status.scoreStr` (official) | Source of truth; goal events reproduce it except the 7 awarded matches. |
| HT score | Half event, `time` 45, `halfStrShort` HT | Cross-validated against goal events ≤45: 828/828 agreement. Available 828/881. |
| Goals | FT score | The only target that exists. |
| SOT / corners / total shots / xG / xGOT | — | Do not exist (stats null, shotmap empty, all seasons). |
| Yellow cards | — | Do not exist (0 Yellow events; no stats feed). |
| Red cards | Card events (YellowRed/Red) | Exist but 0.21/match; rare-event, no candidate. |
| Referee | infoBox Referee text | Empty in 881/881. |
| Lineups | `content.lineup` | 0/881 with real content (16 unavailable shells). |
| Playoff / split-group matches | — | None exist in any season (round names plain integers 1–36). |
