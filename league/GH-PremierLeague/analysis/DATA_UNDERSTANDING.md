# Step 1 — Data Understanding: Ghana Premier League (FotMob 522)

Corpus: `data_enrichment/fotmob_world/Ghana/Premier League/` — 1,619
matchDetails JSONs, seasons 2021/2022 → 2026/2027, one tier.
Inventory tool: the content scan in `/tmp/gh` (raw results in
`analysis/inventory_summary.json`). Every number below was measured
on the files, never taken from the index's `has_*` flags — which are
all `False` here anyway and, per program experience, test key
presence, not non-null content.

## 0. Integrity headline

- 1,619 index rows = 1,619 files on disk = 1,619 unique match ids. No
  duplicates, nothing on disk missing from the index, nothing in the
  index missing on disk. All scores parse (`score` present on all
  1,619 rows).
- **Structural difference from every league built before: `general`
  and `header` are null in every payload.** There is no
  `header.status.scoreStr`, no `general.homeTeam`/`awayTeam` with
  ids, and no `finished`/`awarded` flags. Team identity and the FT
  score therefore come from the **index** (`home`/`away`/`score`
  columns), cross-checked against the payload where a check exists:
  index date == payload `Match Date` on 1,619/1,619, and goal-event
  counts reproduce the index score on 1,592/1,619 matches (the
  exceptions are the 23 awarded rows with no events, the 184
  event-less 0-0 draws with no goals to count, and the 4
  event-feed errors in §5 — the index score is the source of truth
  for all of them).

## 1. Payload anatomy (one matchDetails JSON)

| Section | Contents | Modelling relevance |
|---|---|---|
| `general` | **null in every payload** | nothing — team ids do not exist here |
| `header` | **null in every payload** | no `scoreStr`, no status flags |
| `content.matchFacts.events.events` | Goal (scorer, `isHome`, minute, `newScore`), Card (`card` ∈ YellowRed/Red only — see §4), Half (time 45/90, **with `homeScore`/`awayScore` at HT**) | HT derivation, dismissals |
| `content.matchFacts.infoBox` | Match Date, Tournament (id 522, `parentLeagueId` 522, round), Stadium (null), Referee (key present, **text always empty**), Attendance (null) | round, no usable referee/stadium data |
| `content.stats` | key present; `Periods` blocks carry **no stat rows in any payload** | SOT/corners/cards/xG targets: absent |
| `content.shotmap.shots` | key present; **empty list in every payload** | no per-shot data |
| `content.lineup`, `content.playerStats` | keys present; lineup content in **10 payloads** (see §2) with **zero starters in all 10**; playerStats empty everywhere | no lineup/player data usable as features |
| `content.table`, `h2h`, `momentum` | standings snapshot, head-to-head, momentum flag | not used (post-match snapshots; leakage risk) |

## 2. Coverage matrix (share of matches with real content, %)

| League-season | n | Stats (non-empty) | Shotmap (shots>0) | Events | HT score | Lineups (starters) | Player stats | Referee (non-empty text) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 306 | **0** | **0** | 89.2 | 89.2 | 0 | 0 | **0** |
| 2022/2023 | 306 | **0** | **0** | 88.6 | 88.6 | 0 | 0 | **0** |
| 2023/2024 | 306 | **0** | **0** | 89.2 | 89.2 | 0 | 0 | **0** |
| 2024/2025 | 305 | **0** | **0** | 83.9 | 83.9 | 0 | 0 | **0** |
| 2025/2026 | 306 | **0** | **0** | 84.6 | 84.6 | 0 | 0 | **0** |
| 2026/2027 (partial) | 90 | **0** | **0** | 88.9 | 88.9 | 0 | 0 | **0** |
| **Total** | **1,619** | **0** | **0** | **87.2** | **87.2** | **0** | **0** | **0** |

Reading of the matrix:

- **Ghana is a scores-only corpus, cleanly.** No season has any stats,
  shotmap, player-stat or referee content at all. The
  `has_stats`/`has_shotmap` index flags are `False` for all 1,619
  rows and the payloads confirm it by content.
- Lineup blocks exist in exactly 10 payloads (2 in 2022/2023, 1 in
  2023/2024, 2 in 2024/2025, 5 in 2025/2026) but carry **zero
  starters in all 10** (types `standard`/`unavailable`, team ids
  only — e.g. Medeama SC 106975). Ten empty blocks cannot support
  any feature and change no verdict; they are recorded here so the
  "empty" claim stays exact.
- Events exist in 1,412/1,619 matches (87.2%). The 207 matches
  without events split exactly two ways (measured, §5): 184 are
  0-0 draws (played, goalless — 21 other 0-0 draws *do* carry Half
  markers, so the feed is present-or-absent per match, not per
  scoreline) and 23 are awarded 3-0/0-3 forfeits. No event-less
  match carries any other scoreline.
- HT scores are directly readable from the Half event at time 45
  (`homeScore`/`awayScore`): 1,412/1,619 matches (87.2%), 1,408 of
  them trustworthy (4 flagged suspect, §5).

## 3. Format

