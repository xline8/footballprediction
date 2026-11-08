# Step 1 — Data Understanding: Nigeria Professional Football League (FotMob 533)

Corpus: `data_enrichment/fotmob_world/Nigeria/Professional Football League/`
— 1,830 matchDetails JSONs, seasons 2021/2022 → 2026/2027, one tier.
Inventory tool: `inventory_ng.py` (worktree root; raw results in
`analysis/inventory_summary.json`). Every number below was measured on
the files, never taken from the index's `has_*` flags — which are all
`False` here anyway and, per program experience, test key presence,
not non-null content.

## 0. Integrity headline

- 1,830 index rows = 1,830 files on disk = 1,830 unique match ids. No
  duplicates, nothing on disk missing from the index, nothing in the
  index missing on disk. All scores parse (`score_parse_fail`: none).
- **FotMob 533 is a parent id**, like RU2's 9123: each payload's
  `general.parentLeagueId` is 533, while `general.leagueId` /
  `leagueName` name the sub-tournament. One sub-tournament per season
  except the abridged 2023 season (see §3).

## 1. Payload anatomy (one matchDetails JSON)

| Section | Contents | Modelling relevance |
|---|---|---|
| `general` | matchId, leagueId/Name, `parentLeagueId` 533, `matchRound`, home/away team **ids + names**, kickoff UTC | identity, season/round structure, sub-tournament |
| `header.status` | `scoreStr` (official FT score), red-card counts, `started` / `finished` / `awarded` flags, `reason` (incl. awarded win), half timestamps | FT target, anomaly flags |
| `content.matchFacts.events.events` | Goal (scorer, `isHome`, minute), Card (`card` ∈ YellowRed/Red only — see §4), Half (time 45/90, **with `homeScore`/`awayScore` at HT**) | HT derivation, dismissals |
| `content.matchFacts.infoBox` | Match Date, Tournament, Stadium (always null here), Referee (key present, **text always empty**), Attendance (null) | no usable referee/stadium data |
| `content.stats` | key present; `Periods` blocks carry **no stat rows in any payload** | SOT/corners/cards/xG targets: absent |
| `content.shotmap.shots` | key present; **empty list in every payload** | no per-shot data |
| `content.lineup`, `content.playerStats` | keys present; lineup content in **exactly 1 payload** (4635917, simple starters only — see §2); playerStats empty everywhere | no lineup/player data usable as features |
| `content.table`, `h2h`, `momentum` | standings snapshot, head-to-head, momentum flag | not used (post-match snapshots; leakage risk) |

## 2. Coverage matrix (share of matches with real content, %)

| League-season | n | Stats (non-empty) | Shotmap (shots>0) | Events | HT score | Lineups | Player stats | Referee (non-empty text) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 380 | **0** | **0** | 91.6 | 91.6 | 0 | 0 | **0** |
| 2023 | 195 | **0** | **0** | 91.8 | 91.8 | 0 | 0 | **0** |
| 2023/2024 | 380 | **0** | **0** | 91.6 | 91.6 | 0 | 0 | **0** |
| 2024/2025 | 380 | **0** | **0** | 90.8 | 90.5 | 0.3 (1 match) | 0 | **0** |
| 2025/2026 | 379 | **0** | **0** | 88.9 | 88.9 | 0 | 0 | **0** |
| 2026/2027 (partial) | 116 | **0** | **0** | 87.9 | 87.9 | 0 | 0 | **0** |
| **Total** | **1,830** | **0** | **0** | **90.7** | **90.7** | **0.05 (1 match)** | **0** | **0** |

Reading of the matrix:

- **NG is a scores-only corpus, cleanly.** No season has any stats,
  shotmap, player-stat or referee content at all. The
  `has_stats`/`has_shotmap` index flags are `False` for all 1,830
  rows and the payloads confirm it by content — this is the opposite
  failure mode from the documented false positives (TH2/DK-1/ID/BRC/
  EE/FNL/FI-YK), where the flags said True on empty blocks.
  Lineups are the single exception to "empty everywhere": exactly
  **one** payload (4635917, Enyimba vs Akwa United, 2024/2025)
  carries a `lineupType: simple` block with 11 starters per side
  (names + shirt numbers only — no minutes, ratings or usable
  positions). One match's starters cannot support any feature and
  change no verdict; they are recorded here so the "empty" claim
  stays exact.
- Events exist in 1,659/1,830 matches (90.7%). The 171 matches without
  events are matches where FotMob carries no event feed at all (no
  Half markers either); their scores still come from `scoreStr` and
  are unaffected. Events carry **Goal (3,863), Half (3,316) and Card
  (155) only — no Substitutions** in any payload.
- HT scores are directly readable from the Half event at time 45
  (`homeScore`/`awayScore`): 1,645/1,813 eligible matches (90.7%).

