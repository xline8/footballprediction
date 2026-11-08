# Phase 1 — Data Understanding: FotMob Norway Eliteserien Warehouse

Corpus: `data_enrichment/fotmob_world/Norway/Eliteserien/` — 1,407 full
matchDetails JSONs (FotMob league_id 59), seasons 2021 → 2026, filtered
from `data_enrichment/fotmob_world_index.csv`. Every number below was
measured on the files / the Phase-2 CSV, not taken from index flags
(the index's `has_period_splits` flag understates early content in the
same way the J.League pull-time flags did; coverage here is by content).

## 0. Integrity headline

- 1,407 index rows = 1,407 files = 1,407 CSV rows; match ids unique;
  goal events reproduce `scoreStr` in **1,406/1,407** matches. The one
  exception is also the corpus's one **awarded** match (Vålerenga vs
  Kristiansund BK, 2025-11-22: official scoreStr 3–0, event feed shows
  3–3 on the pitch). The score of record is `scoreStr` everywhere in
  this build; the flag column `score_events_mismatch` carries the fact.

## 1. Format — a plain calendar-year double round-robin (no split)

The Eliteserien has **16 teams**. A season is 30 rounds, 240 matches,
one double round-robin, March/April to November/December:

| Season | n | First | Last | Teams |
|---|---|---|---|---|
| 2021 | 240 | 2021-05-09 | 2021-12-12 | 16 |
| 2022 | 240 | 2022-04-02 | 2022-11-13 | 16 |
| 2023 | 240 | 2023-04-10 | 2023-12-03 | 16 |
| 2024 | 240 | 2024-03-31 | 2024-12-01 | 16 |
| 2025 | 240 | 2025-03-29 | 2025-11-30 | 16 |
| 2026 (partial) | 207 | 2026-03-14 | 2026-11-08 | 16 |

There is **no split, no championship/relegation round, and no playoff
block inside this league_id**: every indexed match carries a numeric
round 1–30, so `phase = "regular"` for all 1,407 rows (the column is
kept for shape compatibility with the other league CSVs). The
end-of-season relegation play-off (14th-placed Eliteserien club vs a
1. divisjon club) is a separate FotMob competition and is not in this
corpus — nothing is silently missing from the league season itself.
Relegation/promotion still matters at the team level: the bottom two
clubs drop to the 1. divisjon each year and two/three come up, so the
corpus holds **23 distinct clubs** across six seasons and every season
opens with mover clubs that have no recent in-league history (the
thin-team problem the goals shrinkage arm addresses — F4). The 1.
divisjon has no warehouse build in this league's scope, so no mover
tier offset can be estimated (X2 dropped, as in AT). 2021 started late
(9 May, a pandemic-delayed start) and ran to 12 December; the format
was otherwise constant across all six seasons.

**Virgin-window choice (frozen here, before any fitting):** season
**2025 is complete** — 240/240 matches, rounds 1–30, last match
2025-11-30. It is the virgin window. Season 2026 is in progress at
pull time (207 matches through 2026-11-08, round 26) and is reserved
as the confirmatory window, never read by any gate in this build.
This is not a transitional virgin (contrast J1's 2026): the primary
read is on a finished season.

## 2. Coverage matrix (share of matches with real content, %)

| Season | n | FT stats | xG (+ splits) | Shotmap | Period splits | Box touches | Referee named | Lineups |
|---|---|---|---|---|---|---|---|---|
| 2021 | 240 | 100 | 100 | 100 | 0.4 | 40.4 | 76.3 | 100 |
| 2022 | 240 | 100 | 100 | 100 | 0.0 | 42.9 | 100 | 100 |
| 2023 | 240 | 100 | 100 | 100 | 100 | 38.3 | 100 | 100 |
| 2024 | 240 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| 2025 | 240 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| 2026 (partial) | 207 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |

Reading: like AT, there is **no thin era for the targets**: FT team
stats (shots, SOT, corners, yellows, reds, fouls, possession, big
chances, xG with open-play/set-play/non-penalty splits) and the
shotmap exist for every match of every season. The ramps are in the
*secondary* feeds only: period splits arrive in 2023 (one stray match
in 2021, none in 2022); `touches_opp_box` is sporadic (38–43%) before
2024 and complete from 2024; referee names are missing for 23.7% of
2021 but complete from 2022 — the virgin season has 100% referee
coverage, so the K-J1 failure mode (a virgin window with no referees)
does not occur here (the X8 trait itself fails its reliability check
on this corpus — F8 — which is a different, measured reason).

Per-shot fields: x/y, situation, shotType, period, isOnTarget,
isBlocked ≈ 100% throughout. **`expectedGoalsOnTarget` changes
population rule by era**, exactly as in J1/AT: populated for ~34% of
shots (on-target shots only) in 2021–2023, 65.8% in 2024, and ~99.5%
from 2025. The fully-populated era therefore **starts in the virgin
season itself** — cross-era xGOT comparisons must respect that break
(F7), and no xGOT arm can be dev-tested in this build.

## 3. Quirk register

1. **The awarded match (above)** — one match, score of record kept,
   flagged, never excluded.
2. **2022 xG runs low.** Goals per unit stats-feed xG by season:
   1.033, **1.216**, 1.053, 0.984, 1.029 (complete seasons). The 2022
   season's xG feed undervalues the goals actually scored by ~20%
   while every other season sits within ±5%. The goals blend (X1)
   consumes xG as recorded — the reference pattern is unmodified and
   the gate judges the result — but dev-season 2022 numbers for G-NO
   carry this caveat (F11).
3. **2026 is a partial season** (207 matches, rounds 1–26, through
   2026-11-08). Reserved as confirmatory; not read by any gate. Its
   early levels run hot (3.32 goals, 28.8 shots) — a partial segment,
   not comparable to full seasons.
4. **Period-split absence before 2023** — halves constants are
   measured on the complete era 2023–2025 only (F3); no 1H/2H target
   is ever fabricated for 2021–2022.
5. **The stats feed UNDERCOUNTS yellows (found post-build, before
   any cards fitting — the AR/BR artefact in a third league).** Stats
   `yellow_cards` totals 4,353 over the corpus vs 4,625 for event-feed
   Yellow + YellowRed (every yellow shown). 171/1,407 matches
   disagree; 156 of them are stats-low, the gap appears in every
   season and is worst in 2025 (−6.5%). There is no clean identity —
   the stats feed simply drops cards (a second yellow is a YellowRed
   event, which explains a handful of yellows, not gaps of 2–4). The
   unified cards target is therefore the **event feed for all
   seasons** (Phase 2 rule 7, as amended), and every cards number in
   this build (levels, traits, gates) is computed on it. The first
   committed version of this file stated the opposite conclusion from
   an aggregate-only check; the per-match audit above supersedes it,
   and the correction is recorded in PREREG_K_NO's amendment header.
6. **High, variable home edge.** Home-win rate swings 41.7–50.8% by
   season and the pooled home goal edge is +0.42 — the strongest in
   the conveyor so far. Descriptive only; the ratings fit home
   advantage per league as usual.
7. **No shootouts / extra time** anywhere in the corpus (league
   matches, 90-minute settlement) — `has_shootout` is 0 throughout.