- **Single table, 18 teams, double round robin, 34 rounds, 306
  matches** in every full season (2021/2022, 2022/2023, 2023/2024,
  2025/2026; 2024/2025 has 305 — see §5). Every round has exactly
  9 matches; every unordered pair meets exactly twice per full
  season (153 pairs × 2), verified from the index.
- **Turnover: 3–4 new clubs enter every season** (EDA §5) — promoted
  sides from the (unbuilt, not in the warehouse) Ghana Division One.
  There is no built Ghanaian parent/sibling in the warehouse, so no
  cross-league mover prior exists; the SHRINK arm is the thin-data
  treatment (MODEL_DESIGN §2).
- Calendar: autumn–spring. Season date ranges: 2021/2022
  2021-10-29→2022-06-19; 2022/2023 2022-09-10→2023-06-11;
  2023/2024 2023-09-15→2024-06-16; 2024/2025 2024-09-07→2025-06-08;
  2025/2026 2025-09-12→2026-05-24; 2026/2027 2026-09-05→2026-11-08
  (in progress, rounds 1–10).
- Team identity is by **name** (index `home`/`away`): 32 distinct
  names across the six seasons, 18 per season, no name variant or
  rename observed in the per-season sets. Team ids do not exist in
  this corpus (general null); the ids inside the 10 empty lineup
  blocks cover too few matches to key on.

## 4. Cards: why K is not buildable

- The 177 Card events are **all dismissals**: YellowRed 68, Red 109,
  **0 plain Yellow events in 1,619 payloads**. No stats yellows exist
  either (stats empty). There is therefore **no yellow-card target**
  in any form — neither a stats feed nor an event feed — in any
  season. K-GH is NOT BUILDABLE (payload-level evidence in
  `prereg/PREREG_SCKT_GH_NOT_BUILDABLE.md`).
- Referee identity is empty in all 1,619 payloads (`infoBox.Referee`
  key present, `text` always `''`), so X8 has no input even if a
  target existed. Dismissals themselves (0.11/match) are a rare
  event with no reliability evidence and are not a target.

## 5. Anomalies (frozen handling in PREPROCESSING.md)

| match | season | issue | handling |
|---|---|---|---|
| 23 rows (list in `build_data.py` output / `gh_matches.csv` `awarded=1`) | 2023/2024 (1), 2024/2025 (15), 2025/2026 (7) | **Awarded/forfeit 3-0 results**: score 3-0 or 0-3 with **zero events**. A played match with ≥1 goal always carries a goal-event feed in this corpus (1,408/1,412 event matches reproduce the index score; played 3-0s elsewhere carry goal events, e.g. Nations FC 3-0 Nsoatreman 2024-11-10, n_ev 5). The pattern is team-concentrated: **Nsoatreman** lose 14 straight 3-0s from 2025-03-16 (last played match 2025-03-10, 0-1 vs Samartex, with events) and **Hohoe United** lose 7 straight 3-0s from 2026-04-03 (last played match 2026-03-29, 0-3 vs Dreams FC, with events) — both mid-season withdrawals, remaining fixtures forfeited | **EXCLUDED from every fit/score/EDA level**; stay in CSV with `awarded=1`, `eligible=0` |
| 4584723 Nsoatreman vs Hearts of Oak | 2024/2025, round ~27 | Awarded row **direction-reversed in the source**: listed 3-0 home win for Nsoatreman, inside its 14-match forfeit run where every other fixture is a 3-0 loss | EXCLUDED as awarded either way; the flip is flagged, **not repaired** |
| 4015488 Asante Kotoko vs Legon Cities; 4015491 Great Olympics vs Real Tamale; 4015543 Bibiani Gold Stars vs Medeama | 2022/2023, round 7 | **Duplicate goal events**: the same scorer appears twice minutes apart under variant spellings (Steven/Stephen Mukwala; David Sandan Abagna 11' + 12'; Kwasi Donsu / Donsu Kwesi 13'). Event FT scores (2-1, 3-2, 1-2) disagree with the official index scores (1-1, 2-1, 1-1) | FT score from the index (official); HT values flagged `ht_suspect=1`, excluded from HT-share work only |
| 4584614 Nsoatreman vs Karela United | 2024/2025, round 17 | **Missing away goal event**: events say 1-0, official score 1-1 | FT score from the index; HT flagged `ht_suspect=1` (the missing goal's half is unknowable) |
| 2024/2025 round 33 | 2024/2025 | **One fixture absent from the warehouse entirely**: Holy Stars vs Nations FC is in neither the index nor the disk (both clubs on 33 matches; season total 305 not 306; home/away assignment unknowable from the warehouse) | Not a parsing gap; nothing to exclude (no row exists). Recorded as a warehouse gap |

Total excluded from every fit/score/EDA level: 23 awarded rows →
**1,596 eligible rows**.

## 6. What does not exist here (explicit)

- No xG (of any kind), no SOT, no corners, no total shots, no cards
  target, no referee, no player data, no substitutions,
  no stadium, no attendance, no team ids — in **any** season.
  Lineups exist as empty blocks in exactly 10 payloads (0 starters).
  S/C/K/T are not buildable (see MODEL_DESIGN §1). No proxy is
  constructed for any of them.
