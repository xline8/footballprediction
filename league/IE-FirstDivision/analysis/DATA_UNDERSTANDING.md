# Phase 1 — Data Understanding: Ireland First Division (FotMob 218)

Corpus: `data_enrichment/fotmob_world_index.csv` filtered to league_id
218 — 1,028 matchDetails JSONs, seasons 2021–2026, all finished. Every
number below was measured on the files, not taken from the index flags.

## 0. Integrity headline

- 1,028 index rows = 1,028 files on disk = 1,028 built rows; match ids
  unique. No duplicates, nothing missing.
- The index `has_*` flags are all `False` for this league — and for
  once they are right: **there is no team-stats block, no shotmap, and
  no named referee in any payload**. This is a scores + events corpus.

## 1. Format (verified from payloads — the brief's format caution)

| Season | Teams | Regular | Playoffs | Notes |
|---|---|---|---|---|
| 2021 | 10 | 27 rounds × 5 = 135 | 5 | Triple round-robin |
| 2022 | 9 | 36 rounds × 4 = 144 | 5 | Quadruple round-robin, one bye per round |
| 2023 | 10 | 36 rounds × 5 = 180 | 5 | Quadruple round-robin |
| 2024 | 10 | 36 × 5 = 180 | 5 | |
| 2025 | 10 | 36 rounds = **179** | 5 | One regular match absent from the warehouse (see §3.4) |
| 2026 | 10 | 36 × 5 = 180 | 5 | Virgin season, complete |

- Regular season = calendar-year (Feb–Oct), rounds labelled `1`–`36`
  (2021: `1`–`27`). Playoffs each season: `1/2` = two-legged
  semi-finals (4 matches) + `final` (1 match) between the 3rd–6th
  placed clubs. The playoff winner then faces the Premier Division
  9th-placed club in a separate promotion/relegation playoff that is
  **not** in this league's warehouse rows.
- **Modelled scope: regular season only** (998 matches). Playoffs are
  built into the table (`phase='playoff'`) but excluded from every
  EDA/design number and from all fitting and evaluation — two-legged
  knockout ties with different incentives are not regular-season
  football. Playoff levels for the record: 2.47 goals/match (n=30)
  vs 2.82 regular.
- Team count churn: 2022 has 9 teams because 2021 promoted two clubs
  (champion Shelbourne + playoff winner UCD) and relegated two from
  the Premier Division (Longford Town 10th, Waterford FC 9th via the
  playoff). 2023 has 10 again with new club Kerry FC joining.
- 2024 playoff final (Bray Wanderers vs Athlone Town, 2–2) went to
  extra time and penalties (Bray won 4–2 on pens). The 2023 and 2025
  finals also went to extra time. `scoreStr` is the regulation score
  in all three — the goals target is unaffected.

## 2. Payload anatomy (one matchDetails JSON)

| Section | Contents | Modelling relevance |
|---|---|---|
| `general` | matchId, leagueId, matchRound, home/away team ids + names, `coverageLevel` = `lower` everywhere, kickoff UTC | identity, season/round structure |
| `header.status` | `scoreStr` (official FT score), red-card counts, `awarded`, `reason` (incl. penalties), half timestamps | FT target, anomaly flags |
| `content.matchFacts.events.events` | Goal (scorer, `isHome` = credited side, minute), Card (`card` ∈ Red/YellowRed only — see §3.2), Half markers. **No substitutions.** | HT derivation, reds |
| `content.stats` | Present as a key but `Periods` is `None` in **every** match | nothing — no SOT/corners/shots/xG |
| `content.shotmap.shots` | Empty list in **every** match | nothing — no xG/xGOT |
| `content.matchFacts.infoBox` | Stadium, Referee (text always `''`), Attendance | nothing — referee never named |
| `content.lineup` / `content.playerStats` | Absent/empty in every match | nothing |
| `content.table`, `h2h`, `momentum` | Present | not used (post-match snapshots; leakage) |

## 3. Coverage matrix (share of matches with real content, %)

