# Phase 1 — Data Understanding: FotMob J.League Warehouse

Corpus: `data_enrichment/fotmob_jleague/` — 6,228 full matchDetails JSONs
pulled 2026-11-08 (commit `0d6ac1a`), seasons 2021 → 2026/27, three tiers:
J1 (FotMob id 223, 2,091 matches), J2 (8974, 2,318), J3 (9136, 1,819).
Inventory tool: `inventory.py` (raw results in `inventory_summary.json`).
Every number below was measured on the files, not taken from the pull log.

## 0. Integrity headline

- 6,228 files = 6,228 unique match ids = 6,228 rows in
  `fotmob_jleague_index.csv`. No duplicates, nothing on disk missing from
  the index, nothing in the index missing on disk. All 6,228 finished.
- The index's own `has_*` flags are pull-time key-presence flags. They are
  **not** depth measures: J2/J3 payloads carry a `shotmap` block whose
  shot list is empty, and J3 2026/27 carries a `stats.Periods.All` block
  with no stat rows. All coverage below is measured by content
  (non-empty), never by key presence.

## 1. Payload anatomy (one matchDetails JSON)

| Section | Contents | Modelling relevance |
|---|---|---|
| `general` | matchId, leagueId/Name, round, home/away team **ids + names**, `coverageLevel`, kickoff UTC | identity, season/round structure |
| `header.status` | `scoreStr` (official FT score), red-card counts, `awarded` flag, status `reason` (incl. shootout result), half timestamps | FT target, anomaly flags |
| `header.events` | goals/red cards grouped by player | redundant with matchFacts events |
| `content.matchFacts.events.events` | full event list: Goal (scorer, assist, `isHome` = **credited** side, `ownGoal`, minute), Card (`card` ∈ Yellow/YellowRed/Red, player, side), Substitution (swap pairs, minute), Half markers | HT derivation, cards, timelines |
| `content.stats.Periods` | team stats for `All` / `FirstHalf` / `SecondHalf`: possession, team xG (+ open-play / set-play / non-penalty splits), total shots, SOT, off target, blocked, in/out of box, big chances, box touches, corners, yellows, reds, fouls, offsides, saves, passing, duels | all team-stat targets, per-half splits |
| `content.shotmap.shots` | one row per shot: x/y, `expectedGoals` (xG), `expectedGoalsOnTarget` (xGOT), `situation` (RegularPlay/SetPiece/Penalty/FastBreak/FromCorner/ThrowInSetPiece…), `shotType` (Head/RightFoot/LeftFoot/OtherBodyPart), `period` (FirstHalf/SecondHalf/PenaltyShootout), `eventType` (Goal/AttemptSaved/Miss/Post), `isOnTarget`, `isBlocked`, blocked-shot coordinates, on-goal placement (goalCrossedY/Z), playerId, minute | per-shot analysis the top-5 spine never had at this scale for Japan |
| `content.lineup` | formations, 11 starters + subs per side with positions, ages, FotMob ratings, coach; subs carry `substitutionEvents` (sub-in minute) | lineups, formations, minutes — J1/J2 only |
| `content.playerStats` | per-player stat blocks + per-player shotmap (J1 only) | player-level aggregation |
| `content.matchFacts` extras | infoBox (stadium, attendance where present), teamForm, insights | context only |
| `content.table`, `h2h`, `momentum` | standings snapshot, head-to-head, momentum flag | not used (standings are post-match snapshots; leakage risk if used naively) |

Stat-value typing quirk: values arrive mixed — ints, floats, numeric
strings (`'1.49'`), and percent-suffixed strings (`'188 (64%)'`). The
extractor (`jleague_lib._num`) takes the leading number. The same stat key
appears in several stat groups (e.g. `expected_goals` in "Top stats" and
in the xG group); across all 6,228 files the duplicated entries **never
disagree** (0 conflicts measured).

## 2. Coverage matrix (share of matches with real content, %)

