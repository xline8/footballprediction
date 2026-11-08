# Step 1 — Data Understanding: BG-FirstLeague (Bulgaria First Professional League, FotMob id 270)

Source: FotMob world warehouse, index `data_enrichment/fotmob_world_index.csv`
filtered to `league_id = 270`; per-match JSONs under
`Bulgaria/First Professional League/<season>/<id>.json`. All numbers below
were computed from the warehouse and independently recomputed from the raw
JSONs by a second path (identical results).

## Inventory

| Season | Matches | Teams | Regular | Champ. play-off | ECL group | Relegation group | ECL play-off |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 222 | 14 | 182 | 15 | 12 | 12 | 1 |
| 2022/2023 | 283 | 16 | 240 | 15 | 12 | 15 | 1 |
| 2023/2024 | 283 | 16 | 240 | 15 | 12 | 15 | 1 |
| 2024/2025 | 293 | 16 | 240 | 12 | 12 | 28 | 1 |
| 2025/2026 | 293 | 16 | 240 | 12 | 12 | 28 | 1 |
| 2026/2027 | 97 | 14 | 97 | — | — | — | — |

Total 1,471 matches. Split-year seasons (autumn–spring), as labelled in the
warehouse. 2025/2026 is the last COMPLETE season (293 = full regular +
all split phases played). 2026/2027 is in progress (97 matches, regular
phase only at extraction) and returns to 14 teams.

## Format (verified from `general.leagueName` in every JSON)

The league is a regular double round-robin followed by split phases
(championship play-off, ECL group, relegation group, and a single-match
ECL play-off). The shape changed repeatedly: 14 teams in 2021/2022
(182 regular matches), 16 teams 2022/2023–2025/2026 (240 regular), the
relegation group grew from 12–15 matches to 28 in 2024/2025, and
2026/2027 is back to 14 teams. All phases are official league matches.
**Phase rule (frozen in Step 2/prereg): every phase stays in the corpus,
flagged by the `phase` column (AT-Bundesliga precedent) — no phase is
excluded or modelled separately.**

## Field coverage (per season, % of matches)

| Field | 2021/22 | 2022/23 | 2023/24 | 2024/25 | 2025/26 | 2026/27 |
|---|---|---|---|---|---|---|
| Score | 100 | 100 | 100 | 100 | 100 | 100 |
| Stats block (All) | 97.3 | 95.4 | 98.2 | 100 | 100 | 100 |
| Period splits (FirstHalf/SecondHalf) | 0 | 0 | 0 | 0 | 0 | 0 |
| Shotmap / xG | 0 | 0 | 0 | 0 | 0 | 0 |
| Events | 100 | 100 | 100 | 100 | 100 | 100 |
| Referee text | 100 | 100 | 100 | 99.7 | 100 | 100 |

- The stats block carries exactly four keys in every season:
  `BallPossesion`, `total_shots`, `ShotsOnTarget`, `corners`. There is
  **no** `expected_goals`, `touches_opp_box`, `big_chance`, `fouls`, or
  `yellow_cards`/`red_cards` stat key anywhere in this league.
- `has_period_splits` is False for all 1,471 index rows and no JSON
  carries FirstHalf/SecondHalf stat periods. Halves can therefore only
  come from event times (goals, cards) — see Step 3/5.
- Goals model is goals-only DC (no xG, no shotmap — the task brief's
  warehouse facts agree: shotmap 0).

## Cards: the stats-vs-events artefact check (required, done first)

The stats feed publishes **no yellow-card key at all**, in any season,
so there is no stats target to conflict with the event feed (this is
not the TH/ZA era-flipped artefact — there the stats feed existed and
the event feed lost plain yellows; here the event feed is the only
feed). The event feed is complete: events present in 1,471/1,471
matches, with plain `Yellow` events abundant in every season
(1,181–1,520 per season) plus `YellowRed` (27–41) and `Red` (30–57).
**Frozen target: event-unified yellows = direct Yellow + YellowRed,
per side (RU-1Division precedent, whose stats feed likewise had no
yellows).** `cards_source = events` for all rows.

## Team identity

22 distinct FotMob team ids across the corpus. Names are NOT stable
for 2 ids — 10144 appears as `CSKA Sofia`, `CSKA-Sofia` and
`PFC CSKA-Sofia`; 10135 as `Etar` and `Etar Veliko Tarnovo` — so all
logic keys on team id, never name. The second tier (id 9096, Second
Professional League) IS in the warehouse (1,735 matches, scores only,
no stats), so promoted-club (mover) descriptives can be measured
against the real feeder corpus (Step 3/5); its reserve sides
(e.g. `CSKA 1948 II`) never appear in tier 1 and do not contaminate
the mover set, which is keyed by team id.