| Season | n | Stats FT | Stats halves | Shotmap | Lineups | Player stats | Events (any) | Named referee |
|---|---|---|---|---|---|---|---|---|
| 2021 | 140 | 0 | 0 | 0 | 0 | 0 | 94 | 0 |
| 2022 | 149 | 0 | 0 | 0 | 0 | 0 | 93 | 0 |
| 2023 | 185 | 0 | 0 | 0 | 0 | 0 | 95 | 0 |
| 2024 | 185 | 0 | 0 | 0 | 0 | 0 | 95 | 0 |
| 2025 | 184 | 0 | 0 | 0 | 0 | 0 | 95 | 0 |
| 2026 | 185 | 0 | 0 | 0 | 0 | 0 | 95 | 0 |

## 4. Quirk register (each verified on the files)

1. **Yellow cards do not exist in this corpus.** The event feed lists
   Card events of type `Red` (142) and `YellowRed` (68) only — zero
   plain `Yellow` events in 1,028 matches. Total red-family events
   210 (0.20/match). A cards model has no yellow target; reds alone
   are a rare-event count the production design excludes. K-IEFD is
   NOT buildable (see `prereg/PREREG_NOT_BUILDABLE.md`).
2. **Event-less matches are (almost) all 0–0.** 55 matches have an
   empty event list; 54 of them finished 0–0, so their HT is 0–0 by
   the FT score itself (`ht_source='inferred-0-0'`). The exception
   is Cabinteely vs Galway United FC, 2021-04-09, 0–3 with no events
   at all — its HT is NaN (`ht_source='none'`).
3. **One goal-event feed contradicts the official score.**
   UCD vs Wexford FC, 2025-02-14: official 3–0, goal events say 0–3
   (the sides are flipped in the feed). Flagged
   (`score_events_mismatch=1`), official score kept, HT left NaN
   (`ht_source='mismatch'`). Everywhere else (1,026/1,028) goal
   events reproduce `scoreStr` exactly (the Cabinteely match has no
   events to check).
4. **One regular match is absent from the warehouse.** 2025 round 1
   has 4 matches instead of 5; the missing fixture is Finn Harps vs
   Kerry FC (the pair met only 3 times in 2025 instead of 4; both
   clubs are absent from round 1). Not imputed, not repaired —
   recorded as a gap. Dev regular n = 683, not 684.
5. **Team identity is stable by FotMob team id** (15 ids total; no
   name maps to two ids). Keying on ids is exact; no renames.
6. **`has_extra_time` needs a value check, not a key check.**
   `status.halfs` carries `firstExtraHalfStarted` /
   `secondExtraHalfStarted` keys in *every* match, empty (`''`)
   unless extra time was played. The builder flags only non-empty
   values — 3 matches (the 2023/2024/2025 playoff finals). A
   key-presence check would have flagged ~all of 2021 (this was
   caught during the build and fixed before any analysis ran).
7. **Coverage comes as a league property, not per-match randomness.**
   The stats/shotmap/referee absence is total and flat across all
   six seasons — there is no era to wait for and no window to
   exploit. The feasibility boundary is permanent for this corpus.

## 5. Definition alignment

| Concept | FotMob First Division source | Alignment result |
|---|---|---|
| FT score | `header.status.scoreStr` (official) | Source of truth. Event goal counts reproduce it in 1,026/1,028 (2 flagged exceptions above). |
| HT score | Derived from goal events (`time ≤ 45`, credited side); 0–0 inferred for event-less 0–0s | Derivable for 1,026/1,028 matches (99.8%). NaN only for the two flagged matches. |
| SOT / corners / total shots / xG | — | Do not exist anywhere in the corpus. |
| Yellow cards | — | Do not exist anywhere in the corpus (see quirk 1). |
| Red cards | Event feed (`Red` + `YellowRed`) | 0.20/match; descriptive only, not a modelling target. |
| Referee | `infoBox.Referee.text` | Empty string in 1,028/1,028 matches. |

## 6. What this corpus can and cannot do

- Can: a goals model (1X2 / OU / BTTS / DC) on regular-season scores
  — 998 matches, six seasons, stable team identities, a measurable
  cross-tier bridge to the Premier Division.
- Cannot: SOT, corners, total shots, or cards models — no target
  exists for any of them in any season, including the virgin window.
  This is a one-candidate league.