| League-season | n | Shotmap (shots>0) | Team stats FT | Team stats per half | Lineups | Player stats | Events |
|---|---|---|---|---|---|---|---|
| J1 2021 | 380 | **0** | 100 (no xG, no halves) | 0 | 100 | 100 | 100 |
| J1 2022 | 306 | 100 | 100 (incl. xG) | 0 | 100 | 100 | 100 |
| J1 2023 | 306 | 100 | 100 | 86 | 100 | 100 | 100 |
| J1 2024 | 380 | 100 | 100 | 100 | 100 | 100 | 100 |
| J1 2025 | 380 | 100 | 100 | 100 | 100 | 100 | 100 |
| J1 2026 (transitional) | 200 | 100 | 100 | 100 | 100 | 100 | 100 |
| J1 2026/27 (partial) | 139 | 100 | 100 | 100 | 100 | 100 | 100 |
| J2 2021 | 462 | 0 | 29 (4 keys only) | 0 | 100 | 0 | 100 |
| J2 2022 | 465 | 0 | 100 (4 keys) | 0 | 100 | 0 | 100 |
| J2 2023 | 465 | 0 | 98 (4 keys) | 0 | 100 | 0 | 100 |
| J2 2024 | 383 | 0 | 89 (4 keys) | 0 | 100 | 0 | 100 |
| J2 2025 | 383 | 0 | ~0 | 0 | 100 | 0 | 100 |
| J2 2026/27 (partial) | 160 | 0 | 0 | 0 | 100 | 0 | 100 |
| J3 2021 | 210 | 0 | 0 | 0 | 0 | 0 | 93 |
| J3 2022 | 306 | 0 | 0 | 0 | 0 | 0 | 94 |
| J3 2023 | 380 | 0 | 0 | 0 | 0 | 0 | 93 |
| J3 2024 | 380 | 0 | 0 | 0 | 0 | 0 | 93 |
| J3 2025 | 383 | 0 | 16 | 16 (60 matches) | 54 | 16 | 94 |
| J3 2026/27 (partial) | 160 | 0 | 0 (empty blocks) | 0 | 100 | 0 | 93 |

Reading of the matrix:

- **J1 is two corpora.** 2021 is a stats-and-events season (full FT team
  stats incl. shots/SOT/corners/cards, lineups, player stats — but no
  shotmap, no team xG, no per-half stats). From 2022 it is a full xG-era
  corpus; per-half team stats ramp in during Mar–Apr 2023 (86% of 2023)
  and are complete from 2024.
- **J2 is a scores + lineups + events corpus.** Its stats block, when
  present at all, contains exactly four keys (possession, total shots,
  SOT, corners) — never xG, never halves, never cards. Coverage is
  calendar-windowed: starts mid-Sep 2021, near-complete 2022 – Sep 2024,
  **dies in Oct 2024** and never returns (2025 ≈ 0, 2026/27 = 0). Cards
  for J2 exist only in the event feed (which is complete: ~800–1,240
  yellows per season).
- **J3 is a scores corpus with events.** No stats at all except a
  Jun–Aug 2025 window (62 matches with full FT stats, 60 with halves) and
  lineups in 2025 (54%) / 2026/27 (100%). Its event feed omits yellow
  cards entirely — only red-family events are listed (11–34 per season
  vs ~1,000 expected yellows) — so **J3 yellows do not exist in this
  corpus** outside the 62 stats matches of 2025. Events are missing
  altogether for 123 J3 matches (6.8%), which are also the only matches
  in the corpus without a derivable half-time score.
- `general.coverageLevel` tracks this faithfully: J1 2021 = `ratings`,
  J1 2022+ = `xG`, J2/J3 = `lower`.

Per-shot field completeness (J1, where shotmap exists): x/y, situation,
shotType, period, isOnTarget, isBlocked, playerId ≈ 100%; `expectedGoals`
99.7–99.9% per season. **`expectedGoalsOnTarget` changes meaning by era:**
populated only for on-target shots in 2022–2024 (32–56% of shots),
populated for ~100% of shots from 2025. Cross-era xGOT comparisons must
respect that break.

## 3. Quirk register (each verified on the files)

1. **J1's double 2026 label is two different competitions, not a split
   season.** Folder `2026` = Feb 6 – Jun 6 2026, 200 matches, 20 teams
   (the transitional half-season played before the calendar switch);
   folder `2026-2027` = Aug 7 – Nov 8 2026, 139 matches so far. Date
   ranges are disjoint, match ids are globally unique — no overlap, no
   double counting. J2/J3 have no `2026` folder: their transitional
   competition was a combined J2/J3 league under a different FotMob
   competition id that this pull did not cover, leaving a Feb–Jul 2026
   calendar gap for tiers 2–3 (documented gap, not missing files).
2. **The transitional J1 2026 league settled draws by penalty shootout.**
   57 of its 200 matches were drawn; 51 have shootout attempts inside the
   shotmap with `period = 'PenaltyShootout'` and a flat xG of 0.7884
   each. The stats feed excludes them; naive shotmap sums do not. One
   further match (Machida Zelvia 2–1 Nagoya Grampus) is a playoff played
   to extra time (stats periods include ExtraHalf blocks).
