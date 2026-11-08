# Phase 1 — Data Understanding: FotMob Honduras Liga Nacional Warehouse

Corpus: `data_enrichment/fotmob_world/` — 1,132 full matchDetails JSONs
(FotMob league id 337, "Liga Nacional"), seasons 2021/2022 –
2026/2027 in Apertura/Clausura split-season form (11 phase labels).
Inventory tool: `league/HN-LigaNacional/data/build_data.py` (raw
results in `analysis/inventory_summary.json`). Every number below
was measured on the files, not taken from the pull log.

## 0. Integrity headline

- 1,132 files = 1,132 unique match ids = 1,132 rows in
  `fotmob_world_index.csv` (filter `league_id = 337`). No duplicates,
  nothing on disk missing from the index, nothing in the index
  missing on disk. All 1,132 finished (`header.status.finished`).
- The index's own `has_*` flags are pull-time key-presence flags and
  are **not** depth measures: `has_stats` is `False` for all 1,132
  rows, and the payloads confirm `content.stats` is `None`
  everywhere — but the flag must not be trusted generally. All
  coverage below is measured by content (non-empty), never by key
  presence.

## 1. Payload anatomy (one matchDetails JSON)

| Section | Contents | Modelling relevance |
|---|---|---|
| `general` | matchId, leagueId/Name, round, home/away team ids + names, kickoff UTC | identity, season/round structure |
| `header.status` | `scoreStr` (official FT score), red-card counts, `awarded` flag, half timestamps, `finished` | FT target, anomaly flags |
| `header.teams` | team id, name, FT score per side | team identity (key on id), FT target |
| `content.matchFacts.events.events` | full event list: Goal (scorer, `isHome` = **credited** side, minute), Card (`card` ∈ Red/YellowRed — **no Yellow**), Substitution, Half markers | HT derivation, dismissal counts |
| `content.matchFacts.infoBox` | Tournament (leagueName, roundName), Match Date, Stadium, Referee (empty), Attendance | round/stage structure; referee text always empty |
| `content.stats` | `None` in 1,132/1,132 | no team stats of any kind |
| `content.shotmap.shots` | empty list in 1,132/1,132 | no shots, no xG, no xGOT |
| `content.lineup` | absent in 1,132/1,132 | no lineups/formations |
| `content.playerStats` | present as a key, no usable content | not used |
| `content.table`, `h2h`, `momentum` | standings snapshot, head-to-head, momentum flag | not used (post-match snapshots; leakage risk if used naively) |

## 2. Coverage matrix (share of matches with real content, %)

| Phase | n | FT score | Shotmap (shots>0) | Team stats FT | Team stats per half | Lineups | Referee named | Events |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 - Apertura | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 98 |
| 2021/2022 - Clausura | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 93 |
| 2022/2023 - Apertura | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 97 |
| 2022/2023 - Clausura | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 96 |
| 2023/2024 - Apertura | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 96 |
| 2023/2024 - Clausura | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 93 |
| 2024/2025 - Apertura | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 93 |
| 2024/2025 - Clausura | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 95 |
| 2025/2026 - Apertura | 124 | 100 | 0 | 0 | 0 | 0 | 0 | 96 |
| 2025/2026 - Clausura | 124 | 100 | 0 | 0 | 0 | 0 | 0 | 97 |
| 2026/2027 - Apertura | 84 | 100 | 0 | 0 | 0 | 0 | 0 | 95 |
| **Total** | **1,132** | **100** | **0** | **0** | **0** | **0** | **0** | **95** |

Reading of the matrix:

- **This is a scores + events corpus, nothing else.** The only
  modelling target that exists is FT goals (header scores, 1,132/1,132).
  HT goals are event-derived for 1,079/1,132 matches (95.3%).
- **No stats feed exists in any season.** There is no SOT, corners,
  total-shots, xG, yellow-card, or period-split source anywhere in
  the corpus — not a windowed feed, a total absence.
- **The event feed omits yellow cards entirely.** All 365 Card
  events are dismissals (253 Red + 112 YellowRed); 0 plain Yellow.
  Dismissals exist only as a count (0.32/match); they are not a
  validated target and are not a feature.
- Events are missing altogether for 52 matches (4.6%), which are
  also the matches without a derivable half-time score (plus one
  awarded match whose HT is deliberately blanked — see §3).
