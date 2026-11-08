# Phase 1 — Data Understanding: FotMob Vietnam V-League Warehouse

Corpus: `data_enrichment/fotmob_world/Vietnam/V-League/` — 969 full
matchDetails JSONs, FotMob league id 9088, seasons 2021 → 2026/2027.
Inventory tool: `analysis/eda.py` (raw results in
`analysis/inventory_summary.json`). Every number below was measured on
the files, not taken from the index flags.

## 0. Integrity headline

- 969 files = 969 unique match ids = 969 index rows for league 9088.
  No duplicates, nothing on disk missing from the index, nothing in the
  index missing on disk. All 969 finished (`header.status.finished`).
- The index's `has_*` flags are pull-time key-presence flags and they
  lie in both directions here: `has_lineup` is False on all rows, yet
  413 payloads (2024/2025 onward) carry full 11-man lineups; `stats`
  and `shotmap` keys exist in every payload but are always empty. All
  coverage below is measured by content (non-empty), never by key
  presence.

## 1. Payload anatomy (one matchDetails JSON)

| Section | Contents | Modelling relevance |
|---|---|---|
| `general` | matchId, leagueId/Name, matchRound, leagueRoundName, home/away team **ids + names**, `coverageLevel` (`lower` everywhere), kickoff UTC | identity, round structure |
| `header.status` | `scoreStr` (official FT score), red-card counts, `finished` | FT target |
| `header.teams` | team ids + names + FT scores | identity cross-check |
| `content.matchFacts.events.events` | event list: Goal (scorer, `isHome` = credited side, `newScore`, minute), Card (`card` ∈ Yellow/YellowRed/Red), Substitution, Half markers (HT/FT with `homeScore`/`awayScore`), MissedPenalty | HT score derivation, cards (windowed — see §2) |
| `content.stats.Periods` | present but **empty in all 969 payloads** | no team stats of any kind |
| `content.shotmap.shots` | present but **empty list in all 969 payloads** | no shots, no xG |
| `content.lineup` | **null** in 2021–2023/2024 (556 payloads); full 11 starters + subs + coach + averageStarterAge from 2024/2025 (413 payloads) | lineups, late era only |
| `content.playerStats` | **null in all 969 payloads** | nothing |
| `content.matchFacts.infoBox` | legInfo, Match Date, Tournament, Stadium, Referee, Attendance | Referee `text` is the **empty string in all 969 payloads** — no named referee anywhere |

## 2. Coverage matrix (share of matches with real content, %)

| Season | n | Stats FT | Shotmap (shots>0) | Per-half stats | Lineups | Events | HT via Half marker |
|---|---|---|---|---|---|---|---|
| 2021 | 84 | 0 | 0 | 0 | 0 | 95 (80/84) | 95 (80/84) |
| 2022 | 156 | 0 | 0 | 0 | 0 | 94 (147/156) | 94 (147/156) |
| 2023 | 134 | 0 | 0 | 0 | 0 | 85 (114/134) | 85 (114/134) |
| 2023/2024 | 182 | 0 | 0 | 0 | 0 | 95 (172/182) | 95 (172/182) |
| 2024/2025 | 182 | 0 | 0 | 0 | 0 | 100 | 100 |
| 2025/2026 | 182 | 0 | 0 | 0 | 0 | 99 (180/182) | 99 (180/182) |
| 2026/2027 (partial) | 49 | 0 | 0 | 0 | 100 | 100 | 100 |

Reading of the matrix:

- **This is a scores-only corpus.** No SOT, corners, total shots, xG,
  or team-stat target exists in any season. The only per-match
  quantities are the FT score (official, always present) and the HT
  score (Half-event marker, 924/969 = 95.4%; the 45 missing are exactly
  the 45 event-less matches).
- **Card events are calendar-windowed, not a target.** Plain Yellow
  events: **0 in 2021–2023/2024 (0/556 matches)**, then 609 in
  2024/2025 (3.35/match), 606 in 2025/2026, 139 in 2026/2027. Red /
  YellowRed events exist throughout but are rare (46–52 per season
  pre-2024/2025). A cards model would have no yellow target at all in
  any dev season — K is not buildable (see MODEL_DESIGN).
- **Substitution events are windowed the same way**: 0 matches in
  2021–2023/2024, 176/182 in 2024/2025, 117/182 in 2025/2026.
- **Lineups switch on in 2024/2025** (413/969). No playerStats ever.
  Lineup features stay closed by program precedent (see FEATURES R6);
  no reliability check for them was run here.
