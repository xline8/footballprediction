# NL Tweede Divisie — data understanding

Phase 1 uses FotMob league id 9195 and filters `general.leagueName
== "Tweede Divisie"`. The warehouse index contains 1,638 rows: 306 in
each of 2021/2022–2025/2026 and 108 in 2026/2027 (partial, through
2026-11-07). Every selected row is a finished regular-season match,
rounds 1–34 in the complete seasons. There are no play-off rows in
this feed; no exclusion count is invented.

## Coverage — measured by content, never by the index flags

The index's `has_*` flags are all `False` for this league — and for
once they are right. Every number below was measured on the payloads
(`inventory.py`, results in `inventory_summary.json`):

| season | matches | score | stats (non-null) | shotmap shots>0 | period splits | lineups | player stats | events | referee text |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 306 | 100% | 0 | 0 | 0 | 0 | 0 | 96.4% | 0% |
| 2022/2023 | 306 | 100% | 0 | 0 | 0 | 0 | 0 | 96.4% | 0% |
| 2023/2024 | 306 | 100% | 0 | 0 | 0 | 0 | 0 | 97.4% | 0% |
| 2024/2025 | 306 | 100% | 0 | 0 | 0 | 0 | 0 | 96.7% | 0% |
| 2025/2026 | 306 | 100% | 0 | 0 | 0 | 0 | 0 | 96.7% | 0% |
| 2026/2027 | 108 | 100% | 0 | 0 | 0 | 0 | 0 | 96.3% | 0% |

- `content.stats` is `None` in all 1,638 payloads; the shotmap shot
  list is empty in all 1,638; `content.lineup` and `content.playerStats`
  are empty/None in all 1,638. The payload keys exist but carry no
  content — the classic false-positive shape the program warns about,
  here in reverse (the flags say absent, and absent it is).
- The event feed is the only live feed: 8,722 events total — 5,314
  Goal, 3,170 Half markers (45' and 90', 1,585 each), 238 Card.
  **Card events are Red (176) and YellowRed (62) only; there is not
  a single Yellow event in the corpus.** Yellows do not exist here.
- Referee: the `infoBox.Referee` dict exists but its `text` is empty
  in all 1,638 matches. No referee identity exists anywhere.
- `general.coverageLevel` is `lower` throughout.

## Score integrity

- Goal events reproduce `header.status.scoreStr` exactly in
  **1,638/1,638** matches (0 mismatches). No awarded/abnormal
  matches were found (no `awarded` flag set; no shootout or
  extra-time markers).
- 53 matches have an empty event feed; all 53 are 0-0, so their HT
  is (0, 0) by the same feed. HT goals are therefore derivable for
  all 1,638 matches (1,585 via goal events, 53 via events-zero).
- Team identity is stable by FotMob team id (no name maps to two
  ids in this corpus).

## Competition format

18 teams, 34 rounds, single round-robin home/away (18 × 17 = 306).
The Dutch pyramid has **no promotion/relegation between the Eerste
Divisie and the Tweede Divisie**, and the warehouse confirms it: no
entrant in any observed transition played in the Eerste Divisie the
previous season (checked name-by-name against FotMob id 111; 0 in
every transition). Entrants come from below (Derde Divisie, tier 4,
not in the warehouse) plus reserve sides. Reserve sides in the feed:
Jong Almere City FC, Jong FC Volendam, Jong Sparta Rotterdam.

## What this corpus can and cannot support

- CAN: goals (FT + HT from events) — the only buildable candidate.
- CANNOT: SOT, corners, total shots (no stats/shotmap); cards
  (no yellows; reds are 0.145/match, a rare event with split-half
  r = −0.09); xG / set-play / xGOT / box touches / possession
  (no stats at all); referee features (no referee text); lineup /
  absence features (no lineups); halves models beyond the frozen
  goals constant (see EDA F3).

The exact reproducible inventory is in `inventory_summary.json`;
the script is `inventory.py`.