- `general.coverageLevel` is not a useful signal here; the corpus
  is uniformly scores-level.

## 3. Quirk register (each verified on the files)

1. **Apertura/Clausura split seasons with playoffs.** Each phase
   is a single round-robin (2021/22–2024/25: 10 teams, 18 rounds,
   90 regular matches) followed by a two-legged knockout
   (quarter-finals, semi-finals, final: 10 matches). From 2025/26
   the league expanded to 11 teams: 22 rounds, 110 regular matches,
   then a 12-match semifinal group stage (two groups of 3, double
   round-robin) plus a two-legged final (14 playoff matches).
   2026/27 expanded again to 12 teams (14 rounds × 6 = 84 matches
   so far, regular phase only, in progress).
2. **Playoff matches reuse round labels 1–6 in 2025/26.** The 12
   semifinal-group matches carry `roundName` 1–6, the same labels
   as the first six regular rounds. They are separated from the
   regular phase only by date: they are played after the last
   regular-phase date (Apertura: regular ends 2025-12-07, group
   matches 2025-12-11–28; Clausura: regular ends 2026-05-01, group
   matches 2026-05-03–19). The builder's stage rule
   (`build_data.py`) uses the last date of the phase's maximum
   numeric round as the regular-phase cutoff.
3. **Three awarded matches.** `3796146` (2021/2022 - Clausura,
   Lobos UPNFM–CD Vida, official 3–0; the event feed describes a
   played 1–1), `3796174` (same phase, CD Victoria–Lobos UPNFM,
   official 3–0; event feed empty), `5066531` (2025/2026 -
   Apertura, CD Olimpia–CD Victoria, official 0–0; event feed
   empty). The official header score is the FT target in all
   three; HT is blanked for awarded matches because the event feed
   describes a result the award overturned (for `3796146` the
   event-derived HT 0–1 would otherwise exceed the awarded
   away-goals total of 0). These are the only two matches where
   goal events disagree with the official score.
4. **FotMob re-ids phases.** `general.leagueId` is 337 for
   2021/22 but 889811 / 941508 (and others) for later phases; the
   index `league_id = 337` is the warehouse grouping, not a stable
   per-phase id. `general.leagueName` is "Liga Nacional -
   Apertura/Clausura" throughout.
5. **Team identity is stable by FotMob team id** (16 ids total; no
   name maps to two ids). Two ids carry two name spellings
   (diacritics only): 9932 `CD Marathón` / `CD Marathon`, 49783
   `Real Espana` / `Real España`. Keying on names would split two
   clubs; keying on ids is exact.
6. **No team ever has a same-phase home-and-away duplicate
   outside the format.** The 2025/26 double round-robin produces
   exactly two meetings per pair (one per venue); the apparent
   "duplicate pairs" in rounds 1–6 are the semifinal-group
   rematches (quirk 2), not data errors.

## 4. Definition alignment with our existing concepts (all measured)

| Concept | FotMob Honduras source | Alignment result |
|---|---|---|
| FT score | `header.status.scoreStr` / `header.teams[].score` (official) | Source of truth. Event goal counts reproduce it in 1,130/1,132 (2 awarded exceptions, §3.3). |
| HT score | **No explicit field exists.** Derived from goal events (`time ≤ 45`, credited side) via `jleague_lib.ht_from_events` | Available for 1,079/1,132 matches (all except 52 event-less matches + 1 awarded match with blanked HT). No cross-validation source exists (no shotmap, no period splits). |
| Shots on target | — | Does not exist. Stats feed is `None`, shotmap empty. |
| Total shots | — | Does not exist. |
| Team xG | — | Does not exist. |
| Corners | — | Does not exist (no stats feed, no corner events). |
| Yellow cards | — | Do not exist. Event feed carries dismissals only (Red/YellowRed). |
| Red cards / dismissals | Event feed `card` ∈ Red/YellowRed | 365 events in 1,132 matches (0.32/match). Descriptive count only. |
| Referee | `infoBox.Referee.text` | Empty in 1,132/1,132. No referee identity anywhere. |

## 5. What this corpus has that the top-5 master spine never did

Nothing beyond the format itself: the corpus is strictly poorer
than the spine (scores + goal-event times + dismissal events).
Its value is the clean split-season structure with a documented
regular/playoff split and six seasons of stable 10-team
round-robins before the 2025/26 expansion.