- `general.coverageLevel` is `lower` for all 969 payloads.

## 3. Season labelling and format (verified from payloads, not the index)

- The index uses **mixed labelling**: calendar-year 2021 (84), 2022
  (156), 2023 (134), then season-format 2023/2024 (182), 2024/2025
  (182), 2025/2026 (182), 2026/2027 in progress (49). Date ranges are
  **disjoint** and match ids globally unique: 2023 ends 2023-08-27,
  2023/2024 starts 2023-10-20. **No overlap, no double-count between
  "2023" and "2023/2024".** Dev/virgin windows are defined on these
  verified boundaries.
- **2021 is truncated**: rounds 1–12 only, 7 matches/round, 14 teams
  (84 = 12 × 7). The season was cancelled after round 12 (COVID); it
  is a valid seed (all 84 finished) but a short one.
- **2022**: 13 teams, 26 rounds × 6 matches = 156, balanced
  home-and-away.
- **2023 is a split-group season**: phase 1 single round-robin rounds
  1–13 (91 matches, 14 teams), then phase 2 from 2023-07-15 —
  top-8 championship group (7 rounds × 4 = 28) + bottom-6 relegation
  group (5 rounds × 3 = 15); 91 + 43 = 134. FotMob's `matchRound`
  **restarts at 1 in phase 2**, so the round label alone cannot
  separate the phases; `phase` in the CSV is derived from the date
  (≥ 2023-07-15 → `phase2_split_group`, 43 matches). All 134 are
  regular league matches — there is no separate playoff fixture.
- **2023/2024, 2024/2025, 2025/2026**: 14 teams, 26 rounds × 7 = 182
  each, balanced home-and-away. (`content.hasPlayoff` is present as a
  key from 2024/2025 but False; no extra playoff match exists — every
  season's count is exactly rounds × matches/round.)
- **2026/2027 in progress**: rounds 1–7, 49 matches through
  2026-11-08, 14 teams. Not used for fitting; season-end confirmatory
  read only (see MODEL_DESIGN).

## 4. Quirk register (each verified on the files)

1. **One score/event disagreement, flagged not repaired:** match
   `4688919` (2024/2025, 2025-01-24, Ho Chi Minh City FC vs
   opponent): official scoreStr 1–0, event feed lists 2 home goals.
   The official score is the source of truth everywhere; the CSV
   keeps it and flags `score_events_mismatch`. All other 968 matches:
   goal events reproduce the official score exactly.
2. **HT scores cross-validate perfectly.** The Half-event HT marker
   agrees with goal-event times ≤ 45 in **924/924** matches where
   both exist. HT derivation is therefore exact, not estimated.
3. **Team identity is stable by FotMob team id** (21 ids total; no
   name maps to two ids). Eleven ids carry two or three name
   spellings — ten are diacritic variants (Nam Dinh / Nam Định,
   Ha Noi FC / Hà Nội FC, …) and one is a genuine rename chain
   (HCM City → Ho Chi Minh City FC → Cong An Ho Chi Minh City, id
   179228; FLC Thanh Hoa → Thanh Hoa FC, id 179226). Keying on names
   would split eleven clubs; keying on ids is exact. Canonical names
   in the CSV are the most frequent spelling per id.
4. **Missingness is a provider-feed property, in calendar windows**
   (events thin pre-2024/2025, cards/lineups/subs switch on in
   2024/2025). Nothing is missing at random per match.

## 5. Definition alignment

| Concept | FotMob V-League source | Alignment result |
|---|---|---|
| FT score | `header.status.scoreStr` (official) | Source of truth. Event goal counts reproduce it in 968/969 (1 flagged exception above). |
| HT score | Half event `halfStrShort='HT'` (`homeScore`/`awayScore`) | Cross-validated against goal times ≤45: 924/924 agreement. Available for 924/969 matches. |
| Shots on target | — | **Absent.** No stats feed, no shotmap. |
| Total shots | — | **Absent.** |
| Team xG | — | **Absent.** |
| Corners | — | **Absent.** No corner events exist either. |
| Yellow cards | Event feed `card='Yellow'` | **Absent 2021–2023/2024 (0 events)**; present 2024/2025+ only. Not a usable target (see §2). |
| Red cards | Event feed `card='Red'`/`YellowRed` + `header.status` counts | Present but rare (0.08–0.29/match); production cards design excludes reds as a target. |
| Referee | `content.matchFacts.infoBox.Referee.text` | Empty string in all 969 payloads — no referee identity at all. |