## 3. Format

- **Single table, 20 teams, double round robin, 38 rounds, 380
  matches** in every full season (2021/2022, 2023/2024, 2024/2025,
  2025/2026, 2026/2027 in progress). Every round has exactly 10
  matches except 2025/2026 round 24 (9 — see §5) and the in-progress
  2026/2027 rounds 10/12 (8 each, matches yet to be played).
- **2023 is abridged** (the NPFL's one-off shortened season): two
  groups of 10 (Grp. A 90 + Grp. B 90, double round robin within
  group, 18 rounds each) followed by a 6-team Championship Group /
  Super 6 (15 matches, single round robin). The Championship Group
  is a **neutral-venue mini-tournament**: home goals 0.93 vs away
  1.13, home-win rate 20.0% vs 55.0% in the group stage, draw rate
  53.3% vs 31.1%. Stadium is null in every payload so the venue
  cannot be confirmed from the files, but the scorelines reverse
  home advantage outright (n=15). Frozen rule (prereg): the 15
  Championship Group matches are **excluded from every fit, score
  and EDA level**; the 180 group-stage matches are the league proper
  and are pooled with the other seasons (groups A/B are a single
  season's two disconnected components — cross-group levels rest on
  the DC fit's zero-init anchor, as in RU2; there are no cross-group
  matches to estimate a group effect from, and none are needed: the
  groups never meet except in the excluded Championship Group).
- **Turnover: 3–4 new clubs enter every season** (EDA §5) — promoted
  sides from the (unbuilt, not in the warehouse) Nigeria National
  League. There is no built Nigerian parent/sibling in the warehouse,
  so no cross-league mover prior exists; the SHRINK arm is the
  thin-data treatment (MODEL_DESIGN §2).
- Calendar: autumn–spring except 2023 (Jan–Jun 2023). Season date
  ranges: 2021/2022 2021-12-17→2022-07-17; 2023 2023-01-08→2023-06-11;
  2023/2024 2023-09-30→2024-06-23; 2024/2025 2024-08-31→2025-05-25;
  2025/2026 2025-08-22→2026-05-24; 2026/2027 2026-08-28→2026-11-08
  (in progress, rounds 1–12).

## 4. Cards: why K is not buildable

- The 155 Card events are **all dismissals**: YellowRed 50, Red 105,
  **0 plain Yellow events in 1,830 payloads**. No stats yellows exist
  either (stats empty). There is therefore **no yellow-card target**
  in any form — neither a stats feed nor an event feed — in any
  season. K-NG is NOT BUILDABLE (payload-level evidence in
  `prereg/PREREG_SCKT_NG_NOT_BUILDABLE.md`).
- Referee identity is empty in all 1,830 payloads (`infoBox.Referee`
  key present, `text` always `''`), so X8 has no input even if a
  target existed. Dismissals themselves (0.085/match in the events
  era) are a rare event with no reliability evidence and are not a
  target.

## 5. Anomalies (frozen handling in PREPROCESSING.md)

| match | season | issue | handling |
|---|---|---|---|
| 3786217 Kano Pillars vs Akwa United | 2021/2022, round 21 | **Phantom fixture**: `started=False`, `finished=False`, `scoreStr` null, index score `0-0`, no events | EXCLUDED from every fit/score/EDA level; stays in CSV with `finished=0`, null goals |
| 4464406 Enugu Rangers vs Enyimba | 2023/2024, round 35 | **Awarded win**: `awarded=True`, reason `awarded_win`, score 3-0, no events (match abandoned) | EXCLUDED from every fit/score/EDA level; stays in CSV with `awarded=1` |
| 4765626 Katsina United vs Abia Warriors | 2024/2025, round 34 | `finished=False` **but** score 5-1 with 6 Goal events (minutes 2–90) reconciling exactly to the score | KEPT: the flag is stale, the match was played; score and events agree. Noted here, not excluded |
| 2025/2026 round 24 | 2025/2026 | **One fixture absent from the warehouse entirely**: El Kanemi Warriors vs Kun Khalifat is in neither the index nor the disk (both clubs on 37 matches; season total 379 not 380) | Not a parsing gap; nothing to exclude (no row exists). Recorded as a warehouse gap |

Total excluded from every fit/score/EDA level: 17 rows (1 phantom +
1 awarded + 15 Championship Group) → **1,813 eligible rows**.

## 6. What does not exist here (explicit)

- No xG (of any kind), no SOT, no corners, no total shots, no cards
  target, no referee, no player data, no substitutions,
  no stadium, no attendance — in **any** season. Lineups exist in
  exactly one payload (4635917, simple starters only). S/C/K/T are
  not buildable (see MODEL_DESIGN §1). No proxy is constructed for
  any of them.