3. **Two J1 2021 matches where the event feed disagrees with the
   official score**, both flagged, neither silently repaired:
   `3520725` Urawa–Shonan (awarded 0–3; played events say 2–3) and
   `3520767` (official 3–3; events contain one extra away goal — a
   disallowed goal left in the feed, or an event error). Everywhere else
   (6,226 matches) goal events reproduce `scoreStr` exactly.
4. **Own goals are attributed differently by the two feeds.** In
   matchFacts events, `isHome` is the *credited* team (matches the
   official score 100%). In the shotmap, `teamId` is the *shooting* team,
   so an own goal must be flipped to the opponent. With the flip, the two
   independent HT derivations agree on **1,711 / 1,711** J1 matches.
5. **Team identity is stable by FotMob team id** (63 ids total; no name
   maps to two ids). Five ids carry two name spellings: two genuine
   renames (Omiya Ardija → RB Omiya Ardija; Thespakusatsu Gunma →
   Thespa Gunma) and three diacritic/order variants (Júbilo Iwata,
   FC Ryūkyū, FC Imabari/Imabari FC). Keying on names would split five
   clubs in two; keying on ids is exact.
6. **Coverage comes in calendar windows, not per-match randomness** —
   J2 stats (Sep 2021 → Sep 2024), J3 stats (Jun–Aug 2025), J1 per-half
   stats (from Mar–Apr 2023). Missingness is a provider-feed property:
   analyses must treat it as block-missing, and any feature built on a
   windowed feed inherits the window.

## 4. Definition alignment with our existing concepts (all measured)

| Concept | FotMob J.League source | Alignment result |
|---|---|---|
| FT score | `header.status.scoreStr` (official) | Source of truth. Event goal counts reproduce it in 6,226/6,228 (2 flagged exceptions above). |
| HT score | **No explicit field exists.** Derived from goal events (`time ≤ 45`, credited side) | Cross-validated against shotmap period counts (OG-flip rule): agreement 1,711/1,711 on J1 2022+. Available for 6,105/6,228 matches (all except 123 event-less J3 matches). |
| Shots on target | stats feed `ShotsOnTarget` | FotMob's stats SOT **excludes blocked shots**; the shotmap's `isOnTarget` includes blocked attempts that were on course. The aligned shotmap definition (on-target AND not blocked) reproduces the stats value exactly in 95.6% of J1 team-matches (mean abs diff 0.05, corr 0.995). Use the **stats feed as source of record**; this is the same definitional split the top-5 work documented across providers, not an error in either feed. |
| Total shots | stats feed `total_shots` | Shotmap regulation-shot count matches exactly in ~92% of team-matches (residual ≈ feed-inventory disagreements of 1 shot in ~8% of matches). Stats feed is source of record. |
| Team xG | stats feed `expected_goals` | Equals the sum of per-shot `expectedGoals` over regulation shots (mean abs diff 0.022, corr 0.994, once shootout attempts are excluded). One xG model, two presentations. Splits (open play / set play / non-penalty) exist only in the stats feed. |
| Corners | stats feed `corners` (FT; FH/SH where half stats exist) | No corner events exist in the payload — same concept as the spine's HC/AC. J2 corners ride on the windowed 4-key stats block; J3 corners exist only in the 2025 stats window. |
| Yellow cards | stats feed `yellow_cards`; fallback: event feed `card='Yellow'` counts | Stats vs events agree exactly in 94.0% of J1 matches (mean abs diff 0.08). Whether the stats count includes the second yellow of a YellowRed is indistinguishable at this noise level (effect ≤ 0.05/match). Our production cards model counts yellows (HY+AY) — the unified column takes the stats value as-is where present. |
| Red cards | stats feed `red_cards` | Equals event (straight Red + YellowRed) in 99.8% of J1 matches — FotMob counts a second-yellow dismissal as a red. |
| xGOT (post-shot xG) | per-shot `expectedGoalsOnTarget` | A genuinely new quantity vs the spine: placement quality of on-target shots. Era break in population rule (see §2) must be respected. |

## 5. What this corpus has that the top-5 master spine never did

- Per-shot everything for J1 2022+: location, xG, xGOT, situation,
  shot type, block geometry, goal-mouth placement — 47k+ shots.
- Per-half team stats (J1 2023+): shots/SOT/corners/cards/xG by half,
  from an independent stats feed — not derived from event timestamps.
- Event timelines for 98% of the corpus: every goal, card and
  substitution with a minute — scoring-time and game-state analyses
  become possible without the shotmap.
- Lineups with formations, coaches and substitution minutes (J1 + J2,
  100%) — team-sheet strength is *measurable* here, subject to the
  reliability standard the SOT absence audit set (see EDA).
- Competition-format anomalies are visible and flagged (shootouts,
  extra time, awarded match) instead of silently contaminating targets.
